#!/usr/bin/env python3
"""
VEO 3.1 - FINAL SIMPLE UI
Mỗi scene có: Thông tin + Video + Nút tạo lại ngay bên cạnh
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

DEFAULT_PROJECT_ID = "01JFXPX1ZXPKJXE21YV2MB2HN6"

css = """
.log-box { font-family: 'Courier New', monospace; font-size: 13px; }
.scene-card { border: 2px solid #e0e0e0; border-radius: 8px; padding: 12px; margin: 8px 0; background: #f9f9f9; }
"""

class AppState:
    def __init__(self):
        self.script = None
        self.scenes = []
        self.project_id = None
        self.cookies_path = None

state = AppState()

# ============================================================================
# SCRIPT GENERATION
# ============================================================================

async def generate_script_async(topic, duration, cookies, project_id):
    """Generate script"""
    try:
        if not os.path.exists(cookies):
            return f"❌ Cookie file không tồn tại: {cookies}", "", []

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "❌ Thiếu GEMINI_API_KEY trong .env", "", []

        script_generator = ScriptGenerator(api_key)
        script = script_generator.generate_script(topic, duration * 60)  # convert to seconds

        if not script or 'scenes' not in script:
            return "❌ Không thể tạo kịch bản", "", []

        state.script = script
        state.scenes = [
            {
                'number': i + 1,
                'description': scene['description'],
                'prompt': scene['prompt'],
                'status': 'pending',
                'video_path': None
            }
            for i, scene in enumerate(script['scenes'])
        ]
        state.project_id = project_id if project_id else DEFAULT_PROJECT_ID
        state.cookies_path = cookies

        output = []
        output.append(f"✅ Đã tạo: {script['title']}")
        output.append(f"📝 {script['description']}")
        output.append(f"🎬 Số cảnh: {len(script['scenes'])}")

        return "\n".join(output), render_production_button(), render_scenes()

    except Exception as e:
        return f"❌ Lỗi: {str(e)}", "", []

def render_production_button():
    """Show produce button after script is ready"""
    if state.scenes:
        return gr.update(visible=True)
    return gr.update(visible=False)

def render_scenes():
    """Render each scene as accordion with video + regenerate button"""
    if not state.scenes:
        return [gr.update(visible=False) for _ in range(10)]

    updates = []
    for i in range(10):  # Max 10 scenes
        if i < len(state.scenes):
            scene = state.scenes[i]
            updates.append(gr.update(visible=True, label=f"🎬 Cảnh {scene['number']}: {scene['description'][:50]}..."))
        else:
            updates.append(gr.update(visible=False))

    return updates

# ============================================================================
# VIDEO PRODUCTION
# ============================================================================

def produce_all_videos(progress=gr.Progress()):
    """Produce all videos with detailed logging"""
    if not state.scenes:
        return "❌ Chưa có kịch bản!", *render_scenes()

    log_lines = []
    log = lambda msg: log_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    log("🚀 Bắt đầu sản xuất")
    log(f"📝 Kịch bản: {state.script['title']}")
    log(f"🎬 Tổng cảnh: {len(state.scenes)}")
    log("")

    session = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger = DetailedLogger(session_name=session)

    controller = FlowControllerSelenium(cookies_path=state.cookies_path, headless=False)

    try:
        progress(0.05, desc="🚀 Khởi động Comet...")
        log("🚀 Khởi động Comet...")
        controller.start()
        log("✅ Comet started")

        progress(0.1, desc="🌐 Vào Flow...")
        controller.goto_flow()

        if state.project_id:
            progress(0.15, desc="📁 Vào project...")
            controller.goto_project(state.project_id)
            log("✅ Vào project")

        log("")

        total = len(state.scenes)
        for i, scene in enumerate(state.scenes):
            num = scene['number']
            start_time = datetime.now()

            log(f"{'='*60}")
            log(f"🎬 CẢNH {num}/{total}")
            log(f"📝 {scene['description']}")
            log("")

            scene['status'] = 'processing'

            def progress_cb(elapsed, percent, screenshot):
                progress((0.2 + (i / total) * 0.7), desc=f"🎬 Cảnh {num}/{total} - {percent}%")
                if percent % 20 == 0:
                    log(f"   📊 {percent}%")

            try:
                log("   ⏳ Tạo video...")
                url = controller.create_video_from_prompt(
                    prompt=scene['prompt'],
                    aspect_ratio="16:9",
                    is_first_video=(i == 0),
                    progress_callback=progress_cb
                )

                if url:
                    dur = (datetime.now() - start_time).total_seconds()
                    scene['status'] = 'completed'
                    scene['video_path'] = url
                    log(f"   ✅ Hoàn thành ({dur:.1f}s)")
                    log(f"   📹 {url[:70]}")
                else:
                    scene['status'] = 'failed'
                    log(f"   ❌ Không tạo được video")

            except Exception as e:
                scene['status'] = 'failed'
                log(f"   ❌ Lỗi: {str(e)}")

            log("")

        controller.close()
        logger.close()

        completed = sum(1 for s in state.scenes if s['status'] == 'completed')
        log("="*60)
        log(f"🎉 HOÀN THÀNH: {completed}/{total} cảnh")
        log("="*60)

        progress(1.0, desc="✅ Xong!")
        return "\n".join(log_lines), *render_scenes()

    except Exception as e:
        controller.close()
        logger.close()
        log(f"❌ Lỗi: {str(e)}")
        return "\n".join(log_lines), *render_scenes()

# ============================================================================
# REGENERATE SINGLE SCENE
# ============================================================================

def regenerate_scene_by_index(scene_index, progress=gr.Progress()):
    """Regenerate specific scene"""
    if scene_index >= len(state.scenes):
        return "❌ Scene không tồn tại!", *render_scenes()

    scene = state.scenes[scene_index]
    num = scene['number']

    log_lines = []
    log = lambda msg: log_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    log(f"🔄 TẠO LẠI CẢNH {num}")
    log(f"📝 {scene['description']}")

    session = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger = DetailedLogger(session_name=f"regen_{session}")

    controller = FlowControllerSelenium(cookies_path=state.cookies_path, headless=False)
    scene['status'] = 'processing'

    try:
        progress(0.1, desc="🚀 Khởi động...")
        controller.start()

        progress(0.2, desc="🌐 Vào Flow...")
        controller.goto_flow()

        progress(0.3, desc="📁 Vào project...")
        controller.goto_project(state.project_id)

        start_time = datetime.now()
        log("⏳ Tạo video mới...")

        def regen_cb(elapsed, percent, screenshot):
            progress(0.4 + (percent / 100) * 0.5, desc=f"🔄 {percent}%")
            if percent % 20 == 0:
                log(f"   📊 {percent}%")

        url = controller.create_video_from_prompt(
            prompt=scene['prompt'],
            aspect_ratio="16:9",
            is_first_video=True,
            progress_callback=regen_cb
        )

        if url:
            dur = (datetime.now() - start_time).total_seconds()
            scene['status'] = 'completed'
            scene['video_path'] = url
            log(f"✅ Video mới hoàn thành ({dur:.1f}s)")
        else:
            scene['status'] = 'failed'
            log("❌ Không tạo được")

        controller.close()
        logger.close()

        progress(1.0, desc="✅ Xong!")
        return "\n".join(log_lines), *render_scenes()

    except Exception as e:
        controller.close()
        logger.close()
        scene['status'] = 'failed'
        log(f"❌ Lỗi: {str(e)}")
        return "\n".join(log_lines), *render_scenes()

# ============================================================================
# UI
# ============================================================================

with gr.Blocks(theme=gr.themes.Soft(), css=css, title="VEO 3.1") as app:
    gr.Markdown("# 🎬 VEO 3.1 - Simple Workflow")
    gr.Markdown("### Setup → Script → Produce → Xem video từng scene → Tạo lại (nếu cần)")

    # ===== SETUP =====
    gr.Markdown("## 1️⃣ Setup")
    with gr.Row():
        topic_input = gr.Textbox(label="🎯 Chủ đề", placeholder="Làm phở bò", scale=2)
        duration = gr.Slider(0.5, 3, 1, step=0.5, label="⏱️ Phút", scale=1)

    with gr.Row():
        project_id_input = gr.Textbox(label="📁 Project ID", value=DEFAULT_PROJECT_ID, scale=2)
        cookies_input = gr.Textbox(label="🍪 Cookies", value="./cookie.txt", scale=1)

    generate_btn = gr.Button("📝 Tạo kịch bản", variant="primary", size="lg")

    script_output = gr.Textbox(label="📋 Kết quả", lines=6, elem_classes="log-box")

    # ===== PRODUCE BUTTON (hidden until script ready) =====
    gr.Markdown("## 2️⃣ Tạo videos")
    produce_btn = gr.Button("🎬 Tạo TẤT CẢ videos", variant="primary", size="lg", visible=False)

    production_log = gr.Textbox(label="🔍 Log chi tiết", lines=18, elem_classes="log-box")

    # ===== SCENES (max 10) =====
    gr.Markdown("## 3️⃣ Các cảnh & Videos")
    gr.Markdown("*Mỗi cảnh hiển thị: Mô tả → Prompt → Video → Nút tạo lại*")

    scene_accordions = []
    scene_info_boxes = []
    scene_videos = []
    scene_regen_btns = []

    for i in range(10):
        with gr.Accordion(f"Cảnh {i+1}", open=False, visible=False) as accordion:
            scene_accordions.append(accordion)

            with gr.Row():
                with gr.Column(scale=2):
                    info_box = gr.Textbox(
                        label="Thông tin",
                        lines=4,
                        elem_classes="log-box",
                        interactive=False
                    )
                    scene_info_boxes.append(info_box)

                    regen_btn = gr.Button(f"🔄 Tạo lại cảnh {i+1}", variant="secondary")
                    scene_regen_btns.append(regen_btn)

                with gr.Column(scale=3):
                    video = gr.Video(
                        label="Video",
                        height=300
                    )
                    scene_videos.append(video)

    # Hidden state
    script_data = gr.State()

    # ===== EVENT HANDLERS =====

    def gen_wrapper(topic, dur, cookies, proj):
        result = asyncio.run(generate_script_async(topic, dur, cookies, proj))
        script_out, produce_btn_update, *scene_updates = result
        return script_out, produce_btn_update, *scene_updates

    generate_btn.click(
        fn=gen_wrapper,
        inputs=[topic_input, duration, cookies_input, project_id_input],
        outputs=[script_output, produce_btn, *scene_accordions]
    )

    produce_btn.click(
        fn=produce_all_videos,
        inputs=[],
        outputs=[production_log, *scene_accordions]
    )

    # Wire regenerate buttons
    for i, btn in enumerate(scene_regen_btns):
        btn.click(
            fn=lambda idx=i: regenerate_scene_by_index(idx),
            inputs=[],
            outputs=[production_log, *scene_accordions]
        )

if __name__ == "__main__":
    print("="*60)
    print("🎬 VEO 3.1 - FINAL SIMPLE UI")
    print("="*60)
    print("🌐 http://localhost:7860")
    print("💡 Mỗi scene có video + nút tạo lại")
    print("="*60)

    app.queue().launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
