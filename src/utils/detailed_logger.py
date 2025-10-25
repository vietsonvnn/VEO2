"""
Detailed logging utility with timestamps for VEO automation
"""
import logging
from datetime import datetime
from pathlib import Path
import json

class DetailedLogger:
    """Logger with detailed timestamps and structured output"""

    def __init__(self, log_dir="./data/logs", session_name=None):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Generate session name
        if session_name is None:
            session_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_name = session_name

        # Create log file
        self.log_file = self.log_dir / f"session_{session_name}.log"
        self.json_file = self.log_dir / f"session_{session_name}.json"

        # Session data
        self.session_data = {
            "session_name": session_name,
            "start_time": datetime.now().isoformat(),
            "events": []
        }

        # Setup file logger
        self.logger = logging.getLogger(f"VEO_{session_name}")
        self.logger.setLevel(logging.DEBUG)

        # File handler
        fh = logging.FileHandler(self.log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)

        # Format: [2024-01-25 14:30:45.123] INFO - Message
        formatter = logging.Formatter(
            '[%(asctime)s.%(msecs)03d] %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def log(self, level, message, event_type=None, metadata=None):
        """Log message with timestamp and optional metadata"""
        timestamp = datetime.now().isoformat()

        # Log to file
        if level == "info":
            self.logger.info(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
        elif level == "debug":
            self.logger.debug(message)

        # Add to session data
        event = {
            "timestamp": timestamp,
            "level": level,
            "message": message,
            "type": event_type or "general"
        }
        if metadata:
            event["metadata"] = metadata

        self.session_data["events"].append(event)

    def info(self, message, event_type=None, **metadata):
        """Log info message"""
        self.log("info", message, event_type, metadata if metadata else None)

    def warning(self, message, event_type=None, **metadata):
        """Log warning message"""
        self.log("warning", message, event_type, metadata if metadata else None)

    def error(self, message, event_type=None, **metadata):
        """Log error message"""
        self.log("error", message, event_type, metadata if metadata else None)

    def debug(self, message, event_type=None, **metadata):
        """Log debug message"""
        self.log("debug", message, event_type, metadata if metadata else None)

    def scene_start(self, scene_num, total_scenes, description):
        """Log scene start"""
        self.info(
            f"Scene {scene_num}/{total_scenes} started: {description}",
            event_type="scene_start",
            scene_num=scene_num,
            total_scenes=total_scenes,
            description=description
        )

    def scene_complete(self, scene_num, video_url, duration_seconds):
        """Log scene completion"""
        self.info(
            f"Scene {scene_num} completed in {duration_seconds}s",
            event_type="scene_complete",
            scene_num=scene_num,
            video_url=video_url,
            duration_seconds=duration_seconds
        )

    def scene_failed(self, scene_num, error_message):
        """Log scene failure"""
        self.error(
            f"Scene {scene_num} failed: {error_message}",
            event_type="scene_failed",
            scene_num=scene_num,
            error=error_message
        )

    def flow_progress(self, scene_num, progress_percent):
        """Log Flow progress update"""
        self.debug(
            f"Scene {scene_num} - Flow progress: {progress_percent}%",
            event_type="flow_progress",
            scene_num=scene_num,
            progress=progress_percent
        )

    def queue_status(self, pending_count, max_queue=5):
        """Log queue status"""
        self.info(
            f"Queue status: {pending_count}/{max_queue} pending",
            event_type="queue_status",
            pending=pending_count,
            max_queue=max_queue
        )

    def screenshot_captured(self, scene_num, screenshot_path):
        """Log screenshot capture"""
        self.debug(
            f"Screenshot captured for scene {scene_num}",
            event_type="screenshot",
            scene_num=scene_num,
            path=screenshot_path
        )

    def save_json(self):
        """Save session data to JSON file"""
        self.session_data["end_time"] = datetime.now().isoformat()

        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(self.session_data, f, indent=2, ensure_ascii=False)

    def get_summary(self):
        """Get session summary"""
        events = self.session_data["events"]

        summary = {
            "session": self.session_name,
            "total_events": len(events),
            "scenes_started": len([e for e in events if e["type"] == "scene_start"]),
            "scenes_completed": len([e for e in events if e["type"] == "scene_complete"]),
            "scenes_failed": len([e for e in events if e["type"] == "scene_failed"]),
            "errors": len([e for e in events if e["level"] == "error"]),
            "warnings": len([e for e in events if e["level"] == "warning"]),
        }

        return summary

    def close(self):
        """Close logger and save JSON"""
        self.save_json()

        # Remove handlers
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)
