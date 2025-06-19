from flask import Flask, render_template, request, redirect, send_file
import csv
import os
from datetime import datetime

# --- Google Sheets ---
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)
CSV_FILE = 'inventario.csv'

# ---------------------- GOOGLE SHEETS FUNCIONES ----------------------
def get_worksheet():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('google_credentials.json', scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open("Inventario en Tiempo Real")  # Asegúrate que este sea el nombre exacto
    worksheet = spreadsheet.sheet1
    return worksheet

# ---------------------- INICIAR CSV SI NO EXISTE ----------------------
def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='latin-1') as file:
            writer = csv.writer(file)
            writer.writerow(['Código', 'Nombre', 'Cantidad', 'Tipo', 'Fecha'])

# ---------------------- RUTA PRINCIPAL ----------------------
@app.route('/')
def index():
    return render_template('index.html')

# ---------------------- GUARDAR PRODUCTO ----------------------
@app.route('/guardar', methods=['POST'])
def guardar():
    codigo = request.form['codigo']
    nombre = request.form['nombre']
    cantidad = int(request.form['cantidad'])
    tipo = request.form['tipo']
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Guardar en CSV
    with open(CSV_FILE, 'a', newline='', encoding='latin-1') as file:
        writer = csv.writer(file)
        writer.writerow([codigo, nombre, cantidad, tipo, fecha])

    # Guardar en Google Sheets
    try:
        worksheet = get_worksheet()
        worksheet.append_row([codigo, nombre, cantidad, tipo, fecha])
    except Exception as e:
        print("Error al actualizar Google Sheets:", e)

    return redirect('/')

# ---------------------- LISTAR INVENTARIO ----------------------
@app.route('/lista')
def lista():
    inventario = []
    movimientos = []

    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, newline='', encoding='latin-1') as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                codigo, nombre, cantidad, tipo, fecha = row
                cantidad = int(cantidad)
                movimientos.append(row)

                encontrado = next((item for item in inventario if item[0] == codigo), None)
                if encontrado:
                    if tipo == "Entrada":
                        encontrado[2] += cantidad
                    else:
                        encontrado[2] -= cantidad
                else:
                    inventario.append([codigo, nombre, cantidad if tipo == "Entrada" else -cantidad])

    return render_template('lista.html', inventario=inventario)

# ---------------------- BUSCAR PRODUCTO ----------------------
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

# ---------------------- DESCARGAR ARCHIVO ----------------------
@app.route('/descargar')
def descargar():
    return send_file(CSV_FILE, as_attachment=True)

# ---------------------- INICIAR APP ----------------------
if __name__ == '__main__':
    init_csv()
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
