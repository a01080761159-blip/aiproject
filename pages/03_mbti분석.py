
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
st.subheader("세계 국가별 MBTI 분석")

st.write(
    "국가를 선택하거나 MBTI를 선택해서 "
    "세계의 MBTI 분포를 알아보세요!"
)

# ==========================================
# 2. CSV 파일 경로
# ==========================================
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
    st.error("CSV 파일을 찾을 수 없습니다.")
    st.stop()

try:
    df = load_data()
except Exception as e:
    st.error(f"데이터 오류: {e}")
    st.stop()


# ==========================================
# 4. 데이터 정리
# ==========================================
if "Country" not in df.columns:
    st.error("Country 열이 없습니다.")
    st.stop()

mbti_types = [
    col for col in df.columns
    if col != "Country"
]

for col in mbti_types:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

df["Country"] = (
    df["Country"].astype(str).str.strip()
)

df = df.dropna(subset=["Country"])
df = df[df["Country"] != ""]

# ==========================================
# 5. 분석 방식 선택
# ==========================================
st.divider()

mode = st.radio(
    "🔍 어떤 방식으로 분석할까요?",
    [
        "국가별 MBTI 분석",
        "MBTI별 국가 분석"
    ],
    horizontal=True
)

# ==========================================
# 6. 그라데이션 색상 함수
# ==========================================
def make_gradient(count):

    dark_color = (36, 74, 128)
    light_color = (220, 235, 250)

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
            "#{:02x}{:02x}{:02x}".format(*rgb)
        )

    return colors


# ==========================================
# 7. 국가별 MBTI 분석
# ==========================================
if mode == "국가별 MBTI 분석":

    st.markdown("### 🗺️ 국가 선택")

    countries = sorted(
        df["Country"].unique().tolist()
    )

    selected_country = st.selectbox(
        "국가를 선택하세요",
        countries
    )

    country_data = df[
        df["Country"] == selected_country
    ].iloc[0]

    chart_data = pd.DataFrame({
        "MBTI": mbti_types,
        "비율": [
            country_data[m]
            for m in mbti_types
        ]
    })

    chart_data = chart_data.dropna(
        subset=["비율"]
    )

    if chart_data.empty:
        st.warning("데이터가 없습니다.")
        st.stop()

    if chart_data["비율"].max() <= 1:
        chart_data["비율"] *= 100

    chart_data = chart_data.sort_values(
        "비율",
        ascending=False
    ).reset_index(drop=True)

    top = chart_data.iloc[0]

    col1, col2 = st.columns(2)

    col1.metric(
        "🌟 가장 높은 MBTI",
        top["MBTI"]
    )

    col2.metric(
        "📊 최고 비율",
        f'{top["비율"]:.2f}%'
    )

    colors = make_gradient(len(chart_data))

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
        height=650,
        xaxis_title="비율 (%)",
        yaxis_title="MBTI 유형",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=60, t=30, b=20)
    )

    st.markdown(
        f"### 📈 {selected_country}의 MBTI 순위"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ==========================================
# 8. MBTI별 국가 분석
# ==========================================
else:

    st.markdown("### 🧩 MBTI 유형 선택")

    selected_mbti = st.selectbox(
        "MBTI를 선택하세요",
        mbti_types
    )

    # 국가별 해당 MBTI 비율 추출
    country_chart = df[
        ["Country", selected_mbti]
    ].copy()

    country_chart = country_chart.dropna(
        subset=[selected_mbti]
    )

    country_chart = country_chart.rename(
        columns={
            selected_mbti: "비율"
        }
    )

    # 소수 비율을 백분율로 변환
    if country_chart["비율"].max() <= 1:
        country_chart["비율"] *= 100

    # 높은 비율 순으로 정렬
    country_chart = country_chart.sort_values(
        "비율",
        ascending=False
    ).reset_index(drop=True)

    # 상위 국가 수 선택
    display_count = st.selectbox(
        "📊 표시할 국가 수",
        ["TOP 10", "TOP 20", "전체 국가"]
    )

    if display_count == "TOP 10":
        display_data = country_chart.head(10)

    elif display_count == "TOP 20":
        display_data = country_chart.head(20)

    else:
        display_data = country_chart.copy()

    # 1위 국가 정보
    top_country = country_chart.iloc[0]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "🏆 1위 국가",
        top_country["Country"]
    )

    col2.metric(
        "📊 1위 비율",
        f'{top_country["비율"]:.2f}%'
    )

    col3.metric(
        "🌍 전체 국가",
        f"{len(country_chart)}개"
    )

    st.divider()

    # 그라데이션 색상
    colors = make_gradient(
        len(display_data)
    )

    # 국가별 색상 지정
    color_map = {
        row["Country"]: colors[i]
        for i, row in display_data.iterrows()
    }

    # 국가별 막대그래프
    fig = px.bar(
        display_data,
        x="비율",
        y="Country",
        orientation="h",
        text="비율",
        color="Country",
        color_discrete_map=color_map,
        category_orders={
            "Country": display_data["Country"].tolist()[::-1]
        }
    )

    fig.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside",
        cliponaxis=False
    )

    fig.update_layout(
        title=f"🌍 {selected_mbti} 비율이 높은 국가 순위",
        showlegend=False,
        height=max(450, len(display_data) * 32),
        xaxis_title="비율 (%)",
        yaxis_title="국가",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=70, t=60, b=30)
    )

    fig.update_xaxes(
        showgrid=True,
        rangemode="tozero"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ======================================
    # 9. 국가별 순위표
    # ======================================
    st.markdown(
        f"### 🏆 {selected_mbti} 국가별 순위표"
    )

    rank_data = country_chart.copy()

    rank_data.insert(
        0,
        "순위",
        range(1, len(rank_data) + 1)
    )

    rank_data = rank_data.rename(
        columns={
            "Country": "국가",
            "비율": "MBTI 비율"
        }
    )

    rank_data["MBTI 비율"] = (
        rank_data["MBTI 비율"]
        .map(lambda x: f"{x:.2f}%")
    )

    st.dataframe(
        rank_data,
        hide_index=True,
        use_container_width=True
    )


# ==========================================
# 10. 안내 문구
# ==========================================
st.divider()

st.caption(
    "※ 제공된 CSV 데이터 기준입니다. "
    "조사 표본과 출처에 따라 실제 국가 전체의 "
    "MBTI 분포와 다를 수 있습니다."
)

st.success("🌍 WORLD MBTI 분석 완료!")
