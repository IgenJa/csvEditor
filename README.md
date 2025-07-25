# CSV Column Modifier Script

This Python script searches for a specified column (by name) in CSV files and appends a `;` character to the end of the matching cells.  
The program preserves the original structure of the file and only modifies the targeted column.

---

## Features

- Processes CSV files using UTF-8 encoding
- Searches by column name (case-insensitive)
- Modifies only non-empty cells
- Saves the result into a new file
- Displays the total number of modifications made

---

## Versions

- Simple terminal interface (`csvEditTer.py`)
- Visual interface (`csvEditVis.py`)
