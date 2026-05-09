# Student Management System

## Overview
A modern, dark‑themed desktop application for managing student records. It is built with **Python 3**, `tkinter` for the GUI, and `sqlite3` for persistent storage. The app follows an object‑oriented design and provides full CRUD (Create, Read, Update, Delete) functionality.

## Features
- Add, Update, Delete, Search, Clear, Show All student records
- Dark theme with professional fonts (Roboto) and responsive layout
- Input validation and informative message boxes
- `ttk.Treeview` with vertical scrollbar for tabular display
- Automatic creation of the SQLite database and table if they do not exist
- Single‑file implementation for easy distribution

## Requirements
- **Python 3.8+** (the script uses f‑strings and type hints)
- `tkinter` package for Python 3 (`python3‑tkinter` on Fedora, `python3-tk` on Debian/Ubuntu, etc.)
- Standard library modules only (`sqlite3`, `os`)

## Installation
1. **Clone or copy the project** into a directory of your choice.
   ```bash
   git clone <repository‑url> "python mini project"
   cd "python mini project"
   ```
2. **Install Tkinter** for your distribution:
   - **Fedora**:
     ```bash
     sudo dnf install python3-tkinter
     ```
   - **Ubuntu / Debian**:
     ```bash
     sudo apt install python3-tk
     ```
   - **Arch Linux**:
     ```bash
     sudo pacman -S tk
     ```
3. Ensure you are using the Python 3 interpreter:
   ```bash
   python3 --version
   ```

## Running the Application
Execute the script with Python 3:
```bash
python3 "student_management_system.py"
```
The GUI window will launch with the dark theme. Use the input fields and buttons to manage student data.

## Project Structure
```
student_management_system.py   # Main application (single file)
students.db                    # SQLite database (created automatically)
README.md                     # This file
```

## How It Works (Compile Details)
- The script does **not require compilation**; it is interpreted Python code.
- On first run, the `StudentDB` class creates `students.db` and the `students` table if they do not exist.
- GUI widgets are created using `tkinter` and styled with `ttk.Style` for the dark appearance.
- CRUD operations interact with SQLite through parameterised SQL queries, ensuring safety and consistency.

## License
This project is provided under the MIT License – feel free to modify and distribute it.
