# Student Management System

## Overview
A modern, dark‑themed desktop application for managing student records. It is built with **Python 3**, `tkinter` for the GUI, and `sqlite3` for persistent storage. The app follows an object‑oriented design and provides full CRUD (Create, Read, Update, Delete) functionality with multiple pages including login authentication.

## Features
- **Multi-page Application**: Login page, Dashboard, Students management, Reports, and Settings
- **User Authentication**: Secure login system with default admin credentials
- **Student Management**: Add, Update, Delete, Search, Clear, Show All student records
- **Dashboard**: Statistics and overview of student data
- **Reports**: Generate and view reports
- **Settings**: Application configuration options
- Dark theme with professional fonts (Roboto) and responsive layout
- Input validation and informative message boxes
- `ttk.Treeview` with vertical scrollbar for tabular display
- Automatic creation of the SQLite database and table if they do not exist
- Single‑file implementation for easy distribution

## Requirements
- **Python 3.8+** (the script uses f‑strings and type hints)
- `tkinter` package for Python 3 (`python3‑tkinter` on Fedora, `python3-tk` on Debian/Ubuntu, etc.)
- Standard library modules only (`sqlite3`, `os`, `datetime`)

## Installation
1. **Clone or copy the project** into a directory of your choice.
   ```bash
   git clone <https://github.com/adhilgafoor00-stack/Student-Management-System.git> "python mini project"
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

## Compilation and Execution Details
This is a Python script that does not require traditional compilation. However, here are the detailed steps to run the application:

### Prerequisites Check
- Verify Python version: `python3 --version` (should be 3.8 or higher)
- Check if tkinter is available:
  ```bash
  python3 -c "import tkinter; print('Tkinter available')"
  ```

### Running the Application
1. Navigate to the project directory:
   ```bash
   cd "python mini project"
   ```

2. Execute the script with Python 3:
   ```bash
   python3 student_management_system.py
   ```

3. The application will start with the login page. Use the default credentials:
   - **Username**: admin
   - **Password**: admin123

### Database Setup
- On first run, the application automatically creates `students.db` SQLite database
- Creates necessary tables: `students` and `users`
- Inserts default admin user if not exists
- Database file is created in the same directory as the script

### Application Flow
1. **Login Page**: Authenticate with username/password
2. **Dashboard**: View statistics and overview
3. **Students Page**: Manage student records (CRUD operations)
4. **Reports Page**: Generate and view reports
5. **Settings Page**: Configure application settings

## Project Structure
```
student_management_system.py   # Main application (single file)
students.db                    # SQLite database (created automatically)
README.md                     # This file
```

## How It Works
- The script is interpreted Python code using Tkinter for GUI
- Object-oriented design with classes for database handling and page management
- SQLite database for persistent storage with parameterized queries for security
- Multi-page interface managed by PageManager class
- Responsive layout using Tkinter's grid system
- Dark theme implemented using ttk.Style configurations

## Troubleshooting
- **Tkinter not found**: Install tkinter package for your OS as shown in Installation section
- **Python version error**: Ensure using Python 3.8+
- **Permission denied**: Run with appropriate permissions or in user directory
- **Database errors**: Delete students.db and restart to recreate database

## License
This project is provided under the MIT License – feel free to modify and distribute it.
