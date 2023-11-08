import tkinter as tk
import requests
import os
import sys
import subprocess

# Suponha que a versão atual do script seja um número de versão
# E que existe um endpoint onde você pode obter a última versão
VERSAO_ATUAL = "0.0.5"
URL_BASE = "https://smp.fdge.com.br"
URL_VERIFICACAO = URL_BASE + "/launcher/latest.txt"
URL_ATUALIZACAO = URL_BASE + "/launcher/dist"


def verificar_atualizacao():
    try:
        resposta = requests.get(URL_VERIFICACAO)
        ultima_versao = resposta.text.strip()

        if ultima_versao != VERSAO_ATUAL:
            resposta_exe = requests.get(
                f"{URL_ATUALIZACAO}/fdge-smp-launcher_v{ultima_versao}.exe"
            )
            novo_exe_path = "aplicativo_atualizado.exe"

            with open(novo_exe_path, "wb") as arquivo:
                arquivo.write(resposta_exe.content)

            # Substituir o executável atual pelo novo e reiniciar
            os.rename(sys.executable, "aplicativo_antigo.exe")
            os.rename(novo_exe_path, sys.executable)

            # Reiniciar o aplicativo
            subprocess.Popen([sys.executable])
            sys.exit()  # Certifique-se de encerrar o aplicativo atual corretamente
        else:
            label_status.config(text="O aplicativo está atualizado.")
    except requests.RequestException as e:
        label_status.config(text=f"Erro ao verificar atualizações: {e}")


# Inicia a interface gráfica do usuário se este script for o ponto de entrada principal
if __name__ == "__main__":
    app = tk.Tk()
    app.title("Verificador de Atualização")

    # Centralizar a janela
    window_width = app.winfo_reqwidth()
    window_height = app.winfo_reqheight()
    position_right = int(app.winfo_screenwidth()/2 - window_width/2)
    position_down = int(app.winfo_screenheight()/2 - window_height/2)
    app.geometry("+{}+{}".format(position_right, position_down))

    # Define um tamanho fixo para a janela
    app.geometry('300x200')
    app.resizable(False, False)

    label_status = tk.Label(app, text="Verificando por atualizações...")
    label_status.pack()

    # Verificação de atualização automática
    app.after(0, verificar_atualizacao)

    app.mainloop()
