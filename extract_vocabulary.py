import os
import re
import json
from pypdf import PdfReader

pdf_path = r"d:\code\Vocabulary\data\旋元佑英文字彙.pdf"
output_json_path = r"d:\code\Vocabulary\public\vocabulary.json"

if not os.path.exists(pdf_path):
    print(f"File not found: {pdf_path}")
    exit(1)

reader = PdfReader(pdf_path)
print(f"Total PDF pages: {len(reader.pages)}")

exclude_words = {
    "part", "page", "toefl", "tpo", "the", "sars", "and", "but", "for", "with", "from", "after", "fewer",
    "without", "not", "non", "against", "together", "apart", "away", "into", "out", "under", "over",
    "through", "before", "after", "with", "from", "down", "in", "co", "com", "con", "col", "cor",
    "same", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "many",
    "bad", "good", "self", "all", "back", "again", "life", "death", "force", "power", "heavy", "light",
    "across", "towards", "toward", "beside", "between", "behind", "above", "below", "upon", "about",
    "around", "along", "within", "without", "inside", "outside", "into", "onto", "true", "false",
    "born", "death", "life", "earth", "world", "water", "fire", "air", "wind", "empty", "full",
    "far", "near", "high", "low", "great", "small", "equal", "short", "long", "half", "double", "multi",
    "new", "old", "first", "last", "more", "less", "most", "least", "inner", "outer", "upper", "lower",
    "between", "among", "through", "around", "another", "other", "some", "any", "no"
}

ocr_phrase_replacements = {
    "通用主要街": "通用學術",
    "主要街": "學術",
    "主要營": "學習",
    "主要霄": "學習",
    "不部宇": "不識字",
    "不部": "不識",
    "不部字": "不識字",
    "不識宇": "不識字",
    "；有漠": "冷漠",
    "；在莫": "冷漠",
    "不回 l 山": "不關心",
    "不回l山": "不關心",
    "不回 l山": "不關心",
    "黑庭": "無底",
    "擅度": "極度",
    "幢糟": "極糟",
    "妻惱": "萎縮",
    "萎陌": "萎縮",
    "意青": "患有",
    "（王院": "住院",
    "之1羞": "之後",
    "耐l 山": "耐心",
    "同憬": "同樣",
    "國窟": "問題",
    "哥窯": "遊客",
    "白眼前": "被眼前",
    "震需": "震驚",
    "學前字": "學術字",
    "字首分類": "字首分類",
    "字根分類自": "字根分類",
    "字首分期": "字首分類",
    "字首分崩": "字首分類",
    "字根分期": "字根分類",
    "字根分崩": "字根分類",
    "字根分顛": "字根分類",
    "字首分額": "字首分類",
    "字首分想": "字首分類",
    "字根分額": "字根分類",
    "字根分想": "字根分類",
    "字根分顛": "字根分類",
    "字首分顛": "字首分類",
    "字根分部": "字根分類",
    "字首分部": "字首分類",
    "字首分顛": "字首分類",
    "字首分類自": "字首分類",
    "i去示": "表示",
    "去示": "表示",
    "罩字": "單字",
    "罩詞": "單詞",
    "單宇": "單字",
    "生宇": "生字",
    "已程": "已經",
    "虔期": "長期",
    "童民": "貧民",
    "童民區": "貧民區",
    "童窮": "貧窮",
    "童困": "貧困",
    "度理": "處理",
    "度境": "處境",
    "度罰": "處罰",
    "度度": "處處",
    "相度": "相處",
    "度於": "處於",
    "度事": "處事",
    "閣前": "閱讀",
    "闊前": "閱讀",
    "闊覽": "閱覽",
    "闊卷": "閱卷",
    "前書": "讀書",
    "前者": "讀者",
    "前言": "語言",
    "前合": "適合",
    "前擇": "選擇",
    "前佈": "遍佈",
    "前程": "課程",
    "前譯": "翻譯",
    "前讀": "閱讀",
    "前識": "認識",
    "前載": "認識",
    "知載": "知識",
    "前查": "調查",
    "前生": "謀生",
    "保前": "保護",
    "前明": "證明",
    "申前": "申論",
    "學前": "學術",
    "前考": "小考",
    "前題": "考題",
    "前者": "讀者",
    "筒案": "答案",
    "筒答": "回答",
    "口否": "回答",
    "黑限": "無限",
    "黑知": "無知",
    "黑人": "無人",
    "黑法": "無法",
    "黑助": "無助",
    "黑聊": "無聊",
    "黑耐": "無奈",
    "黑耐": "無奈",
    "黑法": "無法",
    "黑疑": "無疑",
    "黑毒": "病毒",
    "黑數": "無數",
    "黑辜": "無辜",
    "黑效": "無效",
    "黑線": "無線",
    "黑邊": "無邊",
    "黑聲": "無聲",
    "黑窮": "無窮",
    "黑力": "無力",
    "黑私": "無私",
    "黑償": "無償",
    "黑情": "無情",
    "黑意": "無意",
    "http": "http", # skip
    "黑神": "無神",
    "黑常": "無常",
    "黑休": "無休",
    "黑關": "無關",
    "黑底": "無底",
    "黑比": "無比",
    "黑期": "無期",
    "黑阻": "無阻",
    "黑畏": "無畏",
    "黑暇": "無暇",
    "黑瑕": "無瑕",
    "黑敵": "無敵",
    "黑雙": "無雙",
    "黑論": "無論",
    "黑用": "無用",
    "黑能": "無能",
    "草生": "學生",
    "大草": "大學",
    "研究草": "研究生",
    "留草": "留學",
    "小草": "小考",
    "字囊": "字彙",
    "字最": "字彙",
    "字羹": "字彙",
    "字靠": "字彙",
    "字聾": "字彙",
    "字最": "字彙",
    "仰們": "你們",
    "兄胃口好": "祝胃口好",
    "而－路 ~I 自凰": "一路順風",
    "開設": "開設",
}

single_char_replacements = {
    "仰": "你",
    "需": "驚",
}

def clean_ocr(text):
    if not text:
        return ""
    text = text.replace("］", "]").replace("［", "[")
    for k, v in ocr_phrase_replacements.items():
        text = text.replace(k, v)
    for k, v in single_char_replacements.items():
        text = re.sub(f"(?<=[\u4e00-\u9fff]){k}", v, text)
        text = re.sub(f"{k}(?=[\u4e00-\u9fff])", v, text)
    return text

def get_word_entry(line):
    # Support known two-word loanword phrases under bon-
    two_word_match = re.match(r"^([hH]on\s+appetit|[hH]on\s+voyage|[bB]on\s+appetit|[bB]on\s+voyage)\s+(.*)$", line)
    if two_word_match:
        return two_word_match.group(1), two_word_match.group(2)
        
    match = re.match(r"^([a-zA-Z\-]{3,})\s+(.*)$", line)
    if not match:
        return None
        
    word = match.group(1)
    rest = match.group(2).strip()
    
    if word.lower() in exclude_words:
        return None
        
    if word.endswith("-"):
        return None
        
    # Check if the rest starts with a standalone separator followed by space (etymology descriptor line)
    if re.match(r"^[I\|/l1]\s+", rest):
        return None
        
    # Check if the rest is a pure root/syllable breakdown structure (e.g. anti I bio I (t)ic)
    if len(re.findall(r"[\|I/l1]\s*", rest)) >= 1 and re.match(r"^[a-zA-Z\-I\|/\s\(\)l1]+$", rest):
        return None
        
    if re.search(r"^[I\|/\s]*[a-zA-Z\s]*[I\|/]\s*(?:形容|名|動|副|名前|形容前|形容嗣|形容祠|字根|字首|字尾)+", rest):
        return None
        
    # Rule A: starts with typical phonetic brackets
    if re.match(r"^[\[［\(L\/]", rest):
        return word, rest
        
    # Rule B: contains trailing bracket ] and doesn't look like an English sentence
    if ("]" in rest or "］" in rest) and not any(w in rest.lower().split() for w in ["the", "of", "and", "to", "in", "that", "was", "were", "with", "is", "are", "have", "had"]):
        return word, rest
        
    # Rule C: starts with POS or definition markers
    if re.match(r"^[圖图~回国圈El]\s*", rest):
        return word, rest
        
    # Rule D: looks like a short phonetic or definition line with markers
    if len(rest) < 35 and any(char in rest for char in ["[", "]", "(", ")", "/", "~", "图", "回", "国", "圈", "El", "L", "；", "、", "形容"]):
        if not any(w in rest.lower().split() for w in ["the", "of", "and", "to", "in", "that", "was", "were", "with", "is", "are", "have", "had"]):
            return word, rest
            
    return None

def parse_line_parts(line):
    # Split by POS/definition markers that have a space before them: \s+[marker]
    raw_parts = re.split(r"\s+[回國国團团圖畫画El1固因圈困園园圓圆]\s*", line)
    parts = [p.strip() for p in raw_parts if p.strip()]
    
    chinese_defs = []
    english_syns = []
    literal_parts = []
    
    for p in parts:
        has_chinese = bool(re.search(r"[\u4e00-\u9fff]", p))
        if has_chinese:
            # If it contains grammar indicators AND it contains English words, it's literal
            if re.search(r"(?:字尾|字首|字根|形容|名|動|副|前)", p) and re.search(r"\b[a-zA-Z]+\b", p):
                literal_parts.append(p)
            elif any(sym in p.split() for sym in ["I", "|", "/", "／"]):
                literal_parts.append(p)
            else:
                chinese_defs.append(p)
        else:
            # English only: if it contains standalone syllable separators, it's literal
            if any(sym in p.split() for sym in ["I", "|", "/", "／"]):
                literal_parts.append(p)
            else:
                english_syns.append(p)
                
    return literal_parts, chinese_defs, english_syns

def extract_all():
    line_tuples = []
    for p in range(42, len(reader.pages)):
        text = reader.pages[p].extract_text()
        if not text:
            continue
        text = clean_ocr(text)
        for line in text.split("\n"):
            line_str = line.strip()
            if line_str:
                line_tuples.append((line_str, p))
                
    print(f"Total raw lines: {len(line_tuples)}")
    
    words = []
    current_word = None
    current_chapter = "未分類字彙"
    
    skip_keywords = [
        "part", "tpo", "mp3", "page", "通用", "字首", "字根", 
        "其他", "本書", "學術", "如何有效率", "系列", "導讀", 
        "目錄", "精讀", "廣讀", "附錄"
    ]
    
    i = 0
    pending_definition = ""
    pending_derivatives = []
    
    while i < len(line_tuples):
        line, p = line_tuples[i]
        
        if p < 126:
            part_id = 1
            part_name = "Part 1 通用學術字彙：依字首分類"
        elif p < 450:
            part_id = 2
            part_name = "Part 2 通用學術字彙：依字根分類"
        elif p < 475:
            part_id = 3
            part_name = "Part 3 托福 TPO 字彙：依字首分類"
        elif p < 565:
            part_id = 4
            part_name = "Part 4 托福 TPO 字彙：依字根分類"
        else:
            part_id = 5
            part_name = "Part 5 托福 TPO 字彙：其他"
            
        ch_match = re.search(r"表示「([^」]+)」的(字首|字根)", line)
        if ch_match:
            current_chapter = f"表示「{ch_match.group(1)}」的{ch_match.group(2)}"
            i += 1
            continue
            
        word_res = get_word_entry(line)
        if word_res:
            if current_word:
                words.append(current_word)
                
            w = word_res[0].lower()
            rest = word_res[1]
            
            phonetic = ""
            definition = ""
            
            # Separate phonetic and definition
            if re.match(r"^[\[［\(L\/]", rest):
                bracket_match = re.match(r"^([\[［\(L\/].*?[\]］\)\/L])\s*(.*)$", rest)
                if bracket_match:
                    phonetic = bracket_match.group(1)
                    def_part = bracket_match.group(2).strip()
                    if def_part:
                        literal_parts, chinese_defs, english_syns = parse_line_parts(" " + def_part)
                        if chinese_defs:
                            definition = "；".join(chinese_defs)
                else:
                    phonetic = rest
            else:
                literal_parts, chinese_defs, english_syns = parse_line_parts(" " + rest)
                if chinese_defs:
                    definition = "；".join(chinese_defs)
            
            # Apply pending definition from column swap
            if pending_definition and not definition:
                definition = pending_definition
                pending_definition = ""
                
            chapter = "其他字彙" if part_id == 5 else current_chapter
            
            current_word = {
                "id": f"w_{len(words) + 1:04d}",
                "word": w,
                "phonetic": phonetic,
                "structure": "",
                "literal_meaning": "",
                "definition": definition,
                "synonyms": [],
                "derivatives": list(pending_derivatives),
                "examples": [],
                "part_id": part_id,
                "part_name": part_name,
                "chapter": chapter,
                "page": p
            }
            pending_derivatives = []
            
            i += 1
            sub_lines = []
            while i < len(line_tuples):
                next_line, next_p = line_tuples[i]
                if get_word_entry(next_line):
                    break
                if re.search(r"表示「([^」]+)」的(字首|字根)", next_line):
                    break
                if next_line.isdigit() and len(next_line) <= 3:
                    i += 1
                    continue
                if any(kw in next_line.lower() for kw in skip_keywords) and len(next_line) < 35:
                    i += 1
                    continue
                sub_lines.append(next_line)
                i += 1
                
            block_idx = 0
            
            # 1. Parse Syllable Structure
            if block_idx < len(sub_lines):
                sl = sub_lines[block_idx]
                if len(re.findall(r"[\|I/l1]\s*", sl)) >= 1 and re.match(r"^[a-zA-Z\-I\|/\s\(\)l1]+$", sl):
                    current_word["structure"] = sl
                    block_idx += 1
                    
            # 2. Parse rest
            k = block_idx
            has_examples = False
            while k < len(sub_lines):
                sl = sub_lines[k]
                
                if sl.startswith("•"):
                    has_examples = True
                    en_ex = sl[1:].strip()
                    k += 1
                    zh_ex = ""
                    while k < len(sub_lines):
                        next_sl = sub_lines[k]
                        if next_sl.startswith("•"):
                            k -= 1
                            break
                        if re.search(r"[\u4e00-\u9fff]", next_sl):
                            zh_ex = next_sl
                            break
                        else:
                            en_ex += " " + next_sl
                        k += 1
                    current_word["examples"].append({
                        "en": en_ex.strip(),
                        "zh": zh_ex.strip()
                    })
                elif re.match(r"^(?:困|國|国|回|E|圖|團|团|因|因)\s*([a-zA-Z\-]{3,})", sl):
                    deriv_match = re.findall(r"([a-zA-Z\-]{3,})\s+(?:[回國国團团圖畫画E]\s*)?([\u4e00-\u9fff\s；，、\(\)]+)", sl)
                    for d_word, d_meaning in deriv_match:
                        # Prefix match derivatives checking current and previous word
                        if d_word.lower().startswith(current_word["word"][:3]):
                            current_word["derivatives"].append({
                                "word": d_word.lower(),
                                "meaning": d_meaning.strip()
                            })
                        elif words and d_word.lower().startswith(words[-1]["word"][:3]):
                            words[-1]["derivatives"].append({
                                "word": d_word.lower(),
                                "meaning": d_meaning.strip()
                            })
                            # Fallback empty definition populating
                            if not words[-1]["definition"] and d_meaning:
                                words[-1]["definition"] = d_meaning.strip()
                        else:
                            pending_derivatives.append({
                                "word": d_word.lower(),
                                "meaning": d_meaning.strip()
                            })
                else:
                    if any(kw in sl.lower() for kw in skip_keywords) and len(sl) < 35:
                        k += 1
                        continue
                        
                    literal_parts, chinese_defs, english_syns = parse_line_parts(" " + sl)
                    
                    if chinese_defs and has_examples:
                        # Fallback to current word if its definition is empty
                        if not current_word["definition"]:
                            current_word["definition"] = "；".join(chinese_defs)
                        else:
                            pending_definition = "；".join(chinese_defs)
                    else:
                        if literal_parts:
                            current_word["literal_meaning"] = " / ".join(literal_parts)
                        if chinese_defs:
                            if current_word["definition"]:
                                current_word["definition"] += "；" + "；".join(chinese_defs)
                            else:
                                current_word["definition"] = "；".join(chinese_defs)
                        if english_syns:
                            current_word["synonyms"].extend(english_syns)
                k += 1
                
            if current_word["definition"]:
                current_word["definition"] = re.sub(r"^[回國国團团圖畫画El1固\s；，、\-\+:\.圈困園園园因『l\[\]\(\)）白]+", "", current_word["definition"])
                # Strip previous word's definition if duplicated
                if words and words[-1]["definition"]:
                    prev_def = words[-1]["definition"]
                    if current_word["definition"].startswith(prev_def + "；"):
                        current_word["definition"] = current_word["definition"][len(prev_def) + 1:].strip()
                
            continue
        i += 1
        
    if current_word:
        words.append(current_word)
        
    return words

print("Starting final PDF vocabulary extraction...")
words_db = extract_all()
print(f"Extraction complete! Total words parsed: {len(words_db)}")

# Structure output into Parts and Chapters
parts_dict = {}
for w in words_db:
    pid = w["part_id"]
    pname = w["part_name"]
    ch = w["chapter"]
    
    if pid not in parts_dict:
        parts_dict[pid] = {
            "part_id": pid,
            "part_name": pname,
            "chapters": {}
        }
        
    if ch not in parts_dict[pid]["chapters"]:
        parts_dict[pid]["chapters"][ch] = {
            "chapter_name": ch,
            "words": []
        }
        
    parts_dict[pid]["chapters"][ch]["words"].append({
        "id": w["id"],
        "word": w["word"],
        "phonetic": w["phonetic"],
        "structure": w["structure"],
        "literal_meaning": w["literal_meaning"],
        "definition": w["definition"],
        "synonyms": w["synonyms"],
        "derivatives": w["derivatives"],
        "examples": w["examples"],
        "page": w["page"]
    })

structured_db = []
for pid in sorted(parts_dict.keys()):
    p_data = parts_dict[pid]
    ch_list = []
    for ch_name in sorted(p_data["chapters"].keys()):
        ch_list.append({
            "chapter_name": ch_name,
            "words": p_data["chapters"][ch_name]["words"]
        })
    structured_db.append({
        "part_id": p_data["part_id"],
        "part_name": p_data["part_name"],
        "chapters": ch_list
    })

with open(output_json_path, "w", encoding="utf-8") as f:
    json.dump(structured_db, f, indent=2, ensure_ascii=False)
    
print(f"JSON database written to {output_json_path}")
dist_json_path = r"d:\code\Vocabulary\dist\vocabulary.json"
if os.path.exists(r"d:\code\Vocabulary\dist"):
    with open(dist_json_path, "w", encoding="utf-8") as f:
        json.dump(structured_db, f, indent=2, ensure_ascii=False)
    print(f"Copied to dist JSON path: {dist_json_path}")
