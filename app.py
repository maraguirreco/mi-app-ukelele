import io
import librosa
import numpy as np
import soundfile as sf
import streamlit as st


# Función para sintetizar una batería simple en Python
def generar_bateria(bpm, duracion_seg=8, sr=22050):
    beat_interval = 60.0 / bpm
    t_beat = np.linspace(0, 0.1, int(sr * 0.1))

    # Generamos un sonido de Bombo (Kick)
    freq = np.linspace(130, 30, len(t_beat))
    kick = np.sin(2 * np.pi * freq * t_beat) * np.exp(-t_beat * 30)

    # Generamos un sonido de Tarola (Snare)
    snare = np.random.uniform(-1, 1, len(t_beat)) * np.exp(-t_beat * 25)

    total_samples = int(sr * duracion_seg)
    drums = np.zeros(total_samples)

    num_beats = int(duracion_seg / beat_interval)
    for i in range(num_beats):
        sample_idx = int(i * beat_interval * sr)
        if sample_idx + len(t_beat) < total_samples:
            if i % 2 == 0:
                drums[sample_idx : sample_idx + len(t_beat)] += kick
            else:
                drums[sample_idx : sample_idx + len(t_beat)] += snare

    drums = drums / (np.max(np.abs(drums)) + 1e-6)
    return drums, sr


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

    if st.button("🔍 Analizar el ritmo de mi ukelele"):
        with st.spinner("Escuchando tu ukelele y contando los tiempos..."):
            audio_bytes = audio_grabado.getvalue()
            audio_file = io.BytesIO(audio_bytes)

            y, sr = librosa.load(audio_file, sr=None)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

            bpm_valor = float(np.atleast_1d(tempo)[0])
            st.session_state["bpm"] = int(np.round(bpm_valor))

if "bpm" in st.session_state:
    bpm_estimado = st.session_state["bpm"]
    st.divider()

    # Paso 2: Resultados
    st.header("Paso 2: Lo que la app escuchó")
    st.metric(label="Velocidad detectada", value=f"{bpm_estimado} BPM")

    st.divider()

    # Paso 3: Acompañamiento
    st.header("Paso 3: Genera tu acompañamiento")
    st.write(
        "Presiona el botón para crear una base de batería personalizada para tu ritmo:"
    )

    if st.button("🥁 Crear batería para mi ukelele"):
        with st.spinner("Creando los tambores al ritmo de tu ukelele..."):
            audio_drums, sr_drums = generar_bateria(bpm_estimado)

            # Convertir audio a buffer para reproducir
            buffer = io.BytesIO()
            sf.write(buffer, audio_drums, sr_drums, format="WAV")

            st.success(
                f"¡Batería creada exactamente a {bpm_estimado} BPM! Escúchala aquí:"
            )
            st.audio(buffer.getvalue(), format="audio/wav")
