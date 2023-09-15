import json

# Define a function to load the configuration
# Assumes that the configuration file is in the same directory as this file
def load_config(file_path='config.json'):
    try:
        with open(file_path, 'r') as config_file:
            config = json.load(config_file)
        return config
    except FileNotFoundError:
        print(f"Config file not found at {file_path}. Make sure it exists.")
        return None
    except Exception as e:
        print(f"An error occurred while loading the config file: {e}")
        return None

if __name__ == '__main__':

    # Load the configuration
    config = load_config()

    # Check if the configuration was loaded successfully
    if config:
        # Access configuration values
        database_config = config["database"]
        file_paths = config["filePaths"]
        api_keys = config["apiKeys"]

        # Example usage
        print("Database Host:", database_config["host"])
