import paramiko
from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient


def create_ssh_client(server, port, user, password):
    """连接到指定的服务器"""
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(server, port=port, username=user, password=password)
    return client


def scp_file_through_jump(jump_host, jump_port, jump_user, jump_password,
                          remote_host, remote_port, remote_user, remote_password,
                          local_file_path, remote_file_path):
    """通过跳板机把文件传输到目标服务器"""
    # 连接到跳板机
    jump_client = create_ssh_client(jump_host, jump_port, jump_user, jump_password)

    # 设置跳板机的转发
    transport = jump_client.get_transport()
    remote_channel = transport.open_channel("direct-tcpip", (remote_host, remote_port), ("localhost", 0))

    # 通过跳板机连接目标服务器
    remote_client = paramiko.SSHClient()
    remote_client.set_missing_host_key_policy(AutoAddPolicy())
    remote_client.connect(remote_host, port=remote_port, username=remote_user, password=remote_password,
                          sock=remote_channel)

    # 使用SCP传输文件到目标服务器
    with SCPClient(remote_client.get_transport()) as scp:
        scp.put(local_file_path, remote_file_path)

    # 关闭连接
    remote_client.close()
    jump_client.close()


# 配置信息
jump_host = '222.204.6.193'  # 跳板机IP地址
jump_port = 8087  # 跳板机端口
jump_user = 'ZZQ'  # 你的跳板机用户名
jump_password = 'ZZQ@good114'  # 你的跳板机密码

remote_host = '192.168.1.72'  # 目标服务器IP
remote_port = 22  # 目标服务器端口
remote_user = 'ZZQ'  # 你的目标服务器用户名
remote_password = 'ZZQ@good114'  # 你的目标服务器密码

local_file_path = r'F:\24_Huawei_developer-main\疲劳驾驶摄像头实时检测\model\fack.pt'  # 你想上传的本地文件路径
remote_file_path = '/app/huaweiyun/testwav/'  # 文件在目标服务器上的存储路径

# 调用函数上传文件
scp_file_through_jump(jump_host, jump_port, jump_user, jump_password,
                      remote_host, remote_port, remote_user, remote_password,
                      local_file_path, remote_file_path)
