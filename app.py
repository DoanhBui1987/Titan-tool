import streamlit as st
import requests
import json
import base64
from PIL import Image
import io

# ==============================================================================
# MODULE 1: CẤU HÌNH & GIAO DIỆN HỆ THỐNG
# ==============================================================================
st.set_page_config(
    page_title="TITAN VISION X (Final Stable)",
    page_icon="🧿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS cho giao diện chuyên nghiệp hơn
st.markdown("""
<style>
    .stButton>button {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        color: white;
        border: none;
        height: 3.5em;
        font-weight: bold;
        border-radius: 8px;
        font-size: 16px;
    }
    .stButton>button:hover {
        opacity: 0.9;
        transform: scale(1.01);
    }
    .stTextArea textarea {
        background-color: #f0f2f6;
        color: #000;
        border-radius: 8px;
    }
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    h1, h2, h3 { color: #182848; }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# MODULE 2: CÁC HÀM XỬ LÝ LOGIC (BACKEND)
# ==============================================================================

def encode_image(image_file):
    """Chuyển đổi file ảnh sang Base64 và xác định Mime Type"""
    if image_file is not None:
        try:
            # Lấy mime type thực tế (quan trọng để fix lỗi mù ảnh)
            mime_type = image_file.type
            
            # Đọc file và chuyển sang bytes
            image_instance = Image.open(image_file)
            img_byte_arr = io.BytesIO()
            # Lưu lại vào buffer để lấy bytes, giữ nguyên định dạng gốc
            image_instance.save(img_byte_arr, format=image_instance.format)
            encoded_string = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
            
            return {"mime_type": mime_type, "data": encoded_string}
        except Exception as e:
            st.error(f"Lỗi xử lý ảnh: {e}")
            return None
    return None

def read_text_file(txt_file):
    """Đọc nội dung file text/code để làm context"""
    if txt_file is not None:
        try:
            stringio = io.StringIO(txt_file.getvalue().decode("utf-8"))
            return stringio.read()
        except Exception as e:
            st.warning(f"Không đọc được file {txt_file.name}: {e}")
            return ""
    return ""

def call_gemini_rest_api(api_key, model, prompt, image_data=None, system_instruction=None):
    """Hàm lõi gọi Google REST API (Không dùng thư viện trung gian)"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}

    # 1. Xây dựng System Prompt (Nếu có)
    final_prompt = prompt
    if system_instruction:
        final_prompt = f"{system_instruction}\n\n---\nUSER REQUEST:\n{prompt}"

    # 2. Xây dựng Content Parts
    parts = []
    
    # Nếu có ảnh, đưa ảnh vào trước
    if image_data:
        parts.append({
            "inline_data": {
                "mime_type": image_data['mime_type'],
                "data": image_data['data']
            }
        })
    
    # Đưa text vào sau
    parts.append({"text": final_prompt})

    # 3. Đóng gói Payload
    payload = {
        "contents": [{
            "parts": parts
        }]
    }

    # 4. Gửi Request
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            return {
                "success": True, 
                "text": response.json()['candidates'][0]['content']['parts'][0]['text']
            }
        else:
            return {
                "success": False, 
                "error_code": response.status_code,
                "detail": response.text
            }
    except Exception as e:
        return {"success": False, "detail": str(e)}

# ==============================================================================
# MODULE 3: SIDEBAR & CẤU HÌNH (CONTROLLER)
# ==============================================================================

with st.sidebar:
    st.title("⚙️ TRUNG TÂM ĐIỀU KHIỂN")
    
    # 1. Quản lý API Key
    st.subheader("1. API Key")
    if 'GOOGLE_API_KEY' in st.secrets:
        api_key = st.secrets['GOOGLE_API_KEY']
        st.success("✅ Đã nạp Key bảo mật từ hệ thống")
    else:
        api_key = st.text_input("Nhập Google API Key:", type="password", help="Lấy tại aistudio.google.com")

    st.divider()

    # 2. Chọn Model (Model Hunter Logic)
    st.subheader("2. Chọn Bộ Não AI")
    # Danh sách dự phòng nếu không fetch được
    model_options = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"]
    
    # Nút làm mới danh sách
    if st.button("🔄 Quét Model khả dụng"):
        if api_key:
            try:
                resp = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}")
                if resp.status_code == 200:
                    data = resp.json()
                    fetched_models = []
                    for m in data.get('models', []):
                        if "generateContent" in m.get('supportedGenerationMethods', []):
                            fetched_models.append(m['name'].replace("models/", ""))
                    # Ưu tiên đưa 2.0 lên đầu
                    fetched_models.sort(key=lambda x: "2.0" in x, reverse=True)
                    model_options = fetched_models
                    st.toast(f"Tìm thấy {len(fetched_models)} models!", icon="🎉")
            except:
                st.warning("Không quét được, dùng danh sách mặc định.")
    
    selected_model = st.selectbox("Model đang dùng:", model_options)

    st.divider()

    # 3. Chế độ (Personas - Khôi phục tính năng đã mất)
    st.subheader("3. Chế độ hoạt động")
    mode = st.radio(
        "Chọn vai trò:",
        ["Trợ lý Đa năng", "Chuyên gia Code (Audit)", "Sáng tạo (Marketing)", "Phân tích Dữ liệu"]
    )
    
    # Mapping system instruction
    system_prompts = {
        "Trợ lý Đa năng": "Bạn là trợ lý AI hữu ích, trả lời ngắn gọn, đi thẳng vào vấn đề.",
        "Chuyên gia Code (Audit)": "Bạn là Senior Software Engineer. Nhiệm vụ: Review code, tìm bug, giải thích logic, tối ưu hóa và viết docstring. Chỉ dùng Markdown cho code.",
        "Sáng tạo (Marketing)": "Bạn là Copywriter chuyên nghiệp. Giọng văn: Thu hút, viral, cảm xúc. Dùng emoji hợp lý.",
        "Phân tích Dữ liệu": "Bạn là Data Analyst. Phân tích dữ liệu/hình ảnh đầu vào, tìm ra insight, xu hướng và trình bày dưới dạng bullet point rõ ràng."
    }
    current_instruction = system_prompts[mode]

# ==============================================================================
# MODULE 4: GIAO DIỆN CHÍNH (VIEW)
# ==============================================================================

st.title("🧿 TITAN VISION X")
st.caption(f"Powered by **{selected_model}** | Mode: **{mode}**")

col_left, col_right = st.columns([1, 1])

# --- INPUT AREA ---
with col_left:
    st.subheader("📥 Dữ liệu đầu vào")
    
    # Tab chọn loại input
    tab1, tab2 = st.tabs(["💬 Văn bản & Ảnh", "📄 Tệp đính kèm (RAG Lite)"])
    
    with tab1:
        user_text = st.text_area("Nhập câu lệnh/Prompt:", height=150, placeholder="Ví dụ: Giải thích đoạn code này, hoặc Mô tả bức ảnh...")
        uploaded_img = st.file_uploader("Tải ảnh (Vision):", type=["png", "jpg", "jpeg", "webp", "heic"])
        
        # Preview ảnh
        processed_img_data = None
        if uploaded_img:
            st.image(uploaded_img, caption="Ảnh Input", use_container_width=True)
            processed_img_data = encode_image(uploaded_img)

    with tab2:
        st.info("Tải file code/text để AI đọc hiểu (Tối đa 2MB)")
        uploaded_txt = st.file_uploader("Chọn file (.txt, .py, .md, .json):", type=["txt", "py", "md", "json", "csv"])
        file_context = ""
        if uploaded_txt:
            file_context = read_text_file(uploaded_txt)
            with st.expander("Xem nội dung file đã đọc"):
                st.code(file_context)

    # Nút Action (Đặt ở ngoài tab để luôn bấm được)
    st.markdown("---")
    btn_submit = st.button("🚀 KÍCH HOẠT TITAN", use_container_width=True)

# --- OUTPUT AREA ---
with col_right:
    st.subheader("💎 Kết quả")
    
    if btn_submit:
        if not api_key:
            st.error("⚠️ CHƯA CÓ CHÌA KHÓA: Vui lòng nhập API Key ở menu bên trái!")
        elif not user_text and not processed_img_data and not file_context:
            st.warning("⚠️ Vui lòng nhập nội dung hoặc tải ảnh/file!")
        else:
            with st.spinner("⏳ TITAN đang suy nghĩ..."):
                # Ghép Context từ file vào Prompt
                full_prompt = user_text
                if file_context:
                    full_prompt = f"CONTEXT DATA:\n{file_context}\n\n---\nQUESTION:\n{user_text}"
                
                # Gọi hàm xử lý
                result = call_gemini_rest_api(
                    api_key=api_key,
                    model=selected_model,
                    prompt=full_prompt,
                    image_data=processed_img_data,
                    system_instruction=current_instruction
                )
                
                # Hiển thị kết quả
                if result["success"]:
                    st.success("✅ Hoàn tất!")
                    st.markdown(result["text"])
                    
                    # Nút Copy/Download
                    st.download_button(
                        label="💾 Tải kết quả (.md)",
                        data=result["text"],
                        file_name="titan_output.md",
                        mime="text/markdown"
                    )
                else:
                    st.error("🔥 CÓ LỖI XẢY RA!")
                    st.json(result) # Hiển thị chi tiết lỗi JSON để debug
