"""
VEO 3.1 Complete Automation System
Hệ thống tự động hóa hoàn chỉnh cho VEO 3.1
"""

import gradio as gr
import os
import sys
import io
import json
import asyncio
from datetime import datetime
from pathlib import Path
import shutil
from typing import Dict, List, Optional

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from dotenv import load_dotenv
from src.script_generator import ScriptGenerator
from src.browser_automation.flow_controller import FlowController
from src.video_assembler import VideoAssembler

# Load environment
load_dotenv()

# ========== Global State Management ==========

class ProjectState:
    """Manages the complete project state"""
    def __init__(self):
        self.project_id = None
        self.project_name = None
        self.gemini_api_key = None
        self.output_folder = "./data/projects"
        self.model = "gemini-2.0-flash-exp"
        self.script = None
        self.scenes = []  # List of scene states
        self.seo_content = None
        self.final_video_path = None

    def create_new_project(self, project_name: str):
        """Initialize a new project"""
        self.project_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.project_name = project_name
        project_dir = os.path.join(self.output_folder, f"{self.project_id}_{project_name}")
        os.makedirs(project_dir, exist_ok=True)
        os.makedirs(os.path.join(project_dir, "scenes"), exist_ok=True)
        os.makedirs(os.path.join(project_dir, "downloads"), exist_ok=True)
        return project_dir

    def get_project_dir(self):
        """Get current project directory"""
        if not self.project_id or not self.project_name:
            return None
        return os.path.join(self.output_folder, f"{self.project_id}_{self.project_name}")

    def save_state(self):
        """Save project state to file"""
        project_dir = self.get_project_dir()
        if not project_dir:
            return

        state_file = os.path.join(project_dir, "project_state.json")
        state_data = {
            "project_id": self.project_id,
            "project_name": self.project_name,
            "model": self.model,
            "script": self.script,
            "scenes": self.scenes,
            "seo_content": self.seo_content,
            "final_video_path": self.final_video_path,
            "last_updated": datetime.now().isoformat()
        }

        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, ensure_ascii=False, indent=2)

    def load_state(self, project_dir: str):
        """Load project state from file"""
        state_file = os.path.join(project_dir, "project_state.json")
        if not os.path.exists(state_file):
            return False

        with open(state_file, 'r', encoding='utf-8') as f:
            state_data = json.load(f)

        self.project_id = state_data.get("project_id")
        self.project_name = state_data.get("project_name")
        self.model = state_data.get("model", "gemini-2.0-flash-exp")
        self.script = state_data.get("script")
        self.scenes = state_data.get("scenes", [])
        self.seo_content = state_data.get("seo_content")
        self.final_video_path = state_data.get("final_video_path")

        return True

# Global project state
project = ProjectState()


# ========== API Key Management ==========

def load_api_key_from_file(file_path: str) -> tuple:
    """Load API key from TXT file"""
    try:
        if not file_path:
            return "❌ Vui lòng chọn file API key", None

        with open(file_path, 'r', encoding='utf-8') as f:
            api_key = f.read().strip()

        if not api_key:
            return "❌ File rỗng, không có API key", None

        # Test API key by creating ScriptGenerator
        try:
            generator = ScriptGenerator(api_key)
            project.gemini_api_key = api_key

            # Save to .env
            env_path = ".env"
            env_content = f"GEMINI_API_KEY={api_key}\n"

            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    lines = f.readlines()

                updated = False
                for i, line in enumerate(lines):
                    if line.startswith("GEMINI_API_KEY="):
                        lines[i] = env_content
                        updated = True
                        break

                if not updated:
                    lines.append(env_content)

                with open(env_path, 'w') as f:
                    f.writelines(lines)
            else:
                with open(env_path, 'w') as f:
                    f.write(env_content)

            return f"✅ API key đã được tải thành công!\n\nKey: {api_key[:20]}...{api_key[-10:]}", api_key

        except Exception as e:
            return f"❌ API key không hợp lệ: {str(e)}", None

    except Exception as e:
        return f"❌ Lỗi đọc file: {str(e)}", None


# ========== Project Initialization ==========

def initialize_project(project_name: str, output_folder: str, model: str) -> str:
    """Initialize a new project"""
    try:
        if not project_name:
            return "❌ Vui lòng nhập tên dự án"

        if not project.gemini_api_key:
            return "❌ Vui lòng tải API key trước"

        project.output_folder = output_folder or "./data/projects"
        project.model = model

        project_dir = project.create_new_project(project_name)
        project.save_state()

        return f"""✅ Dự án đã được khởi tạo!

📁 **Tên dự án**: {project_name}
🆔 **Project ID**: {project_id}
📂 **Thư mục**: {project_dir}
🤖 **Model**: {model}

Bạn có thể bắt đầu tạo kịch bản ở tab tiếp theo.
"""

    except Exception as e:
        return f"❌ Lỗi khởi tạo dự án: {str(e)}"


# ========== Enhanced Script Generation ==========

def generate_script_with_characters(
    topic: str,
    duration: int,
    scene_duration: int,
    style: str,
    aspect_ratio: str,
    character_mode: str,
    character_images: Optional[List] = None,
    character_descriptions: str = ""
) -> tuple:
    """Generate script with character support"""
    try:
        if not project.gemini_api_key:
            return "❌ Vui lòng tải API key trước", None, ""

        if not topic:
            return "❌ Vui lòng nhập chủ đề video", None, ""

        if not project.project_id:
            return "❌ Vui lòng khởi tạo dự án trước", None, ""

        # Create script generator
        generator = ScriptGenerator(project.gemini_api_key)

        # Build character context
        character_context = ""
        if character_mode == "AI tự nhận diện":
            character_context = "AI sẽ tự động tạo và duy trì nhất quán các nhân vật trong video."
        elif character_mode == "Upload ảnh nhân vật":
            if character_images:
                # Save character images to project
                project_dir = project.get_project_dir()
                char_dir = os.path.join(project_dir, "characters")
                os.makedirs(char_dir, exist_ok=True)

                saved_chars = []
                for idx, img in enumerate(character_images):
                    if img:
                        char_path = os.path.join(char_dir, f"character_{idx+1}.jpg")
                        shutil.copy(img, char_path)
                        saved_chars.append(char_path)

                character_context = f"Sử dụng {len(saved_chars)} nhân vật từ ảnh đã upload. "

            if character_descriptions:
                character_context += f"Mô tả nhân vật: {character_descriptions}"

        # Generate script with character context
        enhanced_topic = f"{topic}\n\n{character_context}" if character_context else topic

        script = generator.generate_script(
            topic=enhanced_topic,
            duration=duration,
            scene_duration=scene_duration,
            style=style,
            aspect_ratio=aspect_ratio
        )

        # Save script
        project.script = script
        project_dir = project.get_project_dir()
        script_file = os.path.join(project_dir, "script.json")

        with open(script_file, 'w', encoding='utf-8') as f:
            json.dump(script, f, ensure_ascii=False, indent=2)

        # Initialize scene states
        project.scenes = []
        for i, scene in enumerate(script['scenes']):
            project.scenes.append({
                "scene_index": i,
                "scene_number": i + 1,
                "prompt": scene['veo_prompt'],
                "description": scene['description'],
                "duration": scene['duration'],
                "status": "pending",  # pending, generating, completed, failed, rejected
                "video_url": None,
                "download_path": None,
                "error": None,
                "approved": False
            })

        project.save_state()

        # Format output
        script_json = json.dumps(script, ensure_ascii=False, indent=2)

        summary = f"""✅ Kịch bản đã được tạo!

📝 **Tổng số cảnh**: {len(script['scenes'])}
⏱️ **Tổng thời lượng**: {duration}s
🎬 **Style**: {style}
📐 **Tỷ lệ**: {aspect_ratio}

Kịch bản đã được lưu vào: {script_file}
"""

        return summary, script_json, script_file

    except Exception as e:
        return f"❌ Lỗi tạo kịch bản: {str(e)}", None, ""


# ========== SEO Content Generator ==========

def generate_seo_content(script_json: str) -> tuple:
    """Generate SEO content for YouTube"""
    try:
        if not script_json:
            return "❌ Chưa có kịch bản", ""

        script = json.loads(script_json)

        # Generate title
        title = script.get('title', 'Video tự động từ VEO 3.1')

        # Generate description
        description_lines = [
            f"🎬 {title}",
            "",
            "📝 Mô tả:",
            script.get('description', ''),
            "",
            "🎯 Các cảnh trong video:",
        ]

        for i, scene in enumerate(script.get('scenes', []), 1):
            description_lines.append(f"{i}. {scene.get('description', '')}")

        description_lines.extend([
            "",
            "🤖 Video được tạo tự động bằng VEO 3.1",
            "",
            "#VEO #AI #VideoGeneration #AutomatedVideo"
        ])

        description = "\n".join(description_lines)

        # Generate tags
        tags = [
            "VEO 3.1",
            "AI Video",
            "Video tự động",
            "Generative AI",
            script.get('style', 'Cinematic'),
        ]

        # Add keywords from scenes
        for scene in script.get('scenes', []):
            words = scene.get('description', '').split()[:3]
            tags.extend(words)

        tags = list(set(tags))[:15]  # Limit to 15 unique tags
        tags_text = ", ".join(tags)

        # Generate thumbnail prompt
        first_scene = script.get('scenes', [{}])[0]
        thumbnail_prompt = f"Tạo thumbnail cho video: {title}. Cảnh chính: {first_scene.get('description', '')}. Style: {script.get('style', 'Cinematic')}, bold text overlay với tiêu đề, high quality, eye-catching"

        # Build SEO content
        seo_content = f"""TIÊU ĐỀ:
{title}

MÔ TẢ:
{description}

TAGS:
{tags_text}

THUMBNAIL PROMPT:
{thumbnail_prompt}
"""

        # Save SEO content
        project.seo_content = seo_content
        project_dir = project.get_project_dir()
        if project_dir:
            seo_file = os.path.join(project_dir, "seo_content.txt")
            with open(seo_file, 'w', encoding='utf-8') as f:
                f.write(seo_content)

            project.save_state()

            return f"✅ Nội dung SEO đã được tạo và lưu vào:\n{seo_file}", seo_content

        return "✅ Nội dung SEO đã được tạo", seo_content

    except Exception as e:
        return f"❌ Lỗi tạo SEO: {str(e)}", ""


# ========== Video Generation with Progress ==========

async def generate_all_videos_async(cookies_file: str, headless: bool = True) -> str:
    """Generate videos for all scenes"""
    try:
        if not project.script:
            return "❌ Chưa có kịch bản"

        if not os.path.exists(cookies_file):
            return f"❌ File cookies không tồn tại: {cookies_file}"

        project_dir = project.get_project_dir()
        download_dir = os.path.join(project_dir, "downloads")

        # Initialize controller
        controller = FlowController(cookies_file, download_dir, headless=headless)

        # Generate videos for each scene
        results = []
        for i, scene_state in enumerate(project.scenes):
            scene = project.script['scenes'][i]

            # Update status
            scene_state['status'] = 'generating'
            project.save_state()

            try:
                # Generate video
                video_url = await controller.generate_video_flow(
                    prompt=scene['veo_prompt'],
                    duration=scene['duration'],
                    aspect_ratio=project.script.get('aspect_ratio', '16:9')
                )

                if video_url:
                    scene_state['status'] = 'completed'
                    scene_state['video_url'] = video_url
                    results.append(f"✅ Scene {i+1}: Hoàn thành")
                else:
                    scene_state['status'] = 'failed'
                    scene_state['error'] = 'Không tạo được video'
                    results.append(f"❌ Scene {i+1}: Thất bại")

            except Exception as e:
                scene_state['status'] = 'failed'
                scene_state['error'] = str(e)
                results.append(f"❌ Scene {i+1}: Lỗi - {str(e)}")

            project.save_state()

        await controller.close()

        summary = "\n".join(results)
        return f"🎬 Kết quả tạo video:\n\n{summary}"

    except Exception as e:
        return f"❌ Lỗi: {str(e)}"


def generate_all_videos(cookies_file: str, headless: bool = True) -> str:
    """Wrapper for async video generation"""
    return asyncio.run(generate_all_videos_async(cookies_file, headless))


# ========== Video Download with Auto-Upscale ==========

async def download_all_videos_async(quality: str = "1080p") -> str:
    """Download all generated videos with auto-upscale"""
    try:
        if not project.scenes:
            return "❌ Chưa có video nào được tạo"

        cookies_file = os.path.join(project.get_project_dir(), "../../../config/cookies.json")
        download_dir = os.path.join(project.get_project_dir(), "downloads")

        controller = FlowController(cookies_file, download_dir, headless=True)

        results = []
        for scene_state in project.scenes:
            if scene_state['status'] != 'completed' or not scene_state.get('approved', True):
                continue

            scene_num = scene_state['scene_number']

            try:
                # Try 1080p first
                file_path = await controller.download_video_flow(
                    video_url=scene_state['video_url'],
                    quality="1080p",
                    filename=f"scene_{scene_num:03d}_1080p.mp4"
                )

                if file_path:
                    scene_state['download_path'] = file_path
                    results.append(f"✅ Scene {scene_num}: Downloaded 1080p")
                else:
                    # Fallback to 720p
                    file_path = await controller.download_video_flow(
                        video_url=scene_state['video_url'],
                        quality="720p",
                        filename=f"scene_{scene_num:03d}_720p.mp4"
                    )

                    if file_path:
                        scene_state['download_path'] = file_path
                        results.append(f"⚠️ Scene {scene_num}: Downloaded 720p (1080p failed)")
                    else:
                        results.append(f"❌ Scene {scene_num}: Download failed")

            except Exception as e:
                results.append(f"❌ Scene {scene_num}: Error - {str(e)}")

            project.save_state()

        await controller.close()

        summary = "\n".join(results)
        return f"📥 Kết quả tải video:\n\n{summary}"

    except Exception as e:
        return f"❌ Lỗi: {str(e)}"


def download_all_videos(quality: str = "1080p") -> str:
    """Wrapper for async download"""
    return asyncio.run(download_all_videos_async(quality))


# ========== Video Preview & Approval ==========

def get_scene_preview_data(scene_index: int) -> tuple:
    """Get preview data for a specific scene"""
    try:
        if scene_index >= len(project.scenes):
            return None, "❌ Scene không tồn tại", ""

        scene = project.scenes[scene_index]

        # Build status text
        status_text = f"""**Scene {scene['scene_number']}**
Status: {scene['status']}
Prompt: {scene['prompt'][:100]}...

Approved: {'✅' if scene.get('approved', False) else '❌'}
"""

        if scene.get('error'):
            status_text += f"\nError: {scene['error']}"

        # Get video path if available
        video_path = scene.get('download_path')

        return video_path, status_text, scene['prompt']

    except Exception as e:
        return None, f"❌ Error: {str(e)}", ""


def approve_scene(scene_index: int) -> str:
    """Approve a scene video"""
    try:
        if scene_index >= len(project.scenes):
            return "❌ Scene không tồn tại"

        project.scenes[scene_index]['approved'] = True
        project.save_state()

        return f"✅ Scene {scene_index + 1} đã được phê duyệt"

    except Exception as e:
        return f"❌ Error: {str(e)}"


def reject_scene(scene_index: int) -> str:
    """Reject a scene video (mark for regeneration)"""
    try:
        if scene_index >= len(project.scenes):
            return "❌ Scene không tồn tại"

        project.scenes[scene_index]['approved'] = False
        project.scenes[scene_index]['status'] = 'rejected'
        project.save_state()

        return f"❌ Scene {scene_index + 1} đã bị từ chối, cần tạo lại"

    except Exception as e:
        return f"❌ Error: {str(e)}"


async def regenerate_scene_async(scene_index: int, cookies_file: str) -> str:
    """Regenerate a specific scene"""
    try:
        if scene_index >= len(project.scenes):
            return "❌ Scene không tồn tại"

        scene_state = project.scenes[scene_index]
        scene = project.script['scenes'][scene_index]

        # Reset status
        scene_state['status'] = 'generating'
        scene_state['error'] = None
        project.save_state()

        # Initialize controller
        download_dir = os.path.join(project.get_project_dir(), "downloads")
        controller = FlowController(cookies_file, download_dir, headless=True)

        # Generate video
        video_url = await controller.generate_video_flow(
            prompt=scene['veo_prompt'],
            duration=scene['duration'],
            aspect_ratio=project.script.get('aspect_ratio', '16:9')
        )

        if video_url:
            scene_state['status'] = 'completed'
            scene_state['video_url'] = video_url
            scene_state['approved'] = False  # Need review again
            project.save_state()

            await controller.close()
            return f"✅ Scene {scene_index + 1} đã được tạo lại thành công"
        else:
            scene_state['status'] = 'failed'
            scene_state['error'] = 'Không tạo được video'
            project.save_state()

            await controller.close()
            return f"❌ Scene {scene_index + 1} tạo lại thất bại"

    except Exception as e:
        project.scenes[scene_index]['status'] = 'failed'
        project.scenes[scene_index]['error'] = str(e)
        project.save_state()
        return f"❌ Error: {str(e)}"


def regenerate_scene(scene_index: int, cookies_file: str) -> str:
    """Wrapper for async regenerate"""
    return asyncio.run(regenerate_scene_async(scene_index, cookies_file))


def get_all_scenes_summary() -> str:
    """Get summary of all scenes for preview tab"""
    if not project.scenes:
        return "❌ Chưa có scene nào"

    summary_lines = ["# 📊 Tổng quan các scene\n"]

    for i, scene in enumerate(project.scenes):
        status_emoji = {
            'pending': '⏳',
            'generating': '🎬',
            'completed': '✅',
            'failed': '❌',
            'rejected': '🚫'
        }.get(scene['status'], '❓')

        approved_emoji = '✅' if scene.get('approved', False) else '⬜'

        summary_lines.append(
            f"{status_emoji} **Scene {scene['scene_number']}** "
            f"[{scene['status']}] {approved_emoji}\n"
            f"   Prompt: {scene['prompt'][:80]}...\n"
        )

    return "\n".join(summary_lines)


# ========== Video Assembly ==========

def assemble_final_video() -> tuple:
    """Assemble all scene videos into final video"""
    try:
        if not project.scenes:
            return "❌ Chưa có video nào", None

        # Get all approved and downloaded scenes
        video_files = []
        for scene_state in sorted(project.scenes, key=lambda x: x['scene_number']):
            if scene_state.get('download_path') and scene_state.get('approved', True):
                video_files.append(scene_state['download_path'])

        if not video_files:
            return "❌ Chưa có video nào được tải về", None

        # Assemble
        project_dir = project.get_project_dir()
        output_path = os.path.join(project_dir, f"{project.project_name}_final.mp4")

        assembler = VideoAssembler()
        final_path = assembler.assemble_videos(
            video_files=video_files,
            output_path=output_path,
            script=project.script
        )

        if final_path:
            project.final_video_path = final_path
            project.save_state()

            return f"✅ Video hoàn chỉnh đã được tạo!\n\nFile: {final_path}", final_path
        else:
            return "❌ Lỗi khi nối video", None

    except Exception as e:
        return f"❌ Lỗi: {str(e)}", None


# ========== Create Gradio UI ==========

def create_complete_ui():
    """Create the complete Gradio interface"""

    with gr.Blocks(title="VEO 3.1 Complete Automation", theme=gr.themes.Soft()) as app:
        gr.Markdown("""
        # 🎬 VEO 3.1 Complete Automation System
        Hệ thống tự động hóa hoàn chỉnh cho video AI
        """)

        # Tab 1: Project Setup
        with gr.Tab("1️⃣ Khởi tạo dự án"):
            gr.Markdown("## Bước 1: Tải API Key")

            with gr.Row():
                api_key_file = gr.File(label="📁 Chọn file TXT chứa API key", file_types=[".txt"])

            api_key_status = gr.Textbox(label="Trạng thái", lines=3, interactive=False)
            api_key_display = gr.Textbox(label="API Key", type="password", interactive=False)

            api_key_file.change(
                fn=load_api_key_from_file,
                inputs=[api_key_file],
                outputs=[api_key_status, api_key_display]
            )

            gr.Markdown("## Bước 2: Thiết lập dự án")

            with gr.Row():
                project_name_input = gr.Textbox(
                    label="Tên dự án",
                    placeholder="VD: video_marketing_2024",
                    value="demo_project_test"
                )
                output_folder_input = gr.Textbox(
                    label="Thư mục lưu video",
                    value="./data/projects"
                )

            model_select = gr.Dropdown(
                label="Chọn mô hình AI",
                choices=["gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash"],
                value="gemini-2.0-flash-exp"
            )

            init_project_btn = gr.Button("🚀 Khởi tạo dự án", variant="primary")
            init_status = gr.Textbox(label="Trạng thái", lines=5, interactive=False)

            init_project_btn.click(
                fn=initialize_project,
                inputs=[project_name_input, output_folder_input, model_select],
                outputs=[init_status]
            )

        # Tab 2: Script Generation
        with gr.Tab("2️⃣ Tạo kịch bản"):
            gr.Markdown("## Tạo kịch bản tự động")

            with gr.Row():
                with gr.Column():
                    topic_input = gr.Textbox(
                        label="Chủ đề video",
                        placeholder="VD: Hướng dẫn làm bánh pizza tại nhà",
                        value="Hướng dẫn nấu món phở Việt Nam truyền thống - từ hầm xương đến hoàn thiện tô phở",
                        lines=3
                    )

                    with gr.Row():
                        duration_input = gr.Slider(
                            label="Tổng thời lượng (giây)",
                            minimum=10,
                            maximum=300,
                            value=60,
                            step=5
                        )
                        scene_duration_input = gr.Slider(
                            label="Thời lượng mỗi cảnh (giây)",
                            minimum=3,
                            maximum=20,
                            value=8,
                            step=1
                        )

                    style_input = gr.Dropdown(
                        label="Phong cách hình ảnh",
                        choices=["Realistic", "Cinematic", "Artistic", "Documentary", "Animated"],
                        value="Cinematic"
                    )

                    aspect_ratio_input = gr.Dropdown(
                        label="Tỷ lệ khung hình",
                        choices=["16:9", "9:16", "1:1"],
                        value="16:9"
                    )

                with gr.Column():
                    character_mode = gr.Radio(
                        label="Chế độ nhân vật",
                        choices=["Không có nhân vật", "AI tự nhận diện", "Upload ảnh nhân vật"],
                        value="AI tự nhận diện"
                    )

                    character_images = gr.File(
                        label="Upload ảnh nhân vật (nếu có)",
                        file_count="multiple",
                        file_types=["image"]
                    )

                    character_desc = gr.Textbox(
                        label="Mô tả nhân vật",
                        placeholder="VD: Một đầu bếp nam, 30 tuổi, mặc đồng phục trắng...",
                        lines=3
                    )

            generate_script_btn = gr.Button("📝 Tạo kịch bản", variant="primary", size="lg")

            script_status = gr.Textbox(label="Trạng thái", lines=3, interactive=False)
            script_output = gr.JSON(label="Kịch bản JSON")
            script_file_output = gr.File(label="📥 Tải kịch bản")

            generate_script_btn.click(
                fn=generate_script_with_characters,
                inputs=[
                    topic_input, duration_input, scene_duration_input,
                    style_input, aspect_ratio_input, character_mode,
                    character_images, character_desc
                ],
                outputs=[script_status, script_output, script_file_output]
            )

        # Tab 3: SEO Content
        with gr.Tab("3️⃣ Tạo nội dung SEO"):
            gr.Markdown("## Tạo tiêu đề, mô tả, tags cho YouTube")

            generate_seo_btn = gr.Button("🎯 Tạo nội dung SEO", variant="primary")

            seo_status = gr.Textbox(label="Trạng thái", lines=2, interactive=False)
            seo_output = gr.Textbox(label="Nội dung SEO", lines=20, interactive=False)

            generate_seo_btn.click(
                fn=generate_seo_content,
                inputs=[script_output],
                outputs=[seo_status, seo_output]
            )

        # Tab 4: Generate Videos
        with gr.Tab("4️⃣ Tạo video"):
            gr.Markdown("## Sinh video cho từng phân cảnh")

            with gr.Row():
                cookies_file_input = gr.Textbox(
                    label="File cookies.json",
                    value="./config/cookies.json"
                )
                headless_checkbox = gr.Checkbox(label="Chạy ẩn (headless)", value=True)

            generate_videos_btn = gr.Button("🎬 Tạo tất cả video", variant="primary", size="lg")
            video_gen_status = gr.Textbox(label="Trạng thái", lines=15, interactive=False)

            generate_videos_btn.click(
                fn=generate_all_videos,
                inputs=[cookies_file_input, headless_checkbox],
                outputs=[video_gen_status]
            )

        # Tab 5: Preview & Approve
        with gr.Tab("5️⃣ Xem trước & phê duyệt"):
            gr.Markdown("## Player xem trước video")

            # Summary of all scenes
            refresh_summary_btn = gr.Button("🔄 Làm mới danh sách", size="sm")
            scenes_summary = gr.Markdown("Chưa có scene nào")

            refresh_summary_btn.click(
                fn=get_all_scenes_summary,
                inputs=[],
                outputs=[scenes_summary]
            )

            gr.Markdown("---")
            gr.Markdown("### Xem chi tiết từng scene")

            # Scene selector - fixed maximum to avoid JSON schema issues
            scene_selector = gr.Number(
                label="Chọn scene (nhập số từ 0)",
                value=0,
                precision=0
            )

            with gr.Row():
                with gr.Column(scale=2):
                    preview_video = gr.Video(label="Video preview", interactive=False)

                with gr.Column(scale=1):
                    preview_status = gr.Markdown("Chọn scene để xem")
                    preview_prompt = gr.Textbox(label="Prompt", lines=4, interactive=False)

                    with gr.Row():
                        approve_btn = gr.Button("✅ Phê duyệt", variant="primary")
                        reject_btn = gr.Button("❌ Từ chối", variant="stop")

                    action_status = gr.Textbox(label="Trạng thái", lines=2, interactive=False)

                    gr.Markdown("---")

                    cookies_for_regen = gr.Textbox(
                        label="File cookies (để tạo lại)",
                        value="./config/cookies.json"
                    )
                    regenerate_btn = gr.Button("🔄 Tạo lại scene này", variant="secondary")

            # Connect functions
            scene_selector.change(
                fn=get_scene_preview_data,
                inputs=[scene_selector],
                outputs=[preview_video, preview_status, preview_prompt]
            )

            approve_btn.click(
                fn=approve_scene,
                inputs=[scene_selector],
                outputs=[action_status]
            )

            reject_btn.click(
                fn=reject_scene,
                inputs=[scene_selector],
                outputs=[action_status]
            )

            regenerate_btn.click(
                fn=regenerate_scene,
                inputs=[scene_selector, cookies_for_regen],
                outputs=[action_status]
            )

        # Tab 6: Download Videos
        with gr.Tab("6️⃣ Tải video"):
            gr.Markdown("## Tải hàng loạt video (Auto-upscale 1080p)")

            quality_select = gr.Radio(
                label="Chất lượng ưu tiên",
                choices=["1080p", "720p"],
                value="1080p"
            )

            download_btn = gr.Button("📥 Tải tất cả video", variant="primary", size="lg")
            download_status = gr.Textbox(label="Trạng thái", lines=15, interactive=False)

            download_btn.click(
                fn=download_all_videos,
                inputs=[quality_select],
                outputs=[download_status]
            )

        # Tab 7: Assemble Final Video
        with gr.Tab("7️⃣ Nối video"):
            gr.Markdown("## Nối các video thành file hoàn chỉnh")

            assemble_btn = gr.Button("🎞️ Nối video", variant="primary", size="lg")

            assemble_status = gr.Textbox(label="Trạng thái", lines=3, interactive=False)
            final_video_output = gr.Video(label="Video hoàn chỉnh")

            assemble_btn.click(
                fn=assemble_final_video,
                inputs=[],
                outputs=[assemble_status, final_video_output]
            )

    return app


# ========== Main ==========

if __name__ == "__main__":
    print("="*60)
    print("VEO 3.1 Complete Automation System")
    print("Hệ thống tự động hóa hoàn chỉnh")
    print("="*60)
    print("\nLaunching Gradio interface...")
    print("Access at: http://localhost:7860")
    print("="*60)

    app = create_complete_ui()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
