import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from signal_utils import calculate_energy, calculate_power, is_periodic, is_causal
from sample_signals import get_sample_signals

# For browser-based audio recording
from st_audiorec import st_audiorec
import io
import soundfile as sf

st.title("📊 Signal Type Analyzer")

st.write("👉 Select whether your signal is Discrete-Time or Continuous-Time.")

signal_type = st.radio("Signal Type:", ["Discrete-Time", "Continuous-Time"])

option = st.selectbox(
    "Select a sample signal or input your own:", 
    [
        "Exponential Decay", 
        "Sine Wave", 
        "Cosine Wave", 
        "Unit Step Signal", 
        "Unit Impulse Signal", 
        "Ramp Signal", 
        "Non-Causal", 
        "Custom Input",
        "Real-Time Voice Signal"
    ]
)

signal = None
time_axis = None

# 1️⃣ Predefined sample signals
if option not in ["Custom Input", "Real-Time Voice Signal"]:
    signals = get_sample_signals()
    signal = signals[list(signals.keys())[[
        "Exponential Decay", "Sine Wave", "Cosine Wave", 
        "Unit Step Signal", "Unit Impulse Signal", "Ramp Signal", "Non-Causal"
    ].index(option)]]
    time_axis = np.arange(len(signal)) if signal_type == "Discrete-Time" else np.linspace(0, len(signal)/10, len(signal))

# 2️⃣ Custom input
elif option == "Custom Input":
    signal_input = st.text_area(
        "Enter comma-separated signal values (e.g., 1, 0, -1, 0, 1):",
        placeholder="Example: 1, 0, -1, 0, 1"
    )
    if signal_input:
        try:
            signal = np.array([float(x.strip()) for x in signal_input.split(",")])
            time_axis = np.arange(len(signal)) if signal_type == "Discrete-Time" else np.linspace(0, len(signal)/10, len(signal))
        except:
            st.error("❌ Invalid input format.")
            signal = None

# 3️⃣ Real-time voice signal (browser-based)
elif option == "Real-Time Voice Signal":
    st.subheader("🎤 Record Your Voice")
    wav_audio_data = st_audiorec()
    
    if wav_audio_data is not None and len(wav_audio_data) > 0:
        st.audio(wav_audio_data, format='audio/wav')
        try:
            audio_array, sample_rate = sf.read(io.BytesIO(wav_audio_data))
            
            # Ensure mono channel
            if audio_array.ndim > 1:
                signal = audio_array[:, 0]
            else:
                signal = audio_array
            
            # Normalize amplitude
            if np.max(np.abs(signal)) > 0:
                signal = signal / np.max(np.abs(signal))
            
            # Generate time axis
            time_axis = np.arange(len(signal)) if signal_type == "Discrete-Time" else np.linspace(0, len(signal)/sample_rate, len(signal))
        
        except Exception as e:
            st.error(f"❌ Error processing audio: {e}")

# 4️⃣ File upload support
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

# Run analysis and visualization
if signal is not None and time_axis is not None and len(signal) > 0:
    st.subheader("📈 Signal Visualization")
    fig, ax = plt.subplots()
    if signal_type == "Discrete-Time":
        ax.stem(time_axis, signal)
        ax.set_xlabel('n (samples)')
    else:
        ax.plot(time_axis, signal)
        ax.set_xlabel('t (seconds)')
    ax.set_ylabel('Amplitude')
    st.pyplot(fig)

    energy = calculate_energy(signal)
    power = calculate_power(signal)
    periodic, period = is_periodic(signal)
    causal = is_causal(signal)

    st.subheader("✅ Analysis Results")
    st.write(f"**Energy**: {energy:.4f}")
    st.write(f"**Power**: {power:.4f}")
    
    if energy < 1e3:
        st.write("🟢 Classified as **Energy Signal**")
    else:
        st.write("🟢 Classified as **Power Signal**")

    st.write(f"🔄 Periodic: {'Yes' if periodic else 'No'}", f"(Period = {period})" if periodic else "")
    st.write(f"🔔 Causal: {'Yes' if causal else 'No'}")
