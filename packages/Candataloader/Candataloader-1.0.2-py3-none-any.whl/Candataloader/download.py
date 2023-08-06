import os
import requests

# Define the dataset mapping
dataset_mapping = {
    'Survival': 'Survival Analysis Dataset for automobile IDS.csv',
    'SynCan': 'SynCAN.csv',
    # Add more dataset names and their corresponding URLs
}

def download_dataset(dataset_names):
    current_directory = os.getcwd()

    if isinstance(dataset_names, str):
        dataset_names = [dataset_names]

    for dataset_name in dataset_names:
        if dataset_name in dataset_mapping:
            url = dataset_mapping[dataset_name]
            filename = os.path.basename(url)

            file_path = os.path.join(current_directory, filename)
            response = requests.get(url, stream=True)

            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
        else:
            print(f"Dataset '{dataset_name}' is not available.")
