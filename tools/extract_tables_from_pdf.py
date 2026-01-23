import sys
from pathlib import Path
import pdfplumber
import csv

p = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('nbt.3437.pdf')
if not p.exists():
    print('PDF not found:', p)
    raise SystemExit(2)

out_dir = Path('tools/pdf_tables')
out_dir.mkdir(parents=True, exist_ok=True)

with pdfplumber.open(str(p)) as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        if not tables:
            continue
        for j, table in enumerate(tables):
            # write table to CSV
            out = out_dir / f'page_{i+1}_table_{j+1}.csv'
            with out.open('w', newline='', encoding='utf-8') as fh:
                writer = csv.writer(fh)
                for row in table:
                    writer.writerow([cell if cell is not None else '' for cell in row])
            print('Wrote', out)

print('Done')
