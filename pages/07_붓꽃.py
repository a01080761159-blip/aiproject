import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression

# 페이지 기본 설정
st.set_page_config(page_title="붓꽃(Iris) 품종 예측기", page_icon="🌸", layout="centered")

st.title("🌸 붓꽃(Iris) 품종 다중 알고리즘 예측기")
st.write("꽃잎(Petal) 또는 꽃받침(Sepal)의 크기와 분류 알고리즘을 선택하여 품종 예측 결과와 작동 원리를 비교해보세요.")

# 데이터 로드 및 각 특성 조합별 4가지 모델 학습 캐싱
@st.cache_resource
def load_data_and_train_models():
    iris = load_iris()
    df = pd.DataFrame(data=iris.data, columns=['SepalLength', 'SepalWidth', 'PetalLength', 'PetalWidth'])
    df['Species'] = [iris.target_names[i] for i in iris.target]
    y = df['Species']

    def train_suite(X):
        models = {
            "랜덤 포레스트 (Random Forest)": RandomForestClassifier(n_estimators=100, random_state=42),
            "K-최근접 이웃 (KNN)": KNeighborsClassifier(n_neighbors=5),
            "서포트 벡터 머신 (SVM)": SVC(probability=True, random_state=42),
            "로지스틱 회귀 (Logistic Regression)": LogisticRegression(random_state=42)
        }
        for model in models.values():
            model.fit(X, y)
        return models

    petal_models = train_suite(df[['PetalLength', 'PetalWidth']])
    sepal_models = train_suite(df[['SepalLength', 'SepalWidth']])
    
    return df, petal_models, sepal_models

df, petal_models, sepal_models = load_data_and_train_models()

# --- 사이드바: 공통 알고리즘 선택 ---
st.sidebar.header("⚙️ 알고리즘 설정")
selected_algorithm = st.sidebar.selectbox(
    "분류 알고리즘 선택",
    list(petal_models.keys())
)

# 알고리즘별 작동 원리 설명 딕셔너리
descriptions = {
    "랜덤 포레스트 (Random Forest)": """
    * **앙상블(Ensemble) 학습**: 수많은 **결정 트리(Decision Tree)**들을 무작위로 생성한 뒤, 각 트리가 내린 예측 결과를 종합하여 다수결 투표나 평균으로 최종 결론을 내리는 알고리즘입니다.
    * **장점**: 과적합(Overfitting)에 강하고 직관적이며, 데이터의 비선형적 특성을 매우 잘 학습합니다.
    """,
    "K-최근접 이웃 (KNN)": """
    * **거리 기반 분류**: 새로운 데이터가 들어왔을 때, 다차원 공간 상에서 **가장 가까운 K개의 주변 데이터**를 찾아 가장 비중이 높은 품종으로 분류하는 가장 직관적인 지도학습 알고리즘입니다.
    * **장점**: 별도의 복잡한 학습 모델을 만들지 않고 데이터 자체를 기억해두었다가 판별하므로 구현이 간단하고 직관적입니다.
    """,
    "서포트 벡터 머신 (SVM)": """
    * **최적의 경계선(Hyperplane) 탐색**: 데이터들을 가장 잘 구분할 수 있는 **결정 경계(초평면)**를 찾되, 서로 다른 품종 간의 마진(Margin, 여유 공간)이 최대가 되도록 최적화하는 알고리즘입니다.
    * **장점**: 데이터가 고차원이거나 경계선이 복잡한 경우에도 뛰어난 분류 성능과 일반화 능력을 발휘합니다.
    """,
    "로지스틱 회귀 (Logistic Regression)": """
    * **시그모이드(Sigmoid) 함수 활용**: 이름은 회귀이지만 대표적인 **선형 분류** 알고리즘입니다. 입력된 변수들의 선형 결합을 계산한 뒤, 시그모이드(또는 소프트맥스) 함수를 통해 특정 품종에 속할 확률(0~1 사이 값)을 계산하여 판별합니다.
    * **장점**: 연산 속도가 매우 빠르고 결과가 도출되는 과정(가중치)이 투명하여 해석하기 쉽습니다.
    """
}

# 탭 화면 렌더링 함수
def render_prediction_tab(
    models_dict, col_x, col_y, label_x, label_y,
    range_info, min_x, max_x, default_x, min_y, max_y, default_y, key_prefix
):
    st.info(range_info)
    
    # 사용자 입력 슬라이더 (2단 컬럼 배치)
    in_col1, in_col2 = st.columns(2)
    with in_col1:
        val_x = st.slider(f"{label_x} (cm)", min_value=min_x, max_value=max_x, value=default_x, step=0.1, key=f"{key_prefix}_x")
    with in_col2:
        val_y = st.slider(f"{label_y} (cm)", min_value=min_y, max_value=max_y, value=default_y, step=0.1, key=f"{key_prefix}_y")

    # 예측 수행
    current_model = models_dict[selected_algorithm]
    input_data = pd.DataFrame([[val_x, val_y]], columns=[col_x, col_y])
    prediction = current_model.predict(input_data)[0]
    prediction_proba = current_model.predict_proba(input_data)[0]

    # 결과 출력
    st.subheader(f"🔍 예측 결과 ({selected_algorithm})")
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.metric(label="예측된 붓꽃 품종", value=f"Iris-{prediction}")
    with res_col2:
        proba_df = pd.DataFrame({
            '품종': [f"Iris-{name}" for name in current_model.classes_],
            '확률 (%)': [round(p * 100, 1) for p in prediction_proba]
        })
        st.dataframe(proba_df, hide_index=True, use_container_width=True)

    # 시각화 (가로축: 길이, 세로축: 너비, 입력값: 핑크 별)
    st.subheader("📊 데이터 분포 및 입력값 위치")
    fig, ax = plt.subplots(figsize=(8, 5))

    colors = {'setosa': '#4C72B0', 'versicolor': '#55A868', 'virginica': '#C44E52'}
    for species, color in colors.items():
        subset = df[df['Species'] == species]
        ax.scatter(
            subset[col_x],
            subset[col_y],
            label=f"Iris-{species}",
            color=color,
            alpha=0.7,
            s=50
        )

    # 사용자 입력값 (핑크 별)
    ax.scatter(
        val_x,
        val_y,
        color='#FF1493',
        marker='*',
        s=350,
        edgecolor='black',
        linewidth=1.2,
        label='User Input (Your Flower)',
        zorder=5
    )

    ax.set_title(f"Iris {col_x} vs {col_y} ({selected_algorithm})", fontsize=13, fontweight='bold')
    ax.set_xlabel(f"{col_x} (cm)", fontsize=11)
    ax.set_ylabel(f"{col_y} (cm)", fontsize=11)
    ax.legend(loc='upper left', frameon=True)
    ax.grid(True, linestyle='--', alpha=0.5)

    st.pyplot(fig)

    # 그래프 하단 작동 원리 설명
    st.markdown("---")
    st.subheader(f"📖 [{selected_algorithm}] 작동 원리")
    st.markdown(descriptions[selected_algorithm])


# --- 탭 구성 ---
tab1, tab2 = st.tabs(["🌸 꽃잎 (Petal) 기준 예측", "🌿 꽃받침 (Sepal) 기준 예측"])

with tab1:
    render_prediction_tab(
        models_dict=petal_models,
        col_x='PetalLength',
        col_y='PetalWidth',
        label_x='꽃잎 길이 (Petal Length)',
        label_y='꽃잎 너비 (Petal Width)',
        range_info="**[꽃잎 데이터 입력 범위]** 꽃잎 길이: `1.0 ~ 6.9 cm` | 꽃잎 너비: `0.1 ~ 2.5 cm` (품종 구분력이 매우 높음)",
        min_x=0.5, max_x=7.5, default_x=3.8,
        min_y=0.1, max_y=3.0, default_y=1.2,
        key_prefix="petal"
    )

with tab2:
    render_prediction_tab(
        models_dict=sepal_models,
        col_x='SepalLength',
        col_y='SepalWidth',
        label_x='꽃받침 길이 (Sepal Length)',
        label_y='꽃받침 너비 (Sepal Width)',
        range_info="**[꽃받침 데이터 입력 범위]** 꽃받침 길이: `4.3 ~ 7.9 cm` | 꽃받침 너비: `2.0 ~ 4.4 cm` (일부 품종 간 영역이 겹침)",
        min_x=4.0, max_x=8.5, default_x=5.8,
        min_y=1.5, max_y=5.0, default_y=3.0,
        key_prefix="sepal"
    )
