from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import networkx as nx
from app.db_handler import connect_to_db, get_connections
import math

class MapVisualizer(FigureCanvas):
    def __init__(self, parent):
        self.figure = plt.Figure(figsize=(8, 6))
        super().__init__(self.figure)
        self.ax = None
        self.parent = parent
        self.city_points = {}
        self.graph = nx.Graph()
        self.start_city = None
        self.end_city = None
        self.steps = []
        self.current_step = 0
        self.shortest_path = []
        self.map_crs = None
        self.country_settings = None
        self.database_path = None
        self.mpl_connect("button_press_event", self.on_click)

    def set_database(self, database_path):
        """Ustawia bazę danych dla wizualizacji."""
        self.database_path = database_path

    def set_country_settings(self, settings):
        """Ustawia specyficzne ustawienia dla kraju."""
        self.country_settings = settings
        print(f"Ustawienia kraju: {self.country_settings}")

    def load_map(self, shp_path):
        """Ładuje mapę i rysuje miasta oraz połączenia."""
        import geopandas as gpd

        if self.ax is None:
            self.ax = self.figure.add_subplot(111)
        self.ax.clear()

        try:
            gdf = gpd.read_file(shp_path)
            self.map_crs = gdf.crs

            # Sprawdzanie zgodności CRS
            if self.map_crs.to_string() != self.country_settings["crs"]:
                gdf = gdf.to_crs(self.country_settings["crs"])
                self.map_crs = gdf.crs

            # Rysowanie mapy
            gdf.plot(ax=self.ax, color="lightgray", edgecolor="black")
            self.ax.axis("off")
        except Exception as e:
            self.parent.steps_text.append(f"Błąd ładowania mapy: {e}")
            return

        self._load_cities_and_connections()
        self._convert_city_coordinates_to_map_crs()
        self._draw_cities_and_connections()
        self.draw()
        self.figure.canvas.mpl_connect("button_press_event", self.on_click)


    def _load_cities_and_connections(self):
        """Ładuje miasta i połączenia z bazy danych."""
        conn = connect_to_db(self.database_path)
        if conn:
            from app.db_handler import get_cities, get_connections
            # Pobieranie miast
            cities = get_cities(conn)
            self.city_points = {city[1]: (city[0], city[3], city[2]) for city in cities}  # (id, lon, lat)

            # Pobieranie połączeń
            self.connections = get_connections(conn)

            conn.close()
        else:
            self.parent.steps_text.append("Błąd: Nie udało się nawiązać połączenia z bazą danych.")

    def _convert_city_coordinates_to_map_crs(self):
        """Konwertuje współrzędne miast na CRS mapy."""
        import pyproj
        from pyproj import Transformer

        if not self.city_points:
            self.parent.steps_text.append("Brak danych o miastach do konwersji.")
            return

        if not self.map_crs:
            self.parent.steps_text.append("Nie można przekształcić współrzędnych: brak CRS mapy.")
            return

        # Pobranie EPSG mapy
        map_crs_epsg = self.map_crs.to_epsg()
        print(f"Konwersja współrzędnych miast do CRS: EPSG:{map_crs_epsg}")  # Debugowanie CRS

        # Tworzenie transformera
        transformer = Transformer.from_crs("EPSG:4326", map_crs_epsg, always_xy=True)

        # Konwersja współrzędnych miast
        for city_name, (id, lon, lat) in self.city_points.items():
            x, y = transformer.transform(lat, lon)  # Upewniamy się, że kolejność współrzędnych jest poprawna
            self.city_points[city_name] = (id, x, y)

    def reset(self):
        """Resetuje wizualizator."""
        self.ax.clear()
        self.city_points.clear()
        self.graph.clear()
        self.start_city = None
        self.end_city = None
        self.steps.clear()
        self.current_step = 0
        self.shortest_path = []
        self.draw()

    def run_dijkstra(self):
        """Uruchamia algorytm Dijkstry."""
        if not self.start_city or not self.end_city:
            QMessageBox.warning(self, "Błąd", "Wybierz miasto początkowe i końcowe.")
            return

        # Budowa grafu
        for city_name, (id, x, y) in self.city_points.items():
            self.graph.add_node(city_name, pos=(x, y))
        for connection in self.connections:
            _, city_a_id, city_b_id, distance = connection
            city_a = next((name for name, (id, _, _) in self.city_points.items() if id == city_a_id), None)
            city_b = next((name for name, (id, _, _) in self.city_points.items() if id == city_b_id), None)
            if city_a and city_b:
                self.graph.add_edge(city_a, city_b, weight=distance)

        # Uruchomienie algorytmu
        try:
            from app.algorithms.dijkstra import dijkstra
            path, total_cost, steps = dijkstra(self.graph, self.start_city, self.end_city)
            self.shortest_path = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
            self.steps = steps
            self.current_step = 0
        except Exception as e:
            self.parent.steps_text.append(f"Błąd podczas uruchamiania algorytmu: {e}")

    def next_step(self):
        """Przejście do następnego kroku algorytmu."""
        # Sprawdzenie, czy mapa została załadowana
        if not self.city_points:
            self._show_error("Błąd", "Najpierw załaduj mapę.")
            return

        # Sprawdzenie, czy wybrano miasta początkowe i końcowe
        if not self.start_city or not self.end_city:
            self._show_error("Błąd", "Wybierz miasto początkowe i końcowe przed rozpoczęciem algorytmu.")
            return

        # Sprawdzenie, czy wybrano algorytm
        if not hasattr(self, "algorithm") or self.algorithm is None:
            self._show_error("Błąd", "Wybierz algorytm przed rozpoczęciem kroków.")
            return

        # Przejście przez kroki algorytmu
        if self.current_step < len(self.steps):
            current, neighbor, weight = self.steps[self.current_step]
            self.parent.steps_text.append(f"Krok {self.current_step + 1}: Relaksacja krawędzi {current} -> {neighbor} (waga: {weight})")
            self._highlight_edge(current, neighbor, color='red', linewidth=2)
            self.current_step += 1
        else:
            self._highlight_shortest_path()
            self._show_info(
                "Najkrótsza ścieżka", 
                f"Najkrótsza ścieżka: {' -> '.join([a for a, b in self.shortest_path]) + ' -> ' + self.shortest_path[-1][1]}\n"
                f"Koszt: {sum(self.graph[a][b]['weight'] for a, b in self.shortest_path):.2f}"
            )



    def _highlight_shortest_path(self):
        """Podświetla najkrótszą ścieżkę na mapie."""
        for city_a, city_b in self.shortest_path:
            self._highlight_edge(city_a, city_b, color='blue', linewidth=2)
        self.parent.steps_text.append(f"Najkrótsza ścieżka: {' -> '.join([a for a, b in self.shortest_path]) + ' -> ' + self.shortest_path[-1][1]}")

    def _highlight_edge(self, city_a, city_b, color='red', linewidth=2):
        """Podświetla krawędź na mapie."""
        if city_a in self.city_points and city_b in self.city_points:
            x1, y1 = self.city_points[city_a][1:]
            x2, y2 = self.city_points[city_b][1:]
            self.ax.plot([x1, x2], [y1, y2], color=color, linewidth=linewidth)
            self.draw()

    def _draw_cities_and_connections(self):
        """Rysuje miasta i połączenia na mapie."""
        if not self.city_points:
            self.parent.steps_text.append("Brak danych o miastach. Upewnij się, że dane są załadowane.")
            return

        # Rysowanie miast
        for city_name, (_, x, y) in self.city_points.items():
            self.ax.plot(x, y, 'bo', markersize=5)  # Kropki reprezentujące miasta
            self.ax.text(x, y, city_name, fontsize=8, ha='right')  # Nazwa miasta

        # Rysowanie połączeń
        for connection in self.connections:
            _, city_a_id, city_b_id, distance = connection
            city_a = next((name for name, (id, _, _) in self.city_points.items() if id == city_a_id), None)
            city_b = next((name for name, (id, _, _) in self.city_points.items() if id == city_b_id), None)
            if city_a and city_b:
                x1, y1 = self.city_points[city_a][1:]
                x2, y2 = self.city_points[city_b][1:]
                self.ax.plot([x1, x2], [y1, y2], 'g-', alpha=0.5)  # Linie reprezentujące połączenia

    def on_click(self, event):
        if not self.city_points:  # Sprawdzenie, czy mapa została załadowana
            self._show_error(
                "Błąd: Nie załadowano mapy.",
                "Wybierz mapę z menu 'Mapy'."
            )
            return
        if event.inaxes == self.ax:
            clicked_city = None
            for city, (id, x, y) in self.city_points.items():
                distance = math.sqrt((x - event.xdata) ** 2 + (y - event.ydata) ** 2)
                if distance <= 20000:  # Tolerancja kliknięcia
                    clicked_city = city
                    break

            if clicked_city:
                if not self.start_city:
                    self.start_city = clicked_city
                    self._highlight_city(clicked_city, 'red')
                    self.parent.steps_text.append(f"Wybrano miasto początkowe: {clicked_city}")
                elif not self.end_city:
                    self.end_city = clicked_city
                    self._highlight_city(clicked_city, 'green')
                    self.parent.steps_text.append(f"Wybrano miasto końcowe: {clicked_city}")
                else:
                    self.parent.steps_text.append("Oba miasta zostały już wybrane. Zresetuj, aby wybrać ponownie.")
            else:
                self._show_error(
                    "Nie wybrano miasta.",
                    "Kliknij dokładnie na punkt symbolizujący miasto, aby je wybrać."
                )
                self.parent.steps_text.append("Błąd: Kliknij dokładnie na miasto.")

    def _highlight_city(self, city, color):
        _, x, y = self.city_points[city]
        self.ax.plot(x, y, marker='o', color=color, markersize=10)
        self.draw()

    def reset(self):
        if self.ax:
            self.figure.delaxes(self.ax)
            self.ax = None
        self.graph.clear()
        self.city_points = {}
        self.connections = []
        self.steps = []
        self.current_step = 0
        self.shortest_path = []
        self.start_city = None
        self.end_city = None
        self.map_crs = None
        self.country_settings = None
        self.database_path = None
        self.algorithm = None
        self.parent.steps_text.append("Reset zakończony. Wybierz mapę, aby rozpocząć.")
        self.draw()

    def _show_error(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        custom_icon_path = "app\\resources\\error.png"  # Ścieżka do ikony
        msg.setWindowIcon(QIcon(custom_icon_path))
        msg.exec_()

    def _show_info(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        custom_icon_path = "app\\resources\\info.png"
        msg.setWindowIcon(QIcon(custom_icon_path))

        msg.exec_()