
import json
import urllib.request

# Simulated readings - NOT real sensor data
plant_data = {
    "soil_raw": 2500,
    "temperature_c": 26.5,
    "humidity_percent": 55,
    "soil_state": "DRY",
    "light_state": "UNKNOWN"
}


def interpret_plant_state(data):
    observations = []

    if data["soil_state"] == "DRY":
        observations.append(
            "My soil is dry, so I need water."
        )
    elif data["soil_state"] == "WET":
        observations.append(
            "My soil is moist."
        )
    else:
        observations.append(
            "My soil moisture condition is unknown."
        )

    if data["light_state"] == "UNKNOWN":
        observations.append(
            "I cannot determine my light condition."
        )

    observations.append(
        f"The temperature is {data['temperature_c']} degrees Celsius."
    )

    return " ".join(observations)


plant_summary = interpret_plant_state(plant_data)

question = "How are you feeling today?"

prompt = f"""
You are Leafy, a friendly plant robot.

FACTS ABOUT YOUR CURRENT CONDITION:
{plant_summary}

USER QUESTION:
{question}

IMPORTANT:
- Answer based on the facts above.
- If soil is dry, say you are thirsty.
- Do not say you feel good if your soil is dry.
- Do not invent missing sensor information.
- Speak in first person.
- Respond in English.
- Maximum 2 short sentences.

LEAFY:
"""

payload = {
    "model": "leafy",
    "prompt": prompt,
    "stream": False,
    "options": {
        "temperature": 0.1,
        "num_predict": 60
    }
}

request = urllib.request.Request(
    "http://127.0.0.1:11434/api/generate",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST"
)

with urllib.request.urlopen(request, timeout=120) as response:
    result = json.load(response)

print("Plant summary:", plant_summary)
print("Leafy:", result["response"].strip())
