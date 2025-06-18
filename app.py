from flask import Flask, render_template, request, redirect
import csv
from datetime import datetime

app = Flask(__name__)

CSV_FILE = 'inventario.csv'

def init_csv():
    try:
        with open(CSV_FILE, 'x', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Código de barras', 'Nombre', 'Cantidad', 'Fecha'])
    except FileExistsError:
        pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/guardar', methods=['POST'])
def guardar():
    codigo = request.form['codigo']
    nombre = request.form['nombre']
    cantidad = request.form['cantidad']
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(CSV_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([codigo, nombre, cantidad, fecha])

    return redirect('/')

import os

if __name__ == '__main__':
    init_csv()
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

@app.route('/lista')
def lista():
    with open(CSV_FILE, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Saltar la cabecera
        inventario = list(reader)
    return render_template('lista.html', inventario=inventario)
