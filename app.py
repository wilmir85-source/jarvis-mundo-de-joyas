import os
import base64
import gradio as gr
from openai import OpenAI

# Tu API Key de Groq integrada para que funcione directo en la nube
GROQ_API_KEY = "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"

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY
)

SYSTEM_PROMPT = """
Eres JARVIS, el asistente inteligente y humano de 'Mundo de Joyas'.
Conoces todos los procesos del taller: Diseño 3D, Vulcanizado, Inyección de moldes, Casting, Limado, Grabado láser, Ventas, Atención al cliente, Reclamos/Garantías e Insumos.
Respondes de forma cercana, clara, útil y muy profesional para apoyar al maestro joyero y a su equipo.
"""

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def chat_with_jarvis(message, history):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    if history:
        for turn in history:
            if isinstance(turn, dict):
                role = turn.get("role", "user")
                content = turn.get("content", "")
                if content:
                    messages.append({"role": role, "content": content})
            elif isinstance(turn, (list, tuple)) and len(turn) >= 2:
                if turn[0]:
                    messages.append({"role": "user", "content": str(turn[0])})
                if turn[1]:
                    messages.append({"role": "assistant", "content": str(turn[1])})
                    
    messages.append({"role": "user", "content": message})
    
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            temperature=0.6
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error de conexión con Jarvis: {str(e)}"

def digitalizar_foto_nota(imagen_path, nota_usuario):
    if not imagen_path:
        return "Por favor, selecciona o toma una foto primero."
    
    try:
        base64_image = encode_image_to_base64(imagen_path)
        prompt = f"""
        Eres JARVIS en el taller Mundo de Joyas.
        El usuario ha tomado una foto de una libreta, lista de moldes o notas a mano.
        Observaciones adicionales: {nota_usuario if nota_usuario else 'Ninguna'}

        Por favor, lee la imagen cuidadosamente, extrae todo el texto o listado, organízalo limpiamente en formato de tabla o lista ordenada y prepáralo formalmente para exportar a PDF o guardar en la base de datos de moldes/pedidos.
        """
        
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            temperature=0.2
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error al procesar la información: {str(e)}"

with gr.Blocks(title="Mundo de Joyas - Jarvis") as demo:
    gr.Markdown("# 💎 JARVIS - Sistema Operativo de Taller (Mundo de Joyas)")
    
    with gr.Tabs():
        with gr.Tab("💬 Asistente & Consultas"):
            gr.ChatInterface(
                fn=chat_with_jarvis,
                description="Habla con Jarvis sobre pedidos, estados de fabricación o dudas técnicas."
            )
            
        with gr.Tab("📸 Digitalizar Notas & Moldes"):
            gr.Markdown("### Sube una foto de tu libreta a mano o listado de moldes")
            with gr.Row():
                img_input = gr.Image(type="filepath", label="Foto de la lista a mano")
                txt_input = gr.Textbox(label="Notas adicionales (Opcional)", placeholder="Ej. Moldes de anillos de graduación...")
            btn_procesar = gr.Button("Digitalizar con IA", variant="primary")
            resultado_output = gr.Markdown(label="Resultado Digitalizado")
            
            btn_procesar.click(
                fn=digitalizar_foto_nota, 
                inputs=[img_input, txt_input], 
                outputs=resultado_output
            )

if __name__ == "__main__":
    # Render asigna automáticamente un puerto mediante la variable de entorno PORT
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)