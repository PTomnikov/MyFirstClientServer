	Краткое описание работы сервера и клиента.

	Сервер содержит класс светодиода и имитирует взаимодействие с ним. При подключении
клиенту отправляется список доступных команд с описаниями. Допустимо управление
одновременно тремя клиентами.
	Клиент получает список доступных команд, что позволяет не вносить изменений при
добавлении новых команд или изменении существующих. На экране отображатеся список
доступных команд и их номера. Для управления светодиодом предлагается вводить номера
команд, а затем, при необходимости, аргументы.