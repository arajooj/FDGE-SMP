const { getVersionList, install } = require("@xmcl/installer");
const { Version, diagnose, launch } = require("@xmcl/core");
const readline = require("readline");

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

const gamePath = "./minecraft_game";
const GAME_VERSION = "1.20.2";

async function installGame() {
  const list = (await getVersionList()).versions;
  const aVersion = list.find((v) => v.id === GAME_VERSION);

  console.log("Iniciando instalação...");
  await install(aVersion, gamePath);
  console.log("Jogo instalado com sucesso.");
}

async function diagnoseGame() {
  const resolvedVersion = await Version.parse(gamePath, GAME_VERSION);
  const report = await diagnose(
    resolvedVersion.id,
    resolvedVersion.minecraftDirectory
  );

  const issues = report.issues;

  for (let issue of issues) {
    switch (issue.role) {
      case "minecraftJar":
        console.error("Problema detectado com o arquivo JAR do Minecraft.");
        break;
      case "versionJson":
        console.error("Problema detectado com o JSON da versão.");
        break;
      case "library":
        console.error(
          "Uma ou mais bibliotecas estão faltando ou estão corrompidas."
        );
        break;
      case "assets":
        console.error("Alguns assets estão faltando ou estão corrompidos.");
        break;
      default:
        console.error("Problema desconhecido detectado.");
        break;
    }
  }
}

async function checkAndUpdateGame() {
  const resolvedVersion = await Version.parse(gamePath, GAME_VERSION);
  const report = await diagnose(
    resolvedVersion.id,
    resolvedVersion.minecraftDirectory
  );

  const issues = report.issues;

  if (issues.length === 0) {
    console.log("Tudo parece estar em ordem com o jogo!");
    return;
  }

  console.log("Detectados problemas com o jogo. Tentando corrigir...");

  for (let issue of issues) {
    switch (issue.role) {
      case "minecraftJar":
      case "versionJson":
      case "library":
      case "assets":
        console.log(`Corrigindo ${issue.role}...`);
        await install({ id: GAME_VERSION, type: "release" }, gamePath);
        break;
    }
  }

  console.log(
    "Problemas corrigidos. Você pode tentar iniciar o jogo novamente."
  );
}

async function startGame() {
  const javaPath = "java";

  try {
    const proc = await launch({
      gamePath: gamePath,
      javaPath: javaPath,
      version: GAME_VERSION,
    });
    console.log("Jogo iniciado!");
  } catch (error) {
    console.error("Erro ao iniciar o jogo:", error.message);
    await diagnoseGame();
  }
}

rl.question(
  "Digite 1 para instalar, 2 para iniciar o jogo, 3 para verificar e corrigir arquivos: ",
  function (input) {
    switch (input) {
      case "1":
        installGame();
        break;
      case "2":
        startGame();
        break;
      case "3":
        checkAndUpdateGame();
        break;
      default:
        console.log("Opção inválida.");
        break;
    }
    rl.close();
  }
);
