import os
from pypdf import PdfReader

pdf_path = r"d:\code\Vocabulary\data\旋元佑英文字彙.pdf"
output_path = r"d:\code\Vocabulary\pdf_sample.txt"

if not os.path.exists(pdf_path):
    print(f"File not found: {pdf_path}")
    exit(1)

reader = PdfReader(pdf_path)
print(f"Total pages: {len(reader.pages)}")

with open(output_path, "w", encoding="utf-8") as f:
    f.write(f"Total pages: {len(reader.pages)}\n\n")
    for page_num in range(min(50, len(reader.pages))):
        page = reader.pages[page_num]
        text = page.extract_text()
        f.write(f"=== Page {page_num} ===\n")
        if text:
            f.write(text)
        else:
            f.write("[No text extracted]\n")
        f.write("\n\n")

print(f"Sample written to {output_path}")
