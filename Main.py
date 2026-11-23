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

        self.left_slider.valueChanged.connect(self.left_temperature_changed)
        self.right_slider.valueChanged.connect(self.right_temperature_changed)

        self.left_material_combo.currentTextChanged.connect(self.left_material_changed)
        self.right_material_combo.currentTextChanged.connect(self.right_material_changed)
        self.left_cap_box.valueChanged.connect(self.left_cap_manual_changed)
        self.right_cap_box.valueChanged.connect(self.right_cap_manual_changed)

        self.start_button.toggled.connect(self.start_stop_button_method)
        self.timer.timeout.connect(self.timer_method)

    def closeEvent(self, event):
        self.graph_window.close()
        self.about_window.close()

    def update_body_color(self, widget, temp):
        red = max(0, min(255, int((temp / 200.0) * 255)))
        widget.setStyleSheet(f"background-color: rgb({red}, 0, 0); border-radius: 8px;")

    def left_temperature_changed(self, value):
        self.left_temp_box.setValue(float(value))
        self.update_body_color(self.left_body_box, value)

    def right_temperature_changed(self, value):
        self.right_temp_box.setValue(float(value))
        self.update_body_color(self.right_body_box, value)

    def left_material_changed(self, material_name):
        cap = MATERIALS[material_name]
        if cap is not None:
            self.left_cap_box.blockSignals(True)
            self.left_cap_box.setValue(cap)
            self.left_cap_box.blockSignals(False)

    def right_material_changed(self, material_name):
        cap = MATERIALS[material_name]
        if cap is not None:
            self.right_cap_box.blockSignals(True)
            self.right_cap_box.setValue(cap)
            self.right_cap_box.blockSignals(False)

    def left_cap_manual_changed(self):
        self.left_material_combo.setCurrentText("Custom")

    def right_cap_manual_changed(self):
        self.right_material_combo.setCurrentText("Custom")

    def set_inputs_enabled(self, enabled):
        self.left_slider.setEnabled(enabled)
        self.right_slider.setEnabled(enabled)
        self.left_mass_box.setEnabled(enabled)
        self.left_cap_box.setEnabled(enabled)
        self.left_material_combo.setEnabled(enabled)
        self.right_mass_box.setEnabled(enabled)
        self.right_cap_box.setEnabled(enabled)
        self.right_material_combo.setEnabled(enabled)
        self.conductivity_box.setEnabled(enabled)

    def start_stop_button_method(self, checked):
        if checked:
            self.start_button.setText("Stop")
            self.set_inputs_enabled(False)
            self.status_label.setText("Running...")

            self.body1 = Body(
                self.left_mass_box.value(),
                self.left_cap_box.value(),
                self.left_temp_box.value()
            )
            self.body2 = Body(
                self.right_mass_box.value(),
                self.right_cap_box.value(),
                self.right_temp_box.value()
            )

            self.time_elapsed = 0.0
            self.time_history = [0.0]
            self.body1_temp_history = [self.body1.temperature]
            self.body2_temp_history = [self.body2.temperature]

            self.timer.start(100)
        else:
            self.timer.stop()
            self.start_button.setText("Start")
            self.set_inputs_enabled(True)
            if self.status_label.text() == "Running...":
                self.status_label.setText("Paused")

    def timer_method(self):
        dt = 0.01
        sigma = self.conductivity_box.value()

        t1 = self.body1.temperature
        t2 = self.body2.temperature

        i1 = sigma * (t2 - t1)
        i2 = sigma * (t1 - t2)

        dq1 = i1 * dt
        dq2 = i2 * dt

        new_t1 = self.body1.add_heat(dq1)
        new_t2 = self.body2.add_heat(dq2)

        self.time_elapsed = round(self.time_elapsed + dt, 2)
        self.time_history.append(self.time_elapsed)
        self.body1_temp_history.append(new_t1)
        self.body2_temp_history.append(new_t2)

        self.left_slider.blockSignals(True)
        self.left_slider.setValue(int(round(new_t1)))
        self.left_slider.blockSignals(False)
        self.left_temp_box.setValue(new_t1)
        self.update_body_color(self.left_body_box, new_t1)

        self.right_slider.blockSignals(True)
        self.right_slider.setValue(int(round(new_t2)))
        self.right_slider.blockSignals(False)
        self.right_temp_box.setValue(new_t2)
        self.update_body_color(self.right_body_box, new_t2)

        if self.auto_stop_checkbox.isChecked() and abs(new_t1 - new_t2) < 0.01:
            self.status_label.setText("Equilibrium reached")
            self.start_button.setChecked(False)


if __name__ == "__main__":
    app = QApplication()
    with open("style.qss") as f:
        app.setStyleSheet(f.read())
    window = HeatTransfer()
    window.show()
    app.exec()