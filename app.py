from flask import Flask, render_template, request, redirect, send_file
import csv
import os
import io
from datetime import datetime
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

# Cargar variables del entorno
load_dotenv()

app = Flask(__name__)

INVENTARIO_CSV = "inventario.csv"

# Conexión a Google Sheets desde .env
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
google_creds = json.loads(os.environ["GOOGLE_CREDENTIALS"])
credentials = ServiceAccountCredentials.from_json_keyfile_dict(google_creds, scope)
client = gspread.authorize(credentials)
sheet = client.open("Inventario en Tiempo Real").sheet1

def guardar_producto(codigo, nombre, cantidad):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    existe = os.path.isfile(INVENTARIO_CSV)
    
    with open(INVENTARIO_CSV, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not existe:
            writer.writerow(["Código de barras", "Nombre", "Cantidad", "Fecha"])
        writer.writerow([codigo, nombre, cantidad, fecha])
    
    sheet.append_row([codigo, nombre, cantidad, fecha])

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/guardar", methods=["POST"])
def guardar():
    codigo = request.form["codigo"]
    nombre = request.form["nombre"]
    cantidad = request.form["cantidad"]
    
    if codigo and nombre and cantidad:
        guardar_producto(codigo, nombre, cantidad)
    
    return redirect("/")

@app.route("/lista")
def lista():
    productos = []

    if os.path.isfile(INVENTARIO_CSV):
        with open(INVENTARIO_CSV, "r", encoding="latin-1") as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    codigo = row["Código de barras"]
                    nombre = row["Nombre"]
                    cantidad = int(row["Cantidad"])
                    fecha = row["Fecha"]
                    productos.append({
                        "codigo": codigo,
                        "nombre": nombre,
                        "cantidad": cantidad,
                        "fecha": fecha,
                        "estado": (
                            "Pocas unidades" if cantidad <= 3 else
                            "Inventario bajo" if cantidad <= 5 else
                            "Suficiente"
                        )
                    })
                except (KeyError, ValueError):
                    continue  # Saltar si falta alguna columna o cantidad no es número

    return render_template("lista.html", productos=productos)

@app.route("/descargar")
def descargar():
    if not os.path.isfile(INVENTARIO_CSV):
        return "No hay inventario aún."

    with open(INVENTARIO_CSV, mode="r", encoding="utf-8") as file:
        contenido = file.read()

    return send_file(
        io.BytesIO(contenido.encode("utf-8")),
        mimetype="text/csv",
        as_attachment=True,
        download_name="inventario.csv"
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
