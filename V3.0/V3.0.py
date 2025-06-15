import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import sqlite3
import pandas as pd

# GPA Mapping
grade_points = {
    "A+": 4.0, "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0, "D-": 0.7, "F": 0.0
}

class AddStudentDialog(tk.Toplevel):
    def __init__(self, parent, name='', index_number=''):
        super().__init__(parent)
        self.title("Add/Edit Student")
        self.geometry("360x230")
        self.resizable(False, False)
        self.grab_set()
        self.configure(bg="#f0f4f8")
        self.result = None

        label_style = {"background":"#f0f4f8", "font": ("Inter", 11), "anchor":"w", "foreground":"#333333"}
        entry_style = {"font": ("Inter", 11)}

        ttk.Label(self, text="Student Name:", **label_style).pack(pady=(12,4), fill='x', padx=12)
        self.name_entry = ttk.Entry(self, **entry_style)
        self.name_entry.pack(fill="x", padx=12)
        self.name_entry.insert(0, name)

        ttk.Label(self, text="Index Number:", **label_style).pack(pady=(12,4), fill='x', padx=12)
        self.index_entry = ttk.Entry(self, **entry_style)
        self.index_entry.pack(fill="x", padx=12)
        self.index_entry.insert(0, index_number)

        btn_frame = ttk.Frame(self, style="Dialog.TFrame")
        btn_frame.pack(pady=12)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy, style="Secondary.TButton").pack(side="right", padx=6)
        ttk.Button(btn_frame, text="Save", command=self.on_add, style="Primary.TButton").pack(side="right", padx=6)

        self.name_entry.focus_set()

    def on_add(self):
        name = self.name_entry.get().strip()
        index_number = self.index_entry.get().strip()
        if not name or not index_number:
            messagebox.showwarning("Input Error", "Both Name and Index Number are required.", parent=self)
            return
        self.result = (name, index_number)
        self.destroy()

class GPAApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GPA Calculator with Student Management")
        self.root.geometry("1100x750")
        self.root.minsize(950, 700)
        self.root.configure(bg="#e9f0f7")

        self.database = 'data.db'
        self.conn = sqlite3.connect(self.database)
        self.cursor = self.conn.cursor()
        self.init_db()

        self.current_student = None  # (name, index_number)
        self.current_year = 'Year 1'
        self.current_semester = 'Semester 1'
        self.entries = []

        self.style = ttk.Style(self.root)
        self.configure_style()
        self.build_ui()

    def init_db(self):
        # Create students table with index_number UNIQUE
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                index_number TEXT UNIQUE NOT NULL,
                UNIQUE(name, index_number)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                year TEXT, semester TEXT, 
                course_name TEXT, grade TEXT, credits REAL,
                FOREIGN KEY(student_id) REFERENCES students(id)
            )
        """)
        self.conn.commit()

    def configure_style(self):
        # Overall theme colors
        primary_color = "#2a62bc"
        primary_dark = "#204a86"
        secondary_color = "#f39c12"
        bg_color = "#e9f0f7"
        text_color = "#333333"
        accent_bg = "#f7f9fc"
        border_color = "#cbd4db"

        default_font = ("Inter", 11)
        header_font = ("Inter", 13, "bold")

        self.style.theme_use('clam')

        self.style.configure("TFrame", background=bg_color)
        self.style.configure("TLabel",
                             font=default_font,
                             background=bg_color,
                             foreground=text_color)
        self.style.configure("Header.TLabel",
                             font=header_font,
                             background=bg_color,
                             foreground=primary_color)
        self.style.configure("TButton",
                             font=default_font,
                             padding=8,
                             background=primary_color,
                             foreground="white")
        self.style.map("TButton",
                       background=[('pressed', primary_dark), ('active', primary_dark)])

        self.style.configure("Primary.TButton",
                             font=default_font,
                             padding=10,
                             background=primary_color,
                             foreground="white",
                             relief="flat")
        self.style.map("Primary.TButton",
                       background=[('pressed', primary_dark), ('active', primary_dark)])

        self.style.configure("Secondary.TButton",
                             font=default_font,
                             padding=10,
                             background="#8a9ba8",
                             foreground="white",
                             relief="flat")
        self.style.map("Secondary.TButton",
                       background=[('pressed', '#6a7a8a'), ('active', '#6a7a8a')])

        self.style.configure("TCombobox",
                             padding=6,
                             relief="flat",
                             selectbackground=primary_color,
                             fieldbackground=accent_bg,
                             background=bg_color)
        self.style.map("TCombobox",
                       fieldbackground=[('readonly', accent_bg)],
                       selectbackground=[('readonly', primary_color)])

        self.style.configure("Horizontal.TScrollbar",
                             troughcolor=accent_bg,
                             background=primary_color,
                             bordercolor=border_color,
                             arrowcolor=primary_color)

        self.style.configure("Treeview.Heading",
                             font=header_font,
                             background=primary_color,
                             foreground="white",
                             relief="flat")
        self.style.map("Treeview.Heading",
                       background=[('active', primary_dark)])

        self.style.configure("Treeview",
                             font=default_font,
                             background=accent_bg,
                             fieldbackground=accent_bg,
                             foreground=text_color,
                             bordercolor=border_color,
                             lightcolor=border_color,
                             darkcolor=border_color,
                             rowheight=28)
        self.style.map("Treeview",
                       background=[('selected', primary_color)],
                       foreground=[('selected', "white")])

        self.style.configure("Dialog.TFrame", background=bg_color)

    def build_ui(self):
        container = ttk.Frame(self.root, padding=16, style="TFrame")
        container.pack(fill="both", expand=True)

        # Student Management Frame
        student_frame = ttk.LabelFrame(container, text="Student Management", padding=16, style="TFrame")
        student_frame.grid(row=0, column=0, sticky="ew", pady=(0,16))
        student_frame.columnconfigure(1, weight=1)

        ttk.Label(student_frame, text="Select Student:", style="Header.TLabel").grid(row=0, column=0, sticky="w", padx=(0,10))
        self.student_combo = ttk.Combobox(student_frame, state="normal", width=40, font=("Inter", 11))
        self.student_combo.grid(row=0, column=1, sticky="ew", pady=4)
        self.student_combo.bind('<KeyRelease>', self.filter_students)

        ttk.Button(student_frame, text="Add Student", command=self.add_student, style="Primary.TButton").grid(row=0, column=2, padx=8, pady=4)
        ttk.Button(student_frame, text="Edit Student", command=self.edit_student, style="Primary.TButton").grid(row=0, column=3, padx=8, pady=4)
        ttk.Button(student_frame, text="Delete Student", command=self.delete_student, style="Secondary.TButton").grid(row=0, column=4, padx=8, pady=4)
        ttk.Button(student_frame, text="Select", command=self.select_student, style="Primary.TButton").grid(row=0, column=5, padx=8, pady=4)

        # Year & Semester Frame
        sem_frame = ttk.LabelFrame(container, text="Year & Semester", padding=16, style="TFrame")
        sem_frame.grid(row=1, column=0, sticky="ew", pady=(0,16))
        sem_frame.columnconfigure(2, weight=1)

        ttk.Label(sem_frame, text="Year:", style="Header.TLabel").grid(row=0, column=0, sticky="w", padx=(0,10))
        self.year_var = tk.StringVar(value=self.current_year)
        year_combo = ttk.Combobox(sem_frame, textvariable=self.year_var,
                                  values=[f'Year {i}' for i in range(1, 6)],
                                  width=12, state="readonly", style="TCombobox")
        year_combo.grid(row=0, column=1, sticky="w", padx=(0,16), pady=4)

        ttk.Label(sem_frame, text="Semester:", style="Header.TLabel").grid(row=0, column=2, sticky="w", padx=(0,10))
        self.semester_var = tk.StringVar(value=self.current_semester)
        semester_combo = ttk.Combobox(sem_frame, textvariable=self.semester_var,
                                      values=["Semester 1", "Semester 2", "Summer"],
                                      width=12, state="readonly", style="TCombobox")
        semester_combo.grid(row=0, column=3, sticky="w", padx=(0,16), pady=4)

        ttk.Button(sem_frame, text="Load Courses", command=self.load_courses, style="Primary.TButton").grid(row=0, column=4, sticky="w", pady=4)

        # Courses Frame (Scrollable)
        self.course_frame = ttk.LabelFrame(container, text="Courses", padding=16, style="TFrame")
        self.course_frame.grid(row=2, column=0, sticky="nsew", pady=(0,16))
        container.rowconfigure(2, weight=1)

        self.course_canvas = tk.Canvas(self.course_frame, borderwidth=0, highlightthickness=0, background="#f7f9fc")
        self.course_scroll = ttk.Scrollbar(self.course_frame, orient="vertical", command=self.course_canvas.yview, style="Vertical.TScrollbar")
        self.course_inner = ttk.Frame(self.course_canvas, style="TFrame")

        self.course_inner.bind("<Configure>", lambda e: self.course_canvas.configure(scrollregion=self.course_canvas.bbox("all")))
        self.course_canvas.create_window((0, 0), window=self.course_inner, anchor="nw")
        self.course_canvas.configure(yscrollcommand=self.course_scroll.set)
        self.course_canvas.pack(side="left", fill="both", expand=True)
        self.course_scroll.pack(side="right", fill="y")

        # Course List Headers
        header = ['Course Name', 'Grade', 'Credits', 'Action']
        for idx, text in enumerate(header):
            lbl = ttk.Label(self.course_inner, text=text, style="Header.TLabel", background="#e0e6ef", padding=4, relief="flat")
            lbl.grid(row=0, column=idx, sticky="w", padx=8, pady=6, ipadx=4, ipady=4)

        self.add_course_row()

        # Bottom Buttons Frame
        bottom_frame = ttk.Frame(container, style="TFrame")
        bottom_frame.grid(row=3, column=0, sticky="ew")
        bottom_frame.columnconfigure((0,1,2,3,4,5), weight=1)

        ttk.Button(bottom_frame, text="Add Course", command=self.add_course_row, style="Primary.TButton").grid(row=0, column=0, padx=5, pady=10, sticky="ew")
        ttk.Button(bottom_frame, text="Save Courses", command=self.save_courses, style="Primary.TButton").grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        ttk.Button(bottom_frame, text="Clear Courses", command=self.clear_course_rows, style="Secondary.TButton").grid(row=0, column=2, padx=5, pady=10, sticky="ew")
        ttk.Button(bottom_frame, text="Export to Excel", command=self.export_excel, style="Primary.TButton").grid(row=0, column=3, padx=5, pady=10, sticky="ew")
        ttk.Button(bottom_frame, text="Import from Excel", command=self.import_excel, style="Primary.TButton").grid(row=0, column=4, padx=5, pady=10, sticky="ew")
        ttk.Button(bottom_frame, text="Calculate GPA", command=self.calculate_gpa, style="Primary.TButton").grid(row=0, column=5, padx=5, pady=10, sticky="ew")

        # GPA Labels for cumulative and semester
        gpa_frame = ttk.Frame(container, style="TFrame")
        gpa_frame.grid(row=4, column=0, sticky="w", pady=8)
        self.gpa_label = ttk.Label(gpa_frame, text="", font=("Inter", 16, "bold"), foreground="#2a62bc", background="#e9f0f7")
        self.gpa_label.grid(row=0, column=0, sticky="w", padx=(0,30))
        self.sem_gpa_label = ttk.Label(gpa_frame, text="", font=("Inter", 16, "bold"), foreground="#204a86", background="#e9f0f7")
        self.sem_gpa_label.grid(row=0, column=1, sticky="w")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Load students after the UI is fully built
        self.load_students()

    def filter_students(self, event):
        pattern = self.student_combo.get().lower()
        self.cursor.execute("SELECT name, index_number FROM students ORDER BY name")
        students = self.cursor.fetchall()
        filtered = [f"{idx} - {name}" for name, idx in students if pattern in name.lower() or pattern in idx.lower()]
        self.student_combo['values'] = filtered

    def load_students(self):
        self.cursor.execute("SELECT name, index_number FROM students ORDER BY name")
        students = self.cursor.fetchall()
        display_values = [f"{idx} - {name}" for name, idx in students]
        self.student_combo['values'] = display_values
        if students:
            self.student_combo.current(0)
            selected = students[0]
            self.current_student = (selected[0], selected[1])
            self.load_courses()
        else:
            self.student_combo.set('')
            self.current_student = None
            self.clear_entries()
            self.gpa_label.config(text="")
            self.sem_gpa_label.config(text="")

    def parse_student(self, display_text):
        try:
            parts = display_text.split(" - ", 1)
            if len(parts) == 2:
                index_number = parts[0].strip()
                name = parts[1].strip()
                return (name, index_number)
        except Exception:
            pass
        return None

    def add_student(self):
        dialog = AddStudentDialog(self.root)
        self.root.wait_window(dialog)
        if dialog.result:
            name, index_number = dialog.result
            try:
                self.cursor.execute("INSERT INTO students (name, index_number) VALUES (?, ?)", (name, index_number))
                self.conn.commit()
                self.load_students()
                messagebox.showinfo("Success", f"Student '{name}' (Index: {index_number}) added.", parent=self.root)
            except sqlite3.IntegrityError as e:
                if "UNIQUE" in str(e).upper():
                    messagebox.showwarning("Exists", "Student name or index number already exists! Use unique index numbers.", parent=self.root)
                else:
                    messagebox.showerror("Error", "Database error: " + str(e), parent=self.root)

    def edit_student(self):
        selected = self.student_combo.get()
        if not selected:
            messagebox.showwarning("Warning", "No student selected to edit.", parent=self.root)
            return
        student = self.parse_student(selected)
        if not student:
            messagebox.showerror("Error", "Selected student format invalid.", parent=self.root)
            return
        name, index_number = student

        dialog = AddStudentDialog(self.root, name, index_number)
        self.root.wait_window(dialog)
        if dialog.result:
            new_name, new_index = dialog.result
            if (new_name, new_index) == (name, index_number):
                return  # No change
            try:
                # Update statement with unique constraint handling
                self.cursor.execute("UPDATE students SET name=?, index_number=? WHERE name=? AND index_number=?",
                                    (new_name, new_index, name, index_number))
                self.conn.commit()
                self.load_students()
                self.gpa_label.config(text="")
                self.sem_gpa_label.config(text="")
                messagebox.showinfo("Updated", f"Student changed to '{new_name}' (Index: {new_index}).", parent=self.root)
            except sqlite3.IntegrityError as e:
                if "UNIQUE" in str(e).upper():
                    messagebox.showwarning("Exists", "New student name or index number conflicts with existing record.", parent=self.root)
                else:
                    messagebox.showerror("Error", "Database error: " + str(e), parent=self.root)

    def delete_student(self):
        selected = self.student_combo.get()
        if not selected:
            messagebox.showwarning("Warning", "No student selected.", parent=self.root)
            return
        student = self.parse_student(selected)
        if not student:
            messagebox.showerror("Error", "Selected student format invalid.", parent=self.root)
            return
        name, index_number = student
        confirm = messagebox.askyesno("Confirm", f"Delete student '{name}' with Index Number '{index_number}' and all related data?", parent=self.root)
        if confirm:
            self.cursor.execute("SELECT id FROM students WHERE name=? AND index_number=?", (name, index_number))
            res = self.cursor.fetchone()
            if not res:
                messagebox.showerror("Error", "Student not found in the database.", parent=self.root)
                return
            student_id = res[0]
            self.cursor.execute("DELETE FROM courses WHERE student_id=?", (student_id,))
            self.cursor.execute("DELETE FROM students WHERE id=?", (student_id,))
            self.conn.commit()
            self.load_students()
            self.clear_entries()
            self.current_student = None
            self.gpa_label.config(text="")
            self.sem_gpa_label.config(text="")
            messagebox.showinfo("Deleted", f"Student '{name}' (Index: {index_number}) and all data deleted.", parent=self.root)

    def select_student(self):
        selected = self.student_combo.get()
        if not selected:
            messagebox.showwarning("Warning", "Select a student first.", parent=self.root)
            return
        student = self.parse_student(selected)
        if not student:
            messagebox.showerror("Error", "Selected student format invalid.", parent=self.root)
            return
        self.current_student = student  # (name, index)
        self.load_courses()

    def load_courses(self):
        if not self.current_student:
            messagebox.showwarning("Warning", "Please select a student first.", parent=self.root)
            return
        self.clear_entries()
        self.gpa_label.config(text="")
        self.sem_gpa_label.config(text="")
        name, index_number = self.current_student
        self.cursor.execute("""
            SELECT id FROM students WHERE name=? AND index_number=?
        """, (name, index_number))
        student_id_res = self.cursor.fetchone()
        if not student_id_res:
            messagebox.showerror("Error", "Selected student does not exist in database.", parent=self.root)
            return
        student_id = student_id_res[0]
        self.cursor.execute("""
            SELECT course_name, grade, credits FROM courses 
            WHERE student_id=? AND year=? AND semester=?
        """, (student_id, self.year_var.get(), self.semester_var.get()))
        rows = self.cursor.fetchall()
        if rows:
            for row in rows:
                self.add_course_row(*row)
        else:
            self.add_course_row()

    def add_course_row(self, cname='', grade='A', credits=''):
        row = len(self.entries) + 1
        bg_color = "#f9f9f9" if row % 2 == 0 else "#ffffff"

        name_entry = ttk.Entry(self.course_inner, width=30)
        name_entry.grid(row=row, column=0, padx=8, pady=4, sticky="ew")
        name_entry.insert(0, cname)
        name_entry.configure(background=bg_color)

        grade_var = tk.StringVar(value=grade)
        grade_combo = ttk.Combobox(self.course_inner,
                                  textvariable=grade_var,
                                  values=list(grade_points.keys()),
                                  width=5,
                                  state="readonly")
        grade_combo.grid(row=row, column=1, padx=8, pady=4, sticky="ew")
        grade_combo.configure(background=bg_color)

        credits_entry = ttk.Entry(self.course_inner, width=10)
        credits_entry.grid(row=row, column=2, padx=8, pady=4, sticky="ew")
        credits_entry.insert(0, credits)
        credits_entry.configure(background=bg_color)

        del_button = ttk.Button(self.course_inner, text="Delete", command=lambda: self.confirm_delete_row(row - 1), width=8)
        del_button.grid(row=row, column=3, padx=8, pady=4)

        # Bind validation on credits_entry for float and grade combo selection event
        credits_entry.bind("<FocusOut>", lambda e, ent=credits_entry, cname=name_entry: self.validate_credits(ent, cname))
        grade_combo.bind("<<ComboboxSelected>>", lambda e, var=grade_var, cname=name_entry: self.validate_grade(var, cname))

        self.entries.append((name_entry, grade_var, credits_entry, del_button))

    def confirm_delete_row(self, idx):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this course?"):
            self.delete_row(idx)

    def validate_credits(self, entry_widget, cname_widget):
        val = entry_widget.get().strip()
        if val == '':
            return True  # allow empty to be caught by save
        try:
            val_f = float(val)
            if val_f <= 0:
                raise ValueError
            entry_widget.configure(foreground='black')
            return True
        except ValueError:
            messagebox.showwarning("Invalid Input", f"Invalid credits value '{val}' for course '{cname_widget.get()}'. Enter positive number.", parent=self.root)
            entry_widget.focus_set()
            entry_widget.configure(foreground='red')
            return False

    def validate_grade(self, var, cname_widget):
        val = var.get()
        if val not in grade_points:
            messagebox.showwarning("Invalid Grade", f"Invalid grade '{val}' for course '{cname_widget.get()}'. Please select a valid grade.", parent=self.root)
            return False
        return True

    def delete_row(self, idx):
        for widget in self.entries[idx]:
            widget.destroy()
        self.entries.pop(idx)
        self.reorder_entries()

    def reorder_entries(self):
        data = [(e[0].get(), e[1].get(), e[2].get()) for e in self.entries]
        for widget in self.course_inner.winfo_children():
            widget.destroy()
        self.entries.clear()

        header = ['Course Name', 'Grade', 'Credits', 'Action']
        for idx, text in enumerate(header):
            lbl = ttk.Label(self.course_inner, text=text, style="Header.TLabel",
                            background="#e0e6ef", padding=4, relief="flat")
            lbl.grid(row=0, column=idx, sticky="w", padx=8, pady=6, ipadx=4, ipady=4)
        for d in data:
            self.add_course_row(*d)

    def clear_entries(self):
        for widget in self.course_inner.winfo_children():
            widget.destroy()
        self.entries.clear()
        header = ['Course Name', 'Grade', 'Credits', 'Action']
        for idx, text in enumerate(header):
            lbl = ttk.Label(self.course_inner, text=text, style="Header.TLabel",
                            background="#e0e6ef", padding=4, relief="flat")
            lbl.grid(row=0, column=idx, sticky="w", padx=8, pady=6, ipadx=4, ipady=4)
        self.add_course_row()

    def clear_course_rows(self):
        if messagebox.askyesno("Clear Courses", "Are you sure you want to clear all course entries for this year and semester?"):
            self.clear_entries()

    def save_courses(self):
        if not self.current_student:
            messagebox.showwarning("Warning", "Please select a student first.", parent=self.root)
            return
        name, index_number = self.current_student
        self.cursor.execute("SELECT id FROM students WHERE name=? AND index_number=?", (name, index_number))
        student_id_res = self.cursor.fetchone()
        if not student_id_res:
            messagebox.showerror("Error", "Selected student does not exist in database.", parent=self.root)
            return
        student_id = student_id_res[0]
        self.cursor.execute("DELETE FROM courses WHERE student_id=? AND year=? AND semester=?",
                            (student_id, self.year_var.get(), self.semester_var.get()))
        for name_entry, grade_var, credits_entry, _ in self.entries:
            cname, grade, credits = name_entry.get().strip(), grade_var.get().strip(), credits_entry.get().strip()
            if cname and credits:
                if not self.validate_credits(credits_entry, name_entry):
                    return
                if not self.validate_grade(grade_var, name_entry):
                    return
                try:
                    credits_val = float(credits)
                    self.cursor.execute("INSERT INTO courses (student_id, year, semester, course_name, grade, credits) VALUES (?,?,?,?,?,?)",
                                        (student_id, self.year_var.get(), self.semester_var.get(), cname, grade, credits_val))
                except ValueError:
                    messagebox.showwarning("Invalid Input", f"Invalid credits value for course '{cname}'. Please enter a valid number.", parent=self.root)
                    return
        self.conn.commit()
        messagebox.showinfo("Saved", "Courses saved successfully.", parent=self.root)

    def calculate_gpa(self):
        if not self.current_student:
            messagebox.showwarning("Warning", "Please select a student first.", parent=self.root)
            return
        name, index_number = self.current_student
        self.cursor.execute("SELECT id FROM students WHERE name=? AND index_number=?", (name, index_number))
        student_id_res = self.cursor.fetchone()
        if not student_id_res:
            messagebox.showerror("Error", "Selected student does not exist in database.", parent=self.root)
            return
        student_id = student_id_res[0]

        # Calculate cumulative GPA
        self.cursor.execute("SELECT grade, credits FROM courses WHERE student_id=?", (student_id,))
        data = self.cursor.fetchall()
        total_points, total_credits = 0, 0
        for grade, credits in data:
            total_points += grade_points.get(grade, 0) * credits
            total_credits += credits
        cum_gpa = total_points / total_credits if total_credits else 0
        self.gpa_label.config(text=f"Cumulative GPA: {cum_gpa:.2f} (Credits: {total_credits})")

        # Calculate semester GPA
        self.cursor.execute("""
            SELECT grade, credits FROM courses WHERE student_id=? AND year=? AND semester=?
        """, (student_id, self.year_var.get(), self.semester_var.get()))
        sem_data = self.cursor.fetchall()
        sem_points, sem_credits = 0, 0
        for grade, credits in sem_data:
            sem_points += grade_points.get(grade, 0) * credits
            sem_credits += credits
        sem_gpa = sem_points / sem_credits if sem_credits else 0
        self.sem_gpa_label.config(text=f"{self.year_var.get()} {self.semester_var.get()} GPA: {sem_gpa:.2f} (Credits: {sem_credits})")

    def export_excel(self):
        if not self.current_student:
            messagebox.showwarning("Warning", "Select a student first.", parent=self.root)
            return
        name, index_number = self.current_student
        self.cursor.execute("SELECT id FROM students WHERE name=? AND index_number=?", (name, index_number))
        student_id_res = self.cursor.fetchone()
        if not student_id_res:
            messagebox.showerror("Error", "Selected student does not exist in database.", parent=self.root)
            return
        student_id = student_id_res[0]
        df = pd.read_sql_query("SELECT year, semester, course_name, grade, credits FROM courses WHERE student_id=?", self.conn, params=(student_id,))
        file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if file:
            try:
                df.to_excel(file, index=False)
                messagebox.showinfo("Exported", "Data exported successfully.", parent=self.root)
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export data. Error: {str(e)}", parent=self.root)

    def export_all_gpa_summary(self):
        # Export all students' GPA summary by year and semester
        self.cursor.execute("SELECT id, name, index_number FROM students ORDER BY name")
        students = self.cursor.fetchall()
        records = []
        for student_id, name, idx in students:
            self.cursor.execute("SELECT DISTINCT year, semester FROM courses WHERE student_id=?", (student_id,))
            ys = self.cursor.fetchall()
            for year, semester in ys:
                self.cursor.execute("SELECT grade, credits FROM courses WHERE student_id=? AND year=? AND semester=?", (student_id, year, semester))
                data = self.cursor.fetchall()
                points = 0
                credits = 0
                for grade, cred in data:
                    points += grade_points.get(grade,0) * cred
                    credits += cred
                gpa = points / credits if credits else 0
                records.append({
                    'Name': name,
                    'Index Number': idx,
                    'Year': year,
                    'Semester': semester,
                    'GPA': round(gpa, 3),
                    'Credits': credits
                })
        if not records:
            messagebox.showinfo("No Data", "No GPA records to export.", parent=self.root)
            return
        df = pd.DataFrame(records)
        file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if file:
            try:
                df.to_excel(file, index=False)
                messagebox.showinfo("Exported", "GPA summary exported successfully.", parent=self.root)
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export GPA summary. Error: {str(e)}", parent=self.root)

    def import_excel(self):
        if not self.current_student:
            messagebox.showwarning("Warning", "Select a student first.", parent=self.root)
            return
        file = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if file:
            try:
                df = pd.read_excel(file)
            except Exception as e:
                messagebox.showerror("Import Error", f"Could not read the Excel file. Error: {str(e)}", parent=self.root)
                return
            required_cols = {"year", "semester", "course_name", "grade", "credits"}
            if not required_cols.issubset(df.columns):
                messagebox.showerror("Error", "Invalid file format. Missing required columns.", parent=self.root)
                return
            name, index_number = self.current_student
            self.cursor.execute("SELECT id FROM students WHERE name=? AND index_number=?", (name, index_number))
            student_id_res = self.cursor.fetchone()
            if not student_id_res:
                messagebox.showerror("Error", "Selected student does not exist in database.", parent=self.root)
                return
            student_id = student_id_res[0]
            errors = []
            for idx, row in df.iterrows():
                try:
                    # Validate grade and credits before inserting
                    g = row['grade']
                    c = float(row['credits'])
                    if g not in grade_points or c <= 0:
                        raise ValueError("Invalid grade or credits.")
                    self.cursor.execute("INSERT INTO courses (student_id, year, semester, course_name, grade, credits) VALUES (?,?,?,?,?,?)",
                        (student_id, row['year'], row['semester'], row['course_name'], g, c))
                except Exception as e:
                    errors.append(f"Row {idx+2}: {row.to_dict()} Error: {str(e)}")
            self.conn.commit()
            if errors:
                err_msg = "\n".join(errors)
                messagebox.showwarning("Import Errors", f"Some rows failed to import:\n{err_msg}", parent=self.root)
            else:
                messagebox.showinfo("Imported", "Data imported successfully.", parent=self.root)
            self.load_courses()

if __name__ == '__main__':
    root = tk.Tk()

    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # For Windows DPI awareness
    except Exception:
        pass

    app = GPAApp(root)

    # Add a menu for the new export all GPA summary function
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label='File', menu=file_menu)
    file_menu.add_command(label='Export All GPA Summary', command=app.export_all_gpa_summary)
    file_menu.add_separator()
    file_menu.add_command(label='Exit', command=root.destroy)

    root.mainloop()

