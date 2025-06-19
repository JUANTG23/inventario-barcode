from flask import Flask, render_template, request, redirect, send_file
import csv
import os
import json
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from io import StringIO
import base64

app = Flask(__name__)
CSV_FILE = 'inventario.csv'
SHEET_NAME = 'Inventario en Tiempo Real'

# Inicializar el archivo CSV si no existe
def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='latin-1') as file:
            writer = csv.writer(file)
            writer.writerow(['Código', 'Nombre', 'Cantidad', 'Tipo', 'Fecha'])

# Conexión con Google Sheets desde variable de entorno
def init_google_sheets():
    google_credentials_str = os.getenv("GOOGLE_CREDENTIALS")
    if google_credentials_str:
        credentials_dict = json.loads(google_credentials_str)
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            credentials_dict,
            ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        )
        client = gspread.authorize(credentials)
        return client.open(SHEET_NAME).sheet1
    return None

sheet = init_google_sheets()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/guardar', methods=['POST'])
def guardar():
    codigo = request.form['codigo']
    nombre = request.form['nombre']
    cantidad = int(request.form['cantidad'])
    tipo = request.form['tipo']
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Guardar en el CSV local
    with open(CSV_FILE, 'a', newline='', encoding='latin-1') as file:
        writer = csv.writer(file)
        writer.writerow([codigo, nombre, cantidad, tipo, fecha])

    # Guardar también en Google Sheets (si está conectado)
    if sheet:
        sheet.append_row([codigo, nombre, cantidad, tipo, fecha])

    return redirect('/')

@app.route('/lista')
def lista():
    inventario = []
    movimientos = []

    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, newline='', encoding='latin-1') as file:
            reader = csv.DictReader(file)
            for row in reader:
                codigo = row.get('Código')
                nombre = row.get('Nombre')
                tipo = row.get('Tipo')
                fecha = row.get('Fecha')

                try:
                    cantidad = int(row.get('Cantidad', 0))
                except ValueError:
                    cantidad = 0

                if not codigo or not nombre or not tipo:
                    continue

                movimientos.append(row)

                encontrado = next((item for item in inventario if item['codigo'] == codigo), None)
                if encontrado:
                    if tipo == "Entrada":
                        encontrado['cantidad'] += cantidad
                    elif tipo == "Salida":
                        encontrado['cantidad'] -= cantidad
                else:
                    stock = cantidad if tipo == "Entrada" else -cantidad
                    inventario.append({
                        'codigo': codigo,
                        'nombre': nombre,
                        'cantidad': stock
                    })

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
        codigo_buscado = request.form['codigo']
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
