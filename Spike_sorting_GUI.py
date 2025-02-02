import os
import shutil
from tempfile import mkdtemp
import numpy as np
import spikeinterface as si
import spikeinterface.preprocessing as spre
import spikeinterface.extractors as se
import mountainsort5 as ms5
from mountainsort5.util import create_cached_recording
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
import spikeinterface.widgets as sw

class SpikeSortingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Spike Sorting GUI")

        # Parameters
        self.file_path = tk.StringVar()
        self.snr_ratio = tk.DoubleVar(value=3.0)
        self.detect_sign = tk.IntVar(value=0)
        self.phase1_threshold = tk.DoubleVar(value=3.5)
        self.detect_threshold = tk.DoubleVar(value=2.5)
        self.channel_radius = tk.IntVar(value=200)
        self.time_radius = tk.DoubleVar(value=0.8)
        self.block_duration = tk.IntVar(value=600)
        self.detect_channel_radius = tk.IntVar(value=30)  # New parameter
        self.detect_time_radius = tk.DoubleVar(value=0.8)  # New parameter
        self.channel_locations = tk.StringVar(value="0,0")  # Default channel locations

        self.create_widgets()

    def create_widgets(self):
        # File selection
        tk.Label(self.root, text="Open Ephys File:").grid(row=0, column=0, sticky="w")
        tk.Entry(self.root, textvariable=self.file_path, width=40).grid(row=0, column=1)
        tk.Button(self.root, text="Browse", command=self.browse_file).grid(row=0, column=2)

        # Input parameters
        tk.Label(self.root, text="SNR Ratio:").grid(row=1, column=0, sticky="w")
        tk.Entry(self.root, textvariable=self.snr_ratio).grid(row=1, column=1)

        tk.Label(self.root, text="Detect Sign:").grid(row=2, column=0, sticky="w")
        tk.Entry(self.root, textvariable=self.detect_sign).grid(row=2, column=1)

        tk.Label(self.root, text="Phase1 Detect Threshold:").grid(row=3, column=0, sticky="w")
        tk.Entry(self.root, textvariable=self.phase1_threshold).grid(row=3, column=1)

        tk.Label(self.root, text="Detect Threshold:").grid(row=4, column=0, sticky="w")
        tk.Entry(self.root, textvariable=self.detect_threshold).grid(row=4, column=1)

        tk.Label(self.root, text="Channel Radius:").grid(row=5, column=0, sticky="w")
        tk.Entry(self.root, textvariable=self.channel_radius).grid(row=5, column=1)

        tk.Label(self.root, text="Time Radius (msec):").grid(row=6, column=0, sticky="w")
        tk.Entry(self.root, textvariable=self.time_radius).grid(row=6, column=1)

        tk.Label(self.root, text="Block Duration (sec):").grid(row=7, column=0, sticky="w")
        tk.Entry(self.root, textvariable=self.block_duration).grid(row=7, column=1)

        # New parameters
        tk.Label(self.root, text="Detect Channel Radius:").grid(row=8, column=0, sticky="w")
        tk.Entry(self.root, textvariable=self.detect_channel_radius).grid(row=8, column=1)

        tk.Label(self.root, text="Detect Time Radius (msec):").grid(row=9, column=0, sticky="w")
        tk.Entry(self.root, textvariable=self.detect_time_radius).grid(row=9, column=1)

        # Channel locations
        tk.Label(self.root, text="Channel Locations (x,y; ...):").grid(row=10, column=0, sticky="w")
        tk.Entry(self.root, textvariable=self.channel_locations, width=40).grid(row=10, column=1, columnspan=2)

        # Run button
        tk.Button(self.root, text="Run Spike Sorting", command=self.run_spike_sorting).grid(row=11, column=1)

    def browse_file(self):
        file_path = filedialog.askdirectory()
        self.file_path.set(file_path)

    def parse_channel_locations(self):
        try:
            loc_strings = self.channel_locations.get().split(';')
            locations = [tuple(map(float, loc.strip().split(','))) for loc in loc_strings]
            return np.array(locations)
        except ValueError:
            raise ValueError("Invalid format for channel locations. Use 'x1,y1; x2,y2; ...'")

    def run_spike_sorting(self):
        file_path = self.file_path.get()
        if not file_path:
            messagebox.showerror("Error", "Please select an Open Ephys file.")
            return

        try:
            locations = self.parse_channel_locations()
            run_spike_sorting(
                file_path,
                self.snr_ratio.get(),
                self.detect_sign.get(),
                self.phase1_threshold.get(),
                self.detect_threshold.get(),
                self.channel_radius.get(),
                self.time_radius.get(),
                self.block_duration.get(),
                self.detect_channel_radius.get(),
                self.detect_time_radius.get(),
                locations
            )
            messagebox.showinfo("Success", "Spike sorting completed and data saved to 'spike_data_GUI.xlsx'")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

def run_spike_sorting(file_path, snr_ratio, detect_sign, phase1_threshold, detect_threshold, channel_radius, time_radius, block_duration, detect_channel_radius, detect_time_radius, locations):
    # Load the recording
    recording = se.read_openephys(file_path)

    # Ensure the locations are in the correct 2D array format
    if len(locations) == 2 and isinstance(locations, (list, tuple, np.ndarray)):
        # Ensure the locations are reshaped to (1, 2) for a single channel
        locations = np.array([locations]).reshape(1, 2)
    
    # Set channel locations on the entire recording
    recording.set_channel_locations(np.tile(locations, (recording.get_num_channels(), 1)))

    # Now select channel CH4
    recording_channel = recording.select_channels(['CH4'])

    # Apply filtering and whitening
    recording_filtered = spre.bandpass_filter(recording_channel, freq_min=300, freq_max=6000, dtype=np.float32)
    recording_whitened = spre.whiten(recording_filtered)

    # Force set channel locations on the selected channel
    if not recording_channel.get_channel_locations().size:
        recording_channel.set_channel_locations(locations)

    # Retrieve and adjust the start time
    try:
        start_times = recording.get_times()
        start_time_sec = start_times[0]
        print(f"Start time of the recording: {start_time_sec:.9f} seconds")
    except (AttributeError, IndexError):
        start_time_sec = 0.0
        print("Start time not found. Using default 0 seconds.")

    # Ensure the SNR is adjusted
    def estimate_noise_level(recording):
        traces = recording.get_traces()
        return np.median(np.abs(traces) / 0.6745, axis=0)

    def ensure_snr(recording, snr_target):
        noise_level = estimate_noise_level(recording)
        if np.any(noise_level == 0):
            print("Warning: Zero noise level detected. Scaling skipped.")
            return recording
        gain = snr_target / noise_level
        return spre.scale(recording, gain=gain)

    recording_scaled = ensure_snr(recording_whitened, snr_ratio)
    recording_resampled = spre.resample(recording_scaled, resample_rate=int(2 * recording.get_sampling_frequency()))

    # Create a temporary directory for caching
    tmpdir = mkdtemp()
    recording_cached = create_cached_recording(recording_resampled, folder=tmpdir)

    # Run the sorting algorithm
    sorting = ms5.sorting_scheme3(
        recording=recording_cached,
        sorting_parameters=ms5.Scheme3SortingParameters(
            block_sorting_parameters=ms5.Scheme2SortingParameters(
                detect_sign=detect_sign,
                phase1_detect_threshold=phase1_threshold,
                detect_threshold=detect_threshold,
                phase1_detect_channel_radius=channel_radius,
                detect_channel_radius=detect_channel_radius,  # Updated with new parameter
                phase1_detect_time_radius_msec=time_radius,
                detect_time_radius_msec=detect_time_radius  # Updated with new parameter
            ),
            block_duration_sec=block_duration
        )
    )

    # Analyze sorting and plot waveforms/templates
    sorting_analyzer = si.create_sorting_analyzer(sorting=sorting, recording=recording_cached, format='memory')
    sorting_analyzer.compute(["random_spikes", "waveforms", "templates"])

    # Collect spike data and save to an Excel file
    spike_data = []
    unit_ids = sorting.get_unit_ids()
    for unit_id in unit_ids:
        spike_train = sorting.get_unit_spike_train(unit_id)
        spike_times = (spike_train / sorting.get_sampling_frequency()) + start_time_sec
        for timestamp in spike_times:
            spike_data.append({"Unit": unit_id, "Timestamp (s)": timestamp})

    # Save the spike data to an Excel file
        # Save the spike data to an Excel file with different sheets for each unit
    with pd.ExcelWriter("spike_data_GUI.xlsx", engine="xlsxwriter") as writer:
        for unit_id in unit_ids:
            # Filter spike data for the current unit
            unit_spike_data = [{"Unit": unit_id, "Timestamp (s)": timestamp} for timestamp in (sorting.get_unit_spike_train(unit_id) / sorting.get_sampling_frequency()) + start_time_sec]
            df_unit = pd.DataFrame(unit_spike_data)
            sheet_name = f"Unit_{unit_id}"
            df_unit.to_excel(writer, sheet_name=sheet_name, index=False, float_format="%.9f")

    

    # Plot waveforms and templates for each unit
    for unit_id in unit_ids:
        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1)
        sw.plot_unit_waveforms(sorting_analyzer, unit_ids=[unit_id])
        plt.title(f"Spike Waveforms for Unit {unit_id}")

        plt.subplot(1, 2, 2)
        sw.plot_unit_templates(sorting_analyzer, unit_ids=[unit_id])
        plt.title(f"Spike Template for Unit {unit_id}")
        plt.tight_layout()
        plt.show()

    # Clean up temporary directory
    shutil.rmtree(tmpdir, ignore_errors=True)

if __name__ == '__main__':
    root = tk.Tk()
    app = SpikeSortingGUI(root)
    root.mainloop()
