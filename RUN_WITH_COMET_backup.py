#!/usr/bin/env python3
"""
VEO 3.1 COMPLETE TOOL - Running with Comet Browser
Tool tạo video tự động với Comet để debug và quan sát

FEATURES:
- Generate script from topic (Gemini 2.0 Flash)
- Create videos for all scenes (VEO 3.1)
- Preview and regenerate individual scenes
- Assemble final movie
- Runs with Comet browser for debugging

USAGE:
    python RUN_WITH_COMET.py

Then open: http://localhost:7860
"""

import gradio as gr
import asyncio
import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from script_generator import ScriptGenerator
from browser_automation.flow_controller_selenium import FlowControllerSelenium
from utils.detailed_logger import DetailedLogger

# Load API key
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
script_generator = ScriptGenerator(GEMINI_API_KEY) if GEMINI_API_KEY else None

# Default project ID
DEFAULT_PROJECT_ID = "125966c7-418b-49da-9978-49f0a62356de"

# Session state
class State:
    def __init__(self):
        self.script = None
        self.scenes = []
        self.project_id = None

state = State()

# CSS styling
css = """
.container {
    max-width: 1400px;
    margin: auto;
}
.log-box {
    font-family: 'Monaco', 'Menlo', monospace;
    font-size: 13px;
    line-height: 1.5;
}
.scene-card {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 15px;
    margin: 10px 0;
}
"""

async def generate_script_async(topic, duration_minutes, cookies, project_id):
    """Generate script from topic"""
    try:
        if not script_generator:
            return "❌ Chưa có API key", [], None

        if not topic:
            return "❌ Vui lòng nhập chủ đề", [], None

        # Convert minutes to seconds
        duration = int(duration_minutes * 60)

        log = ["="*60, "📝 ĐANG TẠO KỊCH BẢN", "="*60, ""]
        log.append(f"🎯 Chủ đề: {topic}")
        log.append(f"⏱️ Thời lượng: {duration}s ({duration_minutes} phút)")
        log.append("")
        log.append("⏳ Đang tạo kịch bản với Gemini 2.0 Flash...")

        # Generate script (synchronous call - not async)
        script = script_generator.generate_script(topic, duration)

        if not script:
            return "❌ Không thể tạo kịch bản", [], None

        # Save to state
        state.script = script
        state.project_id = project_id.strip() if project_id and project_id.strip() else None

        # Create scene list
        state.scenes = []
        for i, scene in enumerate(script['scenes'], 1):
            state.scenes.append({
                'number': i,
                'description': scene['description'],
                'prompt': scene['veo_prompt'],
                'duration': scene['duration'],
                'status': 'pending',
                'url': None,
                'video_path': None
            })

        log.append("")
        log.append("✅ Kịch bản đã tạo xong!")
        log.append("="*60)
        log.append(f"📝 Tiêu đề: {script['title']}")
        log.append(f"🎞️ Số cảnh: {len(script['scenes'])}")
        log.append(f"⏱️ Tổng thời lượng: {script.get('total_duration', duration)}s")
        log.append("="*60)
        log.append("")

        for i, scene in enumerate(script['scenes'], 1):
            log.append(f"Scene {i}: {scene['description'][:60]}...")

        log.append("")
        log.append("👉 Chuyển sang tab 'Tạo Video' để bắt đầu sản xuất!")

        # Create scene cards for display
        scene_data = []
        for scene_state in state.scenes:
            scene_data.append({
                'number': scene_state['number'],
                'description': scene_state['description'],
                'prompt': scene_state['prompt'],
                'status': '⏳ Chờ tạo'
            })

        return "\n".join(log), scene_data, script

    except Exception as e:
        return f"❌ Lỗi: {str(e)}", [], None

def produce_videos_sync(cookies_path, progress=gr.Progress()):
    """Produce all videos with Comet browser (synchronous) with real-time progress"""
    if not state.script or not state.scenes:
        return "❌ Chưa có kịch bản. Vui lòng tạo kịch bản trước!", [], None, None, []

    # NOTE: Videos will create 2 outputs per prompt (x2 setting)
    # This is current Flow behavior - cannot be changed via automation
    status_lines = []
    status_lines.append("="*60)
    status_lines.append("🎬 BẮT ĐẦU SẢN XUẤT VIDEO (COMET)")
    status_lines.append("="*60)
    status_lines.append(f"📝 Kịch bản: {state.script['title']}")
    status_lines.append(f"🎞️ Tổng số cảnh: {len(state.scenes)}")
    status_lines.append(f"🌐 Browser: Comet (có thể quan sát)")
    status_lines.append(f"📊 Flow queue limit: Max 5 videos pending")
    status_lines.append("⚠️  Lưu ý: Flow mặc định tạo 2 videos/prompt (x2)")
    status_lines.append("="*60)
    status_lines.append("")

    # Initialize detailed logger
    session_name = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger = DetailedLogger(session_name=session_name)
    logger.info(f"Session started: {state.script['title']}", event_type="session_start")

    controller = FlowControllerSelenium(cookies_path=cookies_path, headless=False)
    current_screenshot = None  # Track current screenshot
    latest_video = None  # Track latest generated video
    all_videos = []  # Track ALL generated videos for gallery

    try:
        progress(0.05, desc="🚀 Khởi động Comet browser...")
        status_lines.append("🚀 Đang khởi động Comet browser...")
        controller.start()
        status_lines.append("✅ Comet đã khởi động (cửa sổ browser mở)")
        status_lines.append("")

        progress(0.1, desc="🌐 Đang vào Flow...")
        status_lines.append("🌐 Đang vào trang Flow...")
        controller.goto_flow()
        status_lines.append("✅ Đã vào trang Flow")
        status_lines.append("")

        # Handle project
        if state.project_id:
            progress(0.15, desc=f"📁 Đang vào project...")
            status_lines.append(f"📁 Sử dụng project có sẵn: {state.project_id}...")
            success = controller.goto_project(state.project_id)
            if success:
                status_lines.append("✅ Đã vào project")
            else:
                status_lines.append("❌ Không thể vào project")
                controller.close()
                return "\n".join(status_lines), [], None, None, []
        else:
            progress(0.15, desc="📁 Đang tạo project mới...")
            status_lines.append("📁 Đang tạo project mới...")
            project_id = controller.create_new_project(state.script['title'])
            if project_id:
                state.project_id = project_id
                status_lines.append(f"✅ Project đã tạo: {project_id}")
                controller.goto_project(project_id)
                status_lines.append("✅ Đã vào project")
            else:
                status_lines.append("⚠️ Không thể tạo project mới")
                status_lines.append(f"📁 Dùng project mặc định: {DEFAULT_PROJECT_ID}")
                state.project_id = DEFAULT_PROJECT_ID
                success = controller.goto_project(DEFAULT_PROJECT_ID)
                if success:
                    status_lines.append("✅ Đã vào project mặc định")
                else:
                    status_lines.append("❌ Không thể vào project mặc định")
                    controller.close()
                    return "\n".join(status_lines), [], None, None, []

        status_lines.append("")

        # Create videos for each scene
        total_scenes = len(state.scenes)
        for i, scene_state in enumerate(state.scenes):
            scene_num = scene_state['number']
            scene_start_time = datetime.now()

            progress((0.2 + (i / total_scenes) * 0.7), desc=f"🎬 Scene {scene_num}/{total_scenes}")

            status_lines.append(f"{'─'*60}")
            status_lines.append(f"🎬 SCENE {scene_num}/{total_scenes}")
            status_lines.append(f"📝 Mô tả: {scene_state['description'][:50]}...")
            status_lines.append("")

            # Log scene start
            logger.scene_start(scene_num, total_scenes, scene_state['description'])

            try:
                status_lines.append(f"   ⏳ Đang tạo video (VEO 3.1 - Comet)...")

                # Progress callback to update UI during video generation
                def scene_progress_callback(elapsed, percent, screenshot_path):
                    nonlocal current_screenshot
                    if screenshot_path:
                        current_screenshot = screenshot_path
                        logger.screenshot_captured(scene_num, screenshot_path)
                    if percent % 10 == 0:  # Log every 10%
                        logger.flow_progress(scene_num, percent)
                    progress_desc = f"🎬 Scene {scene_num}/{total_scenes} - {percent}% ({elapsed}s)"
                    progress((0.2 + (i / total_scenes) * 0.7), desc=progress_desc)

                url = controller.create_video_from_prompt(
                    prompt=scene_state['prompt'],
                    aspect_ratio="16:9",
                    is_first_video=(i == 0),
                    progress_callback=scene_progress_callback
                )

                if url:
                    # Calculate duration
                    scene_duration = (datetime.now() - scene_start_time).total_seconds()

                    status_lines.append(f"   ✅ Video đã tạo xong!")
                    scene_state['status'] = 'completed'
                    scene_state['url'] = url
                    scene_state['video_path'] = url

                    # Update latest video for display
                    latest_video = url

                    # Add to gallery
                    all_videos.append(url)

                    # Log completion
                    logger.scene_complete(scene_num, url, scene_duration)

                    # Check if it's a local file or URL
                    if url.startswith('/') or url.startswith('./'):
                        status_lines.append(f"   📥 Video đã download: {url}")
                    else:
                        status_lines.append(f"   🌐 Video URL: {url[:60]}...")

                    status_lines.append(f"   ✨ Scene {scene_num}: HOÀN THÀNH ({scene_duration:.1f}s)")
                else:
                    scene_state['status'] = 'failed'
                    status_lines.append(f"   ❌ Không thể tạo video")
                    status_lines.append(f"   ⚠️ Scene {scene_num}: THẤT BẠI")
                    logger.scene_failed(scene_num, "Video generation returned no URL")

            except Exception as e:
                scene_state['status'] = 'failed'
                error_msg = str(e)
                status_lines.append(f"   ❌ Lỗi: {error_msg}")
                status_lines.append(f"   ⚠️ Scene {scene_num}: THẤT BẠI")
                logger.scene_failed(scene_num, error_msg)

            status_lines.append("")

        controller.close()
        status_lines.append("="*60)

        # Count results
        completed = sum(1 for s in state.scenes if s['status'] == 'completed')
        failed = total_scenes - completed

        status_lines.append("📊 KẾT QUẢ CUỐI CÙNG")
        status_lines.append("="*60)
        status_lines.append(f"✅ Hoàn thành: {completed}/{total_scenes} cảnh")
        if failed > 0:
            status_lines.append(f"❌ Thất bại: {failed}/{total_scenes} cảnh")
        status_lines.append("="*60)

        if completed == total_scenes:
            status_lines.append("🎉 HOÀN THÀNH TOÀN BỘ!")
            status_lines.append("💡 Videos đang ở trên Flow, có thể download manual")
        elif completed > 0:
            status_lines.append("⚠️ Một số cảnh thất bại")
        else:
            status_lines.append("❌ Tất cả cảnh đều thất bại")

        status_lines.append("="*60)

        # Update scene display
        scene_updates = []
        for scene_state in state.scenes:
            status_icon = "✅" if scene_state['status'] == 'completed' else "❌"
            scene_updates.append({
                'number': scene_state['number'],
                'description': scene_state['description'],
                'prompt': scene_state['prompt'],
                'status': f"{status_icon} {scene_state['status']}"
            })

        # Close logger and save summary
        summary = logger.get_summary()
        logger.close()

        status_lines.append("")
        status_lines.append(f"📊 Log file: ./data/logs/session_{session_name}.log")
        status_lines.append(f"📊 JSON file: ./data/logs/session_{session_name}.json")

        progress(1.0, desc="✅ Hoàn thành!")
        return "\n".join(status_lines), scene_updates, current_screenshot, latest_video, all_videos

    except Exception as e:
        controller.close()
        if 'logger' in locals():
            logger.error(f"Fatal error: {str(e)}", event_type="fatal_error")
            logger.close()
        status_lines.append("")
        status_lines.append(f"❌ Lỗi: {str(e)}")
        return "\n".join(status_lines), [], None, None, []

def regenerate_single_scene(scene_number, cookies_path, progress=gr.Progress()):
    """Regenerate a single scene"""
    if not state.script or not state.scenes:
        return "❌ Chưa có kịch bản!", None, None, []

    # Find scene
    scene_state = None
    for s in state.scenes:
        if s['number'] == scene_number:
            scene_state = s
            break

    if not scene_state:
        return f"❌ Không tìm thấy scene {scene_number}!", None, None, []

    status_lines = []
    status_lines.append("="*60)
    status_lines.append(f"🔄 REGENERATE SCENE {scene_number}")
    status_lines.append("="*60)
    status_lines.append(f"📝 Mô tả: {scene_state['description']}")
    status_lines.append(f"💬 Prompt: {scene_state['prompt'][:80]}...")
    status_lines.append("")

    # Initialize logger
    session_name = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger = DetailedLogger(session_name=f"regen_{session_name}")
    logger.info(f"Regenerating scene {scene_number}", event_type="regenerate_start")

    controller = FlowControllerSelenium(cookies_path=cookies_path, headless=False)
    current_screenshot = None
    new_video = None

    try:
        progress(0.1, desc="🚀 Khởi động Comet...")
        status_lines.append("🚀 Đang khởi động Comet browser...")
        controller.start()
        status_lines.append("✅ Comet đã khởi động")
        status_lines.append("")

        progress(0.2, desc="🌐 Đang vào Flow...")
        status_lines.append("🌐 Đang vào trang Flow...")
        controller.goto_flow()
        status_lines.append("✅ Đã vào trang Flow")
        status_lines.append("")

        # Go to project
        if state.project_id:
            progress(0.3, desc="📁 Đang vào project...")
            status_lines.append(f"📁 Đang vào project: {state.project_id}...")
            success = controller.goto_project(state.project_id)
            if not success:
                status_lines.append("❌ Không thể vào project")
                controller.close()
                return "\n".join(status_lines), None, None, []
            status_lines.append("✅ Đã vào project")
        else:
            status_lines.append("❌ Không có Project ID")
            controller.close()
            return "\n".join(status_lines), None, None, []

        status_lines.append("")
        status_lines.append(f"🎬 Đang tạo lại video cho scene {scene_number}...")

        scene_start_time = datetime.now()

        # Progress callback
        def regenerate_progress_callback(elapsed, percent, screenshot_path):
            nonlocal current_screenshot
            if screenshot_path:
                current_screenshot = screenshot_path
                logger.screenshot_captured(scene_number, screenshot_path)
            if percent % 10 == 0:
                logger.flow_progress(scene_number, percent)
            progress_desc = f"🔄 Scene {scene_number} - {percent}% ({elapsed}s)"
            progress(0.4 + (percent / 100) * 0.5, desc=progress_desc)

        url = controller.create_video_from_prompt(
            prompt=scene_state['prompt'],
            aspect_ratio="16:9",
            is_first_video=True,
            progress_callback=regenerate_progress_callback
        )

        if url:
            scene_duration = (datetime.now() - scene_start_time).total_seconds()
            status_lines.append(f"✅ Video mới đã tạo xong!")

            # Update scene state
            scene_state['url'] = url
            scene_state['video_path'] = url
            scene_state['status'] = 'completed'
            new_video = url

            logger.scene_complete(scene_number, url, scene_duration)

            if url.startswith('/') or url.startswith('./'):
                status_lines.append(f"📥 Video đã download: {url}")
            else:
                status_lines.append(f"🌐 Video URL: {url[:60]}...")

            status_lines.append(f"✨ Scene {scene_number}: REGENERATED ({scene_duration:.1f}s)")
        else:
            status_lines.append(f"❌ Không thể tạo video")
            logger.scene_failed(scene_number, "Regeneration returned no URL")

        controller.close()
        logger.close()

        status_lines.append("="*60)
        progress(1.0, desc="✅ Hoàn thành!")

        # Get all videos for gallery update
        all_videos = [s.get('video_path') for s in state.scenes if s.get('video_path')]

        return "\n".join(status_lines), current_screenshot, new_video, all_videos

    except Exception as e:
        controller.close()
        logger.error(f"Regeneration error: {str(e)}", event_type="regenerate_error")
        logger.close()
        status_lines.append("")
        status_lines.append(f"❌ Lỗi: {str(e)}")
        return "\n".join(status_lines), None, None, []

def generate_script_wrapper(topic, duration, cookies, project_id):
    """Wrapper for async script generation"""
    return asyncio.run(generate_script_async(topic, duration, cookies, project_id))

def produce_videos_wrapper(cookies_path):
    """Wrapper for synchronous video production with Comet"""
    return produce_videos_sync(cookies_path)

# Create Gradio UI
with gr.Blocks(theme=gr.themes.Glass(), css=css, title="VEO 3.1 - Comet") as app:
    gr.Markdown("# 🎬 VEO 3.1 - Complete Tool (Comet Browser)")
    gr.Markdown("### Tạo phim tự động với Gemini + VEO 3.1 + Comet browser để debug")

    with gr.Tabs() as tabs:
        # Tab 1: Generate Script
        with gr.Tab("1️⃣ Tạo kịch bản"):
            with gr.Row():
                with gr.Column(scale=1):
                    topic_input = gr.Textbox(
                        label="🎯 Chủ đề phim",
                        placeholder="VD: Làm phở bò truyền thống Việt Nam",
                        lines=3
                    )
                    duration = gr.Slider(0.5, 3, 1, step=0.5, label="⏱️ Thời lượng (phút)")

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

                    generate_btn = gr.Button("📝 Tạo kịch bản", variant="primary", size="lg")

                with gr.Column(scale=2):
                    script_output = gr.Textbox(
                        label="📋 Kết quả",
                        lines=20,
                        max_lines=25,
                        elem_classes="log-box"
                    )

            scene_list = gr.JSON(label="🎬 Danh sách cảnh", visible=True)
            script_data = gr.State()

        # Tab 2: Produce Videos
        with gr.Tab("2️⃣ Tạo Video (Comet)"):
            gr.Markdown("""
            ### 🌐 Comet Browser Mode
            - Browser sẽ mở để bạn quan sát quá trình
            - Có thể debug và xem từng bước
            - ⚠️ Lưu ý: Flow mặc định tạo 2 videos/prompt (x2)
            """)

            produce_btn = gr.Button("🎬 Bắt đầu sản xuất", variant="primary", size="lg")

            with gr.Row():
                with gr.Column(scale=1):
                    production_output = gr.Textbox(
                        label="📋 Tiến trình sản xuất",
                        lines=25,
                        max_lines=30,
                        elem_classes="log-box"
                    )

                with gr.Column(scale=1):
                    current_scene_image = gr.Image(
                        label="📸 Màn hình hiện tại (Comet)",
                        type="filepath",
                        height=400
                    )

            # Video player để hiển thị video vừa tạo xong
            gr.Markdown("### 🎬 Video mới nhất")

            selected_video = gr.Video(
                label="📹 Video hiển thị ngay sau khi Flow tạo xong",
                autoplay=True,
                height=400,
                show_label=True
            )

            # Video gallery - hiển thị TẤT CẢ videos đã tạo
            gr.Markdown("### 🎥 Tất cả videos đã tạo")

            video_gallery = gr.Gallery(
                label="Click vào video để xem lại",
                show_label=False,
                elem_id="video_gallery",
                columns=4,
                rows=2,
                height="auto",
                object_fit="contain",
                interactive=False  # Read-only, không cho upload
            )

            # Status details với expandable accordion
            with gr.Accordion("📊 Chi tiết trạng thái các cảnh", open=False):
                scene_status = gr.JSON(label="Scene Details")

        # Tab 3: Regenerate Scene
        with gr.Tab("3️⃣ Tạo lại cảnh"):
            gr.Markdown("""
            ### 🔄 Regenerate Individual Scene
            - Chọn số scene muốn tạo lại
            - Click "Tạo lại" để regenerate với cùng prompt
            - Video mới sẽ thay thế video cũ
            """)

            with gr.Row():
                with gr.Column(scale=1):
                    regenerate_scene_number = gr.Number(
                        label="Số scene muốn tạo lại",
                        value=1,
                        minimum=1,
                        step=1,
                        precision=0
                    )
                    regenerate_btn = gr.Button("🔄 Tạo lại scene này", variant="primary", size="lg")

                    regenerate_output = gr.Textbox(
                        label="📋 Tiến trình",
                        lines=20,
                        max_lines=25,
                        elem_classes="log-box"
                    )

                with gr.Column(scale=1):
                    regenerate_screenshot = gr.Image(
                        label="📸 Màn hình Comet",
                        type="filepath",
                        height=300
                    )

                    regenerate_video = gr.Video(
                        label="🎬 Video mới",
                        autoplay=True,
                        height=300
                    )

            regenerate_gallery = gr.Gallery(
                label="🎥 Tất cả videos (đã cập nhật)",
                show_label=True,
                columns=4,
                rows=2,
                height="auto",
                interactive=False
            )

        # Tab 4: Info
        with gr.Tab("ℹ️ Hướng dẫn"):
            gr.Markdown("""
            ## 📖 Hướng dẫn sử dụng

            ### Bước 1: Tạo kịch bản
            1. Nhập chủ đề phim
            2. Chọn thời lượng (phút)
            3. Nhập Project ID hoặc để mặc định
            4. Click "Tạo kịch bản"

            ### Bước 2: Tạo video
            1. Chuyển sang tab "Tạo Video (Comet)"
            2. Click "Bắt đầu sản xuất"
            3. **Comet browser sẽ mở** - bạn có thể quan sát
            4. Đợi tất cả videos được tạo

            ### 🌐 Về Comet Browser:
            - Tool sử dụng Comet để bạn có thể debug
            - Cửa sổ browser sẽ hiển thị trong quá trình chạy
            - Có thể inspect page và xem lỗi nếu có

            ### ⚠️ Lưu ý quan trọng:
            - Flow hiện tại mặc định tạo **2 videos** cho mỗi prompt (setting x2)
            - Automation chưa thể thay đổi setting này
            - Videos sẽ được lưu trên Flow, download manual nếu cần

            ### 📁 Files cần có:
            - `cookie.txt` - Cookies từ Flow (export từ browser)
            - `.env` - Chứa GEMINI_API_KEY

            ### 🔧 Khắc phục sự cố:
            - Nếu lỗi cookies: Export lại từ Chrome/Comet
            - Nếu lỗi project: Dùng Project ID mặc định
            - Nếu video không tạo được: Kiểm tra Comet window để debug
            """)

    # Event handlers
    generate_btn.click(
        fn=generate_script_wrapper,
        inputs=[topic_input, duration, cookies_input, project_id_input],
        outputs=[script_output, scene_list, script_data]
    )

    produce_btn.click(
        fn=produce_videos_wrapper,
        inputs=[cookies_input],
        outputs=[production_output, scene_status, current_scene_image, selected_video, video_gallery]
    )

    regenerate_btn.click(
        fn=regenerate_single_scene,
        inputs=[regenerate_scene_number, cookies_input],
        outputs=[regenerate_output, regenerate_screenshot, regenerate_video, regenerate_gallery]
    )

if __name__ == "__main__":
    print("="*80)
    print("🎬 VEO 3.1 COMPLETE TOOL - COMET BROWSER MODE")
    print("="*80)
    print()
    print("🌐 Starting server at http://localhost:7860")
    print("🔍 Comet browser will open during video production for debugging")
    print()
    print("📖 Features:")
    print("  - Generate movie script with Gemini 2.0 Flash")
    print("  - Create videos with VEO 3.1")
    print("  - Run with Comet browser (visible for debugging)")
    print("  - Download videos from Flow (manual)")
    print()
    print("⚠️  Note: Flow creates 2 videos per prompt (x2 setting)")
    print("="*80)
    print()

    app.queue().launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
