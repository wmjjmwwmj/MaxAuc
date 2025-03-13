import re
import pandas as pd

import os
from datetime import datetime

# Define the path to your outputs directory
outputs_path = '.\outputs'

# Get all subdirectories under outputs
subdirectories = [d for d in os.listdir(outputs_path) if os.path.isdir(os.path.join(outputs_path, d))]

# Sort subdirectories by their modification time (or by their names assuming they are timestamps)
subdirectories.sort(key=lambda d: datetime.strptime(d, '%Y%m%d-%H%M%S'), reverse=True)

# Get the most recent subdirectory
latest_dir = subdirectories[0]

# Path to the latest _output_log file
file_path = os.path.join(outputs_path, latest_dir, '_output_.log')

print(f"The most recent _output_log file is located at: {file_path}")



# Initialize lists to store log data
robot_ids = []
timestamps = []
positions = []
actions = []
options = []

# Regular expression patterns for log entries
initial_position_pattern = r'(?P<timestamp>[\d-]+ [\d:,]+) - MainThread - INFO - (?P<robot_id>Robot-\d+) in \[(?P<x>\d+), (?P<y>\d+), 1\]'
move_pattern = r'(?P<timestamp>[\d-]+ [\d:,]+) - MainThread - INFO - (?P<robot_id>Robot-\d+) move to \[(?P<x>\d+), (?P<y>\d+), 1\]'

executed_pattern = re.compile(r"(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - .* - Execute option (?P<option>[\d_]+_[\d_]+)")

# Parse the log file
with open(file_path, 'r', encoding='utf-8') as file:
    for line in file:
        # Match initial positions
        initial_match = re.match(initial_position_pattern, line)
        if initial_match:
            timestamp = initial_match.group('timestamp')
            # Convert the timestamp to datetime object and format it to keep precision only to seconds
            timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S,%f').strftime('%Y-%m-%d %H:%M:%S')
            robot_id = initial_match.group('robot_id')
            x = int(initial_match.group('x'))
            y = int(initial_match.group('y'))
            
            robot_ids.append(robot_id)
            timestamps.append(timestamp)
            positions.append((x, y))
            actions.append('initial')
            options.append(None)
        
        # Match move actions
        move_match = re.match(move_pattern, line)
        if move_match:
            timestamp = move_match.group('timestamp')
            # Convert the timestamp to datetime object and format it to keep precision only to seconds
            timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S,%f').strftime('%Y-%m-%d %H:%M:%S')
            robot_id = move_match.group('robot_id')
            x = int(move_match.group('x'))
            y = int(move_match.group('y'))
            # option = move_match.group('option')
            
            robot_ids.append(robot_id)
            timestamps.append(timestamp)
            positions.append((x, y))
            actions.append('move')
            options.append(None)
        
        # Match executed actions
        executed_match = re.match(executed_pattern, line)
        if executed_match:
            timestamp = executed_match.group('timestamp')
            # Convert the timestamp to datetime object and format it to keep precision only to seconds
            timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S,%f').strftime('%Y-%m-%d %H:%M:%S')
            # robot_id = executed_match.group('robot_id')
            # x = int(executed_match.group('x'))
            # y = int(executed_match.group('y'))
            option = executed_match.group('option')
            
            robot_ids.append(robot_ids[-1])  # Use the last known robot ID
            timestamps.append(timestamp)
            positions.append(positions[-1])  # Use the last known position
            actions.append('finished')
            options.append(option)

# Create a dataframe to store the parsed data
log_df = pd.DataFrame({
    'timestamp': timestamps,
    'robot_id': robot_ids,
    'position': positions,
    'action': actions,
    'option': options
})


log_df['timestamp'] = pd.to_datetime(log_df['timestamp'])

# Get the start time (minimum timestamp)
start_time = log_df['timestamp'].min()

# Calculate relative time in seconds
log_df['timestamp'] = (log_df['timestamp'] - start_time).dt.total_seconds()


# Save the dataframe to a CSV file
csv_file_path = os.path.join(outputs_path, latest_dir, 'parsed_log_second.csv')
log_df.to_csv(csv_file_path, index=False)

print(f"Parsed log data has been saved to: {csv_file_path}")

# Display parsed data
# TODO 装不上ace_tools
# import ace_tools as tools; tools.display_dataframe_to_user(name="Robot Log Data", dataframe=log_df)

print(log_df.head())  # Show the first few rows of the parsed log data
