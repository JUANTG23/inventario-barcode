from flask import Flask, render_template, request, redirect, send_file
import csv
import os
from datetime import datetime

app = Flask(__name__)
CSV_FILE = 'inventario.csv'
INVENTARIO_TEMP = {}

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

    # Leer inventario actual
    rows = []
    encontrado = False

    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r', newline='', encoding='latin-1') as file:
            reader = csv.reader(file)
            rows = list(reader)

    # Agregar nueva fila de movimiento
    with open(CSV_FILE, 'a', newline='', encoding='latin-1') as file:
        writer = csv.writer(file)
        writer.writerow([codigo, nombre, cantidad, tipo, fecha])

    return redirect('/')

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
