from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

import anthropic
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def cargar_datos():
    with open("data/polizas.json", encoding="utf-8") as f:
        polizas = json.load(f)
    with open("data/hospitales.json", encoding="utf-8") as f:
        hospitales = json.load(f)
    with open("data/copagos.json", encoding="utf-8") as f:
        copagos = json.load(f)
    with open("data/usuarios.json", encoding="utf-8") as f:
        usuarios = json.load(f)
    return polizas, hospitales, copagos, usuarios

class LoginRequest(BaseModel):
    usuario: str
    password: str

class MensajeRequest(BaseModel):
    mensaje: str
    paciente_id: str
    historial: list = []

@app.get("/")
def index():
    return FileResponse("index.html")

@app.post("/login")
def login(request: LoginRequest):
    polizas, _, _, usuarios = cargar_datos()

    usuario = next((u for u in usuarios
        if u["usuario"] == request.usuario
        and u["password"] == request.password), None)

    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

    paciente = next((p for p in polizas if p["id"] == usuario["paciente_id"]), None)

    deducible_disponible = paciente["deducible_anual"] - paciente["deducible_usado"]
    estado_poliza = "Vigente" if paciente["vigente"] else "Vencida"

    bienvenida = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=300,
        messages=[{
                        "role": "user",
                        "content": f"""
                Genera un mensaje de bienvenida corto y cálido para un paciente que acaba de iniciar sesión 
                en su asistente de cobertura médica. Incluye exactamente esta información:

                - Nombre del paciente: {paciente["nombre"]}
                - Estado de la póliza: {estado_poliza}
                - Plan contratado: {paciente["plan"]}
                - Deducible anual: ${paciente["deducible_anual"]}
                - Deducible usado: ${paciente["deducible_usado"]}
                - Deducible disponible: ${deducible_disponible}

                El mensaje debe:
                1. Saludar por el nombre
                2. Mostrar el estado de la póliza con una viñeta
                3. Mostrar el resumen del deducible con una viñeta
                4. Invitar al paciente a describir su síntoma o consulta
                5. Ser breve, máximo 5 líneas
                6. No usar tablas, solo viñetas y texto
                """
                    }]
    )

    return {
        "paciente_id": usuario["paciente_id"],
        "nombre": paciente["nombre"],
        "plan": paciente["plan"],
        "vigente": paciente["vigente"],
        "bienvenida": bienvenida.content[0].text
    }

@app.post("/chat")
def chat(request: MensajeRequest):
    polizas, hospitales, copagos, _ = cargar_datos()

    paciente = next((p for p in polizas if p["id"] == request.paciente_id), None)

    if not paciente:
        return {"respuesta": "No encontré tu póliza. Verifica tu sesión."}

    system_prompt = f"""
Eres un asistente de seguros médicos amable y claro. Tu trabajo es ayudar al paciente a entender
su cobertura antes de atenderse.

DATOS DEL PACIENTE:
{json.dumps(paciente, ensure_ascii=False, indent=2)}

RED DE HOSPITALES DISPONIBLES:
{json.dumps(hospitales, ensure_ascii=False, indent=2)}

TABLA DE COPAGOS POR ESPECIALIDAD:
{json.dumps(copagos, ensure_ascii=False, indent=2)}

INSTRUCCIONES:
1. Cuando el paciente describa un síntoma, si necesitas más contexto para identificar 
la especialidad correcta, haz una pregunta a la vez. Máximo 3 preguntas antes de 
dar una recomendación. Una vez que tengas suficiente contexto, identifica la 
especialidad y calcula el copago.
2. Considera todas las respuestas dadas por el paciente y recomienda una especialidad. Si son diferentes,
recomienda la especialidad más adecuada, evita seguir haciendo preguntas.
3. Consulta la tabla de copagos y calcula exactamente cuánto pagará el paciente según su plan.
4. Si el deducible anual ya fue usado completamente, indícalo.
5. Busca la ciudad de cada usuario y recomienda sólo hospitales en la ciudad del usuario, 
en caso de no existir un hospital dentro de la ciudad recomienda el más cercano. Esto debe ser considerado en tu respuesta.
6. Si la especialidad requiere referencia previa, avisa al paciente.
5. Recomienda el hospital más conveniente económicamente dentro de la red según su plan. 
7. Responde siempre en español, de forma clara y sin jerga técnica de seguros.
8. Sé conciso pero completo. Usa un tono cálido y profesional.
9. Nunca reveles datos de otros pacientes. Solo tienes acceso al paciente autenticado.
10. No respondas con tablas, responde con texto separado por viñetas.
11. Si los sintomas estan clasificados como para una emergencia, deriva directamente al paciente a
atención de emergencia en el hospital mas cercano. Omite cualquier calculo o recomendación más económica.

FORMATO DE RESPUESTA OBLIGATORIO cuando tengas suficiente contexto para recomendar:
Responde siempre en texto corrido, sin tablas ni markdown. Sigue exactamente este orden:

Primero: indica la especialidad recomendada y por qué.
Segundo: explica la cobertura del plan del paciente para esa especialidad.
Tercero: lista cada hospital disponible en la red con su copago estimado, uno por línea.
Cuarto: recomienda el hospital más conveniente económicamente.
Quinto: agrega una nota final útil, como validar disponibilidad o si necesita referencia previa.

Ejemplo del tono y formato esperado:
"Según los síntomas que describes, la especialidad recomendada es [especialidad] como primer punto de atención.
Con tu plan [plan], tienes cobertura para [tipo de atención] dentro de la red.
Las opciones disponibles en tu red son:
- [Hospital A]: copago estimado de $[X]
- [Hospital B]: copago estimado de $[X]
La opción más conveniente económicamente es [Hospital A].
[Nota adicional relevante].

"""

    historial_recortado = request.historial[-14:]
    mensajes = historial_recortado + [
        {"role": "user", "content": request.mensaje}
    ]

    respuesta = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system=system_prompt,
        messages=mensajes
    )

    return {"respuesta": respuesta.content[0].text}