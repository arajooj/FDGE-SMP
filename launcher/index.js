const {
  getVersionList,
  install,
  installDependencies,
} = require("@xmcl/installer");
const { Version, diagnose, launch } = require("@xmcl/core");
const fs = require("fs").promises;
const path = require("path");
const { constants } = require("fs");

const MAX_RETRY_ATTEMPTS = 10;
const GAME_PATH = "./minecraft_game";
const GAME_VERSION = "1.20.1";
const JAVA2DOWN =
  "https://download.oracle.com/java/17/archive/jdk-17.0.9_windows-x64_bin.zip";

async function installGame() {
  const list = (await getVersionList()).versions;
  const aVersion = list.find((v) => v.id === GAME_VERSION);

  console.log("Iniciando instalação...");
  await install(aVersion, GAME_PATH);
  console.log("Jogo instalado com sucesso.");
}

async function installDep() {
  console.log("Instalando dependências...");
  const resolvedVersion = await Version.parse(GAME_PATH, GAME_VERSION);
  await installDependencies(resolvedVersion);
  console.log("Dependências instaladas com sucesso.");
}

async function startGame() {
  const javaPath =
    "Z:/Repositorios/Mine/FDGE-SMP/launcher/jdk-17.0.9/bin/java.exe";

  try {
    const proc = await launch({
      gamePath: GAME_PATH,
      javaPath: javaPath,
      version: GAME_VERSION,
    });
    console.log("Jogo iniciado!");
  } catch (error) {
    console.error("Erro ao iniciar o jogo:", error.message);
  }
}

async function gameExists() {
  try {
    await fs.access(GAME_PATH, constants.F_OK);
    return true;
  } catch {
    return false;
  }
}

async function main() {
  let gameInstalled = false;
  let depsInstalled = false;

  // Tenta instalar o jogo
  for (let attempt = 1; attempt <= MAX_RETRY_ATTEMPTS; attempt++) {
    try {
      if (!gameInstalled && !(await gameExists())) {
        await installGame();
      }
      gameInstalled = true;
      break;
    } catch (error) {
      console.error(`Erro ao instalar o jogo (Tentativa ${attempt}):`, error);
      if (attempt === MAX_RETRY_ATTEMPTS) {
        throw new Error(
          "Não foi possível instalar o jogo após várias tentativas."
        );
      }
    }
  }

  // Tenta instalar as dependências
  for (let attempt = 1; attempt <= MAX_RETRY_ATTEMPTS; attempt++) {
    try {
      if (!depsInstalled) {
        await installDep();
        depsInstalled = true;
      }
      break;
    } catch (error) {
      console.error(
        `Erro ao instalar as dependências (Tentativa ${attempt}):`,
        error
      );
      if (attempt === MAX_RETRY_ATTEMPTS) {
        throw new Error(
          "Não foi possível instalar as dependências após várias tentativas."
        );
      }
    }
  }

  // Se tudo estiver instalado, inicia o jogo
  if (gameInstalled && depsInstalled) {
    await startGame();
  }
}

main().catch((error) => console.error("Erro no processo:", error));
