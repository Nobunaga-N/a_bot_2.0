from PyQt6.QtWidgets import (
    QPushButton, QLabel, QLineEdit, QTextEdit, QHBoxLayout,
    QVBoxLayout, QGroupBox, QProgressBar, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap, QFont

from .styles import Styles


class UIFactory:
    """
    Factory class for creating UI components with consistent styling.
    """

    @staticmethod
    def create_title_label(text):
        """Create a styled title label."""
        label = QLabel(text)
        label.setObjectName("title")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    @staticmethod
    def create_subtitle_label(text):
        """Create a styled subtitle label."""
        label = QLabel(text)
        label.setObjectName("subtitle")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    @staticmethod
    def create_label(text, alignment=Qt.AlignmentFlag.AlignLeft):
        """Create a standard label with the specified alignment."""
        label = QLabel(text)
        label.setAlignment(alignment)
        return label

    @staticmethod
    def create_primary_button(text, icon=None, tooltip=None):
        """Create a primary styled button."""
        button = QPushButton(text)
        if icon:
            button.setIcon(QIcon(icon))
        if tooltip:
            button.setToolTip(tooltip)
        return button

    @staticmethod
    def create_success_button(text, icon=None, tooltip=None):
        """Create a success styled button."""
        button = QPushButton(text)
        button.setObjectName("success")
        if icon:
            button.setIcon(QIcon(icon))
        if tooltip:
            button.setToolTip(tooltip)
        return button

    @staticmethod
    def create_danger_button(text, icon=None, tooltip=None):
        """Create a danger styled button."""
        button = QPushButton(text)
        button.setObjectName("danger")
        if icon:
            button.setIcon(QIcon(icon))
        if tooltip:
            button.setToolTip(tooltip)
        return button

    @staticmethod
    def create_warning_button(text, icon=None, tooltip=None):
        """Create a warning styled button."""
        button = QPushButton(text)
        button.setObjectName("warning")
        if icon:
            button.setIcon(QIcon(icon))
        if tooltip:
            button.setToolTip(tooltip)
        return button

    @staticmethod
    def create_line_edit(placeholder=None, readonly=False):
        """Create a styled line edit."""
        line_edit = QLineEdit()
        if placeholder:
            line_edit.setPlaceholderText(placeholder)
        if readonly:
            line_edit.setReadOnly(True)
        return line_edit

    @staticmethod
    def create_text_edit(placeholder=None, readonly=False):
        """Create a styled text edit."""
        text_edit = QTextEdit()
        if placeholder:
            text_edit.setPlaceholderText(placeholder)
        if readonly:
            text_edit.setReadOnly(True)
        return text_edit

    @staticmethod
    def create_log_text_edit():
        """Create a text edit styled for log output."""
        text_edit = QTextEdit()
        text_edit.setObjectName("log")
        text_edit.setReadOnly(True)
        font = QFont("Consolas", Styles.FONTS["size_normal"])
        text_edit.setFont(font)
        return text_edit

    @staticmethod
    def create_horizontal_layout(spacing=10, margins=(10, 10, 10, 10)):
        """Create a horizontal layout with the specified spacing and margins."""
        layout = QHBoxLayout()
        layout.setSpacing(spacing)
        layout.setContentsMargins(*margins)
        return layout

    @staticmethod
    def create_vertical_layout(spacing=10, margins=(10, 10, 10, 10)):
        """Create a vertical layout with the specified spacing and margins."""
        layout = QVBoxLayout()
        layout.setSpacing(spacing)
        layout.setContentsMargins(*margins)
        return layout

    @staticmethod
    def create_grid_layout(spacing=10, margins=(10, 10, 10, 10)):
        """Create a grid layout with the specified spacing and margins."""
        from PyQt6.QtWidgets import QGridLayout
        layout = QGridLayout()
        layout.setSpacing(spacing)
        layout.setContentsMargins(*margins)
        return layout

    @staticmethod
    def create_group_box(title, layout=None):
        """Create a styled group box with the specified title and layout."""
        group_box = QGroupBox(title)
        if layout:
            group_box.setLayout(layout)
        return group_box

    @staticmethod
    def create_progress_bar(min_val=0, max_val=100):
        """Create a styled progress bar."""
        progress_bar = QProgressBar()
        progress_bar.setMinimum(min_val)
        progress_bar.setMaximum(max_val)
        return progress_bar

    @staticmethod
    def create_horizontal_line():
        """Create a horizontal line separator."""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        return line

    @staticmethod
    def create_vertical_line():
        """Create a vertical line separator."""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        return line

    @staticmethod
    def create_spacer(horizontal=True, size_policy=QSizePolicy.Policy.Expanding):
        """Create a spacer item."""
        spacer = QFrame()
        if horizontal:
            spacer.setSizePolicy(size_policy, QSizePolicy.Policy.Fixed)
        else:
            spacer.setSizePolicy(QSizePolicy.Policy.Fixed, size_policy)
        return spacer