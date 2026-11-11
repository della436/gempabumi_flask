from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, render_template, request


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "all_month.csv"
app = Flask(__name__)


def load_data():
    data = pd.read_csv(DATA_PATH)
    data["time"] = pd.to_datetime(data["time"], utc=True, errors="coerce")

    for column in ("latitude", "longitude", "mag", "depth"):
        data[column] = pd.to_numeric(data[column], errors="coerce")

    return data.dropna(subset=["latitude", "longitude", "mag"])


DATA = load_data()


def filtered_data():
    def read_magnitude(name, default):
        raw_value = request.args.get(name, "")

        try:
            return float(raw_value.replace(",", ".")) if raw_value else default
        except ValueError:
            return default

    minimum = read_magnitude("min_mag", 2.0)
    maximum = read_magnitude("max_mag", 8.0)

    minimum = max(0.0, min(minimum, 10.0))
    maximum = max(minimum, min(maximum, 10.0))

    result = DATA[DATA["mag"].between(minimum, maximum)]
    return result, minimum, maximum


@app.get("/")
def dashboard():
    return render_template(
        "dashboard.html",
        total=len(DATA),
        max_mag=DATA["mag"].max(),
    )


@app.get("/api/earthquakes")
def earthquakes():
    data, minimum, maximum = filtered_data()

    magnitudes = pd.cut(
        data["mag"],
        bins=[-float("inf"), 2, 3, 4, 5, 6, float("inf")],
        labels=["< 2", "2–3", "3–4", "4–5", "5–6", "6+"],
    )
    distribution = magnitudes.value_counts(sort=False)

    points = data[
        ["latitude", "longitude", "mag", "depth", "place", "time"]
    ].copy()
    points["time"] = points["time"].dt.strftime("%Y-%m-%d %H:%M UTC")
    points = points.where(pd.notna(points), None)

    strongest = data.nlargest(10, "mag")[["place", "mag", "depth", "time"]].copy()
    strongest["place"] = (
    strongest["place"].fillna("Lokasi tidak diketahui").astype(str))
    strongest["time"] = strongest["time"].dt.strftime("%Y-%m-%d %H:%M UTC")
    strongest = strongest.where(pd.notna(strongest), None)

    return jsonify(
        total=int(len(data)),
        max_mag=round(float(data["mag"].max()), 1) if len(data) else None,
        average_mag=round(float(data["mag"].mean()), 2) if len(data) else None,
        minimum=minimum,
        maximum=maximum,
        labels=[str(label) for label in distribution.index],
        counts=[int(value) for value in distribution.values],
        points=points.to_dict(orient="records"),
        strongest=strongest.to_dict(orient="records"),
    )


if __name__ == "__main__":
    app.run(debug=True)