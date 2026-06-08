# Standalone Desktop Manual: How to Download, Install, and Run Lyra

This manual explains how to download, copy, and run the newly compiled, standalone **Lyra AI** desktop application on your Windows 11 laptop. 

We have packaged the entire project into a standard Windows Desktop Application directory. **There is no need to write terminal commands, run batch files, or manage raw code files anymore!** You simply click a single executable, and the app manages itself silently, complete with custom desktop shortcuts and a native **System Tray Icon (App Tray)** next to your clock.

---

## 📥 Step 1: Packaging and Transferring the App to Your Laptop

1. **Locate the Compiled App Folder**:
   * On your current system, navigate to:
     [frontend\dist\packaged\Lyra AI-win32-x64](file:///c:/sabari/Lyra/frontend/dist/packaged/Lyra%20AI-win32-x64)
   * This directory contains the standalone executable **`Lyra AI.exe`** (226 MB) and the silently bundled Python backend server resources.
2. **ZIP the App Folder**:
   * Right-click the folder **`Lyra AI-win32-x64`**, select **Send to** -> **Compressed (zipped) folder**, and name it `Lyra_AI.zip`.
3. **Transfer to Your Laptop**:
   * Copy the `Lyra_AI.zip` file onto a USB drive, external SSD, or share it across your network.
   * Paste it onto your laptop (for example, in your `C:\` drive or on your `Desktop`).
4. **Extract the App**:
   * Right-click `Lyra_AI.zip` and select **Extract All...** to unpack the files. You will now have a direct, standalone app folder named `Lyra AI-win32-x64` on your laptop.

---

## 🧠 Step 2: Set Up the Offline AI Engine (Ollama)
Because Lyra runs completely locally on your hardware to ensure absolute privacy, it connects to **Ollama** running on your laptop:

1. Download and run the Ollama installer from: [https://ollama.com/](https://ollama.com/) (Select **Download for Windows**).
2. Open a standard **Command Prompt** (cmd) from your Start Menu and run the following command to download your fast offline model:
   ```bash
   ollama run qwen2.5:1.5b
   ```
3. Once the download completes, you can close the command prompt. Ollama will continue running silently in your system tray background.

---

## 🚀 Step 3: Launching Lyra (The Normal App Experience!)

1. Open your extracted `Lyra AI-win32-x64` folder.
2. Double-click the file named **`Lyra AI.exe`** (the one with the custom logo icon!).
3. **The app will boot instantly**:
   * The Electron desktop user interface opens immediately.
   * **The FastAPI backend server is spawned silently in the background** — no separate Command Prompt or black terminal windows will ever appear on your desktop!

---

## 📥 Step 4: Adding to Your Windows Start Menu & Desktop Shortcuts

To make Lyra appear inside your standard system application lists:
1. Inside your `Lyra AI-win32-x64` folder, right-click **`Lyra AI.exe`** and select **Show more options** -> **Create shortcut**.
2. Rename the created shortcut to **`Lyra AI`**.
3. **Desktop Icon**: Drag this shortcut directly onto your Windows 11 Desktop!
4. **Start Menu & App List**:
   * Open your Start Menu and search bar.
   * Copy and paste the `Lyra AI` shortcut file into the following system folder:
     `C:\Users\<Your_Username>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs`
   * *Lyra will now appear in your Windows Start Menu, All Apps list, and app search results just like any normal installed program!*

---

## ⚙️ Step 5: Operating Lyra via the Windows System Tray

We have integrated a native **System Tray Icon (App Tray)** next to the system clock (bottom right of your taskbar):

* **Minimizing to the Background**:
  * Clicking the standard red **"X"** close button on the Lyra window **does not shut the app down**.
  * It simply hides and minimizes to the Windows System Tray.
  * This is a premium background running feature that allows the **Double-Clap and Voice Wake System** to remain active! You can double-clap and say "hai lyra" in your room, and the window will instantly restore on top of other apps!
* **Restoring the App Window**:
  * Double-click the Lyra icon (blue logo) next to the system clock.
  * Or, right-click the tray icon and select **"Restore Assistant"**.
* **Exiting the App Completely**:
  * To fully turn off the assistant and stop microphone background listening:
    1. Right-click the Lyra tray icon next to the system clock.
    2. Select **"Quit Lyra"**.
    3. Electron will automatically shut down and cleanly terminate the FastAPI backend server instantly.
