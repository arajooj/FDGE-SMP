import subprocess
import shutil
import os

# Importe a versão atual do seu script principal
from main import VERSAO_ATUAL

NOME_BASE_ARQUIVO = f"fdge-smp-launcher_v{VERSAO_ATUAL}.exe"
CAMINHO_DESTINO = "Z:\\Docker\\nginx\\fdge_smp\\public\\launcher\\dist"
CAMINHO_ARQUIVO_VERSAO = "Z:\\Docker\\nginx\\fdge_smp\\public\\launcher\\latest.txt"
# Substitua pelo nome do seu script principal, se for diferente
SCRIPT_PYTHON = "main.py"


def build_executable():
    # Constrói o executável
    subprocess.check_call(
        ['pyinstaller', '--onefile', '--windowed', '--noconsole', SCRIPT_PYTHON])

    # O nome do executável gerado pelo PyInstaller será o nome do script com '.exe'
    caminho_executavel = os.path.join(
        'dist', SCRIPT_PYTHON.replace('.py', '.exe'))

    # Renomeia para a versão correta
    caminho_final_executavel = os.path.join('dist', NOME_BASE_ARQUIVO)
    os.rename(caminho_executavel, caminho_final_executavel)

    if os.path.isfile(caminho_final_executavel):
        # Mover o executável para o local desejado
        shutil.move(caminho_final_executavel, os.path.join(
            CAMINHO_DESTINO, NOME_BASE_ARQUIVO))
        print(
            f"Executável movido para: {os.path.join(CAMINHO_DESTINO, NOME_BASE_ARQUIVO)}")

        # Atualiza o arquivo de versão
        with open(CAMINHO_ARQUIVO_VERSAO, 'w') as f:
            f.write(VERSAO_ATUAL)
        print(f"Arquivo de versão atualizado para: {VERSAO_ATUAL}")
    else:
        print("Não foi possível encontrar o executável após o build. Verifique se o PyInstaller funcionou corretamente.")


if __name__ == "__main__":
    build_executable()
