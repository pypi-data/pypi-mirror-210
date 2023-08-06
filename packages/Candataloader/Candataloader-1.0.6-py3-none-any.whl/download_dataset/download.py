import shutil
import os
import json

def download_dataset(dataset_names):
    destination_path = os.getcwd()  # Get the current working directory
    
    with open('config.json') as config_file:
        config = json.load(config_file)
    
    for dataset_name in dataset_names:
        if dataset_name not in config['datasets']:
            raise ValueError(f"Dataset '{dataset_name}' not found in the configuration.")
        
        source_path = config['datasets'][dataset_name]
        dataset_destination_path = os.path.join(destination_path, dataset_name)
        
        shutil.copytree(source_path, dataset_destination_path)
        
        # Optional: Remove sensitive files or directories from the copied dataset
        
        # For example, if there is a 'private' directory in your local dataset
        # that should not be shared, you can remove it from the copied dataset
        private_dir = os.path.join(dataset_destination_path, 'private')
        if os.path.exists(private_dir):
            shutil.rmtree(private_dir)