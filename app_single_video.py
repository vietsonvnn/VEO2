#!/usr/bin/env python3
"""
VEO 3.1 - Single Video Generator
Tạo 1 video đơn lẻ với Veo 3.1 Fast
"""
import gradio as gr
import asyncio
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from browser_automation.flow_controller import FlowController

# Default project ID
DEFAULT_PROJECT_ID = "125966c7-418b-49da-9978-49f0a62356de"

async def create_single_video(prompt, project_id, cookies_path, progress=gr.Progress()):
    """Create a single video with Veo 3.1 Fast"""
    log = []

    try:
        if not prompt or not prompt.strip():
            return "❌ Vui lòng nhập prompt để tạo video", None

        log.append("="*60)
        log.append("🎬 BẮT ĐẦU TẠO VIDEO")
        log.append("="*60)
        log.append(f"📝 Prompt: {prompt[:100]}...")
        log.append(f"🎨 Model: Veo 3.1 - Fast")
        log.append("="*60)
        log.append("")

        progress(0.1, desc="🚀 Khởi động browser...")
        controller = FlowController(cookies_path=cookies_path, headless=False)

        log.append("🚀 Đang khởi động browser...")
        await controller.start()
        log.append("✅ Browser đã khởi động")

        progress(0.2, desc="🌐 Đang vào Flow...")
        log.append("🌐 Đang vào trang Flow...")
        await controller.goto_flow()
        log.append("✅ Đã vào trang Flow")
        log.append("")

        # Use provided project ID or default
        pid = project_id.strip() if project_id and project_id.strip() else DEFAULT_PROJECT_ID

        progress(0.3, desc=f"📁 Đang vào project...")
        log.append(f"📁 Đang vào project: {pid}")
        success = await controller.goto_project(pid)

        if not success:
            log.append("❌ Không thể vào project")
            log.append(f"💡 Thử dùng project mặc định: {DEFAULT_PROJECT_ID}")
            success = await controller.goto_project(DEFAULT_PROJECT_ID)
            if not success:
                await controller.close()
                log.append("❌ THẤT BẠI")
                return "\n".join(log), None

        log.append("✅ Đã vào project")
        log.append("")
        log.append("="*60)

        progress(0.4, desc="🎬 Đang tạo video...")
        log.append("🎬 ĐANG TẠO VIDEO")
        log.append("="*60)
        log.append(f"⏳ Gửi prompt đến Veo 3.1 Fast...")

        # Create video
        video_url = await controller.create_video_from_prompt(
            prompt=prompt,
            aspect_ratio="16:9",
            wait_for_generation=True,
            is_first_video=True
        )

        if video_url:
            progress(1.0, desc="✅ Hoàn thành!")
            log.append("")
            log.append("✅ Video đã tạo xong!")
            log.append("")
            log.append("="*60)
            log.append("📊 KẾT QUẢ")
            log.append("="*60)
            log.append(f"✅ Video có sẵn trên Flow")
            log.append(f"🔗 URL: {video_url}")
            log.append(f"💡 Bạn có thể download manual từ Flow")
            log.append("="*60)

            # Save video info
            video_info = {
                'prompt': prompt,
                'url': video_url,
                'created_at': datetime.now().isoformat(),
                'model': 'Veo 3.1 - Fast'
            }

            await controller.close()
            return "\n".join(log), video_info
        else:
            log.append("")
            log.append("❌ Không thể tạo video")
            log.append("💡 Vui lòng kiểm tra:")
            log.append("   - Prompt có hợp lệ không")
            log.append("   - Cookies còn hiệu lực không")
            log.append("   - Project ID có đúng không")
            log.append("="*60)

            await controller.close()
            return "\n".join(log), None

    except Exception as e:
        log.append("")
        log.append(f"❌ Lỗi: {str(e)}")
        log.append("="*60)
        return "\n".join(log), None

# CSS styling
css = """
.container {
    max-width: 1200px;
    margin: auto;
}
.log-box {
    font-family: 'Monaco', 'Menlo', monospace;
    font-size: 14px;
    line-height: 1.6;
}
"""

# Create Gradio interface
with gr.Blocks(theme=gr.themes.Glass(), css=css, title="VEO 3.1 Single Video") as app:
    gr.Markdown("# 🎬 VEO 3.1 - Single Video Generator")
    gr.Markdown("### Tạo 1 video đơn lẻ với Veo 3.1 Fast")

    with gr.Row():
        with gr.Column(scale=2):
            prompt_input = gr.Textbox(
                label="📝 Video Prompt",
                placeholder="Ví dụ: A beautiful sunset over the ocean with waves gently crashing on the shore",
                lines=5
            )

            with gr.Row():
                project_id_input = gr.Textbox(
                    label="📁 Project ID (Flow)",
                    value=DEFAULT_PROJECT_ID,
                    placeholder="Paste Project ID hoặc để mặc định"
                )

            cookies_input = gr.Textbox(
                label="🍪 Cookie File Path",
                value="./cookie.txt",
                placeholder="./cookie.txt"
            )

            gr.Markdown("""
            ### 💡 Hướng dẫn:
            1. Nhập **prompt** mô tả video bạn muốn tạo
            2. Kiểm tra **Project ID** (mặc định đã được set)
            3. Kiểm tra **cookie.txt** đã có (mặc định `./cookie.txt`)
            4. Click **Tạo Video** và đợi kết quả

            ⚠️ **Lưu ý**:
            - Video sẽ được tạo trên Flow (không download về máy)
            - Bạn có thể download manual từ Flow sau khi tạo xong
            - Mỗi video tốn 1 credit của bạn trên Flow
            """)

            create_btn = gr.Button("🎬 Tạo Video", variant="primary", size="lg")

        with gr.Column(scale=3):
            log_output = gr.Textbox(
                label="📋 Nhật ký tiến trình",
                lines=25,
                max_lines=30,
                elem_classes="log-box",
                interactive=False
            )

            video_info = gr.JSON(
                label="📊 Thông tin Video",
                visible=True
            )

    # Examples
    gr.Examples(
        examples=[
            ["A beautiful sunset over the ocean with waves gently crashing on the shore"],
            ["A chef cooking pasta in a modern kitchen, cinematic lighting"],
            ["A cute puppy playing in the park with autumn leaves falling"],
            ["Time lapse of clouds moving over mountains at sunset"],
            ["Close-up of raindrops falling on a window with city lights blurred in background"]
        ],
        inputs=[prompt_input],
        label="📌 Prompt mẫu"
    )

    # Event handler
    create_btn.click(
        fn=lambda p, pid, c: asyncio.run(create_single_video(p, pid, c)),
        inputs=[prompt_input, project_id_input, cookies_input],
        outputs=[log_output, video_info]
    )

if __name__ == "__main__":
    print("🎬 VEO 3.1 Single Video Generator")
    print("🌐 Starting server at http://localhost:7860")
    print("📖 Tạo 1 video đơn lẻ với Veo 3.1 Fast")
    print("")

    app.queue().launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
