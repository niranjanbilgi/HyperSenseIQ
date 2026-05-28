import sys
import os
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QTextEdit,
    QTabWidget, QDoubleSpinBox, QGroupBox, QGridLayout, QStatusBar)
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QFont
import json
from datetime import datetime

class AnalysisWorker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, csv_path, params):
        super().__init__()
        self.csv_path = csv_path
        self.q = params["q"]
        self.B = params["B"]
        self.mu = params["mu"]
        self.h = params["h"]
        self.phi = params["phi"]
        self.ct = params["ct"]
        self.rw = params["rw"]
        self.well_name = params["well_name"]

    def run(self):
        try:
            self.progress.emit("Loading pressure test data...")
            df = pd.read_csv(self.csv_path)
            df.columns = df.columns.str.strip().str.lower()
            time_col = None
            pres_col = None
            for c in df.columns:
                if "time" in c:
                    time_col = c
                if "press" in c:
                    pres_col = c
            if time_col is None or pres_col is None:
                self.error.emit("CSV must have columns with time and pressure in name")
                return
            time = df[time_col].values.astype(float)
            pressure = df[pres_col].values.astype(float)
            self.progress.emit("Computing Horner plot...")
            tp = time[-1]
            horner_x = np.log((tp + time) / time)
            horner_y = pressure
            valid = np.isfinite(horner_x) & np.isfinite(horner_y)
            horner_x = horner_x[valid]
            horner_y = horner_y[valid]
            coeffs = np.polyfit(horner_x, horner_y, 1)
            slope = coeffs[0]
            intercept = coeffs[1]
            self.progress.emit("Calculating reservoir properties...")
            if slope != 0:
                permeability = (162.6 * self.q * self.B * self.mu) / (abs(slope) * self.h)
            else:
                permeability = 0
            if permeability > 0 and slope != 0:
                p1hr = slope * 1.0 + intercept
                log_arg = permeability / (self.phi * self.mu * self.ct * self.rw**2)
                if log_arg > 0:
                    skin = 1.151 * ((p1hr - intercept) / abs(slope) - np.log10(log_arg) + 3.2275)
                else:
                    skin = 0
            else:
                skin = 0
            self.progress.emit("Generating visualizations...")
            fig = Figure(figsize=(10, 6), dpi=150)
            ax = fig.add_subplot(111)
            ax.plot(horner_x, horner_y, "bo", linewidth=2, markersize=10, label="Measured Data")
            fit_line = slope * horner_x + intercept
            ax.plot(horner_x, fit_line, "r--", linewidth=2.5, label="Horner Fit")
            ax.set_xlabel("ln((tp+dt)/dt)", fontsize=12)
            ax.set_ylabel("Pressure (psi)", fontsize=12)
            ax.set_title(f"Horner Plot - {self.well_name}", fontsize=14)
            ax.legend()
            ax.grid(True, alpha=0.3)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            plot_file = f"horner_{self.well_name}_{timestamp}.png"
            fig.savefig(plot_file, dpi=300, bbox_inches="tight")
            report = {
                "well": self.well_name,
                "timestamp": datetime.now().isoformat(),
                "permeability_mD": round(permeability, 3),
                "skin": round(skin, 3),
                "horner_slope": round(slope, 6),
                "horner_intercept": round(intercept, 6),
                "data_points": len(time),
                "time_range": [float(time.min()), float(time.max())],
                "pressure_range": [float(pressure.min()), float(pressure.max())]
            }
            json_file = f"pta_report_{self.well_name}_{timestamp}.json"
            with open(json_file, "w") as f:
                json.dump(report, f, indent=2)
            results = {
                "permeability": permeability,
                "skin": skin,
                "slope": slope,
                "intercept": intercept,
                "time": time,
                "pressure": pressure,
                "horner_x": horner_x,
                "horner_y": horner_y,
                "fit_line": fit_line,
                "plot_file": plot_file,
                "json_file": json_file,
                "fig": fig,
                "well_name": self.well_name
            }
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HyperSenseIQ PTA/RTA Analyzer v2.6")
        self.setMinimumSize(1100, 600)
        self.csv_path = None
        self.setup_ui()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        left_panel = QWidget()
        left_panel.setMaximumWidth(600)
        left_layout = QVBoxLayout(left_panel)
        title = QLabel("HyperSenseIQ PTA/RTA Analyzer")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        left_layout.addWidget(title)
        file_group = QGroupBox("Data File")
        file_layout = QVBoxLayout(file_group)
        self.file_label = QLabel("No file selected")
        file_layout.addWidget(self.file_label)
        browse_btn = QPushButton("Browse CSV File")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_btn)
        left_layout.addWidget(file_group)
        params_group = QGroupBox("Well Parameters")
        params_layout = QGridLayout(params_group)
        self.well_name_field = QLineEdit("Assam-Well-01")
        self.q_spin = QDoubleSpinBox()
        self.q_spin.setRange(0.01, 100000)
        self.q_spin.setValue(99.99)
        self.q_spin.setSuffix(" bbl/d")
        self.B_spin = QDoubleSpinBox()
        self.B_spin.setRange(0.1, 10)
        self.B_spin.setValue(1.00)
        self.B_spin.setDecimals(2)
        self.mu_spin = QDoubleSpinBox()
        self.mu_spin.setRange(0.01, 100)
        self.mu_spin.setValue(0.80)
        self.mu_spin.setSuffix(" cp")
        self.h_spin = QDoubleSpinBox()
        self.h_spin.setRange(0.1, 1000)
        self.h_spin.setValue(45.00)
        self.h_spin.setSuffix(" ft")
        self.phi_spin = QDoubleSpinBox()
        self.phi_spin.setRange(0.01, 0.50)
        self.phi_spin.setValue(0.22)
        self.phi_spin.setDecimals(3)
        self.ct_spin = QDoubleSpinBox()
        self.ct_spin.setRange(0.000001, 0.001)
        self.ct_spin.setValue(0.000015)
        self.ct_spin.setDecimals(8)
        self.rw_spin = QDoubleSpinBox()
        self.rw_spin.setRange(0.01, 1.0)
        self.rw_spin.setValue(0.35)
        self.rw_spin.setSuffix(" ft")
        params_layout.addWidget(QLabel("Well Name:"), 0, 0)
        params_layout.addWidget(self.well_name_field, 0, 1)
        params_layout.addWidget(QLabel("Production Rate (q):"), 1, 0)
        params_layout.addWidget(self.q_spin, 1, 1)
        params_layout.addWidget(QLabel("Formation Volume (B):"), 2, 0)
        params_layout.addWidget(self.B_spin, 2, 1)
        params_layout.addWidget(QLabel("Viscosity (u):"), 3, 0)
        params_layout.addWidget(self.mu_spin, 3, 1)
        params_layout.addWidget(QLabel("Pay Thickness (h):"), 4, 0)
        params_layout.addWidget(self.h_spin, 4, 1)
        params_layout.addWidget(QLabel("Porosity (p):"), 5, 0)
        params_layout.addWidget(self.phi_spin, 5, 1)
        params_layout.addWidget(QLabel("Compressibility (ct):"), 6, 0)
        params_layout.addWidget(self.ct_spin, 6, 1)
        params_layout.addWidget(QLabel("Wellbore Radius (rw):"), 7, 0)
        params_layout.addWidget(self.rw_spin, 7, 1)
        left_layout.addWidget(params_group)
        self.run_btn = QPushButton("RUN ANALYSIS")
        self.run_btn.setMinimumHeight(50)
        self.run_btn.setStyleSheet("background-color: #4CAF50; color: white; font-size: 16px; font-weight: bold;")
        self.run_btn.clicked.connect(self.run_analysis)
        left_layout.addWidget(self.run_btn)
        self.status_label = QLabel("Ready")
        left_layout.addWidget(self.status_label)
        left_layout.addStretch()
        right_panel = QTabWidget()
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setFont(QFont("Courier", 10))
        right_panel.addTab(self.results_text, "Results")
        self.plot_widget = QWidget()
        self.plot_layout = QVBoxLayout(self.plot_widget)
        right_panel.addTab(self.plot_widget, "Horner Plot")
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        self.statusBar().showMessage("Ready")

    def browse_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if path:
            self.csv_path = path
            self.file_label.setText(f"File: {os.path.basename(path)}")
            self.statusBar().showMessage(f"Loaded: {os.path.basename(path)}")

    def run_analysis(self):
        if not self.csv_path:
            self.status_label.setText("Please select a CSV file first")
            return
        self.run_btn.setEnabled(False)
        self.run_btn.setText("Analysing...")
        params = {
            "well_name": self.well_name_field.text(),
            "q": self.q_spin.value(),
            "B": self.B_spin.value(),
            "mu": self.mu_spin.value(),
            "h": self.h_spin.value(),
            "phi": self.phi_spin.value(),
            "ct": self.ct_spin.value(),
            "rw": self.rw_spin.value()
        }
        self.worker = AnalysisWorker(self.csv_path, params)
        self.worker.progress.connect(self.update_status)
        self.worker.finished.connect(self.show_results)
        self.worker.error.connect(self.show_error)
        self.worker.start()

    def update_status(self, msg):
        self.status_label.setText(msg)
        self.statusBar().showMessage(msg)

    def show_results(self, results):
        perm = results["permeability"]
        skin = results["skin"]
        slope = results["slope"]
        intercept = results["intercept"]
        time = results["time"]
        pressure = results["pressure"]
        perm_interp = "Low permeability - tight formation" if perm < 10 else "Moderate permeability" if perm < 100 else "Good permeability"
        skin_interp = "Significant formation damage" if skin > 5 else "Moderate damage" if skin > 0 else "Stimulated well" if skin < -2 else "Near-normal condition"
        report_text = f"""HYPERSENSEIQ PTA/RTA ANALYSIS - COMPLETE
============================================================
Well: {results["well_name"]}
Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

ANALYSIS RESULTS:
============================================================
Permeability (k):        {perm:.2f} mD
Skin Factor (s):         {skin:.2f}
Horner Slope (m):        {slope:.6f}
Horner Intercept (b):    {intercept:.6f}

DATA QUALITY:
============================================================
Data Points:             {len(time)}
Time Range:              {time.min():.2f} to {time.max():.2f} hours
Pressure Range:          {pressure.min():.2f} to {pressure.max():.2f} psi

FILES GENERATED:
============================================================
Horner Plot:             {results["plot_file"]}
JSON Report:             {results["json_file"]}

INTERPRETATION:
============================================================
Permeability: {perm_interp}
Skin Factor: {skin_interp}
"""
        self.results_text.setText(report_text)
        for i in reversed(range(self.plot_layout.count())):
            self.plot_layout.itemAt(i).widget().setParent(None)
        canvas = FigureCanvas(results["fig"])
        self.plot_layout.addWidget(canvas)
        canvas.draw()
        self.run_btn.setEnabled(True)
        self.run_btn.setText("RUN ANALYSIS")
        self.status_label.setText("Complete!")
        self.statusBar().showMessage("Analysis complete!")

    def show_error(self, error_msg):
        self.results_text.setText(f"ERROR: {error_msg}")
        self.run_btn.setEnabled(True)
        self.run_btn.setText("RUN ANALYSIS")
        self.status_label.setText("Error - check results")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
