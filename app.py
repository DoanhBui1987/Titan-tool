import streamlit as st
import requests
import json
import base64
from PIL import Image
import io

# CẤU HÌNH
st.set_page_config(page_title="TITAN REST API", page_icon="⚡")

st.markdown("""
<style>
    .stButton>button {background: #FF4B4B; color: white; width: 100%;}
</style>
""", unsafe_allow_html=True)

st.title("⚡ TITAN DIRECT LINK (REST API)")
st.caption("Bỏ qua thư viện trung gian - Gọi thẳng lên Google Server")

# 1. NHẬP KEY
with st.sidebar:
    st.header("🔑 API KEY")
    if 'GOOGLE_API_KEY' in st.secrets:
        api_key = st.secrets['GOOGLE_API_KEY']
        st.success("Đã nhận Key từ Secrets")
    else:
        api_key = st.text_input("Nhập Key mới tạo:", type="password")

# 2. HÀM GỬI REQUEST TRỰC TIẾP (QUAN TRỌNG NHẤT)
def call_google_direct(key, prompt, image_data=None):
    # Endpoint chính thức của Google Gemini 1.5 Flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
    
    # Chuẩn bị nội dung gửi (Payload)
    parts = [{"text": prompt}]
    
    # Nếu có ảnh, phải mã hóa sang Base64
    if image_data:
        # Convert ảnh sang byte
        img_byte_arr = io.BytesIO()
        image_data.save(img_byte_arr, format=image_data.format)
        img_bytes = img_byte_arr.getvalue()
        
        # Mã hóa base64
        b64_string = base64.b64encode(img_bytes).decode('utf-8')
        
        # Thêm vào gói tin
        img_payload = {
            "inline_data": {
                "mime_type": "image/jpeg", # Giả định ảnh là jpeg/png
                "data": b64_string
            }
        }
        parts.insert(0, img_payload) # Đưa ảnh lên trước text

    payload = {
        "contents": [{
            "parts": parts
        }]
    }

    # Gửi đi bằng requests (Bỏ qua thư viện google-generativeai)
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        # Kiểm tra kết quả
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"❌ LỖI TỪ SERVER GOOGLE ({response.status_code}):\n{response.text}"
            
    except Exception as e:
        return f"🔥 LỖI KẾT NỐI MẠNG: {str(e)}"

# 3. GIAO DIỆN
col1, col2 = st.columns(2)

with col1:
    txt_input = st.text_area("Nội dung:", height=150, value="Mô tả bức ảnh này")
    file = st.file_uploader("Upload ảnh:", type=["jpg", "png", "jpeg"])
    
    img = None
    if file:
        img = Image.open(file)
        st.image(img, caption="Ảnh Input", use_container_width=True)
    
    btn = st.button("🚀 GỬI TRỰC TIẾP")

with col2:
    if btn:
        if not api_key:
            st.error("Chưa nhập Key!")
        else:
            with st.spinner("Đang gọi điện thẳng cho Google..."):
                result = call_google_direct(api_key, txt_input, img)
                
                if "❌" in result or "🔥" in result:
                    st.error(result)
                    st.markdown("---")
                    st.warning("**NẾU VẪN LỖI:**\nCó nghĩa là Key này (hoặc tài khoản Gmail này) đã bị Google chặn IP của Streamlit. Bạn hãy thử chạy code này trên máy tính cá nhân (Localhost) thay vì trên web.")
                else:
                    st.success("✅ THÀNH CÔNG RỰC RỠ!")
                    st.markdown(result)
