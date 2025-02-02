import os
import pandas as pd
import matplotlib.pyplot as plt

# Desired Variables
file_path = 'C:/Users/Anas/OneDrive/Desktop/sop lop/spike_data_GUI.xlsx'  # Path to your Excel file
block_size = 500  # Time block size in ms
output_folder = 'plots/'  # Folder to save the plots for each unit
marker_size = 1 # Reduced marker size for dots
output_spike_counts_file = 'spike_counts.xlsx'  # File to save spike counts in Excel

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Step 1: Load All Sheets from Excel
sheets = pd.read_excel(file_path, sheet_name=None)  # Load all sheets into a dictionary

# Combine data from all sheets into a single DataFrame
combined_data = pd.DataFrame()

for sheet_name, sheet_data in sheets.items():
    print(f"Processing sheet: {sheet_name}")
    
    # Ensure columns are correctly named and stripped of extra spaces
    sheet_data.columns = sheet_data.columns.str.strip()
    
    if 'Timestamp' not in sheet_data.columns:
        print(f"Sheet '{sheet_name}' does not have the required 'Timestamp' column.")
        continue  # Skip sheets without the correct format
    
    # Convert timestamps from seconds to milliseconds
    sheet_data['Timestamp'] = sheet_data['Timestamp'] * 1000  # Convert to ms
    
    # Add a column to distinguish sheets (unit ID is based on sheet name)
    sheet_data['Unit'] = sheet_name  # Use sheet name as Unit ID
    combined_data = pd.concat([combined_data, sheet_data], ignore_index=True)

if combined_data.empty:
    print("No valid data found in the Excel file. Please check the input sheets.")
    exit()

# Step 2: Filter and Group Spikes into 500ms Time Blocks
# Sort data by timestamp
combined_data = combined_data.sort_values(by='Timestamp')

# Calculate block IDs for each timestamp
combined_data['Block'] = (combined_data['Timestamp'] // block_size).astype(int)

# Discard spikes in the final incomplete block
filtered_data = pd.DataFrame()
for Unit, unit_data in combined_data.groupby('Unit'):
    max_timestamp = unit_data['Timestamp'].max()  # Get the maximum timestamp for this unit
    max_full_block = (max_timestamp // block_size) * block_size  # Last complete 500ms block start time
    unit_data = unit_data[unit_data['Timestamp'] < max_full_block + block_size]  # Keep only full blocks
    filtered_data = pd.concat([filtered_data, unit_data], ignore_index=True)

# Step 3: Calculate Spike Counts
spike_counts_dfs = []  # To store DataFrame for each unit

for Unit, unit_data in filtered_data.groupby('Unit'):
    unit_total_spikes = 0  # Initialize total spike count for the unit
    block_spike_counts = []  # To store block-wise counts for the unit

    # Determine the range of block IDs for this unit
    min_block = unit_data['Block'].min()
    max_block = unit_data['Block'].max()

    # Loop through all possible block IDs (including those with zero spikes)
    for block_id in range(min_block, max_block + 1):
        block_data = unit_data[unit_data['Block'] == block_id]
        block_spike_count = len(block_data)  # Count spikes in the current block
        block_spike_counts.append({'Block': block_id, 'Spike_Count': block_spike_count})
        unit_total_spikes += block_spike_count  # Update total spike count for the unit

    # Create a DataFrame for this unit
    unit_spike_counts_df = pd.DataFrame(block_spike_counts)
    unit_spike_counts_df['Unit'] = Unit  # Add unit column
    unit_spike_counts_df['Total_Spikes'] = unit_total_spikes  # Add total spikes column
    spike_counts_dfs.append(unit_spike_counts_df)

# Combine all units' spike counts into a single DataFrame for Excel output
final_spike_counts_df = pd.concat(spike_counts_dfs, ignore_index=True)

# Save spike counts to an Excel file
final_spike_counts_df.to_excel(output_spike_counts_file, index=False)

# Print spike counts
print("Spike counts saved to Excel:")
print(final_spike_counts_df)

# Step 4: Create Separate Plots for Each Unit (Retained from the previous code)
for Unit, unit_data in filtered_data.groupby('Unit'):
    plt.figure(figsize=(10, 6))

    # Determine the range of block IDs for this unit
    min_block = unit_data['Block'].min()
    max_block = unit_data['Block'].max()

    # Loop through all possible block IDs (including those with zero spikes)
    for block_id in range(min_block, max_block + 1):
        block_data = unit_data[unit_data['Block'] == block_id]
        timestamps = block_data['Timestamp'] % block_size  # Normalize timestamps to block range
        y_positions = [block_id] * len(timestamps)  # Stack each block
        plt.scatter(timestamps, y_positions, s=marker_size)

    # Customize Plot
    plt.title(f'Raster Plot for {Unit} (Including Blocks with Zero Spikes)')
    plt.xlabel('Time (ms)')
    plt.ylabel('Block ID')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()

    # Save Plot
    plot_file = f'{output_folder}raster_plot_{Unit}.png'
    plt.savefig(plot_file)
    plt.show()

    print(f"Raster plot for {Unit} saved as '{plot_file}'.")
