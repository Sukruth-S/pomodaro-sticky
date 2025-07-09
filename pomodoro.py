import sys
import winsound
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout
)
from PyQt5.QtCore import Qt, QTimer, QPoint, QObject, QEvent,QUrl
from PyQt5.QtGui import QFont
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import os

class PomodoroSticky(QWidget):
    def __init__(self):
        super().__init__()

        # Basic window style
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(260, 200)
        self.setStyleSheet("background-color: #fff89c; border-radius: 10px;")

        # Timer setup
        self.default_duration = 25 * 60
        self.time_left = self.default_duration
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        # MP3 Sound setup
        self.player = QMediaPlayer()
        alert_path = os.path.join(os.path.dirname(__file__), "alert.mp3")
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(alert_path)))

        # Timer display
        self.label = QLineEdit(self.format_time(self.time_left))
        self.label.setFont(QFont("Arial", 32, QFont.Bold))
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setReadOnly(False)
        self.label.setStyleSheet("""
            QLineEdit {
                color: #ffa500;  /* orange text */
                background-color: transparent;
                border: none;
            }
        """)
        self.label.returnPressed.connect(self.set_custom_time)
        self.label.installEventFilter(self)  # For draggable inside QLineEdit

        # Buttons
        self.start_btn = QPushButton("Start")
        self.pause_btn = QPushButton("Pause")
        self.reset_btn = QPushButton("Reset")
        self.close_btn = QPushButton("✕")
        self.start_btn.setFixedSize(60, 30)
        self.pause_btn.setFixedSize(60, 30)
        self.reset_btn.setFixedSize(60, 30)
        self.close_btn.setFixedSize(25, 25)

        self.start_btn.clicked.connect(self.start_timer)
        self.pause_btn.clicked.connect(self.pause_timer)
        self.reset_btn.clicked.connect(self.reset_timer)
        self.close_btn.clicked.connect(self.close)

        # Layouts
        top_layout = QHBoxLayout()
        top_layout.addStretch()
        top_layout.addWidget(self.close_btn)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.pause_btn)
        button_layout.addWidget(self.reset_btn)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.label)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        # Drag support
        self.old_pos = None
        self.move(400, 300)  # Show visibly


    def format_time(self, seconds):
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02}:{secs:02}"

    def start_timer(self):
        if not self.timer.isActive():
            self.timer.start(1000)

    def pause_timer(self):
        if self.timer.isActive():
            self.timer.stop()

    def reset_timer(self):
        self.timer.stop()
        self.time_left = self.default_duration
        self.label.setText(self.format_time(self.time_left))

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.label.setText(self.format_time(self.time_left))
        else:
            self.timer.stop()
            self.label.setText("Over!")
            self.player.play()


    def set_custom_time(self):
        text = self.label.text().strip()
        try:
            mins, secs = map(int, text.split(":"))
            self.time_left = mins * 60 + secs
        except:
            self.label.setText(self.format_time(self.time_left))

    # Make whole window draggable
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    # Allow dragging on QLineEdit too
    def eventFilter(self, source, event):
        if source == self.label:
            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                self.old_pos = event.globalPos()
                return True
            elif event.type() == QEvent.MouseMove and self.old_pos:
                delta = QPoint(event.globalPos() - self.old_pos)
                self.move(self.x() + delta.x(), self.y() + delta.y())
                self.old_pos = event.globalPos()
                return True
            elif event.type() == QEvent.MouseButtonRelease:
                self.old_pos = None
                return True
        return super().eventFilter(source, event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    sticky = PomodoroSticky()
    sticky.show()
    sys.exit(app.exec_())
