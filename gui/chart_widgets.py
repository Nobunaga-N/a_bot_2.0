import math
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPainterPath
from PyQt6.QtCore import Qt, QRect, QPointF

from .styles import Styles


class BaseChartWidget(QWidget):
    """Base class for all chart widgets."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumHeight(220)
        self.data = {}

        # Chart margins
        self.margin_left = 60
        self.margin_right = 20
        self.margin_top = 20
        self.margin_bottom = 40

        # Chart colors
        self.background_color = QColor(Styles.COLORS["background_dark"])
        self.text_color = QColor(Styles.COLORS["text_primary"])
        self.grid_color = QColor(Styles.COLORS["background_light"])

        # Set up layout
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

    def set_data(self, data):
        """Set the data for the chart."""
        self.data = data
        self.update()

    def get_chart_rect(self):
        """Get the rectangle representing the chart area."""
        return QRect(
            self.margin_left,
            self.margin_top,
            self.width() - self.margin_left - self.margin_right,
            self.height() - self.margin_top - self.margin_bottom
        )

    def draw_grid(self, painter, rect, h_lines=5, v_lines=0):
        """Draw the grid for the chart."""
        painter.setPen(QPen(self.grid_color, 1, Qt.PenStyle.DotLine))

        # Horizontal grid lines
        for i in range(h_lines + 1):
            y = rect.top() + (rect.height() / h_lines) * i
            painter.drawLine(rect.left(), y, rect.right(), y)

        # Vertical grid lines
        if v_lines > 0:
            for i in range(v_lines + 1):
                x = rect.left() + (rect.width() / v_lines) * i
                painter.drawLine(x, rect.top(), x, rect.bottom())

    def draw_axis(self, painter, rect):
        """Draw the axis for the chart."""
        painter.setPen(QPen(self.text_color, 2))

        # X axis
        painter.drawLine(rect.left(), rect.bottom(), rect.right(), rect.bottom())

        # Y axis
        painter.drawLine(rect.left(), rect.top(), rect.left(), rect.bottom())


class LineChartWidget(BaseChartWidget):
    """Widget for displaying line charts."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Line chart specific properties
        self.series = []
        self.show_points = True
        self.smooth_lines = True
        self.fill_area = True
        self.x_labels = []
        self.y_min = 0
        self.y_max = 100
        self.y_step = 20

    def set_data(self, data, series_config=None):
        """
        Set data for the line chart.

        Args:
            data: Dictionary with 'x_labels' for X axis labels and series data
            series_config: Optional list of series configurations (name, color)
        """
        self.data = data
        self.x_labels = data.get('dates', [])

        self.series = []
        if series_config:
            for config in series_config:
                if config['key'] in data:
                    self.series.append({
                        'name': config['name'],
                        'color': QColor(config['color']),
                        'data': data[config['key']]
                    })

        # Calculate y axis range
        all_values = []
        for series in self.series:
            all_values.extend(series['data'])

        if all_values:
            self.y_min = min(0, math.floor(min(all_values) * 0.9))
            self.y_max = math.ceil(max(all_values) * 1.1)

            # Calculate a nice step size
            range_size = self.y_max - self.y_min
            if range_size <= 5:
                self.y_step = 1
            elif range_size <= 20:
                self.y_step = 5
            elif range_size <= 100:
                self.y_step = 20
            else:
                self.y_step = 50

            # Adjust max to be a multiple of step
            self.y_max = math.ceil(self.y_max / self.y_step) * self.y_step

        self.update()

    def paintEvent(self, event):
        """Paint the line chart."""
        if not self.series or not self.x_labels:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Set up the painting area
        painter.fillRect(self.rect(), self.background_color)

        chart_rect = self.get_chart_rect()

        # Draw grid and axis
        self.draw_grid(painter, chart_rect)
        self.draw_axis(painter, chart_rect)

        # Draw Y axis labels
        painter.setPen(QPen(self.text_color))
        font = QFont(Styles.FONTS["family"], Styles.FONTS["size_small"])
        painter.setFont(font)

        for i in range(self.y_min, self.y_max + 1, self.y_step):
            y = chart_rect.bottom() - ((i - self.y_min) / (self.y_max - self.y_min)) * chart_rect.height()
            painter.drawText(
                5,
                y + 5,
                self.margin_left - 10,
                20,
                Qt.AlignmentFlag.AlignRight,
                str(i)
            )

        # Draw X axis labels
        for i, label in enumerate(self.x_labels):
            x = chart_rect.left() + (i / (len(self.x_labels) - 1 if len(self.x_labels) > 1 else 1)) * chart_rect.width()
            painter.drawText(
                x - 40,
                chart_rect.bottom() + 5,
                80,
                30,
                Qt.AlignmentFlag.AlignHCenter,
                label
            )

        # Draw each series
        for series in self.series:
            self.draw_series(painter, chart_rect, series)

    def draw_series(self, painter, rect, series):
        """Draw a single data series on the chart."""
        if not series['data'] or len(series['data']) < 2:
            return

        # Set up pen for the line
        pen = QPen(series['color'], 2)
        painter.setPen(pen)

        # Calculate points
        points = []
        for i, value in enumerate(series['data']):
            x = rect.left() + (i / (len(series['data']) - 1)) * rect.width()
            y = rect.bottom() - ((value - self.y_min) / (self.y_max - self.y_min)) * rect.height()
            points.append(QPointF(x, y))

        # Draw filled area if enabled
        if self.fill_area:
            path = QPainterPath()
            path.moveTo(points[0])

            # Add all points to the path
            for point in points[1:]:
                path.lineTo(point)

            # Close the path to the bottom of the chart
            path.lineTo(points[-1].x(), rect.bottom())
            path.lineTo(points[0].x(), rect.bottom())
            path.closeSubpath()

            # Fill the area
            fill_color = QColor(series['color'])
            fill_color.setAlpha(40)
            painter.fillPath(path, fill_color)

        # Draw the line
        if self.smooth_lines and len(points) > 2:
            # Draw a smooth curve
            path = QPainterPath()
            path.moveTo(points[0])

            for i in range(1, len(points) - 1):
                # Calculate control points for a smooth curve
                c1 = QPointF((points[i].x() + points[i - 1].x()) / 2, points[i - 1].y())
                c2 = QPointF((points[i].x() + points[i - 1].x()) / 2, points[i].y())
                path.cubicTo(c1, c2, points[i])

            path.lineTo(points[-1])
            painter.drawPath(path)
        else:
            # Draw straight line segments
            for i in range(1, len(points)):
                painter.drawLine(points[i - 1], points[i])

        # Draw points if enabled
        if self.show_points:
            point_pen = QPen(series['color'], 1)
            painter.setPen(point_pen)
            painter.setBrush(QBrush(Qt.GlobalColor.white))

            for point in points:
                painter.drawEllipse(point, 4, 4)


class BarChartWidget(BaseChartWidget):
    """Widget for displaying bar charts."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Bar chart specific properties
        self.categories = []
        self.series = []
        self.y_min = 0
        self.y_max = 100
        self.y_step = 20
        self.bar_width = 0.8  # Width of bars as a fraction of available space

    def set_data(self, data, series_config=None):
        """
        Set data for the bar chart.

        Args:
            data: Dictionary with 'categories' for X axis labels and series data
            series_config: Optional list of series configurations (name, color)
        """
        self.data = data
        self.categories = data.get('dates', [])

        self.series = []
        if series_config:
            for config in series_config:
                if config['key'] in data:
                    self.series.append({
                        'name': config['name'],
                        'color': QColor(config['color']),
                        'data': data[config['key']]
                    })

        # Calculate y axis range
        all_values = []
        for series in self.series:
            all_values.extend(series['data'])

        if all_values:
            self.y_min = min(0, math.floor(min(all_values) * 0.9))
            self.y_max = math.ceil(max(all_values) * 1.1)

            # Calculate a nice step size
            range_size = self.y_max - self.y_min
            if range_size <= 5:
                self.y_step = 1
            elif range_size <= 20:
                self.y_step = 5
            elif range_size <= 100:
                self.y_step = 20
            else:
                self.y_step = 50

            # Adjust max to be a multiple of step
            self.y_max = math.ceil(self.y_max / self.y_step) * self.y_step

        self.update()

    def paintEvent(self, event):
        """Paint the bar chart."""
        if not self.series or not self.categories:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Set up the painting area
        painter.fillRect(self.rect(), self.background_color)

        chart_rect = self.get_chart_rect()

        # Draw grid and axis
        self.draw_grid(painter, chart_rect)
        self.draw_axis(painter, chart_rect)

        # Draw Y axis labels
        painter.setPen(QPen(self.text_color))
        font = QFont(Styles.FONTS["family"], Styles.FONTS["size_small"])
        painter.setFont(font)

        for i in range(self.y_min, self.y_max + 1, self.y_step):
            y = chart_rect.bottom() - ((i - self.y_min) / (self.y_max - self.y_min)) * chart_rect.height()
            painter.drawText(
                5,
                y + 5,
                self.margin_left - 10,
                20,
                Qt.AlignmentFlag.AlignRight,
                str(i)
            )

        # Draw X axis labels
        for i, label in enumerate(self.categories):
            x = chart_rect.left() + (i + 0.5) / len(self.categories) * chart_rect.width()
            painter.drawText(
                x - 40,
                chart_rect.bottom() + 5,
                80,
                30,
                Qt.AlignmentFlag.AlignHCenter,
                label
            )

        # Draw bars
        self.draw_bars(painter, chart_rect)

    def draw_bars(self, painter, rect):
        """Draw the bars on the chart."""
        if not self.categories:
            return

        series_count = len(self.series)
        if series_count == 0:
            return

        # Calculate the width of each group of bars
        group_width = rect.width() / len(self.categories)

        # Calculate the width of each bar
        bar_width = group_width * self.bar_width / series_count

        for cat_idx, category in enumerate(self.categories):
            for series_idx, series in enumerate(self.series):
                if cat_idx < len(series['data']):
                    value = series['data'][cat_idx]

                    # Calculate bar position
                    x = rect.left() + cat_idx * group_width + series_idx * bar_width + (
                                group_width * (1 - self.bar_width) / 2)

                    # Calculate bar height
                    height = ((value - self.y_min) / (self.y_max - self.y_min)) * rect.height()

                    # Draw the bar
                    painter.setBrush(QBrush(series['color']))
                    painter.setPen(Qt.PenStyle.NoPen)

                    bar_rect = QRect(
                        int(x),
                        int(rect.bottom() - height),
                        int(bar_width),
                        int(height)
                    )

                    painter.drawRect(bar_rect)

                    # Draw value on top of the bar if there's enough space
                    if height > 20:
                        painter.setPen(QPen(Qt.GlobalColor.white))
                        painter.drawText(
                            bar_rect,
                            Qt.AlignmentFlag.AlignCenter,
                            str(value)
                        )


class PieChartWidget(BaseChartWidget):
    """Widget for displaying pie charts."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Pie chart specific properties
        self.slices = []
        self.donut = False
        self.donut_ratio = 0.5  # Inner circle size as a fraction of outer circle

    def set_data(self, data):
        """
        Set data for the pie chart.

        Args:
            data: List of dictionaries with 'label', 'value', and 'color' keys
        """
        self.slices = data
        self.update()

    def paintEvent(self, event):
        """Paint the pie chart."""
        if not self.slices:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Set up the painting area
        painter.fillRect(self.rect(), self.background_color)

        # Calculate total value
        total = sum(slice['value'] for slice in self.slices)
        if total <= 0:
            return

        # Calculate the center and radius of the pie
        center_x = self.width() / 2
        center_y = self.height() / 2
        radius = min(self.width(), self.height()) / 2 - 40

        # Draw slices
        start_angle = 0
        for slice in self.slices:
            # Calculate angle for this slice
            angle = (slice['value'] / total) * 360

            # Set the brush color
            painter.setBrush(QBrush(QColor(slice['color'])))
            painter.setPen(Qt.PenStyle.NoPen)

            # Draw the slice
            painter.drawPie(
                int(center_x - radius),
                int(center_y - radius),
                int(radius * 2),
                int(radius * 2),
                int(start_angle * 16),
                int(angle * 16)
            )

            # Draw label if there's enough space
            if angle > 15:
                # Calculate position for the label
                label_angle = start_angle + angle / 2
                label_radius = radius * 0.7

                label_x = center_x + math.cos(math.radians(label_angle)) * label_radius
                label_y = center_y - math.sin(math.radians(label_angle)) * label_radius

                # Draw the label
                painter.setPen(QPen(Qt.GlobalColor.white))
                painter.drawText(
                    int(label_x - 40),
                    int(label_y - 10),
                    80,
                    20,
                    Qt.AlignmentFlag.AlignCenter,
                    f"{slice['label']}: {int(slice['value'])}"
                )

            # Update the start angle for the next slice
            start_angle += angle

        # Draw donut hole if enabled
        if self.donut:
            painter.setBrush(QBrush(self.background_color))
            painter.setPen(Qt.PenStyle.NoPen)

            inner_radius = radius * self.donut_ratio
            painter.drawEllipse(
                int(center_x - inner_radius),
                int(center_y - inner_radius),
                int(inner_radius * 2),
                int(inner_radius * 2)
            )

        # Draw legend
        self.draw_legend(painter)

    def draw_legend(self, painter):
        """Draw a legend for the pie chart."""
        painter.setPen(QPen(self.text_color))
        font = QFont(Styles.FONTS["family"], Styles.FONTS["size_small"])
        painter.setFont(font)

        legend_x = 10
        legend_y = 10

        for slice in self.slices:
            # Draw color square
            painter.setBrush(QBrush(QColor(slice['color'])))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(legend_x, legend_y, 15, 15)

            # Draw label
            painter.setPen(QPen(self.text_color))
            painter.drawText(
                legend_x + 20,
                legend_y,
                self.width() - legend_x - 30,
                20,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                f"{slice['label']}: {slice['value']} ({(slice['value'] / sum(s['value'] for s in self.slices)) * 100:.1f}%)"
            )

            legend_y += 25