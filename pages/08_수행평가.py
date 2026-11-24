import streamlit as st
import pandas as pd
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
    /* 전체 배경 및 폰트 느낌 */
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
        font-size: 28px;
        margin-bottom: 8px;
    }
    .title-box p {
        color: #6D4C5D;
        font-size: 15px;
        margin: 0;
    }
    /* 순위 카드 스타일 */
    .rank-card {
        background-color: #FFFFFF;
        border-radius: 18px;
        padding: 18px 20px;
        margin-bottom: 16px;
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
        padding: 4px 10px;
        border-radius: 10px;
        font-size: 12.5px;
        margin: 3px 4px 3px 0;
        border: 1px solid #E5DBFF;
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
# 3. 데이터 로드 및 궁합 분석 함수 (기본 pandas만 활용)
# ---------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("recipes.csv")
    df = df.dropna(subset=["flavors"]).copy()
    
    # 오타/중복 단어 살짝 정제
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
        unique_words = list(dict.fromkeys(words))  # 한 레시피 내 중복 재료 제거
        cleaned_lists.append(unique_words)
        all_counter.update(unique_words)
        
    df["flavor_list"] = cleaned_lists
    # 최소 10번 이상 등장한 주요 재료만 선택 목록에 제공 (너무 희귀한 노이즈 제외)
    valid_ingredients = sorted([k for k, v in all_counter.items() if v >= 10])
    return df, valid_ingredients

def recommend_pairings(df, selected_ing, exclude_common=False):
    # 선택한 재료가 포함된 레시피 필터링
    matched_df = df[df["flavor_list"].apply(lambda x: selected_ing in x)].copy()
    
    pair_scores = Counter()
    pair_counts = Counter()
    
    common_base = {"vanilla", "lemon"} if exclude_common else set()
    
    for _, row in matched_df.iterrows():
        # 평점이 높을수록 가중치 부여 (기본 1.0 + 평점/4.0)
        weight = 1.0 + (row["rating"] / 4.0)
        for item in row["flavor_list"]:
            if item != selected_ing and item not in common_base:
                pair_scores[item] += weight
                pair_counts[item] += 1
                
    top3 = pair_scores.most_common(3)
    results = []
    
    for partner, score in top3:
        # 두 재료가 함께 들어간 레시피 중 평점 높은 순으로 최대 4개 추출
        both_df = matched_df[matched_df["flavor_list"].apply(lambda x: partner in x)]
        both_df = both_df.sort_values(by=["rating", "success"], ascending=False)
        sample_recipes = both_df["recipe_name"].drop_duplicates().head(4).tolist()
        
        results.append({
            "partner": partner,
            "count": pair_counts[partner],
            "recipes": sample_recipes
        })
    return results, len(matched_df)

# ---------------------------------------------------------
# 4. 메인 화면 UI 구성
# ---------------------------------------------------------
st.markdown("""
<div class="title-box">
    <h1>🧁 찰떡궁합 재료 매칭 연구소 🍓</h1>
    <p>재료를 하나 골라주시면, 수천 개의 레시피 데이터를 분석해<br>가장 잘 어울리는 단짝 재료 TOP 3와 추천 메뉴를 알려드려요!</p>
</div>
""", unsafe_allow_html=True)

try:
    df, valid_ingredients = load_data()

    # 사이드바 옵션
    with st.sidebar:
        st.header("🎀 추천 옵션 설정")
        exclude_common = st.checkbox(
            "🌼 기본 베이스 재료 제외하기",
            value=False,
            help="체크하면 어디에나 잘 어울리는 '바닐라'와 '레몬'을 제외하고 더 개성 있는 단짝 재료를 추천해 드려요!"
        )
        st.divider()
        st.caption("📊 총 7,200여 개의 실제 레시피 데이터와 평점을 바탕으로 분석합니다.")

    # 기본 선택값 설정 (딸기 또는 첫 번째 재료)
    default_idx = valid_ingredients.index("strawberry") if "strawberry" in valid_ingredients else 0

    col1, col2 = st.columns([3, 1])
    with col1:
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
            recipe_tags_html = "".join([f'<span class="recipe-tag">🍽️ {r}</span>' for r in recipes])

            st.markdown(f"""
            <div class="rank-card">
                <span class="rank-badge {badge_class}">{badge_text}</span>
                <div class="ing-title">{get_display_name(partner)} <span style="font-size:13px; color:#888; font-weight:normal;">(함께 쓰인 레시피 {count}건)</span></div>
                <div class="reason-text">💡 <b>추천 이유:</b> {reason}</div>
                <div style="font-size:13px; color:#6D4C5D; font-weight:bold; margin-bottom:4px;">👩‍🍳 이 조합으로 만들 수 있는 메뉴:</div>
                <div>{recipe_tags_html}</div>
            </div>
            """, unsafe_allow_html=True)

except FileNotFoundError:
    st.error("🚨 `recipes.csv` 파일을 찾을 수 없어요! `app.py`와 같은 폴더에 `recipes.csv` 파일을 함께 업로드해 주세요.")
