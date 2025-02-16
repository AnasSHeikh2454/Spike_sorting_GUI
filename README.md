# Spike Sorting GUI Project

## Overview
This repository contains the **Spike Sorting GUI**, a Python-based application designed to simplify and streamline the process of spike sorting for neural data. By integrating **MountainSort5** and **SpikeInterface** into an intuitive graphical interface, researchers can efficiently analyze single-channel extracellular recordings without extensive programming knowledge.

## Repository Contents
- **Anas_Sheikh_(2021BA432454H)_Final_Report.pdf**  
  A comprehensive final report detailing the project’s scope, methodology, results, and conclusions.

- **Spike_Sorting_GUI_Report_Detailed.pdf**  
  An in-depth technical description of the spike sorting GUI, including user instructions and advanced configurations.

- **Spike_sorting_GUI.py**  
  The primary Python script that launches the GUI. Users can configure parameters such as SNR ratio, detection thresholds, and channel radius for spike sorting.

- **spike_data_unit_1.csv**, **spike_data_unit_2.csv**, **spike_data_unit_3.csv**  
  Sample CSV files containing spike data for demonstration and testing. These files illustrate how to structure data for input into the GUI.

## Features
1. **User-Friendly Interface**  
   - Developed with **Tkinter**, providing a straightforward layout and clear prompts.

2. **Parameter Customization**  
   - Adjust SNR ratio, detection thresholds, time radius, and more for fine-tuning spike detection.

3. **Visualization Tools**  
   - Integrated plotting (using Matplotlib and SpikeInterface widgets) to observe spike waveforms and templates in real time.

4. **Data Export**  
   - Automatically saves spike data (per unit or channel) into Excel/CSV files, making it easier for subsequent data analysis.

5. **Scalability**  
   - Adapted primarily for single-channel data but can be extended for multi-channel data in the future.

## Installation
1. **Clone this repository**:
   ```bash
   git clone https://github.com/AnasSheikh2454/Spike_Sorting_GUI.git
   cd Spike_Sorting_GUI
   ```

2. **Install required packages**:
   ```bash
   pip install -r requirements.txt
   ```
   If you don't have a `requirements.txt`, install packages manually:
   ```bash
   pip install numpy pandas matplotlib spikeinterface mountainsort5 openpyxl
   ```

3. **Verify data files**:
   Ensure you have valid spike data (e.g., `spike_data_unit_1.csv`) and frequency data (if needed) in the correct format.

## Usage
1. **Run the GUI**:
   ```bash
   python Spike_sorting_GUI.py
   ```
2. **Load Spike Data**:
   - Click on “Browse” to select the folder containing your Open Ephys or CSV files.

3. **Configure Parameters**:
   - Adjust SNR ratio, detection thresholds, channel radius, etc.

4. **Run Spike Sorting**:
   - The GUI will process your data and produce an Excel/CSV file with sorted spikes.

5. **View Results**:
   - Plots of waveforms/templates are automatically displayed.
   - Exported data is stored in the project directory.

## Contributing
Contributions are welcome! For major changes, please open an issue to discuss what you’d like to modify.

1. Fork the repository.
2. Create a new branch for your feature (`git checkout -b feature-name`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to your branch (`git push origin feature-name`).
5. Create a new Pull Request.



## Contact
**Author:** Anas Sheikh  

**GitHub:** [AnasSheikh2454](https://github.com/AnasSheikh2454)

## Acknowledgments
- **MountainSort5** and **SpikeInterface** for providing robust spike sorting algorithms and data handling frameworks.
- **Tkinter** for simplifying GUI development.
- All contributors and mentors who provided guidance and feedback.



