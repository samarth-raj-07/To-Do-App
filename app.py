import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os

GOALS_FILE = "custom_pages_goals.json"

class CustomGoalsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📘 Custom Goals Tracker")
        self.root.geometry("750x650")
        self.root.configure(bg="#f4f4f4")

        self.goals = {}  # page_name: list of goals
        self.selected_page = tk.StringVar()
        self.load_goals()

        # Select the first available page or set to empty
        if self.goals:
            self.selected_page.set(list(self.goals.keys())[0])
        else:
            self.goals["To Do"] = []
            self.selected_page.set("To Do")


        self.create_widgets()

    def create_widgets(self):
        title = tk.Label(self.root, text="Goals Tracker", font=("Helvetica", 20, "bold"), bg="#f4f4f4")
        title.pack(pady=10)

        page_frame = tk.Frame(self.root, bg="#f4f4f4")
        page_frame.pack(pady=10)

        tk.Label(page_frame, text="Select Page:", font=("Arial", 12), bg="#f4f4f4").pack(side="left", padx=5)
        options = list(self.goals.keys()) or ["No Pages"]
        self.page_dropdown = tk.OptionMenu(page_frame, self.selected_page, *options, command=self.update_goal_list)

        self.page_dropdown.config(font=("Arial", 11), bg="#e0e0e0")
        self.page_dropdown.pack(side="left")

        add_page_button = tk.Button(page_frame, text="➕ Add Page", command=self.add_page, bg="#dcedc8", font=("Arial", 10))
        add_page_button.pack(side="left", padx=10)

        self.goal_entry = tk.Entry(self.root, width=50, font=("Arial", 12))
        self.goal_entry.pack(pady=5)

        add_button = tk.Button(self.root, text="➕ Add Goal", command=self.add_goal, bg="#aed581", font=("Arial", 11, "bold"))
        add_button.pack(pady=5)

        self.goal_frame = tk.Frame(self.root, bg="#ffffff", bd=1, relief="solid")
        self.goal_frame.pack(pady=10, fill="both", expand=True, padx=20)

        self.summary_label = tk.Label(self.root, text="", font=("Arial", 12, "bold"), bg="#f4f4f4", fg="#333")
        self.summary_label.pack(pady=5)

        btn_frame = tk.Frame(self.root, bg="#f4f4f4")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="✔️ Show Completed", command=self.show_completed_goals, bg="#ce93d8", font=("Arial", 10)).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="🕗 Show Incomplete", command=self.show_incomplete_goals, bg="#90caf9", font=("Arial", 10)).grid(row=0, column=1, padx=10)
        tk.Button(self.root, text="💾 Save All Goals", command=self.save_goals, bg="#ffcc80", font=("Arial", 11, "bold")).pack(pady=5)

        self.update_goal_list()

    def add_page(self):
        new_page = simpledialog.askstring("New Page", "Enter new page name:")
        if new_page and new_page.strip() and new_page not in self.goals:
            self.goals[new_page] = []
            self.selected_page.set(new_page)
            self.refresh_dropdown()
            self.update_goal_list()

    def refresh_dropdown(self):
        menu = self.page_dropdown["menu"]
        menu.delete(0, "end")
        for page in self.goals:
            menu.add_command(label=page, command=lambda value=page: self.set_page(value))

    def set_page(self, page_name):
        self.selected_page.set(page_name)
        self.update_goal_list()

    def update_goal_list(self, *_):
        for widget in self.goal_frame.winfo_children():
            widget.destroy()

        current_page = self.selected_page.get()
        if not current_page:
            return

        for idx, goal_data in enumerate(self.goals.get(current_page, [])):
            frame = tk.Frame(self.goal_frame, bg="#ffffff")
            frame.pack(anchor="w", pady=4, padx=10, fill="x")

            var = tk.BooleanVar(value=goal_data['completed'])

            def toggle_completion(g=goal_data, v=var):
                g['completed'] = v.get()
                self.update_goal_list()

            cb = tk.Checkbutton(frame, variable=var, command=toggle_completion, bg="#ffffff")
            cb.pack(side="left")

            style = {
                "font": ("Arial", 11),
                "bg": "#ffffff"
            }

            if goal_data['completed']:
                style["fg"] = "gray"
                style["font"] = ("Arial", 11, "overstrike")

            label = tk.Label(frame, text="✔️ " + goal_data['text'] if goal_data['completed'] else goal_data['text'], **style)
            label.pack(side="left", padx=5)

            del_button = tk.Button(frame, text="❌", command=lambda i=idx: self.delete_goal(i), bg="#ef9a9a", font=("Arial", 9, "bold"))
            del_button.pack(side="right", padx=5)

        self.update_summary()

    def update_summary(self):
        current_page = self.selected_page.get()
        goals = self.goals.get(current_page, [])
        total = len(goals)
        completed = sum(1 for g in goals if g['completed'])

        if total > 0:
            percent = round((completed / total) * 100)
            self.summary_label.config(text=f"{completed}/{total} completed ({percent}%)")
        else:
            self.summary_label.config(text="No goals yet for this page.")

    def add_goal(self):
        goal_text = self.goal_entry.get().strip()
        if goal_text:
            current_page = self.selected_page.get()
            self.goals[current_page].append({'text': goal_text, 'completed': False})
            self.goal_entry.delete(0, tk.END)
            self.update_goal_list()

    def delete_goal(self, index):
        current_page = self.selected_page.get()
        del self.goals[current_page][index]
        self.update_goal_list()

    def save_goals(self):
        try:
            with open(GOALS_FILE, 'w') as f:
                json.dump(self.goals, f, indent=4)
            messagebox.showinfo("Success", "Goals saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def load_goals(self):
        if os.path.exists(GOALS_FILE):
            try:
                with open(GOALS_FILE, 'r') as f:
                    self.goals = json.load(f)
            except Exception as e:
                print(f"Error loading goals: {e}")

    def show_completed_goals(self):
        self._show_goals_by_status(True)

    def show_incomplete_goals(self):
        self._show_goals_by_status(False)

    def _show_goals_by_status(self, completed=True):
        status = "Completed" if completed else "Incomplete"
        popup = tk.Toplevel(self.root)
        popup.title(f"{status} Goals - {self.selected_page.get()}")
        popup.geometry("400x300")
        popup.configure(bg="#ffffff")

        goals = [g['text'] for g in self.goals.get(self.selected_page.get(), []) if g['completed'] == completed]

        if not goals:
            tk.Label(popup, text=f"No {status.lower()} goals yet.", bg="#ffffff", font=("Arial", 12)).pack(pady=20)
        else:
            for g in goals:
                tk.Label(popup, text=("✔️ " if completed else "• ") + g, anchor="w", justify="left", font=("Arial", 11), bg="#ffffff").pack(anchor="w", padx=10, pady=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = CustomGoalsApp(root)
    root.mainloop()
