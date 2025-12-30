import streamlit as st
import google.generativeai as genai
from PIL import Image
import time

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="TITAN VISION v4.0", page_icon="👁️", layout="wide")

# CSS làm đẹp nút bấm
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #FF4B4B 0%, #FF914D 100%);
        color: white;
        font-weight: bold;
        border: none;
        height: 3em;
    }
</style>
""", unsafe_allow_html=True)

st.title("👁️ TITAN VISION ENGINE v4.0")
st.caption("Strategic Partner Edition - Auto Detect Model")

# --- 2. SIDEBAR CẤU HÌNH ---
with st.sidebar:
    st.header("⚙️ Trung tâm điều khiển")
    
    # Xử lý API Key
    if 'GOOGLE_API_KEY' in st.secrets:
        api_key = st.secrets['GOOGLE_API_KEY']
        st.success("✅ Đã nạp API Key bảo mật")
    else:
        api_key = st.text_input("🔑 Google API Key", type="password")
        st.caption("Chưa có key? Vào Google AI Studio lấy nhé.")
    
    mode = st.radio("Chế độ:", ["Auto-Router", "Vision Analysis", "Code Audit"])
    
    st.divider()
    
    # --- DEBUG INFO (ĐỂ SOI LỖI) ---
    with st.expander("🛠️ Debug thông tin Model"):
        if api_key:
            try:
                genai.configure(api_key=api_key)
                # Lấy danh sách model thực tế mà tài khoản này dùng được
                models = [m.name for m in genai.list_models()]
                st.write("Các model khả dụng:", models)
            except Exception as e:
                st.error(f"Lỗi kết nối: {e}")
        else:
            st.warning("Nhập Key để xem model.")

# --- 3. LOGIC CHỌN MODEL THÔNG MINH ---
def get_best_model():
    """Tự động chọn model tốt nhất có sẵn"""
    try:
        # Lấy danh sách model từ Google
        available_models = [m.name for m in genai.list_models()]
        
        # Ưu tiên Flash (Nhanh, Rẻ, Vision ngon)
        if 'models/gemini-1.5-flash' in available_models:
            return genai.GenerativeModel('gemini-1.5-flash')
        
        # Nếu không có Flash, tìm Pro Vision (Bản cũ nhưng có mắt)
        elif 'models/gemini-pro-vision' in available_models:
            return genai.GenerativeModel('gemini-pro-vision')
            
        # Đường cùng thì dùng Gemini Pro (Chỉ text)
        elif 'models/gemini-pro' in available_models:
            return genai.GenerativeModel('gemini-pro')
            
        # Nếu vẫn không thấy, thử gọi đại Flash (Cầu may)
        else:
            return genai.GenerativeModel('gemini-1.5-flash')
            
    except Exception as e:
        # Nếu lỗi quá nặng (ví dụ chưa config key), trả về None
        return None

TITAN_INSTRUCTION = """
ROLE: Bạn là TITAN v4.0. Nhiệm vụ: Phân tích Input và đưa ra giải pháp "Production-Ready".
OUTPUT: Markdown format, rõ ràng, sắc bén. Chia làm 3 phần: The Verdict, Deep Dive, Action Plan.
"""

# --- 4. GIAO DIỆN CHÍNH ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📥 Dữ liệu đầu vào")
    txt_input = st.text_area("Nhập ý tưởng / Code / Câu hỏi:", height=250, placeholder="Ví dụ: Phân tích bức ảnh này và trích xuất code HTML...")
    
    uploaded_file = st.file_uploader("Tải ảnh phân tích (JPG/PNG):", type=["jpg", "png", "jpeg"])
    img_data = None
    if uploaded_file:
        img_data = Image.open(uploaded_file)
        st.image(img_data, caption="Ảnh Preview", use_container_width=True)
    
    btn_run = st.button("🚀 KÍCH HOẠT TITAN")

with col2:
    st.subheader("💎 Kết quả phân tích")
    
    if btn_run:
        if not api_key:
            st.warning("⚠️ Vui lòng nhập API Key trước khi chạy!")
        else:
            with st.spinner("📡 TITAN đang kết nối vệ tinh..."):
                try:
                    genai.configure(api_key=api_key)
                    
                    # Gọi hàm chọn model thông minh
                    model = get_best_model()
                    
                    if model is None:
                        st.error("🔥 Không tìm thấy Model nào khả dụng. Kiểm tra API Key hoặc Debug bên sidebar.")
                    else:
                        # Chuẩn bị Prompt
                        req = [f"MODE: {mode}\nINPUT: {txt_input}"]
                        if img_data:
                            # Nếu model là gemini-pro (chỉ text) mà có ảnh -> Báo cảnh báo
                            if 'gemini-pro' in model.model_name and 'vision' not in model.model_name:
                                st.warning(f"⚠️ Đang dùng model '{model.model_name}' (không hỗ trợ ảnh). Ảnh sẽ bị bỏ qua.")
                            else:
                                req.append(img_data)
                                req[0] += "\n(CÓ ẢNH ĐÍNH KÈM)"
                        
                        # Set instruction nếu model hỗ trợ
                        # (Một số model cũ không hỗ trợ system_instruction trong constructor, nên ta kẹp vào prompt)
                        req[0] = TITAN_INSTRUCTION + "\n\n" + req[0]

                        # Bắn API
                        response = model.generate_content(req)
                        
                        # Hiện kết quả
                        st.success(f"✅ Đã xử lý xong bằng model: {model.model_name}")
                        st.markdown(response.text)
                        
                        # Nút tải về
                        st.download_button("💾 Tải báo cáo (.md)", response.text, "Titan_Report.md")
                        
                except Exception as e:
                    st.error(f"🔥 LỖI HỆ THỐNG: {str(e)}")
                    st.info("💡 Mẹo: Hãy mở mục 'Debug thông tin Model' bên trái để xem chi tiết.")
