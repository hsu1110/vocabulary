import re
import json
from pypdf import PdfReader

pdf_path = r"d:\code\Vocabulary\data\旋元佑英文字彙.pdf"
reader = PdfReader(pdf_path)

def clean_ocr(text):
    # Fix common OCR errors
    text = text.replace("］", "]").replace("［", "[")
    text = text.replace("i去示", "表示").replace("去示", "表示")
    return text

def parse_pages(start_page, end_page):
    current_chapter = "未分類"
    words_data = []
    
    # We will iterate page by page
    for p in range(start_page, end_page):
        text = reader.pages[p].extract_text()
        if not text:
            continue
        text = clean_ocr(text)
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        
        # Check for chapter title
        # E.g., 表示「否定」的字首
        for line in lines[:5]:
            ch_match = re.search(r"表示「([^」]+)」的(字首|字根)", line)
            if ch_match:
                current_chapter = f"表示「{ch_match.group(1)}」的{ch_match.group(2)}"
                break
        
        # Now find words on this page
        # A word line starts with English word, followed by KK phonetics in brackets
        # Let's search for lines starting with letters, followed by bracket [
        i = 0
        while i < len(lines):
            line = lines[i]
            # Match word [phonetic
            word_match = re.match(r"^([a-z\-]{3,})\s+\[([^\]\n]+)\]?", line, re.IGNORECASE)
            if word_match:
                word = word_match.group(1).lower()
                phonetic = "[" + word_match.group(2) + "]"
                
                # Let's gather the blocks for this word
                # We read lines until the next word line or the end of lines
                word_lines = []
                j = i + 1
                while j < len(lines):
                    next_line = lines[j]
                    if re.match(r"^([a-z\-]{3,})\s+\[([^\]\n]+)\]?", next_line, re.IGNORECASE):
                        break
                    # Also skip chapter title lines or page numbers at the bottom
                    if re.search(r"表示「([^」]+)」的(字首|字根)", next_line):
                        break
                    word_lines.append(next_line)
                    j += 1
                
                # Now parse the gathered block of word_lines
                structure = ""
                literal_meaning = ""
                definition = ""
                derivatives = []
                examples = []
                
                # Check if first line of block is syllable structure
                block_idx = 0
                if block_idx < len(word_lines):
                    first_block_line = word_lines[block_idx]
                    # Syllable structures contain multiple | or I or /
                    # E.g., a I typ I ical
                    if len(re.findall(r"[\|I/]\s*", first_block_line)) >= 1 and re.match(r"^[a-z\-I\|/\s\(\)]+$", first_block_line, re.IGNORECASE):
                        structure = first_block_line
                        block_idx += 1
                
                # Next line might be literal meaning and definition
                # E.g., without I type I 形容詞字尾 回 非典型的
                if block_idx < len(word_lines):
                    second_block_line = word_lines[block_idx]
                    if "I" in second_block_line or "/" in second_block_line or "|" in second_block_line:
                        # Split by translation markers like 回 or 國 or El
                        parts = re.split(r"[回國畫圖画E]\s*", second_block_line)
                        literal_meaning = parts[0].strip()
                        if len(parts) > 1:
                            definition = parts[1].strip()
                        block_idx += 1
                    else:
                        # Just definition
                        definition = second_block_line
                        block_idx += 1
                
                # Now scan the rest of the lines for derivatives and examples
                current_eng_ex = ""
                k = block_idx
                while k < len(word_lines):
                    curr_line = word_lines[k]
                    if curr_line.startswith("•"):
                        # Start of example sentence
                        current_eng_ex = curr_line[1:].strip()
                        # Check subsequent lines for English or Chinese translation
                        k += 1
                        zh_ex = ""
                        while k < len(word_lines):
                            next_l = word_lines[k]
                            if next_l.startswith("•") or re.match(r"^[a-z\-]{3,}\s+\[", next_l, re.IGNORECASE):
                                # Hit next example or word, backtrack
                                k -= 1
                                break
                            # If contains Chinese, it is the translation
                            if re.search(r"[\u4e00-\u9fff]", next_l):
                                zh_ex = next_l
                                break
                            else:
                                current_eng_ex += " " + next_l
                            k += 1
                        
                        examples.append({
                            "en": current_eng_ex.strip(),
                            "zh": zh_ex.strip()
                        })
                    elif any(curr_line.startswith(m) for m in ["困", "國", "回", "E", "圖"]):
                        # Derivative word line
                        # e.g., 困 anonymity 國 匿名
                        deriv_match = re.findall(r"([a-z\-]{3,})\s+(?:[回國畫圖畫画]\s*)?([\u4e00-\u9fff\s；，、]+)", curr_line, re.IGNORECASE)
                        for d_word, d_meaning in deriv_match:
                            derivatives.append({
                                "word": d_word.lower(),
                                "meaning": d_meaning.strip()
                            })
                    k += 1
                
                # Fallback if definition was not set
                if not definition and len(word_lines) > 0:
                    # Let's search for any Chinese text in the first few lines that isn't an example or derivative
                    for wl in word_lines[:2]:
                        if re.search(r"[\u4e00-\u9fff]", wl) and not wl.startswith("•") and not any(wl.startswith(m) for m in ["困", "國", "回", "E"]):
                            definition = wl.strip()
                            break
                
                words_data.append({
                    "word": word,
                    "phonetic": phonetic,
                    "structure": structure,
                    "literal_meaning": literal_meaning,
                    "definition": definition,
                    "derivatives": derivatives,
                    "examples": examples,
                    "chapter": current_chapter
                })
                
                # Advance i to j-1
                i = j - 1
            i += 1
            
    return words_data

# Test on pages 42-49
test_words = parse_pages(42, 50)
print(f"Parsed {len(test_words)} words:")
print(json.dumps(test_words[:5], indent=2, ensure_ascii=False))
