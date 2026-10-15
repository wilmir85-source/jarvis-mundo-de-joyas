import os
import base64
import json
import gradio as gr
from openai import OpenAI

# Tu API Key de Groq integrada
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

DATA_FILE = "pedidos_taller.json"

def cargar_pedidos():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def guardar_pedidos(pedidos):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(pedidos, f, ensure_ascii=False, indent=4)

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
            model="openai/gpt-oss-120b",
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
        El usuario ha tomado una foto de una libreta, lista de moldes o notas a mano (como la nota de Joyería Yeshua para Jose Vacama).
        Observaciones adicionales del usuario: {nota_usuario if nota_usuario else 'Ninguna'}

        Por favor, analiza la imagen detalladamente, extrae todo el texto, nombres de clientes, medidas, tipos de piedra o procesos descritos a mano, y preséntalos organizados en un formato limpio de orden de trabajo o lista para el taller.
        """
        
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
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
        return f"⚠️ Error al procesar la imagen: {str(e)}"

def agregar_nuevo_pedido(cliente, descripcion, departamento):
    if not cliente or not descripcion:
        return "⚠️ Por favor, completa el nombre del cliente y la descripción.", actualizar_tabla()
    
    pedidos = cargar_pedidos()
    nuevo = {
        "Cliente": cliente,
        "Descripción": descripcion,
        "Departamento": departamento,
        "Estado": "En Proceso"
    }
    pedidos.append(nuevo)
    guardar_pedidos(pedidos)
    return f"✨ ¡Pedido registrado con éxito para {cliente}!", actualizar_tabla()

def actualizar_tabla():
    pedidos = cargar_pedidos()
    if not pedidos:
        return []
    return [[p["Cliente"], p["Descripción"], p["Departamento"], p["Estado"]] for p in pedidos]

custom_css = """
body { background-color: #0b0f19 !important; }
.gradio-container { max-width: 100% !important; padding: 10px !important; }
h1, h2, h3 { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
"""

ios_meta_head = """
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Mundo de Joyas">
"""

with gr.Blocks(
    title="Mundo de Joyas - JARVIS", 
    theme=gr.themes.Soft(
        primary_hue="amber", 
        secondary_hue="slate",
        neutral_hue="slate"
    ),
    css=custom_css,
    head=ios_meta_head
) as demo:
    
    with gr.Row(elem_id="header-row"):
        gr.Markdown("# 💎 MUNDO DE JOYAS — *JARVIS OS*")
    
    with gr.Tabs():
        with gr.Tab("💬 Chat IA"):
            gr.Markdown("### Tu asistente experto en alta joyería y procesos de taller")
            gr.ChatInterface(
                fn=chat_with_jarvis,
                description="Pregunta lo que necesites sobre diseño 3D, aleaciones, casting o logística."
            )
            
        with gr.Tab("📋 Pedidos"):
            gr.Markdown("### ⚙️ Control y Seguimiento de Producción")
            with gr.Row():
                with gr.Column(scale=1):
                    txt_cliente = gr.Textbox(label="👤 Nombre del Cliente", placeholder="Ej. Juan Pérez")
                    txt_desc = gr.Textbox(label="💍 Descripción de la Joya", placeholder="Ej. Anillo de graduación Oro 14k")
                    dd_depto = gr.Dropdown(
                        choices=[
                            "1. Diseño 3D", 
                            "2. Impresión / Inyección", 
                            "3. Casting (Fundición)", 
                            "4. Limado / Armado", 
                            "5. Acabado y Láser", 
                            "6. Entregado"
                        ], 
                        label="📍 Departamento Actual",
                        value="1. Diseño 3D"
                    )
                    btn_add = gr.Button("✨ Registrar Nuevo Pedido", variant="primary", size="lg")
                    lbl_status = gr.Markdown()
                    
            with gr.Row():
                gr.Markdown("### 📊 Estado Actual en el Taller")
            with gr.Row():
                tabla_pedidos = gr.Dataframe(
                    headers=["Cliente", "Descripción", "Departamento", "Estado"],
                    value=actualizar_tabla(),
                    interactive=False,
                    wrap=True
                )
            
            btn_add.click(
                fn=agregar_nuevo_pedido,
                inputs=[txt_cliente, txt_desc, dd_depto],
                outputs=[lbl_status, tabla_pedidos]
            )
            
        with gr.Tab("📸 Escanear"):
            gr.Markdown("### 📷 Digitalizador de Notas y Libretas a Mano")
            with gr.Row():
                img_input = gr.Image(type="filepath", label="Toma o sube una foto de tu libreta")
            with gr.Row():
                txt_input = gr.Textbox(label="Notas o instrucciones adicionales (Opcional)", placeholder="Ej. Priorizar moldes de la fila 3...")
            with gr.Row():
                btn_procesar = gr.Button("🚀 Procesar y Extraer con IA", variant="primary", size="lg")
            with gr.Row():
                resultado_output = gr.Markdown(label="Resultado Organizado")
            
            btn_procesar.click(
                fn=digitalizar_foto_nota, 
                inputs=[img_input, txt_input], 
                outputs=resultado_output
            )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
