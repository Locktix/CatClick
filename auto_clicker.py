import tkinter as tk
from tkinter import ttk
import threading
import time
import pyautogui
import win32api
import win32con
import keyboard

class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Clicker")
        self.root.geometry("500x300")
        self.root.minsize(400, 250)
        self.running = False

        # Style moderne
        style = ttk.Style()
        style.configure('TLabel', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10), padding=8)
        style.configure('TFrame', background='#f5f5f5')
        style.configure('TEntry', padding=5)

        # Couleurs
        self.primary_color = "#3498db"
        self.secondary_color = "#2ecc71"
        self.background_color = "#f5f5f5"
        self.label_color = "#333"

        # Configuration de la fenêtre principale
        self.root.configure(bg=self.background_color)

        # Titre
        title = tk.Label(root, text="Auto Clicker", font=('Arial', 14, 'bold'), bg=self.background_color, fg=self.primary_color)
        title.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

        # Frame pour les entrées d'intervalle
        interval_frame = ttk.Frame(root)
        interval_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=5, sticky="nsew")
        interval_frame.configure(style='TFrame')

        ttk.Label(interval_frame, text="Heures:", background=self.background_color, foreground=self.label_color).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.hours_entry = ttk.Entry(interval_frame, width=8)
        self.hours_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(interval_frame, text="Minutes:", background=self.background_color, foreground=self.label_color).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.minutes_entry = ttk.Entry(interval_frame, width=8)
        self.minutes_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        ttk.Label(interval_frame, text="Secondes:", background=self.background_color, foreground=self.label_color).grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.seconds_entry = ttk.Entry(interval_frame, width=8)
        self.seconds_entry.grid(row=0, column=5, padx=5, pady=5, sticky="ew")

        ttk.Label(interval_frame, text="Millisecondes:", background=self.background_color, foreground=self.label_color).grid(row=0, column=6, padx=5, pady=5, sticky="e")
        self.milliseconds_entry = ttk.Entry(interval_frame, width=8)
        self.milliseconds_entry.grid(row=0, column=7, padx=5, pady=5, sticky="ew")

        # Touche de contrôle
        ttk.Label(root, text="Touche de contrôle:", background=self.background_color, foreground=self.label_color).grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.control_key_label = ttk.Label(root, text="Non définie", background=self.background_color, foreground=self.label_color)
        self.control_key_label.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.control_key_button = ttk.Button(root, text="Définir touche de contrôle", command=self.set_control_key, style='TButton')
        self.control_key_button.grid(row=2, column=2, padx=10, pady=10, sticky="ew")

        self.status_label = ttk.Label(root, text="Status: Arrêté", background=self.background_color, foreground=self.label_color)
        self.status_label.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky="w")

        # Création d'une fenêtre flottante pour l'état de l'auto-clicker
        self.status_window = tk.Toplevel(self.root)
        self.status_window.title("Auto Clicker Status")
        self.status_window.geometry("20x20")  # Taille de la bulle
        self.status_window.overrideredirect(True)  # Supprime les bordures de la fenêtre
        self.status_window.attributes('-topmost', True)  # Garder la fenêtre au-dessus
        self.status_window.config(bg="red")

        # Créer un canvas pour dessiner le rond
        self.canvas = tk.Canvas(self.status_window, width=20, height=20, bg="red", bd=0, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.circle = self.canvas.create_oval(0, 0, 20, 20, fill="red", outline="")

        # Initialiser la position de la fenêtre de statut
        self.update_status_window_position()

        # Initialiser la position de la bulle
        self.status_window_position = (0, 0)

        # Variables de contrôle du clic
        self.click_thread = None
        self.control_key = None
        self.key_listener_active = False

        # Créer un thread pour surveiller les mouvements de la souris
        self.mouse_tracking_thread = threading.Thread(target=self.track_mouse)
        self.mouse_tracking_thread.daemon = True
        self.mouse_tracking_thread.start()

    def update_status_window_position(self):
        # Mettre à jour la position de la fenêtre de statut pour suivre la souris
        x, y = win32api.GetCursorPos()
        self.status_window.geometry(f"+{x+10}+{y+10}")

    def track_mouse(self):
        while True:
            self.update_status_window_position()
            time.sleep(0.01)  # Réduit l'utilisation des ressources

    def start_clicker(self):
        if self.running:
            return

        try:
            hours = int(self.hours_entry.get() or "0")
            minutes = int(self.minutes_entry.get() or "0")
            seconds = int(self.seconds_entry.get() or "0")
            milliseconds = int(self.milliseconds_entry.get() or "0")

            self.interval = (hours * 3600 + minutes * 60 + seconds) + milliseconds / 1000
        except ValueError:
            messagebox.showerror("Erreur", "Intervalle invalide. Veuillez entrer des valeurs numériques correctes.")
            return

        self.running = True
        if self.click_thread:
            self.click_thread.join()

        self.click_thread = threading.Thread(target=self.auto_click)
        self.click_thread.start()
        self.status_label.config(text="Status: En cours", foreground=self.secondary_color)
        self.status_window.config(bg="green")
        self.canvas.itemconfig(self.circle, fill="green")

    def stop_clicker(self):
        self.running = False
        if self.click_thread:
            self.click_thread.join()
        self.status_label.config(text="Status: Arrêté", foreground="red")
        self.status_window.config(bg="red")
        self.canvas.itemconfig(self.circle, fill="red")

    def auto_click(self):
        while self.running:
            pyautogui.click()
            time.sleep(self.interval)

    def set_control_key(self):
        if self.control_key:
            self.reset_key()
            self.status_label.config(text="Cliquez à nouveau pour définir une nouvelle touche", foreground="orange")
            return

        self.key_listener_active = True
        self.status_label.config(text="Choisissez la touche de contrôle", foreground=self.primary_color)
        self.control_key_button.config(text="Réinitialiser la touche")
        self.root.bind("<KeyPress>", self.handle_key_press)

    def handle_key_press(self, event):
        if self.key_listener_active:
            if event.keysym in keyboard.all_modifiers or event.keysym in ["Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R"]:
                messagebox.showerror("Erreur", "Les touches de modification ne sont pas autorisées.")
                return
            
            if self.control_key is None:
                self.control_key = event.keysym
                self.control_key_label.config(text=self.control_key)
                self.key_listener_active = False
                self.status_label.config(text=f"Touche de contrôle définie : {self.control_key}", foreground=self.secondary_color)
                self.setup_key_listeners()
                self.root.unbind("<KeyPress>")
            else:
                if event.keysym == self.control_key:
                    if self.running:
                        self.stop_clicker()
                    else:
                        if not (self.hours_entry.get() or self.minutes_entry.get() or self.seconds_entry.get() or self.milliseconds_entry.get()):
                            messagebox.showerror("Erreur", "Intervalle non défini. Veuillez entrer les valeurs de l'intervalle.")
                            return
                        self.start_clicker()

    def setup_key_listeners(self):
        # Écouter la touche de contrôle
        keyboard.add_hotkey(self.control_key, self.toggle_clicker)

    def toggle_clicker(self):
        if self.running:
            self.stop_clicker()
        else:
            if not (self.hours_entry.get() or self.minutes_entry.get() or self.seconds_entry.get() or self.milliseconds_entry.get()):
                messagebox.showerror("Erreur", "Intervalle non défini. Veuillez entrer les valeurs de l'intervalle.")
                return
            self.start_clicker()

    def reset_key(self):
        self.control_key = None
        self.control_key_label.config(text="Non définie")
        self.control_key_button.config(text="Définir touche de contrôle")
        self.status_label.config(text="Touche réinitialisée. Veuillez définir une nouvelle touche.", foreground="orange")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.mainloop()
