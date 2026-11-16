import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

# 페이지 기본 설정
st.set_page_config(page_title="붓꽃(Iris) 품종 예측기", page_icon="🌸", layout="centered")

st.title("🌸 붓꽃(Iris) 품종 예측 웹 애플리케이션")
st.write("꽃잎의 길이와 너비를 입력하면 머신러닝 모델이 붓꽃의 품종을 예측하고 그래프에 위치를 표시합니다.")

# 데이터 로드 및 모델 학습 (캐싱 적용으로 속도 최적화)
@st.cache_resource
def load_data_and_train_model():
    iris = load_iris()
    df = pd.DataFrame(data=iris.data, columns=['SepalLength', 'SepalWidth', 'PetalLength', 'PetalWidth'])
    df['Species'] = [iris.target_names[i] for i in iris.target]
    
    # 특성(꽃잎 길이, 꽃잎 너비) 및 타겟 설정
    X = df[['PetalLength', 'PetalWidth']]
    y = df['Species']
    
    # 랜덤 포레스트 분류 모델 학습
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    return df, model

df, model = load_data_and_train_model()

# --- 사이드바: 사용자 입력 및 범위 안내 ---
st.sidebar.header("📏 꽃잎 크기 입력")
st.sidebar.info(
    "**[실제 데이터셋 범위 안내]**\n"
    "- **꽃잎 길이 (Petal Length)**: 1.0 ~ 6.9 cm\n"
    "- **꽃잎 너비 (Petal Width)**: 0.1 ~ 2.5 cm"
)

petal_length = st.sidebar.slider(
    "꽃잎 길이 (Petal Length, cm)",
    min_value=0.5,
    max_value=7.5,
    value=3.8,
    step=0.1
)

petal_width = st.sidebar.slider(
    "꽃잎 너비 (Petal Width, cm)",
    min_value=0.1,
    max_value=3.0,
    value=1.2,
    step=0.1
)

# --- 품종 예측 ---
input_data = pd.DataFrame([[petal_length, petal_width]], columns=['PetalLength', 'PetalWidth'])
prediction = model.predict(input_data)[0]
prediction_proba = model.predict_proba(input_data)[0]

# --- 결과 출력 ---
st.subheader("🔍 예측 결과")
col1, col2 = st.columns(2)

with col1:
    st.metric(label="예측된 붓꽃 품종", value=f"Iris-{prediction}")

with col2:
    proba_df = pd.DataFrame({
        '품종': [f"Iris-{name}" for name in model.classes_],
        '확률 (%)': [round(p * 100, 1) for p in prediction_proba]
    })
    st.dataframe(proba_df, hide_index=True, use_container_width=True)

# --- 시각화 (가로축: 꽃잎 길이, 세로축: 꽃잎 너비, 입력값: 핑크 별) ---
st.subheader("📊 데이터 분포 및 입력값 위치")

fig, ax = plt.subplots(figsize=(8, 5))

colors = {'setosa': '#4C72B0', 'versicolor': '#55A868', 'virginica': '#C44E52'}
for species, color in colors.items():
    subset = df[df['Species'] == species]
    ax.scatter(
        subset['PetalLength'],
        subset['PetalWidth'],
        label=f"Iris-{species}",
        color=color,
        alpha=0.7,
        s=50
    )

# 사용자 입력값 표시 (핑크 별)
ax.scatter(
    petal_length,
    petal_width,
    color='#FF1493',      # 선명한 딥 핑크
    marker='*',           # 별 모양 마커
    s=350,                # 마커 크기 강조
    edgecolor='black',    # 테두리 검정색으로 가독성 확보
    linewidth=1.2,
    label='User Input (Your Flower)',
    zorder=5
)

ax.set_title("Iris Petal Length vs Petal Width", fontsize=14, fontweight='bold')
ax.set_xlabel("Petal Length (cm)", fontsize=12)
ax.set_ylabel("Petal Width (cm)", fontsize=12)
ax.legend(loc='upper left', frameon=True)
ax.grid(True, linestyle='--', alpha=0.5)

st.pyplot(fig)
