

import os
import sys

INPUT_FILE = "water_readings.txt"
REPORT_FILE = "billing_report.txt"
ERROR_FILE = "errors.log"

FREE_LIMIT = 6          
BAND2_LIMIT = 20        
RATE_BAND2 = 8.50       
RATE_BAND3 = 12.00      

LOW_LIMIT = 20          
MODERATE_LIMIT = 50     

EXPECTED_FIELDS = 5

def read_file_lines(filename):
    """Return (lines, error_message). Handles a missing/unreadable file."""
    try:
        file = open(filename, "r", encoding="utf-8")
        lines = file.readlines()
        file.close()
        return lines, ""
    except FileNotFoundError:
        return [], "File '" + filename + "' was not found. " \
                   "Place it in the same folder as this program."
    except OSError as problem:
        return [], "Could not read '" + filename + "': " + str(problem)

def clean_fields(line):
    """Split a line on commas and strip whitespace from every field."""
    raw_parts = line.strip().split(",")
    cleaned = []
    for part in raw_parts:
        cleaned.append(part.strip())
    return cleaned


def to_whole_number(text):
    """Convert text to int. Return None if it is not a valid whole number."""
    try:
        return int(text)
    except ValueError:
        return None


def validate_record(fields, accepted):
    """
    Check one record. Returns "" if valid, otherwise the rejection reason.
    'accepted' is the dictionary of valid records so far (duplicate check).
    """

    if len(fields) != EXPECTED_FIELDS:
        return "Wrong number of fields (expected 5, found " + str(len(fields)) + ")"

    meter, name, prev_text, curr_text, area = fields

  
    if meter == "":
        return "Missing meter number"
    if name == "":
        return "Missing household name"
    if prev_text == "":
        return "Missing previous reading"
    if curr_text == "":
        return "Missing current reading"
    if area == "":
        return "Missing area"

   
    if meter in accepted:
        return "Duplicate meter number " + meter

    previous = to_whole_number(prev_text)
    current = to_whole_number(curr_text)
    if previous is None:
        return "Non-numeric previous reading '" + prev_text + "'"
    if current is None:
        return "Non-numeric current reading '" + curr_text + "'"

    if previous < 0:
        return "Negative previous reading (" + str(previous) + ")"
    if current < 0:
        return "Negative current reading (" + str(current) + ")"

    
    if current < previous:
        return "Current reading (" + str(current) + \
               ") is below previous reading (" + str(previous) + ")"

    return ""

def build_records(lines):
    """
    Process every line. Returns (accepted_dict, rejected_list).
    rejected_list items are dictionaries: line number, raw text, reason.
    """
    accepted = {}
    rejected = []
    line_number = 0

    for line in lines:
        line_number = line_number + 1
        if line.strip() == "":                
            continue

        fields = clean_fields(line)
        reason = validate_record(fields, accepted)

        if reason != "":
            rejected.append({"line": line_number,
                             "raw": line.strip(),
                             "reason": reason})
        else:
            meter, name, prev_text, curr_text, area = fields
            accepted[meter] = {"name": name,
                               "previous": int(prev_text),
                               "current": int(curr_text),
                               "area": area}
    return accepted, rejected

def calculate_consumption(previous, current):
    """Q4: monthly consumption in kL."""
    return current - previous


def calculate_bill(kl):
    """Q5: progressive tariff - free / R8.50 / R12.00 bands."""
    if kl <= FREE_LIMIT:
        charge = 0.0
    elif kl <= BAND2_LIMIT:
        charge = (kl - FREE_LIMIT) * RATE_BAND2
    else:
        charge = (BAND2_LIMIT - FREE_LIMIT) * RATE_BAND2 \
                 + (kl - BAND2_LIMIT) * RATE_BAND3
    return charge


def classify_consumption(kl):
    """Q6: LOW / MODERATE / HIGH."""
    if kl <= LOW_LIMIT:
        return "LOW"
    elif kl <= MODERATE_LIMIT:
        return "MODERATE"
    else:
        return "HIGH"


def add_billing_details(accepted):
    """Add consumption, charge and category to every accepted record."""
    for meter in accepted:
        rec = accepted[meter]
        rec["kl"] = calculate_consumption(rec["previous"], rec["current"])
        rec["charge"] = calculate_bill(rec["kl"])
        rec["category"] = classify_consumption(rec["kl"])

def top_five_consumers(accepted):
    """
    Keep a list of the five highest consumers, highest first.
    Each household is compared against the list using loops only.
    Ties keep the household that appeared first in the file.
    """
    top = []  

    for meter in accepted:
        kl = accepted[meter]["kl"]

        position = len(top)
        index = 0
        while index < len(top):
            if kl > top[index][1]:
                position = index
                break
            index = index + 1

       
        if position < 5:
            top.append(None)                       
            shift = len(top) - 1
            while shift > position:               
                top[shift] = top[shift - 1]
                shift = shift - 1
            top[position] = (meter, kl)
            if len(top) > 5:
                top.pop()                        
    return top

def calculate_summary(accepted, rejected):
    """Totals calculated with loops. Returns a dictionary."""
    s = {"accepted": 0, "rejected": len(rejected), "total_kl": 0,
         "total_revenue": 0.0, "LOW": 0, "MODERATE": 0, "HIGH": 0,
         "average_kl": 0.0, "areas": {}}

    for meter in accepted:
        rec = accepted[meter]
        s["accepted"] += 1
        s["total_kl"] += rec["kl"]
        s["total_revenue"] += rec["charge"]
        s[rec["category"]] += 1

        area = rec["area"]
        if area not in s["areas"]:
            s["areas"][area] = {"count": 0, "kl": 0, "revenue": 0.0}
        s["areas"][area]["count"] += 1
        s["areas"][area]["kl"] += rec["kl"]
        s["areas"][area]["revenue"] += rec["charge"]

    if s["accepted"] > 0:
        s["average_kl"] = s["total_kl"] / s["accepted"]
    return s


def write_billing_report(accepted, top, summary, filename=REPORT_FILE):
    """Write billing_report.txt."""
    line = "=" * 98
    out = open(filename, "w", encoding="utf-8")

    out.write(line + "\n")
    out.write("COMMUNITY WATER CONSUMPTION AND BILLING REPORT\n")
    out.write(line + "\n\n")

    out.write("SECTION 1: HOUSEHOLD BILLING DETAILS\n")
    out.write("-" * 98 + "\n")
    out.write("%-7s %-18s %-15s %8s %8s %8s %12s  %s\n" %
              ("Meter", "Household", "Area", "Prev", "Curr", "kL", "Bill (R)", "Category"))
    out.write("-" * 98 + "\n")
    for meter in accepted:
        r = accepted[meter]
        out.write("%-7s %-18s %-15s %8d %8d %8d %12.2f  %s\n" %
                  (meter, r["name"], r["area"], r["previous"], r["current"],
                   r["kl"], r["charge"], r["category"]))

    out.write("\n" + "SECTION 2: TOP 5 HIGHEST-CONSUMING HOUSEHOLDS\n")
    out.write("-" * 98 + "\n")
    out.write("%-5s %-7s %-18s %-15s %8s %12s\n" %
              ("Rank", "Meter", "Household", "Area", "kL", "Bill (R)"))
    rank = 1
    for meter, kl in top:
        r = accepted[meter]
        out.write("%-5d %-7s %-18s %-15s %8d %12.2f\n" %
                  (rank, meter, r["name"], r["area"], kl, r["charge"]))
        rank += 1

    out.write("\n" + "SECTION 3: SUMMARY\n")
    out.write("-" * 98 + "\n")
    out.write("Records accepted        : %d\n" % summary["accepted"])
    out.write("Records rejected        : %d\n" % summary["rejected"])
    out.write("Total consumption       : %d kL\n" % summary["total_kl"])
    out.write("Average consumption     : %.2f kL per household\n" % summary["average_kl"])
    out.write("Total billed revenue    : R%.2f\n" % summary["total_revenue"])
    out.write("LOW households          : %d\n" % summary["LOW"])
    out.write("MODERATE households     : %d\n" % summary["MODERATE"])
    out.write("HIGH households         : %d\n\n" % summary["HIGH"])
    out.write("%-16s %10s %12s %14s\n" % ("Area", "Households", "kL", "Revenue (R)"))
    for area in summary["areas"]:
        a = summary["areas"][area]
        out.write("%-16s %10d %12d %14.2f\n" % (area, a["count"], a["kl"], a["revenue"]))
    out.write(line + "\n")
    out.close()


def write_error_log(rejected, filename=ERROR_FILE):
    """Write errors.log - one entry per rejected record with its reason."""
    out = open(filename, "w", encoding="utf-8")
    out.write("REJECTED RECORDS LOG\n" + "=" * 70 + "\n")
    for item in rejected:
        out.write("Line %d | %s\n    Reason: %s\n" %
                  (item["line"], item["raw"], item["reason"]))
    out.write("=" * 70 + "\nTotal rejected: %d\n" % len(rejected))
    out.close()


def run_pipeline(filename, folder):
    """
    Full workflow. Returns a result dictionary (or one with an 'error' key).
    Output files are written into 'folder'.
    """
    lines, problem = read_file_lines(filename)
    if problem != "":
        return {"error": problem}

    accepted, rejected = build_records(lines)
    add_billing_details(accepted)
    top = top_five_consumers(accepted)
    summary = calculate_summary(accepted, rejected)

    report_path = os.path.join(folder, REPORT_FILE)
    error_path = os.path.join(folder, ERROR_FILE)
    write_billing_report(accepted, top, summary, report_path)
    write_error_log(rejected, error_path)

    return {"error": "", "lines": len(lines), "accepted": accepted,
            "rejected": rejected, "top": top, "summary": summary,
            "report_path": report_path, "error_path": error_path}


def run_console_version():
    """Plain text mode:  python water_billing.py --cli"""
    folder = os.path.dirname(os.path.abspath(__file__))
    result = run_pipeline(os.path.join(folder, INPUT_FILE), folder)
    if result["error"] != "":
        print("ERROR:", result["error"])
        return
    print("Lines read      :", result["lines"])
    print("Records accepted:", result["summary"]["accepted"])
    print("Records rejected:", result["summary"]["rejected"])
    print("Top 5 consumers :")
    rank = 1
    for meter, kl in result["top"]:
        print("  %d. %s %-18s %d kL" % (rank, meter, result["accepted"][meter]["name"], kl))
        rank += 1
    print("Created:", REPORT_FILE, "and", ERROR_FILE)

def launch_gui():
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox

    NAVY, BLUE, LIGHT = "#0b2545", "#13a8e0", "#eef4fb"
    WHITE, TEXT, MUTED = "#ffffff", "#1c2b3a", "#6b7c8f"
    GREEN, AMBER, RED = "#1f9d6b", "#e8a317", "#d64545"
    CAT_COLOUR = {"LOW": GREEN, "MODERATE": AMBER, "HIGH": RED}
    CAT_BG = {"LOW": "#e3f6ee", "MODERATE": "#fdf3d9", "HIGH": "#fbe3e3"}

    class App:
        def __init__(self, root):
            self.root = root
            self.folder = os.path.dirname(os.path.abspath(__file__))
            self.file_path = os.path.join(self.folder, INPUT_FILE)
            self.result = None

            root.title("Community Water Billing Management System")
            root.geometry("1180x760")
            root.minsize(1000, 640)
            root.configure(bg=LIGHT)
            self.setup_style()
            self.build_header()
            self.build_cards()
            self.build_tabs()
            self.build_statusbar()
            self.process()                     

        def setup_style(self):
            st = ttk.Style()
            try:
                st.theme_use("clam")
            except tk.TclError:
                pass
            st.configure("Treeview", rowheight=26, font=("Segoe UI", 10),
                         background=WHITE, fieldbackground=WHITE, foreground=TEXT,
                         borderwidth=0)
            st.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"),
                         background=NAVY, foreground=WHITE, relief="flat")
            st.map("Treeview.Heading", background=[("active", "#17386b")])
            st.map("Treeview", background=[("selected", BLUE)],
                   foreground=[("selected", WHITE)])
            st.configure("TNotebook", background=LIGHT, borderwidth=0)
            st.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"),
                         padding=(18, 8), background="#d6e2f0", foreground=NAVY)
            st.map("TNotebook.Tab", background=[("selected", WHITE)])
            st.configure("TCombobox", padding=4)

        def button(self, parent, text, command, bg=BLUE):
            b = tk.Button(parent, text=text, command=command, bg=bg, fg=WHITE,
                          activebackground=WHITE, activeforeground=NAVY,
                          font=("Segoe UI", 10, "bold"), relief="flat",
                          padx=14, pady=7, cursor="hand2", bd=0)
            return b

        def build_header(self):
            head = tk.Frame(self.root, bg=NAVY)
            head.pack(fill="x")
            left = tk.Frame(head, bg=NAVY)
            left.pack(side="left", padx=22, pady=14)
            tk.Label(left, text="💧  Water Consumption & Billing", bg=NAVY, fg=WHITE,
                     font=("Segoe UI", 20, "bold")).pack(anchor="w")
            tk.Label(left, text="Municipal household meter readings  •  progressive tariff",
                     bg=NAVY, fg="#9fb8d6", font=("Segoe UI", 10)).pack(anchor="w")
            right = tk.Frame(head, bg=NAVY)
            right.pack(side="right", padx=22)
            self.button(right, "📂 Browse file", self.browse).pack(side="left", padx=4)
            self.button(right, "▶ Process & Generate Reports", self.process,
                        GREEN).pack(side="left", padx=4)

        def build_cards(self):
            row = tk.Frame(self.root, bg=LIGHT)
            row.pack(fill="x", padx=18, pady=(14, 4))
            self.card_vars = {}
            specs = [("accepted", "Accepted", GREEN), ("rejected", "Rejected", RED),
                     ("kl", "Total kL", BLUE), ("revenue", "Revenue", NAVY),
                     ("high", "HIGH users", AMBER)]
            for i in range(len(specs)):
                key, title, colour = specs[i]
                card = tk.Frame(row, bg=WHITE, highlightthickness=1,
                                highlightbackground="#d6e2f0")
                card.grid(row=0, column=i, sticky="nsew", padx=6)
                row.columnconfigure(i, weight=1)
                tk.Frame(card, bg=colour, height=4).pack(fill="x")
                var = tk.StringVar(value="–")
                self.card_vars[key] = var
                tk.Label(card, textvariable=var, bg=WHITE, fg=TEXT,
                         font=("Segoe UI", 20, "bold")).pack(pady=(10, 0))
                tk.Label(card, text=title, bg=WHITE, fg=MUTED,
                         font=("Segoe UI", 10)).pack(pady=(0, 10))

        def build_tabs(self):
            self.tabs = ttk.Notebook(self.root)
            self.tabs.pack(fill="both", expand=True, padx=18, pady=(8, 6))
            self.tab_billing = tk.Frame(self.tabs, bg=WHITE)
            self.tab_top = tk.Frame(self.tabs, bg=WHITE)
            self.tab_errors = tk.Frame(self.tabs, bg=WHITE)
            self.tab_calc = tk.Frame(self.tabs, bg=WHITE)
            self.tab_tests = tk.Frame(self.tabs, bg=WHITE)
            self.tabs.add(self.tab_billing, text="  Billing Records  ")
            self.tabs.add(self.tab_top, text="  🏆 Top 5  ")
            self.tabs.add(self.tab_errors, text="  ⚠ Rejected  ")
            self.tabs.add(self.tab_calc, text="  🧮 Bill Calculator  ")
            self.tabs.add(self.tab_tests, text="  ✔ Test Cases  ")
            self.build_billing_tab()
            self.build_top_tab()
            self.build_errors_tab()
            self.build_calc_tab()
            self.build_tests_tab()

        def make_tree(self, parent, columns, widths):
            frame = tk.Frame(parent, bg=WHITE)
            tree = ttk.Treeview(frame, columns=columns, show="headings")
            for i in range(len(columns)):
                tree.heading(columns[i], text=columns[i])
                tree.column(columns[i], width=widths[i], anchor="w")
            bar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=bar.set)
            tree.pack(side="left", fill="both", expand=True)
            bar.pack(side="right", fill="y")
            for cat in CAT_BG:
                tree.tag_configure(cat, background=CAT_BG[cat])
            tree.tag_configure("odd", background="#f7fafd")
            return frame, tree

        def build_billing_tab(self):
            bar = tk.Frame(self.tab_billing, bg=WHITE)
            bar.pack(fill="x", padx=12, pady=10)
            tk.Label(bar, text="Search", bg=WHITE, fg=MUTED).pack(side="left")
            self.search_var = tk.StringVar()
            self.search_var.trace_add("write", lambda *a: self.refresh_billing())
            tk.Entry(bar, textvariable=self.search_var, width=22, relief="solid",
                     bd=1, font=("Segoe UI", 10)).pack(side="left", padx=(6, 18))
            tk.Label(bar, text="Area", bg=WHITE, fg=MUTED).pack(side="left")
            self.area_var = tk.StringVar(value="All")
            self.area_box = ttk.Combobox(bar, textvariable=self.area_var,
                                         state="readonly", width=16, values=["All"])
            self.area_box.pack(side="left", padx=(6, 18))
            self.area_box.bind("<<ComboboxSelected>>", lambda e: self.refresh_billing())
            tk.Label(bar, text="Category", bg=WHITE, fg=MUTED).pack(side="left")
            self.cat_var = tk.StringVar(value="All")
            cat_box = ttk.Combobox(bar, textvariable=self.cat_var, state="readonly",
                                   width=12, values=["All", "LOW", "MODERATE", "HIGH"])
            cat_box.pack(side="left", padx=6)
            cat_box.bind("<<ComboboxSelected>>", lambda e: self.refresh_billing())
            self.count_var = tk.StringVar()
            tk.Label(bar, textvariable=self.count_var, bg=WHITE, fg=MUTED).pack(side="right")
            cols = ("Meter", "Household", "Area", "Previous", "Current", "kL",
                    "Bill (R)", "Category")
            frame, self.bill_tree = self.make_tree(
                self.tab_billing, cols, (80, 170, 140, 90, 90, 80, 110, 110))
            frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        def build_top_tab(self):
            cols = ("Rank", "Meter", "Household", "Area", "kL", "Bill (R)")
            frame, self.top_tree = self.make_tree(
                self.tab_top, cols, (60, 90, 190, 150, 90, 120))
            frame.pack(fill="x", padx=12, pady=(12, 6))
            self.top_tree.configure(height=5)
            self.chart = tk.Canvas(self.tab_top, bg=WHITE, highlightthickness=0)
            self.chart.pack(fill="both", expand=True, padx=12, pady=8)
            self.chart.bind("<Configure>", lambda e: self.draw_chart())

        def draw_chart(self):
            c = self.chart
            c.delete("all")
            if not self.result or not self.result["top"]:
                return
            top = self.result["top"]
            w, h = c.winfo_width(), c.winfo_height()
            c.create_text(10, 12, anchor="w", text="Top 5 consumers (kL)",
                          font=("Segoe UI", 11, "bold"), fill=NAVY)
            biggest = top[0][1] if top[0][1] > 0 else 1
            left, usable = 190, w - 190 - 70
            band = (h - 40) / 5
            for i in range(len(top)):
                meter, kl = top[i]
                rec = self.result["accepted"][meter]
                y = 34 + i * band
                length = usable * kl / biggest
                c.create_text(left - 10, y + band / 2 - 4, anchor="e",
                              text=meter + "  " + rec["name"],
                              font=("Segoe UI", 10), fill=TEXT)
                c.create_rectangle(left, y + 6, left + length, y + band - 14,
                                   fill=BLUE if i else NAVY, outline="")
                c.create_text(left + length + 8, y + band / 2 - 4, anchor="w",
                              text=str(kl), font=("Segoe UI", 10, "bold"), fill=NAVY)

        def build_errors_tab(self):
            frame, self.err_tree = self.make_tree(
                self.tab_errors, ("Line", "Record", "Reason for rejection"), (60, 380, 460))
            frame.pack(fill="both", expand=True, padx=12, pady=12)

        def build_calc_tab(self):
            box = tk.Frame(self.tab_calc, bg=WHITE)
            box.pack(pady=30)
            tk.Label(box, text="Quick bill calculator", bg=WHITE, fg=NAVY,
                     font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 14))
            tk.Label(box, text="Consumption (kL):", bg=WHITE, fg=TEXT,
                     font=("Segoe UI", 11)).grid(row=1, column=0, sticky="e", padx=8)
            self.calc_var = tk.StringVar(value="25")
            ent = tk.Entry(box, textvariable=self.calc_var, width=10, font=("Segoe UI", 12),
                           relief="solid", bd=1)
            ent.grid(row=1, column=1, sticky="w")
            ent.bind("<Return>", lambda e: self.do_calc())
            self.button(box, "Calculate", self.do_calc).grid(row=2, column=0, columnspan=2, pady=14)
            self.calc_out = tk.Label(box, text="", bg=WHITE, fg=TEXT, justify="left",
                                     font=("Consolas", 11))
            self.calc_out.grid(row=3, column=0, columnspan=2)
            tk.Label(box, text="Tariff: first 6 kL free • next 14 kL @ R8.50 • above 20 kL @ R12.00",
                     bg=WHITE, fg=MUTED, font=("Segoe UI", 9)).grid(row=4, column=0,
                                                                   columnspan=2, pady=14)
            self.do_calc()

        def do_calc(self):
            kl = to_whole_number(self.calc_var.get().strip())
            if kl is None or kl < 0:
                self.calc_out.config(text="Enter a whole number of 0 or more.", fg=RED)
                return
            b1 = 0 if kl <= FREE_LIMIT else (kl if kl < BAND2_LIMIT else BAND2_LIMIT) - FREE_LIMIT
            b2 = 0 if kl <= BAND2_LIMIT else kl - BAND2_LIMIT
            text = ("Free band  (%2d kL x R0.00)  = R%8.2f\n"
                    "Band 2     (%2d kL x R8.50)  = R%8.2f\n"
                    "Band 3     (%2d kL x R12.00) = R%8.2f\n"
                    "-----------------------------------\n"
                    "TOTAL BILL (%s)   = R%8.2f") % (
                        FREE_LIMIT if kl > FREE_LIMIT else kl, 0,
                        b1, b1 * RATE_BAND2, b2, b2 * RATE_BAND3,
                        classify_consumption(kl), calculate_bill(kl))
            self.calc_out.config(text=text, fg=TEXT)

        def build_tests_tab(self):
            tk.Label(self.tab_tests, text="Automated test cases (use for your screenshots)",
                     bg=WHITE, fg=NAVY, font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=14, pady=(14, 4))
            cols = ("Test", "Input", "Expected", "Actual", "Result")
            frame, self.test_tree = self.make_tree(self.tab_tests, cols, (330, 150, 150, 150, 90))
            frame.pack(fill="both", expand=True, padx=12, pady=(4, 6))
            self.test_tree.tag_configure("pass", background="#e3f6ee")
            self.test_tree.tag_configure("fail", background="#fbe3e3")
            self.button(self.tab_tests, "Re-run tests", self.run_tests).pack(pady=(0, 12))
            self.run_tests()

        def run_tests(self):
            for item in self.test_tree.get_children():
                self.test_tree.delete(item)
            tariff = [(0, 0.00), (6, 0.00), (7, 8.50), (20, 119.00),
                      (21, 131.00), (25, 179.00), (50, 479.00), (51, 491.00)]
            for kl, expected in tariff:
                actual = calculate_bill(kl)
                self.add_test("Tariff boundary", str(kl) + " kL",
                              "R%.2f" % expected, "R%.2f" % actual, abs(actual - expected) < 0.001)
            labels = [(20, "LOW"), (21, "MODERATE"), (50, "MODERATE"), (51, "HIGH")]
            for kl, expected in labels:
                actual = classify_consumption(kl)
                self.add_test("Classification boundary", str(kl) + " kL", expected, actual,
                              actual == expected)
            cases = [("M300,A,100,120,X", "", "valid record"),
                     ("M001,Dup,1,5,X", "Duplicate", "duplicate meter"),
                     ("M301,A,,5,X", "Missing", "missing reading"),
                     ("M302,A,abc,5,X", "Non-numeric", "non-numeric"),
                     ("M303,A,-10,5,X", "Negative", "negative reading"),
                     ("M304,A,200,100,X", "below", "reversed reading"),
                     ("M305,A,1,5,", "Missing", "missing area"),
                     ("M306,A,1", "Wrong number", "too few fields")]
            known = {"M001": {}}
            for text, key, label in cases:
                reason = validate_record(clean_fields(text), known)
                ok = (reason == "") if key == "" else (key in reason)
                self.add_test("Validation: " + label, text, "Rejected" if key else "Accepted",
                              "Rejected" if reason else "Accepted", ok)
            demo = {}
            for i in range(8):
                demo["T" + str(i)] = {"kl": [10, 90, 40, 90, 70, 5, 120, 60][i]}
            order = []
            for meter, kl in top_five_consumers(demo):
                order.append(kl)
            self.add_test("Top 5 ranking (manual)", "10,90,40,90,70,5,120,60",
                          "[120, 90, 90, 70, 60]", str(order), order == [120, 90, 90, 70, 60])

        def add_test(self, name, given, expected, actual, passed):
            self.test_tree.insert("", "end", values=(name, given, expected, actual,
                                  "PASS" if passed else "FAIL"),
                                  tags=("pass" if passed else "fail",))

        
        def build_statusbar(self):
            self.status = tk.StringVar(value="Ready")
            bar = tk.Frame(self.root, bg=NAVY)
            bar.pack(fill="x", side="bottom")
            tk.Label(bar, textvariable=self.status, bg=NAVY, fg="#cfe1f5",
                     font=("Segoe UI", 9), anchor="w").pack(side="left", padx=14, pady=6)
            self.button(bar, "Open billing_report.txt", lambda: self.open_file(REPORT_FILE),
                        "#17386b").pack(side="right", padx=6, pady=4)
            self.button(bar, "Open errors.log", lambda: self.open_file(ERROR_FILE),
                        "#17386b").pack(side="right", padx=6, pady=4)

      
        def browse(self):
            path = filedialog.askopenfilename(title="Choose meter reading file",
                                              filetypes=[("Text files", "*.txt"), ("All", "*.*")])
            if path:
                self.file_path = path
                self.process()

        def process(self):
            result = run_pipeline(self.file_path, self.folder)
            if result["error"] != "":
                messagebox.showerror("File problem", result["error"])
                self.status.set("Error: " + result["error"])
                return
            self.result = result
            s = result["summary"]
            self.card_vars["accepted"].set(str(s["accepted"]))
            self.card_vars["rejected"].set(str(s["rejected"]))
            self.card_vars["kl"].set("{:,}".format(s["total_kl"]))
            self.card_vars["revenue"].set("R{:,.0f}".format(s["total_revenue"]))
            self.card_vars["high"].set(str(s["HIGH"]))

            areas = ["All"]
            for area in s["areas"]:
                areas.append(area)
            self.area_box.configure(values=areas)
            self.area_var.set("All")
            self.refresh_billing()
            self.refresh_top()
            self.refresh_errors()
            self.status.set("Read %d lines  |  %d accepted, %d rejected  |  reports written to %s"
                            % (result["lines"], s["accepted"], s["rejected"], self.folder))

        def refresh_billing(self):
            if not self.result:
                return
            for item in self.bill_tree.get_children():
                self.bill_tree.delete(item)
            term = self.search_var.get().strip().lower()
            shown = 0
            for meter in self.result["accepted"]:
                r = self.result["accepted"][meter]
                if self.area_var.get() != "All" and r["area"] != self.area_var.get():
                    continue
                if self.cat_var.get() != "All" and r["category"] != self.cat_var.get():
                    continue
                if term != "" and term not in meter.lower() and term not in r["name"].lower():
                    continue
                self.bill_tree.insert("", "end", values=(
                    meter, r["name"], r["area"], r["previous"], r["current"], r["kl"],
                    "%.2f" % r["charge"], r["category"]), tags=(r["category"],))
                shown += 1
            self.count_var.set("Showing %d of %d households" %
                               (shown, self.result["summary"]["accepted"]))

        def refresh_top(self):
            for item in self.top_tree.get_children():
                self.top_tree.delete(item)
            rank = 1
            for meter, kl in self.result["top"]:
                r = self.result["accepted"][meter]
                self.top_tree.insert("", "end", values=(rank, meter, r["name"], r["area"],
                                     kl, "%.2f" % r["charge"]))
                rank += 1
            self.draw_chart()

        def refresh_errors(self):
            for item in self.err_tree.get_children():
                self.err_tree.delete(item)
            for e in self.result["rejected"]:
                self.err_tree.insert("", "end", values=(e["line"], e["raw"], e["reason"]),
                                     tags=("HIGH",))

        def open_file(self, name):
            path = os.path.join(self.folder, name)
            if not os.path.exists(path):
                messagebox.showinfo("Not found", "Run the processing first.")
                return
            try:
                if sys.platform.startswith("win"):
                    os.startfile(path)
                elif sys.platform == "darwin":
                    os.system('open "' + path + '"')
                else:
                    os.system('xdg-open "' + path + '"')
            except OSError as problem:
                messagebox.showerror("Cannot open", str(problem))

    root = tk.Tk()
    App(root)
    root.mainloop()
if __name__ == "__main__":
    if "--cli" in sys.argv:
        run_console_version()
    else:
        launch_gui()
