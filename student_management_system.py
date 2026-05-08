# -*- coding: utf-8 -*-
"""Student Management System

A modern, dark-themed desktop application built with Tkinter and SQLite.
Features:
- Add, Update, Delete, Search, Clear, Show All student records
- Object‑oriented design (StudentDB, StudentApp)
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

# ---------------------------------------------------------------------------
# Database handling (OOP)
# ---------------------------------------------------------------------------
class StudentDB:
    """Encapsulates all SQLite interactions for the student records."""

    def __init__(self, db_path="students.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.create_table()

    def create_table(self):
        """Create the students table if it does not already exist."""
        query = """
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            course TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            address TEXT NOT NULL,
            marks REAL NOT NULL
        )
        """
        self.conn.execute(query)
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

# ---------------------------------------------------------------------------
# Main Application (Tkinter UI)
# ---------------------------------------------------------------------------
class StudentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Management System")
        self.root.geometry("1000x600")
        self.db = StudentDB()
        self.setup_style()
        self.create_widgets()
        self.populate_table()

    # -----------------------------------------------------------------------
    # UI Styling – dark theme
    # -----------------------------------------------------------------------
    def setup_style(self):
        style = ttk.Style(self.root)
        # Use the native theme as a base, then override colors
        if "clam" in style.theme_names():
            style.theme_use("clam")
        # Define a dark colour palette
        dark_bg = "#2b2b2b"
        dark_fg = "#e0e0e0"
        accent = "#3d85c6"
        style.configure("TLabel", background=dark_bg, foreground=dark_fg, font=("Roboto", 10))
        style.configure("TEntry", fieldbackground="#3c3f41", foreground=dark_fg, font=("Roboto", 10))
        style.configure("TButton", background=accent, foreground=dark_fg, font=("Roboto", 10), padding=5)
        style.map("TButton", background=[("active", "#5599dd")])
        style.configure("Treeview", background="#3c3f41", fieldbackground="#3c3f41", foreground=dark_fg, font=("Roboto", 10))
        style.configure("Treeview.Heading", background=dark_bg, foreground=dark_fg, font=("Roboto", 11, "bold"))
        self.root.configure(background=dark_bg)

    # -----------------------------------------------------------------------
    # Layout creation
    # -----------------------------------------------------------------------
    def create_widgets(self):
        # ----- Title Bar -----
        title = ttk.Label(self.root, text="Student Management System", font=("Roboto", 16, "bold"))
        title.grid(row=0, column=0, columnspan=4, pady=15)

        # ----- Input Form -----
        labels = ["Student ID", "Name", "Age", "Gender", "Course", "Phone", "Email", "Address", "Marks"]
        self.entries = {}
        for idx, text in enumerate(labels):
            r = idx // 3 + 1
            c = (idx % 3) * 2
            lbl = ttk.Label(self.root, text=text + ":")
            lbl.grid(row=r, column=c, sticky="e", padx=5, pady=5)
            if text == "Gender":
                var = tk.StringVar()
                entry = ttk.Combobox(self.root, textvariable=var, state="readonly", values=["Male", "Female", "Other"])
                entry.current(0)
            else:
                entry = ttk.Entry(self.root)
            entry.grid(row=r, column=c + 1, sticky="w", padx=5, pady=5)
            self.entries[text.lower().replace(" ", "_")] = entry

        # ----- Buttons -----
        btn_names = [
            ("Add", self.add_student),
            ("Update", self.update_student),
            ("Delete", self.delete_student),
            ("Search", self.search_student),
            ("Clear", self.clear_fields),
            ("Show All", self.show_all),
        ]
        btn_frame = ttk.Frame(self.root)
        btn_frame.grid(row=4, column=0, columnspan=6, pady=15)
        for i, (txt, cmd) in enumerate(btn_names):
            btn = ttk.Button(btn_frame, text=txt, command=cmd)
            btn.grid(row=0, column=i, padx=5)

        # ----- Treeview Table -----
        columns = ("student_id", "name", "age", "gender", "course", "phone", "email", "address", "marks")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=12)
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=100, anchor="center")
        self.tree.grid(row=5, column=0, columnspan=6, sticky="nsew", padx=10, pady=10)
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=5, column=6, sticky="ns")
        # Bind selection
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        # Make the grid cells expand
        for i in range(6):
            self.root.columnconfigure(i, weight=1)
        self.root.rowconfigure(5, weight=1)

    # -----------------------------------------------------------------------
    # Helper methods
    # -----------------------------------------------------------------------
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
        # Additional simple checks (age numeric, marks numeric)
        if not data["age"].isdigit():
            messagebox.showerror("Validation Error", "Age must be a number.")
            return False
        try:
            float(data["marks"])
        except ValueError:
            messagebox.showerror("Validation Error", "Marks must be a numeric value.")
            return False
        return True

    # -----------------------------------------------------------------------
    # CRUD Operations
    # -----------------------------------------------------------------------
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
# Application entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = StudentApp(root)
    root.mainloop()
