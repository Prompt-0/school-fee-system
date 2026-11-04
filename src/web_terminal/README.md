# 💻 Student Developer Web Terminal Sandbox

An in-browser, interactive **Linux / Bash & Python Terminal Sandbox** designed specifically for students and beginners to tinker with the Delhi Public Academy School Fee Management System directly from any web browser without installing Python, Git, or dependencies locally.

---

## 🌟 Why This Exists (For Educators & Students)

Setting up local development environments (Python versions, virtual environments, path variables, terminal shells) is often a major hurdle for students who are just starting to learn programming.

This web terminal provides:
1. **Immediate Access**: Open the web link on a laptop, tablet, or phone and instantly get a working bash terminal in `~/school-fee-system`.
2. **Interactive Project Console (`python main.py`)**: Run the complete interactive menu with 1-9 choices for managing students, fees, dues, and payments.
3. **Interactive Python REPL (`python`)**: Launch a live `>>>` Python shell to experiment with variables, math, and code in real time.
4. **Real Bash & Linux CLI**: Run actual shell commands (`ls -la`, `cat README.md`, `python -m unittest discover tests`).
5. **Mobile & Touch Friendly**: Features dedicated virtual keyboard controls (`↵ Enter`, `TAB`, `↑`, `↓`, quick buttons) and handles mobile form submissions seamlessly.
6. **Student Missions Lab**: A built-in sidebar with guided interactive tasks. Every task has a **"▶ Run"** button that automatically pastes and executes the command in the terminal.
7. **Zero Risk**: Students can experiment, create python test scripts, test fee collections, and run `reset-db` at any time to return the database to its pristine demo state.

---

## 🚀 How to Run the Web Terminal

### Mode 1: Integrated in Cloud / Main Server (Default)
When the main server is running:
```bash
python -m school_fee_system serve --port 8000
```
Open in browser:
- **Local URL**: [http://127.0.0.1:8000/terminal](http://127.0.0.1:8000/terminal)
- **Production Cloud URL**: [https://con-academy.onrender.com/terminal](https://con-academy.onrender.com/terminal)

### Mode 2: Standalone Terminal Server (Port 8080)
From the repository root:
```bash
python -m web_terminal --port 8080
```
Open in browser:
👉 **`http://127.0.0.1:8080/`**

---

## 🎓 Guided Student Missions

| Mission | Command | What the Student Learns |
| :--- | :--- | :--- |
| **1. Launch Interactive Project** | `python main.py` | Runs the interactive menu console with student lookup, dues, and payments |
| **2. Interactive Python REPL** | `python` | Starts a live Python `>>>` prompt to experiment with variables, math, and syntax |
| **3. Explore Project Files** | `ls -la` | Understands directory structure (`src`, `tests`, `data`, `pyproject.toml`) |
| **4. List Enrolled Pupils** | `python -m school_fee_system students list` | Inspects database queries formatted as terminal tables |
| **5. Check Invoices & Due Dates**| `python -m school_fee_system invoices list` | Sees financial ledger state and due dates |
| **6. Identify Defaulters** | `python -m school_fee_system defaulters` | Inspects business logic for overdue grace periods |
| **7. Collect Fee & Issue Receipt**| `python -m school_fee_system payments record --invoice-id 1 --amount 5000 --method UPI` | Runs transactions, updates balance, and prints ASCII receipt |
| **8. Verify Digital Seal** | `python -m school_fee_system receipts verify REC-2026-0001` | Learns cryptographic SHA-256 integrity verification |
| **9. Run Automated Tests** | `python -m unittest discover tests` | Understands Test-Driven Development (TDD) and test suites |
| **10. Write First Python Script**| `echo "print(2 + 2)" > calc.py && python calc.py` | Creates and executes their own custom Python program |
| **11. Reset Demo Database** | `reset-db` | Restores the CBSE 43-student database to fresh demo state |

---

## ⌨️ Terminal Shortcuts & Controls

- **`Enter` or `↵` button**: Executes the current command.
- **`↑` / `↓`**: Navigates through command history.
- **`Tab`**: Auto-completes commands and suggestions.
- **`Ctrl + L`**: Clears the terminal screen.
- **`Ctrl + C`**: Cancels the current input line.
- **Mobile Touch Bar**: Instant touch shortcuts for `↵ Enter`, `python main.py`, `python`, `1`, `2`, `4`, `0 (Exit)`, and `ls -la`.
