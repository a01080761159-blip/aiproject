import streamlit as st
import pandas as pd
import re
from collections import Counter

# ---------------------------------------------------------
# 1. 페이지 설정 및 아기자기한 커스텀 CSS 스타일
# ---------------------------------------------------------
st.set_page_config(
    page_title="달콤 찰떡궁합 재료 찾기 🧁",
    page_icon="🍓",
    layout="centered"
)

st.markdown("""
<style>
    /* 전체 배경 */
    .stApp {
        background-color: #FFF9FB;
    }
    /* 타이틀 박스 */
    .title-box {
        background: linear-gradient(135deg, #FFE5EC 0%, #FFF0F3 100%);
        padding: 24px;
        border-radius: 20px;
        text-align: center;
        border: 2px dashed #FFB3C6;
        margin-bottom: 24px;
    }
    .title-box h1 {
        color: #D6336C;
        font-size: 27px;
        margin-bottom: 8px;
    }
    .title-box p {
        color: #6D4C5D;
        font-size: 14.5px;
        margin: 0;
    }
    /* 순위 카드 스타일 */
    .rank-card {
        background-color: #FFFFFF;
        border-radius: 18px;
        padding: 18px 20px;
        margin-top: 12px;
        margin-bottom: 8px;
        border: 2px solid #FFE3EC;
        box-shadow: 0 4px 12px rgba(255, 179, 198, 0.15);
    }
    .rank-badge {
        display: inline-block;
        background-color: #FF8FA3;
        color: white;
        font-weight: bold;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 13px;
        margin-bottom: 8px;
    }
    .rank-1 { background-color: #FF4D6D; }
    .rank-2 { background-color: #FF8FA3; }
    .rank-3 { background-color: #FFB3C6; color: #590D22; }
    
    .ing-title {
        font-size: 21px;
        font-weight: 800;
        color: #3D2C2E;
        margin: 4px 0 8px 0;
    }
    .reason-text {
        background-color: #FFF5F7;
        padding: 10px 14px;
        border-radius: 12px;
        color: #5C3A42;
        font-size: 14px;
        margin-bottom: 10px;
    }
    .recipe-tag {
        display: inline-block;
        background-color: #F3F0FF;
        color: #5F3DC4;
        padding: 5px 11px;
        border-radius: 10px;
        font-size: 13px;
        font-weight: 600;
        margin: 3px 5px 3px 0;
        border: 1px solid #E5DBFF;
    }
    /* 만드는 과정 박스 */
    .process-box {
        background-color: #FFFDF7;
        border: 1.5px solid #FFE082;
        border-radius: 15px;
        padding: 16px 18px;
        margin-top: 6px;
        margin-bottom: 14px;
        color: #4A3B32;
        font-size: 14px;
        line-height: 1.65;
    }
    .process-title {
        font-weight: 800;
        color: #D97706;
        font-size: 15.5px;
        margin-bottom: 8px;
    }
    /* 버튼 스타일 귀엽게 커스텀 */
    div.stButton > button {
        background-color: #FFF0F5;
        color: #C2255C;
        border: 1.5px solid #FFCCD5;
        border-radius: 12px;
        font-size: 13px;
        font-weight: 600;
        padding: 6px 12px;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        background-color: #FFE3EC;
        border-color: #FF8FA3;
        color: #A61E4D;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 재료별 한글 이름 & 센스 있는 이모지 매핑 사전
# ---------------------------------------------------------
INGREDIENT_INFO = {
    "vanilla": ("바닐라", "🌼", "달콤하고 부드러운 향으로 모든 재료의 풍미를 포근하게 감싸줘요."),
    "chocolate": ("초콜릿", "🍫", "진하고 쌉싸름한 달콤함이 더해져 실패 없는 환상의 밸런스를 만들어요."),
    "lemon": ("레몬", "🍋", "상큼한 산미가 자칫 무거울 수 있는 맛을 산뜻하고 깔끔하게 잡아줘요."),
    "cinnamon": ("시나몬", "🪵", "따뜻하고 스파이시한 향이 어우러져 깊고 고급스러운 여운을 남겨요."),
    "orange": ("오렌지", "🍊", "화사하고 달콤한 시트러스 향이 입안 가득 기분 좋은 산뜻함을 더해줘요."),
    "almond": ("아몬드", "🥜", "고소하고 바삭한 견과류의 풍미가 더해져 한층 풍부한 식감과 맛을 내요."),
    "cocoa": ("코코아", "🤎", "깊고 진한 카카오의 쌉싸름함이 단맛과 어우러져 세련된 맛을 완성해요."),
    "ginger": ("생강(진저)", "🫚", "알싸하고 향긋한 풍미가 느끼함을 잡아주고 독특한 매력을 불어넣어요."),
    "raspberry": ("라즈베리", "🍓", "새콤달콤한 베리 향이 톡 쏘는 생기와 예쁜 색감을 동시에 선물해요."),
    "apple": ("사과", "🍎", "아삭하고 은은한 단맛이 부드럽게 스며들어 편안하고 조화로운 맛을 내요."),
    "strawberry": ("딸기", "🍓", "사랑스러운 달콤함과 상큼함이 어우러져 누구든 반할 클래식한 조합이에요."),
    "honey": ("꿀", "🍯", "자연스럽고 깊은 단맛과 윤기를 더해 풍미를 한 단계 끌어올려 줘요."),
    "nutmeg": ("넛맥", "🌰", "은은하고 따뜻한 향신료의 뉘앙스가 디저트의 완성도를 높여줘요."),
    "walnut": ("호두", "🧠", "묵직한 고소함과 오독오독한 식감이 더해져 씹는 즐거움이 살아나요."),
    "pecan": ("피칸", "🥧", "버터처럼 진하고 고소한 견과류 향이 달콤한 재료와 찰떡처럼 어우러져요."),
    "coconut": ("코코넛", "🥥", "이국적이고 크리미한 달콤함이 더해져 부드럽고 매력적인 풍미를 만들어요."),
    "clove": ("정향(클로브)", "🌺", "독특하고 알싸한 향이 소량만으로도 깊고 입체적인 풍미를 완성해 줘요."),
    "rum": ("럼", "🥃", "은은한 오크향과 달큰한 풍미가 어우러져 어른스럽고 깊은 맛을 내요."),
    "lime": ("라임", "🍈", "톡 쏘는 청량한 산미가 더해져 입맛을 확 돋워주는 상큼한 조합이에요."),
    "cherry": ("체리", "🍒", "진하고 매혹적인 과즙의 달콤새콤함이 깊은 풍미와 완벽하게 어울려요."),
    "brandy": ("브랜디", "🍷", "과일의 깊은 향을 끌어올려 주며 고급스럽고 우아한 여운을 남겨줘요."),
    "apricot": ("살구", "🍑", "은은한 새콤달콤함과 부드러운 과일 향이 우아한 조화를 이뤄요."),
    "mint": ("민트", "🌿", "상쾌하고 시원한 허브 향이 입안을 깔끔하게 정돈해 주는 매력적인 짝꿍이에요."),
    "pear": ("배", "🍐", "은은하고 시원한 달콤함이 다른 재료의 향을 해치지 않고 부드럽게 받쳐줘요."),
    "coffee": ("커피", "☕", "그윽하고 쌉싸름한 로스팅 향이 단맛의 깊이를 배로 만들어 줘요."),
    "raisin": ("건포도", "🍇", "쫀득한 식감과 농축된 달콤함이 더해져 클래식하고 풍성한 맛을 내요."),
    "hazelnut": ("헤이즐넛", "🌰", "고소하고 향긋한 견과류 풍미가 더해져 깊고 진한 여운을 선사해요."),
    "blueberry": ("블루베리", "🫐", "상큼하게 터지는 과즙과 은은한 단맛이 부드러운 조화를 이뤄요."),
    "peach": ("복숭아", "🍑", "향긋하고 부드러운 과즙의 달콤함이 기분 좋은 화사함을 더해줘요."),
    "banana": ("바나나", "🍌", "크리미하고 진한 달콤함이 더해져 촉촉하고 든든한 풍미를 완성해요."),
    "cardamom": ("카다멈", "🌱", "청량하면서도 이국적인 스파이스 향이 세련되고 감각적인 맛을 내요."),
    "cranberry": ("크랜베리", "🍒", "기분 좋은 새콤함과 쫀득함이 더해져 달콤한 맛의 균형을 딱 맞춰줘요."),
    "allspice": ("올스파이스", "🍂", "여러 향신료가 어우러진 듯 따뜻하고 복합적인 향이 깊은 맛을 내요."),
    "blackberry": ("블랙베리", "🫐", "깊고 진한 베리의 풍미가 더해져 우아하고 성숙한 맛의 조화를 이뤄요."),
    "oat": ("오트(귀리)", "🌾", "구수한 곡물의 풍미와 쫄깃·바삭한 식감이 더해져 고소함이 배가 돼요."),
    "maple": ("메이플", "🍁", "우디하고 진한 단맛이 어우러져 포근하고 깊은 풍미를 완성해 줘요."),
    "pumpkin": ("단호박", "🎃", "포슬포슬하고 은은한 단맛이 향신료나 견과류와 찰떡처럼 어울려요."),
    "pineapple": ("파인애플", "🍍", "트로피컬한 상큼달콤함이 더해져 활기차고 경쾌한 맛을 만들어 줘요."),
    "peanut": ("땅콩", "🥜", "고소하고 짭조름한 매력이 단맛과 만나 중독성 강한 단짠 조화를 이뤄요."),
    "graham": ("그레이엄 크래커", "🍪", "고소하고 바삭한 비스킷 풍미가 부드러운 재료를 든든하게 받쳐줘요."),
    "pistachio": ("피스타치오", "💚", "고급스러운 고소함과 화사한 초록빛 색감이 완벽한 포인트를 줘요."),
    "mascarpone": ("마스카포네", "🧀", "부드럽고 진한 크림 치즈의 풍미가 재료들을 우아하게 하나로 묶어줘요."),
    "mango": ("망고", "🥭", "진하고 달콤한 열대과일의 풍미가 입안 가득 부드럽게 퍼져요."),
    "plum": ("자두", "🍑", "새콤달콤한 과즙과 껍질의 쌉싸름함이 어우러져 입체적인 맛을 내요."),
    "rhubarb": ("루바브", "🥬", "기분 좋은 상큼한 신맛이 달콤한 과일이나 크림과 환상의 짝꿍을 이뤄요."),
    "fig": ("무화과", "🪻", "은은한 꿀맛과 톡톡 씹히는 씨앗의 식감이 고급스러운 풍미를 더해줘요."),
    "date": ("대추야자", "🌴", "카라멜처럼 진하고 쫀득한 단맛이 깊은 풍미를 한층 끌어올려 줘요."),
    "caramel": ("카라멜", "🍮", "달콤하고 쌉싸름한 구운 설탕의 풍미가 진한 감동을 더해줘요."),
    "matcha": ("말차", "🍵", "쌉싸름하고 짙은 녹차의 풍미가 단맛을 세련되게 눌러주는 최고의 조합이에요."),
    "earl": ("얼그레이", "🫖", "향긋한 베르가못 홍차 향이 더해져 우아하고 향기로운 티타임을 완성해요."),
    "rose": ("장미", "🌹", "은은하고 로맨틱한 플로럴 향이 더해져 특별하고 우아한 디저트가 돼요."),
    "lavender": ("라벤더", "💜", "향긋한 허브의 여운이 달콤한 맛에 세련되고 편안한 포인트를 줘요."),
    "rosemary": ("로즈마리", "🌿", "싱그러운 허브 향이 단맛에 반전 매력을 더해 고급스러운 풍미를 내요."),
    "thyme": ("타임", "🌱", "은은하고 깔끔한 허브 향이 과일이나 크림의 풍미를 한층 살려줘요."),
    "basil": ("바질", "🍃", "상큼하고 향긋한 허브 풍미가 더해져 색다르고 감각적인 맛을 완성해요."),
    "ricotta": ("리코타", "🥛", "담백하고 몽글몽글한 우유의 고소함이 재료 본연의 맛을 살려줘요."),
    "chestnut": ("밤", "🌰", "포근하고 달콤한 고소함이 더해져 깊고 부드러운 계절감을 선사해요."),
}

# ---------------------------------------------------------
# 3. 영문 레시피명 -> 한글 메뉴명 변환 및 만드는 과정 생성기
# ---------------------------------------------------------
DISH_TERMS = {
    "cupcakes": "컵케이크", "cupcake": "컵케이크",
    "cheesecake": "치즈케이크", "pound cake": "파운드 케이크",
    "bundt cake": "번트 케이크", "sponge cake": "스펀지 케이크",
    "layer cake": "레이어 케이크", "shortcake": "쇼트케이크",
    "coffee cake": "커피 케이크", "cake": "케이크",
    "tartlets": "타르틀렛", "tartlet": "타르틀렛", "tart": "타르트",
    "pie": "파이", "galette": "갈레트", "crumble": "크럼블", "crisp": "크리스프",
    "cobbler": "코블러", "cookies": "쿠키", "cookie": "쿠키",
    "biscotti": "비스코티", "macarons": "마카롱", "macaroons": "마카룬",
    "brownies": "브라우니", "brownie": "브라우니", "blondies": "블론디",
    "bars": "바", "squares": "스퀘어", "muffins": "머핀", "muffin": "머핀",
    "scones": "스콘", "scone": "스콘", "bread": "브레드", "loaf": "로프",
    "rolls": "롤", "roll": "롤케이크", "buns": "번", "donuts": "도넛", "doughnuts": "도넛",
    "pudding": "푸딩", "mousse": "무스", "panna cotta": "판나코타",
    "custard": "커스터드", "creme brulee": "크렘 브륄레", "parfait": "파르페",
    "trifle": "트라이플", "tiramisu": "티라미수", "souffle": "수플레",
    "pavlova": "파블로바", "meringue": "머랭 디저트", "eclairs": "에클레어",
    "profiteroles": "프로피트롤", "crepes": "크레이프", "pancakes": "팬케이크",
    "waffles": "와플", "french toast": "프렌치토스트",
    "ice cream": "아이스크림", "sorbet": "셔벗", "gelato": "젤라또",
    "granita": "그라니타", "popsicles": "아이스바", "smoothie": "스무디",
    "sauce": "소스", "glaze": "글레이즈", "syrup": "시럽", "jam": "잼",
    "compote": "콩포트", "curd": "커드", "ganache": "가나슈", "frosting": "프로스팅",
    "fudge": "퍼지", "truffles": "트뤼플 초콜릿", "bark": "바크 초콜릿",
    "salad": "샐러드", "roast": "로스트", "glazed": "글레이즈드", "stuffed": "스터프드"
}

MODIFIER_TERMS = {
    "roasted": "구운", "toasted": "토스트", "baked": "베이크드",
    "grilled": "그릴드", "poached": "포치드", "caramelized": "카라멜라이즈드",
    "whipped": "휘핑", "creamy": "크리미", "spiced": "스파이스",
    "sweet": "달콤한", "dark": "다크", "white": "화이트",
    "fresh": "프레시", "warm": "따뜻한", "iced": "아이스",
    "glazed": "글레이즈드", "stuffed": "필링 가득", "mini": "미니",
    "classic": "클래식", "easy": "간편", "rich": "진한", "crispy": "바삭한"
}

EXTRA_WORD_MAP = {
    "cream": "크림", "butter": "버터", "cheese": "치즈", "yogurt": "요거트",
    "milk": "밀크", "sugar": "슈가", "brown": "브라운", "oatmeal": "오트밀",
    "oats": "귀리", "nut": "견과류", "nuts": "견과류", "berry": "베리",
    "berries": "베리", "fruit": "과일", "citrus": "시트러스", "spice": "스파이스",
    "tea": "티", "matcha": "말차", "earl grey": "얼그레이", "espresso": "에스프레소",
    "liqueur": "리큐르", "bourbon": "버번", "wine": "와인", "champagne": "샴페인",
    "salt": "솔트", "salted": "솔티드", "sea salt": "씨솔트"
}

def translate_menu_to_korean(eng_title, base_key, partner_key):
    """영문 레시피명을 자연스러운 한글 메뉴명으로 변환"""
    text = eng_title.lower()
    
    # 1) 요리 카테고리(디저트 종류) 찾기
    detected_dish = "디저트"
    detected_dish_eng = ""
    for eng_k in sorted(DISH_TERMS.keys(), key=len, reverse=True):
        if eng_k in text:
            detected_dish = DISH_TERMS[eng_k]
            detected_dish_eng = eng_k
            break
            
    # 2) 수식어 찾기
    modifiers = []
    for mod_eng, mod_kr in MODIFIER_TERMS.items():
        if re.search(rf"\b{mod_eng}\b", text):
            modifiers.append(mod_kr)
            if len(modifiers) == 1:
                break

    # 3) 본문에 등장하는 재료들 한글로 수집
    found_ings = []
    # 우선 선택한 두 재료가 제목에 있으면 순서대로 반영
    for key in [base_key, partner_key]:
        if key in text and key in INGREDIENT_INFO:
            kr_name = INGREDIENT_INFO[key][0].split("(")[0]
            if kr_name not in found_ings:
                found_ings.append(kr_name)
                
    # 제목에 있는 다른 재료 키워드 추가
    for key, (kr, _, _) in INGREDIENT_INFO.items():
        if re.search(rf"\b{key}\b", text):
            clean_kr = kr.split("(")[0]
            if clean_kr not in found_ings:
                found_ings.append(clean_kr)
                
    for ext_eng, ext_kr in EXTRA_WORD_MAP.items():
        if re.search(rf"\b{ext_eng}\b", text) and ext_kr not in found_ings:
            found_ings.append(ext_kr)
            if len(found_ings) >= 3:
                break

    # 만약 제목에서 재료가 1개 이하로 잡히면 선택된 두 재료를 기본으로 넣어줌
    if len(found_ings) < 2:
        b_kr = INGREDIENT_INFO.get(base_key, (base_key,))[0].split("(")[0]
        p_kr = INGREDIENT_INFO.get(partner_key, (partner_key,))[0].split("(")[0]
        for k in [b_kr, p_kr]:
            if k not in found_ings:
                found_ings.append(k)

    ing_phrase = " ".join(found_ings[:3])
    mod_phrase = f"{modifiers[0]} " if modifiers else ""
    
    # '소스/글레이즈/크림' 등이 뒷부분에 붙는 경우 자연스럽게 연결
    korean_name = f"{mod_phrase}{ing_phrase} {detected_dish}".strip()
    return korean_name, detected_dish

def get_cooking_steps(kr_menu_name, dish_type, base_key, partner_key):
    """메뉴의 디저트 유형과 재료 특성을 반영한 단계별 만드는 과정 생성"""
    b_name = INGREDIENT_INFO.get(base_key, (base_key,))[0].split("(")[0]
    p_name = INGREDIENT_INFO.get(partner_key, (partner_key,))[0].split("(")[0]

    # 카테고리별 맞춤 베이킹/조리 공정 템플릿
    if any(k in dish_type for k in ["타르트", "파이", "갈레트", "타르틀렛"]):
        return [
            f"**1. 타르트지(파트 사브레) 준비:** 차가운 버터와 박력분, 설탕을 소보로 상태로 만든 뒤 노른자를 넣고 한 덩어리로 뭉쳐 냉장 휴지합니다.",
            f"**2. 구움 및 식히기:** 휴지된 반죽을 3mm 두께로 밀어 틀에 안착시키고 포크로 피케(구멍)를 낸 뒤, 175°C 오븐에서 노릇하게 블라인드 베이킹합니다.",
            f"**3. {b_name} & {p_name} 필링 만들기:** {b_name}의 풍미를 살린 베이스 크림(아몬드 크림 또는 커스터드/가나슈)을 채우고 {p_name}을(를) 조화롭게 얹거나 섞어줍니다.",
            f"**4. 마무리 장식:** 오븐에서 한 번 더 구워내거나 차갑게 식힌 뒤, {p_name} 토핑과 슈가파우더·허브 등으로 먹음직스럽게 데코레이션합니다."
        ]
    elif any(k in dish_type for k in ["케이크", "컵케이크", "머핀", "스콘", "브레드", "로프", "번"]):
        return [
            f"**1. 재료 계량 및 전처리:** 실온에 둔 버터와 달걀을 준비하고, {b_name}와(과) {p_name}은(는) 반죽에 고루 섞이도록 다지거나 퓨레·제스트 형태로 준비합니다.",
            f"**2. 크림화 및 반죽하기:** 부드럽게 푼 버터에 설탕과 달걀을 나누어 넣으며 휘핑한 뒤, 체 친 가루류와 {b_name} 재료를 넣어 주걱으로 가볍게 섞어줍니다.",
            f"**3. 팬닝 및 오븐 굽기:** 유산지를 깐 틀에 반죽을 70~80% 채우고 중간에 {p_name}을(를) 콕콕 박아 170~180°C 오븐에서 속까지 촉촉하게 구워냅니다.",
            f"**4. 식힘 및 글레이즈:** 구워진 반죽을 식힘망에서 충분히 식힌 뒤, {p_name} 향을 더한 크림이나 글레이즈를 얹어 촉촉함과 달콤함을 극대화합니다."
        ]
    elif any(k in dish_type for k in ["무스", "푸딩", "판나코타", "커스터드", "파르페", "티라미수", "크렘 브륄레", "파블로바"]):
        return [
            f"**1. 베이스 인퓨징:** 우유나 생크림에 {b_name}을(를) 넣고 약불에서 은은하게 데워 재료 본연의 깊고 향긋한 풍미를 충분히 우려냅니다.",
            f"**2. 크림 무스 제조:** 노른자(또는 머랭)와 설탕을 휘핑한 뒤 우린 베이스와 불린 젤라틴을 섞고, 부드럽게 휘핑한 생크림을 2~3번에 나누어 폴딩합니다.",
            f"**3. {p_name} 레이어링:** 컵이나 틀에 무스를 반쯤 채운 뒤, 새콤달콤하거나 고소한 {p_name} 콩포트·크림을 가운데 샌드하고 나머지 무스로 덮어줍니다.",
            f"**4. 냉장 굳히기 & 플레이팅:** 냉장고에서 3시간 이상 단단하게 굳힌 뒤, {p_name} 가니쉬를 올려 우아하고 산뜻하게 완성합니다."
        ]
    elif any(k in dish_type for k in ["쿠키", "비스코티", "마카롱", "브라우니", "블론디", "바", "스퀘어"]):
        return [
            f"**1. 버터 베이스 만들기:** 실온 버터(또는 녹인 버터·초콜릿)에 설탕과 달걀을 넣고 뽀얗고 매끄러워질 때까지 휘핑합니다.",
            f"**2. 가루류 및 메인 재료 혼합:** 박력분과 베이킹파우더를 체 쳐 넣고 날가루가 보이지 않을 때쯤 {b_name}와(과) {p_name}을(를) 듬뿍 넣어 섞어줍니다.",
            f"**3. 성형 및 휴지:** 반죽을 일정한 크기로 분할하거나 사각 팬에 평평하게 팬닝한 뒤, 식감을 살리기 위해 냉장고에서 30분간 휴지시킵니다.",
            f"**4. 굽기 및 식히기:** 175°C 오븐에서 가장자리가 노릇해질 때까지 12~18분간 구운 뒤, 식힘망에서 완전히 식혀 바삭·쫀득한 식감을 살립니다."
        ]
    elif any(k in dish_type for k in ["아이스크림", "셔벗", "젤라또", "그라니타", "스무디", "아이스바"]):
        return [
            f"**1. 시럽 및 과즙/베이스 준비:** 물과 설탕을 끓여 식힌 시럽에 손질한 {b_name}을(를) 넣고 블렌더로 곱게 갈아 부드러운 퓨레 베이스를 만듭니다.",
            f"**2. 풍미 밸런스 맞추기:** 준비된 베이스에 {p_name} 과즙이나 퓨레를 더해 상큼함과 달콤함의 황금 비율을 맞춥니다.",
            f"**3. 냉동 및 공기층 형성:** 밀폐 용기에 담아 냉동실에서 얼리되, 1~2시간 간격으로 포크나 휘퍼로 3~4회 긁어주며 부드러운 식감을 만듭니다.",
            f"**4. 스쿠핑 및 서빙:** 차갑게 칠링한 볼에 동그랗게 스쿱으로 떠 담고, 신선한 {p_name} 토핑이나 민트 잎을 얹어 시원하게 즐깁니다."
        ]
    elif any(k in dish_type for k in ["소스", "글레이즈", "시럽", "잼", "콩포트", "커드", "가나슈"]):
        return [
            f"**1. 재료 손질:** {b_name}와(과) {p_name}의 향과 과즙이 잘 우러나도록 잘게 썰거나 즙을 내어 냄비에 준비합니다.",
            f"**2. 약불 졸이기:** 설탕(또는 꿀·생크림)을 함께 넣고 중약불에서 바닥이 눌어붙지 않도록 주걱으로 저어가며 원하는 농도가 나올 때까지 졸입니다.",
            f"**3. 농도 조절 및 체 거르기:** 더욱 매끄러운 식감을 원한다면 고운 체에 한 번 내려 건더기를 걸러내고 윤기를 더해줍니다.",
            f"**4. 소독 병 보관 및 활용:** 열탕 소독한 유리병에 담아 식힌 뒤, 스콘·팬케이크·케이크 필링이나 아이스크림 토핑으로 곁들여 드세요."
        ]
    else:
        return [
            f"**1. 주재료 밑준비:** {b_name}의 향이 가장 잘 살아나도록 깨끗이 손질하고, 짝꿍 재료인 {p_name}도 적당한 크기로 준비합니다.",
            f"**2. 베이스 반죽/크림 조합:** 기본 반죽이나 크림 베이스에 {b_name}을(를) 먼저 넣어 전체적인 맛의 중심을 잡아줍니다.",
            f"**3. 포인트 풍미 더하기:** 조리 중간이나 마무리 단계에서 {p_name}을(를) 더해 두 재료의 향이 입체적으로 어우러지도록 익히거나 섞어줍니다.",
            f"**4. 플레이팅 마무리:** 접시에 먹음직스럽게 담아낸 뒤, {p_name} 가니쉬를 살짝 얹어 시각적인 매력까지 완성합니다."
        ]

def get_display_name(key):
    if key in INGREDIENT_INFO:
        kr, emoji, _ = INGREDIENT_INFO[key]
        return f"{emoji} {kr} ({key})"
    return f"🍽️ {key.capitalize()}"

def get_short_name(key):
    if key in INGREDIENT_INFO:
        kr, emoji, _ = INGREDIENT_INFO[key]
        return f"{emoji} {kr}"
    return f"🍽️ {key.capitalize()}"

def get_reason(base_key, pair_key):
    base_name = get_short_name(base_key)
    pair_name = get_short_name(pair_key)
    if pair_key in INGREDIENT_INFO:
        desc = INGREDIENT_INFO[pair_key][2]
        return f"{base_name}에 {pair_name}을(를) 더하면, {desc}"
    return f"{base_name}의 풍미를 {pair_name}이(가) 조화롭게 받쳐주어 훌륭한 밸런스를 만들어줘요."

# ---------------------------------------------------------
# 4. 데이터 로드 및 궁합 분석 함수 (기본 pandas만 활용)
# ---------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("recipes.csv")
    df = df.dropna(subset=["flavors"]).copy()
    
    typo_map = {
        "expresso": "coffee",
        "tomatoe": "tomato",
        "whisky": "whiskey",
        "oatmeal": "oat",
        "Cookies": "cookie"
    }
    
    cleaned_lists = []
    all_counter = Counter()
    for text in df["flavors"]:
        words = [typo_map.get(w.strip(), w.strip().lower()) for w in str(text).split()]
        unique_words = list(dict.fromkeys(words))
        cleaned_lists.append(unique_words)
        all_counter.update(unique_words)
        
    df["flavor_list"] = cleaned_lists
    valid_ingredients = sorted([k for k, v in all_counter.items() if v >= 10])
    return df, valid_ingredients

def recommend_pairings(df, selected_ing, exclude_common=False):
    matched_df = df[df["flavor_list"].apply(lambda x: selected_ing in x)].copy()
    
    pair_scores = Counter()
    pair_counts = Counter()
    common_base = {"vanilla", "lemon"} if exclude_common else set()
    
    for _, row in matched_df.iterrows():
        weight = 1.0 + (row["rating"] / 4.0)
        for item in row["flavor_list"]:
            if item != selected_ing and item not in common_base:
                pair_scores[item] += weight
                pair_counts[item] += 1
                
    top3 = pair_scores.most_common(3)
    results = []
    
    for partner, score in top3:
        both_df = matched_df[matched_df["flavor_list"].apply(lambda x: partner in x)]
        both_df = both_df.sort_values(by=["rating", "success"], ascending=False)
        raw_recipes = both_df["recipe_name"].drop_duplicates().head(3).tolist()
        
        translated_recipes = []
        seen_kr = set()
        for r_eng in raw_recipes:
            kr_name, dish_type = translate_menu_to_korean(r_eng, selected_ing, partner)
            # 중복 한글명 방지
            if kr_name in seen_kr:
                kr_name = f"{kr_name} 스페셜"
            seen_kr.add(kr_name)
            translated_recipes.append({
                "kr_name": kr_name,
                "eng_name": r_eng,
                "dish_type": dish_type
            })
        
        results.append({
            "partner": partner,
            "count": pair_counts[partner],
            "recipes": translated_recipes
        })
    return results, len(matched_df)

# ---------------------------------------------------------
# 5. 메인 화면 UI 구성
# ---------------------------------------------------------
st.markdown("""
<div class="title-box">
    <h1>🧁 찰떡궁합 재료 매칭 연구소 🍓</h1>
    <p>재료를 하나 골라주시면, 수천 개의 레시피 데이터를 분석해<br>가장 잘 어울리는 단짝 재료 TOP 3와 한글 메뉴, 만드는 과정까지 알려드려요!</p>
</div>
""", unsafe_allow_html=True)

# 버튼 토글 상태를 기억하기 위한 session_state 초기화
if "open_recipe_key" not in st.session_state:
    st.session_state.open_recipe_key = None

try:
    df, valid_ingredients = load_data()

    with st.sidebar:
        st.header("🎀 추천 옵션 설정")
        exclude_common = st.checkbox(
            "🌼 기본 베이스 재료 제외하기",
            value=False,
            help="체크하면 어디에나 잘 어울리는 '바닐라'와 '레몬'을 제외하고 더 개성 있는 단짝 재료를 추천해 드려요!"
        )
        st.divider()
        st.caption("📊 총 7,200여 개의 실제 레시피 데이터와 평점을 바탕으로 분석합니다.")

    default_idx = valid_ingredients.index("strawberry") if "strawberry" in valid_ingredients else 0

    selected_ing = st.selectbox(
        "✨ 오늘의 주인공 재료를 선택해 주세요!",
        options=valid_ingredients,
        index=default_idx,
        format_func=get_display_name
    )

    recommendations, total_recipes = recommend_pairings(df, selected_ing, exclude_common)

    st.markdown(
        f"##### 🔍 **{get_short_name(selected_ing)}**이(가) 들어간 레시피 **{total_recipes:,}개**를 분석한 결과예요!"
    )

    if not recommendations:
        st.warning("앗, 함께 조합된 레시피 데이터가 부족해요! 다른 재료를 선택해 볼까요? 🐰")
    else:
        rank_styles = [
            ("🥇 1위 · 최고의 환상 짝꿍", "rank-1"),
            ("🥈 2위 · 실패 없는 꿀조합", "rank-2"),
            ("🥉 3위 · 매력 만점 추천 조합", "rank-3")
        ]

        for idx, item in enumerate(recommendations):
            partner = item["partner"]
            count = item["count"]
            recipes = item["recipes"]
            badge_text, badge_class = rank_styles[idx]
            reason = get_reason(selected_ing, partner)

            # 한글 메뉴 태그 HTML 생성
            recipe_tags_html = "".join([
                f'<span class="recipe-tag">🍽️ {r["kr_name"]}</span>' for r in recipes
            ])

            st.markdown(f"""
            <div class="rank-card">
                <span class="rank-badge {badge_class}">{badge_text}</span>
                <div class="ing-title">{get_display_name(partner)} <span style="font-size:13px; color:#888; font-weight:normal;">(함께 쓰인 레시피 {count}건)</span></div>
                <div class="reason-text">💡 <b>추천 이유:</b> {reason}</div>
                <div style="font-size:13.5px; color:#6D4C5D; font-weight:bold; margin-bottom:6px;">👩‍🍳 이 조합으로 만들 수 있는 추천 메뉴 (아래 버튼을 눌러 레시피 과정을 확인하세요!):</div>
                <div>{recipe_tags_html}</div>
            </div>
            """, unsafe_allow_html=True)

            # 각 추천 메뉴별 "만드는 과정 보기" 버튼 배치
            btn_cols = st.columns(len(recipes))
            for r_idx, r_info in enumerate(recipes):
                unique_btn_id = f"{selected_ing}_{partner}_{r_idx}"
                is_opened = (st.session_state.open_recipe_key == unique_btn_id)
                btn_label = f"🔽 {r_info['kr_name']} 닫기" if is_opened else f"📖 {r_info['kr_name']} 만드는 법"
                
                with btn_cols[r_idx]:
                    if st.button(btn_label, key=f"btn_{unique_btn_id}", use_container_width=True):
                        if is_opened:
                            st.session_state.open_recipe_key = None
                        else:
                            st.session_state.open_recipe_key = unique_btn_id
                        st.rerun()

            # 현재 순위 카드에 속한 메뉴 버튼이 눌려있다면 만드는 과정 박스 표시
            for r_idx, r_info in enumerate(recipes):
                unique_btn_id = f"{selected_ing}_{partner}_{r_idx}"
                if st.session_state.open_recipe_key == unique_btn_id:
                    steps = get_cooking_steps(
                        r_info["kr_name"], r_info["dish_type"], selected_ing, partner
                    )
                    steps_html = "<br>".join([f"• {s}" for s in steps])
                    st.markdown(f"""
                    <div class="process-box">
                        <div class="process-title">🧁 [{r_info['kr_name']}] 만드는 과정 <span style="font-size:12px; color:#888; font-weight:normal;">(원제: {r_info['eng_name']})</span></div>
                        <div>{steps_html}</div>
                    </div>
                    """, unsafe_allow_html=True)

except FileNotFoundError:
    st.error("🚨 `recipes.csv` 파일을 찾을 수 없어요! `app.py`와 같은 폴더에 `recipes.csv` 파일을 함께 업로드해 주세요.")
