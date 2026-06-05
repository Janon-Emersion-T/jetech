const { app, BrowserWindow, ipcMain, Notification } = require("electron");
const path = require("path");
const fs = require("fs");

const appRoot = path.join(__dirname, "../..");
const logDir = path.join(appRoot, "runtime", "logs");
const desktopLogPath = path.join(logDir, "desktop-ui.log");
const distIndex = path.join(__dirname, "../dist/index.html");
let mainWindow;
let appIsQuitting = false;

fs.mkdirSync(logDir, { recursive: true });

function writeDesktopLog(message) {
  const line = `[${new Date().toISOString()}] ${message}\n`;
  fs.appendFileSync(desktopLogPath, line);
}

function resolveEntry() {
  if (fs.existsSync(distIndex)) {
    return { type: "file", value: distIndex };
  }
  return { type: "url", value: "http://127.0.0.1:5173" };
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1480,
    height: 940,
    minWidth: 1180,
    minHeight: 760,
    show: false,
    backgroundColor: "#08111b",
    title: "Jarvis v2",
    webPreferences: {
      preload: path.join(__dirname, "preload.cjs"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  const entry = resolveEntry();
  writeDesktopLog(`Loading desktop entry: ${entry.type}:${entry.value}`);
  if (entry.type === "file") {
    mainWindow.loadFile(entry.value);
  } else {
    mainWindow.loadURL(entry.value);
  }

  mainWindow.once("ready-to-show", () => {
    writeDesktopLog("Desktop window ready to show.");
    mainWindow.show();
    mainWindow.focus();
  });

  mainWindow.on("close", (event) => {
    if (!appIsQuitting) {
      event.preventDefault();
      writeDesktopLog("Desktop window hidden instead of closing.");
      mainWindow.hide();
    }
  });

  mainWindow.webContents.on("did-fail-load", (_, errorCode, errorDescription) => {
    writeDesktopLog(`Renderer failed to load: ${errorCode} ${errorDescription}`);
  });

  mainWindow.webContents.on("render-process-gone", (_, details) => {
    writeDesktopLog(`Renderer process gone: ${JSON.stringify(details)}`);
  });

  mainWindow.webContents.on("console-message", (_, level, message, line, sourceId) => {
    writeDesktopLog(`Renderer console [${level}] ${sourceId}:${line} ${message}`);
  });
}

ipcMain.handle("jarvis:notify", async (_, payload) => {
  if (!Notification.isSupported()) {
    return { ok: false };
  }
  new Notification({
    title: payload?.title || "Jarvis",
    body: payload?.body || "",
  }).show();
  return { ok: true };
});

ipcMain.handle("jarvis:environment", async () => ({
  brainApiUrl: process.env.JARVIS_BRAIN_API_URL || "http://127.0.0.1:8000",
}));

app.whenReady().then(() => {
  writeDesktopLog("Electron app ready.");
  createWindow();
});

app.on("window-all-closed", () => {
  writeDesktopLog("window-all-closed received.");
});

app.on("before-quit", () => {
  appIsQuitting = true;
  writeDesktopLog("before-quit received.");
});

app.on("activate", () => {
  if (!mainWindow) {
    writeDesktopLog("Recreating desktop window on activate.");
    createWindow();
    return;
  }
  mainWindow.show();
  mainWindow.focus();
});

process.on("uncaughtException", (error) => {
  writeDesktopLog(`Uncaught exception: ${error.stack || error.message}`);
});

process.on("unhandledRejection", (reason) => {
  writeDesktopLog(`Unhandled rejection: ${reason?.stack || reason}`);
});
