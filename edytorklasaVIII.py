import tkinter as tk
from tkinter import messagebox, filedialog
import subprocess
import threading
import os


class PythonEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Editor")
        self.root.geometry("800x600")
        
        # Logo programu
        logo = tk.Label(self.root, text="Bumboksod Editor", font=("Arial", 16, "bold"))
        logo.pack(pady=5)

        # Tekst edytora
        self.text_area = tk.Text(root, wrap="none", font=("Courier New", 12))
        self.text_area.pack(fill=tk.BOTH, expand=1, padx=10, pady=5)

        # Pasek narzędzi
        self.create_toolbar()

        # Menu plików
        self.create_menu()

        # Bind key events
        self.text_area.bind("<KeyRelease>", self.highlight_syntax)

    def create_toolbar(self):
        toolbar = tk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        tk.Button(toolbar, text="New", command=self.new_file, bg="green", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Open", command=self.open_file, bg="blue", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Save", command=self.save_file, bg="orange", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Run", command=self.run_code, bg="red", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(toolbar, text="Feedback", command=self.open_feedback_window, bg="purple", fg="white").pack(side=tk.RIGHT, padx=5)

    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        
        # Zamiast menu File dodano ikonę X
        menu_bar.add_command(label="X", command=self.root.quit)

        self.root.config(menu=menu_bar)

    def open_feedback_window(self):
        feedback_window = tk.Toplevel(self.root)
        feedback_window.title("Feedback")
        feedback_window.geometry("400x300")
        feedback_window.resizable(False, False)

        tk.Label(feedback_window, text="Your Feedback", font=("Arial", 12, "bold")).pack(pady=10)
        feedback_text = tk.Text(feedback_window, height=10, width=40)
        feedback_text.pack(pady=10)

        def save_feedback():
            feedback = feedback_text.get("1.0", "end").strip()
            if feedback:
                # Zapisz feedback do pliku feedback.txt
                try:
                    with open("feedback.txt", "a") as f:
                        f.write(feedback + "\n" + "-" * 50 + "\n")
                    messagebox.showinfo("Thank you", "Your feedback has been saved to feedback.txt!")
                    feedback_window.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Could not save feedback: {str(e)}")
            else:
                messagebox.showwarning("Warning", "Feedback cannot be empty.")

        tk.Button(feedback_window, text="Save", command=save_feedback, bg="green", fg="white").pack(pady=10)

    def new_file(self):
        self.text_area.delete(1.0, "end")

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
                self.text_area.delete(1.0, "end")
                self.text_area.insert(1.0, content)

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python Files", "*.py")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(self.text_area.get(1.0, "end"))

    def run_code(self):
        code = self.text_area.get(1.0, "end")
        temp_file = "temp_script.py"

        # Zapisz kod do tymczasowego pliku
        with open(temp_file, "w") as file:
            file.write(code)

        # Uruchom kod w osobnym wątku
        threading.Thread(target=self.execute_code, args=(temp_file,), daemon=True).start()

    def execute_code(self, script_path):
        try:
            # Ukryj konsolę systemową (dla Windows)
            startupinfo = None
            if os.name == "nt":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            # Uruchom skrypt w nowym procesie
            result = subprocess.run(["python", script_path], startupinfo=startupinfo, capture_output=True, text=True)

            # Usuń plik tymczasowy po wykonaniu
            os.remove(script_path)

            # Wyświetl wynik
            self.display_output(result.stdout, result.stderr)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def display_output(self, stdout, stderr):
        output_window = tk.Toplevel(self.root)
        output_window.title("Output Console")
        output_window.geometry("600x400")

        console_text = tk.Text(output_window, wrap="word", font=("Courier New", 12))
        console_text.pack(fill=tk.BOTH, expand=1, padx=10, pady=10)

        if stdout:
            console_text.insert("end", stdout)
        if stderr:
            console_text.insert("end", "\n" + stderr)

        console_text.configure(state="disabled")

    def highlight_syntax(self, event=None):
        keywords = {"def", "return", "if", "else", "elif", "import", "for", "while", "class", "try", "except", "finally", "with", "as"}
        text = self.text_area.get(1.0, "end")

        # Reset text styling
        self.text_area.tag_remove("keyword", "1.0", "end")

        for word in keywords:
            start_idx = "1.0"
            while True:
                start_idx = self.text_area.search(rf"\b{word}\b", start_idx, stopindex="end", regexp=True)
                if not start_idx:
                    break
                end_idx = f"{start_idx}+{len(word)}c"
                self.text_area.tag_add("keyword", start_idx, end_idx)
                start_idx = end_idx

        self.text_area.tag_config("keyword", foreground="blue", font=("Courier New", 12, "bold"))


if __name__ == "__main__":
    root = tk.Tk()
    editor = PythonEditor(root)
    root.mainloop()
