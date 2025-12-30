import streamlit as st
import os
import google.generativeai as genai
from PIL import Image

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="TITAN VISION ENGINE v4.0",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS TÙY CHỈNH (Giao diện sạch) ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .stButton > button { width: 100%; border-radius: 5px; height: 3em; font-weight: bold;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Chỉnh lại cái thông báo System Online cho đẹp hơn */
    div[data-testid="stMarkdownContainer"] > div.stAlert {
        padding: 0.5rem;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. SIDEBAR: CONTROL CENTER ---
with st.sidebar:
    st.header("⚙ Trung tâm điều khiển")
    
    # Menu chọn Model (Logic thật)
     
    # CẬP NHẬT CORE ENGINE MỚI NHẤT (GEMINI 2.0)
    mode_mapping = {
        # Auto-Router dùng 2.0 Flash Exp (Nhanh và Đa phương thức chuẩn nhất hiện nay)
        "🔴 Auto-Router": "gemini-2.0-flash-exp",
        
        # Vision Analysis dùng 2.0 để nhận diện ảnh tốt hơn 1.5 Pro
        "⚪ Vision Analysis": "gemini-2.0-flash-exp",
        
        # Code Audit vẫn dùng 2.0 vì context window nó rất lớn
        "⚪ Code Audit": "gemini-2.0-flash-exp"
    }
    
    selected_mode_label = st.radio("Chế độ:", list(mode_mapping.keys()))
    selected_model_id = mode_mapping[selected_mode_label] # Lấy ID thật của model
    
    st.markdown("---")

    # --- QUẢN LÝ API KEY ---
    api_key = None
    
    # Kiểm tra secrets.toml trước
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("🟢 System Online (Secured)")
    else:
        # Nếu không có file secrets, dùng nhập tay
        if "api_key" not in st.session_state:
            st.session_state.api_key = ""
        
        if not st.session_state.api_key:
            st.warning("⚠️ Disconnected")
            user_input = st.text_input("Google API Key:", type="password")
            if user_input:
                st.session_state.api_key = user_input
                st.rerun()
        else:
            api_key = st.session_state.api_key
            st.info("🟢 Ready")
            if st.button("🔄 Reset Key"):
                st.session_state.api_key = ""
                st.rerun()

    # KẾT NỐI GEMINI (QUAN TRỌNG)
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        genai.configure(api_key=api_key)

    # --- DEBUG INFO (ẨN) ---
    st.markdown("---")
    with st.expander("🛠 Debug Model Info", expanded=False):
        st.code(f"""
Model ID: {selected_model_id}
API Status: {'Connected' if api_key else 'Missing'}
Mode: {selected_mode_label}
        """, language="yaml")

# --- 4. MAIN INTERFACE ---
st.title("👁 TITAN VISION ENGINE v4.0")
st.caption(f"Strategic Partner Edition - Running on: **{selected_model_id}**")

col_input, col_output = st.columns([1, 1], gap="medium")

with col_input:
    st.subheader("📥 Dữ liệu đầu vào")
    user_prompt = st.text_area("Nhập Prompt / Câu hỏi:", height=200, placeholder="Nhập yêu cầu của bạn...")
    uploaded_file = st.file_uploader("Tải ảnh (nếu có):", type=["jpg", "png", "jpeg"])
    
    # Hiển thị ảnh preview nhỏ nếu có upload
    image_data = None
    if uploaded_file:
        image_data = Image.open(uploaded_file)
        st.image(image_data, caption="Preview", use_column_width=True)

    run_btn = st.button("🚀 KÍCH HOẠT TITAN", type="primary")

# --- 5. XỬ LÝ LOGIC GỌI AI ---
with col_output:
    st.subheader("💎 Kết quả phân tích")
    
    if run_btn:
        if not api_key:
            st.error("⛔ Chưa có API Key!")
        elif not user_prompt and not uploaded_file:
            st.warning("⚠️ Hãy nhập nội dung để xử lý.")
        else:
            try:
                with st.spinner("Đang kết nối Neural Network..."):
                    # 1. Khởi tạo Model thật
                    model = genai.GenerativeModel(selected_model_id)
                    
                    # 2. Chuẩn bị dữ liệu gửi đi
                    input_content = []
                    if user_prompt:
                        input_content.append(user_prompt)
                    if image_data:
                        input_content.append(image_data)
                    
                    # 3. Gọi Google Gemini (Xử lý thật)
                    response = model.generate_content(input_content)
                    
                    # 4. Hiển thị kết quả thật
                    st.success("✅ Đã xử lý xong!")
                    st.markdown(response.text)
                    
            except Exception as e:
                st.error(f"❌ Lỗi hệ thống: {str(e)}")
    else:
        st.info("👋 Waiting for command...")
