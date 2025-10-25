"""
VEO 3.1 Auto UI - Hoàn toàn tự động
Workflow: Nhập chủ đề → Tự động tạo video → Xem kết quả
"""

import gradio as gr
import os
import asyncio
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from src.script_generator import ScriptGenerator
from src.browser_automation.flow_controller import FlowController
from src.video_assembler import VideoAssembler

# Load environment
load_dotenv()

# Global variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
script_generator = None

if GEMINI_API_KEY:
    script_generator = ScriptGenerator(GEMINI_API_KEY)

# Global state để share giữa các tabs
class ProjectState:
    def __init__(self):
        self.script = None
        self.script_file = None
        self.video_urls = []
        self.download_dir = None
        self.final_video = None

project_state = ProjectState()


# ========== Full Auto Workflow ==========

async def full_auto_workflow_async(topic: str, duration: int, scene_duration: int, cookies_file: str, progress=gr.Progress()):
    """Complete automated workflow - từ chủ đề đến video hoàn chỉnh"""
    try:
        if not script_generator:
            yield "❌ Chưa có API key trong .env", None, None
            return

        if not topic:
            yield "❌ Vui lòng nhập chủ đề video", None, None
            return

        if not cookies_file or not os.path.exists(cookies_file):
            yield "❌ Vui lòng cung cấp file cookies.json", None, None
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_dir = f"./data/auto_projects/{timestamp}"
        os.makedirs(project_dir, exist_ok=True)

        # ===== BƯỚC 1: TẠO KỊCH BẢN =====
        progress(0.1, desc="📝 Đang tạo kịch bản...")
        yield "📝 Bước 1/4: Đang tạo kịch bản AI...", None, None

        script = script_generator.generate_script(
            topic=topic,
            duration=duration,
            scene_duration=scene_duration,
            style="Cinematic",
            aspect_ratio="16:9"
        )

        # Save script
        script_file = os.path.join(project_dir, "script.json")
        with open(script_file, 'w', encoding='utf-8') as f:
            json.dump(script, f, ensure_ascii=False, indent=2)

        project_state.script = script
        project_state.script_file = script_file

        num_scenes = len(script['scenes'])
        yield f"""✅ Kịch bản đã tạo!

📝 Tiêu đề: {script['title']}
🎬 Số cảnh: {num_scenes}
⏱️ Tổng thời lượng: {duration}s

📝 Kịch bản chi tiết:
{chr(10).join([f"  Scene {i+1}: {scene['description']}" for i, scene in enumerate(script['scenes'])])}

Đang chuyển sang bước 2...""", None, None

        # ===== BƯỚC 2: TẠO VIDEO =====
        progress(0.3, desc=f"🎬 Đang tạo {num_scenes} video...")
        yield f"🎬 Bước 2/4: Đang tạo {num_scenes} video...\n\n(Quá trình này mất 3-5 phút)", None, None

        # Initialize controller
        download_dir = os.path.join(project_dir, "videos")
        os.makedirs(download_dir, exist_ok=True)

        controller = FlowController(cookies_file, download_dir, headless=False)
        await controller.start()

        video_results = []
        for i, scene in enumerate(script['scenes']):
            scene_num = i + 1
            progress((0.3 + (i / num_scenes) * 0.4), desc=f"🎬 Scene {scene_num}/{num_scenes}")

            yield f"""🎬 Bước 2/4: Đang tạo video...

Scene {scene_num}/{num_scenes}: {scene['description']}
Status: Đang tạo...""", None, None

            try:
                # Create video
                video_url = await controller.create_video_from_prompt(
                    prompt=scene['veo_prompt'],
                    duration=scene['duration'],
                    aspect_ratio=script.get('aspect_ratio', '16:9')
                )

                if video_url:
                    video_results.append({
                        'scene': scene_num,
                        'url': video_url,
                        'status': 'success'
                    })
                    yield f"""🎬 Bước 2/4: Đang tạo video...

Scene {scene_num}/{num_scenes}: ✅ Hoàn thành
URL: {video_url}

Tiếp tục scene tiếp theo...""", None, None
                else:
                    video_results.append({
                        'scene': scene_num,
                        'url': None,
                        'status': 'failed'
                    })

            except Exception as e:
                video_results.append({
                    'scene': scene_num,
                    'url': None,
                    'status': 'error',
                    'error': str(e)
                })

        project_state.video_urls = video_results

        # Save video URLs
        urls_file = os.path.join(project_dir, "video_urls.json")
        with open(urls_file, 'w', encoding='utf-8') as f:
            json.dump(video_results, f, ensure_ascii=False, indent=2)

        success_count = sum(1 for v in video_results if v['status'] == 'success')

        yield f"""✅ Tạo video hoàn thành!

Thành công: {success_count}/{num_scenes} video
{chr(10).join([f"  Scene {v['scene']}: {'✅' if v['status'] == 'success' else '❌'}" for v in video_results])}

Đang chuyển sang bước 3...""", None, None

        # ===== BƯỚC 3: TẢI VIDEO =====
        progress(0.7, desc="📥 Đang tải video...")
        yield f"📥 Bước 3/4: Đang tải {success_count} video về máy...", None, None

        downloaded_files = []
        for i, result in enumerate(video_results):
            if result['status'] != 'success' or not result['url']:
                continue

            scene_num = result['scene']
            progress((0.7 + (i / num_scenes) * 0.2), desc=f"📥 Tải scene {scene_num}")

            try:
                # Download with 1080p upscale
                filename = f"scene_{scene_num:03d}.mp4"
                filepath = await controller.download_video_from_ui(
                    video_url=result['url'],
                    quality="1080p",  # Try 1080p first
                    filename=filename
                )

                if filepath and os.path.exists(filepath):
                    downloaded_files.append(filepath)
                    yield f"""📥 Bước 3/4: Đang tải video...

Scene {scene_num}: ✅ Downloaded (1080p)
File: {filename}""", None, None
                else:
                    # Try 720p fallback
                    filepath = await controller.download_video_from_ui(
                        video_url=result['url'],
                        quality="720p",
                        filename=filename
                    )
                    if filepath:
                        downloaded_files.append(filepath)
                        yield f"""📥 Bước 3/4: Đang tải video...

Scene {scene_num}: ⚠️ Downloaded (720p - fallback)
File: {filename}""", None, None

            except Exception as e:
                yield f"❌ Scene {scene_num}: Lỗi tải - {str(e)}", None, None

        await controller.close()
        project_state.download_dir = download_dir

        yield f"""✅ Tải video hoàn thành!

Đã tải: {len(downloaded_files)}/{success_count} video
Thư mục: {download_dir}

Đang nối video...""", None, None

        # ===== BƯỚC 4: NỐI VIDEO =====
        if not downloaded_files:
            yield "❌ Không có video nào để nối", None, None
            return

        progress(0.9, desc="🎞️ Đang nối video...")
        yield "🎞️ Bước 4/4: Đang nối video thành file hoàn chỉnh...", None, None

        final_path = os.path.join(project_dir, f"final_video.mp4")

        assembler = VideoAssembler()
        assembled_path = assembler.assemble_videos(
            video_files=sorted(downloaded_files),
            output_path=final_path,
            script=script
        )

        project_state.final_video = assembled_path

        if assembled_path and os.path.exists(assembled_path):
            progress(1.0, desc="✅ Hoàn thành!")

            script_summary = f"""
📝 **Kịch bản**: {script['title']}
🎬 **Số cảnh**: {num_scenes}
⏱️ **Tổng thời lượng**: {duration}s

📹 **Video đã tạo**: {success_count}/{num_scenes}
📥 **Đã tải về**: {len(downloaded_files)} files
🎞️ **Video cuối**: {os.path.basename(assembled_path)}

📂 **Thư mục dự án**: {project_dir}
"""

            yield f"""🎉 HOÀN THÀNH!

{script_summary}

✅ Video đã sẵn sàng để upload YouTube!
""", assembled_path, script_summary
        else:
            yield "❌ Lỗi khi nối video", None, None

    except Exception as e:
        yield f"❌ Lỗi: {str(e)}", None, None


def full_auto_workflow(topic: str, duration: int, scene_duration: int, cookies_file: str, progress=gr.Progress()):
    """Wrapper for async workflow"""
    return asyncio.run(full_auto_workflow_async(topic, duration, scene_duration, cookies_file, progress))


# ========== Individual Steps (cho advanced users) ==========

def generate_script_only(topic: str, duration: int, scene_duration: int):
    """Chỉ tạo kịch bản"""
    try:
        if not script_generator:
            return "❌ Chưa có API key", None

        script = script_generator.generate_script(
            topic=topic,
            duration=duration,
            scene_duration=scene_duration,
            style="Cinematic",
            aspect_ratio="16:9"
        )

        # Save to state
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("./data/scripts", exist_ok=True)
        script_file = f"./data/scripts/script_{timestamp}.json"

        with open(script_file, 'w', encoding='utf-8') as f:
            json.dump(script, f, ensure_ascii=False, indent=2)

        project_state.script = script
        project_state.script_file = script_file

        summary = f"""✅ Kịch bản đã tạo!

📝 {script['title']}
🎬 {len(script['scenes'])} cảnh
⏱️ {duration}s

Chi tiết:
{chr(10).join([f"  Scene {i+1}: {s['description']}" for i, s in enumerate(script['scenes'])])}

📄 File: {script_file}
"""
        return summary, script_file

    except Exception as e:
        return f"❌ Lỗi: {str(e)}", None


# ========== Create UI ==========

def create_ui():
    """Create auto UI"""

    custom_css = """
    .gradio-container {
        max-width: 1400px !important;
    }
    .big-button {
        font-size: 18px !important;
        padding: 20px !important;
        font-weight: 700 !important;
    }
    """

    with gr.Blocks(
        title="VEO 3.1 Auto",
        theme=gr.themes.Soft(primary_hue="blue"),
        css=custom_css
    ) as app:

        gr.Markdown("""
        # 🎬 VEO 3.1 - Tự động hoàn toàn
        ### Nhập chủ đề → AI tạo video hoàn chỉnh
        """)

        # ===== TAB 1: AUTO MODE =====
        with gr.Tab("🚀 Tự động hoàn toàn"):
            gr.Markdown("""
            ## Quy trình 1 nút - Hoàn toàn tự động
            Chỉ cần nhập chủ đề, tool sẽ tự động:
            1. Tạo kịch bản AI
            2. Sinh video cho từng cảnh
            3. Tải video về (1080p)
            4. Nối thành video hoàn chỉnh

            **⏱️ Thời gian**: 10-15 phút (tùy số cảnh)
            """)

            with gr.Row():
                with gr.Column(scale=2):
                    topic_auto = gr.Textbox(
                        label="🎯 Chủ đề video",
                        placeholder="VD: Hướng dẫn nấu món phở Việt Nam",
                        value="Hướng dẫn nấu món phở Việt Nam truyền thống - từ hầm xương đến hoàn thiện tô phở",
                        lines=3
                    )

                    with gr.Row():
                        duration_auto = gr.Slider(
                            label="⏱️ Tổng thời lượng (giây)",
                            minimum=20,
                            maximum=90,
                            value=40,
                            step=10
                        )
                        scene_duration_auto = gr.Slider(
                            label="🎬 Thời lượng mỗi cảnh (giây)",
                            minimum=5,
                            maximum=15,
                            value=8,
                            step=1
                        )

                    cookies_auto = gr.Textbox(
                        label="🔑 File cookies.json",
                        value="./cookie.txt"
                    )

                with gr.Column(scale=1):
                    gr.Markdown("""
                    ### 💡 Tips

                    **Chủ đề tốt**:
                    - Cụ thể và rõ ràng
                    - Mô tả đầy đủ nội dung
                    - VD: "Review chi tiết iPhone 16 Pro"

                    **Thời lượng**:
                    - Short-form: 20-30s
                    - YouTube: 40-60s
                    - Long-form: 70-90s

                    **Mỗi cảnh**:
                    - Ngắn gọn: 5-6s
                    - Standard: 8-10s
                    - Chi tiết: 12-15s
                    """)

            run_auto_btn = gr.Button(
                "🚀 BẮT ĐẦU TẠO VIDEO TỰ ĐỘNG",
                variant="primary",
                size="lg",
                elem_classes="big-button"
            )

            progress_auto = gr.Textbox(
                label="📊 Tiến trình",
                lines=15,
                interactive=False
            )

            with gr.Row():
                final_video_auto = gr.Video(label="🎞️ Video hoàn chỉnh")
                summary_auto = gr.Markdown(label="📋 Tổng kết")

            run_auto_btn.click(
                fn=full_auto_workflow,
                inputs=[topic_auto, duration_auto, scene_duration_auto, cookies_auto],
                outputs=[progress_auto, final_video_auto, summary_auto]
            )

        # ===== TAB 2: MANUAL MODE =====
        with gr.Tab("⚙️ Chế độ thủ công"):
            gr.Markdown("""
            ## Chế độ nâng cao - Kiểm soát từng bước
            Cho người dùng muốn kiểm tra kịch bản trước khi tạo video
            """)

            gr.Markdown("### Bước 1: Tạo kịch bản")

            topic_manual = gr.Textbox(
                label="Chủ đề",
                value="Hướng dẫn pha cà phê espresso ngon",
                lines=2
            )

            with gr.Row():
                duration_manual = gr.Slider(20, 90, 40, step=10, label="Tổng thời lượng")
                scene_duration_manual = gr.Slider(5, 15, 8, step=1, label="Mỗi cảnh")

            gen_script_btn = gr.Button("📝 Tạo kịch bản", variant="primary")

            script_status = gr.Textbox(label="Kết quả", lines=12, interactive=False)
            script_file_out = gr.File(label="📥 File kịch bản")

            gen_script_btn.click(
                fn=generate_script_only,
                inputs=[topic_manual, duration_manual, scene_duration_manual],
                outputs=[script_status, script_file_out]
            )

            gr.Markdown("### Bước 2-4: Sử dụng Tab Tự động")
            gr.Markdown("Sau khi kiểm tra kịch bản OK, quay lại tab **Tự động hoàn toàn** để tạo video")

        # ===== FOOTER =====
        gr.Markdown("""
        ---
        ### 📚 Hướng dẫn nhanh

        **Quy trình đơn giản**:
        1. Nhập chủ đề vào tab "Tự động hoàn toàn"
        2. Nhấn "Bắt đầu tạo video tự động"
        3. Đợi 10-15 phút
        4. Tải video hoàn chỉnh!

        **Quy trình kiểm soát**:
        1. Tab "Thủ công": Tạo kịch bản → Kiểm tra
        2. Nếu OK → Quay lại tab "Tự động" để tạo video

        ---
        ✅ **API Key**: Đã cấu hình
        🔑 **Cookies**: Cần extract từ browser (xem [hướng dẫn](./README_SIMPLE.md))
        """)

    return app


# ========== Main ==========

if __name__ == "__main__":
    print("="*70)
    print("🎬 VEO 3.1 Auto UI - Tự động hoàn toàn")
    print("="*70)
    print("\n✅ API Key:", "Configured" if GEMINI_API_KEY else "Not found")
    print("\n🚀 Launching UI...")
    print("📍 URL: http://localhost:7860")
    print("\n💡 Quy trình:")
    print("   1. Nhập chủ đề")
    print("   2. Nhấn 'Bắt đầu tạo video tự động'")
    print("   3. Đợi 10-15 phút")
    print("   4. Done!")
    print("="*70)

    app = create_ui()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
