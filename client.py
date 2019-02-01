# Клиент
#
# Получает от сервера список доступных команд для управления светодиодом и их описания


import socket
import json
from collections import OrderedDict


client_sock = socket.socket()
try:
    client_sock.settimeout(2)
    client_sock.connect(("127.0.0.1", 12345))
    # Получение приветственного сообщения
    response = client_sock.recv(1024)
    print(response.decode("utf-8"))
    # Получение словаря доступных команд (команда: описание)
    raw_data = client_sock.recv(1024)
    commands_with_doc = json.loads(raw_data.decode("utf-8"))
    # Упорядочивание словаря, чтобы при каждом запуске была одна последовательность
    commands_with_doc = OrderedDict(sorted(commands_with_doc.items()))
    available_numbers = [str(x) for x in range(1, len(commands_with_doc) + 1)] # Номера команд
    # Формируем упорядоченный словарь с нумерацией запросов (число: (команда, описание))
    key_command = OrderedDict()
    for pair, i in zip(commands_with_doc.items(), available_numbers):
        key_command[i] = pair
    # Выводим на экран описания доступных команд и их номера
    for item in key_command.items():
        print(str(item[0]) + ". " + str(item[1][1]))

    # Выбираем команду по номеру в списке
    command = input("Enter number of command ('q' for exit, 'h' for command list): ")
    while command != 'q':
        if command == 'h':
            for item in key_command.items():
                print(str(item[0]) + ". " + str(item[1][1]))
            command = input("Enter number of command ('q' for exit, 'h' for command list): ")
            continue
        if command not in available_numbers:
            command = input("Invalid input. Try again ('q' for exit, 'h' for command list): ")
            continue
        arguments = input("Enter argument (if not required, just press Enter): ")
        request = key_command[command][0] + " " + arguments + "\n"
        try:
            client_sock.send(request.encode())
            response = client_sock.recv(1024).decode("utf-8")
        except socket.error:
            print("Connection was broken.")
            break
        response = response[0:-1] # отрезаем \n
        print(response)
        command = input("Enter number of command ('q' for exit, 'h' for command list): ")
except ConnectionRefusedError:
    print("Can't connect. Server is offline.")
except ConnectionAbortedError:
    print("Connection timed out.")
except socket.timeout:
    print("Server is busy.")
finally:
    client_sock.close()
print("Bye-bye!")
input()