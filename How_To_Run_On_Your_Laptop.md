# How to Download, Install, and Run Lyra on Your Windows 11 Laptop

This guide provides simple, step-by-step instructions to download and run the **Lyra AI Operating Platform** locally on your Windows 11 laptop. Because Lyra is an offline-first assistant, it runs entirely on your own hardware, guaranteeing absolute privacy and zero latency.

---

## 🛠️ Step 1: Install the Prerequisites
Before transferring Lyra, make sure your Windows 11 laptop has the three core tools installed:

1. **Node.js (LTS Version)**:
   * **Purpose**: Compiles and runs the beautiful glassmorphic desktop interface.
   * **Download**: [https://nodejs.org/](https://nodejs.org/) (Select the **LTS** version).
   * **Installation**: Run the installer and click "Next" through all defaults.

2. **Python (Version 3.10 or Higher)**:
   * **Purpose**: Orchestrates the local task executors, image creation systems, and WebSocket routers.
   * **Download**: [https://www.python.org/downloads/](https://www.python.org/downloads/) (Select the latest release).
   * **Installation**: 
     * > [!IMPORTANT]
     * > **CRITICAL STEP**: During the Python installation setup, check the box that says **"Add python.exe to PATH"** before clicking install. If this is missed, Windows won't be able to run Python from scripts.

3. **Ollama (Local AI Engine)**:
   * **Purpose**: Runs high-speed local AI models offline, powering all text-based intelligence in Lyra.
   * **Download**: [https://ollama.com/download](https://ollama.com/download) (Select **Download for Windows**).
   * **Installation**: Run the installer. It will launch as a background utility (look for the llama icon in your Windows taskbar tray).

---

## 📁 Step 2: Download and Transfer the Project Folder
To get the Lyra project files onto your laptop:

1. **On your current system**:
   * Navigate to your file explorer and locate the `Lyra` project folder (located at `c:\sabari\Lyra`).
   * Right-click the `Lyra` folder, select **Compress to ZIP file**, and name it `Lyra.zip`.
2. **Transfer to your Laptop**:
   * Copy the `Lyra.zip` file onto a USB thumb drive, external SSD, or share it via local network sharing (like Windows Nearby Share).
   * Paste it onto your laptop (for example, in your `C:\` directory or `C:\Users\YourName\Documents`).
3. **Extract the Files**:
   * Right-click `Lyra.zip` and select **Extract All...** to unpack the project files into a folder named `Lyra`.

---

## 🧠 Step 3: Download your Local AI Model
Lyra is configured to connect to Ollama. Let's pull a fast, lightweight, and highly capable model:

1. Open your Windows 11 Start Menu, search for **Command Prompt** (cmd), and open it.
2. In the terminal window, run the following command to download and activate the model:
   ```bash
   ollama run qwen2.5:1.5b
   ```
3. Once the download completes, you will see a chat prompt. You can close the Command Prompt window now — Ollama will continue running silently in the background!

---

## 🚀 Step 4: Run Lyra with 1-Click!
We have built an automated, zero-configuration master launcher to do all heavy lifting:

1. Open your extracted `Lyra` project directory.
2. Locate the file named **`Launch_Lyra.bat`** (the master launcher).
3. **Double-click `Launch_Lyra.bat`** to start!
   * **What happens on the FIRST RUN**: The script will detect that this is a new laptop installation. It will automatically build a Python virtual environment, download the necessary libraries, and download the frontend packages. *This first-time setup takes 1–3 minutes depending on your internet connection.*
   * **What happens on SUBSEQUENT RUNS**: The script instantly skips setup, performs rapid pre-flight safety checks, and boots the backend server and desktop app in under 3 seconds!

---

## 💡 Quick Troubleshooting
* **Error: Node.js / Python is not installed**: If the console window turns red and halts, follow the links in the console output to install the missing environment, close the window, and double-click `Launch_Lyra.bat` again.
* **Microphone Permissions (Clap & Wake Word)**: The first time you launch, click the **Settings Gear** in the top right, turn **Voice & Clap Wake System** ON, and allow microphone access in the browser/app overlay. You are now fully configured to double-clap and say "hai lyra" to bring the window to the front!
