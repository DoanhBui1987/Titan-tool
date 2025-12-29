import streamlit as st
import google.generativeai as genai
from PIL import Image

# ==========================================
# 1. CẤU HÌNH TRANG & GIAO DIỆN
# ==========================================
st.set_page_config(
    page_title="TITAN VISION ENGINE v4.0",
    page_icon="👁️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        height: 3em;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("👁️ TITAN VISION ENGINE v4.0")
st.caption("Từ Ý tưởng đến Đế chế - Powered by Gemini 1.5 Flash")

# ==========================================
# 2. CẤU HÌNH API & SIDEBAR
# ==========================================
with st.sidebar:
    st.header("⚙️ Cấu hình")
    # Lấy API Key từ Secrets hoặc nhập tay
    if 'GOOGLE_API_KEY' in st.secrets:
        api_key = st.secrets['GOOGLE_API_KEY']
        st.success("✅ Đã nạp API Key từ hệ thống")
    else:
        api_key = st.text_input("🔑 Nhập Google API Key", type="password")
        st.info("💡 Mẹo: Cài đặt API Key trong Streamlit Secrets để không phải nhập lại.")
    
    mode = st.radio(
        "Chế độ vận hành:",
        ["Auto-Router (Tự động)", "Vision Analysis (Phân tích ảnh)", "Code Audit (Soi code)"]
    )
    
    # Nút kiểm tra model (Debug)
    if st.button("🔍 Kiểm tra Model khả dụng"):
        if not api_key:
            st.error("Vui lòng nhập API Key trước!")
        else:
            try:
                genai.configure(api_key=api_key)
                models = [m.name for m in genai.list_models()]
                st.write(models)
            except Exception as e:
                st.error(f"Lỗi: {e}")
    
    st.markdown("---")
    st.markdown("### 📝 Hướng dẫn")
    st.markdown("1. Nhập Text hoặc Tải ảnh lên.")
    st.markdown("2. Bấm **KÍCH HOẠT TITAN**.")
    st.markdown("3. Tải kết quả về máy.")

# ==========================================
# 3. BỘ NÃO TITAN (SYSTEM INSTRUCTION)
# ==========================================
TITAN_SYSTEM_INSTRUCTION = """
ROLE: Bạn là TITAN - Hệ thống tinh chế Đa phương thức (Multimodal Refinery).
MISSION: Phân tích Input (Văn bản hoặc Hình ảnh) và đưa ra giải pháp tối ưu nhất.

OUTPUT FORMAT (MARKDOWN):
---
## 🎯 THE VERDICT
- **One-Liner:** [Nhận xét sắc bén]

## 🛠️ DEEP DIVE
- **Analysis:** [Phân tích chi tiết]

## 🚀 ACTION PLAN
- **Step 1:** [Làm gì?]

## 💎 THE REFINED ARTIFACT
(Code sửa lỗi hoặc Prompt, nội dung đã tối ưu)
""" 

# ==========================================
# 4. GIAO DIỆN CHÍNH
# ==========================================
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📥 Input Data")
    input_text = st.text_area("Mô tả ý tưởng / Paste Code / Câu hỏi:", height=200, placeholder="Ví dụ: Phân tích giao diện này và viết lại code HTML...")
    uploaded_file = st.file_uploader("Tải ảnh lên (Optional)", type=["jpg", "png", "jpeg"])
    
    image_data = None
    if uploaded_file is not None:
        image_data = Image.open(uploaded_file)
        st.image(image_data, caption="Ảnh đã tải lên", use_container_width=True)

    # ĐÂY LÀ DÒNG TẠO NÚT BẤM (QUAN TRỌNG)
    btn_submit = st.button("✨ KÍCH HOẠT TITAN")

with col2:
    st.subheader("💎 Titan Output")
    output_placeholder = st.empty()

    if btn_submit:
        if not api_key:
            st.error("⚠️ Vui lòng nhập API Key!")
        else:
            try:
                with st.spinner("📡 TITAN đang quét dữ liệu..."):
                    # Cấu hình Gemini
                    genai.configure(api_key=api_key)
                    
                    # Tên model chuẩn nhất
                    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=TITAN_SYSTEM_INSTRUCTION)
                    
                    # Chuẩn bị input
                    prompt_parts = [f"CHẾ ĐỘ: {mode}\n\nINPUT USER:\n{input_text}"]
                    if image_data:
                        prompt_parts.append(image_data)
                        prompt_parts[0] += "\n\n(CÓ ẢNH ĐÍNH KÈM)"
                    
                    # Gọi API
                    response = model.generate_content(prompt_parts)
                    result_text = response.text
                    
                    # Hiển thị kết quả
                    output_placeholder.markdown(result_text)
                    
                    # Tạo nút tải xuống
                    st.download_button(
                        label="💾 Tải báo cáo (.md)",
                        data=result_text,
                        file_name="Titan_Report.md",
                        mime="text/markdown"
                    )

            except Exception as e:
                st.error(f"🔥 LỖI HỆ THỐNG: {str(e)}")
