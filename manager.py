#!/usr/bin/env python3
"""
Управляющий скрипт для проекта "Агрегатор IT-вакансий Уфы"
Работает в интерактивном режиме.
"""

import os
import sys
import subprocess
import venv
import socket
import webbrowser
import signal
import time
from pathlib import Path

# Цвета для вывода
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"

# Константы
VENV_DIR = "venv"
REQUIREMENTS = "requirements.txt"
PARSER_SCRIPT = "main.py"
INDEX_HTML = "index.html"
PID_FILE = ".server.pid"

# Вспомогательные функции
def clear_screen():
    """Очистка экрана"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_colored(text, color=RESET, bold=False):
    """Цветной вывод"""
    if bold:
        print(f"{BOLD}{color}{text}{RESET}")
    else:
        print(f"{color}{text}{RESET}")

def get_venv_paths():
    """Возвращает пути к python и pip внутри venv"""
    if sys.platform == "win32":
        python_exe = os.path.join(VENV_DIR, "Scripts", "python.exe")
        pip_exe = os.path.join(VENV_DIR, "Scripts", "pip.exe")
    else:
        python_exe = os.path.join(VENV_DIR, "bin", "python")
        pip_exe = os.path.join(VENV_DIR, "bin", "pip")
    return python_exe, pip_exe

def venv_exists():
    return os.path.exists(VENV_DIR)

def is_server_running():
    """Проверяет, запущен ли сервер (по наличию PID-файла)"""
    return os.path.exists(PID_FILE)

def get_server_pid():
    if is_server_running():
        with open(PID_FILE, "r") as f:
            return int(f.read().strip())
    return None

def find_free_port(start=8000, end=8010):
    """Поиск свободного порта в диапазоне"""
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('', port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"Нет свободных портов в диапазоне {start}-{end}")

def wait_for_key():
    """Ожидание нажатия Enter"""
    input("\nНажмите Enter, чтобы продолжить...")

# Основные действия
def action_install():
    """Установка / подготовка окружения"""
    clear_screen()
    print_colored("УСТАНОВКА ОКРУЖЕНИЯ", BLUE, bold=True)
    try:
        if not venv_exists():
            print("Создаём виртуальное окружение...")
            venv.create(VENV_DIR, with_pip=True)
        else:
            print("Виртуальное окружение уже существует.")

        python_exe, pip_exe = get_venv_paths()
        if not os.path.exists(pip_exe):
            raise RuntimeError("pip не найден в виртуальном окружении")

        print("Устанавливаем зависимости из requirements.txt...")
        subprocess.run([pip_exe, "install", "-r", REQUIREMENTS], check=True)

        print_colored("Окружение успешно подготовлено.", GREEN)
    except Exception as e:
        print_colored(f"Ошибка: {e}", RED)
    wait_for_key()

def action_run():
    """Запуск парсера и сервера"""
    clear_screen()
    print_colored("ЗАПУСК", BLUE, bold=True)

    # Проверка наличия venv
    if not venv_exists():
        print_colored("Виртуальное окружение не найдено. Сначала выполните 'Установка'.", RED)
        wait_for_key()
        return

    python_exe, _ = get_venv_paths()
    if not os.path.exists(python_exe):
        print_colored("Python в виртуальном окружении не найден.", RED)
        wait_for_key()
        return

    # 1. Запуск парсера
    print("Запуск парсера...")
    try:
        subprocess.run([python_exe, PARSER_SCRIPT], check=True)
    except subprocess.CalledProcessError as e:
        print_colored(f"Ошибка при выполнении парсера: {e}", RED)
        wait_for_key()
        return

    if not os.path.exists("vacancies.json"):
        print_colored("Файл vacancies.json не создан. Парсер не сработал.", RED)
        wait_for_key()
        return

    # 2. Поиск порта
    try:
        port = find_free_port()
        print(f"Найден свободный порт: {port}")
    except RuntimeError as e:
        print_colored(f"{e}", RED)
        wait_for_key()
        return

    # 3. Запуск сервера
    print(f"Запуск HTTP-сервера на порту {port}...")
    try:
        server_process = subprocess.Popen(
            [python_exe, "-m", "http.server", str(port)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        # Сохраняем PID
        with open(PID_FILE, "w") as f:
            f.write(str(server_process.pid))
    except Exception as e:
        print_colored(f"Не удалось запустить сервер: {e}", RED)
        wait_for_key()
        return

    # 4. Открываем браузер
    url = f"http://localhost:{port}/{INDEX_HTML}"
    print(f"Открываем браузер: {url}")
    webbrowser.open(url)

    print_colored("Сервер успешно запущен.", GREEN)
    wait_for_key()

def action_stop():
    """Остановка сервера"""
    clear_screen()
    print_colored("ОСТАНОВКА СЕРВЕРА", BLUE, bold=True)

    if not is_server_running():
        print_colored("Сервер не запущен (PID-файл отсутствует).", YELLOW)
        wait_for_key()
        return

    pid = get_server_pid()
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=True)
        else:
            os.kill(pid, signal.SIGTERM)
        print_colored(f"Процесс {pid} остановлен.", GREEN)
    except ProcessLookupError:
        print_colored("Процесс уже завершён.", YELLOW)
    except Exception as e:
        print_colored(f"Ошибка при остановке: {e}", RED)
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
    wait_for_key()

def action_status():
    """Показать текущий статус"""
    clear_screen()
    print_colored("СТАТУС", BLUE, bold=True)

    print("Виртуальное окружение: " + ("установлено" if venv_exists() else "не установлено"))
    print("Файл vacancies.json: " + ("есть" if os.path.exists("vacancies.json") else "отсутствует"))

    if is_server_running():
        pid = get_server_pid()
        print_colored(f"HTTP-сервер: ЗАПУЩЕН (PID: {pid})", GREEN)
    else:
        print_colored("HTTP-сервер: ОСТАНОВЛЕН", RED)

    wait_for_key()

# Главное меню
def main_menu():
    while True:
        clear_screen()

        # Заголовок со статусом сервера
        print_colored("=" * 60, BLUE)
        print_colored("УПРАВЛЕНИЕ ПРОЕКТОМ АГРЕГАТОРА ВАКАНСИЙ", BLUE, bold=True)
        print_colored("=" * 60, BLUE)

        # Статус сервера в цвете
        if is_server_running():
            print_colored("Сервер: ЗАПУЩЕН", GREEN, bold=True)
        else:
            print_colored("Сервер: ОСТАНОВЛЕН", RED, bold=True)
        print()

        print("1. Установка / подготовка окружения")
        print("2. Запуск (парсер + сервер + браузер)")
        print("3. Остановка сервера")
        print("4. Показать статус")
        print("5. Выход")
        print()

        choice = input("Выберите действие (1-5): ").strip()

        if choice == "1":
            action_install()
        elif choice == "2":
            action_run()
        elif choice == "3":
            action_stop()
        elif choice == "4":
            action_status()
        elif choice == "5":
            clear_screen()
            print_colored("До свидания!", BLUE, bold=True)
            break
        else:
            clear_screen()
            print_colored("Неверный ввод, попробуйте снова.", RED)
            wait_for_key()

# Точка входа
if __name__ == "__main__":
    # Если передан аргумент, выполняем соответствующее действие (для совместимости)
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "install":
            action_install()
        elif cmd == "run":
            action_run()
        elif cmd == "stop":
            action_stop()
        elif cmd == "status":
            action_status()
        else:
            print("Неизвестная команда. Доступные: install, run, stop, status")
        sys.exit(0)
    else:
        main_menu() 
