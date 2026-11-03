
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ==========================================
# 1. 페이지 설정
# ==========================================
st.set_page_config(
    page_title="WORLD MBTI",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 WORLD MBTI")
st.subheader("국가별 MBTI 유형 비율 알아보기")

st.write(
    "국가를 선택하면 해당 국가의 "
    "MBTI 16가지 유형별 비율을 확인할 수 있어요!"
)

# ==========================================
# 2. CSV 파일 경로 설정
# ==========================================

# pages 폴더의 상위 폴더에서 CSV 찾기
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "countriesMBTI_16types.csv"


# ==========================================
# 3. CSV 파일 불러오기
# ==========================================
@st.cache_data
def load_data():
    try:
        return pd.read_csv(
            DATA_FILE,
            encoding="utf-8-sig"
        )
    except UnicodeDecodeError:
        return pd.read_csv(
            DATA_FILE,
            encoding="cp949"
        )


if not DATA_FILE.exists():
    st.error(
        "CSV 파일을 찾을 수 없습니다. "
        "프로젝트 상위 폴더에 "
        "countriesMBTI_16types.csv 파일이 있는지 확인해주세요."
    )
    st.stop()

try:
    df = load_data()

except Exception as e:
    st.error(f"데이터를 불러오지 못했습니다: {e}")
    st.stop()


# ==========================================
# 4. 데이터 정리
# ==========================================
if "Country" not in df.columns:
    st.error("CSV 파일에 Country 열이 없습니다.")
    st.stop()

mbti_types = [
    col for col in df.columns
    if col != "Country"
]

if len(mbti_types) != 16:
    st.warning(
        f"MBTI 유형 열이 16개가 아닙니다. "
        f"현재 {len(mbti_types)}개입니다."
    )

# 숫자 데이터 변환
for col in mbti_types:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

# 국가 이름 정리
df["Country"] = (
    df["Country"]
    .astype(str)
    .str.strip()
)

df = df.dropna(subset=["Country"])
df = df[df["Country"] != ""]

if df.empty:
    st.error("표시할 국가 데이터가 없습니다.")
    st.stop()


# ==========================================
# 5. 국가 선택
# ==========================================
countries = sorted(
    df["Country"].unique().tolist()
)

selected_country = st.selectbox(
    "🗺️ 국가를 선택하세요",
    countries
)

country_data = df[
    df["Country"] == selected_country
].iloc[0]


# ==========================================
# 6. MBTI 데이터 만들기
# ==========================================
chart_data = pd.DataFrame({
    "MBTI": mbti_types,
    "비율": [
        country_data[mbti]
        for mbti in mbti_types
    ]
})

chart_data = chart_data.dropna(
    subset=["비율"]
)

if chart_data.empty:
    st.warning("선택한 국가의 데이터가 없습니다.")
    st.stop()

# 소수 형태라면 백분율로 변환
if chart_data["비율"].max() <= 1:
    chart_data["비율"] = (
        chart_data["비율"] * 100
    )

# 비율이 높은 순서대로 정렬
chart_data = chart_data.sort_values(
    "비율",
    ascending=False
).reset_index(drop=True)


# ==========================================
# 7. 가장 높은 MBTI 표시
# ==========================================
top_type = chart_data.iloc[0]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "🌟 가장 높은 MBTI",
        top_type["MBTI"]
    )

with col2:
    st.metric(
        "📊 최고 비율",
        f'{top_type["비율"]:.2f}%'
    )

with col3:
    st.metric(
        "🧩 MBTI 유형",
        f"{len(chart_data)}개"
    )

st.divider()


# ==========================================
# 8. 그라데이션 색상 만들기
# ==========================================
def hex_to_rgb(color):
    color = color.lstrip("#")

    return tuple(
        int(color[i:i+2], 16)
        for i in (0, 2, 4)
    )


def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(
        *rgb
    )


# 1위: 가장 진한 파란색
dark_color = hex_to_rgb("#244A80")

# 최하위: 가장 연한 파란색
light_color = hex_to_rgb("#DCEBFA")

count = len(chart_data)
colors = []

for i in range(count):

    ratio = i / max(count - 1, 1)

    rgb = tuple(
        round(
            dark_color[j]
            + (
                light_color[j]
                - dark_color[j]
            ) * ratio
        )
        for j in range(3)
    )

    colors.append(
        rgb_to_hex(rgb)
    )


# ==========================================
# 9. 막대그래프 만들기
# ==========================================
st.markdown(
    f"### 📈 {selected_country}의 MBTI 비율"
)

color_map = {
    row["MBTI"]: colors[i]
    for i, row in chart_data.iterrows()
}

fig = px.bar(
    chart_data,
    x="비율",
    y="MBTI",
    orientation="h",
    text="비율",
    color="MBTI",
    color_discrete_map=color_map,
    category_orders={
        "MBTI": chart_data["MBTI"].tolist()[::-1]
    }
)

fig.update_traces(
    texttemplate="%{text:.2f}%",
    textposition="outside",
    cliponaxis=False
)

fig.update_layout(
    showlegend=False,
    xaxis_title="비율 (%)",
    yaxis_title="MBTI 유형",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(
        family="Arial",
        size=13
    ),
    height=650,
    margin=dict(
        l=20,
        r=60,
        t=30,
        b=20
    )
)

fig.update_xaxes(
    showgrid=True,
    gridcolor="rgba(128,128,128,0.18)",
    rangemode="tozero"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ==========================================
# 10. MBTI 순위표
# ==========================================
st.markdown("### 🏆 MBTI 비율 순위")

rank_data = chart_data[
    ["MBTI", "비율"]
].copy()

rank_data.insert(
    0,
    "순위",
    range(1, len(rank_data) + 1)
)

rank_data["비율"] = rank_data[
    "비율"
].map(
    lambda x: f"{x:.2f}%"
)

st.dataframe(
    rank_data,
    hide_index=True,
    use_container_width=True
)


# ==========================================
# 11. 안내 문구
# ==========================================
st.divider()

st.caption(
    "※ 제공된 CSV 데이터 기준입니다. "
    "실제 국가 전체 인구의 MBTI 분포와 "
    "다를 수 있습니다."
)

st.success(
    "🌍 WORLD MBTI 분석이 완료되었습니다!"
)
