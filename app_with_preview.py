"""
VEO 3.1 Automation - Gradio Web UI with Video Preview & Regenerate
Enhanced UI để xem và regenerate videos
"""

import gradio as gr
import os
import sys
import io
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from dotenv import load_dotenv
from src.script_generator import ScriptGenerator
from src.browser_automation import FlowController

# Load environment
load_dotenv()

# Global variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
script_generator = None
current_project_state = {
    "script": None,
    "videos": [],  # List of {scene_index, prompt, status, video_path, download_path}
    "project_id": None
}

if GEMINI_API_KEY:
    script_generator = ScriptGenerator(GEMINI_API_KEY)


# ========== Video Generation with Preview ==========

def start_video_generation(script_path):
    """Start video generation from script"""
    global current_project_state

    try:
        # Load script
        with open(script_path, 'r', encoding='utf-8') as f:
            script = json.load(f)

        current_project_state["script"] = script
        current_project_state["videos"] = []

        # Initialize video states
        for i, scene in enumerate(script['scenes']):
            current_project_state["videos"].append({
                "scene_index": i,
                "scene_number": i + 1,
                "prompt": scene['veo_prompt'],
                "description": scene['description'],
                "duration": scene['duration'],
                "status": "pending",  # pending, generating, completed, failed
                "video_path": None,
                "download_path": None,
                "error": None
            })

        status = f"""
✅ Loaded script: {script['title']}
📊 Total scenes: {len(script['scenes'])}
⏱️ Total duration: {script['total_duration']}s

🚀 Ready to generate videos!
Click "Start Generation" to begin.
"""

        # Return initial video grid
        video_components = build_video_grid()

        return status, *video_components

    except Exception as e:
        return f"❌ Error: {str(e)}", *([None] * 20)


def build_video_grid():
    """Build video preview grid components"""
    components = []

    for i in range(10):  # Support up to 10 scenes
        if i < len(current_project_state["videos"]):
            video_data = current_project_state["videos"][i]

            # Video player or placeholder
            if video_data["download_path"] and os.path.exists(video_data["download_path"]):
                video_path = video_data["download_path"]
            else:
                video_path = None

            # Status text
            status_icons = {
                "pending": "⏳",
                "generating": "🎬",
                "completed": "✅",
                "failed": "❌"
            }
            icon = status_icons.get(video_data["status"], "❓")
            status_text = f"{icon} Scene {video_data['scene_number']}: {video_data['status'].upper()}"

            components.extend([
                video_path,  # Video component
                status_text  # Status text
            ])
        else:
            # Empty slot
            components.extend([None, ""])

    return components


async def generate_single_video_async(scene_index, regenerate=False):
    """Generate or regenerate a single video"""
    global current_project_state

    if scene_index >= len(current_project_state["videos"]):
        return f"❌ Invalid scene index: {scene_index}"

    video_data = current_project_state["videos"][scene_index]
    video_data["status"] = "generating"

    try:
        # Initialize Flow Controller
        controller = FlowController(
            cookies_path="./config/cookies.json",
            download_dir="./data/videos",
            headless=True  # Run in background
        )

        await controller.start()
        await controller.goto_flow()

        # Create or reuse project
        if not current_project_state["project_id"]:
            project_id = await controller.create_new_project()
            current_project_state["project_id"] = project_id
        else:
            project_id = current_project_state["project_id"]
            await controller.goto_project(project_id)

        # Generate video
        prompt = video_data["prompt"]
        await controller.create_video_from_prompt(
            prompt=prompt,
            wait_for_generation=False
        )

        # Wait for completion
        completed = await controller.wait_for_video_completion(timeout=420)

        if completed:
            # Download video
            filename = f"scene_{scene_index + 1:03d}.mp4"
            download_path = await controller.download_video_from_ui(
                filename=filename,
                quality="1080p"
            )

            if download_path:
                video_data["status"] = "completed"
                video_data["download_path"] = download_path
                result = f"✅ Scene {scene_index + 1} completed!"
            else:
                video_data["status"] = "failed"
                video_data["error"] = "Download failed"
                result = f"❌ Scene {scene_index + 1} download failed"
        else:
            video_data["status"] = "failed"
            video_data["error"] = "Generation timeout"
            result = f"❌ Scene {scene_index + 1} generation timeout"

        await controller.close()
        return result

    except Exception as e:
        video_data["status"] = "failed"
        video_data["error"] = str(e)
        return f"❌ Scene {scene_index + 1} error: {str(e)}"


def generate_single_video(scene_index):
    """Wrapper for async video generation"""
    return asyncio.run(generate_single_video_async(scene_index))


def regenerate_video(scene_index):
    """Regenerate a specific video"""
    return generate_single_video(scene_index)


def get_video_info(scene_index):
    """Get info about a specific video"""
    if scene_index >= len(current_project_state["videos"]):
        return "No video data"

    video_data = current_project_state["videos"][scene_index]

    info = f"""
🎬 Scene {video_data['scene_number']}
📝 Description: {video_data['description']}
⏱️ Duration: {video_data['duration']}s
📊 Status: {video_data['status']}

🤖 VEO Prompt:
{video_data['prompt']}
"""

    if video_data["error"]:
        info += f"\n❌ Error: {video_data['error']}"

    return info


# ========== Create Enhanced UI ==========

def create_enhanced_ui():
    """Create enhanced Gradio interface with video preview"""

    with gr.Blocks(
        title="VEO 3.1 Video Automation - Enhanced",
        theme=gr.themes.Soft()
    ) as app:

        gr.Markdown("""
        # 🎬 VEO 3.1 Video Automation - Enhanced
        ### Video Preview & Regenerate Interface
        """)

        with gr.Tabs():

            # ===== Tab: Video Generation & Preview =====
            with gr.Tab("🎥 Video Generation & Preview"):
                gr.Markdown("""
                ## Generate and Preview Videos
                Load a script, generate videos, and preview results
                """)

                with gr.Row():
                    with gr.Column(scale=1):
                        # Script selection
                        gr.Markdown("### 1. Select Script")
                        script_dropdown = gr.Dropdown(
                            label="📄 Saved Scripts",
                            choices=[str(s) for s in Path("./data/scripts").glob("*.json")] if Path("./data/scripts").exists() else [],
                            interactive=True
                        )

                        load_script_btn = gr.Button("📂 Load Script", variant="primary")

                        script_status = gr.Textbox(
                            label="Script Status",
                            lines=10,
                            interactive=False
                        )

                        gr.Markdown("### 2. Start Generation")
                        start_all_btn = gr.Button("🚀 Generate All Videos", variant="primary", size="lg")

                        generation_status = gr.Textbox(
                            label="Generation Status",
                            lines=5,
                            interactive=False
                        )

                    with gr.Column(scale=2):
                        gr.Markdown("### 3. Video Preview Grid")

                        # Video grid (up to 10 scenes)
                        video_components = []
                        for i in range(10):
                            with gr.Row():
                                with gr.Column(scale=2):
                                    video_player = gr.Video(
                                        label=f"Scene {i+1}",
                                        interactive=False
                                    )
                                    video_components.append(video_player)

                                with gr.Column(scale=1):
                                    status_text = gr.Textbox(
                                        label="Status",
                                        lines=2,
                                        interactive=False
                                    )
                                    video_components.append(status_text)

                                    regen_btn = gr.Button(f"🔄 Regenerate Scene {i+1}")
                                    regen_btn.click(
                                        fn=lambda idx=i: regenerate_video(idx),
                                        outputs=generation_status
                                    )

                                    info_btn = gr.Button(f"ℹ️ Info")
                                    info_btn.click(
                                        fn=lambda idx=i: get_video_info(idx),
                                        outputs=generation_status
                                    )

                        # Connect load script button
                        load_script_btn.click(
                            fn=start_video_generation,
                            inputs=script_dropdown,
                            outputs=[script_status, *video_components]
                        )

            # ===== Tab: Simple Generation (Original) =====
            with gr.Tab("📝 Script Generation"):
                gr.Markdown("Original script generation interface...")
                # Keep original UI here

        gr.Markdown("""
        ---
        ### 🎬 VEO 3.1 Automation - Enhanced v2.0
        With Video Preview & Regenerate Feature
        """)

    return app


# ========== Main ==========

if __name__ == "__main__":
    print("="*60)
    print("Starting VEO 3.1 Enhanced Web UI...")
    print("="*60)

    app = create_enhanced_ui()
    app.launch(
        server_name="0.0.0.0",
        server_port=7861,
        share=False,
        show_error=True
    )
