import tkinter as tk
from tkinter import ttk
import pandas as pd
from sklearn.tree import DecisionTreeRegressor
import os
import re

# ---------- LOAD & CLEAN DATASET ----------
model = None
file_path = "2013-1.csv"   #  dataset file

if os.path.exists(file_path):
    try:
        df = pd.read_csv(file_path)

        # Keep required columns
        df = df[["Dist.Run", "Fuel"]]

        # Clean Distance column
        def clean_distance(value):
            if isinstance(value, str):
                value = value.replace("M", "")
                value = value.replace("*", "")
                value = re.sub("[^0-9.]", "", value)
            return value

        df["Dist.Run"] = df["Dist.Run"].apply(clean_distance)

        # Convert to numeric
        df["Dist.Run"] = pd.to_numeric(df["Dist.Run"], errors="coerce")
        df["Fuel"] = pd.to_numeric(df["Fuel"], errors="coerce")

        # Remove null values
        df = df.dropna()

        # Remove unrealistic data
        df = df[(df["Fuel"] > 0) & (df["Fuel"] < 500)]
        df = df[(df["Dist.Run"] > 1) & (df["Dist.Run"] < 2000)]

        # 🔥 Create Fuel per KM column
        df["Fuel_per_km"] = df["Fuel"] / df["Dist.Run"]

        # Remove unrealistic mileage values
        df = df[(df["Fuel_per_km"] > 0.1) & (df["Fuel_per_km"] < 1)]

        if len(df) > 20:
            X = df[["Dist.Run"]]
            y = df["Fuel_per_km"]

            model = DecisionTreeRegressor(
                max_depth=4,
                min_samples_leaf=5,
                min_samples_split=10,
                random_state=42
            )

            model.fit(X, y)

    except:
        model = None


# ---------- GUI ----------
root = tk.Tk()
root.title("Bus Fuel Consumption Prediction (Decision Tree)")
root.geometry("950x650")
root.resizable(False, False)

canvas = tk.Canvas(root, width=950, height=650)
canvas.pack(fill="both", expand=True)

for i in range(0, 650):
    color = f"#{int(10+i/8):02x}{int(10+i/8):02x}{int(10+i/8):02x}"
    canvas.create_line(0, i, 950, i, fill=color)

container = tk.Frame(root, bg="#1e1e1e", bd=2, relief="ridge")
container.place(relx=0.5, rely=0.5, anchor="center", width=520, height=520)

title = tk.Label(container,
                 text="BUS FUEL CONSUMPTION PREDICTION (Decision Tree)",
                 font=("Arial", 14, "bold"),
                 fg="white",
                 bg="#1e1e1e")
title.pack(pady=15)

tk.Label(container, text="Distance (km)", fg="white", bg="#1e1e1e").pack()
distance_entry = tk.Entry(container)
distance_entry.pack(pady=5)

tk.Label(container, text="Traffic Level", fg="white", bg="#1e1e1e").pack()
traffic = ttk.Combobox(container, values=["Low", "Moderate", "High"], state="readonly")
traffic.pack(pady=5)

tk.Label(container, text="Road Type", fg="white", bg="#1e1e1e").pack()
road = ttk.Combobox(container, values=["Highway", "City", "Hilly"], state="readonly")
road.pack(pady=5)

tk.Label(container, text="Passenger Load", fg="white", bg="#1e1e1e").pack()
passengers = ttk.Combobox(container, values=["Low", "Medium", "Full"], state="readonly")
passengers.pack(pady=5)

tk.Label(container, text="AC Usage", fg="white", bg="#1e1e1e").pack()
ac = ttk.Combobox(container, values=["OFF", "ON"], state="readonly")
ac.pack(pady=5)

result_label = tk.Label(container,
                        text="Fuel estimation will appear here",
                        font=("Arial", 12, "bold"),
                        fg="#00ffcc",
                        bg="#1e1e1e")
result_label.pack(pady=20)

# ---------- MANUAL ADJUSTMENT ----------
def manual_adjustment(fuel):
    factor = 1.0

    if traffic.get() == "High":
        factor *= 1.2
    elif traffic.get() == "Moderate":
        factor *= 1.1

    if road.get() == "Hilly":
        factor *= 1.25
    elif road.get() == "City":
        factor *= 1.15

    if passengers.get() == "Full":
        factor *= 1.15
    elif passengers.get() == "Medium":
        factor *= 1.05

    if ac.get() == "ON":
        factor *= 1.1

    return fuel * factor


# ---------- PREDICTION FUNCTION ----------
def predict():
    try:
        distance = float(distance_entry.get())

        if model is not None:
            # Predict fuel per km using Decision Tree
            fuel_per_km = model.predict([[distance]])[0]
            base_fuel = fuel_per_km * distance
        else:
            # Fallback if dataset not loaded
            base_fuel = distance / 4

        final_fuel = manual_adjustment(base_fuel)
        cost = final_fuel * 95

        result_label.config(
            text=f"Fuel Needed: {final_fuel:.2f} L\nEstimated Cost: ₹{cost:.2f}"
        )

    except:
        result_label.config(text="Enter valid inputs")


btn = tk.Button(container,
                text="Predict Fuel",
                font=("Arial", 12, "bold"),
                bg="#00b894",
                fg="white",
                width=20,
                command=predict)

btn.pack(pady=10)

root.mainloop()