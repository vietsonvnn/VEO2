#!/usr/bin/env python3
"""
VEO 3.1 - SIMPLE UI
Đơn giản nhất: 1 page dọc, videos theo thứ tự scene
"""

import gradio as gr
import asyncio
import os
import sys
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from script_generator import ScriptGenerator
from browser_automation.flow_controller_selenium import FlowControllerSelenium
from utils.detailed_logger import DetailedLogger
from dotenv import load_dotenv

load_dotenv()

DEFAULT_PROJECT_ID = "01JFXPX1ZXPKJXE21YV2MB2HN6"

css = """
.log-box {
    font-family: 'Courier New', monospace;
    font-size: 13px;
}
"""

class AppState:
    def __init__(self):
        self.script = None
        self.scenes = []
        self.project_id = None

state = AppState()

async def generate_script_async(topic, duration, cookies, project_id):
    """Generate script"""
    try:
        if not os.path.exists(cookies):
            return f"❌ Cookie file không tồn tại: {cookies}", pd.DataFrame(), None

        script_generator = ScriptGenerator()
        script = script_generator.generate_script(topic, duration)

        if not script or 'scenes' not in script:
            return "❌ Không thể tạo kịch bản", pd.DataFrame(), None

        state.script = script
        state.scenes = [
            {
                'number': i + 1,
                'description': scene['description'],
                'prompt': scene['prompt'],
                'status': '⏸️ Chưa tạo',
                'video_path': None
            }
            for i, scene in enumerate(script['scenes'])
        ]
        state.project_id = project_id if project_id else DEFAULT_PROJECT_ID

        output = []
        output.append(f"✅ Đã tạo kịch bản: {script['title']}")
        output.append(f"📝 {script['description']}")
        output.append(f"🎬 Số cảnh: {len(script['scenes'])}")
        output.append("")
        for i, s in enumerate(script['scenes'], 1):
            output.append(f"Scene {i}: {s['description']}")

        df = pd.DataFrame([
            [s['number'], s['description'][:50], s['prompt'][:60], s['status'], ""]
            for s in state.scenes
        ], columns=["#", "Mô tả", "Prompt", "Status", "Video"])

        return "\n".join(output), df, script

    except Exception as e:
        return f"❌ Lỗi: {str(e)}", pd.DataFrame(), None

def produce_videos(cookies_path, progress=gr.Progress()):
    """Produce all videos"""
    if not state.scenes:
        return "❌ Chưa có kịch bản!", pd.DataFrame(), []

    log_lines = []
    log = lambda msg: log_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    log("🚀 Bắt đầu sản xuất")
    log(f"📝 Kịch bản: {state.script['title']}")
    log(f"🎬 Tổng cảnh: {len(state.scenes)}")
    log("")

    session = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger = DetailedLogger(session_name=session)
    logger.info(f"Production: {state.script['title']}", event_type="start")

    controller = FlowControllerSelenium(cookies_path=cookies_path, headless=False)

    try:
        progress(0.05, desc="🚀 Khởi động Comet...")
        log("🚀 Khởi động Comet...")
        controller.start()
        log("✅ Comet started")

        progress(0.1, desc="🌐 Vào Flow...")
        log("🌐 Vào Flow...")
        controller.goto_flow()
        log("✅ Vào Flow")

        if state.project_id:
            progress(0.15, desc="📁 Vào project...")
            log(f"📁 Vào project {state.project_id}")
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

            scene['status'] = '⏳ Đang tạo...'
            logger.scene_start(num, total, scene['description'])

            def progress_cb(elapsed, percent, screenshot):
                progress((0.2 + (i / total) * 0.7), desc=f"🎬 Cảnh {num}/{total} - {percent}%")
                if percent % 20 == 0:
                    log(f"   📊 {percent}%")
                    logger.flow_progress(num, percent)

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
                    scene['status'] = '✅ Hoàn thành'
                    scene['video_path'] = url
                    log(f"   ✅ Hoàn thành ({dur:.1f}s)")
                    log(f"   📹 {url[:70]}")
                    logger.scene_complete(num, url, dur)
                else:
                    scene['status'] = '❌ Thất bại'
                    log(f"   ❌ Không tạo được video")
                    logger.scene_failed(num, "No URL")

            except Exception as e:
                scene['status'] = '❌ Lỗi'
                log(f"   ❌ Lỗi: {str(e)}")
                logger.scene_failed(num, str(e))

            log("")

        controller.close()
        logger.close()

        completed = sum(1 for s in state.scenes if '✅' in s['status'])
        log("="*60)
        log(f"🎉 HOÀN THÀNH: {completed}/{total} cảnh")
        log("="*60)

        df = pd.DataFrame([
            [s['number'], s['description'][:50], s['prompt'][:60], s['status'],
             s['video_path'][:50] if s['video_path'] else ""]
            for s in state.scenes
        ], columns=["#", "Mô tả", "Prompt", "Status", "Video"])

        videos = [s['video_path'] for s in sorted(state.scenes, key=lambda x: x['number'])
                  if s['video_path']]

        progress(1.0, desc="✅ Xong!")
        return "\n".join(log_lines), df, videos

    except Exception as e:
        controller.close()
        logger.close()
        log(f"❌ Lỗi: {str(e)}")
        return "\n".join(log_lines), pd.DataFrame(), []

def regenerate_scene(scene_num, cookies_path, progress=gr.Progress()):
    """Regenerate 1 scene"""
    num = int(scene_num)

    if not state.scenes:
        return "❌ Chưa có kịch bản!", pd.DataFrame(), []

    scene = None
    for s in state.scenes:
        if s['number'] == num:
            scene = s
            break

    if not scene:
        return f"❌ Không tìm thấy cảnh {num}!", pd.DataFrame(), []

    log_lines = []
    log = lambda msg: log_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    log(f"🔄 TẠO LẠI CẢNH {num}")
    log(f"📝 {scene['description']}")
    log("")

    session = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger = DetailedLogger(session_name=f"regen_{session}")

    controller = FlowControllerSelenium(cookies_path=cookies_path, headless=False)
    scene['status'] = '⏳ Đang tạo lại...'

    try:
        progress(0.1, desc="🚀 Khởi động...")
        log("🚀 Khởi động Comet...")
        controller.start()

        progress(0.2, desc="🌐 Vào Flow...")
        controller.goto_flow()

        progress(0.3, desc="📁 Vào project...")
        controller.goto_project(state.project_id)
        log("✅ Vào project")

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
            scene['status'] = '✅ Hoàn thành'
            scene['video_path'] = url
            log(f"✅ Video mới hoàn thành ({dur:.1f}s)")
            log(f"📹 {url[:70]}")
            logger.scene_complete(num, url, dur)
        else:
            scene['status'] = '❌ Thất bại'
            log("❌ Không tạo được")
            logger.scene_failed(num, "No URL")

        controller.close()
        logger.close()

        df = pd.DataFrame([
            [s['number'], s['description'][:50], s['prompt'][:60], s['status'],
             s['video_path'][:50] if s['video_path'] else ""]
            for s in state.scenes
        ], columns=["#", "Mô tả", "Prompt", "Status", "Video"])

        videos = [s['video_path'] for s in sorted(state.scenes, key=lambda x: x['number'])
                  if s['video_path']]

        progress(1.0, desc="✅ Xong!")
        return "\n".join(log_lines), df, videos

    except Exception as e:
        controller.close()
        logger.close()
        scene['status'] = '❌ Lỗi'
        log(f"❌ Lỗi: {str(e)}")
        return "\n".join(log_lines), pd.DataFrame(), []

with gr.Blocks(theme=gr.themes.Soft(), css=css, title="VEO 3.1") as app:
    gr.Markdown("# 🎬 VEO 3.1 - Simple Workflow")
    gr.Markdown("### Vertical workflow: Setup → Script → Produce → Results → Regenerate")

    gr.Markdown("## 1️⃣ Setup")
    with gr.Row():
        topic_input = gr.Textbox(label="🎯 Chủ đề", placeholder="Làm phở bò", scale=2)
        duration = gr.Slider(0.5, 3, 1, step=0.5, label="⏱️ Phút", scale=1)

    with gr.Row():
        project_id_input = gr.Textbox(label="📁 Project ID", value=DEFAULT_PROJECT_ID, scale=2)
        cookies_input = gr.Textbox(label="🍪 Cookies", value="./cookie.txt", scale=1)

    gr.Markdown("## 2️⃣ Tạo kịch bản")
    with gr.Row():
        generate_btn = gr.Button("📝 Tạo kịch bản", variant="primary", size="lg", scale=2)
        produce_btn = gr.Button("🎬 Tạo TẤT CẢ videos", variant="primary", size="lg", scale=2)

    script_output = gr.Textbox(label="📋 Kịch bản", lines=10, elem_classes="log-box")
    script_data = gr.State()

    gr.Markdown("## 3️⃣ Log sản xuất (real-time)")
    production_log = gr.Textbox(label="🔍 Chi tiết từng bước", lines=20, elem_classes="log-box")

    gr.Markdown("## 4️⃣ Kết quả")
    scenes_table = gr.Dataframe(
        headers=["#", "Mô tả", "Prompt", "Status", "Video"],
        label="📋 Bảng cảnh",
        wrap=True,
        interactive=False,
        row_count=(1, "dynamic")
    )

    gr.Markdown("### 🎥 Videos (theo thứ tự Scene 1, 2, 3...)")
    video_gallery = gr.Gallery(
        label="Click để xem",
        columns=4,
        rows=2,
        height=350,
        object_fit="contain",
        interactive=False
    )

    gr.Markdown("## 5️⃣ Tạo lại (nếu cần)")
    with gr.Row():
        regenerate_num = gr.Number(label="Số cảnh", value=1, minimum=1, precision=0, scale=1)
        regenerate_btn = gr.Button("🔄 Tạo lại", variant="secondary", size="lg", scale=2)

    regenerate_log = gr.Textbox(label="🔄 Log", lines=12, elem_classes="log-box")

    def gen_wrapper(topic, dur, cookies, proj):
        return asyncio.run(generate_script_async(topic, dur, cookies, proj))

    generate_btn.click(
        fn=gen_wrapper,
        inputs=[topic_input, duration, cookies_input, project_id_input],
        outputs=[script_output, scenes_table, script_data]
    )

    produce_btn.click(
        fn=produce_videos,
        inputs=[cookies_input],
        outputs=[production_log, scenes_table, video_gallery]
    )

    regenerate_btn.click(
        fn=regenerate_scene,
        inputs=[regenerate_num, cookies_input],
        outputs=[regenerate_log, scenes_table, video_gallery]
    )

if __name__ == "__main__":
    print("="*60)
    print("🎬 VEO 3.1 - SIMPLE UI")
    print("="*60)
    print("🌐 http://localhost:7860")
    print("📊 Videos hiển thị theo thứ tự scene")
    print("="*60)

    app.queue().launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
