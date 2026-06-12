import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="세계 지진 위험도 분석",
    page_icon="🌎",
    layout="wide"
)

# -----------------------------
# 데이터 불러오기
# -----------------------------
df_new = pd.read_csv("earthquake.csv")

risk_dict = {
    0: "🔴 높음",
    1: "🟢 낮음",
    2: "🟡 중간"
}

colors = {
    0: "red",
    1: "blue",
    2: "green"
}

# -----------------------------
# 제목
# -----------------------------
st.title("🌎 세계 지진 위험도 분석 시스템")
st.markdown("---")

st.write(
    "위도와 경도를 입력하면 주변 지진 데이터를 기반으로 "
    "예상 위험도를 분석합니다."
)

# -----------------------------
# 사이드바
# -----------------------------
st.sidebar.header("📍 위치 입력")

lat = st.sidebar.number_input(
    "위도",
    value=37.5,
    format="%.4f"
)

lon = st.sidebar.number_input(
    "경도",
    value=127.0,
    format="%.4f"
)

analyze = st.sidebar.button("🚨 위험도 분석")

# -----------------------------
# 통계 카드
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    st.metric(
        "전체 지진 데이터",
        len(df_new)
    )

with col2:
    st.metric(
        "군집 종류",
        df_new["cluster"].nunique()
    )

# -----------------------------
# 분석 실행
# -----------------------------
if analyze:

    near_df = df_new[
        (df_new['위도'] >= lat - 5) &
        (df_new['위도'] <= lat + 5) &
        (df_new['경도'] >= lon - 5) &
        (df_new['경도'] <= lon + 5)
    ]

    if len(near_df) == 0:

        st.warning("⚠️ 주변 지진 데이터가 없습니다.")

    else:

        cluster_ratio = near_df['cluster'].value_counts(
            normalize=True
        )

        main_cluster = cluster_ratio.idxmax()

        st.success(
            f"### 예상 위험도 : {risk_dict[main_cluster]}"
        )

        st.metric(
            "주변 지진 발생 건수",
            len(near_df)
        )

        # -----------------------------
        # 지도 생성
        # -----------------------------
        m = folium.Map(
            location=[lat, lon],
            zoom_start=5,
            tiles="CartoDB positron"
        )

        df_sample = df_new.sample(
            min(500, len(df_new)),
            random_state=42
        )

        for _, row in df_sample.iterrows():

            cluster = row["cluster"]

            folium.CircleMarker(
                location=[
                    row["위도"],
                    row["경도"]
                ],
                radius=max(row["규모"], 3),
                color=colors[cluster],
                fill=True,
                fill_color=colors[cluster],
                fill_opacity=0.6,
                popup=f"""
                규모: {row['규모']}<br>
                군집: {cluster}
                """
            ).add_to(m)

        # 사용자 위치
        folium.Marker(
            location=[lat, lon],
            popup="📍 입력 위치",
            icon=folium.Icon(
                color="black",
                icon="info-sign"
            )
        ).add_to(m)

        st.subheader("🗺️ 지진 분포 지도")

        st_folium(
            m,
            width=None,
            height=650
        )

        # 데이터 테이블
        st.subheader("📊 주변 지진 데이터")

        st.dataframe(
            near_df.head(20),
            use_container_width=True
        )
