
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="월별 기온분석",
    page_icon="🌡️",
    layout="wide"
)

# 제목
st.title("🌡️ 월별 기온분석")
st.write("원하는 월을 선택하여 연도별 최고기온과 최저기온을 비교해 보세요!")

# CSV 파일 경로 확인
current_folder = Path(__file__).resolve().parent

file_candidates = [
    current_folder / "temperature.csv",
    current_folder.parent / "temperature.csv"
]

csv_path = next(
    (path for path in file_candidates if path.exists()),
    None
)

# 데이터 불러오기
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path, encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="euc-kr")

    # 불필요한 열 제거
    df = df.loc[
        :,
        ~df.columns.astype(str).str.contains("^Unnamed")
    ]

    # 필요한 열
    required_columns = [
        "일시",
        "최고기온(℃)",
        "최저기온(℃)"
    ]

    # 필요한 열 확인
    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"CSV 파일에 필요한 열이 없습니다: {missing_columns}"
        )

    # 기온 데이터 숫자 변환
    for col in ["최고기온(℃)", "최저기온(℃)"]:
        df[col] = pd.to_numeric(
            df[col], errors="coerce"
        )

    # 날짜 처리
    # 데이터의 2자리 연도를 순서에 맞게 4자리 연도로 변환
    month_dict = {
        "Jan": 1, "Feb": 2, "Mar": 3,
        "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9,
        "Oct": 10, "Nov": 11, "Dec": 12
    }

    years = []
    months = []

    century = 1900
    previous_year = None

    for value in df["일시"]:
        parts = str(value).strip().split("-")

        if len(parts) != 2:
            years.append(None)
            months.append(None)
            continue

        month_text = parts[0].title()
        year_text = parts[1]

        if month_text not in month_dict or not year_text.isdigit():
            years.append(None)
            months.append(None)
            continue

        short_year = int(year_text)

        # 99년에서 00년으로 넘어갈 때 세기 변경
        if (
            previous_year is not None
            and short_year < previous_year
        ):
            century += 100

        full_year = century + short_year

        years.append(full_year)
        months.append(month_dict[month_text])

        previous_year = short_year

    df["연도"] = years
    df["월"] = months

    # 필요한 데이터가 없는 행 제거
    df = df.dropna(
        subset=[
            "연도",
            "월",
            "최고기온(℃)",
            "최저기온(℃)"
        ]
    )

    df["연도"] = df["연도"].astype(int)
    df["월"] = df["월"].astype(int)

    return df


# 파일 존재 확인
if csv_path is None:
    st.error(
        "temperature.csv 파일을 찾을 수 없습니다. "
        "CSV 파일의 위치를 확인해 주세요."
    )
    st.stop()

# 데이터 읽기
try:
    df = load_data(str(csv_path))
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()


# 월 선택
month_names = [
    "1월", "2월", "3월", "4월",
    "5월", "6월", "7월", "8월",
    "9월", "10월", "11월", "12월"
]

selected_month_name = st.selectbox(
    "📅 분석할 월을 선택하세요.",
    month_names
)

selected_month = month_names.index(
    selected_month_name
) + 1


# 선택한 월의 데이터 추출
month_df = df[
    df["월"] == selected_month
].copy()

month_df = month_df.sort_values("연도")


# 그래프
if not month_df.empty:

    fig = go.Figure()

    # 최고기온 - 형광 노란색
    fig.add_trace(
        go.Scatter(
            x=month_df["연도"],
            y=month_df["최고기온(℃)"],
            mode="lines+markers",
            name="최고기온",
            line=dict(
                color="#EFFF00",
                width=3
            ),
            marker=dict(
                color="#EFFF00",
                size=7
            )
        )
    )

    # 최저기온 - 형광 초록색
    fig.add_trace(
        go.Scatter(
            x=month_df["연도"],
            y=month_df["최저기온(℃)"],
            mode="lines+markers",
            name="최저기온",
            line=dict(
                color="#39FF14",
                width=3
            ),
            marker=dict(
                color="#39FF14",
                size=7
            )
        )
    )

    # 그래프 디자인
    fig.update_layout(
        title={
            "text": "월별 기온분석",
            "x": 0.5,
            "xanchor": "center"
        },
        xaxis_title="연도",
        yaxis_title="온도(℃)",
        legend=dict(
            title="범례",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode="x unified",
        template="plotly_white",
        height=600
    )

    fig.update_xaxes(
        showgrid=True,
        dtick=5
    )

    fig.update_yaxes(
        showgrid=True
    )

    # 그래프 출력
    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # 데이터 표
    with st.expander("📋 선택한 월의 기온 데이터 확인"):
        display_df = month_df[
            [
                "연도",
                "최고기온(℃)",
                "최저기온(℃)"
            ]
        ].copy()

        display_df.columns = [
            "연도",
            "최고기온(℃)",
            "최저기온(℃)"
        ]

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )

else:
    st.warning("선택한 월에 표시할 기온 데이터가 없습니다.")
