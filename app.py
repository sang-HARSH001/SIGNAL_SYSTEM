import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from signal_utils import calculate_energy, calculate_power, is_periodic, is_causal
from sample_signals import get_sample_signals
from st_audiorec import st_audiorec  # ✅ Corrected import
import scipy.io.wavfile as wav
import io

st.title("📊 Signal Type Analyzer")

option = st.selectbox(
    "Select a sample signal or input your own:",
    [
        "Exponential Decay",
        "Sine Wave",
        "Cosine Wave",
        "Unit Step Signal",
        "Unit Impulse Signal",
        "Ramp Signal",
        "Custom Input",
        "Real-Time Voice Signal"
    ]
)

signal = None
time_axis = None

# Predefined sample signals
sample_signals = get_sample_signals()
if option in sample_signals:
    signal = sample_signals.get(option)
    time_axis = np.arange(len(signal))

# Custom input
elif option == "Custom Input":
    signal_input = st.text_area(
        "Enter comma-separated signal values (e.g., 1, 0, -1, 0, 1):",
        placeholder="Example: 1, 0, -1, 0, 1"
    )
    if signal_input:
        try:
            signal = np.array([float(x.strip()) for x in signal_input.split(",")])
            time_axis = np.arange(len(signal))
        except ValueError:
            st.error("❌ Invalid input format. Please enter numeric values separated by commas.")

# Real-time voice signal
elif option == "Real-Time Voice Signal":
    st.subheader("🔊 Input Voice Signal")
    input_mode = st.radio("Choose Input Mode:", ["Record Real-Time Voice", "Upload WAV File"])

    if input_mode == "Record Real-Time Voice":
        st.info("🎙️ Click below to start recording using your browser microphone.")
        wav_audio_data = st_audiorec()

        if wav_audio_data is not None:
            st.audio(wav_audio_data, format='audio/wav')
            st.success("🎤 Recording captured successfully!")

            try:
                wav_bytes = io.BytesIO(wav_audio_data)
                sample_rate, data = wav.read(wav_bytes)
                signal = data.astype(np.float32)
                if signal.ndim > 1:
                    signal = signal.mean(axis=1)
                duration = len(signal) / sample_rate
                time_axis = np.linspace(0, duration, len(signal))
            except Exception as e:
                st.error(f"❌ Error processing audio: {e}")

    else:
        uploaded_audio = st.file_uploader("Upload your .wav file", type=['wav'])
        if uploaded_audio is not None:
            try:
                sample_rate, data = wav.read(uploaded_audio)
                signal = data.astype(np.float32)
                if signal.ndim > 1:
                    signal = signal.mean(axis=1)
                duration = len(signal) / sample_rate
                time_axis = np.linspace(0, duration, len(signal))
                st.success("✅ Audio file loaded successfully.")
            except Exception as e:
                st.error(f"❌ Error reading audio file: {e}")

# CSV file upload
uploaded_file = st.file_uploader("Or upload a CSV file (with columns 'time' and 'amplitude')", type=['csv'])
if uploaded_file is not None:
    try:
        data = pd.read_csv(uploaded_file)
        if 'time' in data.columns and 'amplitude' in data.columns:
            time_axis = data['time'].values
            signal = data['amplitude'].values
        else:
            st.error("❌ CSV must contain 'time' and 'amplitude' columns.")
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")

# Visualization and Analysis
if signal is not None and time_axis is not None:
    st.subheader("📈 Signal Visualization")
    signal_type = st.radio("Select Signal Type:", ["Discrete-Time", "Continuous-Time"])
    if signal_type == "Continuous-Time":
        time_axis = np.linspace(0, len(signal)/10, len(signal))
    else:
        time_axis = np.arange(len(signal))

    fig, ax = plt.subplots(figsize=(10, 4))
    if signal_type == "Discrete-Time":
        ax.stem(time_axis, signal, linefmt='b-', markerfmt='bo', basefmt='r-')
        ax.set_xlabel('n (samples)')
    else:
        ax.plot(time_axis, signal)
        ax.set_xlabel('t (seconds)')
    ax.set_ylabel('Amplitude')
    ax.set_title(f"{option} - {signal_type} Representation")
    st.pyplot(fig)

    # Analysis Results
    energy = calculate_energy(signal)
    power = calculate_power(signal)
    periodic, period = is_periodic(signal)
    causal = is_causal(signal)

    st.subheader("✅ Analysis Results")
    st.write(f"**Energy**: {energy:.4f}")
    st.write(f"**Power**: {power:.4f}")
    st.write("🟢 Classified as **Energy Signal**" if energy < 1e3 else "🟢 Classified as **Power Signal**")
    st.write(f"🔄 Periodic: {'Yes' if periodic else 'No'}" + (f" (Period = {period})" if periodic else ""))
    st.write(f"🔔 Causal: {'Yes' if causal else 'No'}")
