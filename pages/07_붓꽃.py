import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

# 페이지 기본 설정
st.set_page_config(page_title="붓꽃(Iris) 3대 알고리즘 비교 예측기", page_icon="🌸", layout="centered")

st.title("🌸 붓꽃(Iris) 3대 알고리즘 비교 예측 웹 애플리케이션")
st.write("꽃잎(Petal) 또는 꽃받침(Sepal)의 크기를 입력하면 **랜덤 포레스트, KNN, SVM** 3가지 알고리즘의 예측 결과와 확률을 한눈에 비교할 수 있습니다.")

# 데이터 로드 및 3가지 모델 학습 캐싱
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
            "서포트 벡터 머신 (SVM)": SVC(probability=True, random_state=42)
        }
        for model in models.values():
            model.fit(X, y)
        return models

    petal_models = train_suite(df[['PetalLength', 'PetalWidth']])
    sepal_models = train_suite(df[['SepalLength', 'SepalWidth']])
    
    return df, petal_models, sepal_models

df, petal_models, sepal_models = load_data_and_train_models()

# 알고리즘별 작동 원리 설명 딕셔너리
descriptions = {
    "랜덤 포레스트 (Random Forest)": """
    * **앙상블(Ensemble) 학습**: 수많은 **결정 트리(Decision Tree)**들을 무작위로 생성한 뒤, 각 트리의 예측 결과를 종합하여 다수결 투표로 결론을 내립니다.
    * **장점**: 과적합에 강하고 비선형적 특성을 매우 잘 학습합니다.
    """,
    "K-최근접 이웃 (KNN)": """
    * **거리 기반 분류**: 새로운 데이터 주변에서 **가장 가까운 K개의 데이터**를 찾아 다수결로 품종을 분류하는 직관적인 알고리즘입니다.
    * **장점**: 별도의 복잡한 학습 없이 데이터 자체를 활용해 직관적입니다.
    """,
    "서포트 벡터 머신 (SVM)": """
    * **최적의 경계선(Hyperplane) 탐색**: 품종 간의 마진(여유 공간)이 최대가 되도록 최적의 결정 경계를 찾는 알고리즘입니다.
    * **장점**: 복잡한 경계선에서도 뛰어난 분류 성능과 일반화 능력을 발휘합니다.
    """
}

# 탭 화면 렌더링 함수 (3개 알고리즘 동시 비교)
def render_comparison_tab(
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

    input_data = pd.DataFrame([[val_x, val_y]], columns=[col_x, col_y])

    # --- 3개 알고리즘 결과 비교 섹션 ---
    st.subheader("🔍 3대 알고리즘 예측 결과 비교")
    
    col_a, col_b, col_c = st.columns(3)
    cols = [col_a, col_b, col_c]
    
    for i, (algo_name, model) in enumerate(models_dict.items()):
        prediction = model.predict(input_data)[0]
        prediction_proba = model.predict_proba(input_data)[0]
        
        with cols[i]:
            st.markdown(f"**{algo_name.split(' ')[0]}**")
            st.metric(label="예측 품종", value=f"Iris-{prediction}")
            
            proba_df = pd.DataFrame({
                '품종': [name[:3] for name in model.classes_],
                '확률(%)': [round(p * 100, 1) for p in prediction_proba]
            })
            st.dataframe(proba_df, hide_index=True, use_container_width=True)

    # --- 시각화 (가로축: 길이, 세로축: 너비, 입력값: 핑크 별) ---
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

    ax.set_title(f"Iris {col_x} vs {col_y} Distribution", fontsize=13, fontweight='bold')
    ax.set_xlabel(f"{col_x} (cm)", fontsize=11)
    ax.set_ylabel(f"{col_y} (cm)", fontsize=11)
    ax.legend(loc='upper left', frameon=True)
    ax.grid(True, linestyle='--', alpha=0.5)

    st.pyplot(fig)

    # 그래프 하단 3가지 알고리즘 작동 원리 설명
    st.markdown("---")
    st.subheader("📖 3대 알고리즘 작동 원리")
    for algo_name, desc in descriptions.items():
        st.markdown(f"**[{algo_name}]**")
        st.markdown(desc)


# --- 탭 구성 ---
tab1, tab2 = st.tabs(["🌸 꽃잎 (Petal) 기준 비교", "🌿 꽃받침 (Sepal) 기준 비교"])

with tab1:
    render_comparison_tab(
        models_dict=petal_models,
        col_x='PetalLength',
        col_y='PetalWidth',
        label_x='꽃잎 길이 (Petal Length)',
        label_y='꽃잎 너비 (Petal Width)',
        range_info="**[꽃잎 데이터 입력 범위]** 꽃잎 길이: `1.0 ~ 6.9 cm` | 꽃잎 너비: `0.1 ~ 2.5 cm` (품종 간 구분력이 매우 뛰어남)",
        min_x=0.5, max_x=7.5, default_x=3.8,
        min_y=0.1, max_y=3.0, default_y=1.2,
        key_prefix="petal"
    )

with tab2:
    render_comparison_tab(
        models_dict=sepal_models,
        col_x='SepalLength',
        col_y='SepalWidth',
        label_x='꽃받침 길이 (Sepal Length)',
        label_y='꽃받침 너비 (Sepal Width)',
        range_info="**[꽃받침 데이터 입력 범위]** 꽃받침 길이: `4.3 ~ 7.9 cm` | 꽃받침 너비: `2.0 ~ 4.4 cm` (일부 품종 영역이 겹침)",
        min_x=4.0, max_x=8.5, default_x=5.8,
        min_y=1.5, max_y=5.0, default_y=3.0,
        key_prefix="sepal"
    )
