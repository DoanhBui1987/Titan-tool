import streamlit as st
import os
import subprocess
import sys

# --- 1. CÀI ĐẶT CƯỠNG CHẾ (FORCE INSTALL) ---
# Đoạn này sẽ chạy ngay khi app khởi động để ép cài bản mới nhất
try:
    import google.generativeai as genai
    # Kiểm tra xem có phải bản cũ không, nếu cũ quá thì cài lại
    version = genai.__version__
    if version < "0.8.3":
        st.warning(f"⚠️ Phát hiện bản cũ ({version}). Đang tự động nâng cấp...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "google-generativeai"])
        import google.generativeai as genai # Import lại
        st.success("✅ Đã nâng cấp xong! Vui lòng bấm Rerun nếu cần.")
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])
    import google.generativeai as genai

from PIL import Image
import io

# --- 2. CẤU HÌNH TRANG ---
st.set_page_config(page_title="TITAN GENESIS", page_icon="🌌", layout="wide")

st.markdown("""
<style>
    .stButton>button {background-color: #FF4B4B; color: white;}
    .reportview-container {background: #0E1117;}
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIC XỬ LÝ ---
with st.sidebar:
    st.title("🌌 TITAN CONTROL")
    # Hiển thị phiên bản để kiểm tra
    try:
        st.caption(f"Engine Version: {genai.__version__}")
    except:
        st.caption("Engine: Updating...")
        
    api_key = st.text_input("🔑 Google API Key", type="password", placeholder="AIza...")
    
    st.markdown("---")
    st.subheader("🧠 Chế độ")
    mode = st.radio("Chọn vai trò:", ["Free Chat", "Code Audit", "Creative"])

    st.markdown("---")
    rag_files = st.file_uploader("📚 Nạp Tài Liệu (RAG)", accept_multiple_files=True)

def call_titan(api_key, text, img, rag_context, mode):
    if not api_key: return "⚠️ Chưa nhập API Key!"
    
    try:
        genai.configure(api_key=api_key)
        
        # System Prompt
        sys_msg = "Bạn là TITAN - Trợ lý AI đa năng."
        if mode == "Code Audit": sys_msg += " Hãy soi lỗi code kỹ lưỡng."
        
        # Model config
        # Dùng model Flash 1.5 mới nhất
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=sys_msg)
        
        # Ghép nội dung
        content = []
        full_text = f"CHẾ ĐỘ: {mode}\n"
        if rag_context: full_text += f"TÀI LIỆU THAM KHẢO:\n{rag_context}\n\n"
        full_text += f"USER HỎI:\n{text}"
        
        content.append(full_text)
        if img: content.append(img)
        
        response = model.generate_content(content)
        return response.text

    except Exception as e:
        return f"🔥 LỖI: {str(e)}"

# --- 4. GIAO DIỆN CHÍNH ---
st.title("🌌 TITAN GENESIS ENGINE")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📥 Input")
    user_input = st.text_area("Nhập nội dung...", height=200)
    user_img = st.file_uploader("🖼️ Thêm ảnh", type=['png', 'jpg', 'jpeg'])
    
    if st.button("✨ KÍCH HOẠT TITAN", type="primary", use_container_width=True):
        if not user_input and not user_img:
            st.warning("Nhập gì đó đi chứ!")
        else:
            with st.spinner("Đang xử lý..."):
                # Xử lý RAG
                rag_data = ""
                if rag_files:
                    for f in rag_files:
                        try: rag_data += f.getvalue().decode("utf-8") + "\n"
                        except: pass
                
                # Xử lý Ảnh
                img_obj = Image.open(user_img) if user_img else None
                
                # Gọi AI
                result = call_titan(api_key, user_input, img_obj, rag_data, mode)
                st.session_state['result'] = result

with col2:
    st.subheader("📤 Output")
    if 'result' in st.session_state:
        st.markdown(st.session_state['result'])
