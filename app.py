import streamlit as st
import google.generativeai as genai
from PIL import Image

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN
# ==========================================
st.set_page_config(
    page_title="TITAN VISION ENGINE v5.3",
    page_icon="👁️",
    layout="wide"
)

# CSS làm đẹp
st.markdown("""
<style>
    .stButton>button {
        background: linear-gradient(90deg, #FF4B4B 0%, #FF9068 100%);
        color: white;
        border: none;
        height: 3em;
        font-weight: bold;
    }
    .stTextArea textarea {
        background-color: #0E1117;
        color: #FAFAFA;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. THANH CÀI ĐẶT (SIDEBAR)
# ==========================================
with st.sidebar:
    st.title("⚙️ CẤU HÌNH")
    
    # Ưu tiên lấy Key từ Secrets của Streamlit Cloud, nếu không có thì nhập tay
    if 'GOOGLE_API_KEY' in st.secrets:
        api_key = st.secrets['GOOGLE_API_KEY']
        st.success("✅ Đã kết nối API Key hệ thống")
    else:
        api_key = st.text_input("🔑 Google API Key", type="password")
        st.caption("Nếu chưa có, [lấy Key tại đây](https://aistudio.google.com/app/apikey)")

    st.divider()
    mode = st.selectbox(
        "Chế độ:",
        ["Phân tích Hình ảnh", "Review Code", "Viết Content", "Chat Tự do"]
    )

# ==========================================
# 3. HÀM XỬ LÝ (LOGIC)
# ==========================================
def call_gemini(key, text, img, mode):
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt_parts = [f"CHẾ ĐỘ: {mode}\n\nYÊU CẦU: {text}"]
        if img:
            prompt_parts.append(img)
            prompt_parts[0] = f"[XỬ LÝ ẢNH - CHẾ ĐỘ {mode}]\n" + prompt_parts[0]
            
        response = model.generate_content(prompt_parts)
        return response.text
    except Exception as e:
        return f"🔥 LỖI: {str(e)}"

# ==========================================
# 4. GIAO DIỆN CHÍNH
# ==========================================
st.title("👁️ TITAN VISION ENGINE v5.3")
st.caption("Phiên bản chuẩn cho Streamlit Cloud")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📥 Input")
    user_input = st.text_area("Nội dung / Câu hỏi:", height=200)
    uploaded_file = st.file_uploader("Tải ảnh (nếu cần)", type=["jpg", "png", "jpeg", "webp"])
    
    image_data = None
    if uploaded_file:
        image_data = Image.open(uploaded_file)
        st.image(image_data, caption="Ảnh Preview", use_container_width=True)

    btn_run = st.button("✨ KÍCH HOẠT TITAN", type="primary", use_container_width=True)

with col2:
    st.subheader("💎 Kết quả")
    
    if btn_run:
        if not api_key:
            st.error("⚠️ Chưa nhập API Key!")
        elif not user_input and not image_data:
            st.warning("⚠️ Nhập nội dung hoặc ảnh để bắt đầu.")
        else:
            with st.spinner("📡 TITAN đang xử lý..."):
                result = call_gemini(api_key, user_input, image_data, mode)
                st.markdown(result)
