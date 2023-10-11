from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle the form submission
        nombre = request.form['nombre']
        actividad = request.form['actividad']
        cantidad_personas = request.form['cantidad_personas']
        pago_total = request.form['pago_total']
        
        # You can process or save the data as needed.
        # For now, let's return it as a JSON response:
        return jsonify({
            "Nombre": nombre,
            "Actividad": actividad,
            "Cantidad de Personas": cantidad_personas,
            "Pago Total": pago_total
        })

    return render_template('form.html')

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
