import os
import time
from datetime import datetime

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QStatusBar, QMessageBox,
    QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QPushButton, QFrame, QLineEdit, QSpinBox, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QIcon, QPixmap

from .ui_factory import UIFactory
from .license_dialog import LicenseDialog
from .styles import Styles


class BotSignals(QObject):
    """Signals for bot operations and UI updates."""
    state_changed = pyqtSignal(str)
    log_message = pyqtSignal(str, str)  # level, message
    error = pyqtSignal(str)
    stats_updated = pyqtSignal(dict)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, bot_engine, license_validator):
        super().__init__()

        self.bot_engine = bot_engine
        self.license_validator = license_validator

        # Create and connect signals
        self.signals = BotSignals()
        self.signals.state_changed.connect(self.update_bot_state)
        self.signals.log_message.connect(self.append_log)
        self.signals.error.connect(self.show_error)
        self.signals.stats_updated.connect(self.update_stats)

        # Set bot signals
        self.bot_engine.set_signals(self.signals)

        # Init UI
        self.init_ui()

        # Timer for stats update
        self.stats_timer = QTimer(self)
        self.stats_timer.timeout.connect(self.update_runtime)
        self.stats_timer.start(1000)  # Update every second

        # Bot runtime
        self.start_time = None

    def init_ui(self):
        """Initialize the UI components."""
        self.setWindowTitle("Age of Magic Bot v2.0")
        self.setMinimumSize(800, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = UIFactory.create_vertical_layout()

        # Title
        title_label = UIFactory.create_title_label("Age of Magic Bot")
        main_layout.addWidget(title_label)

        # Status label
        self.status_label = UIFactory.create_subtitle_label("Status: Idle")
        main_layout.addWidget(self.status_label)

        # Tab widget
        tab_widget = QTabWidget()

        # Main tab
        main_tab = QWidget()
        tab_widget.addTab(main_tab, "Control")

        # Stats tab
        stats_tab = QWidget()
        tab_widget.addTab(stats_tab, "Statistics")

        # Settings tab
        settings_tab = QWidget()
        tab_widget.addTab(settings_tab, "Settings")

        # License tab
        license_tab = QWidget()
        tab_widget.addTab(license_tab, "License")

        # Add tabs to main layout
        main_layout.addWidget(tab_widget)

        # Set the layout for the central widget
        central_widget.setLayout(main_layout)

        # Setup each tab
        self.setup_main_tab(main_tab)
        self.setup_stats_tab(stats_tab)
        self.setup_settings_tab(settings_tab)
        self.setup_license_tab(license_tab)

        # Status bar setup
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready")

        # Update license info in status bar
        self.update_license_status()

    def setup_main_tab(self, tab):
        """Setup the main control tab."""
        layout = UIFactory.create_vertical_layout()

        # Controls section
        controls_layout = UIFactory.create_horizontal_layout()

        # Start button
        self.start_button = UIFactory.create_success_button(
            "▶ Start Bot",
            tooltip="Start the bot"
        )
        self.start_button.clicked.connect(self.start_bot)
        controls_layout.addWidget(self.start_button)

        # Stop button
        self.stop_button = UIFactory.create_danger_button(
            "⛔ Stop Bot",
            tooltip="Stop the bot"
        )
        self.stop_button.clicked.connect(self.stop_bot)
        self.stop_button.setEnabled(False)
        controls_layout.addWidget(self.stop_button)

        # Add controls to layout
        controls_group = UIFactory.create_group_box("Controls")
        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)

        # Stats section
        stats_layout = UIFactory.create_grid_layout()

        # Runtime
        stats_layout.addWidget(UIFactory.create_label("Runtime:"), 0, 0)
        self.runtime_label = UIFactory.create_label("00:00:00")
        stats_layout.addWidget(self.runtime_label, 0, 1)

        # Battles started
        stats_layout.addWidget(UIFactory.create_label("Battles Started:"), 1, 0)
        self.battles_label = UIFactory.create_label("0")
        stats_layout.addWidget(self.battles_label, 1, 1)

        # Victories
        stats_layout.addWidget(UIFactory.create_label("Victories:"), 2, 0)
        self.victories_label = UIFactory.create_label("0")
        stats_layout.addWidget(self.victories_label, 2, 1)

        # Defeats
        stats_layout.addWidget(UIFactory.create_label("Defeats:"), 3, 0)
        self.defeats_label = UIFactory.create_label("0")
        stats_layout.addWidget(self.defeats_label, 3, 1)

        # Connection losses
        stats_layout.addWidget(UIFactory.create_label("Connection Losses:"), 0, 2)
        self.conn_losses_label = UIFactory.create_label("0")
        stats_layout.addWidget(self.conn_losses_label, 0, 3)

        # Errors
        stats_layout.addWidget(UIFactory.create_label("Errors:"), 1, 2)
        self.errors_label = UIFactory.create_label("0")
        stats_layout.addWidget(self.errors_label, 1, 3)

        # Success rate
        stats_layout.addWidget(UIFactory.create_label("Success Rate:"), 2, 2)
        self.success_rate_label = UIFactory.create_label("0%")
        stats_layout.addWidget(self.success_rate_label, 2, 3)

        # Add stats to layout
        stats_group = UIFactory.create_group_box("Statistics")
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Log section
        log_group = UIFactory.create_group_box("Log")
        log_layout = UIFactory.create_vertical_layout()

        # Log text
        self.log_text = UIFactory.create_log_text_edit()
        log_layout.addWidget(self.log_text)

        # Clear log button
        clear_log_button = UIFactory.create_primary_button("Clear Log")
        clear_log_button.clicked.connect(self.clear_log)
        log_layout.addWidget(clear_log_button)

        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        tab.setLayout(layout)

    def setup_stats_tab(self, tab):
        """Setup the statistics tab."""
        layout = UIFactory.create_vertical_layout()

        # Placeholder for future stats visualizations
        placeholder = UIFactory.create_label(
            "Detailed statistics will be shown here in future updates.",
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        layout.addWidget(placeholder)

        tab.setLayout(layout)

    def setup_settings_tab(self, tab):
        """Настройка вкладки настроек."""
        layout = UIFactory.create_vertical_layout()

        # Настройки ADB
        adb_group = UIFactory.create_group_box("Настройки ADB")
        adb_layout = UIFactory.create_grid_layout()

        # Статус ADB
        adb_layout.addWidget(UIFactory.create_label("Статус ADB:"), 0, 0)
        self.adb_status_label = UIFactory.create_label("Не проверено")
        adb_layout.addWidget(self.adb_status_label, 0, 1)

        # Кнопка проверки соединения
        test_button = UIFactory.create_primary_button("Проверить соединение")
        test_button.clicked.connect(self.test_adb_connection)
        adb_layout.addWidget(test_button, 1, 1)

        # Информация о встроенной ADB
        info_label = UIFactory.create_label(
            "ADB уже включен в дистрибутив бота и \n"
            "должен работать автоматически при использовании эмулятора LDPlayer."
        )
        adb_layout.addWidget(info_label, 2, 0, 1, 3)

        adb_group.setLayout(adb_layout)
        layout.addWidget(adb_group)

        # Настройки бота
        bot_group = UIFactory.create_group_box("Настройки бота")
        bot_layout = UIFactory.create_grid_layout()

        # Время ожидания
        bot_layout.addWidget(UIFactory.create_label("Время ожидания боя (сек):"), 0, 0)
        self.battle_timeout_input = UIFactory.create_line_edit(placeholder="120")
        bot_layout.addWidget(self.battle_timeout_input, 0, 1)

        # Попытки обновления
        bot_layout.addWidget(UIFactory.create_label("Макс. попыток обновления:"), 1, 0)
        self.max_refresh_input = UIFactory.create_line_edit(placeholder="3")
        bot_layout.addWidget(self.max_refresh_input, 1, 1)

        # Кнопка сохранения настроек
        save_button = UIFactory.create_success_button("Сохранить настройки")
        bot_layout.addWidget(save_button, 2, 1)

        bot_group.setLayout(bot_layout)
        layout.addWidget(bot_group)

        # Место для будущих настроек
        layout.addStretch()

        tab.setLayout(layout)

    def setup_license_tab(self, tab):
        """Setup the license tab."""
        layout = UIFactory.create_vertical_layout()

        # License info
        info_group = UIFactory.create_group_box("License Information")
        info_layout = UIFactory.create_grid_layout()

        # Status
        info_layout.addWidget(UIFactory.create_label("Status:"), 0, 0)
        self.license_status_label = UIFactory.create_label("Checking...")
        info_layout.addWidget(self.license_status_label, 0, 1)

        # Expiration
        info_layout.addWidget(UIFactory.create_label("Expiration Date:"), 1, 0)
        self.license_expiration_label = UIFactory.create_label("Unknown")
        info_layout.addWidget(self.license_expiration_label, 1, 1)

        # Days left
        info_layout.addWidget(UIFactory.create_label("Days Remaining:"), 2, 0)
        self.license_days_left_label = UIFactory.create_label("Unknown")
        info_layout.addWidget(self.license_days_left_label, 2, 1)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Activation
        activation_group = UIFactory.create_group_box("License Activation")
        activation_layout = UIFactory.create_vertical_layout()

        # Activate button
        activate_button = UIFactory.create_primary_button("Activate License")
        activate_button.clicked.connect(self.show_activation_dialog)
        activation_layout.addWidget(activate_button)

        # View fingerprint button
        fingerprint_button = UIFactory.create_primary_button("View Machine Fingerprint")
        fingerprint_button.clicked.connect(self.show_fingerprint)
        activation_layout.addWidget(fingerprint_button)

        activation_group.setLayout(activation_layout)
        layout.addWidget(activation_group)

        # Placeholder for future license features
        layout.addStretch()

        tab.setLayout(layout)

        # Update license info
        self.update_license_info()

    def start_bot(self):
        """Start the bot."""
        if self.bot_engine.start():
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.start_time = time.time()
            self.statusBar().showMessage("Bot running")
            self.update_runtime()

    def stop_bot(self):
        """Stop the bot."""
        if self.bot_engine.stop():
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.start_time = None
            self.statusBar().showMessage("Bot stopped")

    def clear_log(self):
        """Clear the log text."""
        self.log_text.clear()

    def append_log(self, level, message):
        """Append a message to the log text."""
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Get color for the log level
        log_colors = Styles.get_log_colors()
        color = log_colors.get(level.lower(), log_colors["info"])

        # Format the log message with HTML
        html_message = f'<span style="color:{color};">[{timestamp}] [{level.upper()}] {message}</span><br>'

        # Append to log
        self.log_text.insertHtml(html_message)

        # Scroll to bottom
        self.log_text.moveCursor(self.log_text.textCursor().MoveOperation.End)

    def update_bot_state(self, state):
        """Update the UI to reflect the current bot state."""
        self.status_label.setText(f"Status: {state}")

        # Different colors based on state
        if state == "IDLE":
            self.status_label.setStyleSheet(f"color: {Styles.COLORS['text_secondary']}")
        elif state in ["STARTING", "RECONNECTING"]:
            self.status_label.setStyleSheet(f"color: {Styles.COLORS['warning']}")
        elif state in ["ERROR", "CONNECTION_LOST"]:
            self.status_label.setStyleSheet(f"color: {Styles.COLORS['accent']}")
        else:
            self.status_label.setStyleSheet(f"color: {Styles.COLORS['secondary']}")

    def update_stats(self, stats):
        """Update the statistics displays."""
        self.battles_label.setText(str(stats.get("battles_started", 0)))
        self.victories_label.setText(str(stats.get("victories", 0)))
        self.defeats_label.setText(str(stats.get("defeats", 0)))
        self.conn_losses_label.setText(str(stats.get("connection_losses", 0)))
        self.errors_label.setText(str(stats.get("errors", 0)))

        # Calculate success rate
        battles = stats.get("victories", 0) + stats.get("defeats", 0)
        if battles > 0:
            success_rate = (stats.get("victories", 0) / battles) * 100
            self.success_rate_label.setText(f"{success_rate:.1f}%")
        else:
            self.success_rate_label.setText("0%")

    def update_runtime(self):
        """Update the runtime display."""
        if self.start_time:
            elapsed = int(time.time() - self.start_time)
            hours = elapsed // 3600
            minutes = (elapsed % 3600) // 60
            seconds = elapsed % 60
            self.runtime_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")

            # Also update the stats from bot engine
            self.update_stats(self.bot_engine.stats)

    def show_error(self, message):
        """Show an error message."""
        QMessageBox.critical(self, "Error", message)

    def test_adb_connection(self):
        """Проверка соединения с ADB."""
        if self.bot_engine.adb.check_connection():
            self.adb_status_label.setText("Подключено")
            self.adb_status_label.setStyleSheet(f"color: {Styles.COLORS['secondary']}")
            QMessageBox.information(
                self,
                "Подключение ADB",
                "Успешное подключение к устройству ADB!"
            )
        else:
            self.adb_status_label.setText("Не подключено")
            self.adb_status_label.setStyleSheet(f"color: {Styles.COLORS['accent']}")
            QMessageBox.warning(
                self,
                "Ошибка подключения ADB",
                "Не удалось подключиться к устройству ADB. Пожалуйста, проверьте настройки эмулятора."
            )

    def show_activation_dialog(self):
        """Show the license activation dialog."""
        dialog = LicenseDialog(self.license_validator, self)
        dialog.signals.activation_successful.connect(self.update_license_info)
        dialog.exec()

    def show_fingerprint(self):
        """Show the machine fingerprint."""
        # Use LicenseDialog's fingerprint method
        dialog = LicenseDialog(self.license_validator, self)
        dialog.show_fingerprint()

    def update_license_info(self):
        """Update the license information displays."""
        license_info = self.license_validator.get_license_info()

        # Update status
        status = license_info.get("status", "unknown")
        self.license_status_label.setText(status.capitalize())

        # Set color based on status
        if status == "valid":
            self.license_status_label.setStyleSheet(f"color: {Styles.COLORS['secondary']}")
        elif status == "expired":
            self.license_status_label.setStyleSheet(f"color: {Styles.COLORS['accent']}")
        elif status in ["missing", "invalid", "error"]:
            self.license_status_label.setStyleSheet(f"color: {Styles.COLORS['warning']}")

        # Update expiration
        expiration = license_info.get("expiration")
        if expiration:
            self.license_expiration_label.setText(expiration.strftime("%Y-%m-%d"))
        else:
            self.license_expiration_label.setText("N/A")

        # Update days left
        days_left = license_info.get("days_left", 0)
        self.license_days_left_label.setText(str(days_left))

        # Update status bar
        self.update_license_status()

    def update_license_status(self):
        """Update the license status in the status bar."""
        if self.license_validator.is_license_valid():
            license_info = self.license_validator.get_license_info()
            days_left = license_info.get("days_left", 0)
            self.statusBar().showMessage(f"License: Valid ({days_left} days remaining)")
        else:
            self.statusBar().showMessage("License: Invalid or expired")

    def closeEvent(self, event):
        """Handle the window close event."""
        if self.bot_engine.running.is_set():
            reply = QMessageBox.question(
                self,
                "Exit Confirmation",
                "The bot is still running. Are you sure you want to exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.bot_engine.stop()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()