import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="인구 구조 변화 대시보드", page_icon="📈", layout="wide"
)


@st.cache_data
def load_and_clean_data(file_path: str = "pop_data.csv") -> pd.DataFrame:
    df = pd.read_csv(file_path)

    # 1. 공백 제거 및 쉼표 제거 후 수치형 변환
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip().replace("", np.nan)
            df[col] = df[col].str.replace(",", "")
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 2. 연령대별 비중(%) 계산
    age_cols = [
        "0-19세 (유소년/청소년)",
        "20-39세 (청년층)",
        "40-59세 (중장년층)",
        "60세 이상 (고령층)",
    ]
    for col in age_cols:
        pct_col_name = f"{col.split(' ')[0]}_비중(%)"
        df[pct_col_name] = ((df[col] / df["총인구"]) * 100).round(2)

    return df


df = load_and_clean_data()

st.title("📈 인구 구조 변화 분석 대시보드 (2010~2024)")

tab1, tab2, tab3 = st.tabs(
    ["📋 정제 데이터", "📊 주요 요약 지표", "📈 연령대별 인구 추이"]
)

# 탭 1: 정제 데이터
with tab1:
    st.subheader("📋 정제 완료된 데이터셋")
    st.dataframe(df, use_container_width=True)

# 탭 2: 주요 요약 지표
# 탭 2: 주요 요약 지표
with tab2:
    st.subheader("📌 2010년 대비 2024년 변화 (KPI)")

    # 해당 연도 행 추출 (데이터가 없을 수 있으므로 예외 처리)
    df_2010 = df[df["연도"] == 2010]
    df_2024 = df[df["연도"] == 2024]

    row_2010 = df_2010.iloc[0] if not df_2010.empty else None
    row_2024 = df_2024.iloc[0] if not df_2024.empty else None

    col1, col2, col3 = st.columns(3)

    # 안전하게 값 변환하는 함수
    def safe_int(val):
        if pd.isna(val) or val is None:
            return None
        try:
            return int(val)
        except (ValueError, TypeError):
            return None

    def safe_float(val):
        if pd.isna(val) or val is None:
            return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None

    # col1: 총인구
    with col1:
        pop_2024 = safe_int(row_2024['총인구']) if row_2024 is not None else None
        pop_2010 = safe_int(row_2010['총인구']) if row_2010 is not None else None

        val_str = f"{pop_2024:,} 명" if pop_2024 is not None else "데이터 없음"
        
        if pop_2024 is not None and pop_2010 is not None:
            delta_str = f"{pop_2024 - pop_2010:,} 명"
        else:
            delta_str = None

        st.metric("총인구", val_str, delta_str)

    # col2: 유소년층 비중
    with col2:
        ratio1_2024 = safe_float(row_2024['0-19세_비중(%)']) if row_2024 is not None else None
        ratio1_2010 = safe_float(row_2010['0-19세_비중(%)']) if row_2010 is not None else None

        val_str2 = f"{ratio1_2024:.1f}%" if ratio1_2024 is not None else "데이터 없음"
        
        if ratio1_2024 is not None and ratio1_2010 is not None:
            delta_str2 = f"{ratio1_2024 - ratio1_2010:.1f}%p"
        else:
            delta_str2 = None

        st.metric("유소년층 (0-19세) 비중", val_str2, delta_str2)

    # col3: 고령층 비중
    with col3:
        ratio2_2024 = safe_float(row_2024['60세_비중(%)']) if row_2024 is not None else None
        ratio2_2010 = safe_float(row_2010['60세_비중(%)']) if row_2010 is not None else None

        val_str3 = f"{ratio2_2024:.1f}%" if ratio2_2024 is not None else "데이터 없음"
        
        if ratio2_2024 is not None and ratio2_2010 is not None:
            delta_str3 = f"{ratio2_2024 - ratio2_2010:.1f}%p"
        else:
            delta_str3 = None

        st.metric("고령층 (60세 이상) 비중", val_str3, delta_str3)

    st.markdown("---")
    st.subheader("📊 기술통계량")
    st.dataframe(df.describe().round(2), use_container_width=True)

# 탭 3: 연령대별 인구 추이 그래프
with tab3:
    st.subheader("📈 연도별 연령대 인구수 추이 (명)")
    chart_data = df.set_index("연도")[
        [
            "0-19세 (유소년/청소년)",
            "20-39세 (청년층)",
            "40-59세 (중장년층)",
            "60세 이상 (고령층)",
        ]
    ]
    st.line_chart(chart_data, use_container_width=True)