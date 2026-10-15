import os
import json
import gradio as gr
from openai import OpenAI

# Tu API Key de Groq integrada
GROQ_API_KEY = "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"

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY
)

# Personalidad renovada: Cálida, experta, de confianza y directo al grano
SYSTEM_PROMPT = """
Eres JARVIS, el compa y asistente personal en 'Mundo de Joyas'. Estás en la jugada con todo lo relacionado al taller: desde diseño 3D en Rhino, impresión de resina, vulcanizado, inyección, casting, hasta el refinado de metales y acabados con láser o platino.
Hablas de forma natural, relajada pero ultra profesional, cercana y con calidez humana. Nada de respuestas robóticas o frías; tratas al maestro joyero de cuate a cuate, con confianza, claridad y siempre tirando buena vibra para sacar la chamba adelante sin enredos.
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
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Puchica, se me cayó tantito la conexión con el servidor: {str(e)}. Inténtalo de nuevo en un segundo, compa."

def procesar_texto_nota(texto_nota):
    if not texto_nota:
        return "¡Ey! Escribe o pega los datos de la nota para pasártelos limpios y organizados."
    
    try:
        prompt_texto = f"""
        [ORGANIZADOR DE NOTAS DE TALLER - MUNDO DE JOYAS]
        El jefe me pasó estos apuntes rápidos de la libreta:
        "{texto_nota}"
        
        Organízalos como una orden de trabajo de alta joyería de forma impecable y con buena energía:
        - Joyería o Cliente principal
        - Cliente Final
        - Descripción exacta de la pieza
        - Talla / Medida
        - Medidas de piedra
        - Servicio a realizar
        """
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt_texto}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Rayos, algo falló al procesar: {str(e)}"

def agregar_nuevo_pedido(cliente, descripcion, departamento):
    if not cliente or not descripcion:
        return "⚠️ Échale un ojo: faltó poner el nombre del cliente o la descripción de la joya.", actualizar_tabla()
    
    pedidos = cargar_pedidos()
    nuevo = {
        "Cliente": cliente,
        "Descripción": descripcion,
        "Departamento": departamento,
        "Estado": "En Proceso"
    }
    pedidos.append(nuevo)
    guardar_pedidos(pedidos)
    return f"¡Listo, mi estimado! Pedido registrado con éxito para {cliente}.", actualizar_tabla()

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
            gr.Markdown("### Tu compa experto en alta joyería y taller")
            gr.ChatInterface(
                fn=chat_with_jarvis,
                description="Pregúntame lo que necesites de diseño, aleaciones o chequemos la jugada del taller."
            )
            
        with gr.Tab("📋 Pedidos"):
            gr.Markdown("### ⚙️ Producción al Día")
            with gr.Row():
                with gr.Column(scale=1):
                    txt_cliente = gr.Textbox(label="👤 Cliente", placeholder="Ej. Joyería Yeshua")
                    txt_desc = gr.Textbox(label="💍 Joya", placeholder="Ej. Anillo con piedra 7x9")
                    dd_depto = gr.Dropdown(
                        choices=[
                            "1. Diseño 3D", 
                            "2. Impresión / Inyección", 
                            "3. Casting (Fundición)", 
                            "4. Limado / Armado", 
                            "5. Acabado y Láser", 
                            "6. Entregado"
                        ], 
                        label="📍 Departamento",
                        value="1. Diseño 3D"
                    )
                    btn_add = gr.Button("✨ Guardar Pedido", variant="primary", size="lg")
                    lbl_status = gr.Markdown()
                    
            with gr.Row():
                gr.Markdown("### 📊 Trabajos en Marcha")
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
            
        with gr.Tab("📝 Notas Rápidas"):
            gr.Markdown("### 📋 Traductor de Apuntes a Orden Formal")
            gr.Markdown("Escribe lo que anotaste a la carrera en la libreta (ej. *Jose Vacama, anillo, #7 1/2, piedra 7x9*) y te lo armo al chilazo.")
            with gr.Row():
                txt_nota_input = gr.Textbox(label="Apunte de la libreta", lines=4, placeholder="Pega o escribe tu nota aquí...")
            with gr.Row():
                btn_procesar_texto = gr.Button("🚀 Darle Formato", variant="primary", size="lg")
            with gr.Row():
                resultado_texto_output = gr.Markdown(label="Orden Lista")
            
            btn_procesar_texto.click(
                fn=procesar_texto_nota, 
                inputs=[txt_nota_input], 
                outputs=resultado_texto_output
            )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
