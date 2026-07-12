import os
from pypdf import PdfReader

pdf_path = r"d:\code\Vocabulary\data\旋元佑英文字彙.pdf"
reader = PdfReader(pdf_path)

# Let's inspect the first 40 pages to find the table of contents and where Part 1 starts
out_path = r"d:\code\Vocabulary\find_pages_out.txt"
with open(out_path, "w", encoding="utf-8") as f:
    for page_num in range(40):
        if page_num >= len(reader.pages):
            break
        text = page.extract_text() if (page := reader.pages[page_num]) else ""
        # search for headings
        for line in text.split("\n"):
            line_str = line.strip()
            if any(k in line_str for k in ["Part", "PART", "目", "錄", "字首", "字根"]):
                f.write(f"Page {page_num}: {line_str}\n")

print("Done find_pages.py")
