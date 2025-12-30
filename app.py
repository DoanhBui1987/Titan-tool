import streamlit as st
import requests
import json
import base64
from PIL import Image
import io

# ==============================================================================
# CẤU HÌNH CƠ BẢN (KHÔNG CSS MÀU MÈ)
# ==============================================================================
st.set_page_config(
    page_title="TITAN VISION (Clean UI)",
    page_icon="🧿",
    layout="wide"
)

# Chỉ giữ lại CSS cho nút bấm to rõ, bỏ hết can thiệp màu chữ/nền
st.markdown("""
<style>
    .stButton>button {
        height: 3em;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# LOGIC BACKEND (GIỮ NGUYÊN VÌ ĐÃ CHẠY ĐƯỢC)
# ==============================================================================

def encode_image(image_file):
    if image_file is not None:
        try:
            mime_type = image_file.type
            image_instance = Image.open(image_file)
            img_byte_arr = io.BytesIO()
            image_instance.save(img_byte_arr, format=image_instance.format)
            encoded_string = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
            return {"mime_type": mime_type, "data": encoded_string}
        except Exception as e:
            st.error(f"Lỗi ảnh: {e}")
            return None
    return None

def read_text_file(txt_file):
    if txt_file is not None:
        try:
            stringio = io.StringIO(txt_file.getvalue().decode("utf-8"))
            return stringio.read()
        except Exception:
            return ""
    return ""

def call_gemini_rest_api(api_key, model, prompt, image_data=None, system_instruction=None):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}

    final_prompt = prompt
    if system_instruction:
        final_prompt = f"{system_instruction}\n\n---\nUSER REQUEST:\n{prompt}"

    parts = []
    if image_data:
        parts.append({
            "inline_data": {
                "mime_type": image_data['mime_type'],
                "data": image_data['data']
            }
        })
    parts.append({"text": final_prompt})

    payload = {"contents": [{"parts": parts}]}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            return {"success": True, "text": response.json()['candidates'][0]['content']['parts'][0]['text']}
        else:
            return {"success": False, "detail": response.text}
    except Exception as e:
        return {"success": False, "detail": str(e)}

# ==============================================================================
# GIAO DIỆN (ĐÃ BỎ CÁC CLASS GÂY LỖI MÙ CHỮ)
# ==============================================================================

with st.sidebar:
    st.header("CẤU HÌNH") # Dùng header chuẩn, không chỉnh màu
    
    # 1. API Key
    if 'GOOGLE_API_KEY' in st.secrets:
        api_key = st.secrets['GOOGLE_API_KEY']
        st.success("Đã có Key hệ thống")
    else:
        api_key = st.text_input("Nhập API Key:", type="password")

    st.divider()

    # 2. Chọn Model
    st.subheader("Chọn Model")
    model_options = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"]
    
    if st.button("Quét Model"):
        if api_key:
            try:
                resp = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}")
                if resp.status_code == 200:
                    data = resp.json()
                    fetched = [m['name'].replace("models/", "") for m in data.get('models', []) if "generateContent" in m.get('supportedGenerationMethods', [])]
                    fetched.sort(key=lambda x: "2.0" in x, reverse=True)
                    model_options = fetched
                    st.success(f"Tìm thấy {len(fetched)} model")
            except:
                pass
    
    selected_model = st.selectbox("Danh sách:", model_options)

    st.divider()

    # 3. Chế độ
    st.subheader("Chế độ")
    mode = st.radio(
        "Vai trò:",
        ["Trợ lý Đa năng", "Code Audit", "Marketing", "Data Analyst"]
    )
    
    prompts = {
        "Trợ lý Đa năng": "Bạn là trợ lý AI hữu ích.",
        "Code Audit": "Bạn là Senior Developer. Review code, tìm bug, tối ưu.",
        "Marketing": "Bạn là Copywriter. Viết nội dung thu hút.",
        "Data Analyst": "Phân tích dữ liệu và đưa ra insight."
    }
    instruction = prompts[mode]

# --- MAIN ---
st.title(f"TITAN VISION ({selected_model})")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Input")
    tab1, tab2 = st.tabs(["Văn bản & Ảnh", "File Text"])
    
    with tab1:
        user_text = st.text_area("Nội dung:", height=150)
        uploaded_img = st.file_uploader("Ảnh:", type=["png", "jpg", "jpeg", "webp"])
        processed_img = encode_image(uploaded_img)
        if processed_img:
            st.image(uploaded_img, width=200)

    with tab2:
        uploaded_txt = st.file_uploader("File Text/Code:", type=["txt", "py", "md"])
        file_ctx = read_text_file(uploaded_txt)
        if file_ctx:
            st.info("Đã đọc file")

    st.markdown("---")
    if st.button("CHẠY (RUN)", type="primary", use_container_width=True):
        if not api_key:
            st.error("Thiếu API Key")
        else:
            with st.spinner("Đang chạy..."):
                full_prompt = f"CONTEXT:\n{file_ctx}\nUSER:\n{user_text}" if file_ctx else user_text
                
                res = call_gemini_rest_api(api_key, selected_model, full_prompt, processed_img, instruction)
                
                if res["success"]:
                    st.session_state['last_result'] = res["text"]
                else:
                    st.error(res["detail"])

with col2:
    st.subheader("Output")
    if 'last_result' in st.session_state:
        st.markdown(st.session_state['last_result'])
