import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="TITAN VISION v4.0", page_icon="👁️", layout="wide")
st.markdown("<style>.stButton>button {width: 100%; background: #FF4B4B; color: white; font-weight: bold;}</style>", unsafe_allow_html=True)

# --- TIÊU ĐỀ ---
st.title("👁️ TITAN VISION ENGINE v4.0")
st.caption("Auto-Switch Model: Ưu tiên Flash, tự động fallback nếu lỗi.")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Cấu hình")
    if 'GOOGLE_API_KEY' in st.secrets:
        api_key = st.secrets['GOOGLE_API_KEY']
        st.success("✅ API Key hệ thống")
    else:
        api_key = st.text_input("🔑 Google API Key", type="password")
    
    mode = st.radio("Chế độ:", ["Auto-Router", "Vision Analysis", "Code Audit"])
    st.info("💡 Mẹo: Nhập text hoặc tải ảnh rồi bấm nút KÍCH HOẠT.")

# --- HÀM XỬ LÝ (QUAN TRỌNG: TỰ ĐỘNG CHỌN MODEL) ---
def get_model():
    # Thử ưu tiên Flash
    try:
        return genai.GenerativeModel('gemini-1.5-flash')
    except:
        # Nếu lỗi thì quay về Pro (Chống cháy)
        return genai.GenerativeModel('gemini-pro')

SYSTEM_PROMPT = "ROLE: Bạn là TITAN. Nhiệm vụ: Phân tích Input và đưa ra giải pháp tối ưu (Markdown)."

# --- GIAO DIỆN CHÍNH ---
c1, c2 = st.columns(2)
with c1:
    txt = st.text_area("Input:", height=200, placeholder="Nhập ý tưởng...")
    img_file = st.file_uploader("Ảnh (nếu có):", type=["jpg", "png", "jpeg"])
    img = Image.open(img_file) if img_file else None
    if img: st.image(img, caption="Preview", use_container_width=True)
    
    # NÚT BẤM DUY NHẤT
    btn = st.button("✨ KÍCH HOẠT TITAN")

with c2:
    if btn and api_key:
        with st.spinner("TITAN đang chạy..."):
            try:
                genai.configure(api_key=api_key)
                model = get_model() # Tự động chọn model
                
                req = [f"MODE: {mode}\nINPUT: {txt}"]
                if img: req.append(img)
                
                res = model.generate_content(req)
                st.markdown(res.text)
                st.download_button("💾 Tải về", res.text, "titan.md")
            except Exception as e:
                st.error(f"Lỗi: {e}")
    elif btn:
        st.warning("⚠️ Chưa nhập API Key!")
