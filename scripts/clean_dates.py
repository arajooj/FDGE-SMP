import re
import os

# Lista dos arquivos ou padrões de arquivos a limpar
files_to_clean = ["config1.properties", "config2.properties", "directory/config3.txt"]

# Expressão regular para encontrar as linhas de data e hora
pattern = re.compile(r"^\s*#\w{3}\s+\w{3}\s+\d{2}\s+\d{2}:\d{2}:\d{2}\s+BRT\s+\d{4}\s*$")

for file_name in files_to_clean:
    if os.path.exists(file_name):
        with open(file_name, 'r+') as file:
            lines = file.readlines()
            file.seek(0)
            file.truncate()
            for line in lines:
                if not pattern.match(line):
                    file.write(line)
