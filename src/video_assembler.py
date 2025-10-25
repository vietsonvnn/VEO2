"""
Video Assembler
Nối các video scenes thành video hoàn chỉnh
"""

import os
import logging
from typing import List, Optional, Dict
from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip

logger = logging.getLogger(__name__)


class VideoAssembler:
    """Assembles multiple scene videos into a single final video"""

    def __init__(self):
        self.logger = logger

    def assemble_videos(
        self,
        video_files: List[str],
        output_path: str,
        script: Optional[Dict] = None,
        add_transitions: bool = False,
        transition_duration: float = 0.5
    ) -> Optional[str]:
        """
        Assemble multiple video files into one

        Args:
            video_files: List of video file paths (in order)
            output_path: Output file path
            script: Optional script metadata
            add_transitions: Whether to add crossfade transitions
            transition_duration: Duration of transitions in seconds

        Returns:
            Path to the final video, or None if failed
        """
        try:
            logger.info(f"🎞️  Assembling {len(video_files)} videos...")

            # Load all video clips
            clips = []
            for i, video_file in enumerate(video_files):
                if not os.path.exists(video_file):
                    logger.warning(f"⚠️  Video file not found: {video_file}")
                    continue

                try:
                    clip = VideoFileClip(video_file)
                    clips.append(clip)
                    logger.info(f"   ✅ Loaded scene {i+1}: {os.path.basename(video_file)} ({clip.duration}s)")
                except Exception as e:
                    logger.error(f"   ❌ Failed to load {video_file}: {str(e)}")
                    continue

            if not clips:
                logger.error("❌ No valid video clips to assemble")
                return None

            # Concatenate clips
            if add_transitions:
                # Add crossfade transitions
                logger.info("   Adding crossfade transitions...")
                final_clip = concatenate_videoclips(
                    clips,
                    method="compose",
                    transition=lambda clip1, clip2: clip2.crossfadein(transition_duration)
                )
            else:
                # Simple concatenation
                final_clip = concatenate_videoclips(clips, method="compose")

            logger.info(f"   Total duration: {final_clip.duration}s")

            # Write output
            logger.info(f"   Writing to: {output_path}")
            final_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=30,
                preset='medium',
                logger=None  # Suppress moviepy logging
            )

            # Close clips to free memory
            final_clip.close()
            for clip in clips:
                clip.close()

            logger.info(f"✅ Video assembly complete: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"❌ Assembly failed: {str(e)}")
            return None

    def resize_video(
        self,
        input_path: str,
        output_path: str,
        width: int,
        height: int
    ) -> Optional[str]:
        """Resize a video to specific dimensions"""
        try:
            clip = VideoFileClip(input_path)
            resized = clip.resize((width, height))
            resized.write_videofile(output_path, codec='libx264', audio_codec='aac')
            clip.close()
            resized.close()
            return output_path
        except Exception as e:
            logger.error(f"❌ Resize failed: {str(e)}")
            return None
