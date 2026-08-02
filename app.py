import io
import librosa
import numpy as np
import streamlit as st

st.set_page_config(page_title="UkeFlow", page_icon="🎸")

st.title("🎸 UkeFlow: De la Idea al Demo")
st.write("Tu intuición musical, convertida en canción. Sin complicaciones.")

st.divider()

# Paso 1: Grabación
st.header("Paso 1: Captura la inspiración")
st.write("Toma tu ukelele. Toca ese rasgueo o melodía que tienes en la mente.")

audio_grabado = st.audio_input("Toca para grabar:")

if audio_grabado:
    st.success("¡Audio capturado!")
    st.audio(audio_grabado)

    # Botón para activar la magia de Librosa
    if st.button("🔍 Analizar el ritmo de mi ukelele"):
        with st.spinner("Escuchando tu ukelele y contando los tiempos..."):
            # Convertimos el audio para que Librosa lo entienda
            audio_bytes = audio_grabado.getvalue()
            audio_file = io.BytesIO(audio_bytes)

            # Cargar el sonido
            y, sr = librosa.load(audio_file, sr=None)

            # Calcular los Beats Per Minute (BPM)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            bpm_estimado = int(np.round(tempo))

            st.divider()

            # Paso 2: Resultados intuitivos
            st.header("Paso 2: Lo que la app escuchó")

            st.metric(
                label="Velocidad / Tempo detectado",
                value=f"{bpm_estimado} BPM",
            )

            # Feedback según el ritmo
            if bpm_estimado < 85:
                st.info(
                    "🌧️ **Ritmo Calmo / Balada**: Una onda relajada, perfecta para letras melancólicas o acústicas."
                )
            elif bpm_estimado < 120:
                st.info(
                    "🌙 **Ritmo Medio / Fluido**: Un tiempo ideal para Pop, Lofi o un rasgueo veraniego continuo."
                )
            else:
                st.info(
                    "✨ **Ritmo Enérgico**: Tu ukelele va rápido. Le vendría increíble una batería con mucho impulso."
                )
