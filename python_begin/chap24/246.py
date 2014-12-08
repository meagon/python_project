
#encoding = utf-8
from asyncore import dispatcher
from asyncore import async_chat

import socket, asyncore

PORT = 5005
NAME = 'TestChat'

class EndSession(Exception):
    pass

class CommandHandler(object):

    def unknown(self, session, cmd):
        session.push('Unknown command :%s\r\n' %cmd)

    def handle(self, session, line):
        if not line.strip():
            return

        parts = line.split(' ',1)
        
        cmd = parts[0]
        try:
            line = parts[1].strip()
        except IndexError:
            line =''
        meth = getattr(self, 'do_'+cmd, None)
        try:
            meth(session, line)
        except TypeError:
            self.unknown(session, cmd)

    class Room(CommandHandler):
        def __init__(self, server):
            self.server = server
            self.sessions = []
        def add(self,session):
            self.sessions.append(session)

        def remove(self, session):
            self.sessions.remove(session)

        def broatcast(self, line):
            for session in self.sessions:
                session.push(line)

        def do_logout(self, session, line):
            raise EndSession

    class LoginRoom(Room):

        def add(self, session):
            Room.add(self,session)
            self.broadcast('welcome to %s\r\n' %self.server.name)

        def unknown(self, session, cmd):
            session.push('please log in\n use "login <nick>"\r\n')

        def do_login(self,session, line):
            name = line.strip()
            if not name:
                session.push("please enter a name \r\n")
            elif name in self.servers.users:
                session.push('The name "%s" is taken\r\n' %name)
                session.push("please try again.\r\n")
            else:
                session.name = name
                session.enter(self.server.main_room)

    class ChatRoom(Room):
        def add(self, session):
            # 告诉所有人
            self.broadcast(session.name + 'has entered the room\r\n')
            self.server.user[session.name] = session
            Room.add(self., session)
        def remove(self, session):
            Room.remove(self, session)
            self.broadcast(session.name + 'has left the room.\r\n')

        def do_say(self,session, line):
            self.broadcast(session,name + ':' + line + '\r\n')

        def do_look(self, session, line):
            # 处理look 命令，该命令用于查看谁在房间内
            session.push('The following are in this room:\r\n')
            for other in self.sessions:
                session.push(other.name + '\r\n')

        def do_who(self, session, line):
            """处理 who 命令， 该命令用于查看谁登陆了"""
                session.push("The following are logged in" + '\r\n')
                for name in self.server.users:
                    session.push(name + '\r\n')

class LogoutRoom(Room):
    def add(self, session):
        try:
            del self.server.users[session.name]
        except KeyError:
            pass

class ChatSession(async_chat):
    """ 单会话, 负责和单用户通信 """

    def __init__(self, server, sock):
        async_chat.__init__(self, sock)
        self.server = server
        self.set_terminator("\r\n")
        self.data = []
        self.name = None
        self.enter(LoginRoom(Server))

    def enter(self, room)L
    """ 从当前房间移除自身(self), 并且将自身添加到
        下一个房间
    """
        try:
            cur = self.room
        except AttributeError:
            pass
        else:
            cur.remove(self)
        self.room = room
        room.add(self)

    def collect_incomming_data(self, data):
        self.data.append(data)

    def found_terminator(self):
        line = "".join(self.data)
        self.data = []
        try:
            self.room.handler(self, line)
        except EndSession:
            self.handle_close()

    def handle_close(self):
        async_chat.handle_close(self)
        self.enter(LogoutRoom(self.server)

class ChatServer(dispatcher):
    """ 只有一个房间的聊天服务器 """
    def __init__(self, port, name):
        dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(('',port))
        self.listen(5)
        self.name = name
        self.users = {}
        self.main_room = ChatRoom(self)

    def handle_accept(self):
        conn, addr = self.accept()
        ChatSession(self, conn)

if __nam__ == '__main__':
    ser = ChatServer(Port, NAME)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        print ""



