# Standalone Installation & System Tray Manual: Lyra AI OS

This guide walks you through installing and using **Lyra AI**, now packaged as a standard Windows 11 Desktop Application Installer. There is no need to handle folders, write terminal commands, or copy source files. You simply run a standard installation wizard!

---

## 🚀 Step 1: Running the Installation Wizard
To install Lyra on your Windows 11 laptop:

1. **Transfer the Installer**:
   * Locate the compiled installer file named **`Lyra AI Setup.exe`** (found inside your `Lyra\frontend\dist\installer` directory).
   * Copy this single `.exe` file onto a USB thumb drive or share it with your laptop.
2. **Launch the Wizard**:
   * Double-click **`Lyra AI Setup.exe`** on your laptop.
   * *If Windows SmartScreen prompts an "Unrecognized App" message, click **"More info"** and then select **"Run anyway"**.*
3. **Complete Installation**:
   * Follow the standard setup wizard screens:
     1. Choose your preferred installation directory (defaults to your local app programs folder).
     2. Click **Install**.
     3. The installer will unpack the React application, the Electron shell, and the pre-configured FastAPI private server automatically.
     4. Click **Finish**.
4. **Shortcuts Added**:
   * The installer automatically creates a **Desktop Shortcut** ("Lyra AI") and a **Start Menu Shortcut**! You can search for "Lyra" in your Start Menu and launch it like a normal app.

---

## 🧠 Step 2: Set Up the Local Offline AI Engine
Because Lyra runs 100% locally and keeps your data private, it integrates with **Ollama** on your laptop:

1. Download and run the Ollama installer from: [https://ollama.com/](https://ollama.com/) (Select **Download for Windows**).
2. Open a **Command Prompt** (cmd) from your Start Menu and run the following command to download your high-speed offline model:
   ```bash
   ollama run qwen2.5:1.5b
   ```
3. Once the download finishes, you can close the command prompt. Ollama will run silently in your system background.

---

## 📥 Step 3: Operating Lyra via the Windows System Tray
We have integrated a native **System Tray Icon (App Tray)** next to the clock at the bottom right of your screen:

* **Background-Minimize Close (X)**:
  * When you click the standard red **"X"** close button on the top right of the Lyra window, the application **does not shut down**.
  * It simply hides and minimizes to your System Tray, running silently in the background.
  * This allows the **Double-Clap Wake System** to remain active! You can double-clap and say "hai lyra" at any time, and the window will instantly restore and focus on top of other apps!
* **Restoring the App manually**:
  * Double-click the Lyra icon (blue logo) inside your Windows System Tray next to the clock.
  * Or, right-click the System Tray icon and select **"Restore Assistant"**.
* **Closing the App permanently**:
  * To completely exit Lyra and turn off the microphone wake system:
    1. Locate the Lyra tray icon next to the system clock.
    2. Right-click the icon and select **"Quit Lyra"**.
    3. This safely kills the Electron interface and terminates the FastAPI backend processes instantly.
