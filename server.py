import socket
import threading
import time
#used to get local ip address
HOST=socket.gethostbyname(socket.gethostname())
PORT=50000

#SOCK_STREAM is for TCP
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((HOST,PORT))

#inside listen u can write a number let say 5
#this number specifies how many client can be in waiting area
#if more than 5 client are already in waiting new clients are rejected
server.listen()

clients=[]
nicknames=[]

#broadcast
def broadcast(message,user):
    for client in clients:
        try:
            if client==clients[nicknames.index(user)] :
                message1 = f"You : {message}".encode('utf-8')
                # print("You")
                client.send(message1)
            else:
                if message== 'joined the chat.\n':
                    message1 = f"{nicknames[-1].decode('utf-8')} {message}".encode('utf-8')
                    # print("joined")
                    client.send(message1)
                else:
                    message1 = f"{user.decode('utf-8')}: {message}".encode('utf-8')
                    # print("message")
                    client.send(message1)
        except:
            if message == "left the chatroom!\n":
                message1 = f"{user.decode('utf-8')} {message}".encode('utf-8')
                # print("Left")
                client.send(message1)
            else:
                print("Exception")



def handle(client):
    flag=True
    while True:
        try:
            msg = client.recv(1024).decode('utf-8')
            if msg=="leaving":
                message=f"left the chatroom!\n"
                index = clients.index(client)
                leaving_nickname = nicknames[index]
                clients.pop(index)
                nicknames.pop(index)
                print("Client list updated:",nicknames)
                flag = False
                broadcast(message, leaving_nickname)

            else:
                print("CLient list: ",nicknames)
                message = f"{msg}"
                broadcast(message,nicknames[clients.index(client)])


        except:
            if flag:
                index = clients.index(client)
                clients.pop(index)
                nicknames.pop(index)
                flag = False
            break

def receive():
    while True:
        client,address = server.accept()
        print(f"Connected with {str(address)}!")

        #receive the nickname
        client.send("NICK".encode('utf-8'))
        nickname = client.recv(1024)

        #update the client list and nickname
        clients.append(client)
        nicknames.append(nickname)

        print(f"Nickname of the client is {nickname}")
        broadcast(f"joined the chat.\n",nicknames[clients.index(client)]) #broadcast to all client



        thread = threading.Thread(target=handle,args=(client,))
        thread.start()
        time.sleep(0.1)
        client.send(f"Connected to the server as '{nickname.decode('utf-8')}'\n".encode('utf-8'))  # not working


print("Server running.......")
receive()
