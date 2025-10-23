from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

app = Flask(__name__, static_folder='.')
CORS(app)

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")
supabase = create_client(supabase_url, supabase_key)

@app.route("/")
def index():
    return send_from_directory('.', 'index.html')


@app.route("/api/restaurants", methods=["GET"])
def get_restaurants():
    try:
        result = supabase.table("restaurant").select("*").order("ville").execute()
        return jsonify(result.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/kpis", methods=["GET"])
def get_kpis():
    try:
        result = supabase.table("restaurant").select("*").execute()
        restaurants = result.data

        kpis = {}
        for r in restaurants:
            ville = r["ville"]
            if ville not in kpis:
                kpis[ville] = {
                    "ville": ville,
                    "nombre_restaurants": 0,
                    "total_notes": 0,
                    "total_avis": 0,
                    "meilleure_note": 0,
                    "pire_note": 5
                }

            kpis[ville]["nombre_restaurants"] += 1
            kpis[ville]["total_notes"] += r["note"]
            kpis[ville]["total_avis"] += r["nb_avis"]
            kpis[ville]["meilleure_note"] = max(kpis[ville]["meilleure_note"], r["note"])
            kpis[ville]["pire_note"] = min(kpis[ville]["pire_note"], r["note"])

        results = []
        for ville, data in kpis.items():
            results.append({
                "ville": ville,
                "nombre_restaurants": data["nombre_restaurants"],
                "moyenne_note": round(data["total_notes"] / data["nombre_restaurants"], 1),
                "total_avis": data["total_avis"],
                "meilleure_note": data["meilleure_note"],
                "pire_note": data["pire_note"]
            })

        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/bubble-chart", methods=["GET"])
def get_bubble_chart_data():
    try:
        result = supabase.table("restaurant").select("*").execute()
        restaurants = result.data

        city_data = {}
        for r in restaurants:
            ville = r["ville"]
            if ville not in city_data:
                city_data[ville] = {
                    "ville": ville,
                    "total_notes": 0,
                    "total_avis": 0,
                    "nombre_restaurants": 0
                }

            city_data[ville]["total_notes"] += r["note"]
            city_data[ville]["total_avis"] += r["nb_avis"]
            city_data[ville]["nombre_restaurants"] += 1

        results = []
        for ville, data in city_data.items():
            results.append({
                "ville": ville,
                "moyenne_note": round(data["total_notes"] / data["nombre_restaurants"], 1),
                "total_avis": data["total_avis"],
                "nombre_restaurants": data["nombre_restaurants"]
            })

        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/pie-chart", methods=["GET"])
def get_pie_chart_data():
    try:
        result = supabase.table("restaurant").select("*").execute()
        restaurants = result.data

        city_counts = {}
        for r in restaurants:
            ville = r["ville"]
            city_counts[ville] = city_counts.get(ville, 0) + 1

        results = [
            {"ville": ville, "nombre_restaurants": count}
            for ville, count in city_counts.items()
        ]

        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/line-chart", methods=["GET"])
def get_line_chart_data():
    try:
        result = supabase.table("restaurant").select("*").execute()
        restaurants = result.data

        city_data = {}
        for r in restaurants:
            ville = r["ville"]
            if ville not in city_data:
                city_data[ville] = {"total_notes": 0, "count": 0}

            city_data[ville]["total_notes"] += r["note"]
            city_data[ville]["count"] += 1

        results = sorted([
            {
                "ville": ville,
                "moyenne_note": round(data["total_notes"] / data["count"], 1)
            }
            for ville, data in city_data.items()
        ], key=lambda x: x["ville"])

        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

