# lc-finder

A point-and-click tool that scans a folder of OCT **TIFF stacks**, finds the slices that show **Lamina Cribrosa (LC)**, and saves new “LC-only” stacks for you.  


---

## 📦 What you get

| File | What it is |
|------|------------|
| **`lc_gui_app.py`** | Drag-and-drop window—just pick two folders and click **Run**. |
| **`lc_pipeline.py`** | Command-line / batch version (optional). |
| **`environment.yml`** | One-stop installer for all required libraries. |

Your folders:
lc-finder/
├── lc_gui_app.py
├── lc_pipeline.py
├── environment.yml
├── inputs/                ← put raw .tif stacks here
└── reassembled_outputs/   ← LC-only stacks appear here

---

## 🖥️  1-Time Setup (macOS & Windows)

1. **Install Python 3.10+**  
   *macOS:* <https://www.python.org/downloads/> or Conda.
If need conda:
   ```bash
conda env create -f environment.yml     # sets up python 3.10 + all libs
conda activate lc-finder

   *Windows:* Use the “Add Python to PATH” option during install.

3. **Install the required libraries**

   Open *Terminal* (macOS) or *Command Prompt* (Windows) and run:

   ```bash
   pip install PySimpleGUI pillow roboflow

## 🚀 Using the GUI (recommended)
1.	Double-click lc_gui_app.py
  - If your system opens a text editor instead of running it:
      - macOS: right-click → Open With → Python Launcher
  	  - Windows: right-click → Open with → Python
3.	The LC Stack Processor window appears:
