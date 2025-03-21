import time
import logging
import threading
from enum import Enum, auto
from typing import Dict, Tuple, Optional, List, Callable


class BotState(Enum):
    """Possible states of the bot."""
    IDLE = auto()
    STARTING = auto()
    SELECTING_BATTLE = auto()
    CONFIRMING_BATTLE = auto()
    IN_BATTLE = auto()
    BATTLE_ENDED = auto()
    CONNECTION_LOST = auto()
    RECONNECTING = auto()
    ERROR = auto()


class BotEngine:
    """Main bot logic and state management."""

    def __init__(self, adb_controller, image_matcher):
        self.adb = adb_controller
        self.image_matcher = image_matcher
        self.logger = logging.getLogger("BotLogger")

        # Event to control the bot thread
        self.running = threading.Event()

        # Current state of the bot
        self.state = BotState.IDLE

        # Click coordinates for different actions
        self.click_coords = {
            "start_battle": (1227, 832),
            "confirm_battle": (1430, 830),
            "auto_battle": (66, 642),
            "exit_after_win": (743, 819),
            "refresh_opponents": (215, 826),
            "reconnect_button": (803, 821)
        }

        # Define actions for different bot states
        self.state_actions = {
            BotState.IDLE: self._handle_idle,
            BotState.STARTING: self._handle_starting,
            BotState.SELECTING_BATTLE: self._handle_selecting_battle,
            BotState.CONFIRMING_BATTLE: self._handle_confirming_battle,
            BotState.IN_BATTLE: self._handle_in_battle,
            BotState.BATTLE_ENDED: self._handle_battle_ended,
            BotState.CONNECTION_LOST: self._handle_connection_lost,
            BotState.RECONNECTING: self._handle_reconnecting,
            BotState.ERROR: self._handle_error
        }

        # Bot statistics
        self.stats = {
            "battles_started": 0,
            "victories": 0,
            "defeats": 0,
            "connection_losses": 0,
            "errors": 0
        }

        # Signals for communicating with the UI (will be set in the main application)
        self.signals = None

    def set_signals(self, signals):
        """Sets the signals object for UI communication."""
        self.signals = signals

    def capture_screen(self):
        """Captures the screen and returns the data."""
        return self.adb.capture_screen()

    def start(self):
        """Starts the bot in a separate thread."""
        if not self.running.is_set():
            if not self.adb.check_connection():
                self.logger.error("🚨 ADB not connected. Check emulator settings!")
                if self.signals:
                    self.signals.error.emit("ADB not connected. Check emulator settings!")
                return False

            self.running.set()
            self.state = BotState.STARTING
            threading.Thread(target=self._bot_loop, daemon=True).start()
            self.logger.info("▶ Bot started")
            return True
        return False

    def stop(self):
        """Stops the bot."""
        if self.running.is_set():
            self.running.clear()
            self.state = BotState.IDLE
            self.logger.info("⛔ Bot stopped")
            return True
        return False

    def _bot_loop(self):
        """Main bot loop that handles state transitions and actions."""
        round_count = 0
        try:
            while self.running.is_set():
                # Call the appropriate handler for the current state
                handler = self.state_actions.get(self.state)
                if handler:
                    # State handlers return the next state
                    self.logger.info(f"Обработка состояния: {self.state}")
                    next_state = handler()
                    if next_state and next_state != self.state:
                        self.logger.info(f"Переход состояния: {self.state} -> {next_state}")
                        self.state = next_state

                        # Update UI with state change
                        if self.signals:
                            self.signals.state_changed.emit(self.state.name)
                else:
                    self.logger.error(f"🚨 Нет обработчика для состояния: {self.state}")
                    self.state = BotState.ERROR

                # Short sleep to prevent CPU hogging
                time.sleep(0.1)

        except Exception as e:
            self.logger.error(f"🚨 Ошибка в цикле бота: {e}")
            self.state = BotState.ERROR
            self.stats["errors"] += 1
            if self.signals:
                self.signals.error.emit(f"Ошибка бота: {e}")
        finally:
            # Clean up when the bot stops
            self.running.clear()
            self.state = BotState.IDLE
            if self.signals:
                self.signals.state_changed.emit(self.state.name)

    def _handle_idle(self):
        """Handler for IDLE state."""
        # In the idle state, we just wait for the start command
        time.sleep(0.5)
        return BotState.IDLE

    def _handle_starting(self):
        """Handler for STARTING state."""
        self.logger.info("🔄 Запуск бота...")

        # Look for the battle screen
        self.logger.info("Делаем скриншот экрана...")
        screen_data = self.capture_screen()
        if screen_data:
            self.logger.info("Скриншот получен, анализируем...")

            # Check for connection issues first
            if self._check_connection_issues(screen_data):
                self.logger.info("Обнаружены проблемы с соединением")
                return BotState.CONNECTION_LOST

            # Check if we're already on the battle screen
            if self.image_matcher.find_in_screen(screen_data, "cheak.png"):
                self.logger.info("Найден экран выбора боя (cheak.png)")
                return BotState.SELECTING_BATTLE

            # Check if we're at the battle confirmation screen
            if self.image_matcher.find_in_screen(screen_data, "confirm_battle.png"):
                self.logger.info("Найден экран подтверждения боя (confirm_battle.png)")
                return BotState.CONFIRMING_BATTLE

            # Check if we're already in a battle
            if self.image_matcher.find_in_screen(screen_data, "auto_battle.png"):
                self.logger.info("Найден экран боя (auto_battle.png)")
                return BotState.IN_BATTLE

            # Check if a battle just ended
            victory_found = self.image_matcher.find_in_screen(screen_data, "victory.png")
            defeat_found = self.image_matcher.find_in_screen(screen_data, "defeat.png")

            if victory_found:
                self.logger.info("Найден экран победы (victory.png)")
                return BotState.BATTLE_ENDED
            elif defeat_found:
                self.logger.info("Найден экран поражения (defeat.png)")
                return BotState.BATTLE_ENDED

            self.logger.warning("Не удалось найти ни один известный экран")
        else:
            self.logger.error("Не удалось получить скриншот экрана")

        # If we couldn't find a known screen, wait and try again
        self.logger.info("Ожидаем 2 секунды и пробуем снова...")
        time.sleep(2)
        return BotState.STARTING

    def _handle_selecting_battle(self):
        """Handler for SELECTING_BATTLE state."""
        self.logger.info("Selecting battle...")
        self.adb.tap(*self.click_coords["start_battle"])
        time.sleep(2)
        return BotState.CONFIRMING_BATTLE

    def _handle_confirming_battle(self):
        """Handler for CONFIRMING_BATTLE state."""
        self.logger.info("Confirming battle...")
        self.adb.tap(*self.click_coords["confirm_battle"])
        self.stats["battles_started"] += 1

        # Wait for the auto battle button to appear
        _, match_loc = self.image_matcher.wait_for_images(
            self.capture_screen, ["auto_battle.png"], timeout=50, check_interval=3
        )

        if match_loc:
            return BotState.IN_BATTLE
        else:
            self.logger.error("🚨 Auto battle button not found!")

            # Check for connection issues
            screen_data = self.capture_screen()
            if screen_data and self._check_connection_issues(screen_data):
                return BotState.CONNECTION_LOST

            return BotState.ERROR

    def _handle_in_battle(self):
        """Handler for IN_BATTLE state."""
        self.logger.info("In battle, enabling auto battle...")
        self.adb.tap(*self.click_coords["auto_battle"])

        # Wait for battle to end (victory or defeat)
        result, _ = self.image_matcher.wait_for_images(
            self.capture_screen, ["victory.png", "defeat.png"], timeout=120, check_interval=3
        )

        if result:
            return BotState.BATTLE_ENDED
        else:
            # Check for connection issues
            screen_data = self.capture_screen()
            if screen_data and self._check_connection_issues(screen_data):
                return BotState.CONNECTION_LOST

            # Battle seems to be stuck, try emergency clicks
            self.logger.warning("⚠ Battle seems stuck! Performing emergency clicks.")
            self._perform_emergency_clicks()
            return BotState.STARTING

    def _handle_battle_ended(self):
        """Handler for BATTLE_ENDED state."""
        # Check which result screen we're on
        screen_data = self.capture_screen()
        if not screen_data:
            return BotState.ERROR

        if self.image_matcher.find_in_screen(screen_data, "victory.png"):
            self.logger.info("🏆 Victory! Continuing to next battle.")
            self.stats["victories"] += 1
            self.adb.tap(*self.click_coords["exit_after_win"])
            time.sleep(5)
            return BotState.STARTING

        elif self.image_matcher.find_in_screen(screen_data, "defeat.png"):
            self.logger.info("❌ Defeat! Refreshing opponents and trying again.")
            self.stats["defeats"] += 1
            self.adb.tap(*self.click_coords["exit_after_win"])
            time.sleep(10)
            self.adb.tap(*self.click_coords["refresh_opponents"])
            time.sleep(2)
            return BotState.STARTING

        # If we can't find victory or defeat screens
        return BotState.STARTING

    def _handle_connection_lost(self):
        """Handler for CONNECTION_LOST state."""
        self.logger.warning("⚠ Connection to server lost! Attempting to reconnect...")
        self.stats["connection_losses"] += 1

        # Wait for the "Связаться с нами" button to appear
        screen_data = self.capture_screen()
        if not screen_data:
            return BotState.ERROR

        # Check if we already see the contact us button
        if self.image_matcher.find_in_screen(screen_data, "contact_us.png"):
            # Click on the "Связаться с нами" button at coordinates 803, 821
            self.adb.tap(*self.click_coords["reconnect_button"])
            time.sleep(7)
            return BotState.RECONNECTING

        # If not, wait for it to appear
        result, _ = self.image_matcher.wait_for_images(
            self.capture_screen, ["contact_us.png"], timeout=60, check_interval=3
        )

        if result:
            self.adb.tap(*self.click_coords["reconnect_button"])
            time.sleep(7)
            return BotState.RECONNECTING
        else:
            self.logger.error("🚨 Unable to find reconnect button!")
            return BotState.ERROR

    def _handle_reconnecting(self):
        """Handler for RECONNECTING state - implements the recovery algorithm."""
        self.logger.info("Reconnecting to game...")

        # Try to find cheak.png or confirm_battle.png first (5 seconds)
        result, _ = self.image_matcher.wait_for_images(
            self.capture_screen,
            ["cheak.png", "confirm_battle.png"],
            timeout=5,
            check_interval=1
        )

        if result == "cheak.png":
            return BotState.SELECTING_BATTLE
        elif result == "confirm_battle.png":
            return BotState.CONFIRMING_BATTLE

        # If not found, try to find victory.png or defeat.png (another 5 seconds)
        result, _ = self.image_matcher.wait_for_images(
            self.capture_screen,
            ["victory.png", "defeat.png"],
            timeout=5,
            check_interval=1
        )

        if result in ["victory.png", "defeat.png"]:
            return BotState.BATTLE_ENDED

        # If still not found, look for auto_battle.png
        result, _ = self.image_matcher.wait_for_images(
            self.capture_screen,
            ["auto_battle.png"],
            timeout=5,
            check_interval=1
        )

        if result == "auto_battle.png":
            return BotState.IN_BATTLE

        # If we still can't find any known screens, return to starting state
        self.logger.warning("⚠ Could not determine game state after reconnect. Restarting...")
        return BotState.STARTING

    def _handle_error(self):
        """Handler for ERROR state."""
        self.logger.error("🚨 Bot encountered an error. Attempting to recover...")
        time.sleep(5)
        return BotState.STARTING

    def _check_connection_issues(self, screen_data: bytes) -> bool:
        """
        Checks if there are connection issues on the current screen.

        Returns:
            True if connection issues detected, False otherwise
        """
        # Check for "Ожидание ответа от сервера" message
        if self.image_matcher.find_in_screen(screen_data, "waiting_for_server.png"):
            self.logger.warning("⚠ 'Waiting for server response' message detected")
            return True

        # Check for "Связаться с нами" button
        if self.image_matcher.find_in_screen(screen_data, "contact_us.png"):
            self.logger.warning("⚠ 'Contact us' button detected")
            return True

        return False

    def _perform_emergency_clicks(self):
        """Performs emergency clicks to try to recover from a stuck state."""
        self.logger.warning("⚠ Performing emergency clicks...")

        # Click back button
        self.adb.tap(49, 50)
        time.sleep(2)

        # Click center of screen
        self.adb.tap(588, 825)
        time.sleep(2)

        # Click exit button position
        self.adb.tap(743, 819)
        time.sleep(10)

        # Click refresh button position
        self.adb.tap(215, 826)
        time.sleep(2)