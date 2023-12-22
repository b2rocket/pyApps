import tkinter as tk
from tkinter import messagebox
import json
import os
from datetime import datetime

# Globale Variablen
SPORTS_FILE = 'sports.json'
RESULTS_FILE = 'results.json'
MAX_RESULTS = 5

# Lädt die Sportarten-Daten
def load_sports_data():
    if not os.path.exists(SPORTS_FILE):
        print("sports.json nicht gefunden")
        return []
    with open(SPORTS_FILE, 'r') as file:
        return json.load(file)

# Lädt die Trainingsergebnisse
def load_results():
    if not os.path.exists(RESULTS_FILE):
        return {}
    with open(RESULTS_FILE, 'r') as file:
        return json.load(file)

# Fügt ein neues Ergebnis hinzu
def add_result(sport_num, result):
    results = load_results()
    today = datetime.now().strftime("%Y-%m-%d")
    if sport_num not in results:
        results[sport_num] = {}
    if today not in results[sport_num]:
        results[sport_num][today] = []
    results[sport_num][today].append(result)
    with open(RESULTS_FILE, 'w') as file:
        json.dump(results, file)

# Aktualisiert die GUI
def update_gui(window, entry_fields):
    sports = load_sports_data()
    results = load_results()
    
    for i, sport in enumerate(sports):
        sport_results = results.get(str(sport['nummer']), {})
        dates_sorted = sorted(sport_results.keys(), reverse=True)
        
        for j in range(MAX_RESULTS):
            result_text = ''
            if j < len(dates_sorted):
                date = dates_sorted[j]
                result = sport_results[date]
                result_text = ', '.join(result[-MAX_RESULTS:])
            tk.Label(window, text=result_text).grid(row=i, column=4+j)

    # Feldinhalte leeren
    for entry in entry_fields.values():
        entry.delete(0, tk.END)

# Erstellt die GUI
def create_gui():
    window = tk.Tk()
    window.title("Sporttracker")

    sports = load_sports_data()
    entry_fields = {}  # Dictionary zum Speichern der Eingabefelder

    for i, sport in enumerate(sports):
        # Bild anzeigen
        img_path = f"BILD{sport['nummer']}.png"
        if os.path.exists(img_path):
            photo = tk.PhotoImage(file=img_path)
            img_label = tk.Label(window, image=photo)
            img_label.photo = photo
            img_label.grid(row=i, column=0)

        # Sportname und Soll-Wiederholungen
        tk.Label(window, text=sport['name']).grid(row=i, column=1)
        tk.Label(window, text=str(sport['anzahlWiederholungen'])).grid(row=i, column=2)

        # Eingabefeld für das aktuelle Ergebnis
        entry = tk.Entry(window)
        entry.grid(row=i, column=3)
        entry_fields[sport['nummer']] = entry

    # Funktion, um die Ergebnisse zu speichern
    def save_results():
        for num, entry in entry_fields.items():
            if entry.get():
                add_result(num, entry.get())
        update_gui(window, entry_fields)

    # Button, um Ergebnisse zu speichern
    tk.Button(window, text="Ergebnisse speichern", command=save_results).grid(row=len(sports), column=0)

    window.mainloop()

if __name__ == "__main__":
    create_gui()
