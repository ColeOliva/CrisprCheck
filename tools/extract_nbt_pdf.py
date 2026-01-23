import sys
from pathlib import Path
from PyPDF2 import PdfReader

p = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('nbt.3437.pdf')
if not p.exists():
    print('PDF not found:', p)
    sys.exit(2)

reader = PdfReader(str(p))
all_text = []
for i, page in enumerate(reader.pages):
    text = page.extract_text()
    all_text.append(f'=== PAGE {i+1} ===\n')
    if text:
        all_text.append(text)
    else:
        all_text.append('[no text extracted on this page]')

out = '\n'.join(all_text)
# write to a file for inspection
out_path = p.with_suffix('.txt')
out_path.write_text(out, encoding='utf-8')
print('Wrote extracted text to', out_path)
# print a short preview
print('\n'.join(out.splitlines()[:400]))
