from flask import Flask, render_template, request, redirect
import csv
from datetime import datetime
import os

app = Flask(__name__)
CSV_FILE = 'inventario.csv'

def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Código de barras', 'Nombre', 'Cantidad', 'Fecha'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/guardar', methods=['POST'])
def guardar():
    codigo = request.form.get('codigo', '').strip()
    nombre = request.form.get('nombre', '').strip()
    cantidad = request.form.get('cantidad', '').strip()
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not codigo or not nombre or not cantidad:
        return "Error: todos los campos son obligatorios.", 400

    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([codigo, nombre, cantidad, fecha])

    return redirect('/')

@app.route('/lista')
def lista():
    inventario = []
    with open(CSV_FILE, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader, None)
        for fila in reader:
            if len(fila) == 4:
                inventario.append(fila)
    return render_template('lista.html', inventario=inventario)

@app.route('/buscar', methods=['GET', 'POST'])
def buscar():
    resultado = None
    if request.method == 'POST':
        codigo_buscado = request.form['codigo'].strip()
        with open(CSV_FILE, newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader, None)
            for fila in reader:
                if len(fila) >= 1 and fila[0] == codigo_buscado:
                    resultado = fila
                    break
            if resultado is None:
                resultado = []
    return render_template('buscar.html', resultado=resultado)

if __name__ == '__main__':
    init_csv()
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
