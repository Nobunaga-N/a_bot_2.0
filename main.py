import os
import sys
import logging

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from config import config, resource_path
from core.logger import BotLogger
from core.adb_controller import AdbController
from core.image_matcher import ImageMatcher
from core.bot_engine import BotEngine
from license.fingerprint import MachineFingerprint
from license.storage import LicenseStorage
from license.validator import LicenseValidator
from gui.main_window import MainWindow
from gui.license_dialog import LicenseDialog
from gui.styles import Styles


def init_logging():
    """Initialize the logging system."""
    log_level_str = config.get("ui", "log_level", "INFO")
    log_level = getattr(logging, log_level_str)

    logger = BotLogger(
        log_file=os.path.join(config.get("license", "directory"), "bot_log.txt"),
        max_bytes=500000,
        backup_count=3,
        log_level=log_level
    )

    logging.info(f"Инициализация логгера с уровнем {log_level_str}")
    return logger


def init_license_system():
    """Initialize the license validation system."""
    # Get paths
    license_dir = config.get("license", "directory")
    public_key_path = resource_path("public.pem")

    # Create components
    fingerprint = MachineFingerprint()
    storage = LicenseStorage(license_dir)
    validator = LicenseValidator(storage, fingerprint, public_key_path)

    return validator


def init_bot_engine():
    """Initialize the bot engine."""
    # Get configuration
    adb_path = resource_path(config.get("adb", "path", "adb.exe" if os.name == "nt" else "adb"))
    template_dir = resource_path("resources/images")

    # Debug information
    logging.info(f"ADB Path: {adb_path}")
    logging.info(f"Шаблоны изображений: {template_dir}")
    logging.info(f"Существует ли папка с шаблонами? {os.path.exists(template_dir)}")

    if os.path.exists(template_dir):
        template_files = [f for f in os.listdir(template_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
        logging.info(f"Найдены шаблоны: {', '.join(template_files)}")

    # Create components
    adb_controller = AdbController(adb_path)
    image_matcher = ImageMatcher(template_dir)
    bot_engine = BotEngine(adb_controller, image_matcher)

    return bot_engine


def setup_exception_handler(logger):
    """Set up a global exception handler to log uncaught exceptions."""

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Don't log keyboard interrupt
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception


def main():
    """Main application entry point."""
    # Initialize logging
    logger = init_logging()
    setup_exception_handler(logger)

    # Log application start
    logger.info("=" * 40)
    logger.info("Starting Age of Magic Bot v2.0")
    logger.info("=" * 40)

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("Age of Magic Bot")
    app.setApplicationVersion("2.0")

    # Set application icon
    app.setWindowIcon(QIcon(resource_path("aom.ico")))

    # Apply styles
    app.setPalette(Styles.get_dark_palette())
    app.setStyleSheet(Styles.get_base_stylesheet())

    # Initialize license system
    license_validator = init_license_system()

    # Check if license is valid
    if not license_validator.is_license_valid():
        logger.warning("License not valid or missing. Showing activation dialog.")
        # Create a temporary parent window to own the dialog
        temp_window = QApplication.activeWindow()

        # Show activation dialog
        dialog = LicenseDialog(license_validator, temp_window)
        result = dialog.exec()

        # Check if license is now valid
        if not license_validator.is_license_valid():
            logger.error("License validation failed. Exiting.")
            return 1

    # Initialize bot engine
    bot_engine = init_bot_engine()

    # Create main window
    main_window = MainWindow(bot_engine, license_validator)
    main_window.show()

    # Run application event loop
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())