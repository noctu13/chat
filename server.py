from socket import *
import threading
import random
import pickle
import queue
from PyQt6.QtCore import QThread, QTimer
import sys
from PyQt6.QtWidgets import QApplication


class Server(QThread):
    def __init__(self, host, port):
        super(Server, self).__init__(parent = None)
        self.connections = []
        self.messageQueue = queue.Queue()
        self.host = host
        self.port = port

        self.serversock = socket(AF_INET, SOCK_STREAM)
        self.serversock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        self.timer = QTimer()
        self.timer.timeout.connect(self.sendMsgs)
        self.timer.start(500)

        try:
            self.port = int(self.port)
            self.serversock.bind((self.host, self.port))
        except Exception as e:
            print(e)
            self.port = int(self.port) + random.randint(1, 1000)
            self.serversock.bind((self.host, self.port))
        
        self.serversock.listen(5)

        debugMsg = f"Server running on {self.host} at port {self.port}"
        print(debugMsg)

    def run(self):
        while True:
            self.clientsock, self.addr = self.serversock.accept()

            if self.clientsock:
                self.data = self.clientsock.recv(1024)
                self.nickname = pickle.loads(self.data)
                self.connections.append((self.nickname, self.clientsock, self.addr))
                threading.Thread(
                    target=self.receiveMsg, 
                    args=(self.serversock, self.addr),
                    daemon=True
                ).start()
    
    def receiveMsg(self, sock, addr):
        length = len(self.connections)
        nickname = self.connections[-1][0]
        client = self.connections[-1][2]
        debugMsg = f"{nickname} is connected with {client[0]} on port {client[1]}"

        while True:
            try:
                self.data = sock.recv(1024)
            except:
                self.data = None
            if self.data:
                self.data = pickle.loads(self.data)
                self.messageQueue.put(self.data)

    def sendMsgs(self):
        while(not self.messageQueue.empty()):
            self.message = self.messageQueue.get()
            self.message = pickle.dump(self.message)
            if self.message:
                for i in self.connections:
                    try:
                        i[1].send(self.message)
                    except:
                        debugMsg = f"[ERROR] Sending message to {str(i[0])}"
                        print(debugMsg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    hostname = "192.168.88.213"
    port = 8080
    server = Server(hostname, port)
    server.start()
    sys.exit(app.exec())