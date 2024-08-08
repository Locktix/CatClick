import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import pyautogui
import win32api
import pynput.mouse as mouse
import keyboard

class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Clicker")
        self.root.minsize(400, 250)
        self.running = False
        self.control_key = None
        self.key_listener_active = False
        self.click_thread = None
        self.button_coords = None
        self.mouse_listener = None

        # Define styles
        style = ttk.Style()
        style.configure('TLabel', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10), padding=8)
        style.configure('TFrame', background='#f5f5f5')
        style.configure('TEntry', padding=5)

        # Colors
        self.primary_color = "#3498db"
        self.secondary_color = "#2ecc71"
        self.background_color = "#f5f5f5"
        self.label_color = "#333"

        # Configure main window
        self.root.configure(bg=self.background_color)
        self.create_widgets()
        self.setup_mouse_tracking()

    def create_widgets(self):
        # Title
        title = tk.Label(self.root, text="Auto Clicker", font=('Arial', 14, 'bold'), bg=self.background_color, fg=self.primary_color)
        title.grid(row=0, column=0, columnspan=8, padx=10, pady=10, sticky="nsew")

        # Interval frame
        interval_frame = ttk.Frame(self.root)
        interval_frame.grid(row=1, column=0, columnspan=8, padx=10, pady=5, sticky="nsew")
        interval_frame.configure(style='TFrame')

        # Labels and Entries
        labels = ["Heures:", "Minutes:", "Secondes:", "Millisecondes:"]
        default_values = ["0", "0", "0", "1"]  # Default values, with 1 ms in the last entry
        self.entries = []
        for i, (text, default) in enumerate(zip(labels, default_values)):
            ttk.Label(interval_frame, text=text, background=self.background_color, foreground=self.label_color).grid(row=0, column=i*2, padx=5, pady=5, sticky="e")
            entry = ttk.Entry(interval_frame, width=8)
            entry.grid(row=0, column=i*2+1, padx=5, pady=5, sticky="ew")
            entry.insert(0, default)  # Set default value
            self.entries.append(entry)

        # Mouse button dropdown
        ttk.Label(self.root, text="Bouton de souris:", background=self.background_color, foreground=self.label_color).grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.mouse_button_var = tk.StringVar()
        self.mouse_button_var.set("Gauche")  # Default value
        self.mouse_button_dropdown = ttk.Combobox(self.root, textvariable=self.mouse_button_var, values=["Gauche", "Droit", "Milieu"])
        self.mouse_button_dropdown.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        # Click type dropdown
        ttk.Label(self.root, text="Type de clic:", background=self.background_color, foreground=self.label_color).grid(row=2, column=2, padx=10, pady=10, sticky="e")
        self.click_type_var = tk.StringVar()
        self.click_type_var.set("Simple")  # Default value
        self.click_type_dropdown = ttk.Combobox(self.root, textvariable=self.click_type_var, values=["Simple", "Double"])
        self.click_type_dropdown.grid(row=2, column=3, padx=10, pady=10, sticky="w")

        # Control key
        ttk.Label(self.root, text="Touche de contrôle:", background=self.background_color, foreground=self.label_color).grid(row=3, column=0, padx=10, pady=10, sticky="e")
        self.control_key_label = ttk.Label(self.root, text="Non définie", background=self.background_color, foreground=self.label_color)
        self.control_key_label.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        self.control_key_button = ttk.Button(self.root, text="Définir touche de contrôle", command=self.set_control_key, style='TButton')
        self.control_key_button.grid(row=3, column=2, padx=10, pady=10, sticky="ew")

        # Status window
        self.create_status_window()

    def create_status_window(self):
        self.status_window = tk.Toplevel(self.root)
        self.status_window.title("Auto Clicker Status")
        self.status_window.overrideredirect(True)
        self.status_window.attributes('-topmost', True)

        self.canvas = tk.Canvas(self.status_window, width=20, height=20, bg="red", bd=0, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.circle = self.canvas.create_oval(0, 0, 20, 20, fill="red", outline="")

    def setup_mouse_tracking(self):
        self.mouse_tracking_thread = threading.Thread(target=self.track_mouse)
        self.mouse_tracking_thread.daemon = True
        self.mouse_tracking_thread.start()

    def update_status_window_position(self):
        x, y = win32api.GetCursorPos()
        self.status_window.geometry(f"+{x+10}+{y+10}")

    def track_mouse(self):
        while True:
            self.update_status_window_position()
            time.sleep(0.01)

    def start_clicker(self):
        if self.running:
            return

        try:
            hours = int(self.entries[0].get() or "0")
            minutes = int(self.entries[1].get() or "0")
            seconds = int(self.entries[2].get() or "0")
            milliseconds = int(self.entries[3].get() or "0")
            self.interval = (hours * 3600 + minutes * 60 + seconds) + milliseconds / 1000
        except ValueError:
            messagebox.showerror("Erreur", "Intervalle invalide. Veuillez entrer des valeurs numériques correctes.")
            return

        self.running = True
        if self.click_thread:
            self.click_thread.join()

        self.click_thread = threading.Thread(target=self.auto_click)
        self.click_thread.start()
        self.status_window.config(bg="green")
        self.canvas.itemconfig(self.circle, fill="green")

    def stop_clicker(self):
        self.running = False
        if self.click_thread:
            self.click_thread.join()
        self.status_window.config(bg="red")
        self.canvas.itemconfig(self.circle, fill="red")

    def auto_click(self):
        while self.running:
            if self.button_coords and self.is_cursor_within_button():
                time.sleep(self.interval)
                continue
            if self.click_type_var.get() == "Double":
                pyautogui.click(button=self.get_mouse_button())
                time.sleep(self.interval)
            pyautogui.click(button=self.get_mouse_button())
            time.sleep(self.interval)

    def is_cursor_within_button(self):
        if not self.button_coords:
            return False
        x, y = win32api.GetCursorPos()
        button_x1, button_y1, button_x2, button_y2 = self.button_coords
        return button_x1 <= x <= button_x2 and button_y1 <= y <= button_y2
    
    def get_mouse_button(self):
        button = self.mouse_button_var.get()
        if button == "Gauche":
            return "left"
        elif button == "Droit":
            return "right"
        elif button == "Milieu":
            return "middle"

    def set_control_key(self):
        if self.control_key:
            self.reset_key()
            return

        self.key_listener_active = True
        self.control_key_button.config(text="Réinitialiser la touche")
        self.button_coords = self.get_button_coords(self.control_key_button)  # Save button coordinates
        self.root.bind("<KeyPress>", self.handle_key_press)

        # Configure mouse listener
        if self.mouse_listener:
            self.mouse_listener.stop()
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
        self.mouse_listener.start()

    def handle_key_press(self, event):
        if self.key_listener_active:
            if event.keysym in keyboard.all_modifiers or event.keysym in ["Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R"]:
                messagebox.showerror("Erreur", "Les touches de modification ne sont pas autorisées.")
                return

            if self.control_key is None:
                self.control_key = event.keysym
                self.control_key_label.config(text=self.control_key)
                self.key_listener_active = False
                self.root.unbind("<KeyPress>")
                self.setup_key_listeners()
            else:
                if event.keysym == self.control_key:
                    if self.running:
                        self.stop_clicker()
                    else:
                        if not any(entry.get() for entry in self.entries):
                            messagebox.showerror("Erreur", "Intervalle non défini. Veuillez entrer les valeurs de l'intervalle.")
                            return
                        self.start_clicker()

    def get_button_coords(self, button):
        button.update_idletasks()
        x1 = button.winfo_rootx()
        y1 = button.winfo_rooty()
        x2 = x1 + button.winfo_width()
        y2 = y1 + button.winfo_height()
        return (x1, y1, x2, y2)

    def on_mouse_click(self, x, y, button, pressed):
        if not self.key_listener_active:
            return

        if pressed:
            button_name = f"mouse{button.value}"
            if self.control_key is None:
                self.control_key = button_name
                self.control_key_label.config(text=self.control_key)
                self.key_listener_active = False
                self.setup_key_listeners()
            else:
                if self.control_key == button_name:
                    if self.running:
                        self.stop_clicker()
                    else:
                        if not any(entry.get() for entry in self.entries):
                            messagebox.showerror("Erreur", "Intervalle non défini. Veuillez entrer les valeurs de l'intervalle.")
                            return
                        self.start_clicker()

    def setup_key_listeners(self):
        # Remove any existing listeners
        if self.mouse_listener:
            self.mouse_listener.stop()

        # Add support for mouse buttons
        if self.control_key.startswith("mouse"):
            self.mouse_listener = mouse.Listener(on_click=self.on_click)
            self.mouse_listener.start()
        else:
            # If it was a keyboard key, add the hotkey
            keyboard.add_hotkey(self.control_key, self.toggle_clicker)

    def on_click(self, x, y, button, pressed):
        if pressed and f"mouse{button.value}" == self.control_key:
            if self.running:
                self.stop_clicker()
            else:
                if not any(entry.get() for entry in self.entries):
                    messagebox.showerror("Erreur", "Intervalle non défini. Veuillez entrer les valeurs de l'intervalle.")
                    return
                self.start_clicker()

    def reset_key(self):
        self.control_key = None
        self.control_key_label.config(text="Non définie")
        self.control_key_button.config(text="Définir touche de contrôle")
        keyboard.unhook_all_hotkeys()
        if self.mouse_listener:
            self.mouse_listener.stop()

    def toggle_clicker(self):
        if self.running:
            self.stop_clicker()
        else:
            if not any(entry.get() for entry in self.entries):
                messagebox.showerror("Erreur", "Intervalle non défini. Veuillez entrer les valeurs de l'intervalle.")
                return
            self.start_clicker()

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerApp(root)
    root.mainloop()