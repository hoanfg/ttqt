import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- 1. Hàm tính toán logic (Giữ nguyên) ---
def calculate_factoring_costs(advance_amount, advance_rate, discount_rate_annual, service_fee_rate, tenor_months):
    if advance_rate <= 0 or advance_rate > 1:
        return None
        
    total_ar = advance_amount / advance_rate
    service_fee = total_ar * service_fee_rate
    
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

# --- 2. Hàm trực quan hóa chính (Cơ cấu AR - Biểu đồ Cột dọc) ---
def create_main_visualization(results):
    net_cash = results["Số tiền Thực nhận (Net Cash Received)"]
    total_costs = results["Tổng chi phí (Total Cost)"]
    reserve = results["Khoản Dự trữ (Reserve)"]
    total_ar = results["Trị giá Nợ phải thu (Total AR)"]
    
    # Sắp xếp theo giá trị
    data = pd.DataFrame({
        'Thành phần': ['Số tiền Thực nhận', 'Tổng Chi phí', 'Khoản Dự trữ'],
        'Giá trị (USD)': [net_cash, total_costs, reserve]
    }).sort_values(by='Giá trị (USD)', ascending=False)
    
    # Màu sắc cố định (Xanh lá, Đỏ, Vàng)
    colors = ['#4CAF50', '#F44336', '#FFC107']
    
    # Thiết lập nền trắng và kích thước
    plt.style.use('default') 
    fig, ax = plt.subplots(figsize=(9, 4.5), facecolor='white') 
    
    bars = ax.bar(data['Thành phần'], data['Giá trị (USD)'], color=colors)
    
    ax.set_title(f'Cơ cấu Trị giá Nợ phải thu: {total_ar:,.2f} USD', fontsize=14, color='black')
    ax.set_ylabel('Giá trị (USD)', fontsize=12, color='black') 
    ax.set_xlabel('') # Loại bỏ nhãn trục X không cần thiết
    ax.tick_params(axis='x', colors='black', rotation=15)
    ax.tick_params(axis='y', colors='black')
    ax.set_facecolor('white')
    
    # Grid và Border
    ax.grid(axis='y', linestyle='--', alpha=0.7, color='lightgray')
    for spine in ax.spines.values():
        spine.set_edgecolor('black')

    # Thêm nhãn giá trị trên đỉnh cột
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + (total_ar * 0.005), 
                f'{height:,.2f} USD', ha='center', fontsize=10, color='black')

    plt.ylim(0, max(data['Giá trị (USD)']) * 1.15) 
    plt.tight_layout()
    return fig

# --- 3. Biểu đồ Thay thế Waterfall (Sử dụng Stacked Bar với Plotly) ---
def create_waterfall_chart(results):
    advance_amount = results["Khoản tiền Ứng trước (Advance Amount)"]
    service_fee = results["Hoa hồng phí (Service Fee)"]
    discount_interest = results["Lãi suất chiết khấu (Discount Interest)"]
    net_cash = results["Số tiền Thực nhận (Net Cash Received)"]

    # Dữ liệu cho biểu đồ xếp chồng (Stacked Bar Chart)
    # Chúng ta sẽ hiển thị 3 cột: Khoản ứng trước, Chi phí, và Net Cash
    
    data = {
        'Hạng mục': ['Khoản Ứng trước (Start)', 'Chi phí (Total Cost)', 'Net Cash (End)'],
        'Giá trị': [advance_amount, results["Tổng chi phí (Total Cost)"], net_cash]
    }
    df = pd.DataFrame(data)

    # Để trực quan hóa 3 cột chính, ta dùng biểu đồ cột đơn (Single Bar)
    # Để thể hiện mối quan hệ trừ bớt (tương tự Waterfall) ta dùng biểu đồ xếp chồng TƯƠNG ĐỐI
    
    # Chuẩn bị dữ liệu cho biểu đồ hiển thị chi phí giảm trừ từ Khoản ứng trước (Net Cash)
    
    categories = ['Phần chi phí', 'Phần thực nhận']
    
    # Cấu trúc: 
    # Cột 1: Chi phí + Net Cash = Advance (Cột gốc)
    # Cột 2: Net Cash (Cột kết quả)
    
    plot_data = pd.DataFrame({
        'Thành phần': ['Net Cash', 'Chi phí'],
        'Khởi điểm ứng trước': [net_cash, results["Tổng chi phí (Total Cost)"]],
        'Kết quả': [net_cash, 0] # Chi phí là 0 ở cột Net Cash
    }).set_index('Thành phần')


    fig = go.Figure(data=[
        # Lớp dưới: Net Cash (Màu xanh lá cây)
        go.Bar(
            name='Số tiền Thực nhận',
            x=['Khởi điểm ứng trước', 'Kết quả'],
            y=[net_cash, net_cash],
            marker_color='#4CAF50',
            text=[f'{net_cash:,.0f}', f'{net_cash:,.0f}'],
            textposition='inside',
            hoverinfo='name+y'
        ),
        # Lớp trên: Chi phí (Màu đỏ) - Chỉ xuất hiện ở cột Khởi điểm
        go.Bar(
            name='Tổng Chi phí (Giảm trừ)',
            x=['Khởi điểm ứng trước', 'Kết quả'],
            y=[results["Tổng chi phí (Total Cost)"], 0],
            marker_color='#F44336',
            text=[f'-{results["Tổng chi phí (Total Cost)"]:,.0f}', ''],
            textposition='inside',
            hoverinfo='name+y'
        )
    ])
    
    # Cập nhật layout để làm rõ mối quan hệ
    fig.update_layout(
        barmode='stack',
        title="Dòng tiền: Khoản Ứng trước và Giảm trừ Chi phí",
        height=450,
        width=800,
        showlegend = True,
        plot_bgcolor='white',      
        paper_bgcolor='white',     
        font=dict(color="black"),
        xaxis=dict(
            title='Trạng thái Dòng tiền', 
            showline=True, 
            linewidth=1, 
            linecolor='black'
        ),
        yaxis=dict(
            title='Giá trị (USD)', 
            showline=True, 
            linewidth=1, 
            linecolor='black'
        )
    )

    return fig

# --- 4. Biểu đồ Phân tích Độ nhạy Kỳ hạn (Matplotlib - FIX màu và nền) ---
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

    # Thiết lập màu nền trắng cho Matplotlib và kích thước
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(7, 3.8), facecolor='white') 
    
    bars = ax.bar(df['Kỳ hạn (Tháng)'], df['Net Cash'], color='#2196F3') 
    
    ax.set_title('Độ nhạy: Net Cash theo Kỳ hạn', fontsize=14, color='black')
    ax.set_ylabel('Net Cash (USD)', fontsize=12, color='black')
    ax.set_xlabel('Kỳ hạn bao thanh toán', fontsize=12, color='black')
    ax.tick_params(axis='x', colors='black')
    ax.tick_params(axis='y', colors='black')
    ax.set_facecolor('white')

    # Border
    for spine in ax.spines.values():
        spine.set_edgecolor('black')

    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + (max(net_cash_data) * 0.02),
                f'{yval:,.0f}', ha='center', fontsize=10, color='black')

    ax.grid(axis='y', linestyle='--', alpha=0.7, color='lightgray')
    plt.tight_layout()
    return fig


# --- 5. Xây dựng Giao diện Streamlit (Giữ nguyên) ---
st.set_page_config(page_title="Mô Hình Chi Phí Bao Thanh Toán", layout="wide")
st.title("💰 Công Cụ Mô Phỏng Chi Phí Bao Thanh Toán (Factoring)")
st.markdown("---")

st.sidebar.header("Tham Số Đầu Vào")

advance_amount = st.sidebar.number_input("Khoản tiền Ứng trước (USD)", value=120000.0, min_value=1.0, step=1000.0, format="%.2f")
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
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Trị giá Nợ phải thu (Total AR)", f"{results['Trị giá Nợ phải thu (Total AR)']:,.2f} USD")
        col2.metric("Tổng Chi phí (Lãi + Phí)", f"{results['Tổng chi phí (Total Cost)']:,.2f} USD")
        col3.metric("Số tiền Thực nhận (Net Cash)", f"{results['Số tiền Thực nhận (Net Cash Received)']:,.2f} USD")

        st.markdown("---")

        # KHU VỰC BIỂU ĐỒ 1: Cơ cấu AR
        st.subheader("1. Cơ Cấu Khoản Phải Thu (Biểu đồ Cột dọc)")
        fig_main = create_main_visualization(results)
        st.pyplot(fig_main)
        
        st.markdown("---")

        # KHU VỰC BIỂU ĐỒ 2: Dòng tiền (Waterfall - MỚI)
        st.subheader("2. Dòng tiền và Chi phí Giảm trừ (Biểu đồ Waterfall - Tương tác)")
        fig_waterfall = create_waterfall_chart(results)
        st.plotly_chart(fig_waterfall, use_container_width=True)
        
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



