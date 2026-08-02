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

# Cargar automáticamente el token desde Secrets si existe
if "HF_TOKEN" in st.secrets:
    os.environ["HF_TOKEN"] = st.secrets["HF_TOKEN"]

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
        status_box = st.empty()
        status_box.info("⏳ Preparando tu audio...")

        # Guardamos el audio temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_final.getvalue())
            tmp_path = tmp.name

        # Lista de servidores gratuitos a los que intentaremos conectarnos
        servidores = [
            "facebook/MusicGen",
            "reach-vb/musicgen-melody",
            "mrfakename/MusicGen-Melody",
        ]

        audio_generado = None

        # Intentar en cada servidor de la lista hasta que uno funcione
        for servidor in servidores:
            try:
                status_box.info(
                    f"🛰️ Conectando con el servidor `{servidor}`..."
                )
                client = Client(servidor)

                result = client.predict(
                    "melody",
                    estilo,
                    handle_file(tmp_path),
                    8,
                )

                # Extraer respuesta de forma segura
                if result:
                    if isinstance(result, (list, tuple)) and len(result) > 0:
                        for item in result:
                            if isinstance(item, str) and item.endswith(
                                (".wav", ".mp3", ".flac", ".ogg")
                            ):
                                audio_generado = item
                                break
                        if not audio_generado and isinstance(result[-1], str):
                            audio_generado = result[-1]
                    elif isinstance(result, str):
                        audio_generado = result

                # Si logramos obtener un archivo real, salimos del bucle
                if audio_generado and os.path.exists(str(audio_generado)):
                    status_box.empty()
                    break

            except Exception:
                # Si falla o está saturado este servidor, pasa al siguiente
                continue

        # Limpieza del archivo de entrada
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

        # Mostrar resultado final
        if audio_generado and os.path.exists(str(audio_generado)):
            st.success("🎉 ¡Tu canción producida por IA está lista!")
            st.audio(audio_generado)
        else:
            status_box.empty()
            st.error(
                "⚠️ Todos los servidores gratuitos están congestionados en este"
                " instante. Espera unos 30 segundos y vuelve a presionar el"
                " botón."
            )
