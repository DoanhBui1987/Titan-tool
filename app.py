import streamlit as st
import google.generativeai as genai
from PIL import Image

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
    # Phần này cực quan trọng để biết tài khoản bạn có model gì
    available_models = []
    with st.expander("🛠️ Debug thông tin Model", expanded=True):
        if api_key:
            try:
                genai.configure(api_key=api_key)
                # Lấy danh sách model thực tế
                available_models = [m.name for m in genai.list_models()]
                st.write("Model tìm thấy:", available_models)
            except Exception as e:
                st.error(f"Lỗi kết nối: {e}")
        else:
            st.warning("Nhập Key để xem model.")

# --- 3. LOGIC CHỌN MODEL THÔNG MINH ---
def get_best_model(models_list):
    """Chọn model dựa trên danh sách thực tế"""
    try:
        # Ưu tiên Flash (Nhanh, Rẻ, Vision ngon)
        if 'models/gemini-1.5-flash' in models_list:
            return genai.GenerativeModel('gemini-1.5-flash')
        
        # Nếu không có Flash, tìm Pro Vision (Bản cũ nhưng có mắt)
        elif 'models/gemini-pro-vision' in models_list:
            return genai.GenerativeModel('gemini-pro-vision')
            
        # Đường cùng thì dùng Gemini Pro (Chỉ text)
        elif 'models/gemini-pro' in models_list:
            return genai.GenerativeModel('gemini-pro')
            
        # Nếu danh sách rỗng hoặc lạ, thử gọi Flash mặc định
        else:
            return genai.GenerativeModel('gemini-1.5-flash')
            
    except Exception as e:
        return None

TITAN_INSTRUCTION = """
ROLE: Bạn là TITAN v4.0. Nhiệm vụ: Phân tích Input và đưa ra giải pháp "Production-Ready".
OUTPUT: Markdown format. Chia làm 3 phần: The Verdict, Deep Dive, Action Plan.
"""

# --- 4. GIAO DIỆN CHÍNH ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📥 Dữ liệu đầu vào")
    txt_input = st.text_area("Nhập ý tưởng / Code / Câu hỏi:", height=250, placeholder="Ví dụ: Phân tích bức ảnh này...")
    
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
                    
                    # Gọi hàm chọn model thông minh dựa trên list đã quét
                    model = get_best_model(available_models)
                    
                    if model is None:
                        st.error("🔥 Lỗi khởi tạo Model.")
                    else:
                        # Chuẩn bị Prompt
                        req = [f"MODE: {mode}\nINPUT: {txt_input}"]
                        if img_data:
                            # Kiểm tra nếu model chỉ hỗ trợ text (gemini-pro thường)
                            if 'gemini-pro' in model.model_name and 'vision' not in model.model_name:
                                st.warning(f"⚠️ Model '{model.model_name}' không đọc được ảnh. Đang chạy chế độ Text.")
                            else:
                                req.append(img_data)
                                req[0] += "\n(CÓ ẢNH ĐÍNH KÈM)"
                        
                        # Kẹp instruction vào prompt để an toàn cho mọi model
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
