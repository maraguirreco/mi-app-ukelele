import os
import tempfile
from gradio_client import Client, handle_file
import streamlit as st

st.set_page_config(page_title="UkeFlow AI Free", page_icon="🤖")

st.title("🤖 UkeFlow: Edición IA (Gratis)")
st.write(
    "Graba o sube tu ukelele, escribe lo que imaginas y deja que la IA"
    " produzca la canción gratis."
)
st.divider()

st.header("1. Captura tu ukelele")
tab1, tab2 = st.tabs(["🎤 Grabar con micrófono", "📁 Subir archivo de audio"])

audio_final = None

with tab1:
    audio_grabado = st.audio_input(
        "Toca tu ukelele (recomendado: 5 a 10 segundos):"
    )
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

    st.header("2. ¿Cómo quieres que suene?")
    estilo = st.text_area(
        "Describe la producción que imaginas:",
        value=(
            "Una canción indie pop alegre, con batería acústica, bajo profundo"
            " y sintetizadores de fondo, vibra de playa."
        ),
    )

    if st.button("✨ Transformar con IA (Servidor Gratis)"):
        with st.spinner(
            "Conectando con la supercomputadora de Hugging Face (esto toma unos"
            " segundos)..."
        ):
            try:
                # Guardamos el audio temporalmente
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".wav"
                ) as tmp:
                    tmp.write(audio_final.getvalue())
                    tmp_path = tmp.name

                # Conexión directa a MusicGen
                client = Client("facebook/MusicGen")

                # Dejamos que Gradio elija la ruta automáticamente sin api_name
                result = client.predict(
                    "melody",  # Tipo de modelo
                    estilo,  # Descripción en texto
                    handle_file(tmp_path),  # Audio de tu ukelele
                    8,  # Duración en segundos
                )

                # Limpieza del archivo temporal
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

                # Extraemos el archivo de audio de la respuesta
                if isinstance(result, (tuple, list)):
                    audio_path = result[1] if len(result) > 1 else result[0]
                else:
                    audio_path = result

                st.success("🎉 ¡Tu canción producida por IA está lista!")
                st.audio(audio_path)

            except Exception as e:
                st.error(f"Hubo un detalle al conectar con el servidor: {e}")
