import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import math # Import thư viện math cho tính toán ngày

# --- 1. Hàm tính toán logic (THÊM CỘT & CHỈ SỐ) ---
def calculate_factoring_costs(advance_amount, advance_rate, discount_rate_annual, service_fee_rate, tenor_months):
    if advance_rate <= 0 or advance_rate > 1:
        return None
        
    total_ar = advance_amount / advance_rate
    service_fee = total_ar * service_fee_rate
    
    # Tính toán chi phí Lãi suất theo số ngày chính xác (giả định 360 ngày/năm)
    tenor_days = tenor_months * (30) 
    discount_rate_daily = discount_rate_annual / 360
    discount_interest = advance_amount * discount_rate_daily * tenor_days
    
    total_costs = service_fee + discount_interest
    net_cash_received = advance_amount - total_costs
    reserve = total_ar - advance_amount
    
    # --- CHỈ SỐ MỚI ---
    if total_costs > 0:
        # Tỷ suất sinh lời (Lợi nhuận ròng/Giá trị nợ)
        net_profit_rate = (net_cash_received / total_ar) * 100 
        # Chi phí hiệu quả hàng năm (Annualized Cost Rate)
        annualized_cost_rate = (total_costs / net_cash_received) * (360 / tenor_days) * 100
        # Phần trăm Chi phí là Lãi suất
        interest_cost_ratio = (discount_interest / total_costs) * 100
    else:
        net_profit_rate = annualized_cost_rate = interest_cost_ratio = 0
    
    results = {
        "Trị giá Nợ phải thu (Total AR)": total_ar,
        "Khoản tiền Ứng trước (Advance Amount)": advance_amount,
        "Khoản Dự trữ (Reserve)": reserve,
        "Hoa hồng phí (Service Fee)": service_fee,
        "Lãi suất chiết khấu (Interest Cost)": discount_interest,
        "Tổng chi phí (Total Cost)": total_costs,
        "Số tiền Thực nhận (Net Cash Received)": net_cash_received,
        # --- CÁC CỘT CHỈ SỐ MỚI ---
        "Tỷ suất Lợi nhuận ròng (%)": net_profit_rate,
        "Tỷ suất Chi phí Hiệu quả/Năm (%)": annualized_cost_rate,
        "Phần trăm Chi phí là Lãi suất (%)": interest_cost_ratio,
    }
    
    return results

# --- 2. Hàm trực quan hóa chính (Cơ cấu AR - Biểu đồ Cột dọc) ---
def create_main_visualization(results):
    net_cash = results["Số tiền Thực nhận (Net Cash Received)"]
    total_costs = results["Tổng chi phí (Total Cost)"]
    reserve = results["Khoản Dự trữ (Reserve)"]
    total_ar = results["Trị giá Nợ phải thu (Total AR)"]
    
    # Sắp xếp theo giá trị
    data = pd.DataFrame({
        'Thành phần': ['Số tiền Thực nhận', 'Khoản Dự trữ', 'Tổng Chi phí'],
        'Giá trị (USD)': [net_cash, reserve, total_costs]
    }).sort_values(by='Giá trị (USD)', ascending=False)
    
    colors = ['#4CAF50', '#FFC107', '#F44336'] # Xanh lá, Vàng, Đỏ
    
    plt.style.use('default') 
    fig, ax = plt.subplots(figsize=(9, 4.5), facecolor='white') 
    
    bars = ax.bar(data['Thành phần'], data['Giá trị (USD)'], color=colors)
    
    ax.set_title(f'1. Cơ cấu Trị giá Nợ phải thu: {total_ar:,.2f} USD', fontsize=14, color='black')
    ax.set_ylabel('Giá trị (USD)', fontsize=12, color='black') 
    ax.set_xlabel('')
    ax.tick_params(axis='x', colors='black', rotation=15)
    ax.tick_params(axis='y', colors='black')
    ax.set_facecolor('white')
    
    ax.grid(axis='y', linestyle='--', alpha=0.7, color='lightgray')
    for spine in ax.spines.values():
        spine.set_edgecolor('black')

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + (total_ar * 0.005), 
                f'{height:,.0f} USD', ha='center', fontsize=10, color='black') # Giảm số chữ số thập phân
    
    plt.ylim(0, max(data['Giá trị (USD)']) * 1.15) 
    plt.tight_layout()
    return fig

# --- 3. Biểu đồ Thay thế: Tỷ trọng Chi phí (Matplotlib Vertical Bar Chart) ---
def create_cost_composition_chart(results):
    service_fee = results["Hoa hồng phí (Service Fee)"]
    discount_interest = results["Lãi suất chiết khấu (Interest Cost)"]
    total_costs = results["Tổng chi phí (Total Cost)"]

    # Chỉ hiển thị nếu có chi phí
    if total_costs <= 0:
        fig, ax = plt.subplots(figsize=(7, 3.8))
        ax.text(0.5, 0.5, "Không có chi phí để phân tích.", ha='center', va='center', fontsize=12)
        ax.axis('off')
        return fig
    
    # Dữ liệu cho biểu đồ cột so sánh
    data = pd.DataFrame({
        'Thành phần': ['Chi phí Lãi suất', 'Hoa hồng phí'],
        'Giá trị': [discount_interest, service_fee]
    }).sort_values(by='Giá trị', ascending=False)
    
    # Màu sắc cố định: Đỏ cho Lãi suất (thường là chi phí lớn hơn), Vàng cho Phí
    colors = ['#F44336', '#FFC107']
    
    # Thiết lập nền trắng cho Matplotlib và kích thước
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(7, 3.8), facecolor='white') 

    bars = ax.bar(data['Thành phần'], data['Giá trị'], color=colors)
    
    # Styling và Labels
    ax.set_title(f'2. Cơ cấu Tổng Chi phí: {total_costs:,.2f} USD', fontsize=14, color='black')
    ax.set_ylabel('Giá trị (USD)', fontsize=12, color='black')
    ax.set_xlabel('Thành phần Chi phí', fontsize=12, color='black')
    ax.tick_params(axis='x', colors='black')
    ax.tick_params(axis='y', colors='black')
    ax.set_facecolor('white')

    # Grid và Border
    ax.grid(axis='y', linestyle='--', alpha=0.7, color='lightgray')
    for spine in ax.spines.values():
        spine.set_edgecolor('black')

    # Thêm nhãn giá trị
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, height + (total_costs * 0.05), 
                f'{height:,.0f} USD', ha='center', fontsize=10, color='black') 

    plt.ylim(0, max(data['Giá trị']) * 1.25)
    plt.tight_layout()
    return fig

# --- 4. Biểu đồ Phân tích Độ nhạy Kỳ hạn (Matplotlib) ---
def create_tenor_sensitivity_chart(advance_amount, advance_rate, service_fee_rate, discount_rate_annual):
    tenor_scenarios = [3, 6, 9, 12]
    net_cash_data = []
    
    for tenor in tenor_scenarios:
        total_ar = advance_amount / advance_rate
        service_fee = total_ar * service_fee_rate
        
        discount_interest = advance_amount * discount_rate_annual * (tenor / 12.0)
        net_cash = advance_amount - (service_fee + discount_interest)
        
        net_cash_data.append(net_cash)
        
    df = pd.DataFrame({
        'Kỳ hạn (Tháng)': [f"{t} tháng" for t in tenor_scenarios],
        'Net Cash': net_cash_data
    })

    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(7, 3.8), facecolor='white') 
    
    bars = ax.bar(df['Kỳ hạn (Tháng)'], df['Net Cash'], color='#2196F3') 
    
    ax.set_title('3. Độ nhạy: Net Cash theo Kỳ hạn', fontsize=14, color='black')
    ax.set_ylabel('Net Cash (USD)', fontsize=12, color='black')
    ax.set_xlabel('Kỳ hạn bao thanh toán', fontsize=12, color='black')
    ax.tick_params(axis='x', colors='black')
    ax.tick_params(axis='y', colors='black')
    ax.set_facecolor('white')

    for spine in ax.spines.values():
        spine.set_edgecolor('black')

    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + (max(net_cash_data) * 0.02),
                f'{yval:,.0f}', ha='center', fontsize=10, color='black')

    ax.grid(axis='y', linestyle='--', alpha=0.7, color='lightgray')
    plt.tight_layout()
    return fig


# --- 5. Xây dựng Giao diện Streamlit ---
st.set_page_config(page_title="Mô Hình Chi Phí Bao Thanh Toán", layout="wide")
st.title("💰 Công Cụ Mô Phỏng Chi Phí Bao Thanh Toán (Factoring)")
st.markdown("---")

st.sidebar.header("Tham Số Đầu Vào")

advance_amount = st.sidebar.number_input("Khoản tiền Ứng trước (USD)", value=200000.00, min_value=1.0, step=1000.0, format="%.2f")
advance_rate_percent = st.sidebar.slider("Tỷ lệ Ứng trước (%)", value=60, min_value=50, max_value=95, step=5)
service_fee_rate_percent = st.sidebar.slider("Hoa hồng phí Dịch vụ (%)", value=5.0, min_value=0.5, max_value=5.0, step=0.1, format="%.1f")
discount_rate_percent = st.sidebar.slider("Lãi suất Chiết khấu/Năm (%)", value=12.4, min_value=5.0, max_value=25.0, step=0.1, format="%.1f")
tenor_months = st.sidebar.slider("Kỳ hạn Bao thanh toán (Tháng)", value=12, min_value=1, max_value=12, step=1)

advance_rate = advance_rate_percent / 100.0
service_fee_rate = service_fee_rate_percent / 100.0
discount_rate_annual = discount_rate_percent / 100.0

# --- 6. Hiển thị Kết quả và Biểu đồ ---
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
        
        # --- HIỂN THỊ CÁC CỘT CHỈ SỐ CHÍNH ---
        col_main_1, col_main_2, col_main_3 = st.columns(3)
        col_main_1.metric("Trị giá Nợ phải thu (Total AR)", f"{results['Trị giá Nợ phải thu (Total AR)']:,.2f} USD")
        col_main_2.metric("Tổng Chi phí (Lãi + Phí)", f"{results['Tổng chi phí (Total Cost)']:,.2f} USD")
        col_main_3.metric("Số tiền Thực nhận (Net Cash)", f"{results['Số tiền Thực nhận (Net Cash Received)']:,.2f} USD")

        st.markdown("---")

        # --- HIỂN THỊ CÁC CỘT CHỈ SỐ MỚI ---
        st.subheader("Chỉ số Hiệu quả & Chi phí")
        col_new_1, col_new_2, col_new_3 = st.columns(3)
        col_new_1.metric("Tỷ suất Lợi nhuận ròng (%)", f"{results['Tỷ suất Lợi nhuận ròng (%)']:,.2f} %")
        col_new_2.metric("Tỷ suất Chi phí Hiệu quả/Năm (%)", f"{results['Tỷ suất Chi phí Hiệu quả/Năm (%)']:,.2f} %")
        col_new_3.metric("Phần trăm Chi phí là Lãi suất (%)", f"{results['Phần trăm Chi phí là Lãi suất (%)']:,.2f} %")


        st.markdown("---")
        
        # KHU VỰC BIỂU ĐỒ 1: Cơ cấu AR
        st.subheader("1. Cơ Cấu Khoản Phải Thu (Phân bổ tài sản)")
        fig_main = create_main_visualization(results)
        st.pyplot(fig_main)
        
        st.markdown("---")

        # KHU VỰC BIỂU ĐỒ 2: Dòng tiền (So sánh)
        st.subheader("2. So sánh Dòng tiền và Chi phí Giảm trừ")
        fig_waterfall = create_cost_composition_chart(results)
        st.pyplot(fig_cost_comp)
        
        st.markdown("---")

        # KHU VỰC BIỂU ĐỒ 3: Độ nhạy Kỳ hạn
        st.subheader("3. Phân Tích Độ Nhạy Lợi nhuận theo Kỳ hạn")
        fig_tenor = create_tenor_sensitivity_chart(
            advance_amount, 
            advance_rate, 
            service_fee_rate, 
            discount_rate_annual
        )
        st.pyplot(fig_tenor)



