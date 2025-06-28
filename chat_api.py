from flask import Flask, request, jsonify
import os
from together import Together

app = Flask(__name__)

os.environ["TOGETHER_API_KEY"] = "tgp_v1_PIjZvu20Ljfly1KpASmkyV3efe5Y0BuhPmX7JGg5gTQ"
client = Together(api_key=os.environ["TOGETHER_API_KEY"])

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    nombre_personaje = data.get('nombre_personaje', '')
    contexto = data.get('contexto', '')
    mensaje_usuario = data.get('mensaje_usuario', '')
    apodo_usuario = data.get('apodo_usuario', '')

    if not nombre_personaje or not contexto or not mensaje_usuario or not apodo_usuario:
        return jsonify({'error': 'Faltan datos'}), 400

    system_prompt = contexto
    prompt = f"<s>[INST] {system_prompt}\n{apodo_usuario}: {mensaje_usuario} [/INST] {nombre_personaje}:"

    respuesta = ""
    try:
        response = client.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            prompt=prompt,
            max_tokens=150,
            temperature=0.7,
            stop=["</s>", f"\n{apodo_usuario}:", f"{apodo_usuario}:", f"{nombre_personaje}:", "\n\n"],
            repetition_penalty=1.2
        )
        respuesta = response.choices[0].text.strip()
        respuesta = respuesta.split(f"{apodo_usuario}:")[0].split(f"{nombre_personaje}:")[0].strip()
        if not respuesta:
            respuesta = "Lo siento, la IA no pudo generar una respuesta en este momento."
    except Exception as e:
        respuesta = f"Lo siento, ocurrió un error al procesar tu solicitud. Error: {str(e)}"

    return jsonify({'respuesta': respuesta})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
