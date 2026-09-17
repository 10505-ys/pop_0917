import streamlit as st
import pandas as pd
import numpy as np

# 페이지 기본 설정
st.set_page_config(
    page_title="인구 구조 변화 분석 대시보드",
    page_icon="📈",
    layout="wide"
)

st.title("📈 인구 구조 변화 분석 대시보드 (2010~2024)")

# -----------------------------------------------------------------------------
# 1. 데이터 불러오기 및 전처리 (사용자 환경에 맞게 로딩 로직을 수정해 주세요)
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    # 예시: 기존 데이터 파일이 있다면 가져오기
    # df = pd.read_csv('your_data.csv')
    
    # 예시 데이터셋 구조 (실제 불러오는 데이터로 대체 가능)
    data = {
        '연도': list(range(2010, 2025)),
        '0-19세 (유소년/청소년)': [985, 951, 920, 891, 863, 834, 806, None, None, None, None, None, None, None, None],
        '20-39세 (청년층)': [None] * 15,
        '40-59세 (중장년층)': [None] * 15,
        '60세 이상 (고령층)': [770, 805, 845, 890, 935, 980, None, None, None, None, None, None, None, None, None],
        '총인구': [770, 805, 845, 890, 935, 980, None, None, None, None, None, None, None, None, None],
        '0-19세_비중(%)': [None] * 15,
        '20-39세_비중(%)': [None] * 15,
        '40-59세_비중(%)': [None] * 15,
        '60세_비중(%)': [None] * 15,
    }
    df = pd.DataFrame(data)
    
    # 숫자로 형변환 가능한 컬럼 변환
    numeric_cols = [c for c in df.columns if c != '연도']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    return df

# 데이터 로드
try:
    df = load_data()
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# -----------------------------------------------------------------------------
# 2. 안전한 형변환 헬퍼 함수 정의 (None / NaN 에러 방지)
# -----------------------------------------------------------------------------
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

# -----------------------------------------------------------------------------
# 3. 탭 구성
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📑 정제 데이터", "📊 주요 요약 지표", "📈 연령대별 인구 추이"])

# -----------------------------------------------------------------------------
# 탭 1: 정제 데이터
# -----------------------------------------------------------------------------
with tab1:
    st.subheader("📑 정제 완료된 데이터셋")
    st.dataframe(df, use_container_width=True)

# -----------------------------------------------------------------------------
# 탭 2: 주요 요약 지표 (KPI)
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("📌 2010년 대비 2024년 변화 (KPI)")

    # 해당 연도 행 추출
    df_2010 = df[df["연도"] == 2010]
    df_2024 = df[df["연도"] == 2024]

    row_2010 = df_2010.iloc[0] if not df_2010.empty else None
    row_2024 = df_2024.iloc[0] if not df_2024.empty else None

    col1, col2, col3 = st.columns(3)

    # Col 1: 총인구
    with col1:
        pop_2024 = safe_int(row_2024['총인구']) if row_2024 is not None else None
        pop_2010 = safe_int(row_2010['총인구']) if row_2010 is not None else None

        val_str = f"{pop_2024:,} 명" if pop_2024 is not None else "데이터 없음"
        delta_str = f"{pop_2024 - pop_2010:,} 명" if (pop_2024 is not None and pop_2010 is not None) else None

        st.metric("총인구", val_str, delta_str)

    # Col 2: 유소년층 (0-19세) 비중
    with col2:
        ratio1_2024 = safe_float(row_2024['0-19세_비중(%)']) if row_2024 is not None else None
        ratio1_2010 = safe_float(row_2010['0-19세_비중(%)']) if row_2010 is not None else None

        val_str2 = f"{ratio1_2024:.1f}%" if ratio1_2024 is not None else "데이터 없음"
        delta_str2 = f"{ratio1_2024 - ratio1_2010:.1f}%p" if (ratio1_2024 is not None and ratio1_2010 is not None) else None

        st.metric("유소년층 (0-19세) 비중", val_str2, delta_str2)

    # Col 3: 고령층 (60세 이상) 비중
    with col3:
        ratio2_2024 = safe_float(row_2024['60세_비중(%)']) if row_2024 is not None else None
        ratio2_2010 = safe_float(row_2010['60세_비중(%)']) if row_2010 is not None else None

        val_str3 = f"{ratio2_2024:.1f}%" if ratio2_2024 is not None else "데이터 없음"
        delta_str3 = f"{ratio2_2024 - ratio2_2010:.1f}%p" if (ratio2_2024 is not None and ratio2_2010 is not None) else None

        st.metric("고령층 (60세 이상) 비중", val_str3, delta_str3)

    st.markdown("---")
    st.subheader("📊 기술통계량")
    st.dataframe(df.describe().round(2), use_container_width=True)

# -----------------------------------------------------------------------------
# 탭 3: 연령대별 인구 추이 그래프
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("📈 연도별 연령대 인구수 추이 (명)")
    
    # 선 그래프로 그릴 연령대 컬럼 선택
    graph_cols = [c for c in ['0-19세 (유소년/청소년)', '20-39세 (청년층)', '40-59세 (중장년층)', '60세 이상 (고령층)'] if c in df.columns]
    
    if graph_cols:
        chart_data = df.set_index('연도')[graph_cols]
        st.line_chart(chart_data)
    else:
        st.info("시각화할 연령대 컬럼이 존재하지 않습니다.")
