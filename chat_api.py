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

    # FORMATO ORIGINAL QUE FUNCIONABA BIEN
    system_prompt = contexto
    prompt = f"<s>[INST] {system_prompt}\n{apodo_usuario}: {mensaje_usuario} [/INST] {nombre_personaje}:"

    respuesta = ""
    try:
        url = "https://api.together.xyz/v1/completions"
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",  # MODELO ORIGINAL
            "prompt": prompt,
            "max_tokens": 150,
            "temperature": 0.7,
            "stop": ["</s>", f"\n{apodo_usuario}:", f"{apodo_usuario}:", f"{nombre_personaje}:", "\n\n"],  # STOPS ORIGINALES
            "repetition_penalty": 1.2
        }

        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            respuesta = result['choices'][0]['text'].strip()
            respuesta = respuesta.split(f"{apodo_usuario}:")[0].split(f"{nombre_personaje}:")[0].strip()
            
            if not respuesta:
                respuesta = "Lo siento, la IA no pudo generar una respuesta en este momento."
        else:
            respuesta = "Lo siento, ocurrió un error al procesar tu solicitud."

    except Exception as e:
        respuesta = "Lo siento, ocurrió un error al procesar tu solicitud."

    return jsonify({'respuesta': respuesta})

@app.route('/healthz', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
