<p align="center">
  <a href="" rel="noopener">
 <img width=320 height=150 src="https://i.loli.net/2020/05/25/otQfzumbqYBMdDn.png" alt="Project logo"></a>
</p>

<h3 align="center">Simply Multi-Machine Collaborative Computing</h3>

<div align="center">

[![HitCount](http://hits.dwyl.com/ExcaliburEX/SMMCC.svg)](http://hits.dwyl.com/ExcaliburEX/SMMCC)
[![Build Status](https://www.travis-ci.org/ExcaliburEX/SMMCC.svg?branch=master)](https://www.travis-ci.org/ExcaliburEX/SMMCC)
[![GitHub Issues](https://img.shields.io/github/issues/ExcaliburEX/SMMCC.svg)](https://github.com/ExcaliburEX/SMMCC)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/ExcaliburEX/SMMCC.svg)](https://github.com/ExcaliburEX/SMMCC/pulls)
![forks](https://img.shields.io/github/forks/ExcaliburEX/SMMCC)
![stars](https://img.shields.io/github/stars/ExcaliburEX/SMMCC)
![repo size](https://img.shields.io/github/repo-size/ExcaliburEX/SMMCC)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)
</div>

---

# 0️⃣ 前言
&emsp;&emsp;前面，我已经将实现这个微型系统的组件程序，单独地实现了。可以在下面三篇文章中回顾。

&emsp;&emsp;[高性能分布式计算(HPC)作业1——节点实时通信](https://blog.csdn.net/ExcaliburUlimited/article/details/105873287)

&emsp;&emsp;[高性能分布式计算(HPC)作业2——节点通信，发布计算任务](https://blog.csdn.net/ExcaliburUlimited/article/details/105873303)

&emsp;&emsp;[高性能分布式计算(HPC)作业3——节点通信，发布计算任务，并在计算任务中阻塞](https://blog.csdn.net/ExcaliburUlimited/article/details/105873315)

# 1️⃣ 系统运行界面
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200525014727450.gif#pic_center)

# 2️⃣ 任务设计
## 2️⃣.1️⃣ 任务下发
![在这里插入图片描述](https://img-blog.csdnimg.cn/2020052501510624.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L0V4Y2FsaWJ1clVsaW1pdGVk,size_16,color_FFFFFF,t_70#pic_center)
&emsp;&emsp;服务器下即控制节点向各计算节点请求确认信息，计算节点返回确认信息。随即控制节点向各计算节点下发计算任务以及参数，然后计算节点返回确认信息。

## 2️⃣.2️⃣ 计算进程
![在这里插入图片描述](https://img-blog.csdnimg.cn/20200525015255792.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L0V4Y2FsaWJ1clVsaW1pdGVk,size_16,color_FFFFFF,t_70#pic_center)
- 各计算节点开始计算；
- 在某个计算节点结束后，向控制节点确认自己是第几个算完的，并返回局部结果；
- 如果自己是最后一个算完的，那么就成为规约节点，否则结束运算，当前节点结束任务；
- 若是，开始接受控制节点的所有局部结果，并进行规约计算，最后返回给控制节点最终结果。

# 3️⃣ 具体程序
## 3️⃣.1️⃣ 初始文件收发

&emsp;&emsp;因为程序运行在本地，节点间通过本地的`socket`连接，所以就把文件收发放在一开始，不用每个节点都收一次，一次即可，所有的节点都从本地调取计算函数`test.py`，使用方式就是通过`import`的方式进行。

```python
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
```

## 3️⃣.2️⃣ 计算节点程序(客户端)
&emsp;&emsp;刚刚也说了，一开始就接收到了计算文件，所以注释的部分就不需要了，这部分内容是假定各节点在不同的机器上，需要各自接收计算文件。除此之外，其他逻辑就是前文提到的过程。

```python
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
```


## 3️⃣.3️⃣ 控制节点程序(服务器端)
&emsp;&emsp;首先先等待所有的计算节点的连接，然后针对每个连接开启相应的服务器控制函数线程。

```python
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
```


## 3️⃣.4️⃣ 界面`GUI`程序
&emsp;&emsp;这里面就是`PysimpleGUI`的使用，遇到并已经解决的难点：
- 实时展示程序的命令行输出；
- 展示运算进度条。

```python
def GUI(self):
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
        [sg.Button('开始计算', font=(
            "Noto Serif SC", 10), size=(8, 1)), sg.Button('计算加速比', font=(
                "Noto Serif SC", 10), size=(8, 1)), sg.Text(
            '暂无数据', font=("Noto Serif SC", 16), relief=sg.RELIEF_RIDGE,key='-JIASU-'), sg.Button('总运算时长', font=(
                "Noto Serif SC", 10), size=(8, 1), button_color=('lawngreen', 'plum')), sg.Text(
            '暂无数据', font=("Noto Serif SC", 16),relief=sg.RELIEF_RIDGE,key='-TIME-')],
    ]  # button_color=(sg.YELLOWS[0], sg.BLUES[0]

    window = sg.Window(
        'SMMCC', layout, default_element_size=(30, 2), resizable=True)
    
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
```
## 3️⃣.5️⃣ 计算任务
&emsp;&emsp;就是简单的计算某个区间内的素数个数，分成`n`份分发给各个节点进行计算，其中嵌入了进度条展示。

```python
from alive_progress import alive_bar
from math import sqrt

def Prime(n):
    if n == 1:
        return False
    for num in range(2, int(sqrt(n))+1):
        if n % num == 0:
            return False
    else:
        return True
    

def test(rng, m, pos, window):
    sum_prime = 0
    # with alive_bar(rng // m) as bar:
    for i in range(rng // m * (pos-1), rng // m * (pos)):
        # bar()
        window['progressbar-%d'%(pos)].update_bar(100/(rng//m) * (i-(rng // m * (pos-1))) + 1)
        if Prime(i):
            sum_prime += 1
    return sum_prime
```
# 4️⃣ 完整程序(方便大家复制运行)
## 4️⃣.1️⃣ `SMMCC.py`

```python
import socket
import time
import threading
import os
import sys
import json
import PySimpleGUI as sg

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
    house_prc

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
            [sg.Button('开始计算', font=(
                "Noto Serif SC", 10), size=(8, 1)), sg.Button('计算加速比', font=(
                    "Noto Serif SC", 10), size=(8, 1)), sg.Text(
                '暂无数据', font=("Noto Serif SC", 16), relief=sg.RELIEF_RIDGE,key='-JIASU-'), sg.Button('总运算时长', font=(
                    "Noto Serif SC", 10), size=(8, 1), button_color=('lawngreen', 'plum')), sg.Text(
                '暂无数据', font=("Noto Serif SC", 16),relief=sg.RELIEF_RIDGE,key='-TIME-')],
        ]  # button_color=(sg.YELLOWS[0], sg.BLUES[0]

        window = sg.Window(
            'SMMCC', layout, default_element_size=(30, 2), resizable=True)
        
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

```

## 4️⃣.2️⃣ `Func.py`

```python
from alive_progress import alive_bar
from math import sqrt

def Prime(n):
    if n == 1:
        return False
    for num in range(2, int(sqrt(n))+1):
        if n % num == 0:
            return False
    else:
        return True
    

def test(rng, m, pos, window):
    sum_prime = 0
    # with alive_bar(rng // m) as bar:
    for i in range(rng // m * (pos-1), rng // m * (pos)):
        # bar()
        window['progressbar-%d'%(pos)].update_bar(100/(rng//m) * (i-(rng // m * (pos-1))) + 1)
        if Prime(i):
            sum_prime += 1
    return sum_prime
```


