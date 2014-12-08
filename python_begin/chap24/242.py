


from asyncore import dispatcher
import socket, asyncore

class ChatServer(dispatcher):
    def handle_accept(self):
        conn.addr = self.accept()
        print('Connection attempt from ',  addr[0])

server = ChatServer()
server.create_socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0',5005))
server.listen(5)
asyncore.loop()

