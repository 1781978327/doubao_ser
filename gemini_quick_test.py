"""
一次性本地测试：使用内置 API Key，调用 Gemini 2.5 分析目录中的图片。

使用：
  python gemini_quick_test.py
  或指定图片：
  python gemini_quick_test.py --image "F:\\mycode\\服务器端\\received_screenshots\\screenshot_XXXX.png"
"""

import os
import sys
import argparse
from typing import Optional, List

try:
    import google.generativeai as genai
except Exception:
    print("请先安装依赖：pip install google-generativeai")
    sys.exit(1)


# 你提供的测试用 API Key（仅供本地临时测试，不建议长期保存在代码中）
TEST_API_KEY = "AIzaSyBp1EGZxIBODHYql53nE1gchZ3TQpyqg08"

# 默认图片目录
DEFAULT_DIR = os.path.join("F:\\mycode\\服务器端", "received_screenshots")


def list_images(dir_path: str) -> List[str]:
    if not os.path.exists(dir_path):
        return []
    exts = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}
    files = []
    for name in os.listdir(dir_path):
        lower = name.lower()
        if os.path.splitext(lower)[1] in exts:
            files.append(os.path.join(dir_path, name))
    # 按修改时间倒序，最新的在前
    files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return files


def infer_mime(image_path: str) -> str:
    lower = image_path.lower()
    if lower.endswith(".png"):
        return "image/png"
    if lower.endswith(".jpg") or lower.endswith(".jpeg"):
        return "image/jpeg"
    if lower.endswith(".webp"):
        return "image/webp"
    if lower.endswith(".bmp"):
        return "image/bmp"
    return "application/octet-stream"


def run(image_path: str, prompt: Optional[str]) -> None:
    if not os.path.exists(image_path):
        print(f"找不到图片：{image_path}")
        sys.exit(2)

    genai.configure(api_key=TEST_API_KEY)
    model = genai.GenerativeModel("models/gemini-2.5-flash")

    with open(image_path, "rb") as f:
        img_bytes = f.read()

    mime = infer_mime(image_path)
    parts = [{"mime_type": mime, "data": img_bytes}]
    if prompt:
        parts.append(prompt)
    else:
        parts.append("请分析这张图片的主要内容和关键信息，并给出简要要点。")

    resp = model.generate_content(parts)
    print("===== 模型回答 =====")
    print(resp.text or "<无内容>")


def main():
    parser = argparse.ArgumentParser(description="Gemini 2.5 图片分析（一次性测试脚本）")
    parser.add_argument("--image", default=None, help="图片路径（可选，不填则取目录中最新一张）")
    parser.add_argument("--dir", default=DEFAULT_DIR, help="图片目录（默认为 received_screenshots）")
    parser.add_argument("--prompt", default=None, help="额外提示词（可选）")
    args = parser.parse_args()

    image_path = args.image
    if not image_path:
        imgs = list_images(args.dir)
        if not imgs:
            print(f"目录中没有可用图片：{args.dir}")
            sys.exit(3)
        image_path = imgs[0]
        print(f"未指定图片，已选取最新文件：{image_path}")

    try:
        run(image_path, args.prompt)
    except Exception as e:
        print(f"调用失败：{e}")
        sys.exit(4)


if __name__ == "__main__":
    main()


