# image_server.py：独立截图接收服务（无需修改）
import socket
import os
import struct
import argparse
from typing import Tuple


class ImageServer:
    def __init__(self, save_dir: str = "received_screenshots", port: int = 7893):
        self.save_dir = save_dir
        self.port = port
        self.server_socket = None
        self.is_running = False

    def _init_save_dir(self) -> str:
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir, exist_ok=True)
            print(f"[服务端] 已创建保存目录：{os.path.abspath(self.save_dir)}")
        else:
            print(f"[服务端] 已存在保存目录：{os.path.abspath(self.save_dir)}")
        return self.save_dir

    def _receive_data(self, conn: socket.socket, data_len: int) -> bytes:
        received_data = b""
        remaining_len = data_len
        while remaining_len > 0 and self.is_running:
            chunk = conn.recv(min(1024 * 1024, remaining_len))
            if not chunk:
                print("[服务端] 客户端断开连接（数据接收中断）")
                return b""
            received_data += chunk
            remaining_len -= len(chunk)
        return received_data

    def _handle_client(self, conn: socket.socket, client_addr: Tuple[str, int]) -> None:
        print(f"\n[服务端] 新客户端连接：{client_addr[0]}:{client_addr[1]}")
        current_save_dir = self._init_save_dir()

        try:
            # 接收文件名
            filename_len_data = self._receive_data(conn, 4)
            if len(filename_len_data) != 4:
                print(f"[服务端] 接收文件名长度失败（来自{client_addr[0]}）")
                return
            filename_len = struct.unpack("!I", filename_len_data)[0]
            filename_bytes = self._receive_data(conn, filename_len)
            if len(filename_bytes) != filename_len:
                print(f"[服务端] 接收文件名失败（来自{client_addr[0]}）")
                return
            filename = filename_bytes.decode("utf-8")
            full_save_path = os.path.join(current_save_dir, filename)
            print(f"[服务端] 准备接收：{filename}（保存路径：{full_save_path}）")

            # 接收图片数据
            img_len_data = self._receive_data(conn, 4)
            if len(img_len_data) != 4:
                print(f"[服务端] 接收图片长度失败（来自{client_addr[0]}）")
                return
            img_total_len = struct.unpack("!I", img_len_data)[0]
            print(f"[服务端] 图片大小：{img_total_len / 1024:.1f}KB")

            # 分块接收并显示进度
            img_data = b""
            received_len = 0
            while received_len < img_total_len and self.is_running:
                chunk = self._receive_data(conn, min(1024 * 1024, img_total_len - received_len))
                if not chunk:
                    print(f"[服务端] 图片接收中断（来自{client_addr[0]}）")
                    return
                img_data += chunk
                received_len += len(chunk)
                progress = (received_len / img_total_len) * 100
                print(f"[服务端] 接收进度：{progress:.1f}%", end="\r")

            # 保存图片
            if received_len == img_total_len:
                with open(full_save_path, "wb") as f:
                    f.write(img_data)
                print(f"\n[服务端] 接收完成！文件已保存：{full_save_path}")
            else:
                print(f"\n[服务端] 接收不完整（{received_len}/{img_total_len}字节，来自{client_addr[0]}）")

        except Exception as e:
            print(f"\n[服务端] 处理客户端{client_addr[0]}出错：{str(e)}")
        finally:
            conn.close()
            print(f"[服务端] 与{client_addr[0]}的连接已关闭")

    def start(self) -> None:
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(("", self.port))
            self.server_socket.listen(5)

            self.is_running = True
            print("=" * 50)
            print(f"[服务端] 启动成功！")
            print(f"[服务端] 监听端口：{self.port}")
            print(f"[服务端] 保存目录：{os.path.abspath(self.save_dir)}")
            print(f"[服务端] 等待客户端连接（按Ctrl+C停止）")
            print("=" * 50)

            while self.is_running:
                try:
                    client_conn, client_addr = self.server_socket.accept()
                    self._handle_client(client_conn, client_addr)
                except KeyboardInterrupt:
                    self.is_running = False
                except Exception as e:
                    print(f"[服务端] 等待连接时出错：{str(e)}")

        except Exception as e:
            print(f"[服务端] 启动失败：{str(e)}")
        finally:
            if self.server_socket:
                self.server_socket.close()
            print("\n[服务端] 已停止运行")


if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="截图接收服务端")
    parser.add_argument("--port", type=int, default=7893, help="监听端口（默认7893）")
    parser.add_argument("--save-dir", type=str, default="received_screenshots", help="截图保存目录（默认received_screenshots）")
    args = parser.parse_args()
    
    # 启动服务
    server = ImageServer(save_dir=args.save_dir, port=args.port)
    server.start()