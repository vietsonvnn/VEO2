#!/usr/bin/env python3
"""
VEO 3.1 - Production UI (Final Version)
- Card-based layout như reference
- Log collapsed ở dưới
- API key input
- Duration tùy chỉnh
- Regenerate + Delete buttons
"""

import gradio as gr
import asyncio
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from script_generator.gemini_generator import ScriptGenerator
from browser_automation.flow_controller_selenium import FlowControllerSelenium
from utils.detailed_logger import DetailedLogger
from dotenv import load_dotenv

load_dotenv()

DEFAULT_PROJECT_ID = "7527ed36-b1fb-4728-9cac-e42fc01698c4"
DEFAULT_API_KEY = os.getenv("GEMINI_API_KEY", "")

css = """
.scene-card {
    border: 1px solid #374151;
    border-radius: 12px;
    padding: 20px;
    margin: 12px 0;
    background: #1f2937;
}
.prompt-box {
    font-family: 'Courier New', monospace;
    font-size: 13px;
    background: #111827;
    border: 1px solid #374151;
    border-radius: 8px;
    padding: 12px;
    max-height: 300px;
    overflow-y: auto;
    white-space: pre-wrap;
}
.status-success { color: #10b981; font-weight: bold; }
.status-processing { color: #f59e0b; font-weight: bold; }
.status-failed { color: #ef4444; font-weight: bold; }
.log-box { font-family: 'Courier New', monospace; font-size: 12px; line-height: 1.6; }
"""

class AppState:
    def __init__(self):
        self.script = None
        self.scenes = []
        self.project_id = None
        self.cookies_path = None

state = AppState()

def build_scenes_html():
    """Build card-based HTML for scenes"""
    if not state.scenes:
        return "<p style='text-align: center; color: #9ca3af; padding: 40px;'>Chưa có cảnh nào</p>"

    html = []
    for scene in state.scenes:
        status_class = {
            'completed': 'status-success',
            'processing': 'status-processing',
            'failed': 'status-failed'
        }.get(scene['status'], '')

        status_text = {
            'pending': '⏸️ Chưa tạo',
            'processing': f"⏳ Đang tạo...",
            'completed': '✅ Hoàn thành',
            'failed': '❌ Thất bại'
        }.get(scene['status'], '')

        video_html = ""
        if scene.get('video_path'):
            video_html = f"""
            <video controls style="width: 100%; max-height: 400px; border-radius: 8px; background: #000;">
                <source src="{scene['video_path']}" type="video/mp4">
            </video>
            <p class="status-success" style="margin-top: 8px;">✅ Video đã tạo thành công</p>
            """
        else:
            video_html = f"<div style='text-align: center; padding: 80px; background: #111827; border-radius: 8px;'><p style='font-size: 18px;'>{status_text}</p></div>"

        buttons_html = f"""
        <div style="margin-top: 12px; display: flex; gap: 8px;">
            <button onclick="regenerateScene({scene['number']})" 
                    style="flex: 1; padding: 10px; background: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold;">
                🔄 Tạo lại
            </button>
            <button onclick="deleteScene({scene['number']})" 
                    style="padding: 10px 20px; background: #ef4444; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold;">
                🗑️ Xóa
            </button>
        </div>
        """

        html.append(f"""
        <div class="scene-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <h3 style="margin: 0; color: #f9fafb;">🎬 Phân cảnh {scene['number']}: {scene['description'][:60]}</h3>
                <span class="{status_class}" style="font-size: 16px;">{status_text}</span>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1.5fr; gap: 20px;">
                <div>
                    <h4 style="color: #d1d5db; margin-top: 0;">📝 Prompt cho Video</h4>
                    <div class="prompt-box">{scene['prompt']}</div>
                    {buttons_html}
                </div>
                <div>
                    <h4 style="color: #d1d5db; margin-top: 0;">🎥 Media đã tạo</h4>
                    {video_html}
                </div>
            </div>
        </div>
        """)

    js_script = """
    <script>
    function regenerateScene(num) {
        document.getElementById('regen-scene-num').value = num;
        document.getElementById('regen-btn').click();
    }
    function deleteScene(num) {
        if (confirm('Xóa cảnh ' + num + '?')) {
            document.getElementById('delete-scene-num').value = num;
            document.getElementById('delete-btn').click();
        }
    }
    </script>
    """

    return "\n".join(html) + js_script

async def generate_script_async(topic, duration, api_key, cookies, project_id):
    """Generate script"""
    try:
        if not os.path.exists(cookies):
            return f"❌ Cookie không tồn tại: {cookies}", ""

        if not api_key:
            return "❌ Thiếu API key", ""

        generator = ScriptGenerator(api_key)
        script = generator.generate_script(topic, duration * 60)

        if not script or 'scenes' not in script:
            return "❌ Không thể tạo kịch bản", ""

        state.script = script
        state.scenes = [
            {
                'number': i + 1,
                'description': scene.get('description', f'Scene {i+1}'),
                'prompt': scene.get('prompt', ''),
                'status': 'pending',
                'video_path': None
            }
            for i, scene in enumerate(script['scenes'])
        ]
        state.project_id = project_id or DEFAULT_PROJECT_ID
        state.cookies_path = cookies

        output = f"✅ {script.get('title', 'Kịch bản')}\n📝 {script.get('description', '')}\n🎬 {len(state.scenes)} cảnh"
        return output, build_scenes_html()

    except Exception as e:
        return f"❌ Lỗi: {str(e)}", ""

def produce_all_videos(progress=gr.Progress()):
    """Produce all videos"""
    if not state.scenes:
        return "❌ Chưa có kịch bản!", ""

    log = []
    def add_log(msg):
        log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    add_log("🚀 Bắt đầu sản xuất")
    add_log(f"🎬 Tổng: {len(state.scenes)} cảnh")

    session = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger = DetailedLogger(session_name=session)

    controller = FlowControllerSelenium(cookies_path=state.cookies_path, headless=False)

    try:
        progress(0.05, desc="🚀 Khởi động...")
        controller.start()

        # Use default project ID
        project_id = DEFAULT_PROJECT_ID

        progress(0.1, desc="📁 Vào project...")
        add_log(f"📁 Sử dụng project: {project_id}")

        success = controller.goto_project(project_id)

        if success:
            add_log(f"✅ Đã vào project {project_id}")
            state.project_id = project_id
        else:
            add_log("❌ Không vào được project")
            return state

        add_log("✅ Sẵn sàng tạo video")

        total = len(state.scenes)
        for i, scene in enumerate(state.scenes):
            num = scene['number']
            start = datetime.now()

            add_log(f"🎬 CẢNH {num}/{total}: {scene['description']}")
            scene['status'] = 'processing'

            def cb(elapsed, percent, screenshot):
                progress((0.2 + (i/total)*0.7), desc=f"🎬 {num}/{total} - {percent}%")
                if percent % 20 == 0:
                    add_log(f"   📊 {percent}%")

            try:
                url = controller.create_video_from_prompt(
                    prompt=scene['prompt'],
                    aspect_ratio="16:9",
                    is_first_video=(i==0),
                    progress_callback=cb
                )

                if url:
                    dur = (datetime.now() - start).total_seconds()
                    scene['status'] = 'completed'
                    scene['video_path'] = url
                    add_log(f"   ✅ Hoàn thành ({dur:.1f}s)")
                    logger.scene_complete(num, url, dur)
                else:
                    scene['status'] = 'failed'
                    add_log(f"   ❌ Thất bại")

            except Exception as e:
                scene['status'] = 'failed'
                add_log(f"   ❌ Lỗi: {str(e)}")

        controller.close()
        logger.close()

        completed = sum(1 for s in state.scenes if s['status'] == 'completed')
        add_log(f"🎉 KẾT QUẢ: {completed}/{total} hoàn thành")

        progress(1.0, desc="✅ Xong!")
        return "\n".join(log), build_scenes_html()

    except Exception as e:
        controller.close()
        logger.close()
        add_log(f"❌ Lỗi: {str(e)}")
        return "\n".join(log), build_scenes_html()

def regenerate_scene(scene_num, progress=gr.Progress()):
    """Regenerate scene"""
    try:
        num = int(scene_num)
        if num < 1 or num > len(state.scenes):
            return "❌ Scene không hợp lệ!", ""

        scene = state.scenes[num - 1]
        log = []
        def add_log(msg):
            log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

        add_log(f"🔄 TẠO LẠI CẢNH {num}")

        controller = FlowControllerSelenium(cookies_path=state.cookies_path, headless=False)
        scene['status'] = 'processing'

        progress(0.1, desc="🚀 Khởi động...")
        controller.start()
        controller.goto_flow()
        add_log("✅ Đã vào Flow homepage")

        start = datetime.now()

        def cb(elapsed, percent, screenshot):
            progress(0.3 + (percent/100)*0.6, desc=f"🔄 {percent}%")

        url = controller.create_video_from_prompt(
            prompt=scene['prompt'],
            aspect_ratio="16:9",
            is_first_video=True,
            progress_callback=cb
        )

        if url:
            dur = (datetime.now() - start).total_seconds()
            scene['status'] = 'completed'
            scene['video_path'] = url
            add_log(f"✅ Hoàn thành ({dur:.1f}s)")
        else:
            scene['status'] = 'failed'
            add_log("❌ Thất bại")

        controller.close()
        progress(1.0, desc="✅ Xong!")
        return "\n".join(log), build_scenes_html()

    except Exception as e:
        add_log(f"❌ Lỗi: {str(e)}")
        return "\n".join(log), build_scenes_html()

def delete_scene(scene_num):
    """Delete scene"""
    try:
        num = int(scene_num)
        state.scenes = [s for s in state.scenes if s['number'] != num]
        for i, scene in enumerate(state.scenes):
            scene['number'] = i + 1
        return f"✅ Đã xóa cảnh {num}", build_scenes_html()
    except:
        return "❌ Lỗi xóa", ""

with gr.Blocks(theme=gr.themes.Soft(), css=css, title="VEO 3.1") as app:
    gr.Markdown("# 🎬 VEO 3.1 - Production Tool")

    # Top setup section
    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("## ⚙️ Setup")
            topic = gr.Textbox(label="🎯 Chủ đề phim", placeholder="Làm phở bò...")
            
            with gr.Row():
                duration = gr.Number(label="⏱️ Thời lượng (phút)", value=1, minimum=0.5, maximum=10, step=0.5)
                api_key = gr.Textbox(label="🔑 API Key", value=DEFAULT_API_KEY, type="password")

            with gr.Row():
                project_id = gr.Textbox(label="📁 Project ID", value=DEFAULT_PROJECT_ID, scale=2)
                cookies = gr.Textbox(label="🍪 Cookies", value="./cookie.txt", scale=1)

            script_output = gr.Textbox(label="📋 Kết quả", lines=4, elem_classes="log-box")

        with gr.Column(scale=1):
            gr.Markdown("## 🎬 Actions")
            generate_btn = gr.Button("📝 1. Tạo kịch bản", variant="primary", size="lg")
            produce_btn = gr.Button("🎬 2. Tạo videos", variant="primary", size="lg")
            gr.Markdown("---")
            gr.Markdown("### 💡 Tips\n- Thời lượng: 0.5-10 phút\n- Export cookies từ Flow\n- Project ID từ URL Flow")

    # Storyboard
    gr.Markdown("## 🎬 Storyboard (Các phân cảnh)")
    scenes_html = gr.HTML(value="<p style='text-align: center; color: #9ca3af; padding: 40px;'>Chưa có cảnh nào</p>")

    # Log at bottom (collapsed)
    with gr.Accordion("📊 Log chi tiết", open=False):
        log_output = gr.Textbox(label="", lines=15, elem_classes="log-box")

    # Hidden controls
    with gr.Row(visible=False):
        regen_scene_num = gr.Number(value=1, elem_id="regen-scene-num")
        regen_btn_hidden = gr.Button("Regen", elem_id="regen-btn")
        delete_scene_num = gr.Number(value=1, elem_id="delete-scene-num")
        delete_btn_hidden = gr.Button("Delete", elem_id="delete-btn")

    # Event handlers
    def gen_wrapper(t, d, a, c, p):
        return asyncio.run(generate_script_async(t, d, a, c, p))

    generate_btn.click(
        fn=gen_wrapper,
        inputs=[topic, duration, api_key, cookies, project_id],
        outputs=[script_output, scenes_html]
    )

    produce_btn.click(
        fn=produce_all_videos,
        inputs=[],
        outputs=[log_output, scenes_html]
    )

    regen_btn_hidden.click(
        fn=regenerate_scene,
        inputs=[regen_scene_num],
        outputs=[log_output, scenes_html]
    )

    delete_btn_hidden.click(
        fn=delete_scene,
        inputs=[delete_scene_num],
        outputs=[log_output, scenes_html]
    )

if __name__ == "__main__":
    print("="*60)
    print("🎬 VEO 3.1 - Production Tool (Final)")
    print("="*60)
    print("✨ Card-based UI")
    print("📊 Log collapsed at bottom")
    print("🔑 API key input")
    print("⏱️ Duration: 0.5-10 phút")
    print("="*60)
    print("🌐 http://localhost:7860")
    print("="*60)

    app.queue().launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
