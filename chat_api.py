from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

TOGETHER_API_KEY = "tgp_v1_PIjZvu20Ljfly1KpASmkyV3efe5Y0BuhPmX7JGg5gTQ"

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    nombre_personaje = data.get('nombre_personaje', '')
    contexto = data.get('contexto', '')
    mensaje_usuario = data.get('mensaje_usuario', '')
    apodo_usuario = data.get('apodo_usuario', '')

    if not nombre_personaje or not contexto or not mensaje_usuario or not apodo_usuario:
        return jsonify({'error': 'Faltan datos'}), 400

    # Construir el prompt como lo haces en tu PHP
    system_prompt = f"Eres {nombre_personaje}. {contexto} Responde siempre como si fueras {nombre_personaje}, usando su personalidad y forma de hablar. El usuario se llama {apodo_usuario}, refiérete a él por su apodo. No digas que eres un asistente, eres el personaje."
    
    prompt = f"{system_prompt}\n\n{apodo_usuario}: {mensaje_usuario}\n\n{nombre_personaje}:"

    try:
        # Usar la API REST directa (como en tu prueba)
        url = "https://api.together.xyz/v1/completions"
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "mistralai/Mistral-7B-Instruct-v0.1",
            "prompt": prompt,
            "max_tokens": 150,
            "temperature": 0.7,
            "stop": [f"\n{apodo_usuario}:", f"{nombre_personaje}:"],
            "repetition_penalty": 1.2
        }

        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            respuesta = result['choices'][0]['text'].strip()
            
            # Limpiar la respuesta
            if respuesta:
                respuesta = respuesta.split(f"{apodo_usuario}:")[0].split(f"{nombre_personaje}:")[0].strip()
            else:
                respuesta = "Lo siento, no pude generar una respuesta en este momento."
        else:
            respuesta = f"Error en la API: {response.status_code}"

    except Exception as e:
        respuesta = "Lo siento, ocurrió un error al procesar tu solicitud."

    return jsonify({'respuesta': respuesta})

@app.route('/healthz', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
