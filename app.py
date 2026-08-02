import os
import tempfile
from gradio_client import Client, handle_file
import streamlit as st

st.set_page_config(page_title="UkeFlow AI Free", page_icon="🤖")

st.title("🤖 UkeFlow: Edición IA (Gratis)")
st.write(
    "Graba o sube tu ukelele, escribe lo que imaginas y deja que la IA"
    " produzca la canción de forma gratuita."
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
            "Enviando a la supercomputadora gratuita de Hugging Face..."
        ):
            try:
                # Guardamos el audio temporalmente para procesarlo
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".wav"
                ) as tmp:
                    tmp.write(audio_final.getvalue())
                    tmp_path = tmp.name

                # Conexión directa a MusicGen en Hugging Face
                client = Client("facebook/MusicGen")

                result = client.predict(
                    model="melody",
                    text_prompt=estilo,
                    audio_input=handle_file(tmp_path),
                    duration=8,
                    api_name="/predict",
                )

                # Limpieza del archivo temporal
                os.remove(tmp_path)

                # Obtenemos la ruta del audio generado
                audio_path = result[1] if isinstance(result, tuple) else result

                st.success("🎉 ¡Tu canción producida por IA está lista!")
                st.audio(audio_path)

            except Exception as e:
                st.error(
                    "El servidor gratuito puede estar congestionado en este"
                    f" momento. Intenta de nuevo en un par de segundos. Error: {e}"
                )
