"""
Gemini 2.5 聊天与图片分析（命令行工具）

用法示例：
  1) 文本聊天：
     python gemini_chat.py chat --prompt "帮我写一段祝福语"

  2) 图片分析：
     python gemini_chat.py vision --image "./test.png" --prompt "这张图的主要内容是什么？"

API Key 读取顺序：
  --api-key 参数 > 环境变量 GOOGLE_API_KEY > config.api_key（若存在）
默认模型：models/gemini-2.5-flash（可用 --model 覆盖，例如 models/gemini-2.5-pro）
"""

import os
import sys
import argparse
from typing import Optional

try:
    import google.generativeai as genai
except Exception as e:
    print("请先安装依赖：pip install google-generativeai")
    raise


def resolve_api_key(cli_key: Optional[str]) -> str:
    if cli_key:
        return cli_key.strip()
    env_key = os.environ.get("GOOGLE_API_KEY")
    if env_key:
        return env_key.strip()
    try:
        import config  # 优先使用项目现有配置
        if getattr(config, "api_key", None):
            return config.api_key
    except Exception:
        pass
    print("未找到 API Key。请通过 --api-key 或设置环境变量 GOOGLE_API_KEY 提供。")
    sys.exit(1)


def ensure_model(model_name: str) -> str:
    return model_name or "models/gemini-2.5-flash"


def run_chat(model_name: str, api_key: str, prompt: str) -> None:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    chat = model.start_chat(history=[])
    resp = chat.send_message(prompt)
    print(resp.text or "<无内容>")


def load_image_bytes(image_path: str) -> bytes:
    with open(image_path, "rb") as f:
        return f.read()


def run_vision(model_name: str, api_key: str, image_path: str, prompt: Optional[str]) -> None:
    if not os.path.exists(image_path):
        print(f"找不到图片文件：{image_path}")
        sys.exit(1)
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    img_bytes = load_image_bytes(image_path)

    mime = "image/png"
    lower = image_path.lower()
    if lower.endswith(".jpg") or lower.endswith(".jpeg"):
        mime = "image/jpeg"
    elif lower.endswith(".webp"):
        mime = "image/webp"
    elif lower.endswith(".bmp"):
        mime = "image/bmp"

    parts = [
        {"mime_type": mime, "data": img_bytes},
    ]
    if prompt:
        parts.append(prompt)

    resp = model.generate_content(parts)
    print(resp.text or "<无内容>")


def main():
    parser = argparse.ArgumentParser(description="Gemini 2.5 聊天与图片分析")
    parser.add_argument("--api-key", dest="api_key", default=None, help="API Key（可用环境变量 GOOGLE_API_KEY 代替）")
    parser.add_argument("--model", dest="model", default="models/gemini-2.5-flash", help="模型ID，默认 models/gemini-2.5-flash")

    sub = parser.add_subparsers(dest="command", required=True)

    p_chat = sub.add_parser("chat", help="文本聊天")
    p_chat.add_argument("--prompt", required=True, help="问题/提示词")

    p_vision = sub.add_parser("vision", help="图片分析")
    p_vision.add_argument("--image", required=True, help="图片路径")
    p_vision.add_argument("--prompt", default=None, help="可选的额外文本提示")

    args = parser.parse_args()

    api_key = resolve_api_key(args.api_key)
    model = ensure_model(args.model)

    try:
        if args.command == "chat":
            run_chat(model, api_key, args.prompt)
        elif args.command == "vision":
            run_vision(model, api_key, args.image, args.prompt)
        else:
            parser.print_help()
    except Exception as e:
        print(f"调用失败：{e}")
        sys.exit(2)


if __name__ == "__main__":
    main()


