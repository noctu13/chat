import sys
import socket
import pickle
import threading
from PyQt6.QtCore import QObject, QSize, QThread
from PyQt6.QtWidgets import QWidget, QApplication, QTextEdit, QVBoxLayout, QLineEdit, QMainWindow

class Client(QThread):

    def __init__(self, host, port, nickname, 
        lineedit, textedit):
        super(Client, self).__init__(parent = None)
        self.host = host
        self.port = port
        self.nickname = nickname
        self.lineedit = lineedit
        self.textedit = textedit
        self.lineedit.returnPressed.connect(self.send)
        self.msg = ""

        self.running = True
        self.clientsoc = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.clientsoc.connect((self.host, self.port))
            self.clientsoc.send(pickle.dumps(self.nickname))
        except Exception as e:
            print(f"{e}/nCould not connect to server")
            self.stop()
            sys.exit()
    
    def run(self):
        while self.running:
            self.receive()
    
    def receive(self):
        try:
            self.data = self.clientsoc.recv(1024)
            self.data = pickle.loads(self.data)
            if self.data:
                msg = f"{self.data[0]}: {self.data[1]}"
                if self.data[0] != self.nickname:
                    self.textedit.append(msg)
        except:
            print("Error receiving")
            self.stop()
            sys.exit()
    
    def send(self):
        self.msg = self.lineedit.text()
        self.lineedit.setText("")
        self.data = (self.nickname, self.msg)
        self.data = pickle.dumps(self.data)
        try:
            self.clientsoc.send(self.data)
        except:
            print("Error sending message")
    
    def stop(self):
        self.running = False
        self.clientsoc.close()

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setFixedSize(QSize(400, 600))

        self.setWindowTitle("My App")
        self.textedit = QTextEdit()
        
        self.username = QLineEdit()
        self.username.setText('qwerty')
        self.lineedit = QLineEdit()
        #lineedit.setFixedSize(QSize(400, 50))
        self.lineedit.setMaxLength(20)
        self.lineedit.setPlaceholderText("Enter your text")
        
        layout = QVBoxLayout()
        layout.addWidget(self.textedit)
        layout.addWidget(self.username)
        layout.addWidget(self.lineedit)
        self.setLayout(layout)
        #widget.setReadOnly(True) # раскомментируйте, чтобы сделать доступным только для чтения

        self.lineedit.returnPressed.connect(self.return_pressed)
        self.show()
        self.lineedit.setFocus()
        
        self.hostname = "127.0.0.1" #"192.168.88.213"
        self.port = 8080
        #self.username
        self.client = Client(self.hostname, self.port,
            self.username.text(), self.lineedit, self.textedit)
        threading.Thread(
            target=self.client.run).start()


    def return_pressed(self):
        print("Return pressed!")
        message = self.username.text() + ': ' + self.lineedit.text()
        self.textedit.append(message)
        #self.lineedit.setText("")
        

app = QApplication([])

window = MainWindow()

app.exec()