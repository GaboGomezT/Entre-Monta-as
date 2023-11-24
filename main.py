from datetime import datetime
from dotenv import load_dotenv
import json

load_dotenv()

import os
from flask import Flask, jsonify, request, render_template
from pyairtable import Table
from log_config import setup_logging

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

# Set up logging and add the file handler to the app logger
file_handler = setup_logging()
app.logger.addHandler(file_handler)


@app.route("/", methods=["GET", "POST"])
def index():
    # Fetch UUID from query parameters, if present
    uuid_param = request.args.get("uuid")

    # Fetch all records from MIEMBROS table
    miembros = miembros_table.all()
    actividades = actividades_table.all()

    # Filter miembros for empty fields
    miembros = list(filter(lambda record: record["fields"], miembros))

    # Filter actividades for empty fields
    actividades = list(filter(lambda record: record["fields"], actividades))

    # Remove trailing spaces from names
    miembros = [
        {
            **record,
            "fields": {**record["fields"], "Name": record["fields"]["Name"].strip()},
        }
        for record in miembros
    ]

    # Remove trailing spaces from activities
    actividades = [
        {
            **record,
            "fields": {
                **record["fields"],
                "ACTIVIDADES": record["fields"]["ACTIVIDADES"].strip(),
            },
        }
        for record in actividades
    ]

    member_status = {
        record["fields"]["Name"]: record["fields"]["Status"] for record in miembros
    }

    # # Extract activiity names and prices for dropdown
    activity_names = [record["fields"]["ACTIVIDADES"] for record in actividades]
    activities = {
        record["fields"]["ACTIVIDADES"]: {
            "PRECIO": record["fields"]["PRECIO"],
            "PRECIO_MEMBRESIA": record["fields"]["PRECIO_MEMBRESIA"],
        }
        for record in actividades
    }

    if request.method == "POST":
        # Handle the form submission
        nombre = request.form["nombre"]
        if nombre == "new":
            nombre = request.form["new_nombre"]

        actividad = (
            request.form["actividad"].replace('"', "").strip()
        )  # This will remove any double quotes from the input.
        cantidad_personas = int(request.form["cantidad_personas"])
        adelanto = float(request.form["adelanto"])
        costo_guia = int(request.form["costo_guia"])
        costo_taller = int(request.form["costo_taller"])
        costo_comida = int(request.form["costo_comida"])
        fecha_str = request.form["fecha"]
        fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%dT%H:%M")
        formatted_fecha = fecha_obj.isoformat() + "Z"  # 'Z' indicates UTC time

        precio_personalizado = (
            activities[actividad]["PRECIO_MEMBRESIA"]
            if nombre in member_status.keys() and member_status[nombre] == "ACTIVO"
            else activities[actividad]["PRECIO"]
        )
        pago_total = int(cantidad_personas) * precio_personalizado
        falta_pagar = pago_total - int(adelanto)
        costo = costo_guia + costo_taller + costo_comida
        costo_total = int(cantidad_personas) * costo
        ganancia = pago_total - costo_total

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
            "Costo_Guia": costo_guia * int(cantidad_personas),
            "Costo_Comida": costo_comida * int(cantidad_personas),
            "Costo_Taller": costo_taller * int(cantidad_personas),
            "Fecha Actividad": formatted_fecha,
        }
        print(new_reservation)
        reservaciones_table.create(new_reservation)

    name = None
    if uuid_param:
        # From members table, fetch the record with the given UUID
        # UUID is a key in the fields dictionary
        try:
            # find the record with the given UUID
            member = next(
                filter(lambda record: record["fields"]["UUID"] == uuid_param, miembros)
            )
            # get the name from the record
            name = member["fields"]["Name"]
        except StopIteration:
            app.logger.error(f"UUID {uuid_param} not found in members table")

    serialized_activities = json.dumps(activities)
    return render_template(
        "form.html",
        activity_names=activity_names,
        name=name,
        activities=serialized_activities,
    )


if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT", default=5000))
