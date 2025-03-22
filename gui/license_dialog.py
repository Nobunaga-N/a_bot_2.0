from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QClipboard, QFont

from .ui_factory import UIFactory


class LicenseSignals(QObject):
    """Signals for the license dialog."""
    activation_successful = pyqtSignal()


class LicenseDialog(QDialog):
    """Dialog for license activation."""

    def __init__(self, license_validator, parent=None):
        super().__init__(parent)

        self.license_validator = license_validator
        self.signals = LicenseSignals()

        self.init_ui()

    def init_ui(self):
        """Initialize the UI components."""
        self.setWindowTitle("Активация лицензии")
        self.setMinimumWidth(500)
        self.setMinimumHeight(250)

        # Main layout
        main_layout = UIFactory.create_vertical_layout()

        # Title
        title_label = UIFactory.create_title_label("Age of Magic Бот - Активация лицензии")
        main_layout.addWidget(title_label)

        # Instructions
        instructions = UIFactory.create_label(
            "Пожалуйста, введите ваш лицензионный ключ (компактный base64):",
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        instructions.setFont(QFont(UIFactory.create_label("").font().family(), 12))
        main_layout.addWidget(instructions)

        # License key input
        self.license_key_input = UIFactory.create_line_edit(
            placeholder="Введите ваш лицензионный ключ здесь..."
        )
        main_layout.addWidget(self.license_key_input)

        # Buttons row
        button_layout = UIFactory.create_horizontal_layout()

        self.activate_button = UIFactory.create_success_button(
            "Активировать лицензию",
            tooltip="Проверить и активировать лицензионный ключ"
        )
        self.activate_button.clicked.connect(self.activate_license)

        self.fingerprint_button = UIFactory.create_primary_button(
            "Показать отпечаток устройства",
            tooltip="Показать уникальный отпечаток вашего устройства для генерации лицензии"
        )
        self.fingerprint_button.clicked.connect(self.show_fingerprint)

        button_layout.addWidget(self.fingerprint_button)
        button_layout.addWidget(self.activate_button)

        main_layout.addLayout(button_layout)

        # Add some spacing
        main_layout.addSpacing(20)

        self.setLayout(main_layout)

    def activate_license(self):
        """Validate and activate the license key."""
        license_key = self.license_key_input.text().strip()

        if not license_key:
            QMessageBox.warning(
                self,
                "Пустой лицензионный ключ",
                "Пожалуйста, введите действительный лицензионный ключ."
            )
            return

        if self.license_validator.verify_license(license_key):
            # Save the license key
            from license.storage import LicenseStorage
            storage = self.license_validator.storage
            storage.save_license(license_key)

            QMessageBox.information(
                self,
                "Лицензия активирована",
                "Ваша лицензия была успешно активирована!"
            )

            # Emit the activation_successful signal
            self.signals.activation_successful.emit()

            # Close the dialog
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Ошибка лицензии",
                "Лицензионный ключ недействителен или истек.\n"
                "Пожалуйста, проверьте ключ и попробуйте снова."
            )

    def show_fingerprint(self):
        """Show the machine fingerprint in a dialog."""
        # Get the machine fingerprint
        fingerprint = self.license_validator.fingerprint.generate()

        if not fingerprint:
            QMessageBox.critical(
                self,
                "Ошибка",
                "Не удалось сгенерировать отпечаток устройства."
            )
            return

        # Create dialog
        fingerprint_dialog = QDialog(self)
        fingerprint_dialog.setWindowTitle("Отпечаток устройства")
        fingerprint_dialog.setMinimumWidth(450)

        # Layout
        layout = UIFactory.create_vertical_layout()

        # Instructions
        instructions = UIFactory.create_label(
            "Скопируйте этот отпечаток и отправьте его разработчику для получения лицензионного ключа:",
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        layout.addWidget(instructions)

        # Fingerprint display
        fingerprint_text = UIFactory.create_line_edit()
        fingerprint_text.setText(fingerprint)
        fingerprint_text.setReadOnly(True)
        layout.addWidget(fingerprint_text)

        # Copy button
        copy_button = UIFactory.create_primary_button("Копировать в буфер обмена")
        copy_button.clicked.connect(
            lambda: self._copy_to_clipboard(fingerprint, copy_button)
        )
        layout.addWidget(copy_button)

        fingerprint_dialog.setLayout(layout)
        fingerprint_dialog.exec()

    def _copy_to_clipboard(self, text, button):
        """Copy text to clipboard and change button text temporarily."""
        # Copy to clipboard
        clipboard = self.parent().clipboard() if self.parent() else QClipboard()
        clipboard.setText(text)

        # Change button text
        original_text = button.text()
        button.setText("Скопировано!")

        # Reset button text after a delay
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1500, lambda: button.setText(original_text))