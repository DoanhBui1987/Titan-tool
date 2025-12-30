import streamlit as st
import requests
import json
import base64
from PIL import Image
import io

st.set_page_config(page_title="TITAN MODEL HUNTER", page_icon="🏹")

st.title("🏹 TITAN: MODEL HUNTER")
st.caption("Dò tìm xem Key của bạn thực sự dùng được con AI nào.")

# 1. NHẬP KEY
api_key = st.text_input("Dán API Key vào đây:", type="password")

# 2. HÀM DÒ TÌM DANH SÁCH MODEL (QUAN TRỌNG)
def get_available_models(key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # Lọc ra các model hỗ trợ generateContent
            models = []
            if 'models' in data:
                for m in data['models']:
                    if "generateContent" in m['supportedGenerationMethods']:
                        models.append(m['name'].replace("models/", ""))
            return models
        else:
            return None
    except:
        return None

# 3. GIAO DIỆN CHỌN MODEL
valid_models = []
if api_key and len(api_key) > 30:
    with st.spinner("Đang hỏi Google danh sách Model..."):
        valid_models = get_available_models(api_key)
    
    if valid_models:
        st.success(f"✅ Key này ngon! Tìm thấy {len(valid_models)} models khả dụng.")
        selected_model = st.selectbox("👉 CHỌN MODEL ĐỂ CHẠY:", valid_models, index=0)
    else:
        st.error("❌ Key này không lấy được danh sách Model nào cả! (Có thể chưa bật Generative Language API hoặc lỗi mạng)")
        selected_model = None
else:
    selected_model = None

# 4. INPUT VÀ CHẠY
txt = st.text_area("Nội dung:", value="Mô tả bức ảnh này")
file = st.file_uploader("Chọn ảnh:", type=["jpg", "png", "jpeg"])

if st.button("🚀 KÍCH HOẠT") and selected_model:
    # URL gọi đúng model bạn đã chọn
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{selected_model}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    parts = [{"text": txt}]
    
    # Xử lý ảnh
    if file:
        img_bytes = io.BytesIO()
        image = Image.open(file)
        image.save(img_bytes, format=image.format)
        b64_data = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
        parts.insert(0, {"inline_data": {"mime_type": "image/jpeg", "data": b64_data}})

    payload = {"contents": [{"parts": parts}]}

    with st.spinner(f"Đang chạy với model {selected_model}..."):
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            if response.status_code == 200:
                st.success("✅ THÀNH CÔNG!")
                st.write(response.json()['candidates'][0]['content']['parts'][0]['text'])
            else:
                st.error(f"❌ Lỗi: {response.text}")
        except Exception as e:
            st.error(f"Lỗi kết nối: {e}")
