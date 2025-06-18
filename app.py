from flask import Flask, render_template, request, redirect, send_file
import csv
from datetime import datetime
import os

app = Flask(__name__)

CSV_FILE = 'inventario.csv'

# Crear archivo CSV si no existe
def init_csv():
    try:
        with open(CSV_FILE, 'x', newline='', encoding='latin-1') as file:
            writer = csv.writer(file)
            writer.writerow(['Código de barras', 'Nombre', 'Cantidad', 'Fecha'])
    except FileExistsError:
        pass

# Página principal
@app.route('/')
def index():
    return render_template('index.html')

# Guardar producto
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

# Ver productos guardados
@app.route('/lista')
def lista():
    inventario = []
    with open(CSV_FILE, newline='', encoding='latin-1') as file:
        reader = csv.reader(file)
        next(reader, None)  # Saltar encabezado
        inventario = list(reader)
    return render_template('lista.html', inventario=inventario)

# Buscar por código
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

# Descargar inventario CSV
@app.route('/descargar')
def descargar():
    return send_file(CSV_FILE, as_attachment=True, download_name='inventario.csv')

# Ejecutar app
if __name__ == '__main__':
    init_csv()
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
