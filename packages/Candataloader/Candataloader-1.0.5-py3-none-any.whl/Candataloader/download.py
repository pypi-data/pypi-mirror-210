import os
import shutil

# Define the dataset mapping
dataset_mapping = {
    'Survival': 'datasets/Survival Analysis Dataset for automobile IDS.csv',
    'SynCAN': 'datasets/SynCAN.csv',
    # Add more dataset names and their corresponding file paths
}

def download_dataset(dataset_names):
    # Get the current working directory
    current_directory = os.getcwd()

    # Iterate over the dataset names
    for dataset_name in dataset_names:
        if dataset_name in dataset_mapping:
            dataset_file_path = dataset_mapping[dataset_name]
            dataset_file_name = os.path.basename(dataset_file_path)
            destination_file_path = os.path.join(current_directory, dataset_file_name)
            
            # Copy the dataset file to the current directory
            shutil.copy(dataset_file_path, destination_file_path)
            print(f"Dataset '{dataset_name}' downloaded to '{destination_file_path}'.")
        else:
            print(f"Dataset '{dataset_name}' does not exist.")