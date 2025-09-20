#!/usr/bin/env node
import fs from "fs";
import inquirer from "inquirer";

const OUT_FILE = "../redacted_output.json";

function loadFindings() {
  if (!fs.existsSync(OUT_FILE)) {
    console.log("[!] No se encontró el JSON redacted. Ejecuta primero: python3 decrypt_and_redact.py");
    process.exit(1);
  }
  return JSON.parse(fs.readFileSync(OUT_FILE, "utf-8"));
}

async function chatLoop() {
  console.log("=== SmartCompute Secure Chat ===");
  const findings = loadFindings();

  while (true) {
    const { q } = await inquirer.prompt([{ type: "input", name: "q", message: "Tú:" }]);

    if (q.toLowerCase() === "exit") {
      console.log("Adiós 👋");
      break;
    }

    if (q.toLowerCase().includes("riesgo")) {
      console.log("🤖 SmartCompute: Riesgo detectado CRÍTICO en proceso sospechoso.");
      console.log("Sugerencia: Aislar host, recolectar Sysmon logs, bloquear proceso.");
    } else {
      console.log("🤖 SmartCompute: Resultado interpretado ->");
      console.dir(findings, { depth: null });
    }
  }
}

chatLoop();