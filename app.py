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
    """Chọn model tốt nhất dựa trên danh sách thực tế (Cập nhật T12/2025)"""
    try:
        # Ưu tiên số 1: Gemini 3 Flash (Hàng mới về - Siêu nhanh)
        if 'models/gemini-3-flash-preview' in models_list:
            return genai.GenerativeModel('gemini-3-flash-preview')

        # Ưu tiên số 2: Gemini 2.5 Flash (Bản ổn định nhất hiện nay)
        elif 'models/gemini-2.5-flash' in models_list:
            return genai.GenerativeModel('gemini-2.5-flash')

        # Ưu tiên số 3: Gemini 2.5 Pro (Dành cho task khó)
        elif 'models/gemini-2.5-pro' in models_list:
            return genai.GenerativeModel('gemini-2.5-pro')
            
        # Fallback: Tìm bất kỳ model nào có chữ 'flash' trong tên
        else:
            flash_models = [m for m in models_list if 'flash' in m]
            if flash_models:
                return genai.GenerativeModel(flash_models[0])
            # Đường cùng: Chọn đại model đầu tiên
            elif models_list:
                 return genai.GenerativeModel(models_list[0])
            else:
                return None
            
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
