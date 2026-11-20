students = []          

def bubble_sort_desc(items):
    n = len(items)
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            if items[j]["average"] < items[j + 1]["average"]:
                items[j], items[j + 1] = items[j + 1], items[j]
                swapped = True
        if not swapped:
            break
    return items

def get_student(number):
  
    for s in students:
        if s["number"] == number:
            return s
    return None

def check_marks(t1, t2):
    if t1 == "" or t2 == "":
        return False, 0, 0, "Please enter both task marks."
    if not (t1.isdigit() and t2.isdigit()):
        return False, 0, 0, "Marks must be whole numbers."
    t1 = int(t1)
    t2 = int(t2)
    if t1 > 100 or t2 > 100:
        return False, 0, 0, "Marks must be between 0 and 100."
    return True, t1, t2, ""


def find_by_name(text):
    text = text.strip().lower()
    found = []
    if text == "":
        return found
    for s in students:
        if text in s["name"].lower():
            found.append(s)
    return found


def class_average():
    if len(students) == 0:
        return 0
    total = 0
    for s in students:
        total += s["average"]
    return total / len(students)


def highest_average():
    best = 0
    for s in students:
        if s["average"] > best:
            best = s["average"]
    return best

if __name__ == "__main__":
    import tkinter as tk
    from tkinter import ttk, messagebox

    FONT = "Segoe UI"
    NAVY = "#1F3A93"
    BLUE = "#1E88E5"
    GREEN = "#2E9E5B"
    ORANGE = "#F39C12"
    RED = "#E74C3C"
    GREY = "#7F8C8D"
    PAGE_BG = "#F0F4FA"
    CARD_BG = "#FFFFFF"

    def make_button(parent, text, colour, hover, command):
        b = tk.Button(parent, text=text, command=command, bg=colour, fg="white",
                      activebackground=hover, activeforeground="white",
                      font=(FONT, 10, "bold"), relief="flat", bd=0,
                      padx=14, pady=6, cursor="hand2")
        b.bind("<Enter>", lambda e: b.config(bg=hover))
        b.bind("<Leave>", lambda e: b.config(bg=colour))
        return b

    def make_entry(parent, width):
        return tk.Entry(parent, width=width, font=(FONT, 11), relief="solid", bd=1,
                        highlightthickness=2, highlightbackground="#C9D3E3",
                        highlightcolor=BLUE)

    def make_panel(parent, title):
        return tk.LabelFrame(parent, text=" " + title + " ", bg=CARD_BG, fg=NAVY,
                             font=(FONT, 10, "bold"), padx=10, pady=8, bd=1,
                             relief="solid")

    def make_card(parent, title, colour):
        card = tk.Frame(parent, bg=colour, padx=14, pady=8)
        tk.Label(card, text=title, bg=colour, fg="white",
                 font=(FONT, 9)).pack(anchor="w")
        value = tk.Label(card, text="-", bg=colour, fg="white",
                         font=(FONT, 18, "bold"))
        value.pack(anchor="w")
        card.pack(side="left", expand=True, fill="x", padx=5)
        return value

    def set_status(message, kind="info"):
        colours = {"ok": ("#E6F4EA", "#1E7B3A"),
                   "error": ("#FDECEA", "#B3261E"),
                   "info": ("#E8F0FE", NAVY)}
        bg, fg = colours[kind]
        status.config(text="  " + message, bg=bg, fg=fg)

    def warn(title, message):
        set_status(message, "error")
        messagebox.showwarning(title, message)

    def refresh_table(keep_selected=None):
        """Sort the list, redraw the table and update the summary cards."""
        bubble_sort_desc(students)
        for row in table.get_children():
            table.delete(row)
        rank = 1
        for s in students:
            table.insert("", "end", iid=s["number"], values=(
                rank, s["number"], s["name"], s["task1"], s["task2"],
                f"{s['average']:.1f}"))
            rank += 1
        if keep_selected is not None and table.exists(keep_selected):
            table.selection_set(keep_selected)
            table.see(keep_selected)

        count_value.config(text=str(len(students)))
        if len(students) == 0:
            avg_value.config(text="-")
            best_value.config(text="-")
        else:
            avg_value.config(text=f"{class_average():.1f}")
            best_value.config(text=f"{highest_average():.1f}")

    def clear_fields():
        for box in (e_number, e_name, e_task1, e_task2):
            box.delete(0, tk.END)
        e_number.focus()

    def selected_number():
        chosen = table.selection()
        if not chosen:
            messagebox.showinfo("Select a student",
                                "Click a student in the table first.")
            set_status("Click a student in the table first.", "error")
            return None
        return chosen[0]

    def on_select(event):
        chosen = table.selection()
        if not chosen:
            return
        s = get_student(chosen[0])
        if s is None:
            return
        clear_fields()
        e_number.insert(0, s["number"])
        e_name.insert(0, s["name"])
        e_task1.insert(0, s["task1"])
        e_task2.insert(0, s["task2"])
        set_status(f"Selected {s['name']}. Change the Name or marks, then press "
                   "Rename or Re-capture marks.", "info")

    def add_student():
        number = e_number.get().strip()
        name = e_name.get().strip()
        if number == "" or name == "":
            warn("Missing details", "Please enter the student number and name.")
            return
        if not number.isdigit():
            warn("Invalid number", "Student number must be digits only.")
            return
        if get_student(number) is not None:
            warn("Duplicate", "That student number is already in the list.")
            return
        ok, t1, t2, error = check_marks(e_task1.get().strip(), e_task2.get().strip())
        if not ok:
            warn("Invalid marks", error)
            return

        students.append({"number": number, "name": name,
                         "task1": t1, "task2": t2, "average": (t1 + t2) / 2})
        refresh_table()
        clear_fields()
        set_status(f"Added {name}. Total students: {len(students)}", "ok")

    def rename_student():
        number = selected_number()
        if number is None:
            return
        new_name = e_name.get().strip()
        if new_name == "":
            warn("Missing name", "Type the new name in the Name box.")
            return
        s = get_student(number)
        old_name = s["name"]
        s["name"] = new_name
        refresh_table(keep_selected=number)
        set_status(f"Renamed {old_name} to {new_name}.", "ok")

    def recapture_marks():
        number = selected_number()
        if number is None:
            return
        ok, t1, t2, error = check_marks(e_task1.get().strip(), e_task2.get().strip())
        if not ok:
            warn("Invalid marks", error)
            return
        s = get_student(number)
        s["task1"] = t1
        s["task2"] = t2
        s["average"] = (t1 + t2) / 2
        refresh_table(keep_selected=number)
        set_status(f"Marks updated for {s['name']}. New average: {s['average']:.1f}", "ok")

    def find_student():
        text = e_find.get().strip()
        if text == "":
            set_status("Type a name (or part of a name) to find.", "error")
            messagebox.showinfo("Find", "Type a name (or part of a name) to find.")
            return
        matches = find_by_name(text)
        table.selection_remove(table.selection())
        if len(matches) == 0:
            set_status(f'No student found with "{text}" in the name.', "error")
            messagebox.showinfo("Find", f'No student found with "{text}".')
            return
        numbers = []
        for s in matches:
            numbers.append(s["number"])
        table.selection_set(numbers)
        table.see(numbers[0])
        set_status(f'Found {len(matches)} student(s) matching "{text}".', "ok")

    def show_all():
        e_find.delete(0, tk.END)
        table.selection_remove(table.selection())
        set_status("Showing all students.", "info")
        
    def remove_selected():
        number = selected_number()
        if number is None:
            return
        s = get_student(number)
        if not messagebox.askyesno("Remove student",
                                   f"Remove {s['name']} from the list?"):
            return
        students.remove(s)
        refresh_table()
        clear_fields()
        set_status(f"Removed {s['name']}. Total students: {len(students)}", "ok")

    def clear_all():
        if len(students) == 0:
            set_status("The list is already empty.", "info")
            return
        if messagebox.askyesno("Clear all", "Remove EVERY student from the list?"):
            students.clear()
            refresh_table()
            clear_fields()
            set_status("List cleared.", "ok")

 
    root = tk.Tk()
    root.title("Student Results Manager")
    root.geometry("900x740")
    root.minsize(800, 640)
    root.configure(bg=PAGE_BG)


    header = tk.Frame(root, bg=NAVY, padx=20, pady=12)
    header.pack(fill="x")
    tk.Label(header, text="Student Results Manager", bg=NAVY, fg="white",
             font=(FONT, 20, "bold")).pack(anchor="w")
    tk.Label(header, text="Capture marks, find students and see the ranking from "
                          "highest to lowest average",
             bg=NAVY, fg="#BBD0FF", font=(FONT, 10)).pack(anchor="w")

 
    tk.Label(root, bg=PAGE_BG, fg=GREY, font=(FONT, 9), anchor="w", justify="left",
             text="How to use:  1) Fill in the boxes and press Add student     "
                  "2) Click a row to edit it     3) Use Find to search by name"
             ).pack(fill="x", padx=15, pady=(8, 2))

   
    cards = tk.Frame(root, bg=PAGE_BG)
    cards.pack(fill="x", padx=10, pady=5)
    count_value = make_card(cards, "STUDENTS", BLUE)
    avg_value = make_card(cards, "CLASS AVERAGE", GREEN)
    best_value = make_card(cards, "HIGHEST AVERAGE", ORANGE)

  
    form = make_panel(root, "Student details")
    form.pack(fill="x", padx=15, pady=5)

    tk.Label(form, text="Student number", bg=CARD_BG, font=(FONT, 10)).grid(
        row=0, column=0, sticky="w", padx=5)
    tk.Label(form, text="Name", bg=CARD_BG, font=(FONT, 10)).grid(
        row=0, column=1, sticky="w", padx=5)
    tk.Label(form, text="Task 1 mark (0-100)", bg=CARD_BG, font=(FONT, 10)).grid(
        row=0, column=2, sticky="w", padx=5)
    tk.Label(form, text="Task 2 mark (0-100)", bg=CARD_BG, font=(FONT, 10)).grid(
        row=0, column=3, sticky="w", padx=5)

    e_number = make_entry(form, 14)
    e_name = make_entry(form, 20)
    e_task1 = make_entry(form, 14)
    e_task2 = make_entry(form, 14)
    e_number.grid(row=1, column=0, padx=5, pady=(2, 8))
    e_name.grid(row=1, column=1, padx=5, pady=(2, 8))
    e_task1.grid(row=1, column=2, padx=5, pady=(2, 8))
    e_task2.grid(row=1, column=3, padx=5, pady=(2, 8))

    form_buttons = tk.Frame(form, bg=CARD_BG)
    form_buttons.grid(row=2, column=0, columnspan=4, sticky="w", pady=(0, 2))
    make_button(form_buttons, "Add student", GREEN, "#237A46", add_student).pack(
        side="left", padx=5)
    make_button(form_buttons, "Clear boxes", GREY, "#5F6D6E", clear_fields).pack(
        side="left", padx=5)

   
    middle = tk.Frame(root, bg=PAGE_BG)
    middle.pack(fill="x", padx=15, pady=5)

    edit = make_panel(middle, "Edit the selected student (click a row first)")
    edit.pack(side="left", fill="both", expand=True, padx=(0, 5))
    make_button(edit, "Rename student", BLUE, "#1565C0", rename_student).pack(
        side="left", padx=5)
    make_button(edit, "Re-capture marks", BLUE, "#1565C0", recapture_marks).pack(
        side="left", padx=5)
    make_button(edit, "Remove", RED, "#C0392B", remove_selected).pack(
        side="left", padx=5)

    finder = make_panel(middle, "Find by name")
    finder.pack(side="left", fill="both", expand=True, padx=(5, 0))
    e_find = make_entry(finder, 16)
    e_find.pack(side="left", padx=5)
    make_button(finder, "Find", ORANGE, "#D68910", find_student).pack(
        side="left", padx=5)
    make_button(finder, "Show all", GREY, "#5F6D6E", show_all).pack(
        side="left", padx=5)

   
    status = tk.Label(root, text="  Welcome! Enter a student and press Add student.",
                      anchor="w", bg="#E8F0FE", fg=NAVY, font=(FONT, 10), pady=6)
    status.pack(side="bottom", fill="x")

    table_frame = tk.Frame(root, bg=PAGE_BG)
    table_frame.pack(fill="both", expand=True, padx=15, pady=5)

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", rowheight=28, font=(FONT, 10), background="white",
                    fieldbackground="white", foreground="#222222")
    style.configure("Treeview.Heading", font=(FONT, 10, "bold"), background=NAVY,
                    foreground="white", relief="flat", padding=6)
    style.map("Treeview.Heading", background=[("active", BLUE)])
    style.map("Treeview", background=[("selected", BLUE)],
              foreground=[("selected", "white")])

    columns = ("Rank", "Number", "Name", "Task 1", "Task 2", "Average")
    table = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
    widths = (60, 110, 220, 90, 90, 100)
    for col, w in zip(columns, widths):
        table.heading(col, text=col)
        table.column(col, width=w, anchor="center")

    scroll = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
    table.configure(yscrollcommand=scroll.set)
    table.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")
    table.bind("<<TreeviewSelect>>", on_select)

    for box in (e_number, e_name, e_task1, e_task2):
        box.bind("<Return>", lambda event: add_student())
    e_find.bind("<Return>", lambda event: find_student())

    e_number.focus()
    root.mainloop()
