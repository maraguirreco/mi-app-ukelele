import os
import tempfile
from gradio_client import Client, handle_file
import streamlit as st

st.set_page_config(page_title="UkeFlow AI Free", page_icon="🤖")

st.title("🤖 UkeFlow: Edición IA (Gratis)")
st.write(
    "Graba o sube tu ukelele, escribe lo que imaginas y deja que la IA"
    " produzca la canción."
)
st.divider()

# Paso 1: Captura de Audio
st.header("1. Captura tu ukelele")
tab1, tab2 = st.tabs(["🎤 Grabar con micrófono", "📁 Subir archivo de audio"])

audio_final = None

with tab1:
    audio_grabado = st.audio_input("Toca tu ukelele (5 a 10 segundos):")
    if audio_grabado:
        audio_final = audio_grabado

with tab2:
    audio_subido = st.file_uploader(
        "Selecciona un audio desde tu dispositivo:",
        type=["wav", "mp3", "m4a", "ogg"],
    )
    if audio_subido:
        audio_final = audio_subido

if audio_final:
    st.success("¡Audio listo!")
    st.audio(audio_final)

    # Paso 2: Instrucción de Estilo
    st.header("2. ¿Cómo quieres que suene?")
    estilo = st.text_area(
        "Describe la producción que imaginas:",
        value=(
            "Una canción indie pop alegre, con batería acústica, bajo profundo"
            " y sintetizadores de fondo, vibra de playa."
        ),
    )

    # Paso 3: Generación con IA
    if st.button("✨ Transformar con IA"):
        with st.spinner(
            "Usando tu cuota gratuita de ZeroGPU en Hugging Face..."
        ):
            try:
                # Guardamos el archivo de audio recibido temporalmente
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".wav"
                ) as tmp:
                    tmp.write(audio_final.getvalue())
                    tmp_path = tmp.name

                # Obtenemos el token desde Secrets
                hf_token = st.secrets.get("HF_TOKEN", None)

                # Conexión autenticada con el parámetro 'token' correcto
                if hf_token:
                    client = Client("facebook/MusicGen", token=hf_token)
                else:
                    client = Client("facebook/MusicGen")

                # Petición a la supercomputadora
                result = client.predict(
                    "melody",  # Modelo con melodía de referencia
                    estilo,  # Prompt de texto
                    handle_file(tmp_path),  # Tu ukelele
                    8,  # Duración en segundos
                )

                # Borramos el archivo temporal
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

                # Extracción segura de la ruta del audio generado
                audio_path = None
                if isinstance(result, (list, tuple)) and len(result) > 0:
                    for item in result:
                        if isinstance(item, str) and item.endswith(
                            (".wav", ".mp3", ".flac", ".ogg")
                        ):
                            audio_path = item
                            break
                    if not audio_path:
                        audio_path = result[-1]
                elif isinstance(result, str):
                    audio_path = result

                # Mostrar el audio resultante
                if (
                    audio_path
                    and isinstance(audio_path, str)
                    and os.path.exists(audio_path)
                ):
                    st.success("🎉 ¡Tu canción producida por IA está lista!")
                    st.audio(audio_path)
                else:
                    st.warning(
                        "⚠️ El servidor estuvo saturado un segundo. Presiona"
                        " el botón nuevamente."
                    )

            except Exception as e:
                st.error(f"Ocurrió un detalle: {e}")
