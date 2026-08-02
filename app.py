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

# Paso 1: Captura
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

    st.header("2. ¿Cómo quieres que suene?")
    estilo = st.text_area(
        "Describe la producción que imaginas:",
        value=(
            "Una canción indie pop alegre, con batería acústica, bajo profundo"
            " y sintetizadores de fondo, vibra de playa."
        ),
    )

    if st.button("✨ Transformar con IA"):
        with st.spinner("Procesando tu producción musical con la IA..."):
            try:
                # Guardamos el audio temporalmente
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".wav"
                ) as tmp:
                    tmp.write(audio_final.getvalue())
                    tmp_path = tmp.name

                # Revisar si existe el token prioritario gratuito en Secrets
                hf_token = st.secrets.get("HF_TOKEN", None)

                # Conexión pasándole el token para no ser expulsado de la fila
                client = Client("facebook/MusicGen", hf_token=hf_token)

                result = client.predict(
                    "melody",
                    estilo,
                    handle_file(tmp_path),
                    8,
                )

                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

                # Extracción del audio resultante
                audio_path = None
                if isinstance(result, (list, tuple)) and len(result) > 0:
                    for item in result:
                        if isinstance(item, str) and item.endswith(
                            (".wav", ".mp3", ".flac")
                        ):
                            audio_path = item
                            break
                    if not audio_path:
                        audio_path = result[-1]
                elif isinstance(result, str):
                    audio_path = result

                if (
                    audio_path
                    and isinstance(audio_path, str)
                    and os.path.exists(audio_path)
                ):
                    st.success("🎉 ¡Tu canción producida por IA está lista!")
                    st.audio(audio_path)
                else:
                    st.warning(
                        "⚠️ La cola estuvo muy llena. Si no has agregado el"
                        " HF_TOKEN en Secrets, agrégalo para tener prioridad."
                    )

            except Exception as e:
                st.error(
                    f"Error de conexión: {e}. Intenta presionar el botón de"
                    " nuevo."
                )
