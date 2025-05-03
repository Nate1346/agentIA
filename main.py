from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
from loader import load_agents_from_prompts
from session_manager import load_session, save_session

# Charger les variables d'environnement
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# Charger les prompts des assistants
agents = load_agents_from_prompts()

# Session pour retenir l'agent actif
session = load_session()

class PromptRequest(BaseModel):
    input: str

# Détecte un routage dans la réponse (ex : [IA:Fox])
def detect_routing_tag(text):
    if "[IA:" in text:
        return text.split("[IA:")[1].split("]")[0].strip()
    return None

@app.post("/run")
async def run_agent(request: PromptRequest):
    user_input = request.input

    # Si un agent est déjà actif
    if session["active_agent"]:
        if "[RESET]" in user_input.upper():
            session["active_agent"] = None
        else:
            active = session["active_agent"]
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": agents[active]["system"]},
                    {"role": "user", "content": user_input}
                ]
            )
            return {"output": response.choices[0].message.content}

    # Sinon c'est F.R.I.D.A.Y. qui analyse
    friday_key = "F.R.I.D.A.Y."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": agents[friday_key]["system"]},
            {"role": "user", "content": user_input}
        ]
    )
    output = response.choices[0].message.content
    target = detect_routing_tag(output)

    if target and target in agents:
        session["active_agent"] = target
        save_session(session)
        delegated_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": agents[target]["system"]},
                {"role": "user", "content": user_input}
            ]
        )
        final_output = delegated_response.choices[0].message.content
    else:
        final_output = output

    return {"output": final_output.strip()}

@app.get("/start-day")
async def start_day():
    jarvis_key = "J.A.R.V.I.S."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": agents[jarvis_key]["system"]},
            {"role": "user", "content": "Lance la journée avec un focus et transfère si besoin."}
        ]
    )
    output = response.choices[0].message.content
    target = detect_routing_tag(output)

    if target and target in agents:
        session["active_agent"] = target
        delegated_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": agents[target]["system"]},
                {"role": "user", "content": "Rebondis sur l’initiative de J.A.R.V.I.S."}
            ]
        )
        final_output = delegated_response.choices[0].message.content
    else:
        final_output = output

    return {"output": final_output.strip()}
@app.post("/reset")

async def reset_agent():
    session["active_agent"] = None
    save_session(session)
    return {"message": "Session réinitialisée. Aucun agent actif."}