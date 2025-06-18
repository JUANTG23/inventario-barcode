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

if __name__ == '__main__':
    init_csv()
    app.run(debug=True, host='0.0.0.0', port=5000)
