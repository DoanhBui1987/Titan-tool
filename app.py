import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. CẤU HÌNH TRANG
st.set_page_config(page_title="TITAN FINAL", page_icon="🔥")

# 2. XỬ LÝ API KEY
with st.sidebar:
    st.header("🔑 CHÌA KHÓA")
    # Tự động lấy từ Secrets hoặc nhập tay
    if 'GOOGLE_API_KEY' in st.secrets:
        api_key = st.secrets['GOOGLE_API_KEY']
        st.success("✅ Đã nhận Key hệ thống")
    else:
        api_key = st.text_input("Dán API Key vào đây:", type="password")

# 3. HÀM GỌI GEMINI (Cơ chế chống lỗi 404)
def call_titan(key, prompt, img_data):
    genai.configure(api_key=key)
    
    # DANH SÁCH MODEL ĐỂ THỬ (Nếu cái đầu lỗi, thử cái sau)
    models_to_try = ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-pro-vision']
    
    last_error = ""
    
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            
            # Chuẩn bị dữ liệu
            content = [prompt]
            if img_data:
                content.append(img_data)
                
            # Gọi API
            response = model.generate_content(content)
            return f"**✅ Kết quả từ {model_name}:**\n\n" + response.text
            
        except Exception as e:
            last_error = str(e)
            continue # Thử model tiếp theo
            
    return f"❌ TẤT CẢ MODEL ĐỀU THẤT BẠI. Lỗi cuối cùng: {last_error}"

# 4. GIAO DIỆN CHÍNH
st.title("🔥 TITAN VISION: THE FINAL STAND")
st.info("Phiên bản tự động dò tìm Model phù hợp.")

input_text = st.text_area("Nhập câu hỏi:", height=100, placeholder="Ví dụ: Mô tả bức ảnh này...")
uploaded_file = st.file_uploader("Chọn ảnh:", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Ảnh đã chọn", width=300)
else:
    image = None

if st.button("🚀 CHẠY NGAY ĐI", type="primary"):
    if not api_key:
        st.error("⚠️ Chưa có API Key sếp ơi!")
    elif not input_text and not image:
        st.warning("⚠️ Nhập gì đó đi chứ!")
    else:
        with st.spinner("Đang triệu hồi AI... (Chờ xíu)"):
            result = call_titan(api_key, input_text, image)
            st.markdown(result)
