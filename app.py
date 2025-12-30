import streamlit as st
import os
import time

# --- 1. CẤU HÌNH TRANG (Phải đặt đầu tiên) ---
st.set_page_config(
    page_title="TITAN VISION ENGINE v4.0",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS TÙY CHỈNH (Giao diện Dark Mode Hacker) ---
st.markdown("""
<style>
    /* Chỉnh màu nền chính nếu muốn tối hơn nữa */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Tùy chỉnh nút bấm */
    .stButton > button {
        width: 100%;
        border-radius: 5px;
        font-weight: bold;
        height: 3em;
    }
    
    /* Ẩn menu mặc định của Streamlit cho gọn */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Style cho khung kết quả */
    .result-box {
        padding: 20px;
        border: 1px solid #444;
        border-radius: 10px;
        background-color: #1a1c24;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. SIDEBAR: TRUNG TÂM ĐIỀU KHIỂN ---
with st.sidebar:
    st.header("⚙ Trung tâm điều khiển")
    
    # --- A. MENU CHẾ ĐỘ ---
    selected_mode = st.radio(
        "Chế độ vận hành:", 
        ["🔴 Auto-Router", "⚪ Vision Analysis", "⚪ Code Audit"],
        index=0
    )
    
    st.markdown("---") # Đường kẻ phân cách

    # --- B. QUẢN LÝ API KEY (TỰ ĐỘNG) ---
    api_key = None
    
    # 1. Ưu tiên lấy từ secrets.toml (Best Practice)
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("🟢 System Online (Secured)")
    
    # 2. Nếu không có secrets, dùng nhập tay (Session State)
    else:
        if "api_key" not in st.session_state:
            st.session_state.api_key = ""

        if not st.session_state.api_key:
            st.warning("⚠️ Chưa kết nối Core")
            user_input = st.text_input(
                "Nhập Google API Key:", 
                type="password",
                placeholder="Paste Key & Enter...",
                help="Key sẽ được lưu tạm trong phiên làm việc này."
            )
            if user_input:
                st.session_state.api_key = user_input
                st.rerun() # Load lại để nhận key
        else:
            api_key = st.session_state.api_key
            # Giao diện khi đã có key nhập tay
            col_k1, col_k2 = st.columns([5, 1])
            with col_k1:
                st.info("🟢 Ready to serve")
            with col_k2:
                if st.button("🔄", help="Reset Key"):
                    st.session_state.api_key = ""
                    st.rerun()
            st.caption("💡 Tip: Dùng file `secrets.toml` để không phải nhập lại.")

    # Thiết lập biến môi trường nếu có key
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key

    # --- C. DEBUG (ẨN) ---
    st.markdown("---")
    with st.expander("🛠 Debug thông tin Model", expanded=False):
        st.write("Engine Status: **Active**")
        st.json({
            "detected_model": "gemini-1.5-pro-latest",
            "latency": "120ms",
            "token_usage": "0 (Waiting)",
            "mode": selected_mode
        })

# --- 4. GIAO DIỆN CHÍNH (MAIN AREA) ---

# Tiêu đề lớn
st.title("👁 TITAN VISION ENGINE v4.0")
st.caption("Strategic Partner Edition - Auto Detect Model")

# Layout 2 cột: Input (Trái) - Output (Phải)
col_input, col_output = st.columns([1, 1], gap="large")

with col_input:
    st.subheader("📥 Dữ liệu đầu vào")
    
    # Ô nhập Text
    user_prompt = st.text_area(
        "Nhập ý tưởng / Code / Câu hỏi:",
        height=200,
        placeholder="Ví dụ: Phân tích bức ảnh này và trích xuất code HTML..."
    )
    
    # Ô Upload Ảnh
    uploaded_file = st.file_uploader(
        "Tải ảnh phân tích (JPG/PNG):", 
        type=["jpg", "png", "jpeg"]
    )
    
    # Nút Action
    run_btn = st.button("🚀 KÍCH HOẠT TITAN", type="primary")

# --- 5. XỬ LÝ LOGIC ---
with col_output:
    st.subheader("💎 Kết quả phân tích")

    if run_btn:
        if not api_key:
            st.error("⛔ Vui lòng cung cấp API Key để khởi động hệ thống.")
        elif not user_prompt and not uploaded_file:
            st.warning("⚠️ Vui lòng nhập nội dung hoặc tải ảnh lên.")
        else:
            # Giao diện Loading giả lập (Thay bằng code gọi AI thật của bạn sau này)
            with st.spinner("Đang kết nối Neural Network..."):
                time.sleep(1.5) # Giả lập độ trễ xử lý
                
                # --- VÙNG NÀY ĐỂ CODE GỌI GEMINI CỦA BẠN ---
                # response = model.generate_content(...)
                # result_text = response.text
                
                # Demo kết quả giả định:
                st.success(f"✅ Đã xử lý xong bằng model: gemini-1.5-flash")
                
                st.markdown("""
                ### 1. THE VERDICT
                **TITAN v4.0** xác nhận hệ thống hoạt động ổn định.
                
                * **Input:** Đã nhận dữ liệu.
                * **Mode:** {}
                * **Status:** Sẵn sàng tích hợp logic xử lý thực tế.
                
                ### 2. DEEP DIVE
                Đây là khu vực hiển thị kết quả chi tiết từ API. Bạn hãy thay thế phần này bằng biến `response.text` trong code thực tế.
                """.format(selected_mode))
                
                # Hiển thị ảnh nếu có upload
                if uploaded_file:
                    st.image(uploaded_file, caption="Source Image processed", use_column_width=True)

    else:
        # Placeholder khi chưa chạy
        st.info("👋 Waiting for data stream...")
