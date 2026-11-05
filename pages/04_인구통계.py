
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import re

# =========================================
# 1. 페이지 설정
# =========================================
st.set_page_config(
    page_title="연령별 인구 분석",
    page_icon="📊",
    layout="wide"
)

# =========================================
# 2. 화면 디자인
# =========================================
st.markdown("""
<style>
    .main-title {
        font-size: 35px;
        font-weight: bold;
        color: #7952B3;
        text-align: center;
        margin-bottom: 10px;
    }

    .sub-title {
        font-size: 16px;
        color: #888888;
        text-align: center;
        margin-bottom: 30px;
    }

    div[data-testid="stMetric"] {
        background-color: #F5F0FF;
        padding: 15px;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)


# =========================================
# 3. CSV 파일 불러오기
# =========================================
@st.cache_data
def load_data():

    base_dir = os.path.dirname(
        os.path.abspath(__file__)
    )

    csv_path = os.path.abspath(
        os.path.join(
            base_dir,
            "..",
            "population.csv"
        )
    )

    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            "population.csv 파일을 찾을 수 없습니다."
        )

    df = None

    # 한글 인코딩 처리
    for encoding in [
        "cp949",
        "euc-kr",
        "utf-8-sig",
        "utf-8"
    ]:
        try:
            df = pd.read_csv(
                csv_path,
                encoding=encoding
            )
            break

        except UnicodeDecodeError:
            continue

    if df is None:
        raise ValueError(
            "CSV 파일의 인코딩을 확인해주세요."
        )

    # 열 이름 정리
    df.columns = df.columns.str.strip()

    # 숫자 데이터 변환
    for col in df.columns:

        if col != "행정구역":

            df[col] = pd.to_numeric(
                df[col].astype(str)
                .str.replace(",", "", regex=False)
                .str.strip(),
                errors="coerce"
            )

    # 행정구역 이름 추출
    df["행정구역명"] = (
        df["행정구역"]
        .astype(str)
        .str.replace(
            r"^서울특별시\s*중랑구\s*",
            "",
            regex=True
        )
        .str.replace(
            r"\s*\(\d+\)\s*$",
            "",
            regex=True
        )
        .str.strip()
    )

    # 중랑구 전체 행 이름 지정
    df.loc[
        df["행정구역명"] == "",
        "행정구역명"
    ] = "중랑구 전체"

    return df


# =========================================
# 4. 데이터 불러오기
# =========================================
try:

    df = load_data()

except Exception as e:

    st.error(
        f"데이터를 불러오는 중 오류가 발생했습니다: {e}"
    )

    st.stop()


# =========================================
# 5. 연도 및 연령대 설정
# =========================================

# CSV에서 연도 자동 추출
years = sorted(set(
    int(re.match(r"(\d{4})년", col).group(1))
    for col in df.columns
    if re.match(
        r"\d{4}년_거주자_0~9세$",
        col
    )
))

if not years:

    st.error("연도별 인구 데이터를 찾을 수 없습니다.")
    st.stop()


# 연령대 목록
age_groups = [
    "0~9세",
    "10~19세",
    "20~29세",
    "30~39세",
    "40~49세",
    "50~59세",
    "60~69세",
    "70~79세",
    "80~89세",
    "90~99세",
    "100세 이상"
]


# =========================================
# 6. 제목
# =========================================
st.markdown(
    '<div class="main-title">📊 연령별 인구 분석</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    '행정구역, 성별, 연도를 선택하여 '
    '연령별 인구 분포와 동별 인구 순위를 확인해보세요!'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# =========================================
# 7. 분석 조건 선택
# =========================================
st.subheader("🔍 분석 조건 선택")

col1, col2, col3 = st.columns(3)


# 행정구역 선택
with col1:

    regions = sorted(
        df["행정구역명"].dropna().unique().tolist(),
        key=lambda x: (
            x != "중랑구 전체",
            x
        )
    )

    selected_region = st.selectbox(
        "📍 행정구역",
        regions
    )


# 성별 선택
with col2:

    selected_gender = st.selectbox(
        "👥 성별",
        ["전체", "남성", "여성"]
    )


# 연도 선택
with col3:

    selected_year = st.selectbox(
        "📅 연도",
        years,
        index=len(years) - 1
    )


# 성별에 따른 열 이름
if selected_gender == "전체":

    gender_prefix = ""

elif selected_gender == "남성":

    gender_prefix = "남_"

else:

    gender_prefix = "여_"


st.divider()


# =========================================
# 8. 선택한 행정구역 데이터
# =========================================
selected_data = df[
    df["행정구역명"] == selected_region
].iloc[0]


# =========================================
# 9. 연령별 인구 데이터 추출
# =========================================
chart_data = []

for age in age_groups:

    column_name = (
        f"{selected_year}년_"
        f"{gender_prefix}거주자_{age}"
    )

    if column_name not in df.columns:

        st.error(
            f"데이터 열을 찾을 수 없습니다: {column_name}"
        )

        st.stop()

    population = selected_data[column_name]

    if pd.isna(population):
        population = 0

    if age == "100세 이상":

        age_number = 100

    else:

        age_number = int(age.split("~")[0])

    chart_data.append({

        "연령대": age,
        "나이": age_number,
        "인구수": int(population)

    })


chart_df = pd.DataFrame(chart_data)


# =========================================
# 10. 주요 통계
# =========================================
st.header("📌 주요 인구 통계")

total_population = int(
    chart_df["인구수"].sum()
)

max_age = chart_df.loc[
    chart_df["인구수"].idxmax()
]

metric1, metric2, metric3 = st.columns(3)

metric1.metric(
    "전체 인구수",
    f"{total_population:,}명"
)

metric2.metric(
    "인구가 가장 많은 연령대",
    max_age["연령대"]
)

metric3.metric(
    "해당 연령대 인구수",
    f"{max_age['인구수']:,}명"
)


# =========================================
# 11. 연령별 인구 꺾은선 그래프
# =========================================
st.divider()

st.header("1️⃣ 연령별 인구 꺾은선 그래프")

st.caption(
    f"📍 {selected_region} | "
    f"👥 {selected_gender} | "
    f"📅 {selected_year}년"
)


# 성별에 따른 색상
if selected_gender == "남성":

    line_color = "#4285F4"
    fill_color = "rgba(66, 133, 244, 0.15)"

elif selected_gender == "여성":

    line_color = "#E56BA8"
    fill_color = "rgba(229, 107, 168, 0.15)"

else:

    line_color = "#9366D9"
    fill_color = "rgba(147, 102, 217, 0.15)"


fig = go.Figure()

fig.add_trace(
    go.Scatter(

        x=chart_df["나이"],
        y=chart_df["인구수"],

        mode="lines+markers",

        name="인구수",

        line=dict(
            color=line_color,
            width=4
        ),

        marker=dict(
            color=line_color,
            size=9,
            line=dict(
                color="white",
                width=2
            )
        ),

        fill="tozeroy",
        fillcolor=fill_color,

        customdata=chart_df["연령대"],

        hovertemplate=
        "<b>%{customdata}</b><br>"
        "인구수: %{y:,}명"
        "<extra></extra>"
    )
)


# 그래프 디자인
fig.update_layout(

    height=570,

    paper_bgcolor="white",
    plot_bgcolor="#FCFAFF",

    font=dict(
        family="Arial, sans-serif",
        size=13,
        color="#444444"
    ),

    margin=dict(
        l=65,
        r=35,
        t=35,
        b=80
    ),

    hovermode="x unified",

    showlegend=False,

    xaxis=dict(

        title="나이",

        tickmode="array",

        tickvals=[
            0, 10, 20, 30, 40, 50,
            60, 70, 80, 90, 100
        ],

        ticktext=[
            "0~9세",
            "10~19세",
            "20~29세",
            "30~39세",
            "40~49세",
            "50~59세",
            "60~69세",
            "70~79세",
            "80~89세",
            "90~99세",
            "100세 이상"
        ],

        range=[-3, 103],

        showgrid=True,
        gridcolor="#E8E0F2",

        zeroline=False
    ),

    yaxis=dict(

        title="인구수 (명)",

        rangemode="tozero",

        tickformat=",",

        nticks=10,

        showgrid=True,
        gridcolor="#D9D0E5",

        zeroline=False,

        minor=dict(
            dtick=100,
            showgrid=True,
            gridcolor="#EEEAF3",
            gridwidth=0.5
        )
    )
)


st.plotly_chart(
    fig,
    use_container_width=True
)


# =========================================
# 12. 연령별 인구 상세 표
# =========================================
with st.expander("📋 연령별 상세 인구 데이터 보기"):

    display_df = chart_df[
        ["연령대", "인구수"]
    ].copy()

    display_df["인구수"] = display_df[
        "인구수"
    ].apply(lambda x: f"{x:,}명")

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# =========================================
# 13. 동별 연령 인구 순위 분석
# =========================================
st.divider()

st.header("2️⃣ 연령대별 동 인구 순위")

st.write(
    "원하는 연령대를 선택하면 해당 연령의 인구가 "
    "가장 많은 행정구역을 순위별로 보여줘!"
)

# 연령대 선택
selected_age = st.selectbox(
    "🎂 비교할 연령대를 선택하세요.",
    age_groups,
    index=2,
    key="ranking_age"
)


# -----------------------------------------
# 선택한 연령대에 해당하는 열 찾기
# -----------------------------------------
ranking_column = (
    f"{selected_year}년_"
    f"{gender_prefix}거주자_{selected_age}"
)


# -----------------------------------------
# 중랑구 전체 제외
# -----------------------------------------
district_df = df[
    df["행정구역명"] != "중랑구 전체"
].copy()


# -----------------------------------------
# 선택한 연령대 인구 데이터 가져오기
# -----------------------------------------
district_df["선택 연령 인구"] = pd.to_numeric(
    district_df[ranking_column],
    errors="coerce"
).fillna(0)


# -----------------------------------------
# 인구가 많은 순서대로 정렬
# -----------------------------------------
district_df = district_df.sort_values(
    by="선택 연령 인구",
    ascending=False
).reset_index(drop=True)


# 순위 추가
district_df["순위"] = range(
    1,
    len(district_df) + 1
)


# =========================================
# 14. 순위 통계
# =========================================
if not district_df.empty:

    first_district = district_df.iloc[0]

    last_district = district_df.iloc[-1]

    rank_col1, rank_col2, rank_col3 = st.columns(3)

    rank_col1.metric(
        "🥇 인구 1위 행정구역",
        first_district["행정구역명"]
    )

    rank_col2.metric(
        "👥 1위 인구수",
        f"{int(first_district['선택 연령 인구']):,}명"
    )

    rank_col3.metric(
        "📍 비교 행정구역 수",
        f"{len(district_df)}개"
    )


# =========================================
# 15. 가로 막대그래프
# =========================================
st.subheader(
    f"🏆 {selected_age} 인구가 많은 행정구역 TOP {len(district_df)}"
)

st.caption(
    f"📅 {selected_year}년 | "
    f"👥 {selected_gender} | "
    f"🎂 {selected_age}"
)


rank_fig = go.Figure()


# 1위부터 순서대로 그래프 표시
rank_fig.add_trace(

    go.Bar(

        x=district_df["선택 연령 인구"],

        y=district_df["행정구역명"],

        orientation="h",

        marker=dict(

            color=district_df["선택 연령 인구"],

            colorscale=[
                [0, "#E9DDFB"],
                [0.5, "#B99BE8"],
                [1, "#7042B5"]
            ],

            showscale=False,

            line=dict(
                color="white",
                width=1
            )
        ),

        text=district_df[
            "선택 연령 인구"
        ].apply(lambda x: f"{int(x):,}명"),

        textposition="outside",

        cliponaxis=False,

        hovertemplate=
        "<b>%{y}</b><br>"
        "인구수: %{x:,}명"
        "<extra></extra>"
    )
)


rank_fig.update_layout(

    height=650,

    paper_bgcolor="white",
    plot_bgcolor="#FCFAFF",

    font=dict(
        family="Arial, sans-serif",
        size=13,
        color="#444444"
    ),

    margin=dict(
        l=110,
        r=90,
        t=30,
        b=65
    ),

    showlegend=False,

    xaxis=dict(

        title="인구수 (명)",

        tickformat=",",

        showgrid=True,

        gridcolor="#E8E0F2",

        rangemode="tozero"
    ),

    yaxis=dict(

        title="행정구역",

        autorange="reversed",

        showgrid=False
    )
)


st.plotly_chart(
    rank_fig,
    use_container_width=True
)


# =========================================
# 16. 동별 인구 순위표
# =========================================
with st.expander("📋 동별 상세 순위표 보기"):

    ranking_table = district_df[
        ["순위", "행정구역명", "선택 연령 인구"]
    ].copy()

    ranking_table.columns = [
        "순위",
        "행정구역",
        "인구수"
    ]

    ranking_table["인구수"] = ranking_table[
        "인구수"
    ].apply(lambda x: f"{int(x):,}명")

    st.dataframe(
        ranking_table,
        use_container_width=True,
        hide_index=True
    )


# =========================================
# 17. 분석 결과 안내
# =========================================
st.divider()

st.subheader("💡 분석 결과")

if not district_df.empty:

    st.success(
        f"""
        {selected_year}년 기준으로
        **{selected_age} {selected_gender} 인구**가
        가장 많은 지역은
        **{first_district['행정구역명']}**이야!

        해당 지역의 인구는
        **{int(first_district['선택 연령 인구']):,}명**이야.
        """
    )


st.markdown(
    """
    <div style="
        text-align:center;
        color:#9366D9;
        font-size:18px;
        font-weight:bold;
        padding:20px;
    ">
        💜 숫자로 알아보는 우리 동네 인구 이야기 💜
    </div>
    """,
    unsafe_allow_html=True
)

st.caption(
    "데이터 출처: population.csv"
)
