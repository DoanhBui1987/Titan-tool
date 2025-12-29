import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- CẤU HÌNH ---
st.set_page_config(page_title="TITAN GENESIS", page_icon="🌌", layout="wide")

# CSS Custom
st.markdown("""
<style>
    .stButton>button {background-color: #FF4B4B; color: white;}
    .reportview-container {background: #0E1117;}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🌌 TITAN CONTROL")
    api_key = st.text_input("🔑 Google API Key", type="password", placeholder="AIza...")
    
    st.markdown("---")
    st.subheader("🧠 Chế độ (Persona)")
    mode = st.radio("Chọn vai trò:", ["Auto-Router", "Code Audit (Kỹ thuật)", "Creative (Sáng tạo/Ads)", "Free Chat"])

    st.markdown("---")
    st.subheader("📚 Nạp Kiến Thức (RAG Lite)")
    rag_files = st.file_uploader("Upload PDF/TXT/MD", accept_multiple_files=True)

# --- RAG LOGIC ---
def process_rag(files):
    context = ""
    if files:
        for uploaded_file in files:
            try:
                stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
                context += f"\n--- TÀI LIỆU: {uploaded_file.name} ---\n{stringio.read()}\n"
            except:
                pass
    return context

# --- GEMINI LOGIC (AUTO-SWITCH MODEL) ---
TITAN_INSTRUCTION = """
ROLE: Bạn là TITAN - Hệ thống tinh chế Đa phương thức.
MISSION: Xử lý Input dựa trên Context (nếu có) và yêu cầu người dùng.
"""

def call_titan(api_key, text, img, rag_context, mode):
    if not api_key: return "⚠️ Chưa nhập API Key!"
    
    try:
        genai.configure(api_key=api_key)
        
        system_msg = TITAN_INSTRUCTION
        if mode == "Code Audit": system_msg += "\nFOCUS: Tìm lỗi, tối ưu code, bảo mật."
        if mode == "Creative": system_msg += "\nFOCUS: Viết nội dung thu hút, viral, marketing."
        
        # --- CƠ CHẾ TỰ ĐỘNG THỬ MODEL ---
        # Thử lần lượt: 1.5 Flash -> 1.5 Pro -> Pro (Cũ)
        models_to_try = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
        
        response_text = ""
        used_model = ""
        error_log = ""

        # Ghép prompt
        prompt_parts = []
        full_text = f"CHẾ ĐỘ: {mode}\n\n"
        if rag_context: full_text += f"CONTEXT:\n{rag_context}\n\n"
        full_text += f"YÊU CẦU CỦA USER:\n{text}"
        prompt_parts.append(full_text)
        if img: prompt_parts.append(img)

        # Vòng lặp thử model
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name, system_instruction=system_msg)
                response = model.generate_content(prompt_parts)
                response_text = response.text
                used_model = model_name
                break # Thành công thì thoát ngay
            except Exception as e:
                error_log += f"- {model_name}: {str(e)}\n"
                continue
        
        if response_text:
            return f"✅ **Đã xử lý bằng model: {used_model}**\n\n" + response_text
        else:
            return f"🔥 TẤT CẢ MODEL ĐỀU LỖI. CHI TIẾT:\n{error_log}"

    except Exception as e: return f"🔥 LỖI HỆ THỐNG: {str(e)}"

# --- UI CHÍNH ---
st.title("🌌 TITAN GENESIS ENGINE")
st.caption("Powered by Gemini 1.5 Flash • Auto-Fix Edition")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📥 Input")
    user_input = st.text_area("Nhập nội dung...", height=200)
    user_img = st.file_uploader("🖼️ Thêm ảnh", type=['png', 'jpg', 'jpeg'])
    
    img_data = None
    if user_img:
        img_data = Image.open(user_img)
        st.image(img_data, caption="Ảnh Input", use_column_width=True)
        
    if st.button("✨ KÍCH HOẠT TITAN", type="primary", use_container_width=True):
        if not user_input and not img_data:
            st.warning("Nhập gì đó đi chứ!")
        else:
            with st.spinner("TITAN đang xử lý..."):
                rag_data = process_rag(rag_files)
                result = call_titan(api_key, user_input, img_data, rag_data, mode)
                st.session_state['result'] = result

with col2:
    st.subheader("📤 Output")
    if 'result' in st.session_state:
        st.markdown(st.session_state['result'])
        st.download_button("💾 Tải kết quả", st.session_state['result'], "titan_output.md")
