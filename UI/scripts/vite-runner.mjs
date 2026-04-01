import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { resolve } from "node:path";

const mode = process.argv[2] ?? "dev";

function esbuildPackageName() {
  if (process.platform === "win32") {
    if (process.arch === "x64") return "win32-x64";
    if (process.arch === "arm64") return "win32-arm64";
    return "win32-ia32";
  }
  if (process.platform === "darwin") {
    return process.arch === "arm64" ? "darwin-arm64" : "darwin-x64";
  }
  if (process.platform === "linux") {
    return process.arch === "arm64" ? "linux-arm64" : "linux-x64";
  }
  return "";
}

const esbuildPkg = esbuildPackageName();
const esbuildBinary = esbuildPkg
  ? resolve("node_modules", "@esbuild", esbuildPkg, process.platform === "win32" ? "esbuild.exe" : "bin/esbuild")
  : "";

const viteBin = resolve("node_modules", "vite", "bin", "vite.js");
const args = mode === "build" ? ["build"] : mode === "preview" ? ["preview"] : [];

const env = {
  ...process.env,
};

if (esbuildBinary && existsSync(esbuildBinary)) {
  env.ESBUILD_BINARY_PATH = esbuildBinary;
}

const child = spawn(process.execPath, [viteBin, ...args], {
  stdio: "inherit",
  env,
});

child.on("exit", (code) => {
  process.exit(code ?? 1);
});
