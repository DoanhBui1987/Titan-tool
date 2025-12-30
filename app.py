import streamlit as st
import os
import time
import google.generativeai as genai
from PIL import Image

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="TITAN VISION ENGINE v5.0",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS DARK MODE & FIX UI ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; }
    .stButton > button { width: 100%; border-radius: 5px; height: 3em; font-weight: bold;}
    /* Ẩn bớt footer mặc định */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. HÀM TỰ ĐỘNG DÒ TÌM MODEL (AUTO-DISCOVERY) ---
# Đây là "vũ khí bí mật" để fix lỗi 404
def get_best_available_model():
    """Tự động tìm model tốt nhất mà Key này dùng được."""
    try:
        # Lấy danh sách tất cả model khả dụng
        all_models = [m.name for m in genai.list_models()]
        
        # Danh sách ưu tiên (Từ xịn nhất xuống thấp nhất)
        priority_list = [
            "models/gemini-1.5-pro-latest",
            "models/gemini-1.5-pro",
            "models/gemini-1.5-flash",
            "models/gemini-pro-vision", # Bản cũ nhưng ổn định
            "models/gemini-pro"
        ]
        
        # 1. Tìm trong danh sách ưu tiên xem có cái nào khớp không
        for target in priority_list:
            if target in all_models:
                return target # Tìm thấy là chốt luôn
                
        # 2. Nếu không khớp cái nào, tìm bất kỳ cái nào có chữ 'gemini'
        for m in all_models:
            if 'gemini' in m and 'generateContent' in genai.get_model(m).supported_generation_methods:
                return m
                
        # 3. Đường cùng: Trả về default (có thể 404 nhưng hết cách)
        return "models/gemini-1.5-flash"
        
    except Exception as e:
        # Nếu lỗi ngay cả khi list_models (thường do sai Key), trả về fallback
        return "gemini-1.5-flash"

# --- 4. SIDEBAR ---
with st.sidebar:
    st.header("⚙ Trung tâm điều khiển")
    
    # API KEY HANDLING
    api_key = None
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("🟢 Key: Secured")
    else:
        if "api_key" not in st.session_state:
            st.session_state.api_key = ""
        
        if not st.session_state.api_key:
            user_input = st.text_input("Google API Key:", type="password")
            if user_input:
                st.session_state.api_key = user_input
                st.rerun()
        else:
            api_key = st.session_state.api_key
            st.info("🟢 Key: Ready")
            if st.button("🔄 Reset Key"):
                st.session_state.api_key = ""
                st.rerun()

    # KẾT NỐI & TỰ DÒ MODEL
    active_model_name = "Chưa kết nối"
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        genai.configure(api_key=api_key)
        
        # Gọi hàm dò tìm model ngay khi có Key
        try:
            found_model = get_best_available_model()
            # Bỏ tiền tố 'models/' nếu cần thiết để hiển thị đẹp
            active_model_name = found_model.replace("models/", "")
        except:
            active_model_name = "Error Detecting"

    st.markdown("---")
    st.caption(f"🤖 **Active Core:** `{active_model_name}`")
    
    # Chế độ (Giờ chỉ là UI, vì Core đã tự chọn cái tốt nhất)
    mode = st.radio("Chế độ:", ["🔴 Auto-Router (Best Available)", "⚪ Code Audit", "⚪ Vision Analysis"])


# --- 5. GIAO DIỆN CHÍNH ---
st.title("👁 TITAN VISION ENGINE v5.0")
st.caption("Strategic Partner Edition - Auto Discovery Protocol")

col_input, col_output = st.columns([1, 1], gap="medium")

with col_input:
    st.subheader("📥 Dữ liệu đầu vào")
    user_prompt = st.text_area("Nhập Prompt / Câu hỏi:", height=200)
    uploaded_file = st.file_uploader("Tải ảnh (nếu có):", type=["jpg", "png", "jpeg"])
    
    image_data = None
    if uploaded_file:
        image_data = Image.open(uploaded_file)
        st.image(image_data, caption="Preview", use_column_width=True)

    run_btn = st.button("🚀 KÍCH HOẠT TITAN", type="primary")

# --- 6. XỬ LÝ LOGIC (AN TOÀN TUYỆT ĐỐI) ---
with col_output:
    st.subheader("💎 Kết quả phân tích")
    
    if run_btn:
        if not api_key:
            st.error("⛔ Vui lòng nhập API Key!")
        else:
            status_box = st.empty()
            
            try:
                with st.spinner(f"🚀 Đang chạy trên core: {active_model_name}..."):
                    
                    # CẤU HÌNH MODEL TỪ KẾT QUẢ DÒ TÌM
                    # Lưu ý: Một số model cũ không hỗ trợ 'tools', nên ta dùng try-except để cấu hình
                    try:
                        model = genai.GenerativeModel(
                            model_name=active_model_name,
                            tools='google_search_retrieval' # Thử bật Search
                        )
                    except:
                        # Nếu bật Search lỗi (do model cũ), tắt Search đi
                        model = genai.GenerativeModel(model_name=active_model_name)

                    # CHUẨN BỊ INPUT
                    input_content = []
                    if user_prompt: input_content.append(user_prompt)
                    if image_data: input_content.append(image_data)
                    
                    # GỌI API
                    response = model.generate_content(input_content)
                    
                    # HIỂN THỊ KẾT QUẢ
                    status_box.success(f"✅ Thành công! (Core: {active_model_name})")
                    st.markdown(response.text)
                    
                    # HIỂN THỊ NGUỒN (Nếu có)
                    if hasattr(response, 'candidates') and response.candidates:
                         # Check an toàn các thuộc tính sâu bên trong
                         c = response.candidates[0]
                         if hasattr(c, 'grounding_metadata') and c.grounding_metadata.search_entry_point:
                             st.markdown("---")
                             st.caption("🌐 Nguồn dữ liệu:")
                             for chunk in c.grounding_metadata.grounding_chunks:
                                 if chunk.web:
                                     st.markdown(f"- [{chunk.web.title}]({chunk.web.uri})")

            except Exception as e:
                # NẾU VẪN LỖI: In ra danh sách model để debug
                st.error(f"❌ Lỗi xử lý: {str(e)}")
                
                with st.expander("🛠 Debug: Danh sách Model khả dụng của Key này"):
                    try:
                        all_m = genai.list_models()
                        st.write([m.name for m in all_m])
                    except:
                        st.write("Không thể lấy danh sách model (Kiểm tra lại Key/Quyền hạn)")
