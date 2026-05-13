# -*- coding: utf-8 -*-
"""Student Management System

A modern, dark-themed desktop application built with Tkinter and SQLite.
Features:
- Multi-page application with login and various subpages
- Add, Update, Delete, Search, Clear, Show All student records
- Dashboard with statistics
- Reports page
- Settings page
- Object‑oriented design (StudentDB, various Page classes)
- Automatic DB/table creation
- Input validation & message boxes
- ttk Treeview with scrollbar for tabular view
- Responsive layout using grid and weight configuration
- Professional fonts (Roboto) and dark theme styling
"""

import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# ---------------------------------------------------------------------------
# Database handling (OOP)
# ---------------------------------------------------------------------------
class StudentDB:
    """Encapsulates all SQLite interactions for the student records and users."""

    def __init__(self, db_path="students.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.create_tables()

    def create_tables(self):
        """Create the students and users tables if they do not already exist."""
        # Students table
        student_query = """
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            course TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            address TEXT NOT NULL,
            marks REAL NOT NULL,
            created_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.conn.execute(student_query)
        
        # Users table for login
        user_query = """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'admin',
            created_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.conn.execute(user_query)
        
        # Insert default admin user if not exists
        self.conn.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", 
                         ("admin", "admin123", "admin"))
        self.conn.commit()

    def add_student(self, data: dict):
        """Insert a new student record.
        ``data`` keys must match column names.
        """
        placeholders = ", ".join("?" for _ in data)
        columns = ", ".join(data.keys())
        query = f"INSERT INTO students ({columns}) VALUES ({placeholders})"
        try:
            self.conn.execute(query, tuple(data.values()))
            self.conn.commit()
            return True, "Student added successfully."
        except sqlite3.IntegrityError:
            return False, "Student ID already exists."
        except Exception as e:
            return False, str(e)

    def update_student(self, student_id: str, data: dict):
        """Update an existing student identified by ``student_id``."""
        set_clause = ", ".join(f"{k}=?" for k in data.keys())
        query = f"UPDATE students SET {set_clause} WHERE student_id=?"
        params = list(data.values()) + [student_id]
        cur = self.conn.execute(query, params)
        self.conn.commit()
        if cur.rowcount == 0:
            return False, "Student not found."
        return True, "Student updated successfully."

    def delete_student(self, student_id: str):
        """Delete a student record by ID."""
        query = "DELETE FROM students WHERE student_id=?"
        cur = self.conn.execute(query, (student_id,))
        self.conn.commit()
        if cur.rowcount == 0:
            return False, "Student not found."
        return True, "Student deleted successfully."

    def search_student(self, keyword: str):
        """Search by ID or name (case‑insensitive). Returns a list of rows."""
        kw = f"%{keyword}%"
        query = """
        SELECT * FROM students
        WHERE student_id LIKE ? OR name LIKE ?
        """
        cur = self.conn.execute(query, (kw, kw))
        return cur.fetchall()

    def fetch_all(self):
        """Return all student records."""
        cur = self.conn.execute("SELECT * FROM students")
        return cur.fetchall()

    def authenticate_user(self, username: str, password: str):
        """Authenticate user login."""
        query = "SELECT role FROM users WHERE username=? AND password=?"
        cur = self.conn.execute(query, (username, password))
        result = cur.fetchone()
        return result[0] if result else None

    def get_student_stats(self):
        """Get statistics for dashboard."""
        stats = {}
        # Total students
        cur = self.conn.execute("SELECT COUNT(*) FROM students")
        stats['total_students'] = cur.fetchone()[0]
        
        # Average marks
        cur = self.conn.execute("SELECT AVG(marks) FROM students")
        avg_marks = cur.fetchone()[0]
        stats['avg_marks'] = round(avg_marks, 2) if avg_marks else 0
        
        # Gender distribution
        cur = self.conn.execute("SELECT gender, COUNT(*) FROM students GROUP BY gender")
        stats['gender_dist'] = dict(cur.fetchall())
        
        # Course distribution
        cur = self.conn.execute("SELECT course, COUNT(*) FROM students GROUP BY course")
        stats['course_dist'] = dict(cur.fetchall())
        
        return stats

# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Page Management System
# ---------------------------------------------------------------------------
class PageManager:
    """Manages switching between different pages/frames."""
    
    def __init__(self, root, db):
        self.root = root
        self.db = db
        self.current_page = None
        self.pages = {}
        self.container = ttk.Frame(root)
        self.container.pack(fill="both", expand=True)
        
        # Create pages
        self.pages["login"] = LoginPage(self.container, self)
        self.pages["dashboard"] = DashboardPage(self.container, self)
        self.pages["students"] = StudentsPage(self.container, self)
        self.pages["reports"] = ReportsPage(self.container, self)
        self.pages["settings"] = SettingsPage(self.container, self)
        
        self.show_page("login")
    
    def show_page(self, page_name):
        """Show the specified page."""
        if self.current_page:
            self.current_page.pack_forget()
        self.current_page = self.pages[page_name]
        self.current_page.pack(fill="both", expand=True)
        self.current_page.on_show()

# ---------------------------------------------------------------------------
# Base Page Class
# ---------------------------------------------------------------------------
class BasePage(ttk.Frame):
    """Base class for all pages."""
    
    def __init__(self, parent, page_manager):
        super().__init__(parent)
        self.page_manager = page_manager
        self.db = page_manager.db
        self.setup_style()
    
    def setup_style(self):
        """Setup common styling."""
        dark_bg = "#ffffff"
        dark_fg = "#000000"
        accent = "#0066cc"
        self.configure(style="Dark.TFrame")
        
        style = ttk.Style(self)
        style.configure("Dark.TFrame", background=dark_bg)
        style.configure("Dark.TLabel", background=dark_bg, foreground=dark_fg, font=("Roboto", 10))
        style.configure("Dark.TEntry", fieldbackground="#f9f9f9", foreground=dark_fg, font=("Roboto", 10))
        style.configure("Dark.TCombobox", fieldbackground="#f9f9f9", foreground=dark_fg, font=("Roboto", 10))
        style.configure("Dark.TButton", background=accent, foreground="#ffffff", font=("Roboto", 10), padding=5)
        style.map("Dark.TButton", background=[("active", "#0052a3")])
        style.configure("Dark.Treeview", background="#f9f9f9", fieldbackground="#f9f9f9", foreground=dark_fg, font=("Roboto", 10))
        style.configure("Dark.Treeview.Heading", background=dark_bg, foreground=dark_fg, font=("Roboto", 11, "bold"))
    
    def on_show(self):
        """Called when page is shown."""
        pass
    
    def create_navigation(self, parent):
        """Create navigation bar."""
        nav_frame = ttk.Frame(parent, style="Dark.TFrame")
        nav_frame.pack(fill="x", pady=10)
        
        pages = [
            ("Dashboard", "dashboard"),
            ("Students", "students"), 
            ("Reports", "reports"),
            ("Settings", "settings")
        ]
        
        for text, page in pages:
            btn = ttk.Button(nav_frame, text=text, command=lambda p=page: self.page_manager.show_page(p), style="Dark.TButton")
            btn.pack(side="left", padx=5)
        
        # Logout button
        logout_btn = ttk.Button(nav_frame, text="Logout", command=self.logout, style="Dark.TButton")
        logout_btn.pack(side="right", padx=5)
    
    def logout(self):
        """Logout and return to login page."""
        self.page_manager.show_page("login")

# ---------------------------------------------------------------------------
# Login Page
# ---------------------------------------------------------------------------
class LoginPage(BasePage):
    def __init__(self, parent, page_manager):
        super().__init__(parent, page_manager)
        self.create_widgets()
    
    def create_widgets(self):
        # Center the login form
        center_frame = ttk.Frame(self, style="Dark.TFrame")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title
        title = ttk.Label(center_frame, text="Student Management System", 
                         font=("Roboto", 20, "bold"), style="Dark.TLabel")
        title.pack(pady=20)
        
        # Login form
        form_frame = ttk.Frame(center_frame, style="Dark.TFrame")
        form_frame.pack(pady=20)
        
        ttk.Label(form_frame, text="Username:", style="Dark.TLabel").grid(row=0, column=0, pady=5, padx=5, sticky="e")
        self.username_entry = ttk.Entry(form_frame, style="Dark.TEntry")
        self.username_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(form_frame, text="Password:", style="Dark.TLabel").grid(row=1, column=0, pady=5, padx=5, sticky="e")
        self.password_entry = ttk.Entry(form_frame, show="*", style="Dark.TEntry")
        self.password_entry.grid(row=1, column=1, pady=5, padx=5)
        
        # Buttons
        btn_frame = ttk.Frame(center_frame, style="Dark.TFrame")
        btn_frame.pack(pady=20)
        
        login_btn = ttk.Button(btn_frame, text="Login", command=self.login, style="Dark.TButton")
        login_btn.pack(side="left", padx=10)
        
        clear_btn = ttk.Button(btn_frame, text="Clear", command=self.clear_fields, style="Dark.TButton")
        clear_btn.pack(side="left", padx=10)
        
        # Default credentials info
        info_label = ttk.Label(center_frame, 
                              text="Default credentials: admin / admin123", 
                              font=("Roboto", 8), 
                              style="Dark.TLabel")
        info_label.pack(pady=10)
    
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return
        
        role = self.db.authenticate_user(username, password)
        if role:
            messagebox.showinfo("Success", f"Welcome {username}!")
            self.page_manager.show_page("dashboard")
        else:
            messagebox.showerror("Error", "Invalid username or password.")
    
    def clear_fields(self):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

# ---------------------------------------------------------------------------
# Dashboard Page
# ---------------------------------------------------------------------------
class DashboardPage(BasePage):
    def __init__(self, parent, page_manager):
        super().__init__(parent, page_manager)
        self.create_widgets()
    
    def create_widgets(self):
        self.create_navigation(self)
        
        # Title
        title = ttk.Label(self, text="Dashboard", font=("Roboto", 18, "bold"), style="Dark.TLabel")
        title.pack(pady=20)
        
        # Stats frame
        self.stats_frame = ttk.Frame(self, style="Dark.TFrame")
        self.stats_frame.pack(pady=20, fill="x", padx=20)
    
    def on_show(self):
        """Update statistics when page is shown."""
        # Clear previous stats
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        
        stats = self.db.get_student_stats()
        
        # Create stat cards
        stat_items = [
            ("Total Students", str(stats['total_students'])),
            ("Average Marks", f"{stats['avg_marks']:.2f}"),
            ("Male Students", str(stats['gender_dist'].get('Male', 0))),
            ("Female Students", str(stats['gender_dist'].get('Female', 0))),
        ]
        
        for i, (label, value) in enumerate(stat_items):
            card = ttk.Frame(self.stats_frame, style="Dark.TFrame", relief="raised", borderwidth=2)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            
            ttk.Label(card, text=label, font=("Roboto", 12, "bold"), style="Dark.TLabel").pack(pady=5)
            ttk.Label(card, text=value, font=("Roboto", 16), style="Dark.TLabel").pack(pady=5)
        
        # Configure grid weights
        for i in range(len(stat_items)):
            self.stats_frame.columnconfigure(i, weight=1)

# ---------------------------------------------------------------------------
# Students Page (Main CRUD operations)
# ---------------------------------------------------------------------------
class StudentsPage(BasePage):
    def __init__(self, parent, page_manager):
        super().__init__(parent, page_manager)
        self.create_widgets()
    
    def create_widgets(self):
        self.create_navigation(self)
        
        # Title
        title = ttk.Label(self, text="Student Management", font=("Roboto", 18, "bold"), style="Dark.TLabel")
        title.pack(pady=10)
        
        # Input Form
        form_frame = ttk.Frame(self, style="Dark.TFrame")
        form_frame.pack(pady=10, fill="x", padx=20)
        
        labels = ["Student ID", "Name", "Age", "Gender", "Course", "Phone", "Email", "Address", "Marks"]
        self.entries = {}
        
        # Create 3 columns
        for idx, text in enumerate(labels):
            r = idx // 3
            c = (idx % 3) * 2
            
            lbl = ttk.Label(form_frame, text=text + ":", style="Dark.TLabel")
            lbl.grid(row=r, column=c, sticky="e", padx=5, pady=5)
            
            if text == "Gender":
                var = tk.StringVar()
                entry = ttk.Combobox(form_frame, textvariable=var, state="readonly", 
                                   values=["Male", "Female", "Other"], style="Dark.TCombobox")
                entry.current(0)
            else:
                entry = ttk.Entry(form_frame, style="Dark.TEntry")
            
            entry.grid(row=r, column=c + 1, sticky="ew", padx=5, pady=5)
            self.entries[text.lower().replace(" ", "_")] = entry
        
        # Configure grid weights
        for i in range(6):
            form_frame.columnconfigure(i, weight=1)
        
        # Buttons
        btn_frame = ttk.Frame(self, style="Dark.TFrame")
        btn_frame.pack(pady=10)
        
        btn_names = [
            ("Add", self.add_student),
            ("Update", self.update_student),
            ("Delete", self.delete_student),
            ("Search", self.search_student),
            ("Clear", self.clear_fields),
            ("Show All", self.show_all),
        ]
        
        for txt, cmd in btn_names:
            btn = ttk.Button(btn_frame, text=txt, command=cmd, style="Dark.TButton")
            btn.pack(side="left", padx=5)
        
        # Treeview Table
        table_frame = ttk.Frame(self, style="Dark.TFrame")
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        columns = ("student_id", "name", "age", "gender", "course", "phone", "email", "address", "marks")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15, style="Dark.Treeview")
        
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=100, anchor="center")
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=v_scrollbar.set, xscroll=h_scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Bind selection
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
    
    def on_show(self):
        """Populate table when page is shown."""
        self.populate_table()
    
    def get_form_data(self):
        data = {}
        for key, widget in self.entries.items():
            value = widget.get().strip()
            data[key] = value
        return data
    
    def validate_form(self, data):
        # Ensure no empty fields
        for field, val in data.items():
            if val == "":
                messagebox.showerror("Validation Error", f"{field.replace('_', ' ').title()} cannot be empty.")
                return False
        # Additional checks
        if not data["age"].isdigit():
            messagebox.showerror("Validation Error", "Age must be a number.")
            return False
        try:
            float(data["marks"])
        except ValueError:
            messagebox.showerror("Validation Error", "Marks must be a numeric value.")
            return False
        return True
    
    def add_student(self):
        data = self.get_form_data()
        if not self.validate_form(data):
            return
        success, msg = self.db.add_student(data)
        if success:
            messagebox.showinfo("Success", msg)
            self.populate_table()
            self.clear_fields()
        else:
            messagebox.showerror("Error", msg)
    
    def update_student(self):
        data = self.get_form_data()
        if not self.validate_form(data):
            return
        student_id = data.pop("student_id")
        success, msg = self.db.update_student(student_id, data)
        if success:
            messagebox.showinfo("Success", msg)
            self.populate_table()
            self.clear_fields()
        else:
            messagebox.showerror("Error", msg)
    
    def delete_student(self):
        student_id = self.entries["student_id"].get().strip()
        if not student_id:
            messagebox.showerror("Error", "Student ID is required to delete.")
            return
        if messagebox.askyesno("Confirm Delete", f"Delete student with ID {student_id}?"):
            success, msg = self.db.delete_student(student_id)
            if success:
                messagebox.showinfo("Success", msg)
                self.populate_table()
                self.clear_fields()
            else:
                messagebox.showerror("Error", msg)
    
    def search_student(self):
        keyword = self.entries["student_id"].get().strip() or self.entries["name"].get().strip()
        if not keyword:
            messagebox.showerror("Error", "Enter Student ID or Name to search.")
            return
        rows = self.db.search_student(keyword)
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert("", tk.END, values=row)
    
    def clear_fields(self):
        for widget in self.entries.values():
            if isinstance(widget, ttk.Combobox):
                widget.current(0)
            else:
                widget.delete(0, tk.END)
    
    def show_all(self):
        self.populate_table()
        self.clear_fields()
    
    def populate_table(self):
        rows = self.db.fetch_all()
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert("", tk.END, values=row)
    
    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        keys = list(self.entries.keys())
        for key, val in zip(keys, values):
            widget = self.entries[key]
            if isinstance(widget, ttk.Combobox):
                widget.set(val)
            else:
                widget.delete(0, tk.END)
                widget.insert(0, val)

# ---------------------------------------------------------------------------
# Reports Page
# ---------------------------------------------------------------------------
class ReportsPage(BasePage):
    def __init__(self, parent, page_manager):
        super().__init__(parent, page_manager)
        self.create_widgets()
    
    def create_widgets(self):
        self.create_navigation(self)
        
        # Title
        title = ttk.Label(self, text="Reports", font=("Roboto", 18, "bold"), style="Dark.TLabel")
        title.pack(pady=20)
        
        # Report buttons
        btn_frame = ttk.Frame(self, style="Dark.TFrame")
        btn_frame.pack(pady=20)
        
        reports = [
            ("Student List Report", self.show_student_list),
            ("Course Distribution", self.show_course_distribution),
            ("Gender Statistics", self.show_gender_stats),
            ("Top Performers", self.show_top_performers),
        ]
        
        for text, cmd in reports:
            btn = ttk.Button(btn_frame, text=text, command=cmd, style="Dark.TButton")
            btn.pack(side="left", padx=10, pady=10)
        
        # Results area
        self.results_text = tk.Text(self, bg="#f9f9f9", fg="#000000", font=("Roboto", 10), 
                                   wrap=tk.WORD, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(self, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.pack(side="left", fill="both", expand=True, padx=20, pady=10)
        scrollbar.pack(side="right", fill="y")
    
    def on_show(self):
        """Clear results when page is shown."""
        self.clear_results()
    
    def clear_results(self):
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.DISABLED)
    
    def append_result(self, text):
        self.results_text.config(state=tk.NORMAL)
        self.results_text.insert(tk.END, text + "\n")
        self.results_text.config(state=tk.DISABLED)
    
    def show_student_list(self):
        self.clear_results()
        rows = self.db.fetch_all()
        self.append_result("STUDENT LIST REPORT")
        self.append_result("=" * 50)
        self.append_result(f"Total Students: {len(rows)}\n")
        
        for row in rows:
            self.append_result(f"ID: {row[0]}, Name: {row[1]}, Age: {row[2]}, Gender: {row[3]}, Course: {row[4]}, Marks: {row[8]}")
    
    def show_course_distribution(self):
        self.clear_results()
        stats = self.db.get_student_stats()
        self.append_result("COURSE DISTRIBUTION REPORT")
        self.append_result("=" * 50)
        
        for course, count in stats['course_dist'].items():
            self.append_result(f"{course}: {count} students")
    
    def show_gender_stats(self):
        self.clear_results()
        stats = self.db.get_student_stats()
        self.append_result("GENDER STATISTICS REPORT")
        self.append_result("=" * 50)
        
        for gender, count in stats['gender_dist'].items():
            self.append_result(f"{gender}: {count} students")
    
    def show_top_performers(self):
        self.clear_results()
        cur = self.db.conn.execute("SELECT name, marks FROM students ORDER BY marks DESC LIMIT 10")
        top_students = cur.fetchall()
        
        self.append_result("TOP PERFORMERS REPORT")
        self.append_result("=" * 50)
        
        for i, (name, marks) in enumerate(top_students, 1):
            self.append_result(f"{i}. {name}: {marks} marks")

# ---------------------------------------------------------------------------
# Settings Page
# ---------------------------------------------------------------------------
class SettingsPage(BasePage):
    def __init__(self, parent, page_manager):
        super().__init__(parent, page_manager)
        self.create_widgets()
    
    def create_widgets(self):
        self.create_navigation(self)
        
        # Title
        title = ttk.Label(self, text="Settings", font=("Roboto", 18, "bold"), style="Dark.TLabel")
        title.pack(pady=20)
        
        # Settings frame
        settings_frame = ttk.Frame(self, style="Dark.TFrame")
        settings_frame.pack(pady=20, padx=20, fill="x")
        
        # Database info
        ttk.Label(settings_frame, text="Database Information:", font=("Roboto", 12, "bold"), 
                 style="Dark.TLabel").grid(row=0, column=0, columnspan=2, pady=10, sticky="w")
        
        ttk.Label(settings_frame, text="Database File:", style="Dark.TLabel").grid(row=1, column=0, pady=5, padx=5, sticky="e")
        ttk.Label(settings_frame, text=self.db.db_path, style="Dark.TLabel").grid(row=1, column=1, pady=5, padx=5, sticky="w")
        
        # User management
        ttk.Label(settings_frame, text="User Management:", font=("Roboto", 12, "bold"), 
                 style="Dark.TLabel").grid(row=2, column=0, columnspan=2, pady=20, sticky="w")
        
        ttk.Label(settings_frame, text="Current User:", style="Dark.TLabel").grid(row=3, column=0, pady=5, padx=5, sticky="e")
        ttk.Label(settings_frame, text="admin", style="Dark.TLabel").grid(row=3, column=1, pady=5, padx=5, sticky="w")
        
        # Buttons
        btn_frame = ttk.Frame(settings_frame, style="Dark.TFrame")
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Change Password", command=self.change_password, 
                  style="Dark.TButton").pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Backup Database", command=self.backup_database, 
                  style="Dark.TButton").pack(side="left", padx=10)
    
    def change_password(self):
        # Simple password change dialog
        dialog = tk.Toplevel(self)
        dialog.title("Change Password")
        dialog.geometry("300x200")
        dialog.configure(bg="#ffffff")
        
        ttk.Label(dialog, text="New Password:", style="Dark.TLabel").pack(pady=10)
        password_entry = ttk.Entry(dialog, show="*", style="Dark.TEntry")
        password_entry.pack(pady=5)
        
        def save_password():
            new_pass = password_entry.get().strip()
            if new_pass:
                self.db.conn.execute("UPDATE users SET password=? WHERE username=?", (new_pass, "admin"))
                self.db.conn.commit()
                messagebox.showinfo("Success", "Password changed successfully!")
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Password cannot be empty.")
        
        ttk.Button(dialog, text="Save", command=save_password, style="Dark.TButton").pack(pady=10)
    
    def backup_database(self):
        from shutil import copy2
        import os
        
        backup_name = f"students_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        try:
            copy2(self.db.db_path, backup_name)
            messagebox.showinfo("Success", f"Database backed up as {backup_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Backup failed: {str(e)}")

# ---------------------------------------------------------------------------
# Main Application
# ---------------------------------------------------------------------------
class StudentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Management System")
        self.root.geometry("1200x700")
        self.db = StudentDB()
        self.page_manager = PageManager(root, self.db)

# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Application entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = StudentApp(root)
    root.mainloop()
# Application entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = StudentApp(root)
    root.mainloop()
