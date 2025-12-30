import streamlit as st
import requests
import json
import base64
from PIL import Image
import io

st.set_page_config(page_title="TITAN FINAL RESET", page_icon="💀")

st.title("💀 TITAN: RESET HOÀN TOÀN")
st.caption("Phiên bản này bắt buộc nhập Key thủ công mỗi lần chạy để tránh lỗi lưu cache.")

# 1. NHẬP KEY (BẮT BUỘC NHẬP TAY)
# Tôi đã xóa bỏ đoạn kiểm tra st.secrets để tránh nó lấy nhầm key cũ
api_key = st.text_input("1. Dán API Key mới nhất vào đây (Bắt đầu bằng AIza...):", type="password")

# Hiển thị 5 ký tự đầu để bạn kiểm tra xem có đúng key mới không
if api_key:
    st.write(f"👉 Đang dùng Key bắt đầu bằng: **{api_key[:5]}...** (Hãy so sánh với trang Google xem đúng chưa)")

# 2. INPUT
txt = st.text_area("2. Nội dung:", value="Mô tả chi tiết bức ảnh này")
file = st.file_uploader("3. Chọn ảnh:", type=["jpg", "png", "jpeg"])

# 3. HÀM GỬI (Siêu đơn giản)
def run_titan(key, prompt, img_file):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
    headers = {'Content-Type': 'application/json'}
    
    parts = [{"text": prompt}]
    
    if img_file:
        img_bytes = io.BytesIO()
        image = Image.open(img_file)
        image.save(img_bytes, format=image.format)
        b64_data = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
        
        parts.insert(0, {
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": b64_data
            }
        })

    payload = {"contents": [{"parts": parts}]}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            return "✅ THÀNH CÔNG:\n" + response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"❌ LỖI ({response.status_code}): {response.text}"
    except Exception as e:
        return f"🔥 LỖI KẾT NỐI: {str(e)}"

# 4. NÚT BẤM
if st.button("🚀 CHẠY THỬ (Không qua trung gian)"):
    if not api_key:
        st.error("Chưa nhập Key!")
    elif len(api_key) < 30:
        st.error("Key quá ngắn, chắc chắn là copy thiếu rồi!")
    else:
        with st.spinner("Đang gửi..."):
            res = run_titan(api_key, txt, file)
            if "✅" in res:
                st.success(res)
            else:
                st.error(res)
