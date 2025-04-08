import sys
import threading
import tkinter as tk
from colorama import Fore

class GuiProgressUpdater:
    """A class to handle download progress updates in the GUI version of AegisShell"""
    
    def __init__(self, output_area):
        self.output_area = output_area
        self.original_stdout = sys.stdout
        self.progress_text = ""
        self.last_line = ""
        
    def write(self, text):
        """Handle writing to ensure progress updates work in GUI"""
        # If text starts with a carriage return, it's a progress update
        if text.startswith('\r'):
            # Store the text for later display
            self.last_line = text[1:]  # Remove the carriage return
            
            # Update the last line in the output area
            self.output_area.config(state=tk.NORMAL)
            
            # Find the last line and replace it
            last_line_index = self.output_area.index("end-1c linestart")
            if self.progress_text:  # If we've already started a progress line
                self.output_area.delete(last_line_index, "end-1c")
                
            # Write the updated line
            self.output_area.insert("end-1c", self.last_line)
            self.output_area.see("end")
            self.output_area.config(state=tk.DISABLED)
            self.progress_text = self.last_line
        else:
            # For normal text, just write it to the original stdout and the output area
            self.original_stdout.write(text)
            self.output_area.config(state=tk.NORMAL)
            self.output_area.insert(tk.END, text)
            self.output_area.see(tk.END)
            self.output_area.config(state=tk.DISABLED)
            self.progress_text = ""  # Reset progress text when a new line is written
            
    def flush(self):
        """Required for any stdout replacement"""
        self.original_stdout.flush()
        
def redirect_stdout_for_gui(output_area):
    """Redirect stdout to handle progress updates in GUI"""
    sys.stdout = GuiProgressUpdater(output_area)
    
def restore_stdout():
    """Restore the original stdout"""
    if hasattr(sys.stdout, 'original_stdout'):
        sys.stdout = sys.stdout.original_stdout