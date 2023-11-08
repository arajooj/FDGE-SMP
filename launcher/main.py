import tkinter as tk
import requests
import os
import sys
import subprocess
from pkg_resources import parse_version

# Suponha que a versão atual do script seja um número de versão
# E que existe um endpoint onde você pode obter a última versão
VERSAO_ATUAL = "0.0.7"
URL_BASE = "https://smp.fdge.com.br"
URL_VERIFICACAO = URL_BASE + "/launcher/latest.txt"
URL_ATUALIZACAO = URL_BASE + "/launcher/dist"

acao_atual = "Carregando..."


def verificar_instalar():
    # Verifica se todas as condições para "Instalar" são atendidas
    if (
        not os.path.exists("C:/FDGE-SMP") or
        not os.path.exists("C:/FDGE-SMP/.minecraft") or
        not os.path.exists("C:/FDGE-SMP/java") or
        not os.path.exists("C:/FDGE-SMP/version.txt")
    ):
        return True
    return False


def verificar_atualizar():
    try:
        resposta = requests.get(
            "https://github.com/arajooj/FDGE-SMP-ModPack/releases/latest")
        ultima_versao_repo = resposta.url.split("/")[-1]

        if parse_version(ultima_versao_repo) > parse_version(VERSAO_ATUAL):
            with open("C:/FDGE-SMP/version.txt", "r") as arquivo:
                versao_instalada = arquivo.read().strip()
            if parse_version(ultima_versao_repo) > parse_version(versao_instalada):
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
        ultima_versao = resposta.text.strip()

        # Compara as versões utilizando a função parse_version
        if parse_version(ultima_versao) > parse_version(VERSAO_ATUAL):
            resposta_exe = requests.get(
                f"{URL_ATUALIZACAO}/fdge-smp-launcher_v{ultima_versao}.exe"
            )
            novo_exe_path = "FDGE-SMP Launcher.exe"

            # Se um executável antigo existir, removê-lo
            if os.path.exists(novo_exe_path):
                os.remove(novo_exe_path)

            # Salva o novo executável
            with open(novo_exe_path, "wb") as arquivo:
                arquivo.write(resposta_exe.content)

            # Renomear o executável atual para que possa ser deletado posteriormente se necessário
            os.rename(sys.executable, "aplicativo_antigo.exe")

            # Reiniciar o aplicativo
            subprocess.Popen([novo_exe_path])
            sys.exit()  # Encerrar o aplicativo atual corretamente
        elif parse_version(ultima_versao) < parse_version(VERSAO_ATUAL):
            label_status.config(
                text="O aplicativo está atualizado. (Ate de mais 😒)")
        else:
            label_status.config(text="O aplicativo está atualizado.")
    except requests.RequestException as e:
        label_status.config(text=f"Erro ao verificar atualizações: {e}")


def atualizar():
    # Implemente a lógica para a ação "Atualizar" aqui
    print("clicou em atualizar")
    pass


def instalar():
    # Implemente a lógica para a ação "Instalar" aqui
    print("clicou em instalar")
    pass


def jogar():
    # Implemente a lógica para a ação "Jogar" aqui
    print("clicou em jogar")
    pass


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

    # Verificação de atualização automática
    app.after(100, verificar_atualizacao)

    app.after(300, escolher_acao)

    app.mainloop()
