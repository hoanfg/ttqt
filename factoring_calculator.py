import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --- 1. Hàm tính toán logic ---
def calculate_factoring_costs(advance_amount, advance_rate, discount_rate_annual, service_fee_rate, tenor_months):
    if advance_rate <= 0 or advance_rate > 1:
        return None
        
    total_ar = advance_amount / advance_rate
    service_fee = total_ar * service_fee_rate
    
    # Tính lãi suất theo ngày
    tenor_days = tenor_months * (365 / 12) # Approximation
    discount_rate_daily = discount_rate_annual / 365
    
    # Lãi suất được tính theo phương pháp chiết khấu: FV / (1 + r*t) - FV -> Simplified to direct cost for cash flow
    # Interest Cost (Simple interest on Advance Amount for tenor)
    discount_interest = advance_amount * discount_rate_annual * (tenor_months / 12.0)
    
    total_costs = service_fee + discount_interest
    net_cash_received = advance_amount - total_costs
    reserve = total_ar - advance_amount
    
    results = {
        "Trị giá Nợ phải thu (Total AR)": total_ar,
        "Khoản tiền Ứng trước (Advance Amount)": advance_amount,
        "Hoa hồng phí (Service Fee)": service_fee,
        "Lãi suất chiết khấu (Discount Interest)": discount_interest,
        "Tổng chi phí (Total Cost)": total_costs,
        "Số tiền Thực nhận (Net Cash Received)": net_cash_received,
        "Khoản Dự trữ (Reserve)": reserve,
    }
    
    return results

# --- 2. Hàm trực quan hóa chính (Cơ cấu AR) ---
def create_main_visualization(results):
    net_cash = results["Số tiền Thực nhận (Net Cash Received)"]
    total_costs = results["Tổng chi phí (Total Cost)"]
    reserve = results["Khoản Dự trữ (Reserve)"]
    total_ar = results["Trị giá Nợ phải thu (Total AR)"]
    
    data = pd.DataFrame({
        'Thành phần': ['Số tiền Thực nhận', 'Tổng Chi phí', 'Khoản Dự trữ'],
        'Giá trị (USD)': [net_cash, total_costs, reserve]
    })
    
    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.barh(data['Thành phần'], data['Giá trị (USD)'], color=['#4CAF50', '#F44336', '#FFC107'])
    
    ax.set_title(f'Cơ cấu Trị giá Nợ phải thu: {total_ar:,.2f} USD', fontsize=14)
    ax.set_xlabel('Giá trị (USD)', fontsize=12)
    ax.set_ylabel('')
    
    # Thêm nhãn giá trị
    for bar in bars:
        width = bar.get_width()
        ax.text(width + (total_ar * 0.005), bar.get_y() + bar.get_height()/2, 
                f'{width:,.2f} USD', va='center', fontsize=10)

    plt.xlim(0, total_ar * 1.1)
    return fig

# --- 3. Biểu đồ Phân tích Độ nhạy (Mới) ---
def create_sensitivity_chart(advance_amount, advance_rate, service_fee_rate, tenor_months):
    sensitivity_data = []
    base_interest = 12.0 / 100
    
    # Lãi suất thử nghiệm: -5%, base, +5%
    interest_scenarios = [0.07, base_interest, 0.17] 
    
    for rate in interest_scenarios:
        # Tính Net Cash Received cho từng kịch bản lãi suất
        total_ar = advance_amount / advance_rate
        service_fee = total_ar * service_fee_rate
        discount_interest = advance_amount * rate * (tenor_months / 12.0)
        net_cash = advance_amount - (service_fee + discount_interest)
        
        sensitivity_data.append({
            'Lãi suất': f"{rate*100:.1f}%",
            'Net Cash': net_cash
        })
        
    df = pd.DataFrame(sensitivity_data)

    fig, ax = plt.subplots(figsize=(6, 2))
    bars = ax.bar(df['Lãi suất'], df['Net Cash'], color=['#FFC107', '#4CAF50', '#F44336'])
    
    ax.set_title('Độ nhạy: Net Cash theo Lãi suất', fontsize=14)
    ax.set_ylabel('Net Cash (USD)', fontsize=12)
    ax.set_xlabel('Kịch bản Lãi suất/Năm', fontsize=12)
    
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 1000, 
                f'{yval:,.0f}', ha='center', fontsize=10)

    plt.grid(axis='y', linestyle='--', alpha=0.7)
    return fig

# --- 4. Xây dựng Giao diện Streamlit ---
st.set_page_config(page_title="Mô Hình Chi Phí Bao Thanh Toán", layout="wide")
st.title("💰 Công Cụ Mô Phỏng Chi Phí Bao Thanh Toán (Factoring)")
st.markdown("---")

# Sidebar cho Input (Dễ dàng thay đổi biến số)
st.sidebar.header("Tham Số Đầu Vào")

# Input widgets - LƯU Ý: Giữ nguyên tên biến để tránh lỗi
advance_amount = st.sidebar.number_input("Khoản tiền Ứng trước (USD)", value=120000.0, min_value=1.0, step=1000.0, format="%.2f")
advance_rate_percent = st.sidebar.slider("Tỷ lệ Ứng trước (%)", value=60, min_value=50, max_value=95, step=5)
service_fee_rate_percent = st.sidebar.slider("Hoa hồng phí Dịch vụ (%)", value=2.0, min_value=0.5, max_value=5.0, step=0.1, format="%.1f")
discount_rate_percent = st.sidebar.slider("Lãi suất Chiết khấu/Năm (%)", value=15.4, min_value=5.0, max_value=25.0, step=0.1, format="%.1f")
tenor_months = st.sidebar.slider("Kỳ hạn Bao thanh toán (Tháng)", value=6, min_value=1, max_value=12, step=1)

# Chuyển đổi Input sang định dạng thập phân
advance_rate = advance_rate_percent / 100.0
service_fee_rate = service_fee_rate_percent / 100.0
discount_rate_annual = discount_rate_percent / 100.0

# --- 5. Hiển thị Kết quả và Biểu đồ ---
if advance_amount and advance_rate:
    results = calculate_factoring_costs(
        advance_amount,
        advance_rate,
        discount_rate_annual,
        service_fee_rate,
        tenor_months
    )

    if results:
        st.header("Kết Quả Phân Tích Tài Chính")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Trị giá Nợ phải thu (Total AR)", f"{results['Trị giá Nợ phải thu (Total AR)']:,.2f} USD")
        col2.metric("Tổng Chi phí (Lãi + Phí)", f"{results['Tổng chi phí (Total Cost)']:,.2f} USD")
        col3.metric("Số tiền Thực nhận (Net Cash)", f"{results['Số tiền Thực nhận (Net Cash Received)']:,.2f} USD")

        st.markdown("---")

        # KHU VỰC BIỂU ĐỒ 1: Cơ cấu AR
        st.subheader("1. Cơ Cấu Khoản Phải Thu (Total AR)")
        fig_main = create_main_visualization(results)
        st.pyplot(fig_main)
        
        st.markdown("---")

        # KHU VỰC BIỂU ĐỒ 2: Độ nhạy (Sensitivity)
        st.subheader("2. Phân Tích Độ Nhạy Lãi suất")
        st.markdown("*(So sánh Net Cash Received ở các kịch bản Lãi suất khác nhau: Thấp (7%), Hiện tại, Cao (17%))*")
        fig_sensitivity = create_sensitivity_chart(
            advance_amount, 
            advance_rate, 
            service_fee_rate, 
            tenor_months
        )
        st.pyplot(fig_sensitivity)

