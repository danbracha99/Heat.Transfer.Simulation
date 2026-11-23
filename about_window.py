from PySide6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout
from PySide6.QtGui import QPixmap, QPainter, QColor
from PySide6.QtCore import Qt


class AboutWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle("About - Heat Conduction")
        self.setGeometry(850, 120, 340, 280)

        title_label = QLabel("Heat Conduction Simulation")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 17px; font-weight: bold; color: #0f172a;")

        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setPixmap(self.create_diagram_pixmap())

        desc_label = QLabel(
            "Mechatronics Programming Assignment\n"
            "2-Body Thermal Conduction Model\n"
            "Created by: Dan Bracha"
        )
        desc_label.setAlignment(Qt.AlignCenter)

        repo_url = "https://github.com/danbracha99/Heat.Transfer.Simulation"
        link_label = QLabel(f'<a href="{repo_url}">GitHub Project Repository</a>')
        link_label.setAlignment(Qt.AlignCenter)
        link_label.setOpenExternalLinks(True)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.hide)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        layout.addWidget(title_label)
        layout.addWidget(image_label)
        layout.addWidget(desc_label)
        layout.addWidget(link_label)
        layout.addStretch()
        layout.addWidget(close_button)
        self.setLayout(layout)

    def create_diagram_pixmap(self):
        pixmap = QPixmap(240, 70)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        painter.setBrush(QColor(220, 38, 38))
        painter.drawRoundedRect(15, 10, 60, 50, 6, 6)

        painter.setBrush(QColor(148, 163, 184))
        painter.drawRect(75, 27, 90, 16)

        painter.setBrush(QColor(15, 23, 42))
        painter.drawRoundedRect(165, 10, 60, 50, 6, 6)
        painter.end()
        return pixmap