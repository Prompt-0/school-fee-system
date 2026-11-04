# 💻 Student Developer Web Terminal Sandbox

An in-browser, interactive **Linux / Bash Terminal Sandbox** designed specifically for students and beginners to tinker with the School Fee Management System directly from any web browser without installing Python, Git, or dependencies locally.

---

## 🌟 Why This Exists (For Educators & Students)

Setting up local development environments (Python versions, virtual environments, path variables, terminal shells) is often a friction point for students who are just starting to learn programming.

This web terminal provides:
1. **Immediate Access**: Open a web link on a laptop, tablet, or phone and instantly get a working bash terminal in `~/school-fee-system`.
2. **Real CLI Execution**: Students run actual commands (`ls -la`, `cat README.md`, `python -m school_fee_system students list`, `python -m unittest discover tests`).
3. **Student Missions Lab**: A built-in sidebar with guided interactive tasks. Every task has a **"▶ Run"** button that automatically pastes and executes the command in the terminal.
4. **Zero Risk**: Students can experiment, create python test scripts, test fee collections, and run `reset-db` at any time to return the database to its pristine demo state.

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
| **1. Explore Project Files** | `ls -la` | Understands directory structure (`src`, `tests`, `data`, `pyproject.toml`) |
| **2. Check Current Path** | `pwd` | Understands Linux working directories |
| **3. Read Project Docs** | `cat README.md` | Inspecting markdown and project requirements in terminal |
| **4. Run Python CLI Help** | `python -m school_fee_system --help` | Understands Python module execution (`-m`) and CLI subcommands |
| **5. List Enrolled Pupils** | `python -m school_fee_system students list` | Inspects database queries formatted as terminal tables |
| **6. Check Invoices & Due Dates**| `python -m school_fee_system invoices list` | Sees financial ledger state and due dates |
| **7. Identify Defaulters** | `python -m school_fee_system defaulters` | Inspects business logic for overdue grace periods |
| **8. Collect Fee & Issue Receipt**| `python -m school_fee_system payments record --invoice-id 1 --amount 5000 --method UPI` | Runs transactions, updates balance, and prints ASCII receipt |
| **9. Verify Digital Seal** | `python -m school_fee_system receipts verify REC-2026-0001` | Learns cryptographic SHA-256 integrity verification |
| **10. Run Automated Tests** | `python -m unittest discover tests` | Understands Test-Driven Development (TDD) and test suites |
| **11. Write First Python Script**| `echo "print(2 + 2)" > calc.py && python calc.py` | Creates and executes their own custom Python program |
| **12. Reset Demo Database** | `reset-db` | Restores the CBSE 43-student database to fresh demo state |

---

## ⌨️ Terminal Shortcuts & Controls

- **`Tab`**: Auto-completes commands and file paths.
- **`↑` / `↓`**: Navigates through previous command history (persisted in `localStorage`).
- **`Ctrl + L` / `clear`**: Clears the terminal screen.
- **`Ctrl + C`**: Cancels current input buffer.
- **`CRT: On/Off`**: Toggles retro CRT scanline phosphor effect.
- **`Palette`**: Toggles color themes (`teal`, `matrix`, `amber`, `nord`, `cyberpunk`).
- **Mobile Touch Bar**: Virtual buttons (`TAB`, `↑`, `↓`, `ls`, `--help`, `students`, `invoices`, `defaulters`) for phone touch typing.
