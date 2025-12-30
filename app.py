import streamlit as st
import os
import google.generativeai as genai
from PIL import Image

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="TITAN VISION ENGINE v5.0",
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
    
    # CẤU HÌNH MODEL
    mode_mapping = {
        "🔴 Auto-Router": "gemini-2.0-flash-exp",
        "⚪ Vision Analysis": "gemini-2.0-flash-exp",
        "⚪ Code Audit": "gemini-2.0-flash-exp"
    }
    
    selected_mode_label = st.radio("Chế độ:", list(mode_mapping.keys()))
    selected_model_id = mode_mapping[selected_mode_label]
    
    st.markdown("---")

    # --- QUẢN LÝ API KEY ---
    api_key = None
    
    # 1. Kiểm tra secrets.toml
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("🟢 System Online (Secured)")
    else:
        # 2. Kiểm tra Session State
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

    # KẾT NỐI GEMINI
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
        else:
            try:
                with st.spinner("🔄 Đang truy cập dữ liệu thời gian thực..."):
                    # 1. CẤU HÌNH MODEL VỚI SEARCH TOOL
                    model = genai.GenerativeModel(
                        model_name=selected_model_id, # Lấy ID động từ Sidebar
                        tools='google_search_retrieval' # Kích hoạt Search
                    )
                    
                    # 2. Chuẩn bị dữ liệu
                    input_content = []
                    if user_prompt:
                        input_content.append(user_prompt)
                    if image_data:
                        input_content.append(image_data)
                    
                    if not input_content:
                        st.warning("⚠️ Vui lòng nhập nội dung hoặc tải ảnh!")
                    else:
                        # 3. Gọi Google Gemini
                        response = model.generate_content(input_content)
                        
                        # 4. Hiển thị kết quả
                        st.success("✅ Đã xử lý xong!")
                        
                        # Hiển thị nội dung chính
                        st.markdown(response.text)
                        
                        # --- XỬ LÝ HIỂN THỊ NGUỒN (GROUNDING) ---
                        # Logic hiển thị trích dẫn cực xịn của bác
                        if response.candidates and response.candidates[0].grounding_metadata:
                            meta = response.candidates[0].grounding_metadata
                            if meta.search_entry_point:
                                st.markdown("---")
                                st.caption("🌐 **Nguồn dữ liệu tham khảo:**")
                                
                                # Render HTML hiển thị link
                                if meta.grounding_chunks:
                                    for chunk in meta.grounding_chunks:
                                        if chunk.web:
                                            # Hiển thị Title và Link
                                            st.markdown(f"🔗 [{chunk.web.title}]({chunk.web.uri})")

            except Exception as e:
                # Bắt lỗi Rate Limit (429) hoặc lỗi khác
                err_msg = str(e)
                if "429" in err_msg:
                    st.error("🐢 Server đang quá tải (429). Model 'Experimental' bị giới hạn lượt dùng. Vui lòng chờ 30s!")
                else:
                    st.error(f"❌ Lỗi hệ thống: {err_msg}")
