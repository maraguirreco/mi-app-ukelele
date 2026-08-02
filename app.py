import os
import replicate
import streamlit as st

# Configuración de página
st.set_page_config(page_title="UkeFlow AI", page_icon="🤖")

st.title("🤖 UkeFlow: Edición IA")
st.write(
    "Graba tu ukelele o sube un archivo de audio, escribe lo que imaginas y"
    " deja que la IA produzca la canción."
)
st.divider()

# Verificar que la llave de la API esté configurada
if "REPLICATE_API_TOKEN" not in st.secrets:
    st.error("⚠️ Falta configurar la llave secreta de Replicate en Streamlit.")
    st.stop()
else:
    os.environ["REPLICATE_API_TOKEN"] = st.secrets["REPLICATE_API_TOKEN"]

# Paso 1: Captura de Audio (Dos opciones con pestañas)
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
        "Selecciona un audio desde tu dispositivo (WAV, MP3, M4A, Ogg):",
        type=["wav", "mp3", "m4a", "ogg", "flac"],
    )
    if audio_subido:
        audio_final = audio_subido

# Si la app detecta un audio (sea grabado o subido), continúa la producción
if audio_final:
    st.success("¡Audio listo para el estudio!")
    st.audio(audio_final)

    # Paso 2: El Prompt (La instrucción)
    st.header("2. ¿Cómo quieres que suene?")
    estilo = st.text_area(
        "Describe la producción que imaginas:",
        value=(
            "Una canción indie pop alegre, con batería acústica, bajo profundo"
            " y sintetizadores de fondo, vibra de playa."
        ),
    )

    # Paso 3: Magia IA
    if st.button("✨ Transformar con IA"):
        with st.spinner(
            "La Inteligencia Artificial está en el estudio componiendo (esto"
            " puede tardar 1 o 2 minutos)..."
        ):
            try:
                # Se envía el audio (grabado o subido) al modelo MusicGen-Melody de Meta
                output = replicate.run(
                    "meta/musicgen-melody:7a76a8258b23fae65c5a22debb8841d1d7e816b75c2f24218cd2bd8573787906",
                    input={
                        "prompt": estilo,
                        "melody": audio_final,  # Pasa el audio seleccionado
                        "duration": 8,  # Duración del audio generado en segundos
                        "temperature": 1.05,
                    },
                )

                st.success("🎉 ¡Tu canción producida por IA está lista!")
                st.audio(output)

            except Exception as e:
                st.error(f"Ups, ocurrió un error en el estudio: {e}")
