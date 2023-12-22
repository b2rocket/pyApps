import tkinter as tk
from PIL import Image, ImageTk
import json
import locale
import webbrowser

# Setze das Locale, um das Tausendertrennzeichen zu aktivieren
locale.setlocale(locale.LC_ALL, 'de_DE')

# Pfad zur JSON-Datei
JSON_FILE_PATH = "immobilienangebote.json"

# Funktion zum Öffnen des Links
def open_link(url):
    webbrowser.open(url)

# Klasse für den Tooltip
class ToolTip(object):
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def show_tip(self, text):
        if self.tipwindow or not text:
            return
        x, y, _cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=text, justify=tk.LEFT,
                 background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                 font=("tahoma", "12", "normal"), fg="black")  # Setzen der Textfarbe auf Schwarz
        label.pack(ipadx=1)

    def hide_tip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

# Funktion zum Anzeigen des Bildes in voller Größe
def show_full_image(image_path):
    new_window = tk.Toplevel()
    new_window.title("Vollbildansicht")

    image = Image.open(image_path)
    photo = ImageTk.PhotoImage(image)

    label = tk.Label(new_window, image=photo)
    label.image = photo  # Referenz behalten
    label.pack()


# Funktion zum Erstellen der GUI-Komponenten für jedes Angebot
def create_property_widgets(frame, property, global_percentage, global_equity):
    property_frame = tk.Frame(frame)
    property_frame.pack(padx=10, pady=10, fill=tk.X)

    # Frame für das Bild
    image_frame = tk.Frame(property_frame, borderwidth=2, relief="solid")
    if 'price2' in property:
        image_frame.config(highlightbackground="red", highlightthickness=2)
    image_frame.pack(side=tk.LEFT, padx=5, pady=5)

    # Bild anzeigen
    try:
        image_path = f"{property['id']}.png"
        thumbnail = Image.open(image_path)
        thumbnail = thumbnail.resize((90, 60), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(thumbnail)
        image_label = tk.Label(image_frame, image=photo, cursor="hand2")
        image_label.image = photo  # Referenz behalten
        image_label.pack()
        image_label.bind("<Button-1>", lambda e: show_full_image(image_path))
    except IOError:
        tk.Label(image_frame, text="Bild nicht verfügbar").pack()

    # Frame für die Informationen
    info_frame = tk.Frame(property_frame)
    info_frame.pack(side=tk.LEFT, padx=10)

    # Informationen anzeigen
    tk.Label(info_frame, text=f"Angebot {property['id']}").grid(row=0, column=0, sticky="w")
    tk.Label(info_frame, text=f"Ort: {property['location']}").grid(row=1, column=0, sticky="w")
    tk.Label(info_frame, text=f"Quadratmeter: {property['size']} m²").grid(row=2, column=0, sticky="w")
    tk.Label(info_frame, text=f"Preis: {property['price1']} €").grid(row=3, column=0, sticky="w")
    
   

    # Zusätzliche Informationen hinzufügen
    additional_info_frame = tk.Frame(property_frame)
    additional_info_frame.pack(side=tk.LEFT, padx=10)

    # Preis pro m² berechnen
    price_per_m2 = property['price1'] / property['size']
    formatted_price_per_m2 = locale.format_string("%d", price_per_m2, grouping=True)
    tk.Label(additional_info_frame, text=f"Preis pro m²: {formatted_price_per_m2}€").grid(row=0, column=0, sticky="w")

    # Finanzierungskosten berechnen
    financing_cost = (((property['price1'] * 1.0907)- global_equity)* ((global_percentage / 100) + 0.02 )) 
    formatted_financing_cost = locale.format_string("%d", financing_cost, grouping=True)
    tk.Label(additional_info_frame, text=f"Finanzierungskosten: {formatted_financing_cost}€").grid(row=1, column=0, sticky="w")

    # Monatliche Kosten berechnen
    monthly_cost = financing_cost / 12
    formatted_monthly_cost = locale.format_string("%d", monthly_cost, grouping=True)
    tk.Label(additional_info_frame, text=f"Im Monat: {formatted_monthly_cost}€").grid(row=2, column=0, sticky="w")
    
    # Link
    link_label = tk.Label(additional_info_frame, text="LINK", fg="light grey", cursor="hand2")
    link_label.grid(row=3, column=0, sticky="w")
    link_label.bind("<Button-1>", lambda e: open_link(property.get('link', '#')))

    # Preis-Label mit Tooltip für Price2
    formatted_price1 = locale.format_string("%d", property['price1'], grouping=True)
    price_label = tk.Label(info_frame, text=f"Preis: {formatted_price1} €")
    price_label.grid(row=3, column=0, sticky="w")
    if 'price2' in property:
        formatted_price2 = locale.format_string("%d", property['price2'], grouping=True)
        tooltip_text = f"Price 2: {formatted_price2} €\nDate 2: {property.get('date2', 'N/A')}"
        tooltip = ToolTip(price_label)
        price_label.bind("<Enter>", lambda e: tooltip.show_tip(tooltip_text))
        price_label.bind("<Leave>", lambda e: tooltip.hide_tip())

def sort_properties_by_size(properties):
    return sorted(properties, key=lambda x: x['size'])

def sort_properties_by_price(properties):
    return sorted(properties, key=lambda x: x['price1'])

def sort_properties_by_price_per_m2(properties):
    return sorted(properties, key=lambda x: x['price1'] / x['size'])

def update_sorted_view(sort_function, frame, global_percentage, global_equity):
    properties, _, _ = load_properties()
    sorted_properties = sort_function(properties)
    update_financing_info(frame, sorted_properties, global_percentage, global_equity)

def save_properties(properties, global_percentage, global_equity):
    data = {
        'global_percentage': global_percentage,
        'global_equity': global_equity,
        'properties': properties
    }
    with open(JSON_FILE_PATH, "w") as file:
        json.dump(data, file, indent=4)

def load_properties():
    with open(JSON_FILE_PATH, "r") as file:
        data = json.load(file)
    return data.get('properties', []), data.get('global_percentage', 3.5), data.get('global_equity', 50000)



def update_financing_info(frame, properties, global_percentage, global_equity):
    for widget in frame.winfo_children():
        widget.destroy()
    for property in properties:
        create_property_widgets(frame, property, global_percentage, global_equity)

def on_global_values_update(percentage_entry, equity_entry, properties, frame):
    try:
        global_percentage = float(percentage_entry.get().replace('%', ''))
        global_equity = int(equity_entry.get().replace('€', '').replace('.', ''))
        save_properties(properties, global_percentage, global_equity)
        update_financing_info(frame, properties, global_percentage, global_equity)
    except ValueError:
        print("Bitte geben Sie gültige Zahlen ein.")


# Hauptfunktion
def main():
    root = tk.Tk()
    root.title("Immobilienangebote")
    root.geometry('800x600')  # Setzt die Größe des Fensters auf 700x700 Pixel
    
    # Globale Eingabefelder
    global_frame = tk.Frame(root)
    global_frame.pack(padx=10, pady=10)

    tk.Label(global_frame, text="Prozentsatz:").pack(side=tk.LEFT)
    percentage_entry = tk.Entry(global_frame)
    percentage_entry.pack(side=tk.LEFT)
    tk.Label(global_frame, text="%").pack(side=tk.LEFT)

    tk.Label(global_frame, text="Eigenkapital:").pack(side=tk.LEFT)
    equity_entry = tk.Entry(global_frame)
    equity_entry.pack(side=tk.LEFT)
    tk.Label(global_frame, text="€").pack(side=tk.LEFT)

    save_button = tk.Button(global_frame, text="Speichern", command=lambda: on_global_values_update(percentage_entry, equity_entry, properties, scrollable_frame))
    save_button.pack(side=tk.LEFT)
    
    # Sortierbuttons
    sort_frame = tk.Frame(root)
    sort_frame.pack(padx=10, pady=10)

    tk.Button(sort_frame, text="Größe", command=lambda: update_sorted_view(sort_properties_by_size, scrollable_frame, global_percentage, global_equity)).pack(side=tk.LEFT)
    tk.Button(sort_frame, text="Preis", command=lambda: update_sorted_view(sort_properties_by_price, scrollable_frame, global_percentage, global_equity)).pack(side=tk.LEFT)
    tk.Button(sort_frame, text="Preis/m2", command=lambda: update_sorted_view(sort_properties_by_price_per_m2, scrollable_frame, global_percentage, global_equity)).pack(side=tk.LEFT)


    canvas = tk.Canvas(root)
    scrollbar = tk.Scrollbar(root, command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollable_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')

    properties, global_percentage, global_equity = load_properties()
    percentage_entry.insert(0, f"{global_percentage}")
    equity_entry.insert(0, f"{global_equity}")
    update_financing_info(scrollable_frame, properties, global_percentage, global_equity)

    root.mainloop()

if __name__ == "__main__":
    main()
