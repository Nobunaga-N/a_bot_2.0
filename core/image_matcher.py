import os
import cv2
import numpy as np
import logging
import time
from typing import Tuple, Optional, List, Dict, Union, Callable


class ImageMatcher:
    """Handles image recognition for game elements."""

    def __init__(self, template_dir: str):
        self.template_dir = template_dir
        self.logger = logging.getLogger("BotLogger")

        # Cache for loaded templates
        self.templates: Dict[str, np.ndarray] = {}

    def load_template(self, template_name: str) -> Optional[np.ndarray]:
        """
        Loads a template image from the template directory.

        Args:
            template_name: Name of the template file (e.g., "victory.png")

        Returns:
            Loaded template as NumPy array or None if failed
        """
        if template_name in self.templates:
            self.logger.debug(f"Использую кешированный шаблон: {template_name}")
            return self.templates[template_name]

        template_path = os.path.join(self.template_dir, template_name)
        self.logger.debug(f"Загрузка шаблона из: {template_path}")

        if not os.path.exists(template_path):
            self.logger.error(f"🚨 Файл шаблона не найден: {template_path}")
            return None

        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            self.logger.error(f"🚨 Не удалось загрузить шаблон: {template_path}")
            return None

        self.templates[template_name] = template
        self.logger.debug(f"Шаблон {template_name} загружен успешно, размер: {template.shape}")
        return template

    def find_in_screen(self,
                   screen_data: bytes,
                   template_name: str,
                   threshold: float = 0.8) -> Optional[Tuple[int, int]]:
        """
        Searches for a template in the screen data.

        Args:
            screen_data: Raw screen capture data
            template_name: Name of the template to find
            threshold: Matching threshold (0-1)

        Returns:
            (x, y) coordinates of the top-left corner of the match or None if not found
        """
        # Convert screen data to OpenCV format
        try:
            screen_array = np.frombuffer(screen_data, dtype=np.uint8)
            screen_img = cv2.imdecode(screen_array, cv2.IMREAD_COLOR)
            if screen_img is None:
                self.logger.error("🚨 Не удалось декодировать изображение экрана")
                return None

            self.logger.debug(f"Размеры скриншота: {screen_img.shape}")
        except Exception as e:
            self.logger.error(f"🚨 Ошибка при обработке данных экрана: {e}")
            return None

        # Load template
        template = self.load_template(template_name)
        if template is None:
            self.logger.error(f"🚨 Не удалось загрузить шаблон: {template_name}")
            return None

        # Perform template matching
        try:
            self.logger.debug(f"Поиск шаблона {template_name} с порогом {threshold}")
            result = cv2.matchTemplate(screen_img, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)

            self.logger.debug(f"Результат поиска шаблона {template_name}: max_val={max_val:.2f}, max_loc={max_loc}")

            if max_val >= threshold:
                self.logger.info(
                    f"✅ Найдено изображение ({template_name}) с точностью {max_val:.2f} на координатах {max_loc}")
                return max_loc
            else:
                self.logger.debug(
                    f"❌ Шаблон {template_name} не найден (max_val={max_val:.2f} < threshold={threshold:.2f})")
                return None
        except Exception as e:
            self.logger.error(f"🚨 Ошибка при сопоставлении шаблона: {e}")
            return None

    def wait_for_images(self,
                    screen_provider: Callable[[], Optional[bytes]],
                    image_list: List[str],
                    timeout: int = 90,
                    check_interval: float = 3) -> Tuple[Optional[str], Optional[Tuple[int, int]]]:
        """
        Waits for one of the specified images to appear on screen.

        Args:
            screen_provider: Function that returns fresh screen data
            image_list: List of template names to look for
            timeout: Maximum wait time in seconds
            check_interval: Time between checks in seconds

        Returns:
            (image_name, location) of the first matched image or (None, None) if timeout
        """
        import time
        start_time = time.time()

        while time.time() - start_time < timeout:
            screen_data = screen_provider()
            if screen_data is None:
                time.sleep(check_interval)
                continue

            for image_name in image_list:
                match_location = self.find_in_screen(screen_data, image_name)
                if match_location:
                    self.logger.info(f"🏆 Изображение найдено: {image_name}")
                    return image_name, match_location

            time.sleep(check_interval)

        self.logger.warning("⚠ Таймаут ожидания изображений")
        return None, None