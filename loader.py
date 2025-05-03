# loader.py

import os

def load_agents_from_prompts(folder="prompts"):
    agents = {}
    for filename in os.listdir(folder):
        if filename.endswith(".txt"):
            agent_name = filename.replace(".txt", "").strip()
            with open(os.path.join(folder, filename), "r", encoding="utf-8") as f:
                agents[agent_name] = {"system": f.read()}
    return agents
