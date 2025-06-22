import requests

import tkinter as tk
from tkinter import Menu, messagebox
from datetime import datetime
import os
import textwrap
import threading



API_KEY = "1448edc6f228266f8cfb09e451b3ab70"
FILENAME = "weather_history.txt"

class WeatherAPP:
    def __init__(self, root):
        self.root = root
        self.root.title("--- Python Weather APP ---")
        self.root.geometry('640x480')
        
        self.menubar = tk.Menu(self.root)
        filemenu = Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="History", command=self.show_history)
        filemenu.add_command(label="Toggle Theme", command=self.toggle_theme)
        filemenu.add_command(label="About", command=self.show_about)

        self.menubar.add_cascade(label="Options", menu=filemenu)

        self.root.config(menu=self.menubar)

        self.dark_mode = False

        self.label1 = tk.Label(self.root, text="Enter your city:", font=("Arial", 12))
        self.label1.pack(pady=5)

        self.city_entry = tk.Entry(self.root, width=30, font=("Arial", 12))
        self.city_entry.pack(pady=5)

        self.text_area = tk.Text(self.root, width=60, height=13, wrap=tk.WORD, state='disabled', font=("Arial", 15))
        self.text_area.pack(pady=10)

        

        self.submit_btn =tk.Button(self.root, text="Submit", command=self.start_get_weather_thread, font=("Arial", 12), width=20, height=2)
        self.submit_btn.pack(pady=5)

        self.exit_btn =tk.Button(self.root, text="Exit", command=self.root.quit, font=("Arial", 12), width=20, height=2)
        self.exit_btn.pack(pady=5)

        self.root.bind('<Return>', lambda event: self.start_get_weather_thread())

        self.show_history_popup = None
        self.toggle_theme()

    def get_weather(self):
        
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showwarning("Input Error", "Please enter a city name.")
            return

        
        base_url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric"
        }
        
        try:

            response = requests.get(base_url, params=params)
            data = response.json()

            if response.status_code != 200 or "main" not in data:
                error_msg = data.get("message", "Failed to get weather data.")
                self.text_area.config(state='normal')
                self.text_area.delete(1.0, tk.END)
                self.text_area.config(state='disabled')
                messagebox.showerror("Error", f"{error_msg.capitalize()}")
                return
            
            name = data["name"]
            country = data["sys"]["country"]
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            temp_min = data["main"]["temp_min"]
            temp_max = data["main"]["temp_max"]
            desc = data["weather"][0]["description"].title()
            humidity = data["main"]["humidity"]
            pressure = data["main"]["pressure"]
            wind = data["wind"]["speed"]
            clouds = data["clouds"]["all"]
            visibility = data.get("visibility", 0)

            sunrise = datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M:%S")
            sunset = datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M:%S")


            self.text_area.config(state='normal')
            self.text_area.delete(1.0, tk.END)

            weather_report = textwrap.dedent(f"""
📍 Location: {name}, {country}
🌡 Temperature: {temp}°C (Feels like: {feels_like}°C)
🔻 Min: {temp_min}°C   🔺 Max: {temp_max}°C
☁ Description: {desc}
💧 Humidity: {humidity}%
📈 Pressure: {pressure} hPa
💨 Wind Speed: {wind} m/s
☁ Cloudiness: {clouds}%
👁 Visibility: {visibility / 1000} km
🌅 Sunrise: {sunrise}
🌇 Sunset: {sunset}
""").strip()

            self.text_area.insert(tk.END, weather_report.strip())
            self.text_area.config(state='disabled')

            with open(FILENAME, "a", encoding="utf-8") as f:
                now = datetime.now()
                timestamp = now.strftime("%Y-%m-%d, %H-%M-%S %p")

                content = f"\n{timestamp} | City Input: {city}\n{weather_report}\n"

                f.write(content)

        except Exception as e:
            messagebox.showerror("Error", f"Something went wrong:\n{e}")

        self.city_entry.delete(0, tk.END)
        
    def start_get_weather_thread(self):
      
        self.submit_btn.config(state='disabled', text="Loading...")
        
        def weather_thread():
            self.get_weather()
            
            self.submit_btn.config(state='normal', text="Submit")
        
        threading.Thread(target=weather_thread, daemon=True).start()

    def show_history(self):
        if self.show_history_popup and self.show_history_popup.winfo_exists():
            self.show_history_popup.lift()
            return

        if not os.path.exists(FILENAME):
            messagebox.showinfo("History", "No history found.")
            return

        with open(FILENAME, 'r', encoding="utf-8") as f:
            text = f.readlines()
            if not text:
                messagebox.showinfo("History", "No history found.")
                return

        self.show_history_popup = tk.Toplevel(self.root)
        self.show_history_popup.title("--- History ---")
        self.show_history_popup.geometry('450x450')



        frame = tk.Frame(self.show_history_popup)
        frame.pack(pady=10, expand=True, fill=tk.BOTH)

        self.listbox = tk.Listbox(frame, width=50, height=20)
        self.listbox.grid(row=0, column=0, sticky="nsew")

        self.scrollbar = tk.Scrollbar(frame, command=self.listbox.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.listbox.config(yscrollcommand=self.scrollbar.set)


        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        try:
            with open(FILENAME, "r", encoding="utf-8") as f:
                content = f.readlines()
                for line in content:
                    self.listbox.insert(tk.END, line.strip())
            self.listbox.focus()
        except Exception as e:
            messagebox.showerror("Error", f"[Error]:\n{e}")
            return

        self.clean_btn = tk.Button(self.show_history_popup, text="Clean", command=self.clean_history, font=("Arial", 12), width=10, height=1)
        self.clean_btn.pack(pady=5)

        self.done_btn = tk.Button(self.show_history_popup, text="Done", command=self.show_history_popup.destroy, font=("Arial", 12), width=10, height=1)
        self.done_btn.pack(pady=5)

    def clean_history(self):

        confirm = messagebox.askyesno("History", "Do you want to delete history?")

        if confirm:
            try:
                with open(FILENAME, 'r', encoding="utf-8") as f:
                    content = f.readlines()
                    if not content:
                        messagebox.showinfo("History", "History is already cleared.")
                        return

                with open(FILENAME, 'w', encoding="utf-8") as f:
                    f.write('')

                    messagebox.showinfo("History", "History cleared successfully.")
                    self.listbox.delete(0, tk.END)

            except Exception as e:
                messagebox.showerror("Error", f"[Error]:\n{e}")
                return


    def show_about(self):
        messagebox.showinfo("About", "Weather App\nMade with ♥ by Manoj\nUses OpenWeatherMap API")

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode

        if self.dark_mode:
            bg_color = "#1e1e2f"         
            fg_color = "#e0e0e0"         
            button_bg = "#33334d"       
            highlight = "#4fc3f7"     
            entry_bg = "#2b2b3c"
        else:
            bg_color = "#f0faff"          
            fg_color = "#000000"         
            button_bg = "#a0d8ef"         
            highlight = "#1976d2"         
            entry_bg = "white"

       
        self.root.config(bg=bg_color)
        self.text_area.config(bg=bg_color, fg=fg_color, insertbackground=fg_color)
        self.city_entry.config(bg=entry_bg, fg=fg_color, insertbackground=fg_color)
        self.label1.config(bg=bg_color, fg=highlight)

        self.submit_btn.config(bg=button_bg, fg=fg_color, activebackground=highlight)
        self.exit_btn.config(bg=button_bg, fg=fg_color, activebackground=highlight)

       
        if self.show_history_popup and self.show_history_popup.winfo_exists():
            self.show_history_popup.config(bg=bg_color)
            if hasattr(self, 'listbox'):
                self.listbox.config(bg=bg_color, fg=fg_color, selectbackground=highlight, selectforeground=bg_color)
            if hasattr(self, 'clean_btn'):
                self.clean_btn.config(bg=button_bg, fg=fg_color, activebackground=highlight)
            if hasattr(self, 'done_btn'):
                self.done_btn.config(bg=button_bg, fg=fg_color, activebackground=highlight)
            if hasattr(self, 'scrollbar'):
                self.scrollbar.config(bg=button_bg, activebackground=highlight, troughcolor=bg_color)

if __name__ == '__main__':
    root = tk.Tk()
    app = WeatherAPP(root)
    root.mainloop()