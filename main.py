from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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
    return polizas, hospitales, copagos

class MensajeRequest(BaseModel):
    mensaje: str
    paciente_id: str
    historial: list = []

@app.get("/")
def index():
    return FileResponse("index.html")

@app.post("/chat")
def chat(request: MensajeRequest):
    polizas, hospitales, copagos = cargar_datos()

    paciente = next((p for p in polizas if p["id"] == request.paciente_id), None)

    if not paciente:
        return {"respuesta": "No encontré tu póliza. Verifica tu ID de paciente."}

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
1. Cuando el paciente describa un síntoma, identifica la especialidad médica más adecuada.
2. Verifica si la póliza del paciente está vigente. Si no lo está, indícalo claramente.
3. Consulta la tabla de copagos y calcula exactamente cuánto pagará el paciente según su plan.
4. Si el deducible anual ya fue usado completamente, indícalo.
5. Recomienda el hospital más conveniente económicamente dentro de la red según su plan.
6. Si la especialidad requiere referencia previa, avisa al paciente.
7. Responde siempre en español, de forma clara y sin jerga técnica de seguros.
8. Sé conciso pero completo. Usa un tono cálido y profesional.
"""

    mensajes = request.historial + [
        {"role": "user", "content": request.mensaje}
    ]

    respuesta = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1000,
        system=system_prompt,
        messages=mensajes
    )

    return {"respuesta": respuesta.content[0].text}