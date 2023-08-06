# coding=utf-8
import os
import time
import paramiko
from datetime import date


class ShellKit(object):

    # 初始化构造函数（主机，用户名，密码，端口，默认22）
    def __init__(self, hostname='192.168.70.30', username='hasee', password='123456', port=22, timeout=300):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.currentPid = os.getpid()
        self.notrespstamp = None
        self.tipCount = 0
        self.tipLimit = 3

    # 建立ssh连接通道，并绑定在 __transport 上
    def connect(self):
        try:
            # 实例化一个SSH客户端(执行命令用)
            self.ssh = paramiko.SSHClient()
            self.ssh.load_system_host_keys()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # 链接服务器
            self.ssh.connect(
                hostname = self.hostname, #服务器的ip
                port = self.port, #服务器的端口
                username = self.username, #服务器的用户名
                password = self.password, #用户名对应的密码
                compress=True
            )
            # 设置SSH连接的远程主机地址和端口
            self.__transport = paramiko.Transport((self.hostname, self.port))
            # 通过用户名和密码连接SSH服务端
            self.__transport.connect(username=self.username, password=self.password)
            self.chan = self.__transport.open_session()
            self.chan.settimeout(self.timeout)
            self.chan.get_pty()
            self.chan.invoke_shell()
            # 实例化一个 sftp 对象,指定连接的通道(上传下载用)
            self.sftp = paramiko.SFTPClient.from_transport(self.__transport)
        except Exception as e:
            # 连接出错
            print(e)     

    # 进度转化
    def translateByte(self, B):
        B = float(B)
        KB = float(1024)
        MB = float(KB ** 2)
        GB = float(MB ** 2)
        TB = float(GB ** 2)
        if B < KB:
            return '{} {}'.format(B, 'bytes' if B > 1 else "byte")
        elif KB < B < MB:
            return '{:.2f} KB'.format(B / KB)
        elif MB < B < GB:
            return '{:.2f} MB'.format(B / MB)
        elif GB < B < TB:
            return '{:.2f} GB'.format(B / GB)
        else:
            return '{:.2f} TB'.format(B / TB)         

    # 进度监听
    def progress(self, curr=100, total=100):
        bar_length = 100
        percents = '\033[32;1m%s\033[0m' % round(float(curr) * 100 / float(total), 2)
        filled = int(bar_length * curr / float(total))
        bar = '\033[32;1m%s\033[0m' % '=' * filled + '-' * (bar_length - filled)
        print('传输进度: [{}] {}%  已完成: {}, 合计: {}\r\n'.format(bar, percents, self.translateByte(curr), self.translateByte(total)), end='')    

    # 下载指定的文件
    # download_path 待下载的远程文件
    # restore_path  待保存的本地文件
    def download(self,download_path,restore_path):
        try:
            self.sftp.get(download_path,restore_path,callback=self.progress)
        except Exception as e:
            print(f"{download_path}文件下载失败,异常信息:{e}")
        return True    
    
    # 上传指定的文件
    # uploadPath 远程文件的目录(path)
    # restorePath 本地文件的目录
    def upload(self,uploadPath,restorePath):
        try:
            self.sftp.put(uploadPath,restorePath,callback=self.progress)
        except Exception as e:
            print(f"{uploadPath}文件上传失败,异常信息:{e}")
        return True
    
    # 执行单条命令
    def signalCmd(self,command,showLog=False):
        channel = self.ssh.get_transport().open_session()
        channel.get_pty()
        channel.exec_command(command)
        output = channel.makefile().read().decode('utf-8')
        error = channel.makefile_stderr().read().decode('utf-8')
        code = channel.recv_exit_status()
        # channel is closed, but not the client
        channel.close()          
        if showLog:
            print(f"指令执行情况:执行返回结果:{code}\n执行结果:{output}\n异常信息:{error}\n")             
        return output, error, code
    
    # 执行多条命令(以数组的形式传递)
    def multiCmd(self,array,showLog=False):
        commands = ";".join(array)
        return self.signalCmd(commands,showLog=showLog)
    
    # 发送要执行的命令
    def send(self, cmd):
        if(cmd!=None):
            commands = cmd.join('\r')
            result = ''
            # 发送要执行的命令
            self.chan.send(commands)
            # 回显很长的命令可能执行较久，通过循环分批次取回回显,执行成功返回true,失败返回false
            while True:
                time.sleep(0.5)
                ret = self.chan.recv(65535)
                ret = ret.decode('utf-8')
                result += ret
                return result
    def smartExit(self,autoExit=False,autoExitTime=30):
        nowTime = time.time()
        # print(f"当前时间{nowTime - self.notrespstamp}")
        timeCheck = (nowTime - self.notrespstamp)>autoExitTime*(self.tipCount+1)
        limitCheck = self.tipCount<self.tipLimit
        # print(f'{timeCheck} {limitCheck} {self.tipCount}')
        if timeCheck and limitCheck:
            self.notrespstamp = time.time()
            self.tipCount +=1
            print(f"按Ctrl+C可以退出,重要的事情说{self.tipCount}遍")
        if autoExit and not limitCheck:
            raise KeyboardInterrupt('主动退出')
        
    # 回显shell信息
    def display(self,autoExit=False,autoExitTime=30):
        result = ''
        time.sleep(0.5)
        bool = self.chan.recv_ready()
        if bool:
            # print(f"loading.....{bool}")
            ret = self.chan.recv(65535)
            ret = ret.decode('utf-8')
            result += ret
            data=result.replace(result.split("\n")[-1],"")
            print(result.split("\n")[-1] + data.strip("\n"))
        else:
            self.smartExit(autoExit=autoExit,autoExitTime=autoExitTime)
            

    # 根据生成器获取下一条指令
    def obtainCmd(self,generate):
        try:
            msg = next(generate)
        except StopIteration as e:
            msg = None
        return msg
    
    # 发送Command命令
    def sendLinuxCmd(self,command):
        if command!=None:
            command += '\r'
            # 发送要执行的命令
            self.chan.send(command)

    #shell 模拟
    # args 数组的形式
    def simulate(self,array,autoExit=False,autoExitTime=30):
        generate = (item for item in array)
        self.notrespstamp = time.time()
        while True:
            try:
                self.display(autoExit=autoExit,autoExitTime= autoExitTime)
                cmd = self.obtainCmd(generate)    
                self.sendLinuxCmd(cmd)
            except KeyboardInterrupt:
                break
            except AttributeError as attr:    
                print(f"请求失败:{attr}")
                break        


if __name__ == '__main__':
    shellKit = ShellKit('192.168.0.1','user','123456')
    shellKit.connect()
    # 下载
    # shellKit.download('/media/F/AT/sprd.mocor13.androidT/build.log','D:/test/build.log')
    # 上传
    # shellKit.upload('D:/test/build.log','/media/F/AT/sprd.mocor13.androidT/build.log')
    # 执行多条命令(同步的形式,远程执行完成后会继续执行主线程操作)
    cmds = ["ls","ls -al"]
    # output,error,code = shellKit.multiCmd(cmds,showLog=True)

    shellKit.simulate(cmds,autoExit=True,autoExitTime=1)
    print("继续执行...")

