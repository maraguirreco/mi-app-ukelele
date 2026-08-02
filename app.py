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
            "Conectando con la supercomputadora de Hugging Face (esto puede"
            " tomar 30-60 segundos)..."
        ):
            try:
                # Guardar el audio temporalmente
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".wav"
                ) as tmp:
                    tmp.write(audio_final.getvalue())
                    tmp_path = tmp.name

                # Conexión al modelo de producción musical
                client = Client("facebook/MusicGen")

                result = client.predict(
                    "melody",  # Modelo con melodía
                    estilo,  # Instrucción en texto
                    handle_file(tmp_path),  # Audio de tu ukelele
                    8,  # Duración del demo
                )

                # Limpieza del archivo temporal de entrada
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

                # Procesamiento ultra-seguro de la respuesta
                audio_path = None

                if isinstance(result, (list, tuple)):
                    # Buscamos el archivo de audio generado
                    for item in result:
                        if isinstance(item, str) and (
                            item.endswith(".wav")
                            or item.endswith(".mp3")
                            or item.endswith(".flac")
                        ):
                            audio_path = item
                            break
                    if not audio_path and len(result) > 0:
                        audio_path = result[-1]
                elif isinstance(result, str):
                    audio_path = result

                # Verificación final
                if audio_path and os.path.exists(str(audio_path)):
                    st.success("🎉 ¡Tu canción producida por IA está lista!")
                    st.audio(audio_path)
                else:
                    st.warning(
                        "⚠️ El servidor gratuito está despertando o muy"
                        " ocupado en este momento. Por favor presiona el botón"
                        " de nuevo en 5 segundos."
                    )

            except Exception as e:
                st.error(
                    "El servidor está saturado. Intenta presionar el botón de"
                    f" nuevo. Detalle: {e}"
                )
