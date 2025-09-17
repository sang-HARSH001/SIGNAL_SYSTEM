import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from signal_utils import calculate_energy, calculate_power, is_periodic, is_causal
from sample_signals import get_sample_signals
import sympy as sp
from audiorec import audiorec
import io
import soundfile as sf

st.title("📊 Signal Type Analyzer")

# --- Load predefined signals ---
signals = get_sample_signals()
options = list(signals.keys()) + [
    "Modulus of Signal",
    "Derivative of Signal",
    "Integral of Signal",
    "Amplitude Scaling",
    "Custom Input",
    "Real-Time Voice Signal"
]

# --- Dropdown selection ---
option = st.selectbox("Select a sample signal or input your own:", options)

signal = None
time_axis = None
signal_type = None
signal_input = None

# --- Predefined signals ---
if option in signals:
    signal = signals[option]
    time_axis = np.arange(len(signal))
    signal_type = 'Discrete'

# --- Signal Operations ---
elif option in ["Modulus of Signal", "Derivative of Signal", "Integral of Signal", "Amplitude Scaling"]:
    base_signal_option = st.selectbox(
        "Choose base signal:", 
        list(signals.keys()) + ["Custom Input"]
    )

    base_signal = None
    base_signal_type = 'Discrete'
    base_input_expr = None
    
    if base_signal_option == "Custom Input":
        base_input = st.text_area(
            "Enter base signal as comma-separated values or expression (use 't' for continuous, 'n' for discrete):",
            placeholder="Example: 1,0,-1,0,1 or sin(2*n)+cos(n)"
        )
        if base_input:
            try:
                if ',' in base_input:
                    base_signal = np.array([float(x.strip()) for x in base_input.split(",")])
                    time_axis = np.arange(len(base_signal))
                    base_signal_type = 'Discrete'
                else:
                    if 't' in base_input:
                        base_signal_type = 'Continuous'
                        t = np.linspace(0, 10, 1000)
                        expr = sp.sympify(base_input, evaluate=False)
                        base_signal = np.array([float(expr.subs(sp.Symbol('t'), val)) for val in t])
                        time_axis = t
                    elif 'n' in base_input:
                        base_signal_type = 'Discrete'
                        n = np.arange(0, 20)
                        expr = sp.sympify(base_input, evaluate=False)
                        base_signal = np.array([float(expr.subs(sp.Symbol('n'), val)) for val in n])
                        time_axis = n
                    else:
                        st.error("❌ Use 't' for continuous or 'n' for discrete signals.")
                        base_signal = None
                base_input_expr = base_input
            except Exception as e:
                st.error(f"❌ Invalid input: {e}")
                base_signal = None
    else:
        base_signal = signals[base_signal_option]
        time_axis = np.arange(len(base_signal))
        base_signal_type = 'Discrete'

    if base_signal is not None:
        if option == "Modulus of Signal":
            signal = np.abs(base_signal)
        elif option == "Derivative of Signal":
            signal = np.diff(base_signal, prepend=0)
        elif option == "Integral of Signal":
            signal = np.cumsum(base_signal)
        elif option == "Amplitude Scaling":
            factor = st.number_input("Enter scaling factor:", value=1.0)
            signal = base_signal * factor
        signal_type = base_signal_type
        signal_input = base_input_expr

# --- Custom Input ---
elif option == "Custom Input":
    signal_input = st.text_area(
        "Enter a signal as a mathematical expression (use 't' for continuous or 'n' for discrete):",
        placeholder="Example: sin(2*t)*(t>=0)+0.5*cos(3*t)"
    )
    
    if signal_input:
        try:
            if 't' in signal_input:
                signal_type = 'Continuous'
                t = np.linspace(0, 10, 1000)
                expr = sp.sympify(signal_input, evaluate=False)
                signal = np.array([float(expr.subs(sp.Symbol('t'), val)) for val in t])
                time_axis = t
            elif 'n' in signal_input:
                signal_type = 'Discrete'
                n = np.arange(0, 20)
                expr = sp.sympify(signal_input, evaluate=False)
                signal = np.array([float(expr.subs(sp.Symbol('n'), val)) for val in n])
                time_axis = n
            else:
                st.error("❌ Use 't' for continuous or 'n' for discrete signals.")
        except Exception as e:
            st.error(f"❌ Invalid expression: {e}")

# --- Real-Time Voice Signal (Browser) ---
elif option == "Real-Time Voice Signal":
    st.subheader("🔊 Input Voice Signal (Browser Recording)")
    
    audio_bytes = audiorec()
    
    if audio_bytes:
        audio_buffer = io.BytesIO(audio_bytes)
        data, sample_rate = sf.read(audio_buffer)
        signal = data.flatten()
        duration = len(signal)/sample_rate
        time_axis = np.linspace(0, duration, len(signal))
        signal_type = 'Discrete'
        st.success("🎤 Recording completed!")

# --- CSV Upload Support ---
uploaded_file = st.file_uploader("Or upload a CSV file (with columns 'time' and 'amplitude')", type=['csv'])
if uploaded_file is not None:
    try:
        data = pd.read_csv(uploaded_file)
        if 'time' in data.columns and 'amplitude' in data.columns:
            time_axis = data['time'].values
            signal = data['amplitude'].values
            signal_type = 'Discrete'
        else:
            st.error("❌ CSV must contain 'time' and 'amplitude' columns.")
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")

# --- Visualization & Analysis ---
if signal is not None and time_axis is not None:
    st.subheader("📈 Signal Visualization")
    fig, ax = plt.subplots(figsize=(10,4))

    if option == "Custom Input":
        if signal_type == "Discrete":
            ax.stem(time_axis, signal, linefmt='b-', markerfmt='bo', basefmt='r-')
            ax.set_xlabel('n (samples)')
            ax.set_title("Discrete-Time Signal")
        else:
            ax.plot(time_axis, signal)
            ax.set_xlabel('t (seconds)')
            ax.set_title("Continuous-Time Signal")

    elif option == "Real-Time Voice Signal":
        display_type = st.radio("Choose waveform type to display:", ["Continuous-Time", "Discrete-Time"])
        if display_type == "Discrete-Time":
            ax.stem(np.arange(len(signal)), signal, linefmt='b-', markerfmt='bo', basefmt='r-')
            ax.set_xlabel('n (samples)')
            ax.set_title("Discrete-Time Representation")
        else:
            ax.plot(time_axis, signal)
            ax.set_xlabel('t (seconds)')
            ax.set_title("Continuous-Time Representation")

    else:
        signal_type_option = st.radio("Select Signal Type:", ["Discrete-Time", "Continuous-Time"])
        if signal_type_option == "Discrete-Time":
            ax.stem(time_axis, signal, linefmt='b-', markerfmt='bo', basefmt='r-')
            ax.set_xlabel('n (samples)')
        else:
            ax.plot(time_axis, signal)
            ax.set_xlabel('t (seconds)')
        ax.set_title("Signal Visualization")

    ax.set_ylabel('Amplitude')
    st.pyplot(fig)

    # --- Signal Analysis ---
    energy = calculate_energy(signal)
    power = calculate_power(signal)
    periodic, period = is_periodic(signal)

    # --- Automatic Causality Detection ---
    causal = False
    if option == "Custom Input" or signal_type == "Continuous":
        expr_str = signal_input.replace(" ", "").lower() if signal_input else ""
        if "heaviside" in expr_str or "(t>=0)" in expr_str:
            causal = True
        else:
            causal = np.all(time_axis >= 0)
    elif option == "Real-Time Voice Signal" or signal_type == "Discrete":
        causal = np.all(time_axis[np.abs(signal) > 1e-6] >= 0)

    # --- Display Analysis ---
    st.subheader("✅ Analysis Results")
    st.write(f"**Energy**: {energy:.4f}")
    st.write(f"**Power**: {power:.4f}")
    st.write("🟢 Classified as **Energy Signal**" if energy < 1e3 else "🟢 Classified as **Power Signal**")
    st.write(f"🔄 Periodic: {'Yes' if periodic else 'No'}", f"(Period = {period})" if periodic else "")
    st.write(f"🔔 Causal: {'Yes' if causal else 'No'}")
