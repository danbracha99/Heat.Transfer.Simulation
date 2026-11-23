from PySide6.QtWidgets import (
    QApplication, QWidget, QFrame, QLabel, QPushButton, QSlider,
    QDoubleSpinBox, QComboBox, QCheckBox, QVBoxLayout, QHBoxLayout, QFormLayout
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
        self.setGeometry(100, 100, 780, 490)

        # ----- Top Visual Arena (Bodies physically connected by the grey bar) -----
        visual_card = QFrame()
        visual_card.setObjectName("card")

        self.left_slider, self.left_body_box = self.create_visual_pair(200.0, is_left=True)
        self.right_slider, self.right_body_box = self.create_visual_pair(0.0, is_left=False)

        self.bridge_box = QLabel("0.0 W")
        self.bridge_box.setFixedSize(175, 36)
        self.bridge_box.setAlignment(Qt.AlignCenter)
        self.update_bridge_visual(0.0)

        apparatus_layout = QHBoxLayout()
        apparatus_layout.setSpacing(0)
        apparatus_layout.addStretch()
        apparatus_layout.addWidget(self.left_slider)
        apparatus_layout.addSpacing(14)
        apparatus_layout.addWidget(self.left_body_box)
        apparatus_layout.addWidget(self.bridge_box, alignment=Qt.AlignVCenter)
        apparatus_layout.addWidget(self.right_body_box)
        apparatus_layout.addSpacing(14)
        apparatus_layout.addWidget(self.right_slider)
        apparatus_layout.addStretch()

        visual_layout = QVBoxLayout(visual_card)
        visual_layout.setContentsMargins(18, 18, 18, 18)
        visual_layout.addLayout(apparatus_layout)

        # ----- Bottom Controls Row -----
        left_card, self.left_mat, self.left_temp, self.left_mass, self.left_cap = self.create_body_card("BODY 1", 200.0)
        right_card, self.right_mat, self.right_temp, self.right_mass, self.right_cap = self.create_body_card("BODY 2", 0.0)

        center_card = QFrame()
        center_card.setObjectName("card")

        cond_title = QLabel("CONDUCTIVITY")
        cond_title.setObjectName("section_title")
        cond_title.setAlignment(Qt.AlignCenter)

        self.conductivity_box = QDoubleSpinBox()
        self.conductivity_box.setRange(0.01, 500.0)
        self.conductivity_box.setDecimals(2)
        self.conductivity_box.setSingleStep(0.1)
        self.conductivity_box.setSuffix(" J/s°C")
        self.conductivity_box.setValue(1.00)
        self.conductivity_box.setAlignment(Qt.AlignCenter)

        self.start_button = QPushButton("Start")
        self.start_button.setObjectName("start_btn")
        self.start_button.setCheckable(True)
        self.start_button.toggled.connect(self.start_stop_button_method)

        self.auto_stop_checkbox = QCheckBox("Auto-stop at equilibrium")
        self.auto_stop_checkbox.setChecked(True)

        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("status_lbl")
        self.status_label.setAlignment(Qt.AlignCenter)

        graphs_btn = QPushButton("Graphs")
        graphs_btn.clicked.connect(self.open_graph_window)

        about_btn = QPushButton("About")
        about_btn.clicked.connect(self.about_window.show)

        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(8)
        buttons_row.addWidget(graphs_btn)
        buttons_row.addWidget(about_btn)

        center_col = QVBoxLayout(center_card)
        center_col.setContentsMargins(16, 16, 16, 16)
        center_col.setSpacing(10)
        center_col.addWidget(cond_title)
        center_col.addWidget(self.conductivity_box)
        center_col.addStretch()
        center_col.addWidget(self.start_button)
        center_col.addWidget(self.auto_stop_checkbox)
        center_col.addWidget(self.status_label)
        center_col.addLayout(buttons_row)

        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(14)
        bottom_row.addWidget(left_card, 1)
        bottom_row.addWidget(center_card, 1)
        bottom_row.addWidget(right_card, 1)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(14)
        main_layout.addWidget(visual_card)
        main_layout.addLayout(bottom_row)

        self.left_slider.valueChanged.connect(lambda v: self.on_slider_changed(v, self.left_temp, self.left_body_box, True))
        self.right_slider.valueChanged.connect(lambda v: self.on_slider_changed(v, self.right_temp, self.right_body_box, False))
        self.timer.timeout.connect(self.timer_method)

    def create_visual_pair(self, init_temp, is_left):
        slider = QSlider(Qt.Vertical)
        slider.setRange(0, 200)
        slider.setValue(int(init_temp))
        slider.setFixedHeight(145)

        box = QLabel()
        box.setFixedSize(130, 145)
        box.setAlignment(Qt.AlignCenter)
        self.update_body_visual(box, init_temp, is_left)
        return slider, box

    def create_body_card(self, title_text, init_temp):
        card = QFrame()
        card.setObjectName("card")

        title = QLabel(title_text)
        title.setObjectName("section_title")
        title.setAlignment(Qt.AlignCenter)

        mat_combo = QComboBox()
        mat_combo.addItems(list(MATERIALS.keys()))

        temp_label = QLabel(f"{init_temp:.1f} °C")
        temp_label.setObjectName("temp_label")
        temp_label.setAlignment(Qt.AlignCenter)

        mass_box = QDoubleSpinBox()
        mass_box.setRange(0.01, 1000.0)
        mass_box.setDecimals(2)
        mass_box.setSuffix(" kg")
        mass_box.setValue(10.0)

        cap_box = QDoubleSpinBox()
        cap_box.setRange(0.01, 50.0)
        cap_box.setDecimals(2)
        cap_box.setSingleStep(0.05)
        cap_box.setSuffix(" J/kg°C")
        cap_box.setValue(0.40)

        mat_combo.currentTextChanged.connect(lambda m: self.on_material_changed(m, cap_box))
        cap_box.valueChanged.connect(lambda: mat_combo.setCurrentText("Custom"))

        form = QFormLayout()
        form.setSpacing(8)
        form.addRow("Material:", mat_combo)
        form.addRow("Temp.:", temp_label)
        form.addRow("Mass:", mass_box)
        form.addRow("H. Cap.:", cap_box)

        col = QVBoxLayout(card)
        col.setContentsMargins(16, 16, 16, 16)
        col.setSpacing(10)
        col.addWidget(title)
        col.addLayout(form)
        return card, mat_combo, temp_label, mass_box, cap_box

    def update_body_visual(self, widget, temp, is_left):
        red = max(0, min(255, int((temp / 200.0) * 255)))
        corners = (
            "border-top-left-radius: 12px; border-bottom-left-radius: 12px;"
            if is_left else
            "border-top-right-radius: 12px; border-bottom-right-radius: 12px;"
        )
        widget.setText(f"{temp:.1f} °C")
        widget.setStyleSheet(
            f"background-color: rgb({red}, 0, 0); color: #ffffff; "
            f"font-size: 16px; font-weight: bold; border: 2px solid #94a3b8; {corners}"
        )

    def update_bridge_visual(self, heat_flow, eq=False):
        if eq:
            text, border = "EQUILIBRIUM", "#10b981"
        elif heat_flow > 0.05:
            text, border = f"{heat_flow:.1f} W  →", "#94a3b8"
        elif heat_flow < -0.05:
            text, border = f"←  {abs(heat_flow):.1f} W", "#94a3b8"
        else:
            text, border = "0.0 W", "#94a3b8"

        self.bridge_box.setText(text)
        self.bridge_box.setStyleSheet(
            f"background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, "
            f"stop:0 #64748b, stop:0.5 #94a3b8, stop:1 #475569); "
            f"color: #f8fafc; font-weight: bold; "
            f"border-top: 2px solid {border}; border-bottom: 2px solid {border};"
        )

    def on_slider_changed(self, value, label, box, is_left):
        label.setText(f"{value:.1f} °C")
        self.update_body_visual(box, float(value), is_left)

    def on_material_changed(self, material_name, cap_box):
        cap = MATERIALS[material_name]
        if cap is not None:
            cap_box.blockSignals(True)
            cap_box.setValue(cap)
            cap_box.blockSignals(False)

    def open_graph_window(self):
        if len(self.graph_window.plotted_bodies) == 0:
            self.graph_window.plotted_bodies = ["Body 1", "Body 2"]
        self.graph_window.show()
        self.graph_window.update_plot()

    def set_inputs_enabled(self, enabled):
        for widget in (
            self.left_slider, self.right_slider,
            self.left_mass, self.left_cap, self.left_mat,
            self.right_mass, self.right_cap, self.right_mat,
            self.conductivity_box
        ):
            widget.setEnabled(enabled)

    def start_stop_button_method(self, checked):
        if checked:
            m1, c1 = self.left_mass.value(), self.left_cap.value()
            m2, c2 = self.right_mass.value(), self.right_cap.value()
            if m1 <= 0 or c1 <= 0 or m2 <= 0 or c2 <= 0:
                self.status_label.setText("Invalid mass or heat capacity")
                self.start_button.setChecked(False)
                return

            self.start_button.setText("Stop")
            self.set_inputs_enabled(False)
            self.status_label.setText("Running... (0.0 s)")

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
            if self.status_label.text().startswith("Running"):
                self.update_bridge_visual(0.0)
                self.status_label.setText(f"Stopped ({self.time_elapsed:.1f} s)")

    def timer_method(self):
        dt = 0.01
        sigma = self.conductivity_box.value()
        t1, t2 = self.body1.temperature, self.body2.temperature

        i1 = sigma * (t2 - t1)
        i2 = sigma * (t1 - t2)

        new_t1 = self.body1.add_heat(i1 * dt)
        new_t2 = self.body2.add_heat(i2 * dt)

        self.step_counter += 1
        self.time_elapsed = round(self.time_elapsed + dt, 2)
        self.status_label.setText(f"Running... ({self.time_elapsed:.1f} s)")

        self.time_history.append(self.time_elapsed)
        self.body1_temp_history.append(new_t1)
        self.body2_temp_history.append(new_t2)

        for slider, label, box, temp, is_left in (
            (self.left_slider, self.left_temp, self.left_body_box, new_t1, True),
            (self.right_slider, self.right_temp, self.right_body_box, new_t2, False)
        ):
            slider.blockSignals(True)
            slider.setValue(int(round(temp)))
            slider.blockSignals(False)
            label.setText(f"{temp:.1f} °C")
            self.update_body_visual(box, temp, is_left)

        if self.graph_window.isVisible() and self.step_counter % 5 == 0:
            self.graph_window.update_plot()

        if self.auto_stop_checkbox.isChecked() and abs(new_t1 - new_t2) < 0.1:
            self.status_label.setText(f"Equilibrium ({self.time_elapsed:.1f} s)")
            self.update_bridge_visual(0.0, eq=True)
            self.start_button.setChecked(False)
        else:
            self.update_bridge_visual(i2)

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