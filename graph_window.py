import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtWidgets import (
    QWidget, QComboBox, QPushButton, QVBoxLayout, QHBoxLayout
)


class GraphWindow(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle("Graph Window")
        self.setGeometry(850, 250, 620, 420)

        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.style_axes()

        self.body_combo = QComboBox()
        self.body_combo.addItems(["Body 1", "Body 2"])

        self.draw_button = QPushButton("Draw")
        self.clear_button = QPushButton("Clear")
        self.export_button = QPushButton("Export to CSV")

        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(12)
        controls_layout.addWidget(self.body_combo)
        controls_layout.addWidget(self.draw_button)
        controls_layout.addWidget(self.clear_button)
        controls_layout.addWidget(self.export_button)
        controls_layout.addStretch()

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        main_layout.addWidget(self.canvas, 3)
        main_layout.addLayout(controls_layout, 1)
        self.setLayout(main_layout)

    def style_axes(self):
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Temperature (°C)")
        self.ax.set_title("Temperature vs. Time")
        self.ax.grid(True, linestyle="--", alpha=0.5)
        self.fig.tight_layout()