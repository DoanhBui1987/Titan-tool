import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. CẤU HÌNH GIAO DIỆN
st.set_page_config(page_title="TITAN CHECK KEY", page_icon="🔑")

st.title("🔑 KIỂM TRA API KEY & KẾT NỐI")

# 2. KHU VỰC NHẬP KEY (CÓ BÁO TRẠNG THÁI)
st.info("Bước 1: Nhập API Key lấy từ aistudio.google.com")

# Lấy key từ secrets hoặc nhập tay
api_key = st.text_input("Dán API Key vào đây (Bắt đầu bằng AIza...):", type="password")

# --- ĐÂY LÀ PHẦN TRẢ LỜI CÂU HỎI CỦA BẠN ---
if api_key:
    st.success("✅ ĐÃ NHẬN KEY! (Hệ thống đã lưu, hãy bấm nút Test bên dưới)")
    if not api_key.startswith("AIza"):
        st.warning("⚠️ Cảnh báo: Key này trông lạ lắm (thường phải bắt đầu bằng 'AIza'). Kiểm tra lại nhé.")
else:
    st.warning("Waiting... (Chưa nhập Key)")

st.divider()

# 3. NÚT TEST KẾT NỐI RIÊNG BIỆT
st.info("Bước 2: Bấm nút dưới để xem Key này có dùng được Gemini 1.5 Flash không")

if st.button("🔌 KÍCH HOẠT TEST KẾT NỐI", type="primary"):
    if not api_key:
        st.error("Chưa có Key sao mà test được sếp ơi!")
    else:
        status_box = st.status("Đang kết nối tới Google...", expanded=True)
        try:
            # Cấu hình
            genai.configure(api_key=api_key)
            status_box.write("📡 Đã cấu hình xong. Đang gọi thử Gemini 1.5 Flash...")
            
            # Gọi thử model
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content("Chào Titan, bạn có khỏe không?")
            
            status_box.update(label="✅ KẾT NỐI THÀNH CÔNG!", state="complete", expanded=True)
            st.balloons()
            st.success("Tuyệt vời! Key này xịn. Model trả lời: ")
            st.write(f"🤖 AI: {response.text}")
            
        except Exception as e:
            status_box.update(label="❌ KẾT NỐI THẤT BẠI", state="error", expanded=True)
            st.error(f"Lỗi chi tiết: {str(e)}")
            
            # Phân tích lỗi giúp bạn
            err_msg = str(e)
            if "404" in err_msg:
                st.markdown("""
                ### 🛑 LỖI 404: KHÔNG TÌM THẤY MODEL
                **Nguyên nhân:** Key này của bạn là Key cũ hoặc Key của dự án Google Cloud chưa bật quyền.
                **Cách sửa:** 1. Vào [Google AI Studio](https://aistudio.google.com/app/apikey)
                2. Tạo Key mới trong **New Project**.
                """)
            elif "429" in err_msg:
                st.error("Lỗi 429: Hết tiền/Hết lượt dùng (Quota Exceeded). Đổi Key khác.")
            elif "400" in err_msg:
                st.error("Lỗi 400: Key sai hoàn toàn. Copy thiếu chữ cái nào không?")
