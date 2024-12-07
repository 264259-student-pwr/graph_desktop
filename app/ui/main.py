import sys
import importlib
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QMenuBar, QTextEdit, QWidget, QPushButton, QMessageBox, QDialog, QLabel, QComboBox, QLineEdit
from PyQt5.QtGui import QFont
from app.ui.map_visualizer import MapVisualizer
from app.config import MAPS_AND_DATABASES

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplikacja do wizualizacji algorytmów analizy grafów")
        self.setGeometry(100, 100, 1000, 700)

        # Główne okno i układ
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Map Visualizer
        self.map_visualizer = MapVisualizer(self)
        self.layout.addWidget(self.map_visualizer)

        # Obszar tekstowy na kroki algorytmu
        self.steps_text = QTextEdit()
        self.steps_text.setReadOnly(True)
        self.layout.addWidget(self.steps_text)
        font = QFont("Arial", 14)  # Ustawienie czcionki i rozmiaru
        self.steps_text.setFont(font)

        self.next_step_button = QPushButton("Następny krok")
        self.next_step_button.clicked.connect(self.map_visualizer.next_step)
        self.layout.addWidget(self.next_step_button)


        # Menu
        self.menu = QMenuBar(self)
        self.setMenuBar(self.menu)

        self._populate_map_menu()
        self._populate_tools_menu()

    def _populate_map_menu(self):
        """Tworzy dynamiczne menu map i baz danych."""
        map_menu = self.menu.addMenu("Mapy")
        for map_name, data in MAPS_AND_DATABASES.items():
            map_path = data["map_path"]
            database_path = data["database_path"]
            country_module = data["module"]
            map_menu.addAction(
                f"Załaduj: {map_name}",
                lambda mp=map_path, db=database_path, cm=country_module: self.load_map_and_database(mp, db, cm)
            )

    def _populate_tools_menu(self):
        """Dodaje przyciski do menu Narzędzia."""
        tools_menu = self.menu.addMenu("Narzędzia")

        # Wybór i uruchomienie algorytmów
        algorithm_menu = tools_menu.addMenu("Wybierz algorytm")
        algorithm_menu.addAction("Dijkstra", lambda: self.run_algorithm("dijkstra"))

        tools_menu.addAction("Reset", lambda: self.reset())

    def run_algorithm(self, algorithm_name):
        """Ustawia i uruchamia wybrany algorytm."""
        if algorithm_name == "dijkstra":
            self.map_visualizer.algorithm = self.map_visualizer.run_dijkstra
            self.steps_text.append("Wybrano algorytm: Dijkstra")
            self.map_visualizer.run_dijkstra()  # Uruchomienie Dijkstry
        else:
            QMessageBox.warning(self, "Błąd", "Nieznany algorytm.")


    def load_map_and_database(self, map_path, database_path, country_module):
        """Ładuje mapę, bazę danych oraz moduł kraju."""
        # Importowanie modułu kraju
        country = importlib.import_module(country_module)
        settings = country.country_specific_settings()

        # Ustawienia specyficzne dla kraju
        self.map_visualizer.set_country_settings(settings)

        # Ładowanie mapy i bazy danych
        self.map_visualizer.set_database(database_path)
        self.map_visualizer.load_map(map_path)

        self.steps_text.append(f"Załadowano mapę: {map_path}")
        self.steps_text.append(f"Ustawiono bazę danych: {database_path}")

    def reset(self):
        """Resetuje wszystkie ustawienia."""
        self.map_visualizer.reset()
        self.steps_text.clear()
        self.steps_text.append("Zresetowano aplikację.")

    def show_initial_instructions(self):
        """Wyświetla monit z instrukcją kroków do wykonania."""
        instructions = (
            "Witaj w aplikacji!\n\n"
            "Aby poprawnie korzystać z programu, wykonaj następujące kroki:\n"
            "1. Załaduj mapę, wybierając odpowiedni plik w menu 'Mapy'.\n"
            "2. Kliknij na dwa miasta, aby ustawić punkt początkowy i końcowy.\n"
            "3. Wybierz algorytm w menu 'Narzędzia/Wybierz algorytm'.\n"
            "4. Przejdź przez kroki algorytmu za pomocą przycisku 'Next Step'.\n"
            "5. Po zakończeniu sprawdź najkrótszą ścieżkę i jej koszt.\n\n"
            "Miłej pracy!"
        )
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Instrukcja obsługi")
        msg.setText(instructions)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()