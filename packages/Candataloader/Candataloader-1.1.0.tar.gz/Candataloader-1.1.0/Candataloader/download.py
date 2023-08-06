import os
import requests

def download_dataset(dataset_name):
    dataset_mapping = {
        'Survival': 'https://53a9-203-205-29-5.ngrok-free.app/Survival Analysis Dataset for automobile IDS.csv',
        'SynCAN': 'https://53a9-203-205-29-5.ngrok-free.app/SynCAN.csv',
        # Add more dataset URLs as needed
    }

    if dataset_name not in dataset_mapping:
        print(f"Dataset '{dataset_name}' is not available for download.")
        return

    url = dataset_mapping[dataset_name]
    filename = url.split('/')[-1]  # Extract the filename from the URL
    current_dir = os.getcwd()  # Get the current directory path

    file_path = os.path.join(current_dir, filename)

    try:
        response = requests.get(url)
        response.raise_for_status()

        with open(file_path, 'wb') as file:
            file.write(response.content)

        print(f"Dataset '{dataset_name}' downloaded successfully to '{file_path}'.")
    except requests.exceptions.HTTPError as err:
        print(f"Error downloading dataset '{dataset_name}': {err}")
    except Exception as err:
        print(f"An error occurred while downloading dataset '{dataset_name}': {err}")

