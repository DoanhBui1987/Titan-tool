# @title 🚀 TITAN VISION ENGINE v5.2 (Clean & Safe Version)
import os
import urllib.request

# 1. CÀI ĐẶT MÔI TRƯỜNG
# ==========================================================
print("⏳ Đang thiết lập hệ thống... (Vui lòng chờ 30s)")
os.system("pip install -q streamlit google-generativeai pillow localtunnel")

# 2. VIẾT CODE ỨNG DỤNG (app.py)
# ==========================================================
app_code = """
import streamlit as st
import google.generativeai as genai
from PIL import Image
import time

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="TITAN VISION v5.2",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS TỐI ƯU ---
st.markdown(\"\"\"
<style>
    .stButton>button {
        background: linear-gradient(90deg, #FF4B4B 0%, #FF9068 100%);
        color: white;
        font-weight: bold;
        border: none;
        height: 3rem;
    }
    .stTextArea textarea {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    /* Ẩn bớt footer mặc định */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
</style>
\"\"\", unsafe_allow_html=True)

# --- SIDEBAR (CÀI ĐẶT) ---
with st.sidebar:
    st.title("⚙️ CẤU HÌNH TITAN")
    
    api_key = st.text_input("🔑 Nhập Google API Key", type="password", placeholder="Dán Key mới vào đây...")
    st.caption("[👉 Lấy Key mới tại đây nếu bị lỗi Quota](https://aistudio.google.com/app/apikey)")
    
    st.divider()
    
    mode = st.selectbox(
        "Chế độ hoạt động:",
        ["Phân tích Hình ảnh (Vision)", "Review Code & Lỗi", "Sáng tạo Nội dung", "Chat Tự do"]
    )
    
    st.info("💡 Mẹo: Phiên bản v5.2 đã loại bỏ các tác vụ ngầm để tiết kiệm Quota cho bạn.")

# --- HÀM XỬ LÝ GEMINI ---
def call_gemini(api_key, prompt, image=None):
    # Cấu hình
    genai.configure(api_key=api_key)
    
    # Model Flash: Nhanh - Rẻ - Ổn định
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Tạo nội dung gửi đi
    contents = []
    if image:
        contents.append(image)
        prompt = f"[YÊU CẦU XỬ LÝ ẢNH]\\n{prompt}"
    
    contents.append(prompt)
    
    # Gọi API
    response = model.generate_content(contents)
    return response.text

# --- GIAO DIỆN CHÍNH ---
st.title("👁️ TITAN VISION ENGINE v5.2")
st.caption("🚀 Phiên bản tối ưu: Tiết kiệm API - Giao diện sạch")

col1, col2 = st.columns([1, 1])

# CỘT TRÁI: INPUT
with col1:
    st.subheader("📥 Dữ liệu đầu vào")
    user_prompt = st.text_area("Nhập yêu cầu của bạn:", height=180, placeholder="Ví dụ: Phân tích bức ảnh này, hoặc sửa đoạn code này...")
    
    uploaded_file = st.file_uploader("Tải ảnh lên (Nếu cần)", type=["jpg", "png", "jpeg", "webp"])
    image_data = None
    if uploaded_file:
        image_data = Image.open(uploaded_file)
        st.image(image_data, caption="Ảnh Preview", use_container_width=True)

    # Nút bấm kích hoạt (QUAN TRỌNG: Chỉ chạy khi bấm nút này)
    run_btn = st.button("✨ KÍCH HOẠT TITAN NGAY", type="primary", use_container_width=True)

# CỘT PHẢI: OUTPUT
with col2:
    st.subheader("💎 Kết quả phân tích")
    
    if run_btn:
        if not api_key:
            st.warning("⚠️ Vui lòng nhập API Key ở cột bên trái trước!")
        elif not user_prompt and not image_data:
            st.warning("⚠️ Hãy nhập nội dung hoặc tải ảnh lên!")
        else:
            status_box = st.empty()
            try:
                status_box.info("📡 Đang kết nối vệ tinh Gemini...")
                
                # Gọi hàm xử lý
                result = call_gemini(api_key, user_prompt, image_data)
                
                status_box.success("✅ Hoàn tất!")
                st.markdown(result)
                
                # Nút tải về
                st.download_button("💾 Lưu kết quả (.md)", result, file_name="titan_result.md")
                
            except Exception as e:
                err_msg = str(e)
                if "429" in err_msg or "Quota" in err_msg:
                    status_box.error("🛑 LỖI HẾT TIỀN (QUOTA EXCEEDED)!")
                    st.error("API Key này đã hết hạn mức trong ngày. Vui lòng tạo Key mới từ một tài khoản Google khác và thử lại.")
                else:
                    status_box.error(f"🔥 Lỗi kỹ thuật: {err_msg}")

"""

# Ghi file
with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_code)

# 3. KHỞI CHẠY SERVER & LẤY PASSWORD
# ==========================================================
print("--------------------------------------------------")
try:
    ipv4 = urllib.request.urlopen('https://ipv4.icanhazip.com').read().decode('utf8').strip("\n")
    print(f"🔐 PASSWORD CỦA BẠN:  {ipv4}")
    print("👉 Hãy Copy số IP trên, bấm vào link bên dưới và Paste vào ô 'Tunnel Password'")
except:
    print("⚠️ Không lấy được IP tự động. Hãy tra Google 'What is my IP' để lấy IP public của Colab.")
print("--------------------------------------------------")

# Chạy ngầm
!streamlit run app.py &>/content/logs.txt & npx localtunnel --port 8501
