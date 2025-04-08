import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from colorama import init
import threading
import os
import sys
import queue

# Ensure current directory is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from commands.command_handler import handle_command
from config_loader import load_command_mappings, load_config
from utils.permissions import check_admin_rights

init(autoreset=True)

class AegisShellGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🛡️ AegisShell Terminal")
        self.root.geometry("900x600")
        self.root.configure(bg="#0d0d0d")

        # Styling
        self.font = ("Fira Code", 12)
        self.fg_color = "#00ff88"  # Matrix green
        self.bg_color = "#0d0d0d"
        self.prompt_color = "#1affc6"

        # Output area
        self.output_area = ScrolledText(
            root,
            wrap=tk.WORD,
            font=self.font,
            bg=self.bg_color,
            fg=self.fg_color,
            insertbackground=self.fg_color,
            borderwidth=0,
            highlightthickness=0
        )
        self.output_area.pack(padx=12, pady=12, fill=tk.BOTH, expand=True)
        self.output_area.insert(tk.END, "$ aegis-shell\n", ("prompt",))
        self.output_area.insert(tk.END, "[Aegis] Welcome to the ultimate AI-powered terminal shell.\n", ("output",))
        self.output_area.insert(tk.END, "Type 'exit' to quit.\n\n", ("output",))
        self.output_area.config(state=tk.DISABLED)
        self.output_area.tag_config("prompt", foreground=self.prompt_color)
        self.output_area.tag_config("output", foreground=self.fg_color)
        self.output_area.tag_config("error", foreground="#ff5555")

        # Input field
        self.command_entry = tk.Entry(
            root,
            font=self.font,
            bg="#111111",
            fg="white",
            insertbackground="white",
            relief=tk.FLAT,
            highlightthickness=2,
            highlightcolor=self.prompt_color,
            highlightbackground="#222"
        )
        self.command_entry.pack(fill=tk.X, padx=12, pady=(0, 10))
        self.command_entry.bind("<Return>", self.run_command)
        self.command_entry.focus()

        try:
            self.mappings = load_command_mappings()
            self.print_output(f"DEBUG: Loaded {len(self.mappings)} command mappings")
        except Exception as e:
            self.print_output(f"Error loading mappings: {str(e)}", "error")
            self.mappings = {}
            
        self.config = load_config()

        if not check_admin_rights():
            self.print_output("[Aegis] Warning: Admin rights not detected. Some operations may fail.\n", "error")

    def print_output(self, text, tag="output"):
        self.output_area.config(state=tk.NORMAL)
        self.output_area.insert(tk.END, text + "\n", tag)
        self.output_area.see(tk.END)
        self.output_area.config(state=tk.DISABLED)

    def run_command(self, event=None):
        cmd = self.command_entry.get().strip()
        if cmd.lower() == "exit":
            self.root.quit()
            return
        if cmd == "":
            return

        self.print_output(f"aegis> {cmd}", "prompt")
        self.command_entry.delete(0, tk.END)

        threading.Thread(target=self.execute_command, args=(cmd,)).start()

    def execute_command(self, command):
        import io
        old_stdout = sys.stdout
        sys.stdout = mystdout = io.StringIO()

        try:
            # For GUI, we need to handle user input differently
            # Store the original input function
            original_input = __builtins__.input
            
            # Create a queue for GUI responses
            self.input_queue = queue.Queue()
            
            # Override input to handle GUI input
            def gui_input(prompt):
                self.print_output(prompt, "prompt")
                
                # Create a dialog for input
                dialog = tk.Toplevel(self.root)
                dialog.title("Input Required")
                dialog.geometry("400x150")
                dialog.configure(bg=self.bg_color)
                
                # Add prompt text
                prompt_label = tk.Label(dialog, text=prompt, bg=self.bg_color, fg="white", wraplength=380)
                prompt_label.pack(pady=10)
                
                # Add input field
                input_var = tk.StringVar()
                input_entry = tk.Entry(dialog, textvariable=input_var, width=30, bg="#111", fg="white")
                input_entry.pack(pady=10)
                input_entry.focus_set()
                
                # Add buttons
                button_frame = tk.Frame(dialog, bg=self.bg_color)
                button_frame.pack(pady=10)
                
                def on_ok():
                    self.input_queue.put(input_var.get())
                    dialog.destroy()
                    
                def on_cancel():
                    self.input_queue.put("n")  # Default to "no"
                    dialog.destroy()
                    
                ok_button = tk.Button(button_frame, text="OK", command=on_ok, bg="#1e1e1e", fg="white")
                ok_button.pack(side=tk.LEFT, padx=10)
                
                cancel_button = tk.Button(button_frame, text="Cancel", command=on_cancel, bg="#1e1e1e", fg="white")
                cancel_button.pack(side=tk.LEFT, padx=10)
                
                # Wait for dialog response
                dialog.transient(self.root)
                dialog.grab_set()
                self.root.wait_window(dialog)
                
                # Return user input
                return self.input_queue.get()
            
            # Replace input function
            __builtins__.input = gui_input
            
            # Execute command
            handle_command(command, self.mappings, self.config)
            
            # Restore original input function
            __builtins__.input = original_input
            
        except Exception as e:
            self.print_output(f"[Aegis ERROR] {str(e)}", "error")
        finally:
            # Make sure to restore stdout and input
            sys.stdout = old_stdout
            if 'original_input' in locals():
                __builtins__.input = original_input
                
        output = mystdout.getvalue()
        if output:
            self.print_output(output.strip(), "output")

if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg="#0d0d0d")
    root.iconify()
    root.update()
    root.deiconify()
    app = AegisShellGUI(root)
    root.mainloop()