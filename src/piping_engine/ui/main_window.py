import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QFileDialog, QTableWidget, 
                               QTableWidgetItem, QLabel, QMessageBox, QHeaderView,
                               QSplitter)
from PySide6.QtCore import Qt
from piping_engine.core.project_file import load_network_from_yaml
from piping_engine.network.solver import solve_network
from piping_engine.reporting.html_report import generate_report

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("piping-engine - Simulador de Tuberías")
        self.resize(1000, 700)
        self.network = None
        self.results = None
        
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        self.btn_load = QPushButton("Cargar Proyecto YAML")
        self.btn_load.clicked.connect(self.load_project)
        
        self.btn_solve = QPushButton("Resolver Red")
        self.btn_solve.clicked.connect(self.solve_project)
        self.btn_solve.setEnabled(False)
        
        self.btn_report = QPushButton("Generar Reporte HTML")
        self.btn_report.clicked.connect(self.generate_report)
        self.btn_report.setEnabled(False)
        
        toolbar_layout.addWidget(self.btn_load)
        toolbar_layout.addWidget(self.btn_solve)
        toolbar_layout.addWidget(self.btn_report)
        toolbar_layout.addStretch()
        main_layout.addLayout(toolbar_layout)
        
        # Splitter principal
        splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(splitter)
        
        # Tabla Nodos
        self.table_nodes = QTableWidget()
        self.table_nodes.setColumnCount(4)
        self.table_nodes.setHorizontalHeaderLabels(["Nodo", "Tipo", "Elevación (m)", "Presión Res. (bar)"])
        self.table_nodes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        splitter.addWidget(self.table_nodes)
        
        # Tabla Componentes
        self.table_comps = QTableWidget()
        self.table_comps.setColumnCount(5)
        self.table_comps.setHorizontalHeaderLabels(["Componente", "Desde", "Hacia", "Flujo (kg/s)", "dP (bar)"])
        self.table_comps.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        splitter.addWidget(self.table_comps)
        
        # Info Status
        self.lbl_status = QLabel("Listo.")
        main_layout.addWidget(self.lbl_status)

    def load_project(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Abrir Proyecto YAML", "", "YAML Files (*.yaml *.yml)")
        if not filepath:
            return
            
        try:
            self.network = load_network_from_yaml(filepath)
            self.filepath = filepath
            self.update_tables_initial()
            self.btn_solve.setEnabled(True)
            self.btn_report.setEnabled(False)
            self.lbl_status.setText(f"Proyecto cargado: {filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Error al Cargar", f"Ocurrió un error: {str(e)}")

    def update_tables_initial(self):
        self.table_nodes.setRowCount(len(self.network.nodes))
        for row, (name, node) in enumerate(self.network.nodes.items()):
            tipo = "Boundary" if node.fixed_pressure is not None else "Junction"
            self.table_nodes.setItem(row, 0, QTableWidgetItem(name))
            self.table_nodes.setItem(row, 1, QTableWidgetItem(tipo))
            self.table_nodes.setItem(row, 2, QTableWidgetItem(f"{node.elevation:.2f}"))
            self.table_nodes.setItem(row, 3, QTableWidgetItem("-"))
            
        self.table_comps.setRowCount(len(self.network.components))
        for row, comp in enumerate(self.network.components):
            self.table_comps.setItem(row, 0, QTableWidgetItem(comp.name))
            self.table_comps.setItem(row, 1, QTableWidgetItem(comp.from_node))
            self.table_comps.setItem(row, 2, QTableWidgetItem(comp.to_node))
            self.table_comps.setItem(row, 3, QTableWidgetItem("-"))
            self.table_comps.setItem(row, 4, QTableWidgetItem("-"))

    def solve_project(self):
        if not self.network:
            return
            
        self.lbl_status.setText("Resolviendo...")
        QApplication.processEvents()
        
        try:
            self.results = solve_network(self.network)
            if self.results['converged']:
                self.lbl_status.setText(f"Convergencia exitosa en {self.results['iterations']} iteraciones.")
                self.update_tables_results()
                self.btn_report.setEnabled(True)
            else:
                self.lbl_status.setText("Error: El solver no convergió.")
                QMessageBox.warning(self, "Solver", "El motor no logró convergencia.")
        except Exception as e:
            QMessageBox.critical(self, "Error en Solver", f"Ocurrió un error: {str(e)}")
            self.lbl_status.setText("Error en resolución.")

    def update_tables_results(self):
        for row in range(self.table_nodes.rowCount()):
            name = self.table_nodes.item(row, 0).text()
            node = self.network.nodes[name]
            p_bar = node.pressure_result / 100000.0
            self.table_nodes.setItem(row, 3, QTableWidgetItem(f"{p_bar:.4f}"))
            
        for row in range(self.table_comps.rowCount()):
            name = self.table_comps.item(row, 0).text()
            m_flow = self.results['branch_flows'][name]
            info = self.results['branch_details'][name]
            dp_bar = info.get('dp_total', 0.0) / 100000.0
            self.table_comps.setItem(row, 3, QTableWidgetItem(f"{m_flow:.4f}"))
            self.table_comps.setItem(row, 4, QTableWidgetItem(f"{dp_bar:.4f}"))

    def generate_report(self):
        if not self.results or not self.network:
            return
            
        filepath, _ = QFileDialog.getSaveFileName(self, "Guardar Reporte HTML", f"{self.filepath}_report.html", "HTML Files (*.html)")
        if filepath:
            try:
                generate_report(self.network, self.results, filepath)
                self.lbl_status.setText(f"Reporte guardado en: {filepath}")
                QMessageBox.information(self, "Reporte", "Reporte HTML generado exitosamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al generar reporte: {str(e)}")

def run_app():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_app()
