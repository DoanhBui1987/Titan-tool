import streamlit as st
import os

# --- CẤU HÌNH SIDEBAR ---
with st.sidebar:
    st.header("⚙ Trung tâm điều khiển")
    
    # --- PHẦN 1: MENU CHÍNH ---
    # Thay vì để API Key chình ình ở đây, ta đưa Menu lên trước
    mode = st.radio(
        "Chế độ:", 
        ["🔴 Auto-Router", "⚪ Vision Analysis", "⚪ Code Audit"],
        index=0
    )
    
    st.markdown("---") # Đường kẻ ngang phân cách

    # --- PHẦN 2: QUẢN LÝ API KEY THÔNG MINH ---
    # Logic: Ưu tiên lấy từ secrets.toml -> Nếu không có thì mới hiện ô nhập
    
    api_key = None
    
    # Check 1: Lấy từ secrets (Cách tối ưu nhất, không cần nhập lại bao giờ)
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("🟢 System Ready (Key from Secrets)")
    else:
        # Check 2: Lấy từ Session (Lỡ người dùng nhập rồi nhưng F5 lại trang)
        if "api_key" not in st.session_state:
            st.session_state.api_key = ""

        if not st.session_state.api_key:
            # Nếu chưa có key ở đâu cả -> Hiện ô nhập
            user_input_key = st.text_input(
                "Google API Key", 
                type="password", 
                placeholder="Paste key & Enter...",
                help="Nhập key vào đây để chạy session tạm thời."
            )
            if user_input_key:
                st.session_state.api_key = user_input_key
                st.rerun() # Load lại trang để nhận key
        else:
            # Đã có key trong session
            api_key = st.session_state.api_key
            col1, col2 = st.columns([4, 1])
            with col1:
                st.info("🟢 System Ready")
            with col2:
                # Nút Reset để nhập lại nếu muốn
                if st.button("🔄", help="Đổi Key khác"):
                    st.session_state.api_key = ""
                    st.rerun()
            
            # Gợi ý người dùng tạo file secrets để đỡ nhập
            st.caption("💡 Mẹo: Tạo file `.streamlit/secrets.toml` để không phải nhập lại.")

    # Gán key vào biến môi trường để các thư viện AI sử dụng
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key


    # --- PHẦN 3: DEBUG INFO (TÍNH NĂNG ẨN) ---
    st.markdown("---")
    
    # Sử dụng st.expander để mặc định ẩn đi, bấm vào mới hiện
    with st.expander("🛠 Debug thông tin Model", expanded=False):
        if api_key:
            # Giả lập hoặc lấy list model thật
            st.json({
                "0": "models/embedding-gecko-001",
                "1": "models/gemini-2.5-flash",
                "2": "models/gemini-2.5-pro",
                "3": "models/gemini-2.0-flash-exp"
            })
            st.write("Latency: 45ms")
            st.write("Token usage: 1250")
        else:
            st.error("Chưa kết nối API")

# --- KẾT THÚC SIDEBAR ---
