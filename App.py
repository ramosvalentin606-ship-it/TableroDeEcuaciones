import streamlit as st
import base64
from openai import OpenAI
from PIL import Image
import numpy as np
import sympy as sp
from streamlit_drawable_canvas import st_canvas
import io

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title='🧠 Tablero Matemático Inteligente',
    page_icon='🎨',
    layout="wide"
)

# ---------------- ESTILO ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #1f1c2c, #928dab);
    color: white;
}
.title {
    font-size: 42px;
    font-weight: bold;
    text-align: center;
}
.card {
    background-color: #2b2b2b;
    padding: 20px;
    border-radius: 15px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- UI ----------------
st.markdown('<div class="title">🧠 Tablero Matemático Inteligente</div>', unsafe_allow_html=True)
st.write("✍️ Dibuja una ecuación (ej: 2x + 3 = 7) y la resolveré automáticamente")

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("⚙️ Configuración")
    stroke_width = st.slider('Grosor', 1, 30, 5)
    api_key = st.text_input('API Key', type="password")

# ---------------- CANVAS ----------------
col1, col2, col3 = st.columns([1,2,1])

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)

    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=stroke_width,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=300,
        width=400,
        drawing_mode="freedraw",
        key="canvas",
    )

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- BOTÓN ----------------
if st.button("🔍 Analizar y resolver"):

    if canvas_result.image_data is None:
        st.warning("⚠️ Dibuja una ecuación primero")
    elif not api_key:
        st.warning("⚠️ Ingresa tu API Key")
    else:
        try:
            client = OpenAI(api_key=api_key)

            with st.spinner("🧠 Interpretando ecuación..."):

                # Convertir imagen
                img_array = np.array(canvas_result.image_data)
                image = Image.fromarray(img_array.astype('uint8'), 'RGBA')

                buffer = io.BytesIO()
                image.save(buffer, format="PNG")
                base64_image = base64.b64encode(buffer.getvalue()).decode()

                # Prompt optimizado
                prompt = """
                Extrae SOLO la ecuación matemática de la imagen.
                Usa formato Python (ej: 2*x + 3 = 7).
                No expliques nada.
                """

                # Llamada a OpenAI
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{base64_image}"
                                    },
                                },
                            ],
                        }
                    ],
                    max_tokens=200,
                )

                ecuacion = response.choices[0].message.content.strip()

                # Limpieza básica
                ecuacion = ecuacion.replace(" ", "")

                st.success(f"📘 Ecuación detectada: {ecuacion}")

                # Validación
                if "=" not in ecuacion:
                    st.error("❌ No se detectó una ecuación válida")
                else:
                    # ---------------- RESOLVER ----------------
                    x = sp.symbols('x')

                    lhs, rhs = ecuacion.split("=")

                    expr = sp.sympify(lhs) - sp.sympify(rhs)

                    solucion = sp.solve(expr, x)

                    # ---------------- RESULTADO ----------------
                    st.success(f"✅ Solución: x = {solucion}")

                    # ---------------- PASOS ----------------
                    st.subheader("📘 Paso a paso")

                    st.write("1️⃣ Pasamos todo a un lado:")
                    st.latex(sp.latex(expr))

                    st.write("2️⃣ Resolvemos la ecuación:")
                    if solucion:
                        st.latex(f"x = {solucion[0]}")
                    else:
                        st.write("No se encontró solución")

        except Exception as e:
            st.error(f"❌ Error: {e}")
