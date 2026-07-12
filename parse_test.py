import re
from pypdf import PdfReader

pdf_path = r"d:\code\Vocabulary\data\旋元佑英文字彙.pdf"
reader = PdfReader(pdf_path)

# Let's inspect pages 42 to 70
pages_text = []
for p in range(42, 70):
    pages_text.append(reader.pages[p].extract_text())

full_text = "\n".join(pages_text)

# Let's see if we can find words
# Words usually look like: word [phonetic]
# e.g., atypical [e' t1prkJ] or anonymous [内αn;:im;:i s ]
# Let's look for lowercase words (with optional hyphens or spaces) followed by phonetic symbols in square brackets
word_pattern = re.compile(r"^([a-z\-]+)\s+\[([^\]]+)\]", re.MULTILINE)

matches = word_pattern.findall(full_text)
print(f"Found {len(matches)} words:")
for word, phone in matches[:20]:
    print(f"  {word} : {phone}")
