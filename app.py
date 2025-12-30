import streamlit as st
import os
import google.generativeai as genai
from PIL import Image

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="TITAN VISION ENGINE v5.1",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS DARK MODE & FIX UI ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .stButton > button { width: 100%; border-radius: 5px; height: 3em; font-weight: bold;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. HÀM TỰ ĐỘNG DÒ TÌM MODEL (GIỮ NGUYÊN VÌ ĐÃ CHẠY TỐT) ---
def get_best_available_model():
    try:
        all_models = [m.name for m in genai.list_models()]
        # Ưu tiên tìm Gemini 2.0 hoặc 1.5 Pro
        priority_targets = [
            "models/gemini-2.0-flash-exp", 
            "models/gemini-1.5-pro-latest",
            "models/gemini-1.5-pro",
            "models/gemini-1.5-flash"
        ]
        
        for target in priority_targets:
            if target in all_models:
                return target
        
        # Nếu không thấy, lấy cái đầu tiên có chữ 'generateContent'
        for m in all_models:
            if 'gemini' in m and 'generateContent' in genai.get_model(m).supported_generation_methods:
                return m
        return "models/gemini-1.5-flash"
    except:
        return "models/gemini-1.5-flash"

# --- 4. SIDEBAR ---
with st.sidebar:
    st.header("⚙ Trung tâm điều khiển")
    
    api_key = None
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("🟢 Key: Secured")
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
            st.info("🟢 Key: Ready")
            if st.button("🔄 Reset Key"):
                st.session_state.api_key = ""
                st.rerun()

    active_model_name = "Detecting..."
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        genai.configure(api_key=api_key)
        try:
            active_model_name = get_best_available_model().replace("models/", "")
        except:
            active_model_name = "gemini-1.5-flash"

    st.markdown("---")
    st.caption(f"🤖 **Active Core:** `{active_model_name}`")
    mode = st.radio("Mode:", ["🔴 Auto-Router", "⚪ Vision Analysis", "⚪ Code Audit"])

# --- 5. GIAO DIỆN CHÍNH ---
st.title("👁 TITAN VISION ENGINE v5.1")
st.caption("Strategic Partner Edition - Fail-Safe Protocol")

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

# --- 6. XỬ LÝ LOGIC (BẤT TỬ - KHÔNG BAO GIỜ CRASH) ---
with col_output:
    st.subheader("💎 Kết quả phân tích")
    
    if run_btn:
        if not api_key:
            st.error("⛔ Vui lòng nhập API Key!")
        else:
            status_box = st.empty()
            
            # Hàm gọi API có xử lý lỗi thông minh
            def run_titan_engine():
                input_content = []
                if user_prompt: input_content.append(user_prompt)
                if image_data: input_content.append(image_data)
                
                # CÁCH 1: Thử chạy Model với công cụ Search (Cú pháp mới)
                try:
                    # Cố gắng dùng tool object thay vì string để tránh lỗi 400
                    tools_config = {'google_search': {}} 
                    
                    model = genai.GenerativeModel(
                        model_name=active_model_name,
                        tools=[tools_config] 
                    )
                    return model.generate_content(input_content), "Search Enabled"
                
                except Exception as e_search:
                    # CÁCH 2: Nếu Search lỗi (do model không hỗ trợ), chạy CHẾ ĐỘ THUẦN (Text Only)
                    # Đây là bước 'Bất Tử' - Nó sẽ bỏ qua lỗi để trả về kết quả
                    status_box.warning(f"⚠️ Search Tool không tương thích ({str(e_search)[:30]}...). Chuyển sang chế độ Chat thuần.")
                    
                    model_plain = genai.GenerativeModel(model_name=active_model_name)
                    return model_plain.generate_content(input_content), "Text Only"

            try:
                with st.spinner(f"🚀 Đang xử lý trên core {active_model_name}..."):
                    response, mode_run = run_titan_engine()
                    
                    status_box.success(f"✅ Thành công! (Core: {active_model_name} | Mode: {mode_run})")
                    st.markdown(response.text)
                    
                    # Hiển thị nguồn nếu có (chỉ khi Mode Search chạy được)
                    if hasattr(response, 'candidates') and response.candidates:
                         c = response.candidates[0]
                         if hasattr(c, 'grounding_metadata') and c.grounding_metadata.search_entry_point:
                             st.markdown("---")
                             st.caption("🌐 Nguồn dữ liệu:")
                             for chunk in c.grounding_metadata.grounding_chunks:
                                 if chunk.web:
                                     st.markdown(f"- [{chunk.web.title}]({chunk.web.uri})")
                                     
            except Exception as e_final:
                st.error(f"❌ Lỗi hệ thống: {str(e_final)}")
                # Hiện debug list nếu chết hẳn
                with st.expander("Debug Info"):
                    st.write(genai.list_models())
