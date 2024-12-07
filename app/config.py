# config.py

MAPS_AND_DATABASES = {
    "Polska": {
        "map_path": "app/maps/wojewodztwa.shp",
        "database_path": "app/data/polska.db",
        "module": "app.countries.polska"
    }
}


# Lista dostępnych algorytmów
ALGORITHMS = {
    "Dijkstra": "app.algorithms.dijkstra.dijkstra",
}
