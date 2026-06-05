const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("jarvisDesktop", {
  notify: (payload) => ipcRenderer.invoke("jarvis:notify", payload),
  environment: () => ipcRenderer.invoke("jarvis:environment"),
});
