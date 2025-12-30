import streamlit as st
import requests
import json
import base64
from PIL import Image
import io

# CẤU HÌNH TRANG
st.set_page_config(page_title="TITAN VISION FINAL", page_icon="👁️", layout="wide")

st.markdown("""
<style>
    .stButton>button {background: #2E7D32; color: white; height: 3em; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

st.title("👁️ TITAN VISION: DIRECT CORE")
st.caption("Phiên bản chạy trực tiếp qua REST API (Đã sửa lỗi gửi ảnh)")

# ---------------------------------------------------------
# 1. KHU VỰC CHỌN MODEL (Đã chứng minh là chạy được)
# ---------------------------------------------------------
with st.sidebar:
    st.header("🔑 CẤU HÌNH")
    if 'GOOGLE_API_KEY' in st.secrets:
        api_key = st.secrets['GOOGLE_API_KEY']
    else:
        api_key = st.text_input("Nhập API Key:", type="password")

    # Tự động lấy danh sách Model
    available_models = []
    if api_key:
        try:
            url_list = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            resp = requests.get(url_list)
            if resp.status_code == 200:
                data = resp.json()
                for m in data.get('models', []):
                    # Chỉ lấy model hỗ trợ generateContent
                    if "generateContent" in m.get('supportedGenerationMethods', []):
                        available_models.append(m['name'].replace("models/", ""))
                st.success(f"✅ Đã kết nối! Tìm thấy {len(available_models)} models.")
            else:
                st.error("❌ Key đúng nhưng không lấy được list model.")
        except:
            pass

    # Dropdown chọn model (Ưu tiên Flash)
    default_idx = 0
    if "gemini-1.5-flash" in available_models:
        default_idx = available_models.index("gemini-1.5-flash")
    
    selected_model = st.selectbox(
        "Chọn Model:", 
        available_models if available_models else ["gemini-1.5-flash"], 
        index=default_idx
    )

# ---------------------------------------------------------
# 2. XỬ LÝ ẢNH & GỬI (PHẦN QUAN TRỌNG ĐÃ SỬA)
# ---------------------------------------------------------
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Input")
    prompt_text = st.text_area("Nội dung:", height=150, value="Mô tả chi tiết những gì bạn thấy trong ảnh này.")
    uploaded_file = st.file_uploader("Tải ảnh:", type=["png", "jpg", "jpeg", "webp"])
    
    img_blob = None
    mime_type = "image/jpeg" # Mặc định
    
    if uploaded_file:
        # 1. Hiển thị ảnh
        image = Image.open(uploaded_file)
        st.image(image, caption="Ảnh Input", use_container_width=True)
        
        # 2. Lấy đúng định dạng (Fix lỗi AI không thấy ảnh)
        mime_type = uploaded_file.type
        
        # 3. Chuyển sang bytes
        img_bytes = io.BytesIO()
        image.save(img_bytes, format=image.format)
        img_blob = base64.b64encode(img_bytes.getvalue()).decode('utf-8')

    btn_run = st.button("🚀 GỬI YÊU CẦU")

with col2:
    st.subheader("Result")
    if btn_run:
        if not api_key:
            st.error("Chưa nhập Key!")
        else:
            with st.spinner(f"Đang gửi tới {selected_model}..."):
                # URL chuẩn
                url_generate = f"https://generativelanguage.googleapis.com/v1beta/models/{selected_model}:generateContent?key={api_key}"
                headers = {'Content-Type': 'application/json'}
                
                # Payload chuẩn
                parts = []
                
                # Đưa ảnh vào trước (Quan trọng)
                if img_blob:
                    parts.append({
                        "inline_data": {
                            "mime_type": mime_type, # Dùng đúng loại file (png/jpg)
                            "data": img_blob
                        }
                    })
                
                # Đưa text vào sau
                parts.append({"text": prompt_text})
                
                payload = {"contents": [{"parts": parts}]}

                try:
                    # Gửi Request
                    response = requests.post(url_generate, headers=headers, data=json.dumps(payload))
                    
                    if response.status_code == 200:
                        try:
                            # Parse kết quả
                            result_text = response.json()['candidates'][0]['content']['parts'][0]['text']
                            st.success("✅ THÀNH CÔNG!")
                            st.markdown(result_text)
                        except:
                            st.warning("Google trả về OK nhưng cấu trúc lạ. JSON thô:")
                            st.json(response.json())
                    else:
                        st.error(f"❌ Lỗi từ Google ({response.status_code}):")
                        st.code(response.text)
                        
                except Exception as e:
                    st.error(f"Lỗi kết nối: {str(e)}")
