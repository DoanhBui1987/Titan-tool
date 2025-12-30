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
    # Kiểm tra version để yên tâm
    try:
        st.caption(f"GenAI Lib Version: {genai.__version__}")
    except:
        pass
        
    api_key = st.text_input("🔑 Google API Key", type="password", placeholder="AIza...")
    
    st.markdown("---")
    st.subheader("🧠 Chế độ")
    mode = st.radio("Chọn vai trò:", ["Free Chat", "Code Audit", "Creative"])

    st.markdown("---")
    rag_files = st.file_uploader("📚 Nạp Tài Liệu (RAG)", accept_multiple_files=True)

# --- LOGIC ---
def call_titan(api_key, text, img, rag_context, mode):
    if not api_key: return "⚠️ Chưa nhập API Key!"
    
    try:
        genai.configure(api_key=api_key)
        
        # Cấu hình Model - Dùng Flash
        model = genai.GenerativeModel('gemini-1.5-flash')
        
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

# --- GIAO DIỆN CHÍNH ---
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
