# Сервер управления светодиодом
# 
# Содержит класс светодиода.
# Инициализируется объект, доступно одновременное управление тремя клиентами.
# Сервер принимает запрос в виде строки "команда + аргумент".


import socket
import threading
import json
from inspect import signature
from collections import OrderedDict


class LED:
    __available_state = ["on", "off"]
    __available_colors = ["red", "green", "blue"]
    __available_rate = [str(i) for i in range(0, 6)]

    def __init__(self, start_state="off", start_color="red", start_rate=0):
        self.__state = start_state
        self.__color = start_color
        self.__rate = start_rate

    def set_led_state(self, new_state):
        """Установить состояние светодиона (1 аргумент)
        state: string
            Состояние диода: on, off
        """
        if new_state in LED.__available_state:
            self.__state = new_state
            return "OK\n"
        return "FAILED\n"

    def get_led_state(self):
        """Получить состояние светодиода (0 аргументов)
        """
        return "OK " + self.__state + "\n"

    def set_led_color(self, new_color):
        """Установить цвет светодиода (1 аргумент)
        color: string
            Цвет: red, green, blue
        """
        if self.__state == "off":
            return "FAILED\n"
        if new_color in LED.__available_colors:
            self.__color = new_color
            return "OK\n"
        return "FAILED\n"

    def get_led_color(self):
        """Получить цвет светодиода (0 аргументов)
        """
        return "OK " + self.__color + "\n"

    def set_led_rate(self, new_rate):
        """Установить частоту мерцания светодиода (1 аргумент)
        rate: int
            Частота мерцания диода от 0 до 5
        """
        if self.__state == "off":
            return "FAILED\n"
        if new_rate in LED.__available_rate:
            self.__rate = new_rate
            return "OK\n"
        return "FAILED\n"

    def get_led_rate(self):
        """Получить частоту мерцания светодиода (0 аргументов)
        """
        return "OK " + str(self.__rate) + "\n"


class ClientThread(threading.Thread):
    def __init__(self, cl_ip, cl_port, cl_sock):
        threading.Thread.__init__(self)
        self.__ip = cl_ip
        self.__port = cl_port
        self.__sock = cl_sock
        self.__addr = cl_ip + ":" + str(cl_port)

    def run(self):
        print("Connection from: " + self.__addr)
        try:
            self.__sock.send("Welcome to the LED control panel!".encode())
            # Отправляем клиенту список доступных команд с описаниями
            self.__sock.send(json.dumps(commands_with_description, ensure_ascii=False).encode("utf-8"))
            while True:
                # Обрабатываем приходящие запросы пока соединение не будет разорвано.
                self.__sock.settimeout(120)  # установка таймаута
                data = self.__sock.recv(1024)
                if not data:
                    break
                data = data.decode("utf-8")  # декодируем полученные данные из bytes в utf-8
                data = data[0:-1] # отрезаем \n
                print("Request received: \"" + data + "\" from " + self.__addr)
                data = data.split()  # преобразуем в список
                # 1-й элемент списка это запрос к серверу
                request = data[0].replace("-", "_")
                # оставляем в данных только аргументы
                data.pop(0)
                # Проверяем существование метода
                if request in available_commands:
                    response = work_with_led(request, data)
                else:
                    response = "Error: nonexistent request."
                self.__sock.send(response.encode())
        except ConnectionResetError:
            print("Connection was broken.")
        except socket.timeout:
            print("Connection timed out.")
        except ConnectionAbortedError:
            print("Failed connection attempt")
        finally:
            self.__sock.close()
        global connections
        connections -= 1
        print("Client " + self.__addr + " disconnected")


def work_with_led(command, argument_list):
    """Функция с логикой работы с диодом"""
    # Преобразуем запрос в вызываемый метод
    command = getattr(working_led, command)
    # Проверяем количество переданных аргументов
    if len(signature(command).parameters) == len(argument_list):
        return command(*argument_list)
    else:
        return "FAILED\n"


if __name__ == "__main__":
    # Инициализация объекта
    working_led = LED()
    # Собираем все доступные методы LED в список
    available_commands = [method for method in dir(working_led) if callable(getattr(working_led, method))
                          and not method.startswith("__")]
    # Формируем словарь "команда: описание"
    commands_with_description = {method.replace('_', '-'):getattr(working_led, method).__doc__
                                 for method in available_commands}

    # Создаём сокет для связи с клиентом и переходим в режим прослушывания
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
    server_sock.bind(("", 12345))
    server_sock.listen(5)
    connections = 0
    print("Server is on")

    try:
        while True:  # Бесконечно обрабатываем входящие подключения
            if connections >= 3:
                continue
            client_sock, (client_ip, client_port) = server_sock.accept()
            connections += 1
            new_client_thread = ClientThread(client_ip, client_port, client_sock)
            new_client_thread.start()
    finally:
        server_sock.close()
    # При возниковени любой ошибки сокет корректно закроется
