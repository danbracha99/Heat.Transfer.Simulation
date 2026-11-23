from about_window import AboutWindow
from graph_window import GraphWindow
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QSlider,
    QDoubleSpinBox, QComboBox, QCheckBox, QAbstractSpinBox,
    QVBoxLayout, QHBoxLayout, QFormLayout
)
from PySide6.QtCore import Qt, QTimer
from Body import Body

MATERIALS = {
    "Custom": None,
    "Copper": 0.39,
    "Iron": 0.45,
    "Aluminum": 0.90,
    "Water": 4.18,
}


class HeatTransfer(QWidget):
    def __init__(self):
        super().__init__()
        self.body1 = None
        self.body2 = None
        self.time_elapsed = 0.0
        self.time_history = []
        self.body1_temp_history = []
        self.body2_temp_history = []

        self.graph_window = GraphWindow(self)
        self.about_window = AboutWindow()
        self.timer = QTimer(self)
        self.setupUI()
        

    def setupUI(self):
        self.setWindowTitle("Heat Transfer Simulation")
        self.setGeometry(100, 100, 720, 420)

        # ----- left body -----
        self.left_material_combo = QComboBox()
        self.left_material_combo.addItems(list(MATERIALS.keys()))

        self.left_slider = QSlider(Qt.Vertical)
        self.left_slider.setRange(0, 200)
        self.left_slider.setValue(200)

        self.left_body_box = QLabel()
        self.left_body_box.setFixedSize(110, 150)
        self.left_body_box.setStyleSheet("background-color: rgb(255, 0, 0); border-radius: 8px;")

        left_visual_layout = QHBoxLayout()
        left_visual_layout.addWidget(self.left_slider)
        left_visual_layout.addWidget(self.left_body_box)

        self.left_temp_box = QDoubleSpinBox()
        self.left_temp_box.setRange(0.0, 200.0)
        self.left_temp_box.setDecimals(1)
        self.left_temp_box.setSuffix(" °C")
        self.left_temp_box.setValue(200.0)
        self.left_temp_box.setReadOnly(True)
        self.left_temp_box.setButtonSymbols(QAbstractSpinBox.NoButtons)

        self.left_mass_box = QDoubleSpinBox()
        self.left_mass_box.setRange(0.1, 1000.0)
        self.left_mass_box.setDecimals(2)
        self.left_mass_box.setSuffix(" kg")
        self.left_mass_box.setValue(10.0)

        self.left_cap_box = QDoubleSpinBox()
        self.left_cap_box.setRange(0.05, 50.0)
        self.left_cap_box.setDecimals(2)
        self.left_cap_box.setSingleStep(0.05)
        self.left_cap_box.setSuffix(" J/kg°C")
        self.left_cap_box.setValue(0.40)

        left_form = QFormLayout()
        left_form.addRow("Material:", self.left_material_combo)
        left_form.addRow("Temp.:", self.left_temp_box)
        left_form.addRow("Mass:", self.left_mass_box)
        left_form.addRow("H. Cap.:", self.left_cap_box)

        left_col = QVBoxLayout()
        left_col.addLayout(left_visual_layout)
        left_col.addLayout(left_form)

        # ----- center controls -----
        cond_label = QLabel("Conductivity")
        cond_label.setAlignment(Qt.AlignCenter)

        self.conductivity_box = QDoubleSpinBox()
        self.conductivity_box.setRange(0.01, 500.0)
        self.conductivity_box.setDecimals(2)
        self.conductivity_box.setSingleStep(0.1)
        self.conductivity_box.setSuffix(" J/s°C")
        self.conductivity_box.setValue(1.00)

        self.bridge_box = QLabel()
        self.bridge_box.setFixedSize(160, 26)
        self.bridge_box.setStyleSheet("background-color: #94a3b8;")

        self.start_button = QPushButton("Start")
        self.start_button.setObjectName("start_btn")
        self.start_button.setCheckable(True)

        self.auto_stop_checkbox = QCheckBox("Auto-stop at equilibrium")
        self.auto_stop_checkbox.setChecked(True)

        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)

        self.graphs_button = QPushButton("Graphs")
        self.about_button = QPushButton("About")
        self.about_button.clicked.connect(self.about_window.show)
        self.graphs_button.clicked.connect(self.graph_window.show)

        center_col = QVBoxLayout()
        center_col.addWidget(cond_label)
        center_col.addWidget(self.conductivity_box)
        center_col.addSpacing(20)
        center_col.addWidget(self.bridge_box, alignment=Qt.AlignCenter)
        center_col.addStretch()
        center_col.addWidget(self.start_button)
        center_col.addWidget(self.auto_stop_checkbox)
        center_col.addWidget(self.status_label)
        center_col.addSpacing(8)
        center_col.addWidget(self.graphs_button)
        center_col.addWidget(self.about_button)

        # ----- right body -----
        self.right_material_combo = QComboBox()
        self.right_material_combo.addItems(list(MATERIALS.keys()))

        self.right_slider = QSlider(Qt.Vertical)
        self.right_slider.setRange(0, 200)
        self.right_slider.setValue(0)

        self.right_body_box = QLabel()
        self.right_body_box.setFixedSize(110, 150)
        self.right_body_box.setStyleSheet("background-color: rgb(0, 0, 0); border-radius: 8px;")

        right_visual_layout = QHBoxLayout()
        right_visual_layout.addWidget(self.right_body_box)
        right_visual_layout.addWidget(self.right_slider)

        self.right_temp_box = QDoubleSpinBox()
        self.right_temp_box.setRange(0.0, 200.0)
        self.right_temp_box.setDecimals(1)
        self.right_temp_box.setSuffix(" °C")
        self.right_temp_box.setValue(0.0)
        self.right_temp_box.setReadOnly(True)
        self.right_temp_box.setButtonSymbols(QAbstractSpinBox.NoButtons)

        self.right_mass_box = QDoubleSpinBox()
        self.right_mass_box.setRange(0.1, 1000.0)
        self.right_mass_box.setDecimals(2)
        self.right_mass_box.setSuffix(" kg")
        self.right_mass_box.setValue(10.0)

        self.right_cap_box = QDoubleSpinBox()
        self.right_cap_box.setRange(0.05, 50.0)
        self.right_cap_box.setDecimals(2)
        self.right_cap_box.setSingleStep(0.05)
        self.right_cap_box.setSuffix(" J/kg°C")
        self.right_cap_box.setValue(0.40)

        right_form = QFormLayout()
        right_form.addRow("Material:", self.right_material_combo)
        right_form.addRow("Temp.:", self.right_temp_box)
        right_form.addRow("Mass:", self.right_mass_box)
        right_form.addRow("H. Cap.:", self.right_cap_box)

        right_col = QVBoxLayout()
        right_col.addLayout(right_visual_layout)
        right_col.addLayout(right_form)

        # ----- main layout -----
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(24)
        main_layout.addLayout(left_col)
        main_layout.addLayout(center_col)
        main_layout.addLayout(right_col)
        self.setLayout(main_layout)
        
def closeEvent(self, event):
        self.graph_window.close()
        self.about_window.close()


if __name__ == "__main__":
    app = QApplication()
    with open("style.qss") as f:
        app.setStyleSheet(f.read())
    window = HeatTransfer()
    window.show()
    app.exec()