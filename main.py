from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

import os
from flask import Flask, jsonify, request, render_template
from pyairtable import Table

# Configuration
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
MIEMBROS_TABLE_NAME = "MIEMBROS"
ACTIVIDADES_TABLE_NAME = "ACTIVIDADES"
RESERVACIONES_TABLE_NAME = "RESERVACIONES"

# Setup connection to the table
miembros_table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, MIEMBROS_TABLE_NAME)
actividades_table = Table(AIRTABLE_API_KEY, AIRTABLE_BASE_ID, ACTIVIDADES_TABLE_NAME)
reservaciones_table = Table(
    AIRTABLE_API_KEY, AIRTABLE_BASE_ID, RESERVACIONES_TABLE_NAME
)

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    # Fetch all records from MIEMBROS table
    miembros = miembros_table.all()
    actividades = actividades_table.all()

    # Extract names for dropdown
    names = [record["fields"]["Name"] for record in miembros]
    member_status = {
        record["fields"]["Name"]: record["fields"]["Status"] for record in miembros
    }

    # # Extract activiity names and prices for dropdown
    activity_names = [record["fields"]["ACTIVIDADES"] for record in actividades]
    activities = {
        record["fields"]["ACTIVIDADES"]: {
            "PRECIO": record["fields"]["PRECIO"],
            "PRECIO_MEMBRESIA": record["fields"]["PRECIO_MEMBRESIA"],
            "COSTO_GUIA": record["fields"]["COSTO_GUIA"],
            "COSTO_COMIDA": record["fields"]["COSTO_COMIDA"],
            "COSTO_TALLER": record["fields"]["COSTO_TALLER"],
        }
        for record in actividades
    }

    if request.method == "POST":
        # Handle the form submission
        nombre = request.form["nombre"]
        actividad = request.form["actividad"].replace('"', '').strip()  # This will remove any double quotes from the input.
        cantidad_personas = int(request.form["cantidad_personas"])
        adelanto = float(request.form["adelanto"])
        precio_personalizado = (
            activities[actividad]["PRECIO_MEMBRESIA"]
            if member_status[nombre] == "ACTIVO"
            else activities[actividad]["PRECIO"]
        )
        pago_total = int(cantidad_personas) * precio_personalizado
        falta_pagar = pago_total - int(adelanto)
        costo = (
            activities[actividad]["COSTO_GUIA"]
            + activities[actividad]["COSTO_COMIDA"]
            + activities[actividad]["COSTO_TALLER"]
        )
        ganancia = pago_total - costo

        # Create a new row in RESERVACIONES
        new_reservation = {
            "Fecha": str(
                datetime.now()
            ),  # Assuming you want the current timestamp. Adjust as needed.
            "Actividad": actividad,
            "Nombre": nombre,
            "Adelanto": adelanto,
            "Personas": cantidad_personas,
            "Pago Total": pago_total,
            "Falta pagar": falta_pagar,
            "Ganancia": ganancia,
        }
        reservaciones_table.create(new_reservation)
        # You can process or save the data as needed.
        # For now, let's return it as a JSON response:
        return jsonify(
            {
                "Nombre": nombre,
                "Actividad": actividad,
                "Cantidad de Personas": cantidad_personas,
                "pago total": pago_total,
            }
        )

    return render_template("form.html", names=names, activity_names=activity_names)


if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT", default=5000))
