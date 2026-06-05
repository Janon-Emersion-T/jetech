const { app, BrowserWindow, ipcMain, Notification } = require("electron");
const path = require("path");
const fs = require("fs");

const distIndex = path.join(__dirname, "../dist/index.html");
let mainWindow;

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
    backgroundColor: "#08111b",
    title: "Jarvis v2",
    webPreferences: {
      preload: path.join(__dirname, "preload.cjs"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  const entry = resolveEntry();
  if (entry.type === "file") {
    mainWindow.loadFile(entry.value);
  } else {
    mainWindow.loadURL(entry.value);
  }
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
  createWindow();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
