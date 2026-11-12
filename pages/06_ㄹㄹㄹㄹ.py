import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="월별 평균 기온 예측 (선형회귀)",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 평균 기온 추이 및 선형회귀 예측")
st.markdown("과거 기온 데이터를 바탕으로 **선형회귀(Linear Regression)** 알고리즘을 학습하여 미래 특정 연도의 기온을 예측합니다.")

# 2. 데이터 로드 및 전처리 함수 (캐싱 적용)
@st.cache_data
def load_data(file_path):
    # 한국어 CSV(CP949) 및 UTF-8 인코딩 자동 대응
    try:
        df = pd.read_csv(file_path, encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="utf-8")

    # 컬럼명 공백 제거
    df.columns = df.columns.str.strip()

    # '일시' 컬럼 파싱 (예: 'Oct-07' -> 1907년 10월, 'Oct-26' -> 2026년 10월)
    month_map = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }

    split_date = df["일시"].str.split("-")
    df["월_영문"] = split_date.str[0]
    yy = split_date.str[1].astype(int)

    # 26 이하이면 2000년대(2000~2026), 27 이상이면 1900년대(1907~1999)로 변환
    df["연도"] = np.where(yy <= 26, 2000 + yy, 1900 + yy)
    df["월"] = df["월_영문"].map(month_map)

    # 평균기온 결측치 제거 및 연도순 정렬
    df = df.dropna(subset=["평균기온(℃)", "연도", "월"]).sort_values(["연도", "월"]).reset_index(drop=True)
    return df

# 데이터 불러오기
try:
    df = load_data("temperature.csv")
except FileNotFoundError:
    st.error("⚠️ `temperature.csv` 파일을 찾을 수 없습니다. `app.py`와 같은 폴더에 파일을 위치시켜 주세요.")
    st.stop()

# 3. 사용자 입력 (사이드바)
st.sidebar.header("🔍 예측 조건 설정")
selected_month = st.sidebar.selectbox(
    "예측할 월을 선택하세요",
    options=list(range(1, 13)),
    format_func=lambda x: f"{x}월",
    index=7  # 기본값: 8월
)

max_data_year = int(df["연도"].max())
target_year = st.sidebar.number_input(
    "예측할 연도를 입력하세요",
    min_value=max_data_year + 1,
    max_value=2200,
    value=2035,
    step=1
)

# 4. 선택된 월 데이터 필터링 및 선형회귀 학습
month_df = df[df["월"] == selected_month].copy()

X = month_df[["연도"]].values  # 독립 변수 (연도)
y = month_df["평균기온(℃)"].values  # 종속 변수 (평균기온)

model = LinearRegression()
model.fit(X, y)

slope = model.coef_[0]          # 기울기 (w)
intercept = model.intercept_    # y절편 (b)
r2_score = model.score(X, y)    # 결정계수 (R^2)

# 과거 데이터에 대한 추세선 값 및 미래 예측 기온 계산
month_df["추세선_기온"] = model.predict(X)
predicted_temp = model.predict(np.array([[target_year]]))[0]

# 예측 연장선 생성 (데이터 시작 연도 ~ 사용자 입력 연도)
line_years = np.arange(int(month_df["연도"].min()), target_year + 1).reshape(-1, 1)
line_temps = model.predict(line_years)

# 5. 상단 핵심 지표 요약
col1, col2, col3 = st.columns(3)
col1.metric(
    label=f"{target_year}년 {selected_month}월 예측 평균기온",
    value=f"{predicted_temp:.2f} ℃",
    delta=f"최근({int(month_df['연도'].max())}년) 대비 {predicted_temp - month_df['평균기온(℃)'].iloc[-1]:+.2f} ℃"
)
col2.metric(
    label="연간 평균 기온 변화율 (기울기)",
    value=f"{slope:+.4f} ℃ / 년",
    delta=f"100년당 {slope * 100:+.2f} ℃ 변화"
)
col3.metric(
    label=f"역대 {selected_month}월 전체 평균기온",
    value=f"{y.mean():.2f} ℃",
    delta=f"관측 데이터 수: {len(month_df)}개"
)

# 6. 선형회귀 작동 원리가 드러나는 시각화 (Plotly)
fig = go.Figure()

# (1) 오차(잔차, Residual) 수직선 표시: 실제 데이터와 회귀선 사이의 거리
residual_x = []
residual_y = []
for yr, actual, pred in zip(month_df["연도"], month_df["평균기온(℃)"], month_df["추세선_기온"]):
    residual_x.extend([yr, yr, None])
    residual_y.extend([actual, pred, None])

fig.add_trace(go.Scatter(
    x=residual_x,
    y=residual_y,
    mode="lines",
    line=dict(color="rgba(150, 150, 150, 0.35)", width=1, dash="dot"),
    name="오차(잔차): 실제값과 추세선의 차이",
    hoverinfo="skip"
))

# (2) 실제 관측된 월별 평균 기온 산점도 + 연도별 연결선
fig.add_trace(go.Scatter(
    x=month_df["연도"],
    y=month_df["평균기온(℃)"],
    mode="lines+markers",
    name=f"실제 {selected_month}월 평균기온",
    line=dict(color="rgba(70, 130, 180, 0.4)", width=1.2),
    marker=dict(color="#1f77b4", size=6),
    hovertemplate="<b>%{x}년</b><br>실제 평균기온: %{y:.1f}℃<extra></extra>"
))

# (3) 학습된 선형회귀 직선 (과거 구간)
fig.add_trace(go.Scatter(
    x=month_df["연도"],
    y=month_df["추세선_기온"],
    mode="lines",
    name=f"선형회귀 추세선 (y = {slope:.4f}x + {intercept:.2f})",
    line=dict(color="#ff7f0e", width=3),
    hovertemplate="<b>%{x}년 (학습 구간)</b><br>회귀선 기온: %{y:.2f}℃<extra></extra>"
))

# (4) 미래 예측 연장선 (마지막 관측 연도 ~ 목표 예측 연도)
future_mask = line_years.flatten() >= int(month_df["연도"].max())
fig.add_trace(go.Scatter(
    x=line_years.flatten()[future_mask],
    y=line_temps[future_mask],
    mode="lines",
    name="미래 예측 연장선 (외삽)",
    line=dict(color="#d62728", width=3, dash="dash"),
    hovertemplate="<b>%{x}년 (예측 구간)</b><br>예측 기온: %{y:.2f}℃<extra></extra>"
))

# (5) 목표 예측 연도 포인트 강조
fig.add_trace(go.Scatter(
    x=[target_year],
    y=[predicted_temp],
    mode="markers+text",
    name=f"{target_year}년 예측 결과",
    marker=dict(color="#d62728", size=14, symbol="star"),
    text=[f"  <b>{target_year}년 예측: {predicted_temp:.2f}℃</b>"],
    textposition="top left",
    textfont=dict(color="#d62728", size=13),
    hovertemplate=f"<b>{target_year}년 {selected_month}월 예측</b><br>예측 평균기온: {predicted_temp:.2f}℃<extra></extra>"
))

# 그래프 레이아웃 및 수식 주석 추가
fig.update_layout(
    title=f"<b>{selected_month}월 평균기온 전체 추이 및 {target_year}년 선형회귀 예측</b>",
    xaxis_title="연도 (Year)",
    yaxis_title="평균기온 (℃)",
    hovermode="closest",
    height=550,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    annotations=[
        dict(
            x=0.02,
            y=0.95,
            xref="paper",
            yref="paper",
            text=(
                f"<b>[학습된 선형회귀 모델]</b><br>"
                f"수식: 기온(y) = {slope:.4f} × 연도(x) + ({intercept:.2f})<br>"
                f"결정계수(R²): {r2_score:.4f}"
            ),
            showarrow=False,
            align="left",
            bgcolor="rgba(255, 255, 255, 0.85)",
            bordercolor="#ff7f0e",
            borderwidth=1.5,
            font=dict(size=12, color="#222")
        )
    ]
)

st.plotly_chart(fig, use_container_width=True)

# 7. 그래프 하단: 선형회귀 알고리즘 원리 설명
st.divider()
st.subheader("📘 그래프 속 선형회귀(Linear Regression) 알고리즘 작동 원리")

st.markdown(f"""
**선형회귀(Linear Regression)**는 과거 데이터(연도 $x$와 기온 $y$) 사이의 관계를 가장 잘 설명하는 **하나의 직선($y = wx + b$)**을 찾아내어 미래 값을 예측하는 지도학습(Supervised Learning) 알고리즘입니다.

1. **오차(잔차) 최소화 — 최소제곱법 (Ordinary Least Squares):**
   * 위 그래프에서 파란색 점(실제 관측 기온)과 주황색 실선(회귀 추세선)을 잇는 **회색 점선**이 바로 **오차(잔차, Residual)**입니다.
   * 선형회귀 알고리즘은 모든 연도에 대해 이 **회색 점선 길이의 제곱합(MSE, 평균제곱오차)이 가장 작아지는 단 하나의 최적 직선**을 수학적으로 계산합니다.

2. **기울기($w$)와 절편($b$) 학습 결과:**
   * **기울기 ($w = {slope:+.4f}$):** 연도가 1년 지날 때마다 {selected_month}월 평균기온이 평균적으로 **{slope:+.4f}℃**씩 변한다는 뜻입니다. (10년 기준 약 **{slope*10:+.2f}℃** 변화)
   * **절편 ($b = {intercept:.2f}$):** 직선의 시작 기준점 역할을 하는 상수입니다.

3. **미래 기온 예측 (외삽, Extrapolation):**
   * 학습이 완료된 주황색 직선을 목표 연도인 **{target_year}년**까지 그대로 연장한 것이 **빨간색 점선**입니다.
   * 최종적으로 도출된 수식에 $x = {target_year}$을 대입하여 **{predicted_temp:.2f}℃**라는 예측값을 산출합니다.
   $$\\text{{예측 기온}} = ({slope:.4f} \\times {target_year}) + ({intercept:.2f}) = \\mathbf{{{predicted_temp:.2f}^\\circ\\text{{C}}}}$$
""")
