import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import sqlite3
import pandas as pd

# GPA Mapping
grade_points = {
    "A+": 4.0, "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0, "D-": 0.7, "F": 0.0
}

class GPAApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GPA Calculator with Student Management")
        self.root.geometry("1000x700")
        self.root.minsize(900, 650)

        self.database = 'data.db'
        self.conn = sqlite3.connect(self.database)
        self.cursor = self.conn.cursor()
        self.init_db()

        self.current_student = None
        self.current_year = 'Year 1'
        self.current_semester = 'Semester 1'
        self.entries = []

        self.style = ttk.Style(self.root)
        self.configure_style()
        self.build_ui()

    def configure_style(self):
        # Modern font and styles
        default_font = ("Inter", 11)
        header_font = ("Inter", 12, "bold")
        self.style.configure("TLabel", font=default_font)
        self.style.configure("Header.TLabel", font=header_font)
        self.style.configure("TButton",
                             font=default_font,
                             padding=8)
        self.style.configure("Accent.TButton",
                             foreground="white",
                             background="#4a90e2",
                             font=default_font,
                             padding=10)
        self.style.map("Accent.TButton",
                       background=[('active', '#357ABD')])
        self.style.configure("TCombobox", padding=6, relief="flat")
        self.style.configure("Treeview.Heading", font=header_font)
        self.style.configure("Treeview", font=default_font)

    def init_db(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
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

    def build_ui(self):
        # Main container frame with padding
        container = ttk.Frame(self.root, padding=16)
        container.pack(fill="both", expand=True)

        # Student Management Frame
        student_frame = ttk.LabelFrame(container, text="Student Management", padding=16)
        student_frame.grid(row=0, column=0, sticky="ew", pady=(0,16))
        student_frame.columnconfigure(0, weight=1)
        
        # Combobox for students with label
        ttk.Label(student_frame, text="Select Student:", style="Header.TLabel").grid(row=0, column=0, sticky="w", padx=(0,10))
        self.student_combo = ttk.Combobox(student_frame, state="readonly", width=30, font=("Inter", 11))
        self.student_combo.grid(row=0, column=1, sticky="w")
        self.load_students()

        btn_style = "Accent.TButton"
        ttk.Button(student_frame, text="Add Student", command=self.add_student, style=btn_style).grid(row=0, column=2, padx=8)
        ttk.Button(student_frame, text="Delete Student", command=self.delete_student).grid(row=0, column=3, padx=8)
        ttk.Button(student_frame, text="Select", command=self.select_student).grid(row=0, column=4, padx=8)

        # Year & Semester Frame
        sem_frame = ttk.LabelFrame(container, text="Year & Semester", padding=16)
        sem_frame.grid(row=1, column=0, sticky="ew", pady=(0,16))
        sem_frame.columnconfigure(2, weight=1)

        ttk.Label(sem_frame, text="Year:", style="Header.TLabel").grid(row=0, column=0, sticky="w", padx=(0,10))
        self.year_var = tk.StringVar(value=self.current_year)
        year_combo = ttk.Combobox(sem_frame, textvariable=self.year_var, values=[f'Year {i}' for i in range(1, 6)], width=12, state="readonly")
        year_combo.grid(row=0, column=1, sticky="w", padx=(0,16))

        ttk.Label(sem_frame, text="Semester:", style="Header.TLabel").grid(row=0, column=2, sticky="w", padx=(0,10))
        self.semester_var = tk.StringVar(value=self.current_semester)
        semester_combo = ttk.Combobox(sem_frame, textvariable=self.semester_var, values=["Semester 1", "Semester 2", "Summer"], width=12, state="readonly")
        semester_combo.grid(row=0, column=3, sticky="w", padx=(0,16))

        ttk.Button(sem_frame, text="Load Courses", command=self.load_courses, style=btn_style).grid(row=0, column=4, sticky="w")

        # Courses Frame (Scrollable)
        self.course_frame = ttk.LabelFrame(container, text="Courses", padding=16)
        self.course_frame.grid(row=2, column=0, sticky="nsew", pady=(0,16))
        container.rowconfigure(2, weight=1)

        self.course_canvas = tk.Canvas(self.course_frame, borderwidth=0, highlightthickness=0)
        self.course_scroll = ttk.Scrollbar(self.course_frame, orient="vertical", command=self.course_canvas.yview)
        self.course_inner = ttk.Frame(self.course_canvas)

        self.course_inner.bind("<Configure>", lambda e: self.course_canvas.configure(scrollregion=self.course_canvas.bbox("all")))

        self.course_canvas.create_window((0, 0), window=self.course_inner, anchor="nw")
        self.course_canvas.configure(yscrollcommand=self.course_scroll.set)

        self.course_canvas.pack(side="left", fill="both", expand=True)
        self.course_scroll.pack(side="right", fill="y")

        # Course List Headers
        header = ['Course Name', 'Grade', 'Credits', 'Action']
        for idx, text in enumerate(header):
            lbl = ttk.Label(self.course_inner, text=text, style="Header.TLabel")
            lbl.grid(row=0, column=idx, sticky="w", padx=8, pady=6)

        self.add_course_row()

        # Bottom Buttons Frame
        bottom_frame = ttk.Frame(container)
        bottom_frame.grid(row=3, column=0, sticky="ew")
        bottom_frame.columnconfigure((0,1,2,3,4), weight=1)

        ttk.Button(bottom_frame, text="Add Course", command=self.add_course_row).grid(row=0, column=0, padx=5, pady=10, sticky="ew")
        ttk.Button(bottom_frame, text="Save Courses", command=self.save_courses).grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        ttk.Button(bottom_frame, text="Export to Excel", command=self.export_excel).grid(row=0, column=2, padx=5, pady=10, sticky="ew")
        ttk.Button(bottom_frame, text="Import from Excel", command=self.import_excel).grid(row=0, column=3, padx=5, pady=10, sticky="ew")
        ttk.Button(bottom_frame, text="Calculate GPA", command=self.calculate_gpa, style=btn_style).grid(row=0, column=4, padx=5, pady=10, sticky="ew")

        # GPA display label
        self.gpa_label = ttk.Label(container, text="", font=("Inter", 14, "bold"))
        self.gpa_label.grid(row=4, column=0, sticky="w", pady=4)

        # Responsive resizing support
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def add_student(self):
        name = simpledialog.askstring("Add Student", "Enter student name:", parent=self.root)
        if name:
            try:
                self.cursor.execute("INSERT INTO students (name) VALUES (?)", (name.strip(),))
                self.conn.commit()
                self.load_students()
                messagebox.showinfo("Success", "Student added.")
            except sqlite3.IntegrityError:
                messagebox.showwarning("Exists", "Student already exists!")

    def delete_student(self):
        selected = self.student_combo.get()
        if not selected:
            messagebox.showwarning("Warning", "No student selected.")
            return
        confirm = messagebox.askyesno("Confirm", "Delete student and all related data?")
        if confirm:
            self.cursor.execute("DELETE FROM courses WHERE student_id=(SELECT id FROM students WHERE name=?)", (selected,))
            self.cursor.execute("DELETE FROM students WHERE name=?", (selected,))
            self.conn.commit()
            self.load_students()
            self.clear_entries()
            self.current_student = None
            self.gpa_label.config(text="")

    def load_students(self):
        self.cursor.execute("SELECT name FROM students ORDER BY name")
        students = [row[0] for row in self.cursor.fetchall()]
        self.student_combo['values'] = students
        if students:
            self.student_combo.current(0)
            self.current_student = students[0]
            self.load_courses()

    def select_student(self):
        self.current_student = self.student_combo.get()
        self.load_courses()

    def load_courses(self):
        if not self.current_student:
            messagebox.showwarning("Warning", "Please select a student first.")
            return
        self.clear_entries()
        self.cursor.execute("""
            SELECT course_name, grade, credits FROM courses 
            WHERE student_id=(SELECT id FROM students WHERE name=?) AND year=? AND semester=?
        """, (self.current_student, self.year_var.get(), self.semester_var.get()))
        rows = self.cursor.fetchall()
        if rows:
            for row in rows:
                self.add_course_row(*row)
        else:
            self.add_course_row()

    def add_course_row(self, cname='', grade='A', credits=''):
        row = len(self.entries) + 1
        # Alternate row colors for better readability
        bg_color = "#f9f9f9" if row % 2 == 0 else "#ffffff"

        name_entry = ttk.Entry(self.course_inner, width=30)
        name_entry.grid(row=row, column=0, padx=8, pady=4, sticky="ew")
        name_entry.insert(0, cname)
        name_entry.configure(background=bg_color)
        
        grade_var = tk.StringVar(value=grade)
        grade_combo = ttk.Combobox(self.course_inner, textvariable=grade_var, values=list(grade_points.keys()), width=5, state="readonly")
        grade_combo.grid(row=row, column=1, padx=8, pady=4, sticky="ew")
        grade_combo.configure(background=bg_color)

        credits_entry = ttk.Entry(self.course_inner, width=10)
        credits_entry.grid(row=row, column=2, padx=8, pady=4, sticky="ew")
        credits_entry.insert(0, credits)
        credits_entry.configure(background=bg_color)

        del_button = ttk.Button(self.course_inner, text="Delete", command=lambda: self.delete_row(row - 1), width=8)
        del_button.grid(row=row, column=3, padx=8, pady=4)

        self.entries.append((name_entry, grade_var, credits_entry, del_button))

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
            lbl = ttk.Label(self.course_inner, text=text, style="Header.TLabel")
            lbl.grid(row=0, column=idx, sticky="w", padx=8, pady=6)
        for d in data:
            self.add_course_row(*d)

    def clear_entries(self):
        for widget in self.course_inner.winfo_children():
            widget.destroy()
        self.entries.clear()
        header = ['Course Name', 'Grade', 'Credits', 'Action']
        for idx, text in enumerate(header):
            lbl = ttk.Label(self.course_inner, text=text, style="Header.TLabel")
            lbl.grid(row=0, column=idx, sticky="w", padx=8, pady=6)
        self.add_course_row()

    def save_courses(self):
        if not self.current_student:
            messagebox.showwarning("Warning", "Please select a student first.")
            return
        student_id_result = self.cursor.execute("SELECT id FROM students WHERE name=?", (self.current_student,)).fetchone()
        if not student_id_result:
            messagebox.showerror("Error", "Selected student does not exist in the database.")
            return
        student_id = student_id_result[0]
        self.cursor.execute("DELETE FROM courses WHERE student_id=? AND year=? AND semester=?", 
                            (student_id, self.year_var.get(), self.semester_var.get()))
        for name_entry, grade_var, credits_entry, _ in self.entries:
            name, grade, credits = name_entry.get().strip(), grade_var.get().strip(), credits_entry.get().strip()
            if name and credits:
                try:
                    credits_val = float(credits)
                    self.cursor.execute("INSERT INTO courses (student_id, year, semester, course_name, grade, credits) VALUES (?,?,?,?,?,?)",
                                        (student_id, self.year_var.get(), self.semester_var.get(), name, grade, credits_val))
                except ValueError:
                    messagebox.showwarning("Invalid Input", f"Invalid credits value for course '{name}'. Please enter a valid number.")
                    return
        self.conn.commit()
        messagebox.showinfo("Saved", "Courses saved successfully.")

    def calculate_gpa(self):
        if not self.current_student:
            messagebox.showwarning("Warning", "Please select a student first.")
            return
        student_id_result = self.cursor.execute("SELECT id FROM students WHERE name=?", (self.current_student,)).fetchone()
        if not student_id_result:
            messagebox.showerror("Error", "Selected student does not exist in the database.")
            return
        student_id = student_id_result[0]
        self.cursor.execute("SELECT grade, credits FROM courses WHERE student_id=?", (student_id,))
        data = self.cursor.fetchall()
        total_points, total_credits = 0, 0
        for grade, credits in data:
            total_points += grade_points.get(grade, 0) * credits
            total_credits += credits
        gpa = total_points / total_credits if total_credits else 0
        self.gpa_label.config(text=f"Cumulative GPA: {gpa:.2f} (Credits: {total_credits})")

    def export_excel(self):
        if not self.current_student:
            messagebox.showwarning("Warning", "Select a student first.")
            return
        student_id_result = self.cursor.execute("SELECT id FROM students WHERE name=?", (self.current_student,)).fetchone()
        if not student_id_result:
            messagebox.showerror("Error", "Selected student does not exist in the database.")
            return
        student_id = student_id_result[0]
        df = pd.read_sql_query("SELECT year, semester, course_name, grade, credits FROM courses WHERE student_id=?", self.conn, params=(student_id,))
        file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if file:
            df.to_excel(file, index=False)
            messagebox.showinfo("Exported", "Data exported successfully.")

    def import_excel(self):
        if not self.current_student:
            messagebox.showwarning("Warning", "Select a student first.")
            return
        file = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if file:
            df = pd.read_excel(file)
            required_cols = {"year", "semester", "course_name", "grade", "credits"}
            if not required_cols.issubset(df.columns):
                messagebox.showerror("Error", "Invalid file format. Missing required columns.")
                return
            student_id_result = self.cursor.execute("SELECT id FROM students WHERE name=?", (self.current_student,)).fetchone()
            if not student_id_result:
                messagebox.showerror("Error", "Selected student does not exist in the database.")
                return
            student_id = student_id_result[0]
            for _, row in df.iterrows():
                try:
                    self.cursor.execute("INSERT INTO courses (student_id, year, semester, course_name, grade, credits) VALUES (?,?,?,?,?,?)",
                        (student_id, row['year'], row['semester'], row['course_name'], row['grade'], float(row['credits'])))
                except Exception as e:
                    messagebox.showwarning("Import Error", f"Could not import row: {row.to_dict()}. Error: {str(e)}")
            self.conn.commit()
            messagebox.showinfo("Imported", "Data imported successfully.")
            self.load_courses()

if __name__ == '__main__':
    root = tk.Tk()
    app = GPAApp(root)
    root.mainloop()

