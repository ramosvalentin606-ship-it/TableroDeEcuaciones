import os
import streamlit as st
import base64
import openai
from openai import OpenAI
from PIL import Image
import numpy as np
import sympy as sp
from streamlit_drawable_canvas import st_canvas

# ---------------- CONFIG ----------------
st.set_page_config(page_title="🧠 Tablero Matemático", layout="wide")

st.title("🧠 Tablero Matemático Inteligente")
st.write("Dibuja una ecuación simple (ej: 2x + 3 = 7)")

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("⚙️ Configuración")
    stroke_width = st.slider("Grosor", 1, 20, 5)
    api_key = st.text_input("API Key", type="password")

# ---------------- CANVAS ----------------
canvas_result = st_canvas(
    stroke_width=stroke_width,
    stroke_color="#000000",
    background_color="#FFFFFF",
    height=300,
    width=500,
    drawing_mode="freedraw",
    key="math_canvas",
)

# ---------------- BOTÓN ----------------
if st.button("🔍 Resolver"):

    if canvas_result.image_data is None:
        st.warning("Dibuja una ecuación primero")
    elif not api_key:
        st.warning("Ingresa tu API key")
    else:
        os.environ['OPENAI_API_KEY'] = api_key

        with st.spinner("🧠 Interpretando ecuación..."):
            try:
                # Convertir imagen
                img_array = np.array(canvas_result.image_data)
                image = Image.fromarray(img_array.astype('uint8'), 'RGBA')
                image.save("eq.png")

                # Base64
                with open("eq.png", "rb") as f:
                    base64_image = base64.b64encode(f.read()).decode()

                # Prompt mejorado
                prompt = """
                Extrae SOLO la ecuación matemática de la imagen.
                Ejemplo salida: 2*x + 3 = 7
                No expliques nada.
                """

                response = openai.chat.completions.create(
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
                )

                ecuacion = response.choices[0].message.content.strip()

                st.success(f"📘 Ecuación detectada: {ecuacion}")

                # ---------------- RESOLVER ----------------
                x = sp.symbols('x')
                lhs, rhs = ecuacion.split("=")

                solucion = sp.solve(sp.sympify(lhs) - sp.sympify(rhs), x)

                st.success(f"✅ Solución: x = {solucion}")

            except Exception as e:
                st.error(f"❌ Error: {e}")
