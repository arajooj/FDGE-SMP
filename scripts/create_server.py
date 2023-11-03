import os
import shutil
import fnmatch

# Caminhos das pastas A e B
pasta_A = r'Z:\Repositorios\Mine\FDGE-SMP\instances\FDGE-SMP\.minecraft'
pasta_B = r'Z:\Repositorios\Mine\FDGE-SMP\servers'

# Listas dos arquivos e pastas específicas que você quer copiar
arquivos_para_copiar = ['ops.json']
pastas_para_copiar = ['automodpack', 'config', 'emotes',
                      'kubejs', 'patchouli_books']  # 'mods' é tratada separadamente

# Prefixos dos arquivos dentro da pasta mods que NÃO devem ser copiados
# Excluirá todos os arquivos que começam com 'mcwifipnp'
mods_prefixos_para_excluir = ['mcwifipnp']

# Versão fixa para o nome da pasta
versao_fixa = "v0.1.7.1"

# Nome da pasta de destino versionada
pasta_destino_versionada = os.path.join(pasta_B, versao_fixa)

# Cria a pasta versionada se ela não existir
if not os.path.exists(pasta_destino_versionada):
    os.makedirs(pasta_destino_versionada)

# Função para copiar conteúdo da pasta 'mods' excluindo arquivos baseados em prefixos


def copiar_pasta_mods_com_exclusao_por_prefixo(origem, destino, prefixos_excluidos):
    if not os.path.exists(destino):
        os.makedirs(destino)
    for item in os.listdir(origem):
        # Verifica se o item começa com algum prefixo para exclusão
        if not any(fnmatch.fnmatch(item, prefixo + '*') for prefixo in prefixos_excluidos):
            s = os.path.join(origem, item)
            d = os.path.join(destino, item)
            if os.path.isfile(s):
                shutil.copy2(s, d)


# Copiando os arquivos e pastas
for arquivo in arquivos_para_copiar:
    caminho_origem = os.path.join(pasta_A, arquivo)
    caminho_destino = os.path.join(pasta_destino_versionada, arquivo)
    if os.path.exists(caminho_origem):
        shutil.copy2(caminho_origem, caminho_destino)

for pasta in pastas_para_copiar:
    caminho_origem = os.path.join(pasta_A, pasta)
    caminho_destino = os.path.join(pasta_destino_versionada, pasta)
    if os.path.isdir(caminho_origem):
        shutil.copytree(caminho_origem, caminho_destino, dirs_exist_ok=True)

# Copiando a pasta 'mods' com exclusões baseadas em prefixos
caminho_pasta_mods_origem = os.path.join(pasta_A, 'mods')
caminho_pasta_mods_destino = os.path.join(pasta_destino_versionada, 'mods')
copiar_pasta_mods_com_exclusao_por_prefixo(
    caminho_pasta_mods_origem, caminho_pasta_mods_destino, mods_prefixos_para_excluir)

print("Todos os arquivos e pastas especificados foram processados, com exceção dos mods excluídos.")
