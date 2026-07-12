import os
import re
import json

json_path = r"d:\code\Vocabulary\public\vocabulary.json"

if not os.path.exists(json_path):
    print(f"File not found: {json_path}")
    exit(1)

with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Comprehensive replacement rules for OCR typos
replacements = {
    # High-priority combination phrases
    "通用主要街": "通用學術",
    "主要街": "學術",
    "主要營": "學習",
    "主要霄": "學習",
    "主要營": "學習",
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
    
    # Prefix and root headings cleaning
    "i去示": "表示",
    "去示": "表示",
    
    # Safe character mappings in vocabulary context
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
    
    # Infinite and extreme modifiers
    "黑限": "無限",
    "黑知": "無知",
    "黑人": "無人",
    "黑法": "無法",
    "黑助": "無助",
    "黑聊": "無聊",
    "黑奈": "無奈",
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
    
    # Study and school contexts
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
    
    # Pronoun fixes
    "仰們": "你們",
}

# Single character substitutions that are highly safe in this vocabulary list context
single_chars = {
    "仰": "你",
    "需": "驚",
}

def clean_string(s):
    if not isinstance(s, str):
        return s
    
    # Apply phrase replacements
    for key, val in replacements.items():
        s = s.replace(key, val)
        
    # Apply single character replacements
    for key, val in single_chars.items():
        # Match only when it is surrounding Chinese words to avoid breaking English text
        s = re.sub(f"(?<=[\u4e00-\u9fff]){key}", val, s)
        s = re.sub(f"{key}(?=[\u4e00-\u9fff])", val, s)
        
    return s

def clean_data(obj):
    if isinstance(obj, dict):
        return {k: clean_data(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_data(item) for item in obj]
    elif isinstance(obj, str):
        return clean_string(obj)
    return obj

print("Cleaning vocabulary data...")
cleaned_data = clean_data(data)

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

print("Vocabulary database cleaning complete!")
