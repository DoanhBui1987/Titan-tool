import streamlit as st
import os
import time
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
    div[data-testid="stExpander"] div[role="button"] p { font-size: 0.9rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 3. SIDEBAR ---
with st.sidebar:
    st.header("⚙ Trung tâm điều khiển")
    
    # --- CẤU HÌNH MODEL AN TOÀN ---
    # Sử dụng tên gốc (Alias) để tránh lỗi 404
    mode_mapping = {
        "🔴 Auto-Router": "gemini-1.5-pro",  
        "⚪ Vision Analysis": "gemini-1.5-pro",
        "⚪ Code Audit": "gemini-1.5-pro"
    }
    
    selected_mode_label = st.radio("Chế độ:", list(mode_mapping.keys()))
    selected_model_id = mode_mapping[selected_mode_label]
    
    st.markdown("---")

    # --- API KEY HANDLING ---
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
        
    # --- DEBUG: KIỂM TRA MODEL CÓ SẴN ---
    with st.expander("🛠 Kiểm tra kết nối", expanded=False):
        if st.button("Check Models"):
            try:
                available_models = [m.name for m in genai.list_models()]
                st.write(available_models)
            except Exception as e:
                st.error(f"Lỗi kết nối: {e}")

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

# --- 5. XỬ LÝ LOGIC (CHỐNG LỖI) ---
with col_output:
    st.subheader("💎 Kết quả phân tích")
    
    if run_btn:
        if not api_key:
            st.error("⛔ Chưa có API Key!")
        else:
            status_box = st.empty()
            try:
                # 1. THỬ CHẠY MODEL 1.5 PRO
                with st.spinner("🚀 Đang xử lý (Mode: Pro)..."):
                    model = genai.GenerativeModel(
                        model_name=selected_model_id, 
                        tools='google_search_retrieval'
                    )
                    
                    input_content = []
                    if user_prompt: input_content.append(user_prompt)
                    if image_data: input_content.append(image_data)
                    
                    response = model.generate_content(input_content)
                    
                    status_box.success(f"✅ Xử lý thành công! ({selected_model_id})")
                    st.markdown(response.text)
                    
                    # Hiển thị nguồn Search
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
                # 2. NẾU 1.5 PRO LỖI -> TỰ ĐỘNG CHUYỂN SANG FLASH (CỨU CÁNH)
                error_msg = str(e)
                if "404" in error_msg or "not found" in error_msg:
                    status_box.warning(f"⚠️ Model Pro
