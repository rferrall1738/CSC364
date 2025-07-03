from socket import *

serverPort = 8900
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(8)

print('Waiting for a connection...')

while True:
    connectionSocket ,address = serverSocket.accept()
    print("Socket:", connectionSocket,"address:", address)
    message = connectionSocket.recv(1024).decode()
    connectionSocket.send(message.upper().encode())
    connectionSocket.close()