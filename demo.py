import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager, rc
from datetime import datetime
import os

# 데이터셋을 로컬에서 불러오기
data_path = os.path.join("data", "demo_set.csv")
# font_path = os.path.join("data", "fonts", "malgun.ttf")

# # 폰트 설정
# import matplotlib.pyplot as plt
# from matplotlib import font_manager, rc

# font_name = font_manager.FontProperties(fname=font_path).get_name()
# rc('font', family=font_name)

@st.cache_data
def load_data():
    df = pd.read_csv(data_path)
    return df

# 데이터 로드
demo = load_data()

# 열 이름 매핑
column_mapping = {
    "Credit_Utilization_Ratio": "신용 사용 비율",
    "Debt_to_Income_Ratio": "부채 상환 비율",
    "OVERDUE_RATIO": "💸 대출 대비 연체 횟수",
    "Debt_Repayment_Capability_Index": "부채 상환 가능성 지수",
    "LOAN_COUNT": "과거 대출 횟수",
    "AMT_CREDIT": "현재 대출 금액",
    "NAME": "이름",
    "DAYS_BIRTH": "😀 나이",
    "FLAG_MOBIL": "📱 휴대전화 소유 여부",
    "FLAG_OWN_CAR_Y": "🚗 자차 소유 여부",
    "FLAG_OWN_REALTY_Y": "🏡 부동산 소유 여부",
    "DAYS_EMPLOYED": "🏢 재직 여부",
    "AMT_INCOME_TOTAL": "연간 소득",
    "LOAN_STATUS": "대출 상태"
}

# 컬럼명 매핑 적용
demo.rename(columns=column_mapping, inplace=True)

# 대출 상품 딕셔너리 정의
loan_types = {
    "Consumer loans": "소비자 대출",
    "Cash loans": "긴급자금 대출",
    "Revolving loans": "신용 한도 대출",
    "Mortgage": "주택담보 대출",
    "Car loan": "자동차 대출",
    "Microloan": "소액 대출"
}

# 사이드바 위젯 구성
name = st.sidebar.selectbox("이름을 선택하세요", demo["이름"].unique())

# 빈 공간 추가
st.sidebar.write(" ")
st.sidebar.write(" ")

selected_loan_type = st.sidebar.selectbox(
    "대출상품을 선택하세요",
    options=list(loan_types.keys()),
    format_func=lambda x: loan_types[x]
)

# 빈 공간 추가
st.sidebar.write(" ")
st.sidebar.write(" ")

credit_range = st.sidebar.slider(
    "대출 금액 범위 선택 (최대값: ₩50,000,000은 선택 불가)",
    min_value=1_000_000,
    max_value=50_000_000,
    value=(1_000_000, 50_000_000 - 1_000_000),
    step=1_000_000,
    format="₩%d"
)

credit_range_text = f"₩{credit_range[0] // 1_000_000}천만 원 ~ ₩{credit_range[1] // 1_000_000}천만 원"
st.sidebar.write(f"선택된 대출 금액 범위: {credit_range_text}")

# '확인하기' 버튼을 추가하여 연체 예측 결과를 확인
predict_button = st.sidebar.button("확인하기")

# 데이터 필터링
filtered_demo = demo[
    (demo["현재 대출 금액"] >= credit_range[0]) & 
    (demo["현재 대출 금액"] <= credit_range[1])
]

# 시각화 함수 정의
def create_style(ax):
    fig.patch.set_facecolor('#0E1117')  # 전체 figure 배경 색상 설정
    ax.set_facecolor('#0E1117')  # 개별 subplot 배경 색상 설정
    ax.spines['top'].set_color('#31333F')
    ax.spines['right'].set_color('#31333F')
    ax.spines['bottom'].set_color('#31333F')
    ax.spines['left'].set_color('#31333F')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')

if 'show_more' not in st.session_state:
    st.session_state.show_more = False

if predict_button:
    st.header(f"{name}님의 연체 예측 결과")

    selected_user = demo[demo["이름"] == name]

    if selected_user.empty:
        st.write("선택된 사용자 데이터가 없습니다.")
    else:
        selected_user = selected_user.iloc[0]

        def calculate_age(days_birth):
            today = datetime.today()
            birth_date = today - pd.to_timedelta(-days_birth, unit='D')
            age = today.year - birth_date.year
            if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
                age -= 1
            return age

        age = calculate_age(selected_user["😀 나이"])

        st.subheader("현재 나의 정보")
        st.markdown(f"**😀 나이:** {age} 세")
        st.markdown(f"**📱 휴대전화 소유 여부:** {'Y' if selected_user['📱 휴대전화 소유 여부'] else 'N'}")
        st.markdown(f"**🚗 자차 소유 여부:** {'Y' if selected_user['🚗 자차 소유 여부'] else 'N'}")
        st.markdown(f"**🏡 부동산 소유 여부:** {'Y' if selected_user['🏡 부동산 소유 여부'] else 'N'}")
        st.markdown(f"**🏢 재직 여부:** {'Y' if selected_user['🏢 재직 여부'] else 'N'}")

        # 점선 추가
        st.markdown("<hr style='border: 1px dashed #000;' />", unsafe_allow_html=True)

        # 대출 대비 연체 횟수
        st.write(f"**💸 대출 대비 연체 횟수:** {selected_user['💸 대출 대비 연체 횟수']}")

        # 대출 이력 연체 횟수 차트
        loan_count = int(selected_user["과거 대출 횟수"])  # 정수형으로 변환
        if loan_count > 0:
            fig, ax = plt.subplots(figsize=(8, 4))
            create_style(ax)
            ax.set_title('과거 대출 횟수 분포', color='white')

            bins_range = range(0, int(demo['과거 대출 횟수'].max()) + 1)
            sns.histplot(demo['과거 대출 횟수'], kde=False, ax=ax, color='lightblue', bins=bins_range)

            # 사용자 포인트 표시
            ax.axvline(loan_count, color='red', linestyle='--')
            ax.text(loan_count, ax.get_ylim()[1] * 0.9, f'{name}: {loan_count}번', color='#FF4B4B', ha='center')

            st.pyplot(fig)

            # 대출 이력 연체 횟수 차트
            overdue_data = demo[demo['💸 대출 대비 연체 횟수'] > 0]
            if not overdue_data.empty:
                st.write("**대출 대비 연체 횟수 분포**")
                fig, ax = plt.subplots(figsize=(8, 4))
                create_style(ax)
                ax.set_title('대출 대비 연체 횟수 분포', color='white')

                sns.countplot(x='💸 대출 대비 연체 횟수', data=overdue_data, ax=ax, palette='pastel')
                st.pyplot(fig)

            # 신용 사용 비율 차트
            st.write("신용 사용 비율")
            fig, ax = plt.subplots(figsize=(8, 4))
            create_style(ax)
            ax.set_title('신용 사용 비율 분포', color='white')

            sns.histplot(demo['신용 사용 비율'], kde=True, ax=ax, color='skyblue')

            # 사용자 포인트 표시
            ax.axvline(selected_user['신용 사용 비율'], color='red', linestyle='--')
            ax.text(selected_user['신용 사용 비율'], ax.get_ylim()[1] * 0.9, f'{name}: {selected_user["신용 사용 비율"]:.2f}', color='#FF4B4B', ha='center')

            st.pyplot(fig)

            # 연 수입 대비 총 부채 비율 차트
            st.write("연 수입 대비 총 부채 비율")
            fig, ax = plt.subplots(figsize=(8, 4))
            create_style(ax)
            ax.set_title('연 수입 대비 총 부채 비율 분포', color='white')

            sns.histplot(demo['부채 상환 비율'], kde=True, ax=ax, color='salmon')

            # 사용자 포인트 표시
            ax.axvline(selected_user['부채 상환 비율'], color='red', linestyle='--')
            ax.text(selected_user['부채 상환 비율'], ax.get_ylim()[1] * 0.9, f'{name}: {selected_user["부채 상환 비율"]:.2f}', color='#FF4B4B', ha='center')

            st.pyplot(fig)

        else:
            st.write("**조회할 대출 이력이 없습니다.**")
        
        # 점선 추가
        st.markdown("<hr style='border: 1px dashed #000;' />", unsafe_allow_html=True)

        # 대출 상품 정보와 평가 버튼 추가
        st.subheader("신청한 대출 정보")
        st.write(f"선택한 대출 상품: {selected_loan_type}")

        # 대출 가능성 평가 버튼
        evaluate_button = st.button("대출 가능성 평가")

        if evaluate_button:
            st.write("**대출 가능성 평가**")

            # 재직 기간 및 연수입 기준
            today = datetime.today()
            employment_duration_days = -selected_user["🏢 재직 여부"]
            employment_start_date = today - pd.to_timedelta(employment_duration_days, unit='D')
            employment_duration_years = (today - employment_start_date).days / 365.25

            annual_income = selected_user["연간 소득"]

            # 대출 가능성 기준 설정
            min_employment_duration_years = 1 # 1년 이상
            min_annual_income = 20_000_000 # 연 2천만원 이상

            feedback = []

            if employment_duration_years < min_employment_duration_years:
                feedback.append("재직 기간이 부족합니다. 재직 기간을 늘려보세요.")
            else:
                feedback.append("재직 기간은 충분합니다.")

            if annual_income < min_annual_income:
                feedback.append("연수입이 부족합니다. 연수입을 늘려보세요.")
            else:
                feedback.append("연수입은 충분합니다.")

            if not feedback:  # feedback 리스트가 비어있다면
                feedback.append("대출 가능성이 높습니다. 추가적인 조건이 필요한 경우, 금융 기관에 문의하세요.")

            for line in feedback:
                st.write(f" - {line}")
