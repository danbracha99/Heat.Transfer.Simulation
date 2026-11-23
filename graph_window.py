import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from PySide6.QtWidgets import (
    QWidget, QFrame, QComboBox, QPushButton, QVBoxLayout, QHBoxLayout
)


class GraphWindow(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.plotted_bodies = []
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle("Graph Window")
        self.setGeometry(890, 180, 650, 440)

        plot_card = QFrame()
        plot_card.setObjectName("card")
        plot_layout = QVBoxLayout()
        plot_layout.setContentsMargins(10, 10, 10, 10)

        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.style_axes()
        plot_layout.addWidget(self.canvas)
        plot_card.setLayout(plot_layout)

        controls_card = QFrame()
        controls_card.setObjectName("card")

        self.body_combo = QComboBox()
        self.body_combo.addItems(["Body 1", "Body 2"])

        self.draw_button = QPushButton("Draw")
        self.draw_button.clicked.connect(self.draw_clicked)

        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_clicked)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_clicked)

        self.export_button = QPushButton("Export to CSV")
        self.export_button.clicked.connect(self.export_csv_clicked)

        controls_layout = QVBoxLayout()
        controls_layout.setContentsMargins(14, 14, 14, 14)
        controls_layout.setSpacing(12)
        controls_layout.addWidget(self.body_combo)
        controls_layout.addWidget(self.draw_button)
        controls_layout.addWidget(self.remove_button)
        controls_layout.addWidget(self.clear_button)
        controls_layout.addWidget(self.export_button)
        controls_layout.addStretch()
        controls_card.setLayout(controls_layout)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(14)
        main_layout.addWidget(plot_card, 3)
        main_layout.addWidget(controls_card, 1)
        self.setLayout(main_layout)

    def style_axes(self):
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Temperature (°C)")
        self.ax.set_title("Temperature vs. Time")
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.grid(True, linestyle="--", alpha=0.5)
        self.fig.tight_layout()

    def draw_clicked(self):
        selected = self.body_combo.currentText()
        if selected not in self.plotted_bodies:
            self.plotted_bodies.append(selected)
        self.update_plot()

    def remove_clicked(self):
        selected = self.body_combo.currentText()
        if selected in self.plotted_bodies:
            self.plotted_bodies.remove(selected)
        self.update_plot()

    def update_plot(self):
        self.ax.clear()
        self.style_axes()

        if self.main_window is None:
            self.canvas.draw()
            return

        t = self.main_window.time_history
        if len(t) == 0 or len(self.plotted_bodies) == 0:
            self.canvas.draw()
            return

        if "Body 1" in self.plotted_bodies:
            self.ax.plot(
                t, self.main_window.body1_temp_history,
                color="#dc2626", linewidth=2, label="Body 1"
            )
        if "Body 2" in self.plotted_bodies:
            self.ax.plot(
                t, self.main_window.body2_temp_history,
                color="#2563eb", linewidth=2, label="Body 2"
            )

        self.ax.legend()
        self.canvas.draw()

    def clear_clicked(self):
        self.plotted_bodies = []
        self.ax.clear()
        self.style_axes()
        self.canvas.draw()

    def export_csv_clicked(self):
        if self.main_window is None:
            return
        t = self.main_window.time_history
        t1 = self.main_window.body1_temp_history
        t2 = self.main_window.body2_temp_history
        if len(t) == 0:
            return

        filename = "heat_transfer_results.csv"
        with open(filename, "w") as f:
            f.write("Time (s),Body 1 Temp (C),Body 2 Temp (C)\n")
            for i in range(len(t)):
                f.write(f"{t[i]:.2f},{t1[i]:.4f},{t2[i]:.4f}\n")

        if hasattr(os, "startfile"):
            os.startfile(filename)