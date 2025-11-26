import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math 

# --- 1. HÀM TÍNH TOÁN CƠ BẢN (FACTURING) ---
def calculate_factoring_costs(advance_amount, advance_rate, discount_rate_annual, service_fee_rate, tenor_months):
    """Tính toán chi phí và số tiền thực nhận của giao dịch Factoring."""
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
    if total_costs > 0 and net_cash_received > 0:
        net_profit_rate = (net_cash_received / total_ar) * 100 
        annualized_cost_rate = (total_costs / net_cash_received) * (360 / tenor_days) * 100
        interest_cost_ratio = (discount_interest / total_costs) * 100
        service_fee_ratio = (service_fee / total_costs) * 100
    else:
        net_profit_rate = annualized_cost_rate = interest_cost_ratio = service_fee_ratio = 0
    
    results = {
        "Trị giá Nợ phải thu (Total AR)": total_ar,
        "Khoản tiền Ứng trước (Advance Amount)": advance_amount,
        "Khoản Dự trữ (Reserve)": reserve,
        "Hoa hồng phí (Service Fee)": service_fee,
        "Lãi suất chiết khấu (Interest Cost)": discount_interest,
        "Tổng chi phí (Total Cost)": total_costs,
        "Số tiền Thực nhận (Net Cash Received)": net_cash_received,
        "Tỷ suất Lợi nhuận ròng (%)": net_profit_rate,
        "Tỷ suất Chi phí Hiệu quả/Năm (%)": annualized_cost_rate,
        "Phần trăm Chi phí là Lãi suất (%)": interest_cost_ratio,
        "Phần trăm Chi phí là Hoa hồng (%)": service_fee_ratio,
    }
    
    return results

# --- 2. HÀM TÍNH TOÁN L/C (ĐỂ SO SÁNH) ---
def calculate_lc_cost(total_ar, lc_fee_rate_percent, margin_rate_percent, cost_of_capital_annual, tenor_months):
    """Tính toán Tổng chi phí của L/C (Phí + Chi phí cơ hội vốn ký quỹ)."""
    
    # L/C Fee: Tính trên Total AR
    lc_fee = total_ar * (lc_fee_rate_percent / 100)
    
    # Chi phí Cơ hội Vốn Ký quỹ (Giả định thời gian ký quỹ = Kỳ hạn Factoring)
    margin_amount = total_ar * (margin_rate_percent / 100)
    
    # Chi phí cơ hội (Opportunity Cost)
    cost_of_capital_annual = cost_of_capital_annual / 100
    opportunity_cost = margin_amount * cost_of_capital_annual * (tenor_months / 12.0)
    
    total_lc_cost = lc_fee + opportunity_cost
    
    return total_lc_cost

# --- 3. CÁC HÀM TRỰC QUAN HÓA MATPLOTLIB ---

# Biểu đồ 1: Cơ cấu Khoản Phải Thu (Phân bổ Tài sản)
def create_main_visualization(results):
    net_cash = results["Số tiền Thực nhận (Net Cash Received)"]
    total_costs = results["Tổng chi phí (Total Cost)"]
    reserve = results["Khoản Dự trữ (Reserve)"]
    total_ar = results["Trị giá Nợ phải thu (Total AR)"]
    
    data = pd.DataFrame({
        'Thành phần': ['Số tiền Thực nhận', 'Khoản Dự trữ', 'Tổng Chi phí'],
        'Giá trị (USD)': [net_cash, reserve, total_costs]
    }).sort_values(by='Giá trị (USD)', ascending=False)
    
    colors = ['#4CAF50', '#FFC107', '#F44336'] 
    
    plt.style.use('default') 
    fig, ax = plt.subplots(figsize=(9, 4.5), facecolor='white') 
    
    bars = ax.bar(data['Thành phần'], data['Giá trị (USD)'], color=colors)
    
    ax.set_title(f'1. Cơ cấu Trị giá Nợ phải thu: {total_ar:,.2f} USD', fontsize=14, color='black')
    ax.set_ylabel('Giá trị (USD)', fontsize=12, color='black') 
    ax.set_xlabel('')
    ax.tick_params(axis='x', colors='black', rotation=0) # Chữ nằm ngang
    ax.tick_params(axis='y', colors='black')
    ax.set_facecolor('white')
    
    ax.grid(axis='y', linestyle='--', alpha=0.7, color='lightgray')
    for spine in ax.spines.values():
        spine.set_edgecolor('black')

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + (total_ar * 0.005), 
                f'{height:,.0f} USD', ha='center', fontsize=10, color='black')
    
    plt.ylim(0, max(data['Giá trị (USD)']) * 1.15) 
    plt.tight_layout()
    return fig

# Biểu đồ 2: Cơ cấu Tổng Chi phí (Phân tích Lãi suất vs. Phí)
def create_cost_composition_chart(results):
    service_fee = results["Hoa hồng phí (Service Fee)"]
    discount_interest = results["Lãi suất chiết khấu (Interest Cost)"]
    total_costs = results["Tổng chi phí (Total Cost)"]

    if total_costs <= 0:
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.text(0.5, 0.5, "Không có chi phí để phân tích.", ha='center', va='center', fontsize=12)
        ax.axis('off')
        return fig
    
    # Biểu đồ Tròn
    labels = [f'Lãi suất ({results["Phần trăm Chi phí là Lãi suất (%)"]:,.1f}%)', 
              f'Hoa hồng phí ({results["Phần trăm Chi phí là Hoa hồng (%)"]:,.1f}%)']
    values = [discount_interest, service_fee]
    
    def func_pct(pct, allvalues):
        absolute = pct / 100. * allvalues
        return f'{absolute:,.0f} USD'

    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(6, 6), facecolor='white') 

    ax.pie(
        values, 
        labels=labels, 
        autopct=lambda pct: func_pct(pct, total_costs),
        colors=['#F44336', '#FFC107'],
        startangle=90,
        wedgeprops={'edgecolor': 'black'}
    )
    
    ax.set_title(f'2. Cơ cấu Tổng Chi phí: {total_costs:,.2f} USD', fontsize=14, color='black')
    ax.axis('equal') 
    plt.tight_layout()
    return fig

# Biểu đồ 3: Độ nhạy Net Cash theo Kỳ hạn
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

# --- 5. CÁC HÀM SO SÁNH CUỐI CÙNG ---

def create_cost_comparison_chart(factoring_cost, lc_cost):
    """Tạo biểu đồ so sánh chi phí Factoring vs. L/C."""
    data = pd.DataFrame({
        'Phương thức': ['Factoring (Total Cost)', 'L/C (Total Cost)'],
        'Chi phí': [factoring_cost, lc_cost]
    })
    
    # Biểu đồ cột so sánh
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(8, 4), facecolor='white') 
    
    bars = ax.bar(data['Phương thức'], data['Chi phí'], color=['#F44336', '#2196F3']) 
    
    ax.set_title('4. So sánh Tổng Chi phí: Factoring vs. L/C', fontsize=14, color='black')
    ax.set_ylabel('Chi phí (USD)', fontsize=12, color='black')
    ax.set_xlabel('Phương thức Bảo lãnh/Tài trợ', fontsize=12, color='black')
    ax.tick_params(axis='x', colors='black')
    ax.tick_params(axis='y', colors='black')
    ax.set_facecolor('white')
    
    ax.grid(axis='y', linestyle='--', alpha=0.7, color='lightgray')
    for spine in ax.spines.values():
        spine.set_edgecolor('black')

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, height + (max(data['Chi phí']) * 0.05),
                f'{height:,.0f} USD', ha='center', fontsize=10, color='black')
    
    plt.tight_layout()
    return fig


# --- 6. XÂY DỰNG GIAO DIỆN STREAMLIT ---

st.set_page_config(page_title="Mô Hình Chi Phí Bao Thanh Toán", layout="wide")
st.title("💰 Công Cụ Mô Phỏng Chi Phí Bao Thanh Toán (Factoring)")
st.markdown("---")

# --- INPUTS CHÍNH (Sidebar) ---
st.sidebar.header("Tham Số Đầu Vào Factoring")

advance_amount = st.sidebar.number_input("Khoản tiền Ứng trước (USD)", value=200000.00, min_value=1.0, step=1000.0, format="%.2f")
advance_rate_percent = st.sidebar.slider("Tỷ lệ Ứng trước (%)", value=60, min_value=50, max_value=95, step=5)
service_fee_rate_percent = st.sidebar.slider("Hoa hồng phí Dịch vụ (%)", value=2.0, min_value=0.5, max_value=5.0, step=0.1, format="%.1f")
discount_rate_percent = st.sidebar.slider("Lãi suất Chiết khấu/Năm (%)", value=12.4, min_value=5.0, max_value=25.0, step=0.1, format="%.1f")
tenor_months = st.sidebar.slider("Kỳ hạn Bao thanh toán (Tháng)", value=12, min_value=1, max_value=12, step=1)

# --- INPUTS CHO L/C ---
st.sidebar.markdown("---")
st.sidebar.header("Tham Số L/C & So sánh")

lc_fee_rate_percent = st.sidebar.slider("Phí Mở L/C (%)", value=0.15, min_value=0.05, max_value=1.0, step=0.05)
margin_rate_percent = st.sidebar.slider("Tỷ lệ Ký quỹ L/C (%)", value=20, min_value=0, max_value=100, step=5)
cost_of_capital_annual = st.sidebar.number_input("Giá vốn Ký quỹ (Annual %)", value=8.0, min_value=1.0, max_value=30.0, step=0.5)


# --- CHUYỂN ĐỔI TỶ LỆ ---
advance_rate = advance_rate_percent / 100.0
service_fee_rate = service_fee_rate_percent / 100.0
discount_rate_annual = discount_rate_percent / 100.0
lc_fee_rate = lc_fee_rate_percent / 100.0
margin_rate = margin_rate_percent / 100.0


# --- KHỐI THỰC THI CHÍNH ---
if advance_amount and advance_rate:
    results = calculate_factoring_costs(
        advance_amount,
        advance_rate,
        discount_rate_annual,
        service_fee_rate,
        tenor_months
    )

    if results:
        total_ar_val = results["Trị giá Nợ phải thu (Total AR)"]
        factoring_cost = results["Tổng chi phí (Total Cost)"]
        
        # Tính chi phí L/C để so sánh
        lc_cost = calculate_lc_cost(
            total_ar_val, 
            lc_fee_rate_percent, 
            margin_rate_percent, 
            cost_of_capital_annual,
            tenor_months # Sử dụng cùng kỳ hạn để so sánh
        )
        
        st.header("Kết Quả Phân Tích Tài Chính")
        
        # HIỂN THỊ CHỈ SỐ CƠ BẢN
        col1, col2, col3 = st.columns(3)
        col1.metric("Trị giá Nợ phải thu (Total AR)", f"{total_ar_val:,.2f} USD")
        col2.metric("Tổng Chi phí Factoring", f"{factoring_cost:,.2f} USD")
        col3.metric("Số tiền Thực nhận (Net Cash)", f"{results['Số tiền Thực nhận (Net Cash Received)']:,.2f} USD")

        st.markdown("---")

        # HIỂN THỊ CHỈ SỐ HIỆU QUẢ
        st.subheader("Chỉ số Hiệu quả & Chi phí")
        col_new_1, col_new_2, col_new_3 = st.columns(3)
        col_new_1.metric("Tỷ suất Lợi nhuận ròng (%)", f"{results['Tỷ suất Lợi nhuận ròng (%)']:,.2f} %")
        col_new_2.metric("Tỷ suất Chi phí Hiệu quả/Năm (%)", f"{results['Tỷ suất Chi phí Hiệu quả/Năm (%)']:,.2f} %")
        col_new_3.metric("Phần trăm Chi phí là Lãi suất (%)", f"{results['Phần trăm Chi phí là Lãi suất (%)']:,.2f} %")

        st.markdown("---")
        
        # --- KHU VỰC BIỂU ĐỒ ---
        
        # 1. Cơ cấu AR
        st.subheader("1. Cơ Cấu Khoản Phải Thu (Phân bổ tài sản)")
        fig_main = create_main_visualization(results)
        st.pyplot(fig_main)
        
        st.markdown("---")

        # 2. Cơ cấu Tổng Chi phí (Biểu đồ Tròn)
        st.subheader("2. Cơ cấu Tổng Chi phí (Phân tích Lãi suất vs. Phí)")
        fig_cost_comp = create_cost_composition_chart(results)
        st.pyplot(fig_cost_comp)
        
        st.markdown("---")

        # 3. Độ nhạy Kỳ hạn
        st.subheader("3. Phân Tích Độ Nhạy Lợi nhuận theo Kỳ hạn")
        fig_tenor = create_tenor_sensitivity_chart(
            advance_amount, 
            advance_rate, 
            service_fee_rate, 
            discount_rate_annual
        )
        st.pyplot(fig_tenor)
        
        st.markdown("---")

        # 4. So sánh Tổng Chi phí (Biểu đồ MỚI)
        st.subheader("4. So sánh Chi phí: Factoring vs. L/C (Bảo lãnh)")
        fig_comparison = create_cost_comparison_chart(factoring_cost, lc_cost)
        st.pyplot(fig_comparison)
