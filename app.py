# @title 🚀 KÍCH HOẠT TITAN STREAMLIT (FIXED VERSION)
# ==========================================
# 1. CÀI ĐẶT MÔI TRƯỜNG & LẤY MẬT KHẨU
# ==========================================
import os
import urllib.request

# Cài đặt thư viện
print("⏳ Đang cài đặt thư viện (khoảng 30s)...")
os.system("pip install -q streamlit google-generativeai pillow localtunnel")

# Lấy Password Tunnel
print("--------------------------------------------------")
try:
    password = urllib.request.urlopen('https://ipv4.icanhazip.com').read().decode('utf8').strip("\n")
    print(f"🔐 MẬT KHẨU CỦA BẠN LÀ:  {password}")
    print("(Hãy COPY dãy số này để lát nữa nhập vào web)")
    print("--------------------------------------------------")
except:
    print("⚠️ Không lấy được IP tự động. Nếu web hỏi password, hãy thử Google 'what is my ip'")

# ==========================================
# 2. TẠO FILE ỨNG DỤNG (app.py) - Dùng Python Write
# ==========================================
app_code = """
import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- CẤU HÌNH ---
st.set_page_config(page_title="TITAN GENESIS", page_icon="🌌", layout="wide")

# CSS Custom
st.markdown(\"\"\"
<style>
    .stButton>button {background-color: #FF4B4B; color: white;}
    .reportview-container {background: #0E1117;}
</style>
\"\"\", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🌌 TITAN CONTROL")
    api_key = st.text_input("🔑 Google API Key", type="password", placeholder="AIza...")
    
    st.markdown("---")
    st.subheader("🧠 Chế độ (Persona)")
    mode = st.radio("Chọn vai trò:", ["Auto-Router", "Code Audit (Kỹ thuật)", "Creative (Sáng tạo/Ads)", "Free Chat"])

    st.markdown("---")
    st.subheader("📚 Nạp Kiến Thức (RAG Lite)")
    st.info("Tải file tài liệu lên để TITAN học.")
    rag_files = st.file_uploader("Upload PDF/TXT/MD", accept_multiple_files=True)

# --- RAG LOGIC ---
def process_rag(files):
    context = ""
    if files:
        for uploaded_file in files:
            # Đọc file text/md đơn giản
            try:
                stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
                context += f"\\n--- TÀI LIỆU: {uploaded_file.name} ---\\n{stringio.read()}\\n"
            except:
                context += f"\\n(Không đọc được file {uploaded_file.name} do sai định dạng)\\n"
    return context

# --- GEMINI LOGIC ---
TITAN_INSTRUCTION = \"\"\"
ROLE: Bạn là TITAN - Hệ thống tinh chế Đa phương thức.
MISSION: Xử lý Input dựa trên Context (nếu có) và yêu cầu người dùng.
\"\"\"

def call_titan(api_key, text, img, rag_context, mode):
    if not api_key: return "⚠️ Chưa nhập API Key!"
    
    try:
        genai.configure(api_key=api_key)
        
        system_msg = TITAN_INSTRUCTION
        if mode == "Code Audit": system_msg += "\\nFOCUS: Tìm lỗi, tối ưu code, bảo mật."
        if mode == "Creative": system_msg += "\\nFOCUS: Viết nội dung thu hút, viral, marketing."
        
        # Dùng model Flash
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_msg)
        
        # Ghép prompt
        prompt_parts = []
        full_text = f"CHẾ ĐỘ: {mode}\\n\\n"
        
        if rag_context:
            full_text += f"CONTEXT (THÔNG TIN TỪ FILE):\\n{rag_context}\\n\\n"
            
        full_text += f"YÊU CẦU CỦA USER:\\n{text}"
        prompt_parts.append(full_text)
        
        if img: prompt_parts.append(img)
        
        response = model.generate_content(prompt_parts)
        return response.text
    except Exception as e: return f"🔥 LỖI: {str(e)}"

# --- UI CHÍNH ---
st.title("🌌 TITAN GENESIS ENGINE (Streamlit)")
st.caption("Powered by Gemini 1.5 Flash")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📥 Input")
    user_input = st.text_area("Nhập nội dung...", height=200)
    user_img = st.file_uploader("🖼️ Thêm ảnh (Vision)", type=['png', 'jpg', 'jpeg'])
    
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
"""

# Ghi nội dung vào file app.py
with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_code)

print("✅ Đã tạo xong file app.py")

# ==========================================
# 3. KHỞI CHẠY SERVER
# ==========================================
print("🚀 Đang khởi động Server... (Chờ hiện link 'your url is')")
!streamlit run app.py &>/content/logs.txt & npx localtunnel --port 8501
