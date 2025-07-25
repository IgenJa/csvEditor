import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from io import StringIO
import os
import threading

class CSVQuoteAdderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Quote Adder")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        style = ttk.Style()
        style.theme_use('clam')
        
        #frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        #responsive
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        #title
        title_label = ttk.Label(main_frame, text="CSV Quote Adder", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        #input file
        ttk.Label(main_frame, text="Kezelendő fájl:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.input_file_var = tk.StringVar()
        self.input_entry = ttk.Entry(main_frame, textvariable=self.input_file_var, width=40)
        self.input_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 5))
        ttk.Button(main_frame, text="Tallózás", command=self.browse_input_file).grid(row=1, column=2, pady=5)
        
        #output file
        ttk.Label(main_frame, text="Létrehozandó fájl:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.output_file_var = tk.StringVar()
        self.output_entry = ttk.Entry(main_frame, textvariable=self.output_file_var, width=40)
        self.output_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 5))
        ttk.Button(main_frame, text="Tallózás", command=self.browse_output_file).grid(row=2, column=2, pady=5)
        
        #col name
        ttk.Label(main_frame, text="Cella (oszlop) neve:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.column_var = tk.StringVar()
        self.column_entry = ttk.Entry(main_frame, textvariable=self.column_var, width=40)
        self.column_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 5))
        
        #but
        self.process_button = ttk.Button(main_frame, text="Feldolgozás", command=self.start_processing)
        self.process_button.grid(row=4, column=0, columnspan=3, pady=20)
        
        #result
        ttk.Label(main_frame, text="Eredmény:").grid(row=6, column=0, sticky=tk.W, pady=(10, 5))
        
        #scroll
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.result_text = tk.Text(text_frame, height=10, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        #resp
        main_frame.rowconfigure(7, weight=1)
        
    def browse_input_file(self):
        filename = filedialog.askopenfilename(
            title="Válassz bemeneti CSV fájlt",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.input_file_var.set(filename)
            #auto out name
            base_name = os.path.splitext(filename)[0]
            self.output_file_var.set(f"{base_name}_quoted.csv")
    
    def browse_output_file(self):
        filename = filedialog.asksaveasfilename(
            title="Mentés helye",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.output_file_var.set(filename)
    
    def log_message(self, message, color="black"):
        #add to log
        self.result_text.insert(tk.END, message + "\n")
        self.result_text.see(tk.END)
        self.root.update_idletasks()
    
    def start_processing(self):
        #validate
        if not self.input_file_var.get():
            messagebox.showerror("Hiba", "Válassz bemeneti fájlt!")
            return
        
        if not self.output_file_var.get():
            messagebox.showerror("Hiba", "Add meg a kimeneti fájl nevét!")
            return
        
        if not self.column_var.get():
            messagebox.showerror("Hiba", "Add meg az oszlop nevét!")
            return
        
        #but dis
        self.process_button.config(state="disabled")
        self.result_text.delete(1.0, tk.END)
        
        threading.Thread(target=self.process_csv, daemon=True).start()
    
    def process_csv(self):
        try:
            toOpen = self.input_file_var.get()
            toSave = self.output_file_var.get()
            cella = self.column_var.get()
            
            self.log_message(f"Feldolgozás kezdése: {toOpen}")
            
            with open(toOpen, encoding="utf-8") as f:
                lines = f.readlines()
            
            def add_quotes(cell):
                if cell and str(cell).strip() and str(cell).strip() != "None":
                    return f'"{cell};"'
                return cell
            
            processed_lines = []
            current_headers = []
            target_positions = []
            modifications_made = 0
            
            for i, line in enumerate(lines):
                original_line = line
                stripped_line = line.strip()
                
                #just copy
                if not stripped_line or stripped_line.startswith('#') or stripped_line == '-END-':
                    processed_lines.append(original_line)
                    continue
                
                if stripped_line in ['ANALOG', 'DIGITAL']:
                    processed_lines.append(original_line)
                    current_headers = []
                    target_positions = []
                    self.log_message(f"=== {stripped_line} szakasz ===")
                    continue
                
                #headers
                if 'id,' in stripped_line and 'tag_name' in stripped_line:
                    current_headers = [col.strip() for col in stripped_line.split(',')]
                    processed_lines.append(original_line)
                    
                    #find
                    target_positions = []
                    for idx, header in enumerate(current_headers):
                        if header.lower() == cella.lower():
                            target_positions.append(idx)
                    
                    self.log_message(f"'{cella}' oszlop pozíciói: {target_positions}")
                    continue
                
                #proc
                if current_headers and stripped_line.startswith(','):
                    cols = stripped_line.split(',')
                    
                    modified = False
                    for pos in target_positions:
                        if pos < len(cols):
                            original_value = cols[pos]
                            new_value = add_quotes(original_value)
                            if original_value != new_value:
                                cols[pos] = new_value
                                modified = True
                                modifications_made += 1
                    
                    if modified:
                        processed_lines.append(','.join(cols) + '\n')
                    else:
                        processed_lines.append(original_line)
                else:
                    #just copy
                    processed_lines.append(original_line)
            
            #save
            with open(toSave, "w", encoding="utf-8") as f:
                f.writelines(processed_lines)
            
            self.log_message(f"Feldolgozás kész! Eredmény mentve: {toSave}")
            self.log_message(f"Összesen {modifications_made} módosítás történt.")
            
            if modifications_made == 0:
                self.log_message("⚠ Nem történt módosítás!\nEllenőrizze adatok pontosságát!")
            
        except Exception as e:
            self.log_message(f"Hiba: {str(e)}")
            messagebox.showerror("Hiba", f"Hiba történt a feldolgozás során:\n{str(e)}")
        
        finally:
            self.root.after(0, self.finish_processing)
    
    def finish_processing(self):
        self.progress.stop()
        self.process_button.config(state="normal")

def main():
    root = tk.Tk()
    app = CSVQuoteAdderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
