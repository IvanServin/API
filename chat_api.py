from flask import Flask, request, jsonify
import requests
import os
import textwrap

app = Flask(__name__)

TOGETHER_API_KEY = "tgp_v1_PIjZvu20Ljfly1KpASmkyV3efe5Y0BuhPmX7JGg5gTQ"

def construir_prompt_avanzado(nombre_personaje, contexto, mensaje_usuario, apodo_usuario):
    """
    Construye un prompt optimizado que utiliza el contexto estructurado
    que ahora incluye campos avanzados
    """
    # El contexto ya viene estructurado desde api_cht.php, pero podemos mejorarlo
    # para el formato Mistral
    
    # Si el contexto ya está muy estructurado, lo usamos directamente
    if "PERSONALIDAD:" in contexto and "REGLAS:" in contexto:
        # El contexto ya está bien estructurado, solo formateamos para Mistral
        prompt = f"""<s>[INST] Eres {nombre_personaje}. Responde SIEMPRE manteniendo el personaje.

{contexto}

Instrucción actual: Responde al siguiente mensaje manteniendo perfectamente el personaje de {nombre_personaje}.

{apodo_usuario}: {mensaje_usuario} [/INST] {nombre_personaje}:"""
    else:
        # Contexto básico - formato tradicional
        prompt = f"<s>[INST] {contexto}\n{apodo_usuario}: {mensaje_usuario} [/INST] {nombre_personaje}:"
    
    return prompt

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    nombre_personaje = data.get('nombre_personaje', '')
    contexto = data.get('contexto', '')
    mensaje_usuario = data.get('mensaje_usuario', '')
    apodo_usuario = data.get('apodo_usuario', '')

    if not nombre_personaje or not contexto or not mensaje_usuario or not apodo_usuario:
        return jsonify({'error': 'Faltan datos'}), 400

    # Construir prompt optimizado
    prompt = construir_prompt_avanzado(nombre_personaje, contexto, mensaje_usuario, apodo_usuario)

    respuesta = ""
    try:
        url = "https://api.together.xyz/v1/completions"
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "prompt": prompt,
            "max_tokens": 200,  # Aumentado ligeramente para respuestas más completas
            "temperature": 0.75,  # Un poco más de creatividad
            "stop": ["</s>", f"\n{apodo_usuario}:", f"{apodo_usuario}:", f"{nombre_personaje}:", "\n\n"],
            "repetition_penalty": 1.3,  # Un poco más alto para evitar repeticiones
            "top_p": 0.9,
            "top_k": 40
        }

        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                respuesta = result['choices'][0]['text'].strip()
                
                # Limpiar la respuesta más agresivamente
                respuesta = respuesta.split(f"{apodo_usuario}:")[0].split(f"{nombre_personaje}:")[0].strip()
                
                # Remover posibles artefactos del formato
                respuesta = respuesta.replace('[/INST]', '').replace('[INST]', '').strip()
                
                if not respuesta:
                    respuesta = "..."  # Respuesta más natural para personajes
            else:
                respuesta = "No se pudo generar una respuesta en este momento."
        else:
            print(f"Error en API Together: {response.status_code} - {response.text}")
            respuesta = "Lo siento, ocurrió un error al procesar tu solicitud."

    except requests.exceptions.Timeout:
        respuesta = "La solicitud tardó demasiado tiempo. Por favor, intenta nuevamente."
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")
        respuesta = "Error de conexión. Por favor, verifica tu internet e intenta nuevamente."
    except Exception as e:
        print(f"Error inesperado: {e}")
        respuesta = "Lo siento, ocurrió un error inesperado."

    return jsonify({'respuesta': respuesta})

@app.route('/healthz', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy', 
        'service': 'Chat API',
        'version': '2.0'
    })

# Endpoint para verificar el formato del prompt (útil para debugging)
@app.route('/api/debug-prompt', methods=['POST'])
def debug_prompt():
    data = request.get_json()
    nombre_personaje = data.get('nombre_personaje', '')
    contexto = data.get('contexto', '')
    mensaje_usuario = data.get('mensaje_usuario', '')
    apodo_usuario = data.get('apodo_usuario', '')
    
    prompt = construir_prompt_avanzado(nombre_personaje, contexto, mensaje_usuario, apodo_usuario)
    
    return jsonify({
        'prompt_generado': prompt,
        'longitud': len(prompt),
        'tiene_campos_avanzados': "PERSONALIDAD:" in contexto
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
