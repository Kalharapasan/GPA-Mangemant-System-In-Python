
# 📚 GPA Calculator – Multi-Version Archive

This repository contains multiple versions of an evolving **GPA Calculator** application developed using **Python**, **Tkinter**, and **SQLite**. Each version introduces new features, design enhancements, and data handling improvements.

---

## 🔢 Versions Overview

| Version | Key Features |
|---------|--------------|
| V1.0 | Basic student/course management, GPA calculation, Excel support |
| V2.0 | Multi-year GPA, real-time updates, dark mode, SQLite storage |
| V2.1 | UI enhancements, better layout, style consistency |
| V2.2 | Student index number added, improved dialogs, better validation |
| V3.0 | Edit student functionality, live search, scalable UI |
| V3.1 | Material Design UI, icon buttons, export summary, polished styling |

## 🛠️ Installation & Running

### ✅ Requirements

- **Python 3.7+**
- **Libraries Used:**
  - `tkinter` – GUI framework (built-in)
  - `sqlite3` – Database engine (built-in)
  - `pandas` – Excel import/export support (`pip install pandas`)
  - `os`, `sys`, `datetime` – standard libraries

> Most dependencies are built into Python. Only `pandas` needs to be installed manually.


## 📌 Version Summary

### ✅ V1.0 - Basic Multi-Student GPA Tracker
- Student management system (Add/Delete/Select students)
- GPA calculation per semester
- SQLite database for storing students and courses
- Course import/export using Excel
- Simple Tkinter GUI

### ✨ V2.0 - Multi-Year GPA Calculation
- GPA tracked across multiple years and semesters
- Real-time GPA updates
- Persistent semester/cumulative GPA storage
- Enhanced GUI with dark mode toggle
- Total credits tracker
- Data stored using SQLite

### 🎨 V2.1 - UI Refinements & Consistency
- Style consistency using modern fonts (e.g., Inter)
- Refactored layout with padding and spacing
- Responsive elements and themed buttons
- Readable alternating row colors
- Improved GPA result display

### 🧾 V2.2 - Student Index Integration
- Students have unique **index numbers**
- Better UI styling and course scroll behavior
- Database redesigned with `index_number` constraints
- Enhanced Add Student dialog
- Dropdown display: `index - name`

### 🛠️ V3.0 - Edit & Search Capability
- Edit student feature added
- Dynamic student filtering in dropdowns
- Modular Add/Edit dialog
- Resizable and expanded UI
- Enhanced styling with clearer layout

### 🌟 V3.1 - Material Design + Icon Buttons
- Material Design-inspired theme
- Unicode icons (Add, Edit, Delete, Save, Export)
- Enhanced UX with better visual hierarchy
- New GPA summary export feature
- Custom scrollbar and treeview styles
- Fallback font loading mechanism

---

## 🔧 Installation

```bash
# Clone the repo
git clone https://github.com/Kalharapasan/GPA-Mangemant-System-In-Python.git
cd gpa-calculator

# Run a specific version
python V1.0.py   # or V2.2.py, V3.1.py etc.
```

> Requires Python 3.x. Libraries used: `tkinter`, `sqlite3`, `pandas` (for Excel support).

---

### 🚀 Run the Application

To launch a specific version of the app, run:

```bash
python V1.0.py   # Basic GPA calculator with student management
python V2.2.py   # Enhanced version with index numbers
python V3.1.py   # Final version with full feature set and modern UI
```

---

## 🧰 How It Works

- Select or add a student (name + index number in newer versions)
- Choose academic **year** and **semester**
- Enter **course name**, **grade**, and **credits**
- Click **Calculate GPA** to view results
- Save or export course data to Excel
- View cumulative and semester GPA summaries

### 📊 GPA Mapping Table

| Grade | GPA |
|-------|-----|
| A+ / A | 4.0 |
| A− | 3.7 |
| B+ | 3.3 |
| B | 3.0 |
| B− | 2.7 |
| C+ | 2.3 |
| C | 2.0 |
| C− | 1.7 |
| D+ | 1.3 |
| D | 1.0 |
| D− | 0.7 |
| F | 0.0 |

---


## 👤 Author

Developed by **P.R.P.S.Kalhara**

---

## 📄 License

This project is licensed under the **MIT License**.

