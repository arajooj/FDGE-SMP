import tkinter as tk
import requests
import os
import sys
import subprocess
from pkg_resources import parse_version
from portablemc.standard import Context, Version, VersionManifest, TooMuchParentsError, \
    JarNotFoundError
from portablemc.download import DownloadList
from portablemc.fabric import FabricVersion
from pathlib import Path
import time
import zipfile
import shutil
import tempfile


# Suponha que a versão atual do script seja um número de versão
# E que existe um endpoint onde você pode obter a última versão
VERSAO_ATUAL = "0.1.2"
GAME_VERSION = "1.20.1"
URL_BASE = "https://smp.fdge.com.br"
URL_VERIFICACAO = URL_BASE + "/launcher/latest.txt"
URL_ATUALIZACAO = URL_BASE + "/launcher/dist"

PATH_BASE = "C:/FDGE-SMP"
PATH_JAVA = PATH_BASE+"/java"
URL_JAVA = "https://download.oracle.com/java/17/archive/jdk-17.0.9_windows-x64_bin.zip"
SUBPATH_JAVA = "/jdk-17.0.9/bin/java.exe"

acao_atual = "Carregando..."


def download_and_extract_java():

    if os.path.exists(PATH_JAVA):
        return

    if not os.path.exists(PATH_JAVA):
        updateLabel(f"Criando pasta '{PATH_JAVA}'...", 1)
        os.makedirs(PATH_JAVA)
        updateLabel(f"Pasta '{PATH_JAVA}' criada com sucesso.", 1)
    else:
        updateLabel(f"A pasta '{PATH_JAVA}' já existe.", 1)

    # Corrigindo o caminho para obter o diretório temporário
    java_zip_path = os.path.join(tempfile.gettempdir(), "java.zip")

    updateLabel(f"Baixando Java...", 1)

    # Melhoria: adicionando tratamento de exceção e download mais eficiente
    try:
        # Baixa o arquivo
        with requests.get(URL_JAVA, stream=True) as response:
            response.raise_for_status()  # Lança um erro se o download falhar
            with open(java_zip_path, 'wb') as f:
                shutil.copyfileobj(response.raw, f)

        updateLabel(f"Java baixado. Iniciando extração...", 1)

        # Extrai o arquivo
        with zipfile.ZipFile(java_zip_path, 'r') as zip_ref:
            zip_ref.extractall(PATH_JAVA)

        updateLabel(f"Java extraído com sucesso.", 3)

    except requests.HTTPError as e:
        updateLabel(f"Erro ao baixar o Java: {e}", 3)
    except zipfile.BadZipFile as e:
        updateLabel(f"Arquivo zip corrompido: {e}", 3)
    except Exception as e:
        updateLabel(f"Erro desconhecido: {e}", 3)
    finally:
        # Remove o arquivo zip baixado após a extração se ele existir
        if os.path.exists(java_zip_path):
            os.remove(java_zip_path)


def verificar_instalar():
    # Verifica se todas as condições para "Instalar" são atendidas
    if (
        not os.path.exists(PATH_BASE) or
        not os.path.exists(PATH_BASE + "/.minecraft") or
        not os.path.exists(PATH_BASE + "/java") or
        not os.path.exists(PATH_BASE + "/version.txt")
    ):
        return True
    return False


def verificar_atualizar():
    try:
        # Obtenha a lista de tags do repositório
        resposta = requests.get(
            "https://api.github.com/repos/arajooj/FDGE-SMP-ModPack/tags")
        resposta.raise_for_status()  # Garante que a requisição foi bem-sucedida
        tags = resposta.json()
        ultima_tag = tags[0]['name']

        # Verifica se a versão da última tag é maior que a versão atual
        if parse_version(ultima_tag) > parse_version(VERSAO_ATUAL):
            with open(PATH_BASE + "/version.txt", "r") as arquivo:
                versao_instalada = arquivo.read().strip()
            if parse_version(ultima_tag) > parse_version(versao_instalada):
                return True
    except requests.RequestException as e:
        print(f"Erro ao verificar atualização: {e}")
    return False


def escolher_acao():
    global acao_atual
    if verificar_instalar():
        acao_atual = "Instalar"
    elif verificar_atualizar():
        acao_atual = "Atualizar"
    else:
        acao_atual = "Jogar"

    botao.config(text=acao_atual)


def verificar_atualizacao():
    try:
        resposta = requests.get(URL_VERIFICACAO)
        updateLabel(f"Verificando atualizações...", 1)

        ultima_versao = resposta.text.strip()
        updateLabel(f"Ultima versao: {ultima_versao}", 1)

        # Compara as versões utilizando a função parse_version
        if parse_version(ultima_versao) > parse_version(VERSAO_ATUAL):
            updateLabel(f"Nova versão disponível: {ultima_versao}", 1)
            resposta_exe = requests.get(
                f"{URL_ATUALIZACAO}/fdge-smp-launcher_v{ultima_versao}.exe"
            )
            novo_exe_path = "FDGE-SMP_Launcher.exe"
            updateLabel(f"Baixando nova versão...", 1)

            # Se um executável antigo existir, removê-lo
            if os.path.exists(novo_exe_path):
                updateLabel(f"Removendo versão antiga...", 1)
                os.remove(novo_exe_path)

            # Salva o novo executável
            with open(novo_exe_path, "wb") as arquivo:
                updateLabel(f"Salvando nova versão...", 1)
                arquivo.write(resposta_exe.content)

            # Renomear o executável atual para que possa ser deletado posteriormente se necessário
            updateLabel(f"Renomeando executável antigo...", 1)
            os.rename(sys.executable, "aplicativo_antigo.exe")

            # Reiniciar o aplicativo
            updateLabel(f"Reiniciando aplicativo...", 1)
            subprocess.Popen([novo_exe_path])
            sys.exit()  # Encerrar o aplicativo atual corretamente
        elif parse_version(ultima_versao) < parse_version(VERSAO_ATUAL):
            updateLabel("O aplicativo está atualizado. (Ate de mais 😒)", 1)
        else:
            updateLabel("O aplicativo está atualizado.")
    except requests.RequestException as e:
        updateLabel(f"Erro ao verificar atualizações: {e}", 3, "ERRO")


def updateLabel(text, delay, type="INFO"):
    def set_label_text():
        label_status.config(text=text)
        log(text, type)

    # Agendar a mudança de status após 'delay' milissegundos
    app.after(delay * 1000, set_label_text)


def log(text, type="INFO"):
    # Grava o texto no arquivo de log com o tipo especificado
    log_path = PATH_BASE + "/log.txt"
    with open(log_path, "a") as log_file:
        log_file.write(
            f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {type} - {text}\n")


def atualizar():
    try:
        # Obtenha a última tag do GitHub
        resposta = requests.get(
            "https://api.github.com/repos/arajooj/FDGE-SMP-ModPack/tags")
        resposta.raise_for_status()  # Garante que a requisição foi bem-sucedida
        tags = resposta.json()
        ultima_tag = tags[0]['name']
        url_download_tag = tags[0]['zipball_url']

        updateLabel(f"Baixando e atualizando para a versão {ultima_tag}...", 1)
        nome_arquivo = f"{ultima_tag}.zip"
        caminho_download = os.path.join(PATH_BASE, nome_arquivo)

        # Faz o download do zip da tag
        with requests.get(url_download_tag, stream=True) as r:
            with open(caminho_download, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

        # Define o caminho onde o arquivo zip será extraído temporariamente
        caminho_extracao_temp = os.path.join(PATH_BASE, "temp_extraction")

        # Cria o diretório temporário se ele não existir
        if not os.path.exists(caminho_extracao_temp):
            os.makedirs(caminho_extracao_temp)

        # Extrair o arquivo zip
        with zipfile.ZipFile(caminho_download, 'r') as zip_ref:
            zip_ref.extractall(caminho_extracao_temp)

        # Move os arquivos do diretório intermediário para o diretório .minecraft
        # Supondo que haja apenas um diretório no nível superior
        conteudo_temp = os.listdir(caminho_extracao_temp)
        caminho_intermediario = os.path.join(
            caminho_extracao_temp, conteudo_temp[0])

        caminho_destino = os.path.join(PATH_BASE, ".minecraft")

        # Move os arquivos para o destino correto, substituindo-os se já existirem
        for item in os.listdir(caminho_intermediario):
            s = os.path.join(caminho_intermediario, item)
            d = os.path.join(caminho_destino, item)
            if os.path.isdir(s):
                shutil.move(s, d)
            else:
                shutil.copy2(s, d)
                os.remove(s)

        # Exclui o diretório temporário
        shutil.rmtree(caminho_extracao_temp)

        # Exclui o arquivo .zip após a extração
        os.remove(caminho_download)

        # Atualiza o arquivo version.txt com a nova versão
        with open(os.path.join(PATH_BASE, "version.txt"), "w") as arquivo_versao:
            arquivo_versao.write(ultima_tag)

        updateLabel(f"Atualização para {ultima_tag} completa.", 3)

    except Exception as e:
        updateLabel(f"Erro durante a atualização: {e}", 3, "ERRO")

    global acao_atual
    if (verificar_atualizar()):
        acao_atual = "Atualizar"
    else:
        acao_atual = "Jogar"
    botao.config(text=acao_atual)


def instalar():
    # Implemente a lógica para a ação "Instalar" aqui
    # Exemplo de execução de comando para instalar usando o portablemc

    try:

        pontoMinecraft = PATH_BASE + "/.minecraft"
        updateLabel(f"Verificando pasta '{pontoMinecraft}'...", 1)

        # Verifica se a pasta já existe
        if not os.path.exists(pontoMinecraft):
            # Se não existir, cria a pasta
            os.mkdir(pontoMinecraft)
            updateLabel(f"Pasta '{pontoMinecraft}' criada com sucesso.", 1)

        else:
            updateLabel(f"A pasta '{pontoMinecraft}' já existe.", 1)

        context = Context(Path(pontoMinecraft))
        version = FabricVersion.with_fabric("1.20.1", context=context)
        updateLabel(f"Instalando...", 1)
        version.install()
        updateLabel(f"Instalado com sucesso.", 3)

        updateLabel(f"Verificando java...", 1)
        download_and_extract_java()
        updateLabel(f"Java baixado com sucesso.", 3)

    except Exception as e:
        label_status.config(text=f"Erro durante a instalação: {e}")

    if not os.path.exists(PATH_BASE + "/version.txt"):
        # crie o arquivo vestion.txt
        updateLabel(f"Criando arquivo 'version.txt'...", 1)
        with open(PATH_BASE + "/version.txt", "w") as arquivo:
            arquivo.write("0.0.0")
            updateLabel(f"Arquivo 'version.txt' criado com sucesso.", 1)
    else:
        updateLabel(f"Arquivo 'version.txt' já existe.", 1)

    global acao_atual
    if (verificar_atualizar()):
        acao_atual = "Atualizar"
    else:
        acao_atual = "Jogar"
    botao.config(text=acao_atual)


def jogar():
    # Implemente a lógica para a ação "Jogar" aqui
    # Exemplo de execução de comando para jogar usando o portablemc
    try:
        # Substitua 'SEU_COMANDO_DE_JOGAR' pelo comando real que você deseja executar
        updateLabel(f"Iniciando o jogo...", 1)

    except Exception as e:
        updateLabel(f"Erro ao iniciar o jogo: {e}", 3, "ERRO")


def executar_acao():
    if acao_atual == "Instalar":
        instalar()
    elif acao_atual == "Atualizar":
        atualizar()
    elif acao_atual == "Jogar":
        jogar()
    else:
        print("Ação desconhecida:", acao_atual)


# Inicia a interface gráfica do usuário se este script for o ponto de entrada principal
if __name__ == "__main__":
    app = tk.Tk()
    app.title("FDGE-SMP Launcher - v"+VERSAO_ATUAL)

    # Centralizar a janela
    window_width = app.winfo_reqwidth()
    window_height = app.winfo_reqheight()
    position_right = int(app.winfo_screenwidth()/2 - window_width/2)
    position_down = int(app.winfo_screenheight()/2 - window_height/2)
    app.geometry("+{}+{}".format(position_right, position_down))

    # Define um tamanho fixo para a janela
    app.geometry('350x250')  # Aumentei a altura para acomodar o botão
    app.resizable(False, False)

    label_status = tk.Label(app, text="Verificando por atualizações...")
    label_status.pack(side=tk.BOTTOM)  # Coloque a label no meio inferior

    # Crie um único botão com ação dinâmica
    botao = tk.Button(app, text=acao_atual, command=executar_acao)
    botao.pack()

    # Verifica se a pasta já existe
    if not os.path.exists(PATH_BASE):
        # Se não existir, cria a pasta
        os.mkdir(PATH_BASE)
        updateLabel(f"Pasta '{PATH_BASE}' criada com sucesso.", 1)
    else:
        updateLabel(f"A pasta '{PATH_BASE}' já existe.", 1)

    # Verificação de atualização automática
    app.after(100, verificar_atualizacao)

    app.after(300, escolher_acao)

    app.mainloop()
