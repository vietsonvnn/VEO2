"""
VEO 3.1 - Complete UI với Scene Preview & Regenerate
"""

import gradio as gr
import os
import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv

from src.script_generator import ScriptGenerator
from src.browser_automation.flow_controller import FlowController
from src.video_assembler import VideoAssembler

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
script_generator = ScriptGenerator(GEMINI_API_KEY) if GEMINI_API_KEY else None

# Global state
class ProjectState:
    def __init__(self):
        self.script = None
        self.scenes = []  # List of scene data
        self.project_dir = None
        self.cookies = None
        self.project_id = None  # Flow project ID

state = ProjectState()

# Step 1: Generate Script
async def generate_script_async(topic, duration_minutes, cookies, project_id):
    try:
        if not script_generator:
            return "❌ Chưa có API key", [], None

        if not topic:
            return "❌ Vui lòng nhập chủ đề", [], None

        # Convert minutes to seconds
        duration = int(duration_minutes * 60)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_dir = f"./data/projects/{timestamp}"
        os.makedirs(f"{project_dir}/videos", exist_ok=True)

        script = script_generator.generate_script(
            topic=topic,
            duration=duration,
            scene_duration=8,
            style="Cinematic",
            aspect_ratio="16:9"
        )

        # Save to state
        state.script = script
        state.project_dir = project_dir
        state.cookies = cookies
        state.project_id = project_id.strip() if project_id and project_id.strip() else None
        state.scenes = []
        
        for i, scene in enumerate(script['scenes']):
            state.scenes.append({
                'number': i + 1,
                'prompt': scene['veo_prompt'],
                'description': scene['description'],
                'duration': scene['duration'],
                'status': 'pending',
                'video_path': None,
                'url': None
            })
        
        summary = f"""✅ Kịch bản đã tạo!

📝 {script['title']}
🎬 {len(script['scenes'])} cảnh
⏱️ {duration_minutes} phút ({duration}s)

Nhấn "Tạo tất cả video" để bắt đầu!
"""
        
        # Return scene data for UI update
        scene_updates = []
        for scene in state.scenes:
            scene_updates.append({
                'number': scene['number'],
                'desc': scene['description'],
                'status': '⏳ Chưa tạo'
            })
        
        return summary, scene_updates, script
        
    except Exception as e:
        return f"❌ Lỗi: {str(e)}", [], None

def generate_script(topic, duration, cookies, project_id):
    return asyncio.run(generate_script_async(topic, duration, cookies, project_id))

# Step 2: Generate ALL videos
async def generate_all_videos_async(progress=gr.Progress()):
    try:
        if not state.script or not state.scenes:
            return "❌ Vui lòng tạo kịch bản trước", []

        total_scenes = len(state.scenes)
        status_lines = [
            "="*60,
            "🎬 BẮT ĐẦU SẢN XUẤT PHIM",
            "="*60,
            f"📝 Kịch bản: {state.script['title']}",
            f"🎞️ Tổng số cảnh: {total_scenes}",
            f"⏱️ Thời lượng: {state.script.get('total_duration', 0)}s",
            "="*60,
            ""
        ]

        controller = FlowController(state.cookies, f"{state.project_dir}/videos", headless=False)

        status_lines.append("🚀 Khởi động browser...")
        await controller.start()
        status_lines.append("✅ Browser đã sẵn sàng")

        status_lines.append("🌐 Đang vào trang Flow...")
        await controller.goto_flow()
        status_lines.append("✅ Đã vào trang Flow")

        # Use existing project ID or create new
        DEFAULT_PROJECT_ID = "125966c7-418b-49da-9978-49f0a62356de"

        if state.project_id:
            status_lines.append(f"📁 Sử dụng project có sẵn: {state.project_id}...")
            success = await controller.goto_project(state.project_id)
            if success:
                status_lines.append("✅ Đã vào project")
            else:
                status_lines.append("❌ Không thể vào project. Vui lòng kiểm tra Project ID")
                await controller.close()
                return "\n".join(status_lines), []
        else:
            status_lines.append("📁 Đang tạo project mới...")
            project_id = await controller.create_new_project(state.script['title'])
            if project_id:
                state.project_id = project_id
                status_lines.append(f"✅ Project đã tạo: {project_id}")
                await controller.goto_project(project_id)
                status_lines.append("✅ Đã vào project")
            else:
                status_lines.append("⚠️ Không thể tạo project mới")
                status_lines.append(f"📁 Dùng project mặc định: {DEFAULT_PROJECT_ID}")
                state.project_id = DEFAULT_PROJECT_ID
                success = await controller.goto_project(DEFAULT_PROJECT_ID)
                if success:
                    status_lines.append("✅ Đã vào project mặc định")
                else:
                    status_lines.append("❌ Không thể vào project mặc định")
                    await controller.close()
                    return "\n".join(status_lines), []
        status_lines.append("")

        for i, scene_state in enumerate(state.scenes):
            scene_num = scene_state['number']
            progress((i / total_scenes), desc=f"🎬 Scene {scene_num}/{total_scenes}")

            status_lines.append(f"{'─'*60}")
            status_lines.append(f"🎬 SCENE {scene_num}/{total_scenes}")
            status_lines.append(f"📝 Mô tả: {scene_state['description'][:50]}...")
            status_lines.append("")

            try:
                # Create video
                status_lines.append(f"   ⏳ Đang tạo video (VEO 3.1)...")
                url = await controller.create_video_from_prompt(
                    prompt=scene_state['prompt'],
                    aspect_ratio="16:9",
                    is_first_video=(i == 0)  # First scene needs more wait time
                )

                if url:
                    status_lines.append(f"   ✅ Video đã tạo xong!")

                    # SKIP DOWNLOAD FOR NOW - just mark as completed
                    # Videos are on Flow, can download manually
                    scene_state['status'] = 'completed'
                    scene_state['url'] = url
                    scene_state['video_path'] = f"Flow video #{scene_num}"

                    status_lines.append(f"   ✅ Video có sẵn trên Flow")
                    status_lines.append(f"   💡 Download manual từ Flow nếu cần")
                    status_lines.append(f"   ✨ Scene {scene_num}: HOÀN THÀNH")

                    # TODO: Implement download later
                    # filepath = await controller.download_video_from_ui(...)
                else:
                    scene_state['status'] = 'failed'
                    status_lines.append(f"   ❌ Không thể tạo video")
                    status_lines.append(f"   ⚠️ Scene {scene_num}: THẤT BẠI")

            except Exception as e:
                scene_state['status'] = 'failed'
                status_lines.append(f"   ❌ Lỗi: {str(e)}")
                status_lines.append(f"   ⚠️ Scene {scene_num}: THẤT BẠI")

            status_lines.append("")

        await controller.close()
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
            status_lines.append("🎉 HOÀN THÀNH TOÀN BỘ! Chuyển sang tab 'Xem & tạo lại' để preview")
        elif completed > 0:
            status_lines.append("⚠️ Một số cảnh thất bại. Xem tab 'Xem & tạo lại' để tạo lại")
        else:
            status_lines.append("❌ Tất cả cảnh đều thất bại. Vui lòng kiểm tra cookies và thử lại")

        status_lines.append("="*60)

        # Prepare scene updates for UI
        scene_updates = []
        for scene in state.scenes:
            scene_updates.append({
                'number': scene['number'],
                'video_path': scene['video_path'],
                'status': '✅ Hoàn thành' if scene['status'] == 'completed' else '❌ Lỗi'
            })

        summary = "\n".join(status_lines)
        return summary, scene_updates
        
    except Exception as e:
        return f"❌ Lỗi: {str(e)}", []

def generate_all_videos(progress=gr.Progress()):
    return asyncio.run(generate_all_videos_async(progress))

# Step 3: Regenerate single scene
async def regenerate_scene_async(scene_num, progress=gr.Progress()):
    try:
        if not state.scenes or scene_num < 1 or scene_num > len(state.scenes):
            return f"❌ Scene {scene_num} không hợp lệ", None

        scene_idx = scene_num - 1
        scene_state = state.scenes[scene_idx]

        log = []
        log.append("="*60)
        log.append(f"🔄 TẠO LẠI SCENE {scene_num}")
        log.append("="*60)
        log.append(f"📝 Mô tả: {scene_state['description']}")
        log.append("")

        progress(0.1, desc=f"🚀 Khởi động browser...")
        log.append("🚀 Khởi động browser...")

        controller = FlowController(state.cookies, f"{state.project_dir}/videos", headless=False)
        await controller.start()
        log.append("✅ Browser đã sẵn sàng")

        log.append("🌐 Đang vào trang Flow...")
        await controller.goto_flow()
        log.append("✅ Đã vào trang Flow")

        if state.project_id:
            log.append(f"📁 Đang vào project: {state.project_id}...")
            await controller.goto_project(state.project_id)
            log.append("✅ Đã vào project")
        else:
            log.append("❌ Không tìm thấy project ID")
            await controller.close()
            return "\n".join(log), None
        log.append("")

        progress(0.3, desc=f"⏳ Đang tạo video...")
        log.append("⏳ Đang tạo video với VEO 3.1...")

        # Recreate video
        url = await controller.create_video_from_prompt(
            prompt=scene_state['prompt'],
            aspect_ratio="16:9"
        )

        if url:
            log.append("✅ Video đã tạo xong!")
            log.append("")

            progress(0.7, desc="📥 Đang download...")
            log.append("📥 Đang download video (1080p)...")

            filepath = await controller.download_video_from_ui(
                filename=f"scene_{scene_num:03d}.mp4",
                prompt_text=scene_state['description'],
                quality="1080p"
            )

            if filepath:
                scene_state['status'] = 'completed'
                scene_state['video_path'] = filepath
                scene_state['url'] = url

                log.append("✅ Download hoàn tất!")
                log.append(f"💾 Lưu tại: {os.path.basename(filepath)}")
                log.append("")
                log.append("="*60)
                log.append(f"🎉 Scene {scene_num} đã được tạo lại thành công!")
                log.append("="*60)

                await controller.close()
                return "\n".join(log), filepath

        await controller.close()
        log.append("❌ Không thể tạo video")
        log.append("="*60)
        return "\n".join(log), None

    except Exception as e:
        return f"❌ Lỗi: {str(e)}", None

def regenerate_scene(scene_num, progress=gr.Progress()):
    return asyncio.run(regenerate_scene_async(scene_num, progress))

# Step 4: Assemble final video
async def assemble_final_async(progress=gr.Progress()):
    try:
        if not state.scenes:
            return "❌ Chưa có video", None

        log = []
        log.append("="*60)
        log.append("🎞️ GHÉP PHIM HOÀN CHỈNH")
        log.append("="*60)
        log.append("")

        video_files = []
        for scene in state.scenes:
            if scene['status'] == 'completed' and scene['video_path']:
                video_files.append(scene['video_path'])
                log.append(f"✅ Scene {scene['number']}: {os.path.basename(scene['video_path'])}")

        log.append("")
        log.append(f"📊 Tổng số cảnh: {len(video_files)}/{len(state.scenes)}")

        if not video_files:
            log.append("")
            log.append("❌ Không có video hoàn thành nào để ghép")
            log.append("="*60)
            return "\n".join(log), None

        log.append("")
        log.append("="*60)
        progress(0.3, desc="🔧 Chuẩn bị ghép video...")
        log.append("🔧 Bắt đầu ghép video...")

        final_path = f"{state.project_dir}/final.mp4"
        assembler = VideoAssembler()

        progress(0.5, desc="🎬 Đang nối video...")
        log.append(f"🎬 Đang nối {len(video_files)} cảnh...")

        result = assembler.assemble_videos(
            video_files=video_files,
            output_path=final_path,
            script=state.script
        )

        if result:
            log.append("✅ Nối video hoàn tất!")
            log.append("")
            log.append("="*60)
            log.append("🎉 PHIM HOÀN CHỈNH!")
            log.append("="*60)
            log.append(f"📝 Tên phim: {state.script['title']}")
            log.append(f"🎞️ Số cảnh: {len(video_files)}")
            log.append(f"💾 Lưu tại: {final_path}")
            log.append("="*60)
            log.append("")
            log.append("✨ Phim của bạn đã sẵn sàng! Tải về và thưởng thức!")
            log.append("="*60)

            return "\n".join(log), result
        else:
            log.append("❌ Lỗi khi nối video")
            log.append("="*60)
            return "\n".join(log), None

    except Exception as e:
        return f"❌ Lỗi: {str(e)}", None

def assemble_final(progress=gr.Progress()):
    return asyncio.run(assemble_final_async(progress))

# Modern CSS
css = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif !important; }

.gradio-container {
    max-width: 1400px !important;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
}

.contain {
    background: rgba(255,255,255,0.95) !important;
    backdrop-filter: blur(10px) !important;
    border-radius: 20px !important;
    padding: 30px !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1) !important;
}

.gr-button-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: none !important;
    color: white !important;
    border-radius: 12px !important;
    padding: 14px 28px !important;
    font-weight: 600 !important;
}

.gr-button-primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 16px rgba(102,126,234,0.4) !important;
}

h1 {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700 !important;
}

.scene-card {
    border: 2px solid #e0e0e0;
    border-radius: 12px;
    padding: 15px;
    margin: 10px 0;
}
"""

# Create UI
with gr.Blocks(theme=gr.themes.Glass(), css=css, title="VEO 3.1") as app:
    
    gr.Markdown("# 🎬 VEO 3.1 - Complete Auto")
    
    # Tab 1: Create
    with gr.Tab("1️⃣ Tạo video"):
        gr.Markdown("### Bước 1: Tạo kịch bản")
        
        with gr.Row():
            topic = gr.Textbox(
                label="✨ Chủ đề",
                value="Hướng dẫn nấu món phở Việt Nam truyền thống",
                lines=2
            )
            duration = gr.Slider(0.5, 3, 1, step=0.5, label="⏱️ Thời lượng (phút)")

        with gr.Row():
            cookies = gr.Textbox(label="🔑 Cookies", value="./cookie.txt")
            project_id_input = gr.Textbox(
                label="📁 Project ID (Flow)",
                value="125966c7-418b-49da-9978-49f0a62356de",
                placeholder="Paste Project ID hoặc để mặc định"
            )
        
        gen_script_btn = gr.Button("📝 Tạo kịch bản", variant="primary")
        script_status = gr.Textbox(label="Trạng thái", lines=6)
        
        gr.Markdown("### Bước 2: Tạo tất cả video")
        gen_all_btn = gr.Button("🎬 Tạo tất cả video", variant="primary", size="lg")
        gen_status = gr.Textbox(label="Tiến trình", lines=10)
        
        # Hidden components for state
        script_data = gr.State(None)
        scene_data = gr.State([])
        
        gen_script_btn.click(
            fn=generate_script,
            inputs=[topic, duration, cookies, project_id_input],
            outputs=[script_status, scene_data, script_data]
        )
        
        gen_all_btn.click(
            fn=generate_all_videos,
            inputs=[],
            outputs=[gen_status, scene_data]
        )
    
    # Tab 2: Preview & Regenerate
    with gr.Tab("2️⃣ Xem & tạo lại"):
        gr.Markdown("### Xem video từng cảnh & tạo lại nếu cần")
        
        # Create 10 scene slots
        for i in range(10):
            with gr.Group(visible=False) as scene_group:
                gr.Markdown(f"## Scene {i+1}")
                
                with gr.Row():
                    with gr.Column(scale=2):
                        video_player = gr.Video(label=f"Video Scene {i+1}")
                    with gr.Column(scale=1):
                        scene_desc = gr.Textbox(label="Mô tả", lines=3)
                        scene_status = gr.Textbox(label="Trạng thái")
                        regen_btn = gr.Button(f"🔄 Tạo lại Scene {i+1}")
                        regen_status = gr.Textbox(label="Kết quả", lines=2)
                
                # Regenerate handler
                regen_btn.click(
                    fn=lambda: regenerate_scene(i+1),
                    inputs=[],
                    outputs=[regen_status, video_player]
                )
    
    # Tab 3: Final
    with gr.Tab("3️⃣ Video cuối"):
        gr.Markdown("### Nối tất cả cảnh thành video hoàn chỉnh")
        
        assemble_btn = gr.Button("🎞️ Nối video", variant="primary", size="lg")
        final_status = gr.Textbox(label="Trạng thái", lines=3)
        final_video = gr.Video(label="Video hoàn chỉnh")
        
        assemble_btn.click(
            fn=assemble_final,
            inputs=[],
            outputs=[final_status, final_video]
        )
    
    gr.Markdown("""
    ---
    <div style='text-align:center; color:#666; padding:10px;'>
    ✅ API: OK | 🔑 Cookies: cookie.txt | 🎨 Modern Glass Theme
    </div>
    """)

if __name__ == "__main__":
    print("🎬 VEO 3.1 Complete")
    print("URL: http://localhost:7860")
    app.launch(server_name="0.0.0.0", server_port=7860, share=False)
