from socket import *

serverAddress = 'localhost'
serverPort = 8900

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverAddress, serverPort))

message = input("enter your message:")
clientSocket.send(message.encode())

modifiedMessage = clientSocket.recv(1024)
print(modifiedMessage.decode())
clientSocket.close()