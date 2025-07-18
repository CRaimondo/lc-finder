# LC-Finder

**LC-Finder** is a point-and-click utility that scans your OCT **TIFF stacks**, finds every slice containing **Lamina Cribrosa (LC)**, and re-assembles those slices into new “LC-only” stacks—no coding required.

---

## 📂 Repository Layout

| Path | Purpose |
|------|---------|
| `lc_gui_app.py` | **Graphical** interface. Double-click, pick folders, press **Run**. |
| `lc_pipeline.py` | **Command-line** / automated batch runner (optional). |
| `environment.yml` | One-line Conda installer for every Python library you need. |
| `inputs/` | Drop raw `.tif` stacks here (folder is ignored by Git). |
| `reassembled_outputs/` | LC-only stacks are written here. |

Your folders:
lc-finder/
├── lc_gui_app.py
├── lc_pipeline.py
├── environment.yml
├── inputs/                ← put raw .tif stacks here
└── reassembled_outputs/   ← LC-only stacks appear here

---

## 🖥️  One-Time Setup (macOS • Windows)

### 1 Install Python ≥ 3.10  
*Mac:* download from <https://www.python.org/downloads/> **or** install Conda.  
*Windows:* same link; tick **“Add Python to PATH”** during setup.

### 2 Install the dependencies  

	```bash
		conda env create -f environment.yml ## inside lc-finder/
		conda activate lc-finder

### 3 **Install the required libraries**

   Open *Terminal* (macOS) or *Command Prompt* (Windows) and run:

   ```bash
   pip install PySimpleGUI pillow roboflow

## 🚀 Using the GUI (recommended)
1.	Double-click lc_gui_app.py
  - If your system opens a text editor instead of running it:
      - macOS: right-click → Open With → Python Launcher
  	  - Windows: right-click → Open with → Python
2.	The LC Stack Processor window appears:
┌─ LC Stack Processor ──────────────────────────┐
│ Input folder:   [ Browse… ]                   │
│ Output folder:  [ Browse… ]                   │
│ Min LC confidence: 0.90                       │
│ [ Run ]   [ Exit ]                            │
│ ───── live log shows progress here ────────── │
└───────────────────────────────────────────────┘
3.  Choose your folders
Input  – click Browse… and select the directory that contains your raw .tif files (for example lc-finder/inputs).
Output – click Browse… and select / create a folder for results (e.g. lc-finder/reassembled_outputs).
	4.	Leave “Min LC confidence” at 0.90 unless you want stricter filtering.
	5.	Click Run.
Progress messages stream in the console pane, and new files named
originalStack_LC_only.tif appear in the output folder.


🔧  Command-Line (Optional)

# batch-process every .tif in inputs/ once
python lc_pipeline.py --in inputs --out reassembled_outputs --conf 0.90

# keep watching the inputs/ folder and auto-process new files
python lc_pipeline.py --in inputs --out reassembled_outputs --conf 0.90 --watch
