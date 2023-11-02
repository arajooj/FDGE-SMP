import re
import subprocess

# Expressão regular para encontrar as linhas de data e hora gerais
general_pattern = re.compile(
    r"^\s*#\w{3}\s+\w{3}\s+\d{2}\s+\d{2}:\d{2}:\d{2}\s+BRT\s+\d{4}\s*$")
# Expressões regulares para as linhas específicas do arquivo instance.cfg
specific_patterns = {
    'lastLaunchTime': re.compile(r'^lastLaunchTime=\d+$'),
    'lastTimePlayed': re.compile(r'^lastTimePlayed=\d+$'),
    'totalTimePlayed': re.compile(r'^totalTimePlayed=\d+$'),
}

# Caminho para o arquivo específico
specific_file_path = 'instances/FDGE-SMP/instance.cfg'

# Obtém a lista de arquivos modificados que estão staged
staged_files = subprocess.check_output(
    ['git', 'diff', '--name-only', '--cached'], text=True).splitlines()

# Processa cada arquivo
files_cleaned = False
for file_name in staged_files:
    cleaned = False
    with open(file_name, 'r+') as file:
        lines = file.readlines()
        file.seek(0)
        file.truncate()
        for line in lines:
            if file_name.endswith('instance.cfg'):
                if not any(pattern.match(line) for pattern in specific_patterns.values()):
                    file.write(line)
                else:
                    cleaned = True
            else:
                if not general_pattern.match(line):
                    file.write(line)
                else:
                    cleaned = True
        file.truncate()
    if cleaned:
        print(f"Limpeza realizada em: {file_name}")
        files_cleaned = True

# Restage files se eles foram alterados
if files_cleaned:
    subprocess.call(['git', 'add'] + staged_files)
