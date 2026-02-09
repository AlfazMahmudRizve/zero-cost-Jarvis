"""
JARVIS HUD (Visual Interface)
PyQt6-based transparent overlay.
"""

import sys
import math
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSlot, QSize, QPoint
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QBrush

class ReactorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 200)
        self.state = "IDLE"
        self.angle = 0
        self.pulse = 0
        self.pulse_dir = 1
        
        # Animation Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(50)  # 20 FPS

    def set_state(self, state: str):
        self.state = state
        self.update()

    def animate(self):
        # Rotate logic
        if self.state == "PROCESSING":
            self.angle = (self.angle + 10) % 360
        else:
            self.angle = 0
            
        # Pulse logic
        if self.state == "LISTENING":
            self.pulse += 5 * self.pulse_dir
            if self.pulse > 50: self.pulse_dir = -1
            if self.pulse < 0: self.pulse_dir = 1
        else:
            self.pulse = 0
            
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center = QPoint(self.width() // 2, self.height() // 2)
        radius = 80
        
        # Determine Color based on state
        if self.state == "IDLE":
            color = QColor(0, 100, 255, 100) # Dim Blue
            core_color = QColor(0, 200, 255, 150)
        elif self.state == "LISTENING":
            color = QColor(0, 200, 255, 200 + self.pulse) # Bright Blue + Pulse
            core_color = QColor(255, 255, 255, 200)
        elif self.state == "PROCESSING":
            color = QColor(255, 140, 0, 200) # Orange
            core_color = QColor(255, 200, 50, 200)
        elif self.state == "SPEAKING":
            color = QColor(0, 255, 100, 200) # Green
            core_color = QColor(100, 255, 150, 200)
        else:
            color = QColor(100, 100, 100, 100)
            core_color = QColor(50, 50, 50, 100)

        # Draw Outer Ring
        pen = QPen(color, 4)
        painter.setPen(pen)
        painter.drawEllipse(center, radius, radius)
        
        # Draw Rotating Segments (if processing)
        if self.state == "PROCESSING":
            painter.translate(center)
            painter.rotate(self.angle)
            painter.translate(-center)
            painter.drawArc(center.x() - radius - 10, center.y() - radius - 10, 
                           (radius + 10) * 2, (radius + 10) * 2, 0, 90 * 16)
            painter.drawArc(center.x() - radius - 10, center.y() - radius - 10, 
                           (radius + 10) * 2, (radius + 10) * 2, 180 * 16, 90 * 16)
            painter.resetTransform()

        # Draw Core
        painter.setBrush(QBrush(core_color))
        painter.setPen(Qt.PenStyle.NoPen)
        # Pulse effect on size
        core_radius = radius - 20 + (self.pulse / 5)
        painter.drawEllipse(center, int(core_radius), int(core_radius))


class JarvisHUD(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool  # Doesn't show in taskbar
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Geometry (Bottom Right)
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen.width() - 350, screen.height() - 300, 320, 280)
        
        # Central Widget & Layout
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Reactor
        self.reactor = ReactorWidget()
        layout.addWidget(self.reactor, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Text Label
        self.label = QLabel("Online")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 200);
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
                font-weight: bold;
                background-color: rgba(0, 0, 0, 100);
                border-radius: 10px;
                padding: 5px;
            }
        """)
        self.label.setWordWrap(True)
        self.label.setFixedWidth(280)
        layout.addWidget(self.label)
        
        self.show()

    def update_state(self, state: str):
        self.reactor.set_state(state)
        
    def update_text(self, text: str):
        if len(text) > 100: text = text[:97] + "..."
        self.label.setText(text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    hud = JarvisHUD()
    hud.update_state("LISTENING")
    sys.exit(app.exec())
