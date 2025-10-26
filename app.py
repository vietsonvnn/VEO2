#!/usr/bin/env python3
"""
VEO 3.1 - Production UI (Electron Version)
- Card-based layout với video preview
- Electron Browser (Playwright) thay vì Selenium
- Output = 1 video per prompt (auto config)
- Baseline URL Tracking (100% accurate matching)
- Regenerate videos (tạo lại)
- Delete videos from Flow (xóa khỏi project)
- Log collapsed ở dưới
- API key input
- Duration tùy chỉnh
"""

import gradio as gr
import asyncio
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from script_generator.gemini_generator import ScriptGenerator
from flow_video_tracker import FlowVideoTracker
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
        self.aspect_ratio = "16:9"
        self.model = "Veo 3.1 - Fast"

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
        // Find Gradio input by elem_id
        const numInput = document.querySelector('#regen-scene-num input, #regen-scene-num');
        const btn = document.querySelector('#regen-btn');
        if (numInput && btn) {
            numInput.value = num;
            // Dispatch input event to update Gradio state
            numInput.dispatchEvent(new Event('input', { bubbles: true }));
            setTimeout(() => btn.click(), 100);
        }
    }
    function deleteScene(num) {
        if (confirm('Xóa cảnh ' + num + '?')) {
            const numInput = document.querySelector('#delete-scene-num input, #delete-scene-num');
            const btn = document.querySelector('#delete-btn');
            if (numInput && btn) {
                numInput.value = num;
                numInput.dispatchEvent(new Event('input', { bubbles: true }));
                setTimeout(() => btn.click(), 100);
            }
        }
    }
    </script>
    """

    return "\n".join(html) + js_script

async def generate_script_async(topic, duration, api_key, cookies, project_id, aspect_ratio, model):
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
                'prompt': scene.get('veo_prompt', scene.get('prompt', '')),
                'status': 'pending',
                'video_path': None
            }
            for i, scene in enumerate(script['scenes'])
        ]
        state.project_id = project_id or DEFAULT_PROJECT_ID
        state.cookies_path = cookies
        state.aspect_ratio = aspect_ratio
        state.model = model

        output = f"✅ {script.get('title', 'Kịch bản')}\n📝 {script.get('description', '')}\n🎬 {len(state.scenes)} cảnh\n📐 Tỷ lệ: {aspect_ratio}\n🎨 Model: {model}"
        return output, build_scenes_html()

    except Exception as e:
        return f"❌ Lỗi: {str(e)}", ""

async def produce_all_videos_async():
    """Produce all videos with real-time updates using FlowVideoTracker"""
    if not state.scenes:
        yield "❌ Chưa có kịch bản!", ""
        return

    log = []
    def add_log(msg):
        log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    add_log("🚀 Bắt đầu sản xuất với Electron Browser")
    add_log(f"🎬 Tổng: {len(state.scenes)} cảnh")
    yield "\n".join(log), build_scenes_html()

    session = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger = DetailedLogger(session_name=session)

    # Use FlowVideoTracker with Electron
    tracker = FlowVideoTracker(cookies_path=state.cookies_path)

    try:
        add_log("🚀 Khởi động Electron browser...")
        yield "\n".join(log), build_scenes_html()

        await tracker.start()
        add_log("✅ Browser đã khởi động")
        yield "\n".join(log), build_scenes_html()

        # Go to project
        project_id = state.project_id or DEFAULT_PROJECT_ID
        add_log(f"📁 Vào project: {project_id}")
        yield "\n".join(log), build_scenes_html()

        await tracker.goto_project(project_id)
        add_log("✅ Đã vào project")
        yield "\n".join(log), build_scenes_html()

        # Set output to 1 video per prompt
        add_log("⚙️  Cài đặt output = 1 video...")
        yield "\n".join(log), build_scenes_html()

        await tracker.set_output_to_1()
        add_log("✅ Đã cài đặt output = 1")
        yield "\n".join(log), build_scenes_html()

        # Set aspect ratio (default 16:9)
        aspect_ratio = getattr(state, 'aspect_ratio', '16:9')
        add_log(f"⚙️  Cài đặt aspect ratio: {aspect_ratio}...")
        yield "\n".join(log), build_scenes_html()

        await tracker.set_aspect_ratio(aspect_ratio)
        add_log(f"✅ Đã set aspect ratio: {aspect_ratio}")
        yield "\n".join(log), build_scenes_html()

        # Set model (default Veo 3.1 - Fast)
        model = getattr(state, 'model', 'Veo 3.1 - Fast')
        add_log(f"⚙️  Cài đặt model: {model}...")
        yield "\n".join(log), build_scenes_html()

        await tracker.set_model(model)
        add_log(f"✅ Đã set model: {model}")
        yield "\n".join(log), build_scenes_html()

        # Prepare prompts
        prompts = [scene['prompt'] for scene in state.scenes]

        add_log(f"🎬 Bắt đầu tạo {len(prompts)} video...")
        yield "\n".join(log), build_scenes_html()

        # Create all videos (tracker handles sequential creation and URL tracking)
        scenes_data = await tracker.create_videos(prompts)

        # Update state with results
        # scenes_data is Dict[int, Dict], keys are 1-indexed scene numbers
        for scene_num, scene_data in scenes_data.items():
            scene = state.scenes[scene_num - 1]  # Convert to 0-indexed
            scene['number'] = scene_data['scene_number']

            if scene_data['video_url']:
                scene['status'] = 'completed'
                scene['video_path'] = scene_data['video_url']
                add_log(f"   ✅ Cảnh {scene['number']}: {scene['description'][:40]}")
                logger.scene_complete(scene['number'], scene_data['video_url'], 0)
            else:
                scene['status'] = 'failed'
                add_log(f"   ❌ Cảnh {scene['number']} thất bại")

            yield "\n".join(log), build_scenes_html()

        # Keep browser open
        add_log("ℹ️  Trình duyệt vẫn mở - có thể Regenerate hoặc Delete")
        logger.close()

        completed = sum(1 for s in state.scenes if s['status'] == 'completed')
        add_log(f"🎉 KẾT QUẢ: {completed}/{len(state.scenes)} cảnh hoàn thành")
        yield "\n".join(log), build_scenes_html()

    except Exception as e:
        logger.close()
        add_log(f"❌ Lỗi: {str(e)}")
        yield "\n".join(log), build_scenes_html()

def produce_all_videos():
    """Wrapper to run async produce_all_videos_async"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        gen = produce_all_videos_async()
        while True:
            try:
                result = loop.run_until_complete(gen.__anext__())
                yield result
            except StopAsyncIteration:
                break
    finally:
        loop.close()

async def regenerate_scene_async(scene_num, progress=gr.Progress()):
    """Regenerate scene using FlowVideoTracker"""
    try:
        num = int(scene_num)
        if num < 1 or num > len(state.scenes):
            return "❌ Scene không hợp lệ!", ""

        scene = state.scenes[num - 1]
        log = []
        def add_log(msg):
            log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

        add_log(f"🔄 TẠO LẠI CẢNH {num}")
        scene['status'] = 'processing'

        tracker = FlowVideoTracker(cookies_path=state.cookies_path)

        progress(0.1, desc="🚀 Khởi động...")
        await tracker.start()
        add_log("✅ Browser khởi động")

        # Go to project
        project_id = state.project_id or DEFAULT_PROJECT_ID
        await tracker.goto_project(project_id)
        add_log(f"✅ Vào project {project_id}")

        # Set output to 1
        await tracker.set_output_to_1()
        add_log("✅ Đã set output = 1")

        progress(0.3, desc="🎬 Tạo video...")

        # Create single video
        scenes_data = await tracker.create_videos([scene['prompt']])

        if scenes_data and scenes_data[0]['video_url']:
            scene['status'] = 'completed'
            scene['video_path'] = scenes_data[0]['video_url']
            add_log(f"✅ Hoàn thành")
        else:
            scene['status'] = 'failed'
            add_log("❌ Thất bại")

        add_log("ℹ️  Trình duyệt vẫn mở")
        progress(1.0, desc="✅ Xong!")
        return "\n".join(log), build_scenes_html()

    except Exception as e:
        add_log(f"❌ Lỗi: {str(e)}")
        return "\n".join(log), build_scenes_html()

def regenerate_scene(scene_num, progress=gr.Progress()):
    """Wrapper for async regenerate"""
    return asyncio.run(regenerate_scene_async(scene_num, progress))

async def delete_scene_async(scene_num):
    """Delete scene using FlowVideoTracker"""
    try:
        num = int(scene_num)

        # Find scene
        scene = next((s for s in state.scenes if s['number'] == num), None)
        if not scene:
            return "❌ Scene không tồn tại!", ""

        # Get video URL to delete
        video_url = scene.get('video_path')

        log = []
        def add_log(msg):
            log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

        add_log(f"🗑️  XÓA CẢNH {num}")

        if video_url:
            # Delete from Flow
            tracker = FlowVideoTracker(cookies_path=state.cookies_path)

            add_log("🚀 Khởi động browser...")
            await tracker.start()

            project_id = state.project_id or DEFAULT_PROJECT_ID
            await tracker.goto_project(project_id)
            add_log(f"✅ Vào project {project_id}")

            # Delete video
            success = await tracker.delete_video_by_url(video_url)

            if success:
                add_log(f"✅ Đã xóa video khỏi Flow")
            else:
                add_log(f"❌ Không xóa được video khỏi Flow")
        else:
            add_log("ℹ️  Scene chưa có video")

        # Remove from state
        state.scenes = [s for s in state.scenes if s['number'] != num]
        for i, scene in enumerate(state.scenes):
            scene['number'] = i + 1

        add_log(f"✅ Đã xóa cảnh {num} khỏi danh sách")
        return "\n".join(log), build_scenes_html()

    except Exception as e:
        return f"❌ Lỗi: {str(e)}", ""

def delete_scene(scene_num):
    """Wrapper for async delete"""
    return asyncio.run(delete_scene_async(scene_num))

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
                cookies = gr.Textbox(label="🍪 Cookies", value="./config/cookies.json", scale=1)

            with gr.Row():
                aspect_ratio = gr.Radio(
                    choices=["16:9", "9:16"],
                    value="16:9",
                    label="📐 Tỷ lệ khung hình",
                    info="16:9 = Khổ ngang | 9:16 = Khổ dọc"
                )
                model = gr.Dropdown(
                    choices=["Veo 3.1 - Fast", "Veo 3.1 - Quality"],
                    value="Veo 3.1 - Fast",
                    label="🎨 Mô hình",
                    info="Fast = Nhanh hơn | Quality = Chất lượng cao hơn"
                )

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
    def gen_wrapper(t, d, a, c, p, ar, m):
        return asyncio.run(generate_script_async(t, d, a, c, p, ar, m))

    generate_btn.click(
        fn=gen_wrapper,
        inputs=[topic, duration, api_key, cookies, project_id, aspect_ratio, model],
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
    print("🎬 VEO 3.1 - Production Tool (ELECTRON VERSION)")
    print("="*60)
    print("✨ Card-based UI")
    print("🚀 Electron Browser (Playwright)")
    print("🎯 Output = 1 video per prompt")
    print("📍 Baseline URL Tracking (100% accurate)")
    print("🔄 Regenerate videos")
    print("🗑️  Delete videos from Flow")
    print("📊 Log collapsed at bottom")
    print("="*60)
    print("🌐 http://localhost:7860")
    print("="*60)

    app.queue().launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
