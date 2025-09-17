import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from signal_utils import calculate_energy, calculate_power, is_periodic, is_causal
from sample_signals import get_sample_signals
import soundfile as sf

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
if option not in ["Custom Input", "Real-Time Voice Signal"]:
    signals = get_sample_signals()
    signal = signals[list(signals.keys())[[
        "Exponential Decay", "Sine Wave", "Cosine Wave", 
        "Unit Step Signal", "Unit Impulse Signal", "Ramp Signal", 
    ].index(option)]]
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
        except:
            st.error("❌ Invalid input format.")
            signal = None

# Real-time voice signal (Upload WAV instead of recording)
elif option == "Real-Time Voice Signal":
    st.subheader("🔊 Upload a Voice Recording (.wav)")

    uploaded_audio = st.file_uploader("Upload your .wav file", type=['wav'])

    if uploaded_audio is not None:
        data, sample_rate = sf.read(uploaded_audio)
        signal = data.flatten()
        duration = len(signal) / sample_rate
        time_axis = np.linspace(0, duration, len(signal))
        st.success("✅ Audio file loaded successfully.")

# File upload support
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
    if option == "Real-Time Voice Signal":
        st.subheader("📈 Voice Signal Visualization")

        display_type = st.radio("Choose waveform type to display:", ["Continuous-Time", "Discrete-Time"])

        fig, ax = plt.subplots(figsize=(10, 4))
        
        if display_type == "Continuous-Time":
            ax.plot(time_axis, signal)
            ax.set_title("Continuous-Time Representation")
            ax.set_xlabel('t (seconds)')
        else:
            ax.stem(np.arange(len(signal)), signal)
            ax.set_title("Discrete-Time Representation")
            ax.set_xlabel('n (samples)')
        
        ax.set_ylabel('Amplitude')
        st.pyplot(fig)

    else:
        signal_type = st.radio("Select Signal Type:", ["Discrete-Time", "Continuous-Time"])

        if signal_type == "Continuous-Time":
            time_axis = np.linspace(0, len(signal)/10, len(signal))
        else:
            time_axis = np.arange(len(signal))

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

    # Analysis Results
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
