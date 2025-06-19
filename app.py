from flask import Flask, render_template, request, redirect, send_file
import csv
import os
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

app = Flask(__name__)
CSV_FILE = 'inventario.csv'
SHEET_NAME = 'Inventario en Tiempo Real'

# === CONEXIÓN CON GOOGLE SHEETS USANDO VARIABLE DE ENTORNO ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
google_creds_json = os.getenv("GOOGLE_CREDENTIALS")

if not google_creds_json:
    raise ValueError("GOOGLE_CREDENTIALS no está definida en las variables de entorno")

creds_dict = json.loads(google_creds_json)
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(credentials)
sheet = client.open(SHEET_NAME).sheet1

# === INICIALIZAR CSV SI NO EXISTE ===
def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='latin-1') as file:
            writer = csv.writer(file)
            writer.writerow(['Código', 'Nombre', 'Cantidad', 'Tipo', 'Fecha'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/guardar', methods=['POST'])
def guardar():
    codigo = request.form['codigo'].strip()
    nombre = request.form['nombre'].strip()
    cantidad = int(request.form['cantidad'])
    tipo = request.form['tipo'].strip()
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Guardar localmente en CSV
    with open(CSV_FILE, 'a', newline='', encoding='latin-1') as file:
        writer = csv.writer(file)
        writer.writerow([codigo, nombre, cantidad, tipo, fecha])

    # Guardar también en Google Sheets
    sheet.append_row([codigo, nombre, cantidad, tipo, fecha])

    return redirect('/')

@app.route('/lista')
def lista():
    inventario = []

    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, newline='', encoding='latin-1') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Validar campos vacíos
                if not row.get('Código') or not row.get('Nombre') or not row.get('Cantidad') or not row.get('Tipo'):
                    continue

                try:
                    codigo = row['Código'].strip()
                    nombre = row['Nombre'].strip()
                    cantidad = int(row['Cantidad'])
                    tipo = row['Tipo'].strip()
                except (ValueError, KeyError):
                    continue

                producto = next((p for p in inventario if p['codigo'] == codigo), None)

                if producto:
                    if tipo == 'Entrada':
                        producto['cantidad'] += cantidad
                    else:
                        producto['cantidad'] -= cantidad
                else:
                    stock = cantidad if tipo == 'Entrada' else -cantidad
                    inventario.append({'codigo': codigo, 'nombre': nombre, 'cantidad': stock})

    # Alertas visuales
    for item in inventario:
        if item['cantidad'] <= 0:
            item['alerta'] = 'danger'
        elif item['cantidad'] <= 5:
            item['alerta'] = 'warning'
        else:
            item['alerta'] = 'success'

    return render_template('lista.html', inventario=inventario)

@app.route('/buscar', methods=['GET', 'POST'])
def buscar():
    resultado = None
    if request.method == 'POST':
        codigo_buscado = request.form['codigo'].strip()
        with open(CSV_FILE, newline='', encoding='latin-1') as file:
            reader = csv.reader(file)
            next(reader, None)
            for fila in reader:
                if fila[0] == codigo_buscado:
                    resultado = fila
                    break
            if resultado is None:
                resultado = []  # No encontrado
    return render_template('buscar.html', resultado=resultado)

@app.route('/descargar')
def descargar():
    return send_file(CSV_FILE, as_attachment=True)

if __name__ == '__main__':
    init_csv()
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
