import sys
from app.ui.main import MainWindow
from PyQt5.QtWidgets import QApplication
from app.ui.map_visualizer import MapVisualizer

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    main_window.show_initial_instructions()
    sys.exit(app.exec_())
