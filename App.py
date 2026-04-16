import streamlit as st
import base64
from openai import OpenAI
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title='🧠 Tablero Inteligente',
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
st.markdown('<div class="title">🧠 Tablero Inteligente con IA</div>', unsafe_allow_html=True)
st.write("Dibuja algo y deja que la IA lo interprete ✨")

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("⚙️ Configuración")
    stroke_width = st.slider('Grosor', 1, 30, 5)
    api_key = st.text_input('API Key', type="password")

# ---------------- FUNCIÓN ----------------
def encode_image(image):
    return base64.b64encode(image).decode()

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
if st.button("🔍 Analizar dibujo"):

    if canvas_result.image_data is None:
        st.warning("⚠️ Dibuja algo primero")
    elif not api_key:
        st.warning("⚠️ Ingresa tu API Key")
    else:
        try:
            client = OpenAI(api_key=api_key)

            with st.spinner("🧠 Analizando imagen..."):

                # Convertir imagen del canvas
                img_array = np.array(canvas_result.image_data)
                image = Image.fromarray(img_array.astype('uint8'), 'RGBA')

                # Guardar en memoria (sin archivo)
                import io
                buffer = io.BytesIO()
                image.save(buffer, format="PNG")
                base64_image = encode_image(buffer.getvalue())

                # Prompt
                prompt = "Describe en español brevemente lo que ves en la imagen."

                # Llamada a la API (FORMA CORRECTA)
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
                    max_tokens=300,
                )

                resultado = response.choices[0].message.content

                # Mostrar resultado
                st.success("✅ Resultado:")
                st.markdown(f"### 🧾 {resultado}")

        except Exception as e:
            st.error(f"❌ Error: {e}")
