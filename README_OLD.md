# 🎬 VEO 3.1 Video Automation System

> **Tự động hóa hoàn toàn việc tạo video AI trên Google Labs Flow với VEO 3.1**

Hệ thống này giúp bạn:
- ✅ Tạo kịch bản video tự động bằng Gemini API
- ✅ Generate video trên VEO 3.1 bằng browser automation (Playwright)
- ✅ Download và merge thành video hoàn chỉnh
- ✅ Không cần API VEO (dùng cookie để truy cập Flow)

## 🚀 Quick Start

### Option 1: Web UI (Recommended ⭐)

```bash
# 1. Cài đặt cơ bản
pip install gradio google-generativeai python-dotenv pyyaml

# 2. Cấu hình API key
copy .env.example .env
# Thêm GEMINI_API_KEY vào .env

# 3. Start Web UI
python app.py
# Hoặc: run_ui.bat (Windows)

# 4. Mở browser: http://localhost:7860
```

**Web UI cho phép:**
- 📝 Generate scripts với giao diện thân thiện
- 📚 Quản lý script library
- ⚙️ View system status
- ❓ Help & documentation tích hợp

📖 **Xem thêm:** [UI_GUIDE.md](UI_GUIDE.md)

### Option 2: Command Line

```bash
# 1. Cài đặt đầy đủ
pip install -r requirements.txt
playwright install chromium

# 2. Cấu hình
copy .env.example .env
# Thêm GEMINI_API_KEY vào .env

# 3. Extract cookies
python tools/extract_cookies.py cookies_raw.json

# 4. Test
python quick_test.py

# 5. Tạo video
python main.py --topic "Khám phá rừng Amazon" --duration 60
```

📚 **Chi tiết:** [QUICKSTART.md](QUICKSTART.md) | [SETUP_GUIDE.md](SETUP_GUIDE.md) | [INSTALL.md](INSTALL.md)

## 📋 Features

### ✨ Core Features
- 🤖 **AI Script Generation**: Gemini tạo kịch bản với prompts tối ưu cho VEO
- 🎨 **Web UI**: Giao diện Gradio dễ dùng, không cần code
- 🌐 **Browser Automation**: Playwright tự động tương tác với Flow
- 🎥 **Multi-Scene Support**: Chia video thành scenes, generate song song
- 📥 **Auto Download**: Tự động tải video sau khi generate
- 🔗 **Video Merging**: Ghép scenes với transitions mượt mà
- 📊 **Logging & Monitoring**: Track progress, retry failed scenes

### 🎯 Advanced Features
- ⚙️ **Configurable**: YAML config cho mọi settings
- 🔄 **Resume Support**: Generate từ script có sẵn
- 🎨 **Style Customization**: Cinematic, documentary, anime, etc.
- 📐 **Aspect Ratio**: 16:9, 9:16, 1:1
- ⏱️ **Duration Control**: Tùy chỉnh độ dài video và mỗi scene
- 📚 **Script Library**: Quản lý và tái sử dụng scripts

## 🏗️ Kiến Trúc

```
┌─────────────────┐
│  User Input     │
│  (Topic)        │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  Gemini API                 │
│  Script Generator           │
│  • Generate scenes          │
│  • Optimize VEO prompts     │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Playwright Automation      │
│  Flow Controller            │
│  • Load cookies             │
│  • Navigate to Flow         │
│  • Generate videos          │
│  • Monitor & download       │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  MoviePy                    │
│  Video Processor            │
│  • Validate videos          │
│  • Add transitions          │
│  • Merge final video        │
└────────┬────────────────────┘
         │
         ▼
    📹 Final Video
```

## 📂 Project Structure

```
veo-automation/
├── src/
│   ├── script_generator/
│   │   └── gemini_generator.py      # Gemini API integration
│   ├── browser_automation/
│   │   └── flow_controller.py       # Playwright automation
│   ├── video_processor/
│   │   └── merger.py                # Video merging
│   └── utils/
├── config/
│   ├── cookies.json                 # Your Flow cookies (gitignored)
│   └── config.yaml                  # System configuration
├── data/
│   ├── scripts/                     # Generated scripts
│   ├── videos/                      # Downloaded & final videos
│   └── logs/                        # Automation logs
├── tools/
│   └── extract_cookies.py           # Cookie extraction tool
├── main.py                          # Main entry point
├── test_setup.py                    # Setup validation
├── requirements.txt
├── QUICKSTART.md                    # 5-min quick start
└── SETUP_GUIDE.md                   # Detailed setup guide
```

## 🎯 Use Cases

### 1. Content Creation
```bash
python main.py --topic "10 điều thú vị về vũ trụ" --duration 120 --style documentary
```

### 2. Social Media Shorts
```bash
python main.py --topic "Công thức nấu phở Hà Nội" --duration 30 --aspect-ratio 9:16
```

### 3. Educational Videos
```bash
python main.py --topic "Cách hoạt động của AI" --duration 90 --style "educational"
```

### 4. Batch Processing
```bash
# Generate scripts first
for topic in "Topic 1" "Topic 2" "Topic 3"; do
  python main.py --script-only --topic "$topic"
done

# Review scripts, then generate videos
python main.py --from-script data/scripts/script_xxx.json
```

## ⚙️ Configuration

### Basic Settings

[config/config.yaml](config/config.yaml):
```yaml
video:
  default_duration: 60      # Total video duration
  scene_duration: 8         # Duration per scene
  aspect_ratio: "16:9"

gemini:
  model: "gemini-2.0-flash-exp"
  temperature: 0.7

browser:
  headless: false           # Show browser (for debugging)
```

### Environment Variables

[.env](.env.example):
```bash
GEMINI_API_KEY=your_key_here
DOWNLOAD_DIR=./data/videos
```

## 📊 Performance

**Typical Timeline:**
- Script generation: ~10-30 seconds
- Per scene generation: ~5-7 minutes (VEO 3.1)
- Video merging: ~1-2 minutes

**For 60s video (8 scenes):**
- Total time: ~40-60 minutes
- Can run overnight for multiple videos

**API Limits:**
- Gemini Free: 60 req/min, 1500/day (enough for 100+ videos)
- Flow Free: 5 videos/month
- Flow AI Pro: ~50 videos/month

## 🔧 Advanced Usage

### Custom Prompt Engineering

Edit prompts in [src/script_generator/gemini_generator.py](src/script_generator/gemini_generator.py):

```python
prompt = f"""
Your custom prompt template here...
"""
```

### DOM Selector Updates

If Flow UI changes, update selectors in [src/browser_automation/flow_controller.py](src/browser_automation/flow_controller.py):

```python
prompt_selector = 'textarea[placeholder*="prompt"]'
generate_button = 'button:has-text("Generate")'
```

### Add Video Effects

Extend [src/video_processor/merger.py](src/video_processor/merger.py):

```python
def add_custom_effect(clip):
    # Your effect here
    return clip.fx(...)
```

## 🐛 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `GEMINI_API_KEY not found` | Check `.env` file format |
| `Not logged in` | Re-extract cookies from Flow |
| `Timeout waiting for video` | Increase `wait_timeout` in config |
| `Playwright error` | Run `playwright install chromium` |
| `MoviePy error` | `pip install --upgrade moviepy imageio-ffmpeg` |

**Logs:** Check `data/logs/automation.log` for details

## 🔐 Security Notes

- ⚠️ **Cookies contain authentication tokens** - Never share or commit them
- ⚠️ **API keys are sensitive** - Keep `.env` private
- ✅ Both are in `.gitignore` by default

## 📚 Documentation

- [QUICKSTART.md](QUICKSTART.md) - 5-minute quick start guide
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed setup & troubleshooting
- [config/config.yaml](config/config.yaml) - Configuration reference

## 🤝 Workflow

### Phase 1: Script Generation
```python
from src.script_generator import ScriptGenerator

generator = ScriptGenerator(api_key)
script = generator.generate_script(
    topic="Your topic",
    duration=60,
    scene_duration=8
)
```

### Phase 2: Video Generation
```python
from src.browser_automation import FlowController

controller = FlowController(cookies_path="./config/cookies.json")
await controller.start()
await controller.goto_flow()

scenes = await controller.generate_scene_videos(script['scenes'])
```

### Phase 3: Merging
```python
from src.video_processor import VideoMerger

merger = VideoMerger()
final_video = merger.merge_scenes(
    video_paths=[s['download_path'] for s in scenes],
    output_filename="final.mp4"
)
```

## 🎓 Requirements

- Python 3.10+
- 4GB RAM (8GB recommended)
- Stable internet connection
- Google account with Flow access
- Gemini API key (free tier works)

## 📦 Dependencies

```
playwright>=1.48.0
google-generativeai>=0.8.3
moviepy>=1.0.3
python-dotenv>=1.0.1
pyyaml>=6.0.2
```

Full list: [requirements.txt](requirements.txt)

## 🚦 Status & Roadmap

**Current:** v1.0 - Full automation pipeline working

**Planned:**
- [ ] Parallel scene generation (with rate limiting)
- [ ] Better error recovery
- [ ] Video quality upscaling
- [ ] SEO metadata generation
- [ ] YouTube upload integration
- [ ] Web UI dashboard

## 💡 Tips & Best Practices

1. **Start Small**: Test with 30s videos first
2. **Review Scripts**: Use `--script-only` to preview before generating
3. **Monitor Quota**: Track your Flow video limit
4. **Batch Wisely**: Generate scripts in batch, videos one-by-one
5. **Keep Cookies Fresh**: Re-extract every 1-2 weeks

## 📞 Support

**Issues?**
1. Run `python test_setup.py` for diagnostics
2. Check `data/logs/automation.log`
3. Review [SETUP_GUIDE.md](SETUP_GUIDE.md)

## 📄 License

This is an educational project. Use responsibly and respect Google's Terms of Service.

---

**Made with ❤️ for automating AI video creation**

*Last updated: January 2025*
