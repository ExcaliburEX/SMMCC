import socket
import time
import threading
import os
import sys
import json
import PySimpleGUI as sg
import requests
import base64



class SMMCC():
    global ip
    ip = '127.0.0.1'
    global port
    port = 6999
    global pos
    pos = 1
    global part_sum
    part_sum = []
    global who_pos
    who_pos = 1
    global compute_time
    compute_time = []
    global finish
    finish = False


    def __init__(self, rng=1000, m=5):
        self.connectList = []
        self.rng = rng
        self.m = m

    def ReceiveFile(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((ip, port))
        while True:
            with open("test.py", "ab") as f:  # 接收文件
                data = client.recv(1024)
                if data == b'quit':
                    client.send("received".encode('utf-8'))
                    break
                if data != b'success':
                    f.write(data)
                client.send("success".encode('utf-8'))
        print(time.strftime("[%Y-%m-%d %H:%M:%S] ", time.localtime()), "计算文件已经接收！存储为test.py")
        f.close()
        client.shutdown(socket.SHUT_RDWR)
        client.close()

    def SendFile(self):
        conn, addr = self.server.accept()
        print(conn,addr)
        with open('Func.py', 'rb') as f:
            for i in f:
                conn.send(i)
                data = conn.recv(1024)
                if data == b'received':
                    break
        print(time.strftime("[%Y-%m-%d %H:%M:%S] ", time.localtime()), "文件'Func.py'已经发送！")
        conn.send('quit'.encode('utf-8'))



    def Node(self, cnt, window):
        begin_time = time.time()
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((ip, port))
        while True:
                msg = client.recv(1024)
                if msg == b'Connect':  # 接收 Connect
                    client.send('Ready'.encode('utf-8'))  # 发送 Ready
                    print(time.strftime("[%Y-%m-%d %H:%M:%S] ", time.localtime()), "节点%d准备完毕！" % (cnt))
                    window['STATUS%d'%(cnt)].update("准备就绪")
                    break
                else:
                    pass
        # while True:
        #     data = client.recv(1024)
        #     if data == b'exist':
        #         if os.path.exists("test.py"):
        #             client.send("Y".encode('utf-8'))
        #             break
        #         else:
        #             client.send("N".encode('utf-8'))
        #             while True:
        #                 with open("test.py", "ab") as f:  # 接收文件
        #                     data = client.recv(1024)
        #                     if data == b'quit':
        #                         client.send("received".encode('utf-8'))
        #                         break
        #                     if data != b'success':
        #                             f.write(data)
        #                     client.send("success".encode('utf-8'))
        #             print("节点%d：计算文件已经接收！存储为test.py" % (cnt))
        #             f.close()
        #             break
        time.sleep(1)
        window['STATUS%d' % (cnt)].update("接收计算参数")
        client.send("Para".encode('utf-8'))
        rng = int(client.recv(1024))  # 接收rng
        m = int(client.recv(1024))  # 接收分片个数
        pos = int(client.recv(1024))  # 接收位置参数
        # print(time.strftime("[%Y-%m-%d %H:%M:%S] ", time.localtime()), "%d：分别为%d,%d,%d" % (cnt, rng, m, pos))
        window['STATUS%d' % (cnt)].update("计算中...")
        from test import test
        sum_prime = test(rng, m, pos, window)
        print(time.strftime("[%Y-%m-%d %H:%M:%S] ", time.localtime()), "节点%d，第%d个运算完，局部结果为：%d" % (cnt, pos, sum_prime))
        window['STATUS%d' % (cnt)].update("计算完毕，发送结果，请求位置")
        client.send("answer".encode('utf-8'))
        client.send(str(sum_prime).encode('utf-8'))  # 发送局部结果
        time.sleep(1)
        client.send("who".encode('utf-8'))  # 发送位置请求
        who = int(client.recv(1024))  # 接收位置回复
        window['STATUS%d' % (cnt)].update("节点位置为:%d"%(who))
        # print("我是：",who)
        global compute_time
        if who == self.m:
            client.send("Integrate".encode('utf-8'))
            data = client.recv(1024)
            sumList = json.loads(data)
            ans = sum(sumList)
            window['STATUS%d' % (cnt)].update("规约节点，最终结果为:%d" % (ans))
            client.send(str(ans).encode('utf-8'))
            end_time = time.time()
            run_time = end_time-begin_time
            compute_time.append(run_time)
            global finish
            finish = True
            os.remove('test.py')
        else:
            window['STATUS%d' % (cnt)].update("第%d节点，非规约节点，任务结束"%(who))
            client.send("end".encode('utf-8'))
            end_time = time.time()
            run_time = end_time-begin_time
            compute_time.append(run_time)
        client.shutdown(socket.SHUT_RDWR)
        client.close()
        

    def connect(self):
        NumOfConnect = 0
        while True:
            conn, addr = self.server.accept()
            # print(conn, addr)
            self.connectList.append([conn, addr])
            NumOfConnect += 1
            if NumOfConnect == self.m:
                print(time.strftime("[%Y-%m-%d %H:%M:%S] ", time.localtime()), "计算节点与控制节点连接完毕！")
                break

    def Call(self):
        for c in self.connectList:
            threading.Thread(target=self.ServerCommand, args=(c[0], c[1])).start()
            time.sleep(0.5)

    def ServerCommand(self, conn, addr):
        while True:
            conn.send('Connect'.encode('utf-8'))
            data = conn.recv(1024)
            if data == b'Ready':
                break
        
        # conn.send("exist".encode('utf-8'))
        
        # data = conn.recv(1024)
        # if data == b'N':
        #     with open('Func.py', 'rb') as f:
        #         for i in f:
        #             conn.send(i)
        #             data = conn.recv(1024)
        #             if data == b'received':
        #                 break
        #     print("文件'Func.py'已经发送！")
        #     conn.send('quit'.encode('utf-8'))
        
        global pos
        while True:
            data = conn.recv(1024)
            if data == b'Para':
                time.sleep(0.5)
                conn.send(str(self.rng).encode('utf-8'))
                time.sleep(0.5)
                conn.send(str(self.m).encode('utf-8'))
                time.sleep(0.5)
                conn.send(str(pos).encode('utf-8'))
                pos += 1
                break
        while True:
            data = conn.recv(1024)
            if data == b'answer':
                ans = int(conn.recv(1024))
                global part_sum
                part_sum.append(ans)
                break
        while True:
            data = conn.recv(1024)
            if data == b'who':
                global who_pos
                conn.send(str(who_pos).encode('utf-8'))
                who_pos += 1
                break
        while True:
            data = conn.recv(1024)
            if data == b'Integrate':
                sum_string = json.dumps(part_sum)
                conn.send(str(sum_string).encode('utf-8'))
                answer = conn.recv(1024)
                print(time.strftime("[%Y-%m-%d %H:%M:%S] ",time.localtime()), "最终结果：%d" % (int(answer)))
                break
            else:
                break
        conn.close()

    def GUI(self):
        with open('img.png', 'rb') as f:
            image = f.read() 
        f.close()
        base64_data = base64.b64encode(image)
        img = base64_data.decode('utf-8')
        img = bytes(img, encoding="utf8")
        sg.theme('LightGrey1')
        col = []
        for i in range(100):
            col.append([sg.Text('节点%d' % (i+1), justification='center', font=("Noto Serif SC", 10), size=(16, 1), key='NODE%s' % (str(i+1)), text_color='saddlebrown', background_color='powderblue'),
                        sg.Text('未知状态%d' % (i+1), justification='center', font=("Noto Serif SC", 10),
                                size=(24, 1), key='STATUS%s' % (str(i+1)), text_color='mediumblue', background_color='azure'),
                       sg.ProgressBar(100, orientation='h', size=(
                           42, 20), style='winnative', bar_color=('palegreen', 'pink'), relief=sg.RELIEF_RIDGE, key='progressbar-%d' % (i+1))]
            )

        layout = [[sg.Text('Simply Multi-Machine Collaborative Computing', size=(
            40, 1), text_color='green', border_width=1, justification='center', font=("Noto Serif SC",22), relief=sg.RELIEF_RIDGE)],
            [sg.Text('计算范围：', font=("Noto Serif SC", 16)), sg.InputText('100000', font=("Noto Serif SC", 16), size=(21, 2), key='-RANGE-'),
             sg.Text('节点数：', font=("Noto Serif SC", 16)), sg.InputText('10', font=("Noto Serif SC", 16), size=(21, 2), key='-NODENUM-')],
            [sg.Text('节点名', size=(12, 1), text_color='white', font=(
                "Noto Serif SC", 16), background_color='green', justification='center',relief=sg.RELIEF_RIDGE, pad=(0, 0)),
                sg.Text('节点状态', size=(15, 1), text_color='white', font=(
                    "Noto Serif SC", 16), background_color='green', justification='center', relief=sg.RELIEF_RIDGE, pad=(0, 0)),
                sg.Text('运算进度', size=(27, 1), text_color='white', font=("Noto Serif SC", 16), background_color='green', justification='center', relief=sg.RELIEF_RIDGE, pad=(0, 0))],
            [sg.Column(col, background_color='papayawhip', size=(700, 400),scrollable=True, justification="left", element_justification="center")],
                  [sg.Output(size=(100, 10))],
            [sg.Frame('加速比计算公式', [[sg.Image(data=img)]],
                      font=("Noto Serif SC", 20), title_color='Tomato')],
            [sg.Button('开始计算', font=(
                "Noto Serif SC", 10), size=(8, 1)), sg.Button('计算加速比', font=(
                    "Noto Serif SC", 10), size=(8, 1)), sg.Text(
                '暂无数据', font=("Noto Serif SC", 16), relief=sg.RELIEF_RIDGE,key='-JIASU-'), sg.Button('总运算时长', font=(
                    "Noto Serif SC", 10), size=(8, 1), button_color=('lawngreen', 'plum')), sg.Text(
                '暂无数据', font=("Noto Serif SC", 16),relief=sg.RELIEF_RIDGE,key='-TIME-')],
        ]  # button_color=(sg.YELLOWS[0], sg.BLUES[0]

        window = sg.Window(
            'SMMCC', layout, default_element_size=(30, 2), grab_anywhere=False, resizable=True, element_justification='center', text_justification='center')
        
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((ip, port))  # 绑定要监听的端口
        self.server.listen(5)  # 开始监听 表示可以使用五个链接排队

        #conn, addr = server.accept()
        #print("连接建立，地址在%s" % (str(addr)))
        while True:
            event, value = window.read()
            if event == '开始计算':
                self.connectList = []
                global pos
                pos = 1
                global part_sum
                part_sum = []
                global who_pos
                who_pos = 1
                global compute_time
                compute_time = []
                global finish
                finish = False
                for i in range(100):
                    window['progressbar-%d' % (i+1)].update_bar(0)
                self.rng = int(value['-RANGE-'])
                self.m = int(value['-NODENUM-'])
                threading.Thread(target=self.main,args=(window,)).start()
                threading.Thread(target=self.SpeedupRatio,args=(window,)).start()
                print(time.strftime("[%Y-%m-%d %H:%M:%S] ",time.localtime()), "侦听器已启动！port：%d" % (port))
        window.close()


    def SpeedupRatio(self, window):
        global finish
        global compute_time
        while True:
            time.sleep(2)
            if finish == True:
                window['-JIASU-'].update(sum(compute_time) / (max(compute_time) * self.m))
                print(time.strftime("[%Y-%m-%d %H:%M:%S] ", time.localtime()),
                      "加速比为：%lf" % (sum(compute_time) / (max(compute_time) * self.m)))
                window['-TIME-'].update(str(max(compute_time))+'s')
                print(time.strftime("[%Y-%m-%d %H:%M:%S] ", time.localtime()), "总运算时长为：%lfs" % (max(compute_time)))
                finish = False
                break

    def main(self, window):
        threading.Thread(target=self.SendFile).start()
        threading.Thread(target=self.ReceiveFile).start()
        time.sleep(1)
        for i in range(1, self.m + 1):
            threading.Thread(target=self.Node,args=(i,window)).start()
        self.connect()
        self.Call()

if __name__ == "__main__":
    s = SMMCC(100000, 10)
    s.GUI()
