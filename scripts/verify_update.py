import os
import hashlib
import requests
from colorama import init, Fore

init(autoreset=True)  # Inicializa o colorama

MODS_FOLDER_PATH = "Z:\\Repositorios\\Mine\\FDGE-SMP\\instances\\FDGE-SMP\\.minecraft\\mods"

def get_sha1_of_file(file_path):
    """Return the SHA1 hash of a file."""
    BUF_SIZE = 65536
    sha1 = hashlib.sha1()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()

def get_version_info(sha1):
    """Query the Modrinth API for version info using the SHA1 hash."""
    response = requests.get(f'https://api.modrinth.com/v2/version_file/{sha1}')
    if response.status_code == 200:
        return response.json()
    return None

def get_project_info(project_id):
    """Query the Modrinth API for project info using the project ID."""
    response = requests.get(f'https://api.modrinth.com/v2/project/{project_id}')
    if response.status_code == 200:
        return response.json()
    return None

def main():
    # Check if the provided path is valid
    if not os.path.exists(MODS_FOLDER_PATH) or not os.path.isdir(MODS_FOLDER_PATH):
        print("Caminho fornecido não é válido ou não é uma pasta.")
        return

    # Get a list of all files in the specified directory
    files = [os.path.join(MODS_FOLDER_PATH, f) for f in os.listdir(MODS_FOLDER_PATH) if os.path.isfile(os.path.join(MODS_FOLDER_PATH, f))]
    
    total_mods = len(files)
    analyzed_mods = 0
    mods_with_updates = 0
    mods_without_updates = 0

    for file in files:
        sha1 = get_sha1_of_file(file)
        version_info = get_version_info(sha1)
        if version_info:
            project_id = version_info['project_id']
            project_info = get_project_info(project_id)
            
            version_number = version_info['game_versions'][-1]
            
            if project_info:
                latest_game_version = project_info['game_versions'][-1]
                if latest_game_version != version_number:
                    mods_with_updates += 1
                else:
                    mods_without_updates += 1

            analyzed_mods += 1
            print(f"{Fore.YELLOW}Analisados: {analyzed_mods}/{total_mods} | {Fore.RED}Sem atualizacao: {mods_without_updates} | {Fore.GREEN}Tem atualizacao: {mods_with_updates}", end='\r')

    print()  # Print a newline at the end

if __name__ == '__main__':
    main()
