import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# 1. CẤU HÌNH TRANG
st.set_page_config(page_title="TITAN FINAL BOSS", page_icon="🔥", layout="wide")

# 2. CSS FIX GIAO DIỆN
st.markdown("""
<style>
    .stButton>button {width: 100%; background: #FF4B4B; color: white;}
</style>
""", unsafe_allow_html=True)

# 3. SIDEBAR & API KEY
with st.sidebar:
    st.title("🔑 CẤU HÌNH")
    # Ưu tiên lấy từ Secrets, không có thì nhập tay
    if 'GOOGLE_API_KEY' in st.secrets:
        api_key = st.secrets['GOOGLE_API_KEY']
        st.success("✅ Đã nạp Key từ hệ thống")
    else:
        api_key = st.text_input("Dán API Key vào đây:", type="password")
    
    st.info("Phiên bản v6.0: Đã fix lỗi Library cũ.")

# 4. HÀM GỌI GEMINI (Đơn giản hóa tối đa)
def ask_gemini(key, prompt, image):
    try:
        genai.configure(api_key=key)
        # Dùng model chuẩn nhất hiện nay
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        content = [prompt]
        if image:
            content.append(image)
            
        response = model.generate_content(content)
        return response.text
    except Exception as e:
        return f"❌ LỖI: {str(e)}\n\n(Nếu lỗi 404: Hãy kiểm tra lại file requirements.txt)"

# 5. GIAO DIỆN CHÍNH
st.title("🔥 TITAN VISION: FINAL BOSS")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Input")
    txt = st.text_area("Nhập câu hỏi:", height=150)
    img_file = st.file_uploader("Chọn ảnh", type=['png', 'jpg', 'jpeg'])
    
    img = None
    if img_file:
        img = Image.open(img_file)
        st.image(img, caption="Ảnh preview", use_container_width=True) # Streamlit mới dùng use_container_width
        
    btn = st.button("🚀 CHẠY NGAY")

with col2:
    st.subheader("Output")
    if btn:
        if not api_key:
            st.error("⚠️ Thiếu API Key!")
        else:
            with st.spinner("Đang xử lý..."):
                res = ask_gemini(api_key, txt, img)
                st.success("Xong!")
                st.markdown(res)
