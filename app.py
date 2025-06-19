from flask import Flask, render_template, request, redirect, send_file
import csv
import os
from datetime import datetime
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)
CSV_FILE = 'inventario.csv'
SHEET_NAME = 'Inventario en Tiempo Real'

# === Google Sheets Setup ===
def conectar_google_sheets():
    try:
        google_creds = os.getenv("GOOGLE_CREDENTIALS")
        if not google_creds:
            raise ValueError("GOOGLE_CREDENTIALS no está configurado")
        
        credentials_dict = json.loads(google_creds)
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
        client = gspread.authorize(credentials)
        sheet = client.open(SHEET_NAME).sheet1
        return sheet
    except Exception as e:
        print(f"[ERROR] No se pudo conectar a Google Sheets: {e}")
        return None

sheet = conectar_google_sheets()

# === Crear CSV si no existe ===
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
    codigo = request.form['codigo']
    nombre = request.form['nombre']
    cantidad = int(request.form['cantidad'])
    tipo = request.form['tipo']
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Guardar localmente
    with open(CSV_FILE, 'a', newline='', encoding='latin-1') as file:
        writer = csv.writer(file)
        writer.writerow([codigo, nombre, cantidad, tipo, fecha])

    # Guardar en Google Sheets
    if sheet:
        try:
            sheet.append_row([codigo, nombre, cantidad, tipo, fecha])
            print(f"[INFO] Producto {codigo} guardado en Google Sheets")
        except Exception as e:
            print(f"[ERROR] Falló al guardar en Google Sheets: {e}")

    return redirect('/')

@app.route('/lista')
def lista():
    inventario = []
    movimientos = []

    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, newline='', encoding='latin-1') as file:
            reader = csv.DictReader(file)
            for row in reader:
                codigo = row['Código']
                nombre = row['Nombre']
                cantidad = int(row['Cantidad'])
                tipo = row['Tipo']
                fecha = row['Fecha']
                movimientos.append(row)

                encontrado = next((item for item in inventario if item['codigo'] == codigo), None)
                if encontrado:
                    if tipo == "Entrada":
                        encontrado['cantidad'] += cantidad
                    else:
                        encontrado['cantidad'] -= cantidad
                else:
                    stock = cantidad if tipo == "Entrada" else -cantidad
                    inventario.append({
                        'codigo': codigo,
                        'nombre': nombre,
                        'cantidad': stock
                    })

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
    app.run(debug=True, host='0.0.0.0', port=port)
