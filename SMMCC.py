import socket
import time
import threading
import os
import sys
import json
import PySimpleGUI as sg
import requests




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
        img = b'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'
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
