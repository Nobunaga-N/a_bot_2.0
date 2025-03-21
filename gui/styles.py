from PyQt6.QtGui import QColor, QPalette, QFont
from PyQt6.QtCore import Qt


class Styles:
    """
    Centralized styling for the application.
    Provides colors, fonts, and stylesheets for a consistent look.
    """

    # Color palette
    COLORS = {
        # Primary colors
        "primary": "#3498db",  # Blue
        "primary_light": "#5faee3",
        "primary_dark": "#2980b9",

        # Secondary colors
        "secondary": "#2ecc71",  # Green
        "secondary_light": "#54d98c",
        "secondary_dark": "#27ae60",

        # Accent colors
        "accent": "#e74c3c",  # Red
        "accent_light": "#ec7063",
        "accent_dark": "#c0392b",

        # Warning colors
        "warning": "#f39c12",  # Orange
        "warning_light": "#f5b041",
        "warning_dark": "#d35400",

        # Neutral colors
        "background_dark": "#1e1e1e",
        "background_medium": "#2c3e50",
        "background_light": "#34495e",
        "text_primary": "#ecf0f1",
        "text_secondary": "#bdc3c7",
        "border": "#7f8c8d",
    }

    # Font settings
    FONTS = {
        "family": "Segoe UI",
        "size_small": 9,
        "size_normal": 10,
        "size_large": 12,
        "size_title": 14,
    }

    @classmethod
    def get_dark_palette(cls):
        """Create a dark color palette for the application."""
        palette = QPalette()

        # Set window and widget backgrounds
        palette.setColor(QPalette.ColorRole.Window, QColor(cls.COLORS["background_dark"]))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(cls.COLORS["text_primary"]))
        palette.setColor(QPalette.ColorRole.Base, QColor(cls.COLORS["background_medium"]))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(cls.COLORS["background_light"]))

        # Set text colors
        palette.setColor(QPalette.ColorRole.Text, QColor(cls.COLORS["text_primary"]))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(cls.COLORS["text_primary"]))

        # Set button colors
        palette.setColor(QPalette.ColorRole.Button, QColor(cls.COLORS["background_light"]))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(cls.COLORS["text_primary"]))

        # Set highlight colors
        palette.setColor(QPalette.ColorRole.Highlight, QColor(cls.COLORS["primary"]))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(cls.COLORS["text_primary"]))

        # Set disabled colors
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText,
                         QColor(cls.COLORS["text_secondary"]))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(cls.COLORS["text_secondary"]))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText,
                         QColor(cls.COLORS["text_secondary"]))

        # Set tooltip colors
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(cls.COLORS["background_light"]))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(cls.COLORS["text_primary"]))

        return palette

    @classmethod
    def get_base_stylesheet(cls):
        """Get the base stylesheet for the application."""
        return f"""
            QWidget {{
                background-color: {cls.COLORS["background_dark"]};
                color: {cls.COLORS["text_primary"]};
                font-family: "{cls.FONTS["family"]}";
                font-size: {cls.FONTS["size_normal"]}pt;
            }}

            QLabel {{
                color: {cls.COLORS["text_primary"]};
            }}

            QLabel#title {{
                font-size: {cls.FONTS["size_title"]}pt;
                font-weight: bold;
                color: {cls.COLORS["primary"]};
            }}

            QLabel#subtitle {{
                font-size: {cls.FONTS["size_large"]}pt;
                color: {cls.COLORS["text_secondary"]};
            }}

            QPushButton {{
                background-color: {cls.COLORS["primary"]};
                color: {cls.COLORS["text_primary"]};
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}

            QPushButton:hover {{
                background-color: {cls.COLORS["primary_light"]};
            }}

            QPushButton:pressed {{
                background-color: {cls.COLORS["primary_dark"]};
            }}

            QPushButton:disabled {{
                background-color: {cls.COLORS["background_light"]};
                color: {cls.COLORS["text_secondary"]};
            }}

            QPushButton#success {{
                background-color: {cls.COLORS["secondary"]};
            }}

            QPushButton#success:hover {{
                background-color: {cls.COLORS["secondary_light"]};
            }}

            QPushButton#success:pressed {{
                background-color: {cls.COLORS["secondary_dark"]};
            }}

            QPushButton#danger {{
                background-color: {cls.COLORS["accent"]};
            }}

            QPushButton#danger:hover {{
                background-color: {cls.COLORS["accent_light"]};
            }}

            QPushButton#danger:pressed {{
                background-color: {cls.COLORS["accent_dark"]};
            }}

            QPushButton#warning {{
                background-color: {cls.COLORS["warning"]};
            }}

            QPushButton#warning:hover {{
                background-color: {cls.COLORS["warning_light"]};
            }}

            QPushButton#warning:pressed {{
                background-color: {cls.COLORS["warning_dark"]};
            }}

            QLineEdit, QTextEdit, QPlainTextEdit {{
                background-color: {cls.COLORS["background_medium"]};
                color: {cls.COLORS["text_primary"]};
                border: 1px solid {cls.COLORS["border"]};
                border-radius: 4px;
                padding: 4px;
            }}

            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                border: 1px solid {cls.COLORS["primary"]};
            }}

            QTextEdit#log, QPlainTextEdit#log {{
                background-color: {cls.COLORS["background_dark"]};
                color: {cls.COLORS["secondary"]};
                font-family: "Consolas", "Courier New", monospace;
                font-size: {cls.FONTS["size_normal"]}pt;
            }}

            QProgressBar {{
                border: 1px solid {cls.COLORS["border"]};
                border-radius: 4px;
                text-align: center;
                background-color: {cls.COLORS["background_medium"]};
            }}

            QProgressBar::chunk {{
                background-color: {cls.COLORS["primary"]};
                width: 1px;
            }}

            QStatusBar {{
                background-color: {cls.COLORS["background_medium"]};
                color: {cls.COLORS["text_primary"]};
            }}

            QMenuBar {{
                background-color: {cls.COLORS["background_medium"]};
                color: {cls.COLORS["text_primary"]};
            }}

            QMenuBar::item:selected {{
                background-color: {cls.COLORS["primary"]};
            }}

            QMenu {{
                background-color: {cls.COLORS["background_medium"]};
                color: {cls.COLORS["text_primary"]};
            }}

            QMenu::item:selected {{
                background-color: {cls.COLORS["primary"]};
            }}

            QToolTip {{
                background-color: {cls.COLORS["background_light"]};
                color: {cls.COLORS["text_primary"]};
                border: 1px solid {cls.COLORS["border"]};
            }}

            QTabWidget::pane {{
                border: 1px solid {cls.COLORS["border"]};
                background-color: {cls.COLORS["background_medium"]};
            }}

            QTabBar::tab {{
                background-color: {cls.COLORS["background_light"]};
                color: {cls.COLORS["text_primary"]};
                padding: 8px 16px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}

            QTabBar::tab:selected {{
                background-color: {cls.COLORS["primary"]};
            }}

            QGroupBox {{
                border: 1px solid {cls.COLORS["border"]};
                border-radius: 4px;
                margin-top: 16px;
                font-weight: bold;
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                color: {cls.COLORS["text_primary"]};
            }}
        """

    @classmethod
    def get_log_colors(cls):
        """Get colors for different log levels."""
        return {
            "info": cls.COLORS["text_primary"],
            "warning": cls.COLORS["warning"],
            "error": cls.COLORS["accent"],
            "debug": cls.COLORS["secondary"],
        }