import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import plotly.graph_objects as go
import os

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="월별 평균 기온 예측 비교",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 회귀 알고리즘별 월별 평균 기온 예측 비교")
st.markdown("과거 기온 데이터를 바탕으로 **여러 회귀 알고리즘(선형회귀, 랜던 포레스트, SVR)**을 학습시키고, 모델에 따른 예측 결과와 작동 방식을 비교합니다.")

# 2. 데이터 로드 및 전처리 함수 (캐싱 적용)
@st.cache_data
def load_data():
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "temperature.csv"))
    
    try:
        df = pd.read_csv(file_path, encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="utf-8")
    except FileNotFoundError:
        try:
            df = pd.read_csv("temperature.csv", encoding="cp949")
        except:
            df = pd.read_csv("temperature.csv", encoding="utf-8")

    df.columns = df.columns.str.strip()

    month_map = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }

    split_date = df["일시"].str.split("-")
    df["월_영문"] = split_date.str[0]
    yy = split_date.str[1].astype(int)

    df["연도"] = np.where(yy <= 26, 2000 + yy, 1900 + yy)
    df["월"] = df["월_영문"].map(month_map)

    df = df.dropna(subset=["평균기온(℃)", "연도", "월"]).sort_values(["연도", "월"]).reset_index(drop=True)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"⚠️ `temperature.csv` 파일을 불러오는 중 오류가 발생했습니다.\n\n상세 에러: {e}")
    st.stop()

# 3. 사용자 입력 (사이드바)
st.sidebar.header("🔍 예측 조건 설정")

# 알고리즘 선택 옵션 추가
model_type = st.sidebar.selectbox(
    "회귀 알고리즘 선택",
    options=["Linear Regression (선형회귀)", "Random Forest (랜덤 포레스트)", "SVR (서포트 벡터 레그레서)"],
    index=0
)

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

# 4. 선택된 월 데이터 필터링 및 선택된 모델 학습
month_df = df[df["월"] == selected_month].copy()

X = month_df[["연도"]].values  # 독립 변수 (연도)
y = month_df["평균기온(℃)"].values  # 종속 변수 (평균기온)

# 모델 생성 및 학습
if model_type == "Linear Regression (선형회귀)":
    model = LinearRegression()
    model.fit(X, y)
    model_name = "선형회귀 (Linear Regression)"
elif model_type == "Random Forest (랜덤 포레스트)":
    # 과적합 방지를 위해 n_estimators, max_depth 설정
    model = RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42)
    model.fit(X, y)
    model_name = "랜덤 포레스트 (Random Forest)"
else:
    # SVR은 스케일링에 민감하므로 Pipeline 사용
    model = make_pipeline(StandardScaler(), SVR(kernel='rbf', C=10.0, epsilon=0.1))
    model.fit(X, y)
    model_name = "서포트 벡터 머신 회귀 (SVR)"

# 예측 연도 범위 설정 (그래프 곡선용)
min_year = int(month_df["연도"].min())
line_years = np.arange(min_year, target_year + 1).reshape(-1, 1)

# 예측 수행
month_df["추세선_기온"] = model.predict(X)
line_temps = model.predict(line_years)
predicted_temp = model.predict(np.array([[target_year]]))[0]

# 5. 상단 핵심 지표 요약
col1, col2, col3 = st.columns(3)
col1.metric(
    label=f"[{model_type.split()[0]}] {target_year}년 {selected_month}월 예측 평균기온",
    value=f"{predicted_temp:.2f} ℃",
    delta=f"최근({int(month_df['연도'].max())}년) 대비 {predicted_temp - month_df['평균기온(℃)'].iloc[-1]:+.2f} ℃"
)
col2.metric(
    label="선택된 알고리즘",
    value=model_type,
    delta="학습 완료"
)
col3.metric(
    label=f"역대 {selected_month}월 전체 평균기온",
    value=f"{y.mean():.2f} ℃",
    delta=f"관측 데이터 수: {len(month_df)}개"
)

# 6. 시각화 (Plotly)
fig = go.Figure()

# (1) 실제 관측된 월별 평균 기온 산점도
fig.add_trace(go.Scatter(
    x=month_df["연도"],
    y=month_df["평균기온(℃)"],
    mode="lines+markers",
    name=f"실제 {selected_month}월 평균기온",
    line=dict(color="rgba(70, 130, 180, 0.4)", width=1.2),
    marker=dict(color="#1f77b4", size=6),
    hovertemplate="<b>%{x}년</b><br>실제 평균기온: %{y:.1f}℃<extra></extra>"
))

# (2) 알고리즘별 예측/추세선 (과거 ~ 미래 전체 연장)
fig.add_trace(go.Scatter(
    x=line_years.flatten(),
    y=line_temps,
    mode="lines",
    name=f"{model_name} 예측 곡선/추세선",
    line=dict(color="#ff7f0e", width=3),
    hovertemplate="<b>%{x}년</b><br>모델 예측 기온: %{y:.2f}℃<extra></extra>"
))

# (3) 목표 예측 연도 포인트 강조
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

fig.update_layout(
    title=f"<b>{selected_month}월 평균기온 추이 및 [{model_type}]을 이용한 {target_year}년 예측</b>",
    xaxis_title="연도 (Year)",
    yaxis_title="평균기온 (℃)",
    hovermode="closest",
    height=550,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

# 7. 그래프 하단: 선택된 알고리즘 작동 원리 설명
st.divider()
st.subheader(f"📘 현재 선택된 알고리즘 원리: {model_type}")

if "Linear Regression" in model_type:
    slope = model.coef_[0]
    intercept = model.intercept_
    st.markdown(f"""
    **선형회귀 (Linear Regression)**
    * **작동 원리:** 데이터 전체를 관통하는 단 하나의 **직선($y = wx + b$)**을 그립니다. 모든 실제값과 직선 사이의 오차 제곱합이 최소가 되도록 기울기($w$)와 절편($b$)을 찾습니다.
    * **특징 및 한계:** 연도가 흐름에 따라 기온이 일정한 비율(기울기 **{slope:+.4f}℃/년**)로 꾸준히 증가하거나 감소한다는 가정(단조로운 트렌드)을 세울 때 적합합니다. 단, 급격한 변동이나 비선형적인 패턴을 유연하게 표현하기는 어렵습니다.
    """)
elif "Random Forest" in model_type:
    st.markdown(f"""
    **랜덤 포레스트 회귀 (Random Forest Regressor)**
    * **작동 원리:** 수많은 **결정 트리(Decision Tree)**를 앙상블(Ensemble) 형태로 묶어 예측하는 알고리즘입니다. 데이터 구간을 여러 가지 조건(가지치기)으로 나누어 각 그룹의 평균값으로 예측합니다.
    * **특징 및 한계:** 직선 형태가 아니라 **계단식 또는 구불구불한 곡선** 형태로 예측선이 나타납니다. 과거의 특정한 변동 패턴이나 급격한 기온 변화를 유연하게 반영할 수 있지만, 학습 범위를 벗어나는 미래 장기 예측(외삽)에서는 값이 일정하게 수렴하거나 제한될 수 있습니다.
    """)
else:
    st.markdown(f"""
    **서포트 벡터 레그레서 (Support Vector Regressor, SVR)**
    * **작동 원리:** 허용 가능한 오차 범위(Epsilon-tube) 안에서 데이터들을 가장 잘 설명하는 초평면(직선 또는 곡선)을 찾는 알고리즘입니다. 커널(Kernel, 예: RBF) 기법을 사용해 비선형 관계도 유연하게 학습합니다.
    * **특징 및 한계:** 데이터의 국소적인 변동과 전반적인 트렌드를 조화롭게 반영합니다. 이상치(Outlier)에 상대적으로 강건하며, 부드러운 곡선 형태로 미래 기온을 예측합니다.
    """)
