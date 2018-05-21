# -*- coding: utf-8 -*-


import socket, os, sys, thread, time, Queue, threading, numpy as np
from common import *

if __name__ != '__main__':
    sys.exit(1)

# url文件
urlFile = "NTP_IP.csv"


# urlFile = "t.txt"

# ************************************************#

def isOpen(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        msg(ip + ' is open on ' + str(port), 1)
        fos = open('./res/success.txt', 'a')
        fos.write(ip + '\r')
        fos.close()
        return True
    except:
        msg(ip + ' is down on ' + str(port), 2)
        fos = open('./res/fail.txt', 'a')
        fos.write(ip + '\r')
        fos.close()
        return False


# 打开文件
fo = open(urlFile, "r")
msg('file name is %s' % (urlFile), 1)
ipList = []

for line in fo.readlines():  # 依次读取每行
    line = line.strip()  # 去掉每行头尾空白
    line = line.replace('\n', '')  # 去掉每行换行符
    # print line
    # 空行的话跳过
    if (not line):
        continue
    ipList.append(line)

exitFlag = 0


class myThread(threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q

    def run(self):
        print "Starting " + self.name
        process_data(self.name, self.q)
        print "Exiting " + self.name


def process_data(threadName, q):
    while not exitFlag:
        queueLock.acquire()
        if not workQueue.empty():
            data = q.get()
            queueLock.release()
            print "%s processing %s" % (threadName, data)
            isOpen(data, 123)
        else:
            queueLock.release()
        time.sleep(1)


threadList = np.arange(0, 500)
nameList = ipList
queueLock = threading.Lock()
workQueue = Queue.Queue(0)
threads = []
threadID = 1

# 创建新线程
for tName in threadList:
    thread = myThread(threadID, tName, workQueue)
    thread.start()
    threads.append(thread)
    threadID += 1

# 填充队列
queueLock.acquire()
for word in nameList:
    workQueue.put(word)
queueLock.release()

# 等待队列清空
while not workQueue.empty():
    pass

# 通知线程是时候退出
exitFlag = 1

# 等待所有线程完成
for t in threads:
    t.join()
print "Exiting Main Thread"
