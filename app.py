if btn_submit:
        if not api_key:
            st.error("⚠️ Vui lòng nhập API Key!")
        else:
            try:
                with st.spinner("📡 TITAN đang quét dữ liệu..."):
                    # Cấu hình Gemini
                    genai.configure(api_key=api_key)
                    
                    # --- DÒNG BẠN VỪA SỬA (Đã căn lề chuẩn) ---
                    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=TITAN_SYSTEM_INSTRUCTION)
                    # -------------------------------------------
                    
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
# Thêm vào trong with st.sidebar:
if st.button("🔍 Kiểm tra Model khả dụng"):
    try:
        genai.configure(api_key=api_key)
        models = [m.name for m in genai.list_models()]
        st.write(models)
    except Exception as e:
        st.error(f"Lỗi check model: {e}")
