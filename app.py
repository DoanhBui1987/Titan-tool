import streamlit as st
import google.generativeai as genai
from PIL import Image
import sys

# ==========================================
# 1. CẤU HÌNH & KIỂM TRA MÔI TRƯỜNG
# ==========================================
st.set_page_config(page_title="TITAN IMMORTAL", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    .stButton>button {background: #00C853; color: white; font-weight: bold;}
    .reportview-container {background: #0E1117;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LOGIC "BẤT TỬ" (TỰ ĐỘNG DÒ TÌM MODEL)
# ==========================================
def get_working_model_response(api_key, prompt, image):
    # Cấu hình API
    genai.configure(api_key=api_key)
    
    # DANH SÁCH CÁC MODEL SẼ THỬ LẦN LƯỢT
    # Google đổi tên liên tục, nên ta cứ thử hết list này
    model_list = [
        "gemini-1.5-flash",          # Ưu tiên 1: Nhanh, Rẻ
        "gemini-1.5-flash-latest",   # Ưu tiên 2: Bản mới nhất
        "gemini-1.5-pro",            # Ưu tiên 3: Thông minh hơn nhưng chậm
        "gemini-1.5-pro-latest",     # Ưu tiên 4
    ]
    
    log_report = [] # Ghi lại lịch sử thử
    
    for model_name in model_list:
        try:
            # Tạo model
            model = genai.GenerativeModel(model_name)
            
            # Chuẩn bị nội dung
            content = [prompt]
            if image:
                content.append(image)
                
            # GỌI API
            response = model.generate_content(content)
            
            # Nếu chạy đến đây tức là thành công!
            return {
                "success": True, 
                "model_used": model_name, 
                "text": response.text,
                "log": log_report
            }
            
        except Exception as e:
            # Nếu lỗi, ghi lại và thử thằng tiếp theo
            error_msg = str(e)
            log_report.append(f"❌ {model_name}: Thất bại ({error_msg})")
            continue 

    # Nếu thử hết sạch list mà vẫn lỗi
    return {
        "success": False, 
        "text": "TẤT CẢ MODEL ĐỀU THẤT BẠI. Vui lòng kiểm tra API Key hoặc File requirements.txt",
        "log": log_report
    }

# ==========================================
# 3. GIAO DIỆN NGƯỜI DÙNG
# ==========================================
with st.sidebar:
    st.header("🛡️ CẤU HÌNH")
    
    # Kiểm tra version thư viện
    lib_ver = genai.__version__
    if lib_ver < "0.7.0":
        st.error(f"⚠️ THƯ VIỆN CŨ QUÁ ({lib_ver})!")
        st.warning("Bạn cần tạo file requirements.txt với nội dung: google-generativeai>=0.7.2")
    else:
        st.success(f"✅ Thư viện ổn: v{lib_ver}")

    # Nhập Key
    if 'GOOGLE_API_KEY' in st.secrets:
        api_key = st.secrets['GOOGLE_API_KEY']
        st.success("Đã nhận Key ẩn")
    else:
        api_key = st.text_input("Nhập API Key:", type="password")

st.title("🛡️ TITAN IMMORTAL v7.0")
st.caption("Cơ chế tự động chuyển đổi Model khi Google thay đổi.")

col1, col2 = st.columns([1, 1])

with col1:
    user_prompt = st.text_area("Nội dung:", height=150, value="Mô tả bức ảnh này thật chi tiết.")
    uploaded_file = st.file_uploader("Ảnh:", type=["jpg", "png", "jpeg"])
    
    image_data = None
    if uploaded_file:
        image_data = Image.open(uploaded_file)
        st.image(image_data, caption="Input", width=300)

    btn_run = st.button("🚀 KÍCH HOẠT")

with col2:
    if btn_run:
        if not api_key:
            st.error("Chưa có API Key!")
        else:
            with st.spinner("🤖 Titan đang thử kết nối các vệ tinh..."):
                # Gọi hàm bất tử
                result = get_working_model_response(api_key, user_prompt, image_data)
                
                if result["success"]:
                    st.success(f"✅ Thành công với model: **{result['model_used']}**")
                    st.markdown(result["text"])
                    with st.expander("Xem nhật ký kết nối"):
                        st.write(result["log"])
                else:
                    st.error("🔥 HỆ THỐNG SỤP ĐỔ!")
                    st.write(result["text"])
                    with st.expander("Chi tiết lỗi (Gửi cái này cho kỹ thuật)"):
                        st.write(result["log"])
