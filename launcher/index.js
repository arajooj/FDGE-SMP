const {
  getVersionList,
  install,
  installDependencies,
  installFabric,
  getYarnArtifactListFor,
  getLoaderArtifactList,
} = require("@xmcl/installer");

const { getLoaderArtifactListFor } = require("@xmcl/installer");
const { Version, diagnose, launch } = require("@xmcl/core");
const {
  ModrinthV2Client,
  ProjectVersion,
  getProjectVersions,
} = require("@xmcl/modrinth");
const path = require("path");
const { constants } = require("fs");
const os = require("os");
const fs = require("fs");
const fsp = require("fs").promises; // Use isso para métodos baseados em promessas
const axios = require("axios");
const extract = require("extract-zip");

let FABRIC_VERSION = "";
const MAX_RETRY_ATTEMPTS = 10;
const GAME_PATH = "C:/FDGE-SMP/.minecraft";
const JAVA_PATH = "C:/FDGE-SMP/java";
const GAME_VERSION = "1.20.1";
const JAVA2DOWN =
  "https://download.oracle.com/java/17/archive/jdk-17.0.9_windows-x64_bin.zip";
const MODS_URL = "https://files.fdge.com.br/api/public/dl/tC8zLyZf/";
const MODS_PATH = path.join(GAME_PATH, "mods");

async function tryInstallFabric() {
  // Substitua 'yourMinecraftVersion' pela versão do Minecraft que deseja usar
  const minecraftVersion = GAME_VERSION;

  console.log(
    `Obtendo lista de artefatos do Fabric Loader para o Minecraft ${minecraftVersion}...`
  );
  const loaderArtifacts = await getLoaderArtifactListFor(minecraftVersion);

  // Escolher a versão mais recente do Fabric Loader, ou uma específica se necessário
  const latestLoaderArtifact = loaderArtifacts[0];

  console.log(
    `Instalando Fabric Loader versão ${latestLoaderArtifact.loader.version}...`
  );
  const minecraftLocation = GAME_PATH.toString();

  let installedVersionId;
  try {
    console.log("Instalando Fabric...");
    installedVersionId = await installFabric(
      latestLoaderArtifact,
      minecraftLocation
    );

    FABRIC_VERSION = installedVersionId;
  } catch (error) {
    console.error("Erro ao instalar o Fabric:", error);
  }

  // Após instalar o Fabric, você precisa instalar as dependências.
  console.log("Instalando dependências do Fabric...");
  const resolvedVersion = await Version.parse(
    minecraftLocation,
    installedVersionId
  );
  await installDependencies(resolvedVersion);

  console.log("Fabric instalado com sucesso.");
}

function delay(duration) {
  return new Promise((resolve) => setTimeout(resolve, duration));
}

async function downloadAndExtractMods(modsUrl, modsPath) {
  console.log("Baixando mods...");

  // Define o caminho do arquivo zip temporário
  const modsZipPath = path.join(os.tmpdir(), "mods.zip");

  // Baixa o arquivo
  const response = await axios({
    method: "GET",
    url: modsUrl,
    responseType: "stream",
  });

  // Salva o arquivo no caminho temporário
  const writer = response.data.pipe(fs.createWriteStream(modsZipPath));
  await new Promise((resolve, reject) => {
    writer.on("finish", resolve);
    writer.on("error", reject);
  });

  console.log("Mods baixados. Iniciando extração...");

  // Cria a pasta mods se ela não existir
  if (!fs.existsSync(modsPath)) {
    fs.mkdirSync(modsPath, { recursive: true });
  }

  // Extrai o arquivo dentro da pasta mods
  await extract(modsZipPath, { dir: path.resolve(modsPath) });

  console.log("Mods extraídos com sucesso.");
}

// Função para baixar o Java
async function downloadJava() {
  console.log("Baixando Java...");
  const javaZipPath = path.join(os.tmpdir(), "java.zip");

  // Baixa o arquivo
  const response = await axios({
    method: "GET",
    url: JAVA2DOWN,
    responseType: "stream",
  });

  // Salva o arquivo no caminho temporário
  const writer = response.data.pipe(fs.createWriteStream(javaZipPath));
  await new Promise((resolve, reject) => {
    writer.on("finish", resolve);
    writer.on("error", reject);
  });

  console.log("Java baixado. Iniciando extração...");
  await extract(javaZipPath, { dir: path.resolve(JAVA_PATH) });
  console.log("Java extraído com sucesso.");
}

// Atualize as chamadas para fs.promises para usar fsp quando necessário
// Por exemplo, em sua função gameExists, faça o seguinte:
async function gameExists() {
  try {
    await fsp.access(GAME_PATH, fs.constants.F_OK);
    return true;
  } catch {
    return false;
  }
}

async function isJavaDownloaded() {
  try {
    console.log(path.join(JAVA_PATH, "jdk-17.0.9", "bin", "java.exe"));
    if (
      !(await fsp.access(
        path.join(JAVA_PATH, "jdk-17.0.9", "bin", "java.exe"),
        constants.F_OK
      ))
    ) {
      console.log("Java já baixado.");
      return true;
    }
    return false;
  } catch {
    return false;
  }
}

async function installGame() {
  const list = (await getVersionList()).versions;
  const aVersion = list.find((v) => v.id === GAME_VERSION);

  console.log("Iniciando instalação...");
  try {
    await install(aVersion, GAME_PATH);
  } catch (error) {
    console.log("Erro ao instalar o jogo, tentando novamente...");
  }
  console.log("Jogo instalado com sucesso.");
}

async function installDep() {
  console.log("Instalando dependências...");
  const resolvedVersion = await Version.parse(GAME_PATH, GAME_VERSION);
  try {
    await installDependencies(resolvedVersion);
  } catch (error) {
    console.log("Erro ao instalar as dependências, tentando novamente...");
  }

  console.log("Dependências instaladas com sucesso.");
}

async function startGame() {
  try {
    const proc = await launch({
      gamePath: GAME_PATH,
      javaPath: "C:/FDGE-SMP/java/jdk-17.0.9/bin/java.exe",
      version: FABRIC_VERSION || GAME_VERSION,
    });
    console.log("Jogo iniciado!");
  } catch (error) {
    console.error("Erro ao iniciar o jogo:", error.message);
  }
}

async function gameExists() {
  try {
    await fsb.access(GAME_PATH, constants.F_OK);
    return true;
  } catch {
    return false;
  }
}

async function main() {
  let gameInstalled = false;
  let depsInstalled = false;
  let fabricInstalled = false;
  let modsDownloaded = false;

  // Verifica se o Java já está baixado
  if (!(await isJavaDownloaded())) {
    await downloadJava();
  }

  // Tenta instalar o jogo
  if (!gameInstalled && !(await gameExists())) {
    try {
      await installGame();
      gameInstalled = true;
    } catch (error) {
      console.error("Erro ao instalar o jogo:", error);
      throw new Error("Não foi possível instalar o jogo.");
    }
  }

  // Tenta instalar as dependências
  if (!depsInstalled) {
    try {
      await installDep();
      depsInstalled = true;
    } catch (error) {
      console.error("Erro ao instalar as dependências:", error);
      throw new Error("Não foi possível instalar as dependências.");
    }
  }

  // Tenta instalar o Fabric
  if (!fabricInstalled) {
    try {
      console.log("Instalando Fabric...");
      await tryInstallFabric();
      fabricInstalled = true; // Certifique-se de definir isso após uma instalação bem-sucedida
    } catch (error) {
      console.error("Erro ao instalar o Fabric:", error);
      throw new Error("Não foi possível instalar o Fabric.");
    }
  }

  // Tenta baixar e extrair os mods
  if (fabricInstalled && !modsDownloaded) {
    try {
      await downloadAndExtractMods(MODS_URL, MODS_PATH);
      modsDownloaded = true;
    } catch (error) {
      console.error("Erro ao baixar ou extrair os mods:", error);
      throw new Error("Não foi possível baixar ou extrair os mods.");
    }
  }

  // Se tudo estiver instalado, inicia o jogo
  if (gameInstalled && depsInstalled && fabricInstalled && modsDownloaded) {
    try {
      await startGame();
    } catch (error) {
      console.error("Erro ao iniciar o jogo:", error);
      throw new Error("Não foi possível iniciar o jogo.");
    }
  }
}

// Inicia o processo
main().catch((error) => console.error("Erro no processo:", error));
