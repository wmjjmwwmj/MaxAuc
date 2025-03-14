import os
from datetime import datetime

def latest_output_path(outputs_path : str = r".\outputs") -> str:
    # Get all subdirectories under outputs
    subdirectories = [d for d in os.listdir(outputs_path) if os.path.isdir(os.path.join(outputs_path, d))]

    # Sort subdirectories by their modification time (or by their names assuming they are timestamps)
    subdirectories.sort(key=lambda d: datetime.strptime(d, '%Y%m%d-%H%M%S'), reverse=True)

    # Get the most recent subdirectory
    latest_dir = subdirectories[0]

    # # Path to the latest _output_log file
    file_path = os.path.join(outputs_path, latest_dir, '_output_.log')

    return latest_dir, file_path
