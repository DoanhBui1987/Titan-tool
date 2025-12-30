import streamlit as st
import os
import time  # Đã thêm thư viện time để sửa lỗi NameError
import google.generativeai as genai
from PIL import Image

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="TITAN VISION ENGINE v4.0",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS TÙY CHỈNH ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .stButton > button { width: 100%; border-radius: 5px; height: 3em; font-weight: bold;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. SIDEBAR ---
with st.sidebar:
    st.header("⚙ Trung tâm điều khiển")
    
    # CHỌN MODEL: Đã chuyển hết về bản 1.5 Pro (Bản xịn cho người có Key trả phí)
    # Model này hỗ trợ Search, Code cực mạnh và KHÔNG BỊ GIỚI HẠN
    mode_mapping = {
        "🔴 Auto-Router": "gemini-1.5-pro-002", 
        "⚪ Vision Analysis": "gemini-1.5-pro-002",
        "⚪ Code Audit": "gemini-1.5-pro-002"
    }
    
    selected_mode_label = st.radio("Chế độ:", list(mode_mapping.keys()))
    selected_model_id = mode_mapping[selected_mode_label]
    
    st.markdown("---")

    # API KEY
    api_key = None
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("🟢 System Online (Secured)")
    else:
        if "api_key" not in st.session_state:
            st.session_state.api_key = ""
        if not st.session_state.api_key:
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

    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        genai.configure(api_key=api_key)

# --- 4. GIAO DIỆN CHÍNH ---
st.title("👁 TITAN VISION ENGINE v4.0")
st.caption(f"Strategic Partner Edition - Core: **{selected_model_id}**")

col_input, col_output = st.columns([1, 1], gap="medium")

with col_input:
    st.subheader("📥 Dữ liệu đầu vào")
    user_prompt = st.text_area("Nhập Prompt / Câu hỏi:", height=200)
    uploaded_file = st.file_uploader("Tải ảnh (nếu có):", type=["jpg", "png", "jpeg"])
    
    image_data = None
    if uploaded_file:
        image_data = Image.open(uploaded_file)
        st.image(image_data, caption="Preview", use_column_width=True)

    run_btn = st.button("🚀 KÍCH HOẠT TITAN", type="primary")

# --- 5. XỬ LÝ LOGIC (Đã tối ưu cho Key Trả Phí) ---
with col_output:
    st.subheader("💎 Kết quả phân tích")
    
    if run_btn:
        if not api_key:
            st.error("⛔ Chưa có API Key!")
        else:
            try:
                # Dùng Spinner thay vì code fallback phức tạp vì 1.5 Pro rất khó chết
                with st.spinner("🚀 Đang xử lý tốc độ cao (Paid Tier)..."):
                    
                    # Cấu hình Model 1.5 Pro (Bản ổn định nhất)
                    model = genai.GenerativeModel(
                        model_name=selected_model_id, 
                        tools='google_search_retrieval' # Bật tính năng Search
                    )
                    
                    input_content = []
                    if user_prompt: input_content.append(user_prompt)
                    if image_data: input_content.append(image_data)
                    
                    # Gọi API
                    response = model.generate_content(input_content)
                    
                    st.success("✅ Đã xử lý xong!")
                    st.markdown(response.text)
                    
                    # Hiển thị nguồn Search (nếu có)
                    try:
                        if response.candidates[0].grounding_metadata.search_entry_point:
                            st.markdown("---")
                            st.caption("🌐 Nguồn dữ liệu:")
                            for chunk in response.candidates[0].grounding_metadata.grounding_chunks:
                                if chunk.web:
                                    st.markdown(f"- [{chunk.web.title}]({chunk.web.uri})")
                    except:
                        pass

            except Exception as e:
                # Nếu vẫn lỗi thì in ra chi tiết để sửa
                st.error(f"❌ Lỗi: {str(e)}")
