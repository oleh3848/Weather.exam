
import tkinter as tk
from tkinter import messagebox
import requests
import os
from datetime import datetime
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

API_KEY =os.getenv("open_API_KEY")
MODEL = "openrouter/free"

root = tk.Tk()
root.title("Погода")
root.geometry("750x750")
root.configure(bg="#1361d6")


title = tk.Label(
    root,
    text="Погода",
    font=("Impact", 24, "bold"),
    fg="white",
    bg="#03193a"
)
title.pack(pady=15)

city_entry = tk.Entry(
    root,
    font=("Arial", 14),
    justify="center",
    width=25
)
city_entry.pack(pady=10)


weather_label = tk.Label(
    root,
    text="Введи місто",
    font=("Arial", 14),
    fg="white",
    bg="#202b3c",
    justify="center"
)
weather_label.pack(pady=15)

graphik = tk.Frame(root, bg="#202b3c")
graphik.pack(padx=10, pady=10)



def weather_description(code):

    if code == 0:
        return "☀️ Ясно"

    elif code in [1, 2]:
        return "🌤️ Переважно сонячно"

    elif code == 3:
        return "☁️ Хмарно"

    elif code in [45, 48]:
        return "🌫️ Туман"

    elif code in [51, 53, 55, 56, 57]:
        return "🌦️ Мряка"

    elif code in [61, 63, 65, 66, 67]:
        return "🌧️ Дощ"

    elif code in [71, 73, 75, 77]:
        return "❄️ Сніг"

    elif code in [80, 81, 82]:
        return "🌧️ Зливи"

    elif code in [85, 86]:
        return "🌨️ Снігопад"

    elif code in [95, 96, 99]:
        return "⛈️ Гроза"

    
def get_porada(forecast):
    

    prompt = f"""
    Проаналізуй прогноз погоди на 7 днів:

    {forecast}

    Дай відповідь українською мовою.

    Напиши:
    1. Загальну характеристику погоди.
    2. Що краще одягати.
    3. Коли потрібна парасолька.
    4. У які дні буде найхолодніше.
    5. У які дні буде найтепліше.

    Відповідай зрозуміло, коротко і з емодзі.
    Не вигадуй дані, яких немає у прогнозі.
    """

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "Ти Voxel AI, розумний помічник з прогнозування погоди."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    response = requests.post(
        
        headers=headers,
        json=data,
        timeout=40
    )

    response.raise_for_status()

    result = response.json()

    return result["choices"][0]["message"]["content"]



def get_weather():
    
    global canvas
    
    canvas = None
    city = city_entry.get().strip()

    

    weather_label.config(text="Завантаження...")
    

    root.update_idletasks()

    try:

        url = "https://geocoding-api.open-meteo.com/v1/search"

        response = requests.get(
            url,
            params={
                "name": city,
                "count": 1,
                "language": "uk",
                "format": "json"
            },
            timeout=15
        )

       
        data = response.json()

        location = data["results"][0]

        lat = location["latitude"]
        lon = location["longitude"]
        city_name = location["name"]


        weather_url = "https://api.open-meteo.com/v1/forecast"

        response = requests.get(
            weather_url,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,precipitation,weather_code,is_day",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code",
                "forecast_days": 7,
                "timezone": "auto"
            },
            timeout=15
        )

        response.raise_for_status()
        weather = response.json()

        current = weather["current"]
        daily = weather["daily"]

        temperature = current["temperature_2m"]
        rain = current["precipitation"]
        code = current["weather_code"]

        description = weather_description(code)

        
        weather_label.config(
            text=(
                f" {city_name}\n"
                f" Температура: {temperature} °C\n"
                f" Зараз: {description}\n"
                f" Опади: {rain} мм"
            )
        )

   
        if canvas:
            canvas.get_tk_widget().destroy()

        dates = daily["time"]
        max_temp = daily["temperature_2m_max"]
        min_temp = daily["temperature_2m_min"]

        fig, ax = plt.subplots(figsize=(8, 3.5))

        ax.plot(
            dates,
            max_temp,
            marker="o",
            label="Максимальна температура"
        )

        ax.plot(
            dates,
            min_temp,
            marker="o",
            label="Мінімальна температура"
        )

        ax.set_title("Прогноз температури на 7 днів")
        ax.set_ylabel("Температура °C")
        ax.set_xlabel("Дата")

        ax.legend()
        ax.grid(True)
        ax.tick_params(axis="x", rotation=35)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(
            fig,
            master=graphik
        )

        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        plt.close(fig)

        
        forecast = []

        for i in range(len(dates)):

            day = {
                "Дата": dates[i],
                "Максимальна температура": max_temp[i],
                "Мінімальна температура": min_temp[i],
                "Опади мм": daily["precipitation_sum"][i],
                "Погода": weather_description(
                    daily["weather_code"][i]
                )
            }

            forecast.append(day)


    except requests.exceptions.Timeout:
        messagebox.showerror(
            "Помилка",
            "Сервер не відповідає. Спробуй ще раз."
        )

    except requests.exceptions.RequestException as e:
        messagebox.showerror(
            "Помилка мережі",
            str(e)
        )

    except Exception as e:
        messagebox.showerror(
            "Помилка",
            str(e)
        )
        

        
button = tk.Button(
    root,
    text="ДІЗНАТИСЯ ПОГОДУ",
    font=("Arial", 14, "bold"),
    bg="#318ce7",
    fg="white",
    command=get_weather
)

button.pack(pady=10)

root.mainloop()
