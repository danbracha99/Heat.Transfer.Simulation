from PySide6.QtWidgets import (
    QApplication, QWidget, QFrame, QLabel, QPushButton, QSlider,
    QDoubleSpinBox, QComboBox, QCheckBox,
    QVBoxLayout, QHBoxLayout, QFormLayout
)
from PySide6.QtCore import Qt, QTimer
from Body import Body
from about_window import AboutWindow
from graph_window import GraphWindow

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
        self.about_window = AboutWindow()
        self.graph_window = GraphWindow(self)

        self.body1 = None
        self.body2 = None
        self.time_elapsed = 0.0
        self.step_counter = 0
        self.time_history = []
        self.body1_temp_history = []
        self.body2_temp_history = []

        self.timer = QTimer(self)
        self.setupUI()

    def setupUI(self):
        self.setWindowTitle("Heat Transfer Simulation")
        self.setGeometry(100, 100, 780, 450)

        # ----- left body card -----
        left_card = QFrame()
        left_card.setObjectName("card")

        left_title = QLabel("Body 1")
        left_title.setObjectName("section_title")
        left_title.setAlignment(Qt.AlignCenter)

        self.left_material_combo = QComboBox()
        self.left_material_combo.addItems(list(MATERIALS.keys()))
        self.left_material_combo.currentTextChanged.connect(self.left_material_changed)

        self.left_slider = QSlider(Qt.Vertical)
        self.left_slider.setRange(0, 200)
        self.left_slider.setValue(200)
        self.left_slider.valueChanged.connect(self.left_temperature_changed)

        self.left_body_box = QLabel("200.0 °C")
        self.left_body_box.setFixedSize(115, 145)
        self.left_body_box.setAlignment(Qt.AlignCenter)
        self.update_body_visual(self.left_body_box, 200.0)

        left_visual_layout = QHBoxLayout()
        left_visual_layout.addWidget(self.left_slider)
        left_visual_layout.addWidget(self.left_body_box)

        self.left_temp_label = QLabel("200.0 °C")
        self.left_temp_label.setObjectName("temp_label")
        self.left_temp_label.setAlignment(Qt.AlignCenter)
        self.left_temp_label.setMinimumWidth(120)

        self.left_mass_box = QDoubleSpinBox()
        self.left_mass_box.setRange(0.01, 1000.0)
        self.left_mass_box.setDecimals(2)
        self.left_mass_box.setSuffix(" kg")
        self.left_mass_box.setValue(10.0)
        self.left_mass_box.setMinimumWidth(120)

        self.left_cap_box = QDoubleSpinBox()
        self.left_cap_box.setRange(0.01, 50.0)
        self.left_cap_box.setDecimals(2)
        self.left_cap_box.setSingleStep(0.05)
        self.left_cap_box.setSuffix(" J/kg°C")
        self.left_cap_box.setValue(0.40)
        self.left_cap_box.setMinimumWidth(120)
        self.left_cap_box.valueChanged.connect(self.left_cap_manual_changed)

        left_form = QFormLayout()
        left_form.setSpacing(8)
        left_form.addRow("Material:", self.left_material_combo)
        left_form.addRow("Temp.:", self.left_temp_label)
        left_form.addRow("Mass:", self.left_mass_box)
        left_form.addRow("H. Cap.:", self.left_cap_box)

        left_col = QVBoxLayout()
        left_col.setContentsMargins(16, 16, 16, 16)
        left_col.setSpacing(12)
        left_col.addWidget(left_title)
        left_col.addLayout(left_visual_layout)
        left_col.addLayout(left_form)
        left_card.setLayout(left_col)

        # ----- center controls card -----
        center_card = QFrame()
        center_card.setObjectName("card")

        cond_title = QLabel("Conductivity")
        cond_title.setObjectName("section_title")
        cond_title.setAlignment(Qt.AlignCenter)

        self.conductivity_box = QDoubleSpinBox()
        self.conductivity_box.setRange(0.01, 500.0)
        self.conductivity_box.setDecimals(2)
        self.conductivity_box.setSingleStep(0.1)
        self.conductivity_box.setSuffix(" J/s°C")
        self.conductivity_box.setValue(1.00)
        self.conductivity_box.setAlignment(Qt.AlignCenter)

        self.bridge_box = QLabel()
        self.bridge_box.setFixedSize(160, 22)
        self.bridge_box.setStyleSheet("background-color: #94a3b8; border-radius: 4px;")

        self.start_button = QPushButton("Start")
        self.start_button.setObjectName("start_btn")
        self.start_button.setCheckable(True)
        self.start_button.toggled.connect(self.start_stop_button_method)

        self.auto_stop_checkbox = QCheckBox("Auto-stop at equilibrium")
        self.auto_stop_checkbox.setChecked(True)

        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("status_lbl")
        self.status_label.setAlignment(Qt.AlignCenter)

        self.graphs_button = QPushButton("Graphs")
        self.graphs_button.clicked.connect(self.open_graph_window)

        self.about_button = QPushButton("About")
        self.about_button.clicked.connect(self.about_window.show)

        center_col = QVBoxLayout()
        center_col.setContentsMargins(16, 16, 16, 16)
        center_col.setSpacing(10)
        center_col.addWidget(cond_title)
        center_col.addWidget(self.conductivity_box)
        center_col.addSpacing(14)
        center_col.addWidget(self.bridge_box, alignment=Qt.AlignCenter)
        center_col.addStretch()
        center_col.addWidget(self.start_button)
        center_col.addWidget(self.auto_stop_checkbox)
        center_col.addWidget(self.status_label)
        center_col.addSpacing(6)
        center_col.addWidget(self.graphs_button)
        center_col.addWidget(self.about_button)
        center_card.setLayout(center_col)

        # ----- right body card -----
        right_card = QFrame()
        right_card.setObjectName("card")

        right_title = QLabel("Body 2")
        right_title.setObjectName("section_title")
        right_title.setAlignment(Qt.AlignCenter)

        self.right_material_combo = QComboBox()
        self.right_material_combo.addItems(list(MATERIALS.keys()))
        self.right_material_combo.currentTextChanged.connect(self.right_material_changed)

        self.right_slider = QSlider(Qt.Vertical)
        self.right_slider.setRange(0, 200)
        self.right_slider.setValue(0)
        self.right_slider.valueChanged.connect(self.right_temperature_changed)

        self.right_body_box = QLabel("0.0 °C")
        self.right_body_box.setFixedSize(115, 145)
        self.right_body_box.setAlignment(Qt.AlignCenter)
        self.update_body_visual(self.right_body_box, 0.0)

        right_visual_layout = QHBoxLayout()
        right_visual_layout.addWidget(self.right_body_box)
        right_visual_layout.addWidget(self.right_slider)

        self.right_temp_label = QLabel("0.0 °C")
        self.right_temp_label.setObjectName("temp_label")
        self.right_temp_label.setAlignment(Qt.AlignCenter)
        self.right_temp_label.setMinimumWidth(120)

        self.right_mass_box = QDoubleSpinBox()
        self.right_mass_box.setRange(0.01, 1000.0)
        self.right_mass_box.setDecimals(2)
        self.right_mass_box.setSuffix(" kg")
        self.right_mass_box.setValue(10.0)
        self.right_mass_box.setMinimumWidth(120)

        self.right_cap_box = QDoubleSpinBox()
        self.right_cap_box.setRange(0.01, 50.0)
        self.right_cap_box.setDecimals(2)
        self.right_cap_box.setSingleStep(0.05)
        self.right_cap_box.setSuffix(" J/kg°C")
        self.right_cap_box.setValue(0.40)
        self.right_cap_box.setMinimumWidth(120)
        self.right_cap_box.valueChanged.connect(self.right_cap_manual_changed)

        right_form = QFormLayout()
        right_form.setSpacing(8)
        right_form.addRow("Material:", self.right_material_combo)
        right_form.addRow("Temp.:", self.right_temp_label)
        right_form.addRow("Mass:", self.right_mass_box)
        right_form.addRow("H. Cap.:", self.right_cap_box)

        right_col = QVBoxLayout()
        right_col.setContentsMargins(16, 16, 16, 16)
        right_col.setSpacing(12)
        right_col.addWidget(right_title)
        right_col.addLayout(right_visual_layout)
        right_col.addLayout(right_form)
        right_card.setLayout(right_col)

        # ----- main layout -----
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(16)
        main_layout.addWidget(left_card, 1)
        main_layout.addWidget(center_card, 1)
        main_layout.addWidget(right_card, 1)
        self.setLayout(main_layout)

        self.timer.timeout.connect(self.timer_method)

    def update_body_visual(self, widget, temp):
        red = max(0, min(255, int((temp / 200.0) * 255)))
        widget.setText(f"{temp:.1f} °C")
        widget.setStyleSheet(
            f"background-color: rgb({red}, 0, 0); "
            f"color: white; font-size: 16px; font-weight: bold; "
            f"border-radius: 10px; border: 2px solid #94a3b8;"
        )

    def left_temperature_changed(self, value):
        self.left_temp_label.setText(f"{value:.1f} °C")
        self.update_body_visual(self.left_body_box, float(value))

    def right_temperature_changed(self, value):
        self.right_temp_label.setText(f"{value:.1f} °C")
        self.update_body_visual(self.right_body_box, float(value))

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

    def open_graph_window(self):
        if len(self.graph_window.plotted_bodies) == 0:
            self.graph_window.plotted_bodies = ["Body 1", "Body 2"]
        self.graph_window.show()
        self.graph_window.update_plot()

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
            m1 = self.left_mass_box.value()
            c1 = self.left_cap_box.value()
            m2 = self.right_mass_box.value()
            c2 = self.right_cap_box.value()

            if m1 <= 0 or c1 <= 0 or m2 <= 0 or c2 <= 0:
                self.status_label.setText("Invalid mass or heat capacity")
                self.start_button.setChecked(False)
                return

            self.start_button.setText("Stop")
            self.set_inputs_enabled(False)
            self.status_label.setText("Running...")

            self.body1 = Body(m1, c1, float(self.left_slider.value()))
            self.body2 = Body(m2, c2, float(self.right_slider.value()))

            self.time_elapsed = 0.0
            self.step_counter = 0
            self.time_history = [0.0]
            self.body1_temp_history = [self.body1.temperature]
            self.body2_temp_history = [self.body2.temperature]

            if self.graph_window.isVisible():
                self.graph_window.update_plot()

            self.timer.start(10)
        else:
            self.timer.stop()
            self.start_button.setText("Start")
            self.set_inputs_enabled(True)
            if self.graph_window.isVisible():
                self.graph_window.update_plot()
            if self.status_label.text() == "Running...":
                self.status_label.setText("Stopped")

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

        self.step_counter = self.step_counter + 1
        self.time_elapsed = round(self.time_elapsed + dt, 2)
        self.time_history.append(self.time_elapsed)
        self.body1_temp_history.append(new_t1)
        self.body2_temp_history.append(new_t2)

        self.left_slider.blockSignals(True)
        self.left_slider.setValue(int(round(new_t1)))
        self.left_slider.blockSignals(False)
        self.left_temp_label.setText(f"{new_t1:.1f} °C")
        self.update_body_visual(self.left_body_box, new_t1)

        self.right_slider.blockSignals(True)
        self.right_slider.setValue(int(round(new_t2)))
        self.right_slider.blockSignals(False)
        self.right_temp_label.setText(f"{new_t2:.1f} °C")
        self.update_body_visual(self.right_body_box, new_t2)

        if self.graph_window.isVisible() and self.step_counter % 5 == 0:
            self.graph_window.update_plot()

        if self.auto_stop_checkbox.isChecked() and abs(new_t1 - new_t2) < 0.1:
            self.status_label.setText("Equilibrium reached")
            self.start_button.setChecked(False)

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