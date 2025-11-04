# ai_handler.py：AI逻辑（API调用、Markdown处理）
import re
from PyQt5.QtCore import QThread, pyqtSignal
from openai import OpenAI
import base64
import config  # 导入全局变量（使用全局client）


# -------------------------- Markdown格式处理工具 --------------------------
def format_markdown_with_code(md_text):
    """处理Markdown中的代码块，添加样式"""
    code_pattern = r"```(\w*)\n(.*?)```"
    def replace_code(match):
        lang = match.group(1).strip()
        code_content = match.group(2).strip()
        lang_label = f"<div class='code-language'>{lang.capitalize()} 代码</div>" if lang else "<div class='code-language'>代码块</div>"
        code_escaped = code_content.replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>").replace(" ", "&nbsp;")
        return f"{lang_label}<div class='code-block'>{code_escaped}</div>"
    return re.sub(code_pattern, replace_code, md_text, flags=re.DOTALL | re.IGNORECASE)


# -------------------------- AI调用线程 --------------------------
class ApiThread(QThread):
    """独立线程调用AI接口，避免阻塞UI"""
    result_signal = pyqtSignal(str, str)  # 信号：(推理过程, 回答内容)

    def __init__(self, base64_image, question, image_bytes=None, image_mime="image/png"):
        super().__init__()
        self.base64_image = base64_image  # 图片Base64编码
        self.question = question          # 用户问题
        self.image_bytes = image_bytes    # 原始图片字节（Gemini使用）
        self.image_mime = image_mime

    def run(self):
        try:
            if config.PROVIDER == "gemini":
                try:
                    import google.generativeai as genai
                except Exception as e:
                    self.result_signal.emit(f"Gemini依赖未安装：{str(e)}", "")
                    return
                if not config.gemini_api_key:
                    self.result_signal.emit("未配置Gemini API Key，请在初始化配置中填写。", "")
                    return
                if not self.image_bytes:
                    # 如果未传入原始字节，尝试从base64恢复
                    try:
                        self.image_bytes = base64.b64decode(self.base64_image)
                    except Exception:
                        self.result_signal.emit("无法获取图片字节用于Gemini分析。", "")
                        return
                genai.configure(api_key=config.gemini_api_key)
                model = genai.GenerativeModel(config.MODEL or "models/gemini-2.5-flash")
                parts = [
                    {"mime_type": self.image_mime, "data": self.image_bytes},
                    self.question or "请分析这张图片的内容"
                ]
                resp = model.generate_content(parts)
                reasoning = "Gemini不输出推理过程"
                answer = getattr(resp, "text", None) or ""
                self.result_signal.emit(reasoning, answer)
            else:
                # 使用全局配置的OpenAI客户端（Doubao Ark）
                completion = config.client.chat.completions.create(
                    model=config.MODEL,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{self.base64_image}"}},
                                {"type": "text", "text": self.question}
                            ],
                        }
                    ]
                )
                reasoning = "模型不支持推理过程输出"  # 若模型支持可修改
                answer = completion.choices[0].message.content
                self.result_signal.emit(reasoning, answer)
        except Exception as e:
            # 错误信息通过信号传递给UI
            self.result_signal.emit(f"调用失败：{str(e)}", "")


# -------------------------- 初始化AI客户端 --------------------------
def init_ai_client(api_key):
    """初始化OpenAI客户端，赋值给全局变量"""
    config.client = OpenAI(
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        api_key=api_key
    )
    return config.client