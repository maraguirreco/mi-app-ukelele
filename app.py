import io
import librosa
import numpy as np
import soundfile as sf
import streamlit as st


# Generador de Batería Simulado
def generar_bateria(bpm, duracion_seg, sr=22050):
    beat_interval = 60.0 / bpm
    t_beat = np.linspace(0, 0.1, int(sr * 0.1))

    # Sonidos de bombo y tarola
    kick = np.sin(2 * np.pi * np.linspace(130, 30, len(t_beat)) * t_beat) * np.exp(
        -t_beat * 30
    )
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
audio_grabado = st.audio_input("Toca tu ukelele para grabar:")

if audio_grabado:
    st.success("¡Audio capturado!")

    if st.button("🔍 Analizar ritmo y preparar producción"):
        with st.spinner("Procesando tu ukelele..."):
            audio_bytes = audio_grabado.getvalue()
            audio_file = io.BytesIO(audio_bytes)

            # Cargar ukelele
            y_uke, sr_uke = librosa.load(audio_file, sr=22050)
            tempo, _ = librosa.beat.beat_track(y=y_uke, sr=sr_uke)

            bpm_valor = float(np.atleast_1d(tempo)[0])
            st.session_state["bpm"] = int(np.round(bpm_valor))
            st.session_state["y_uke"] = y_uke
            st.session_state["sr"] = sr_uke

if "bpm" in st.session_state:
    bpm = st.session_state["bpm"]
    y_uke = st.session_state["y_uke"]
    sr = st.session_state["sr"]

    duracion_seg = len(y_uke) / sr

    st.divider()
    st.header("Paso 2: Análisis")
    st.metric(label="Velocidad detectada", value=f"{bpm} BPM")

    st.divider()
    st.header("Paso 3: Producción y Mezcla Completa")

    # Controles intuitivos de volumen
    st.subheader("🎛️ Mezclador de volúmenes")
    vol_uke = st.slider("Volumen de tu Ukelele", 0.0, 1.0, 0.8)
    vol_drums = st.slider("Volumen de la Batería", 0.0, 1.0, 0.5)

    if st.button("🎚️ Producir y Mezclar Demo"):
        with st.spinner("Mezclando tu ukelele con la batería..."):
            # Generar batería de la misma duración que la grabación
            drums, _ = generar_bateria(bpm, duracion_seg=duracion_seg, sr=sr)

            # Ajustar volúmenes y mezclar
            uke_ajustado = y_uke * vol_uke
            drums_ajustado = drums * vol_drums

            # Combinar ambas pistas
            mezcla = uke_ajustado + drums_ajustado
            mezcla = mezcla / (np.max(np.abs(mezcla)) + 1e-6)  # Normalizar

            # Guardar en buffer de audio
            buffer_mezcla = io.BytesIO()
            sf.write(buffer_mezcla, mezcla, sr, format="WAV")
            audio_final = buffer_mezcla.getvalue()

            st.success("🎉 ¡Tu Demo está listo!")
            st.audio(audio_final, format="audio/wav")

            # Botón de descarga
            st.download_button(
                label="💾 Descargar mi canción (.wav)",
                data=audio_final,
                file_name=f"demo_ukelele_{bpm}bpm.wav",
                mime="audio/wav",
            )
