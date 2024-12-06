import asyncio
import cv2
import websockets
import threading
import ssl  # 导入 SSL 模块
import  time
class WebSocketVideoStreamer:
    def __init__(self, host, port=8188):
        """
        初始化 WebSocket 视频流类
        """
        self.host = host
        self.port = port
        self.connected_clients = set()  # 存储已连接的客户端

        # 设置 SSL 配置
        self.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.ssl_context.load_cert_chain(certfile="/home/yyh/ioteeth/mydomain.crt", keyfile="/home/yyh/ioteeth/mydomain.key")  # 加载证书和私钥

    def run_server_in_thread(self):
        """
        第一步： 在后台线程中启动 WebSocket 服务器
        """
        server_thread = threading.Thread(target=self.start_server, daemon=True)#线程启动
        server_thread.start()

    def start_server(self):
        """
        第二步：启动 WebSocket 服务器，这里是报错的核心原因
        """
        async def main():
            self.server = await websockets.serve(self.handler, self.host, self.port, ssl=self.ssl_context)
            print(f"WebSocket server started at wss://{self.host}:{self.port}")
            await self.server.wait_closed()
        asyncio.run(main())

    async def handler(self, websocket, path):
        """
        斜撑函数，处理客户端连接和帧发送
        """
        self.connected_clients.add(websocket)
        try:
            while True:
                await asyncio.sleep(0.1)  # 保持连接活跃
        except websockets.ConnectionClosed:
            pass
        finally:
            self.connected_clients.remove(websocket)

    def send_frame(self, frame):
        """
        应用第一步：向所有连接的客户端发送帧
        """
        if not self.connected_clients:
            return  # 如果没有客户端连接，直接返回
        # 将帧编码为 JPEG 格式
        buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 50])[1]
        data = buffer.tobytes()
        # 通过 asyncio 在事件循环中广播帧
        asyncio.run_coroutine_threadsafe(self.broadcast_frame(data), self.loop)
    

    async def broadcast_frame(self, data):
        """
        应用第二步 广播帧到所有连接的客户端
        """
        for client in self.connected_clients:
            try:
                await client.send(data)
            except websockets.ConnectionClosed:
                self.connected_clients.remove(client)


# 使用示例
if __name__ == "__main__":
    # 初始化 WebSocket 视频流类
    streamer = WebSocketVideoStreamer(host="192.168.118.200", port=8188)#应用一个类
    # 在后台线程启动 WebSocket 服务器
    streamer.run_server_in_thread()#在后台启动这个类对应的服务器

    # 模拟主程序的摄像头循环
    cap = cv2.VideoCapture(0)
    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                break
            # 向前端发送当前帧
            streamer.send_frame(frame)
            #cv2.imshow("Local View", frame)  # 显示本地画面
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
