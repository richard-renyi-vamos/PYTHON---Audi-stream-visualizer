import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

# Constants
CHUNK = 1024  # Number of audio samples per frame
FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
CHANNELS = 1  # Number of audio channels
RATE = 44100  # Sampling rate (44.1 kHz)

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Open audio stream
stream = audio.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK
)

# Create GUI window
root = tk.Tk()
root.title("Real-Time Audio Visualizer")

# Create figure for plotting
fig, (ax_waveform, ax_spectrogram) = plt.subplots(2, 1, figsize=(8, 6))

# Waveform plot setup
x_waveform = np.arange(0, CHUNK)
y_waveform = np.zeros(CHUNK)
line_waveform, = ax_waveform.plot(x_waveform, y_waveform, lw=2)
ax_waveform.set_title("Waveform")
ax_waveform.set_xlim(0, CHUNK)
ax_waveform.set_ylim(-32768, 32767)
ax_waveform.set_xlabel("Samples")
ax_waveform.set_ylabel("Amplitude")

# Spectrogram plot setup
x_spectrogram = np.linspace(0, RATE / 2, CHUNK // 2)
z_spectrogram = np.zeros((100, CHUNK // 2))
img_spectrogram = ax_spectrogram.imshow(
    z_spectrogram,
    aspect='auto',
    extent=[0, RATE / 2, 0, 100],
    origin='lower',
    cmap='viridis'
)
ax_spectrogram.set_title("Spectrogram")
ax_spectrogram.set_xlabel("Frequency (Hz)")
ax_spectrogram.set_ylabel("Time (frames)")

# Embed the figure in the Tkinter canvas
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill=tk.BOTH, expand=True)

# Update function for animation
def update():
    # Read audio data
    data = stream.read(CHUNK, exception_on_overflow=False)
    audio_data = np.frombuffer(data, dtype=np.int16)

    # Update waveform
    line_waveform.set_ydata(audio_data)

    # Compute FFT for spectrogram
    fft_data = np.abs(np.fft.rfft(audio_data))
    fft_data = 20 * np.log10(np.maximum(fft_data, 1e-6))  # Convert to dB scale

    # Update spectrogram
    global z_spectrogram
    z_spectrogram = np.roll(z_spectrogram, -1, axis=0)
    z_spectrogram[-1, :] = fft_data
    img_spectrogram.set_array(z_spectrogram)

    # Redraw the canvas
    canvas.draw()

    # Schedule the next update
    root.after(50, update)

# Start the update loop
update()

# Run the Tkinter main loop
try:
    root.mainloop()
except KeyboardInterrupt:
    pass

# Cleanup
def close_stream():
    stream.stop_stream()
    stream.close()
    audio.terminate()

close_stream()
