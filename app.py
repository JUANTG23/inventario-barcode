from flask import Flask, render_template, request, redirect
import csv
from datetime import datetime
import os

app = Flask(__name__)

CSV_FILE = 'inventario.csv'

def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='latin-1') as file:
            writer = csv.writer(file)
            writer.writerow(['Código de barras', 'Nombre', 'Cantidad', 'Fecha'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/guardar', methods=['POST'])
def guardar():
    codigo = request.form['codigo']
    nombre = request.form['nombre']
    cantidad = request.form['cantidad']
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(CSV_FILE, 'a', newline='', encoding='latin-1') as file:
        writer = csv.writer(file)
        writer.writerow([codigo, nombre, cantidad, fecha])

    return redirect('/')

@app.route('/lista')
def lista():
    inventario = []
    try:
        with open(CSV_FILE, newline='', encoding='latin-1') as file:
            reader = csv.reader(file)
            next(reader, None)  # Saltar encabezado
            for fila in reader:
                if len(fila) == 4:
                    inventario.append(fila)
    except Exception as e:
        print(f"❌ Error leyendo CSV: {e}")
        inventario = []
    return render_template('lista.html', inventario=inventario)

@app.route('/buscar', methods=['GET', 'POST'])
def buscar():
    resultado = None
    if request.method == 'POST':
        codigo_buscado = request.form['codigo']
        try:
            with open(CSV_FILE, newline='', encoding='latin-1') as file:
                reader = csv.reader(file)
                next(reader, None)  # Saltar encabezado
                for fila in reader:
                    if fila[0] == codigo_buscado:
                        resultado = fila
                        break
            if resultado is None:
                resultado = []
        except Exception as e:
            print(f"❌ Error leyendo CSV en buscar: {e}")
            resultado = []
    return render_template('buscar.html', resultado=resultado)

if __name__ == '__main__':
    init_csv()
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
