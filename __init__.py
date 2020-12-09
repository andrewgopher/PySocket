import socket
import pickle
import threading


class Client:
    def __init__(self, connect_ip, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((connect_ip, port))

    def recv(self):
        header = self.__recv(10).decode("utf-8")
        message = self.__recv(int(header))
        return pickle.loads(message)

    def send(self, data):
        message = pickle.dumps(data)
        header = str(len(message)) + " " * (10 - len(str(len(message))))
        full_message = header.encode("utf-8") + message
        self.socket.send(full_message)

    def close(self):
        self.socket.close()

    def __recv(self, length):
        message = b""
        while len(message) < length:
            message += self.socket.recv(1)
        return message


class Server:
    def __init__(self, port, queue_size, accept_connection):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((socket.gethostname(), port))
        self.socket.listen(queue_size)
        self.clients = []
        self.accept_connection = accept_connection
        self.accept_thread = threading.Thread(target=self.__accept_connections, daemon=True)
        self.check_thread = threading.Thread(target=self.__check_connections, daemon=True)
        self.accept_thread.start()
        self.check_thread.start()


    def recv(self, client):
        try:
            header = self.__recv(10, client)
            if header is None:
                return None
            message = self.__recv(int(header.decode("utf-8")), client)
            if message is None:
                return None
            message_obj = pickle.loads(message)
            return message_obj
        except (ConnectionResetError, BrokenPipeError):
            return None

    def __recv(self, length, client):
        message = b""
        while len(message) < length:
            try:
                client.send("".encode("utf-8"))
            except:
                return None
            message += client.recv(1)
        return message

    def send(self, data, client):
        try:
            message = pickle.dumps(data)
            header = str(len(message)) + " " * (10 - len(str(len(message))))
            full_message = header.encode("utf-8") + message
            client.send(full_message)
        except (ConnectionResetError, BrokenPipeError):
            return False


    def __accept_connections(self):
        while True:
            client_socket, client_address = self.socket.accept()
            self.clients.append([client_socket, client_address])
            self.accept_connection([client_socket, client_address])

    def __check_connections(self):
        while True:
            i = 0
            while i < len(self.clients):
                try:
                    self.clients[i][0].send("".encode("utf-8"))
                except:
                    del self.clients[i]
                else:
                    i += 1

    def close(self):
        self.socket.close()
