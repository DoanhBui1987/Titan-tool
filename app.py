import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN & CSS (CLEAN UI)
# ==========================================
st.set_page_config(page_title="TITAN GENESIS", page_icon="🌌", layout="wide")

# CSS để làm đẹp và ẩn hiện mượt mà
st.markdown("""
<style>
    /* Tùy chỉnh nút bấm */
    .stButton>button {
        background-color: #FF4B4B; 
        color: white; 
        border-radius: 8px;
        font-weight: bold;
    }
    /* Làm gọn Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #0E1117;
    }
    /* Ẩn bớt các element thừa của Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Style cho Dev Mode Panel */
    .debug-box {
        background-color: #1a1c24;
        border: 1px solid #444;
        padding: 10px;
        border-radius: 5px;
        color: #00ff88;
        font-family: monospace;
        font-size: 0.8em;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. QUẢN LÝ TRẠNG THÁI (SESSION STATE)
# ==========================================
# Giúp lưu lại Key và Kết quả khi bấm nút mà không bị reset
if 'api_key' not in st.session_state:
    st.session_state['api_key'] = ''
if 'result' not in st.session_state:
    st.session_state['result'] = ''

# ==========================================
# 3. SIDEBAR: TRUNG TÂM ĐIỀU KHIỂN
# ==========================================
with st.sidebar:
    st.title("🌌 TITAN CONTROL")
    
    # --- KHU VỰC API KEY (Tự động lưu tạm thời) ---
    with st.expander("🔑 Cấu hình hệ thống", expanded=not st.session_state['api_key']):
        input_key = st.text_input(
            "Google API Key", 
            type="password", 
            value=st.session_state['api_key'],
            placeholder="Dán key vào đây...",
            help="Key sẽ được lưu trong phiên làm việc này."
        )
        if input_key:
            st.session_state['api_key'] = input_key
            st.success("🟢 System Ready")
        else:
            st.warning("🔴 Chưa có Key")
            st.markdown("[👉 Lấy Key miễn phí tại đây](https://aistudio.google.com/app/apikey)")

    st.markdown("---")

    # --- CHẾ ĐỘ HOẠT ĐỘNG ---
    mode = st.radio(
        "Chọn vai trò:", 
        ["Free Chat (Trò chuyện)", "Content Creator (Sáng tạo)", "Code Audit (Kỹ thuật)"],
        index=0
    )

    st.markdown("---")

    # --- NẠP KIẾN THỨC (RAG) ---
    st.write("📚 **Bộ Nhớ Tạm (RAG)**")
    rag_files = st.file_uploader("Nạp tài liệu để TITAN học", accept_multiple_files=True, label_visibility="collapsed")

    st.markdown("---")

    # --- NÚT GẠT DEV MODE (Theo yêu cầu của bạn) ---
    # Đẩy xuống dưới cùng
    st.markdown("<br>" * 3, unsafe_allow_html=True) # Tạo khoảng trống
    dev_mode = st.toggle("🛠️ Dev Mode (Chế độ gỡ lỗi)", value=False)

# ==========================================
# 4. LOGIC XỬ LÝ (CORE ENGINE)
# ==========================================
def call_titan(key, text, img, context, mode):
    if not key: return "⚠️ Vui lòng nhập API Key ở menu bên trái!"
    
    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Tạo Prompt thông minh theo chế độ
        sys_prompt = "Bạn là TITAN - Trợ lý AI cao cấp."
        if mode == "Content Creator": 
            sys_prompt += " Hãy viết nội dung thu hút, viral, giọng văn tự nhiên."
        elif mode == "Code Audit":
            sys_prompt += " Hãy soi lỗi code kỹ, giải thích nguyên nhân và sửa lại."
            
        prompt_parts = [f"SYSTEM: {sys_prompt}\nCHẾ ĐỘ: {mode}\n"]
        
        if context:
            prompt_parts.append(f"DỮ LIỆU THAM KHẢO:\n{context}\n")
            
        prompt_parts.append(f"USER YÊU CẦU:\n{text}")
        if img: prompt_parts.append(img)
        
        response = model.generate_content(prompt_parts)
        return response.text
    except Exception as e:
        return f"🔥 LỖI HỆ THỐNG: {str(e)}"

# ==========================================
# 5. GIAO DIỆN CHÍNH (MAIN UI)
# ==========================================
st.title("🌌 TITAN GENESIS ENGINE")

# Hiển thị thông báo chào mừng nếu chưa có kết quả
if not st.session_state['result']:
    st.caption("🚀 Ready to deploy. Waiting for command...")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📥 Input Data")
    user_text = st.text_area("Nhập nội dung/ý tưởng...", height=250)
    user_img = st.file_uploader("🖼️ Vision Input", type=['png', 'jpg', 'jpeg'])
    
    # Nút kích hoạt
    if st.button("✨ KÍCH HOẠT TITAN", use_container_width=True):
        if not st.session_state['api_key']:
            st.error("❌ Chưa nhập API Key!")
        elif not user_text and not user_img:
            st.warning("⚠️ Nhập gì đó đi chứ!")
        else:
            with st.spinner("⚡ TITAN đang xử lý..."):
                # Xử lý RAG
                rag_context = ""
                if rag_files:
                    for f in rag_files:
                        try: rag_context += f.getvalue().decode("utf-8") + "\n"
                        except: pass
                
                # Gọi AI
                img_obj = Image.open(user_img) if user_img else None
                result = call_titan(st.session_state['api_key'], user_text, img_obj, rag_context, mode)
                st.session_state['result'] = result
                st.rerun() # Load lại để hiện kết quả

with col2:
    st.subheader("📤 Refined Output")
    
    # Khu vực hiển thị kết quả
    if st.session_state['result']:
        # Nếu có lỗi, hiện màu đỏ
        if "🔥 LỖI" in st.session_state['result']:
             st.error(st.session_state['result'])
        else:
             st.markdown(st.session_state['result'])
             st.download_button("💾 Tải kết quả (.md)", st.session_state['result'], "titan_output.md")
    
    # --- KHU VỰC DEBUG (CHỈ HIỆN KHI BẬT DEV MODE) ---
    if dev_mode:
        st.markdown("---")
        st.markdown('<div class="debug-box">', unsafe_allow_html=True)
        st.write("🔧 **DEV MODE: SYSTEM LOGS**")
        st.write(f"- Mode: `{mode}`")
        st.write(f"- API Key Status: `{'Set' if st.session_state['api_key'] else 'Missing'}`")
        st.write(f"- RAG Files Loaded: `{len(rag_files) if rag_files else 0}`")
        if user_img: st.write("- Vision Input: `Detected`")
        st.markdown('</div>', unsafe_allow_html=True)
