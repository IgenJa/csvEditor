import pandas as pd
from io import StringIO

RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"

toOpen = input("Kezelendő file neve: ") + ".csv"
toSave = input("Létrehozandó file neve: ") + ".csv"
cella = input("Cella (oszlop) neve: ")

with open(toOpen, encoding="utf-8") as f:
    lines = f.readlines()

#kirak ";"
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
    
    #sima sorok masol
    if not stripped_line or stripped_line.startswith('#') or stripped_line == '-END-':
        processed_lines.append(original_line)
        continue
    
    if stripped_line in ['ANALOG', 'DIGITAL']:
        processed_lines.append(original_line)
        current_headers = []
        target_positions = []
        print(f"\n=== {stripped_line} szakasz ===")
        continue
    
    #headerek
    if 'id,' in stripped_line and 'tag_name' in stripped_line:
        current_headers = [col.strip() for col in stripped_line.split(',')]
        processed_lines.append(original_line)
        
        #megkeres cella
        target_positions = []
        for idx, header in enumerate(current_headers):
            if header.lower() == cella.lower():
                target_positions.append(idx)
        
        #print(f"Header: {current_headers[:8]}...")
        print(f"'{cella}' oszlop pozíciói: {target_positions}")
        continue
    
    #feldolgoz
    if current_headers and stripped_line.startswith(','):
        cols = stripped_line.split(',')
        
        #megtalaltakra
        modified = False
        for pos in target_positions:
            if pos < len(cols):
                original_value = cols[pos]
                new_value = add_quotes(original_value)
                if original_value != new_value:
                    cols[pos] = new_value
                    modified = True
                    modifications_made += 1
                    #print(f"  Sor {i+1}, pozíció {pos}: '{original_value}' -> '{new_value}'")
        
        if modified:
            processed_lines.append(','.join(cols) + '\n')
        else:
            processed_lines.append(original_line)
    else:
        #tobbit csak masol
        processed_lines.append(original_line)

with open(toSave, "w", encoding="utf-8") as f:
    f.writelines(processed_lines)

print(f"{GREEN}Feldolgozás kész! Eredmény mentve: {toSave}{RESET}")
print(f"Összesen {modifications_made} módosítás történt.")

if modifications_made == 0:
    print(f"{RED}Nem történt módosítás!\nEllenőrizze adatok pontosságát!{RESET}")