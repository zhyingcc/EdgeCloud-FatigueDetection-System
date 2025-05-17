import socket
import pyaudio
from sshtunnel import SSHTunnelForwarder

def stream_audio_to_server_through_ssh():
    # SSH 连接信息
    jump_host = '222.204.6.193'
    jump_user = 'ZJ'
    jump_password = 'ZJ@good114'  # 使用密码认证
    jump_port = 8087

    # 远程服务器的 SSH 连接信息
    remote_server_ip = '192.168.1.72'
    remote_port = 22  # 远程服务器的端口


    # 音频流信息
    chunk = 1024  # 每次读取的数据块大小
    format = pyaudio.paInt16  # 16-bit int
    channels = 1
    rate = 16000  # 16kHz

    # 使用 sshtunnel 创建 SSH 隧道
    with SSHTunnelForwarder(
        (jump_host, jump_port),
        ssh_username=jump_user,
        ssh_password=jump_password,
        remote_bind_address=(remote_server_ip, remote_port),
        local_bind_address=('0.0.0.0', 4000)  # 本地绑定端口
    ) as tunnel:
        print("SSH 隧道已建立，开始连接服务器...")

        # 连接到本地转发的端口
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1', tunnel.local_bind_port))

        # 打开麦克风流
        p = pyaudio.PyAudio()
        stream = p.open(format=format,
                        channels=channels,
                        rate=rate,
                        input=True,
                        frames_per_buffer=chunk)

        print("开始传输音频数据到远程服务器...")

        try:
            while True:
                data = stream.read(chunk)
                sock.sendall(data)  # 通过隧道传输音频数据
        except KeyboardInterrupt:
            print("结束传输")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
            sock.close()

if __name__ == "__main__":
    stream_audio_to_server_through_ssh()
