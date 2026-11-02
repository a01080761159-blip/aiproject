
import folium
from streamlit_folium import st_folium

# 페이지 설정
st.set_page_config(
    page_title="서울 관광 명소 TOP 10",
    page_icon="🗺️",
    layout="wide"
)

# 관광지 데이터
PLACES = [
    {
        "rank": 1,
        "name": "명동",
        "category": "쇼핑 · 먹거리",
        "lat": 37.5636,
        "lon": 126.9869,
        "description": "화장품과 패션 매장, 길거리 음식이 모여 있는 서울 대표 쇼핑 거리예요.",
        "tip": "저녁에는 길거리 음식과 야경을 함께 즐겨 보세요."
    },
    {
        "rank": 2,
        "name": "N서울타워",
        "category": "전망 · 랜드마크",
        "lat": 37.5512,
        "lon": 126.9882,
        "description": "남산 정상에 있는 서울의 대표 전망 명소로, 도심 풍경을 감상할 수 있어요.",
        "tip": "해 질 무렵 방문하면 낮과 밤의 서울 풍경을 모두 볼 수 있어요."
    },
    {
        "rank": 3,
        "name": "코엑스 · 별마당도서관",
        "category": "쇼핑 · 문화",
        "lat": 37.5116,
        "lon": 127.0594,
        "description": "대형 쇼핑몰과 전시 공간, 높은 서가가 인상적인 별마당도서관이 있는 복합문화공간이에요.",
        "tip": "실내에서 쇼핑과 문화 체험을 함께 즐기기 좋아요."
    },
    {
        "rank": 4,
        "name": "강남역 일대",
        "category": "쇼핑 · 도심 체험",
        "lat": 37.4979,
        "lon": 127.0276,
        "description": "패션 매장과 맛집, 카페가 밀집한 활기찬 서울의 중심 상권이에요.",
        "tip": "주변 골목의 개성 있는 카페와 식당도 둘러보세요."
    },
    {
        "rank": 5,
        "name": "홍대 거리",
        "category": "문화 · 공연",
        "lat": 37.5563,
        "lon": 126.9236,
        "description": "거리 공연과 음악, 개성 있는 상점과 카페를 만날 수 있는 젊은 문화 거리예요.",
        "tip": "주말에는 거리 공연과 플리마켓을 구경해 보세요."
    },
    {
        "rank": 6,
        "name": "동대문디자인플라자(DDP)",
        "category": "건축 · 전시",
        "lat": 37.5669,
        "lon": 127.0095,
        "description": "독특한 곡선형 건축물로 유명하며 전시와 디자인 행사가 열리는 문화 공간이에요.",
        "tip": "건물 외관과 주변 야경을 사진으로 남겨 보세요."
    },
    {
        "rank": 7,
        "name": "경복궁",
        "category": "역사 · 전통문화",
        "lat": 37.5796,
        "lon": 126.9770,
        "description": "조선 왕조의 대표 궁궐로, 한국의 전통 건축과 역사를 경험할 수 있어요.",
        "tip": "한복을 입고 궁궐을 둘러보면 특별한 추억을 만들 수 있어요."
    },
    {
        "rank": 8,
        "name": "광장시장",
        "category": "전통시장 · 먹거리",
        "lat": 37.5700,
        "lon": 126.9998,
        "description": "빈대떡과 김밥 등 다양한 한국 음식을 맛볼 수 있는 서울의 대표 전통시장이에요.",
        "tip": "여러 음식을 조금씩 맛보며 시장 분위기를 즐겨 보세요."
    },
    {
        "rank": 9,
        "name": "북촌한옥마을",
        "category": "전통 · 산책",
        "lat": 37.5826,
        "lon": 126.9830,
        "description": "전통 한옥이 모여 있는 마을로 한국의 옛 주거문화를 느낄 수 있어요.",
        "tip": "실제 주민이 생활하는 공간이므로 조용히 관람해 주세요."
    },
    {
        "rank": 10,
        "name": "성수동 카페거리",
        "category": "카페 · 트렌드",
        "lat": 37.5445,
        "lon": 127.0560,
        "description": "옛 공장을 개조한 카페와 편집숍, 팝업스토어가 모여 있는 트렌디한 거리예요.",
        "tip": "개성 있는 디저트 카페와 기간 한정 팝업을 찾아보세요."
    }
]

# 제목
st.title("🗺️ 외국인 관광객이 사랑하는 서울 TOP 10")
st.caption("서울의 대표 관광 명소를 지도에서 찾아보세요!")

st.info(
    "이 목록은 서울의 주요 관광지와 외국인 관광객 방문 정보를 참고해 구성한 추천 목록입니다. "
    "공식적인 통합 순위는 아닙니다."
)

# 서울 지도 생성
m = folium.Map(
    location=[37.5665, 126.9780],
    zoom_start=11,
    tiles="OpenStreetMap",
    control_scale=True
)

# 지도에 관광지 마커 표시
for place in PLACES:

    popup_html = f"""
    <div style="width:220px; font-family:Arial;">
        <h4>{place['rank']}. {place['name']}</h4>
        <p>{place['category']}</p>
        <p>{place['description']}</p>
    </div>
    """

    folium.Marker(
        location=[place["lat"], place["lon"]],
        tooltip=f"{place['rank']}위 · {place['name']}",
        popup=folium.Popup(popup_html, max_width=280),
        icon=folium.DivIcon(
            html=f"""
            <div style="
                background:#e84b62;
                color:white;
                border:2px solid white;
                border-radius:50%;
                width:30px;
                height:30px;
                line-height:26px;
                text-align:center;
                font-weight:bold;
                font-size:13px;
                box-shadow:0 1px 5px rgba(0,0,0,.35);
            ">{place['rank']}</div>
            """,
            icon_size=(30, 30),
            icon_anchor=(15, 15)
        )
    ).add_to(m)

# 지도 출력
st.subheader("📍 서울 관광지 지도")
st.write("지도에 표시된 숫자 마커를 클릭하면 관광지 설명을 볼 수 있어요!")

st_folium(
    m,
    use_container_width=True,
    height=570,
    returned_objects=[]
)

# 관광지 소개
st.divider()
st.subheader("✨ 서울 관광지 TOP 10 소개")

left, right = st.columns(2)

for index, place in enumerate(PLACES):

    target = left if index % 2 == 0 else right

    with target:
        with st.container(border=True):

            st.markdown(
                f"### {place['rank']}. {place['name']}"
            )

            st.caption(place["category"])

            st.write(place["description"])

            st.markdown(
                f"**💡 여행 팁:** {place['tip']}"
            )

            st.markdown(
                f"[🧭 지도에서 길찾기](https://www.google.com/maps/search/?api=1&query={place['lat']},{place['lon']})"
            )

# 하단 안내
st.divider()

st.caption(
    "서울의 대표 관광지를 소개하는 관광 안내 웹앱입니다. "
    "방문 전 운영 시간과 휴무일을 확인해 주세요."
)
