import streamlit as st
import os
import google.generativeai as genai
from PIL import Image
import time

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
# ... (Phần trên giữ nguyên) ...

# --- 5. XỬ LÝ LOGIC GỌI AI (SMART FALLBACK VERSION) ---
with col_output:
    st.subheader("💎 Kết quả phân tích")
    
    if run_btn:
        if not api_key:
            st.error("⛔ Chưa có API Key!")
        else:
            # Tạo placeholder để hiển thị trạng thái xử lý
            status_box = st.empty()
            
            try:
                # BƯỚC 1: THỬ CHẠY MODEL MẠNH NHẤT (GEMINI 2.0)
                status_box.info("⚡ Đang kích hoạt Gemini 2.0 Flash Exp...")
                
                # Cấu hình model chính
                model = genai.GenerativeModel(
                    model_name="gemini-2.0-flash-exp",
                    tools='google_search_retrieval' # Vẫn giữ tính năng Search
                )
                
                # Chuẩn bị dữ liệu
                input_content = []
                if user_prompt: input_content.append(user_prompt)
                if image_data: input_content.append(image_data)
                
                # Gọi API
                response = model.generate_content(input_content)
                
                # Nếu thành công:
                status_box.success("✅ Đã xử lý xong bằng Gemini 2.0!")
                st.markdown(response.text)
                
                # Hiển thị nguồn (nếu có)
                if response.candidates[0].grounding_metadata.search_entry_point:
                    st.markdown("---")
                    st.caption("🌐 Nguồn dữ liệu thời gian thực (Gemini 2.0)")
                    grounding_info = response.candidates[0].grounding_metadata
                    if grounding_info.grounding_chunks:
                        for chunk in grounding_info.grounding_chunks:
                            if chunk.web:
                                st.markdown(f"- [{chunk.web.title}]({chunk.web.uri})")

            except Exception as e:
                # BƯỚC 2: NẾU GEMINI 2.0 BỊ LỖI (429) -> CHUYỂN VỀ 1.5 FLASH
                error_msg = str(e)
                if "429" in error_msg or "ResourceExhausted" in error_msg:
                    status_box.warning("🐢 Gemini 2.0 đang quá tải. Hệ thống tự động chuyển sang Gemini 1.5 Flash...")
                    time.sleep(1) # Nghỉ 1 nhịp
                    
                    try:
                        # Gọi Model dự phòng (Backup Model)
                        backup_model = genai.GenerativeModel("gemini-1.5-flash")
                        
                        # Lưu ý: 1.5 Flash không hỗ trợ Search tool mạnh như 2.0 nên ta bỏ tham số tools
                        response_backup = backup_model.generate_content(input_content)
                        
                        status_box.success("✅ Đã xử lý xong bằng Gemini 1.5 Flash (Backup Mode)!")
                        st.markdown(response_backup.text)
                        
                    except Exception as e2:
                        status_box.error(f"❌ Cả 2 hệ thống đều bận. Vui lòng thử lại sau 30s. Lỗi: {str(e2)}")
                else:
                    # Nếu là lỗi khác (như sai Key, lỗi mạng...)
                    status_box.error(f"❌ Lỗi hệ thống: {error_msg}")

    else:
        st.info("👋 Waiting for command...")
