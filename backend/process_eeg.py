import scipy.io
import numpy as np
import zlib
import hashlib
import json
import pandas as pd

# Load EEG data from .mat file
mat_data = scipy.io.loadmat("eeg_data.mat")
eeg_signals = mat_data['data']  # Assuming 'data' contains EEG signals
fs = 256  # Sampling frequency (modify if different)

# Function to apply a bandpass filter
from scipy.signal import butter, lfilter

def butter_bandpass(lowcut, highcut, fs, order=4):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return b, a

def filter_signal(data, lowcut, highcut, fs):
    b, a = butter_bandpass(lowcut, highcut, fs)
    return lfilter(b, a, data)

# Extract EEG bands
alpha_band = filter_signal(eeg_signals, 8, 12, fs)
beta_band = filter_signal(eeg_signals, 13, 30, fs)
theta_band = filter_signal(eeg_signals, 4, 7, fs)
gamma_band = filter_signal(eeg_signals, 30, 100, fs)

# Prepare structured EEG data
df = pd.DataFrame({
    'alpha': alpha_band.mean(axis=0),
    'beta': beta_band.mean(axis=0),
    'theta': theta_band.mean(axis=0),
    'gamma': gamma_band.mean(axis=0)
})

# Save structured data to JSON for storage
df.to_json("processed_eeg.json", orient="records")

# Convert EEG data to compressed bytes
compressed_data = zlib.compress(df.to_json().encode())

# Generate SHA-256 hash (fingerprint)
hash_fingerprint = hashlib.sha256(compressed_data).hexdigest()

# Save fingerprint for verification
with open("eeg_fingerprint.json", "w") as f:
    json.dump({"hash": hash_fingerprint}, f)

# Save compressed EEG data for blockchain upload
with open("compressed_eeg.bin", "wb") as f:
    f.write(compressed_data)

print(f"✅ EEG Data Processed & Hashed: {hash_fingerprint}")
print(f"📂 Saved compressed EEG data to 'compressed_eeg.bin'")