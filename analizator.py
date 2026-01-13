import re # Модуль для работы с регулярными выражениями
from collections import Counter, defaultdict # Специальные структуры данных для подсчёта
from typing import  Dict, List, Optional # Аннотация типов для лучшей документации
import sys # Модуль для системных функций (например, выход из программы)



def parse_log_line(line: str) -> Optional[Dict[str, str]]: #парсинг для автоматичсекой сборки информации 
    """Парсит строку лога и возвращает структурированные данные"""
    
    # Регулярное выражение для разбора формата лога Nginx 
    pattern = r'^(\S+) - - \[(.*?)\] "(\S+) (\S+) (\S+)" (\d+) (\d+) "([^"]*)"$'
    
    # Проверяем соответствует ли строка шаблону
    match = re.match(pattern, line.strip()) # .strip() удаляет пробелы в начале и конце строки
    if not match: # Если не соответствует шаблону
        return None # Возвращаем None для некорректных строк
    
    # Возвращаем словарь с разобранными данными
    return {
            "ip": match.group(1), # IP-адрес 
            "datetime": match.group(2), #"datetime": "2024-01-01 00:00:00
            "method":  match.group(3), #"method": "GET"
            "url": match.group(4), #"url": "/index.html
            "protocol": match.group(5), #"protocol": "HTTP/1.1"
            "status_code": match.group(6), #"status": "200
            "response_size": match.group(7), #"response_size": "12345
            "user_agent": match.group(8) if match.group(8) != "-" else "" #"user_agent": "Mozilla/5.0
    }   
    
def analyze_log_file(filename: str) -> Dict:
    """Анализирует файлы логов и возвращает статистику""" 

    # Инициализация счётчиков с помощью defaultdict
    method_counter = defaultdict(int) # Счётчик HTTP-методов (GET, POST и т.д.)
    ip_counter = defaultdict(int) # Счётчик IP-адресов
    status_counter = defaultdict(int) # Счётчик статус-кодов
    user_agent_counter = defaultdict(int) # Счётчик User-Agent
    
    
    total_response_size = 0 # Общий размер всех ответов
    total_requests = 0 # Общее количество запросов
    error_4xx = 0 # Количество клиентских ошибок (400-499)
    error_5xx = 0  # Количество серверных ошибок (500-599)
    
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:# Открытие файла на чтение в кодировке UTF-8 
            for line_num, line in enumerate(file,1): # Чтение файла построчно
                if not line.strip(): # Пропускаем пустые строки
                    continue
                
                log_entry = parse_log_line(line) # Парсинг текущей строки
                if not log_entry: # Пропускаем некорректные строки
                    print(f"Предупреждение: строка {line_num} пропущена (некорректный формат)")
                    continue
                try:
                    
                    # Преобразуем строковые значения в правильные типы
                    response_size = int(log_entry["response_size"]) # str → int
                    status_code = int(log_entry["status_code"]) # str → int
            
                    # Увеличиваем счётчики
                    total_requests += 1  #Увеличиваем общее количество запросов
                    total_response_size += response_size # Суммируем размер ответов
                    
                    user_agent = log_entry['user_agent'] # Получаем User-Agent из записи лога
                    if user_agent: # Если User-Agent не пустой
                        user_agent_counter[user_agent] += 1 # Увеличиваем счётчик User-Agent [user_agent
            
                    status_counter[status_code] += 1 # Увеличиваем счётчик статус-код
                    ip_counter[log_entry['ip']] += 1 # Увеличиваем счётчик IP-адреса
                    method_counter[log_entry['method']] += 1 # Увеличиваем счётчик HTTP-метода
                
                    # Считаем ошибки
                    print(f"Строка {line_num}: статус={status_code}, тип={type(status_code)}")
                    if 400 <= status_code < 500: # Если статус-код в диапазоне 400-499
                        print(f"  → Добавлена ошибка 4xx")
                        error_4xx += 1 # Увеличиваем счётчик клиентских ошибок
                    elif 500 <= status_code < 600: # Если статус-код в диапазоне 500-599
                        print(f"  → Добавлена ошибка 5xx")
                        error_5xx += 1 # Увеличиваем счётчик клиентских ошибок
                
                except(ValueError, KeyError) as e:
                    print(f"Предупреждение: ошибка в строке {line_num}: {e}")     
                    continue   
                
    except FileNotFoundError: # Если файл не найден
        print(f"ошибка: {filename} не найден")
        sys.exit(1) # Завершаем программу с кодом ошибки 1
    except Exception as e: # Любая другая ошибка
        print(f"ошибка при чтение: {e}")
        sys.exit(1) # Завершаем программу с кодом ошибки 1                
    
    # Подготавливаем результаты
    # Топ-10 IP-адресов
    top_ips = Counter(ip_counter).most_common(10) #Counter - подсчет количества элементов
    
    # Топ-5 User-Agents
    top_user_agents = Counter(user_agent_counter).most_common(5)
    
    # Средний размер ответа
    avg_response_size = total_response_size / total_requests if total_requests > 0 else 0
    
    # Возвращаем все собранные статистические данные
    return {
            "total_requests": total_requests,   # Общее количество запросов
            "top_ips": top_ips,   # Топ-10 IP-адресов
            "top_user_agents": top_user_agents, # Топ-5 User-Agent
            "avg_response_size": avg_response_size, # Средний размер ответа
            "error_4xx": error_4xx,# Количество ошибок 4xx
            "error_5xx": error_5xx, # Количество ошибок 5xx
            "status_counter": dict(status_counter), # Распределение статус-кодов
            "methods": dict(method_counter) # Распределение HTTP-методов
    }
    
    
def print_result(results: dict) -> None:
    """Выводит результаты анализа в удобочитаемом формате"""    
    
    print("=" * 50)
    print("Анализ логов сервера")
    print("=" * 50)
    
    print(f"\n Общее кол-во запросов: {results['total_requests']} requests") 
    
    print("\n1. Кол-во запросов по методам")
    print("-" * 30)
    for method, count in sorted(results['methods'].items()): # Итерация по словарю методов
        percentage = (count / results['total_requests'] * 100) if results['total_requests'] > 0 else 0   # Рассчитываем процентное соотношение
        print(f"{method:<8} {count:>8} ({percentage:>6.2f}%)") # Выводим метод, количество и процент с форматированием
    
    
    print("\n2. Топ-10 ip-адресов")
    print("-" * 50)
    for i,(ip, count) in enumerate(results['top_ips'],1): # enumerate с start=1 для нумерации с 1
        percentage = (count / results['total_requests'] * 100) if results['total_requests'] > 0 else 0   # Рассчитываем процентное соотношение
        print(f"{i:>2}. {ip:<20} {count:>8} запросов ({percentage:>6.2f}%)") # Выводим номер, IP-адрес, количество и процент с форматированием
     
    print("\n3. Распределение кодов ответов")
    print("-" * 30)
    for code,count in sorted(results['status_counter'].items()): # Сортировка по ключу (коду)
        percentage = (count / results['total_requests'] * 100) if results['total_requests'] > 0 else 0   # Рассчитываем процентное соотношение
        print(f"HTTP {code:<4} {count:>8} ({percentage:>6.2f}%)") # Выводим код, количество и процент с форматированием
            
    print("\n4. Ошибки:")  
    print("-" * 30)   
    total_errors = results['error_4xx'] + results['error_5xx']# Считаем общее количество ошибок
    error_percentage = (total_errors / results['total_requests'] * 100) if results['total_requests'] > 0 else 0  # Рассчитываем процент ошибок
     # Выводим статистику ошибок с форматированием
    print(f"Клиентские ошибки (4xx): {results['error_4xx']:>8}")
    print(f"Серверные ошибки (5xx):  {results['error_5xx']:>8}")
    print(f"Всего ошибок:           {total_errors:>8} ({error_percentage:>6.2f}%)")
    
    print("\n5. Топ-5  User-Agent:") 
    print("-" * 50)
    for i, (ua,count) in enumerate(results['top_user_agents'],1): # enumerate с start=1 
        
        ua_short = (ua[:50] + '...') if len(ua) > 50 else ua #обрезка строки, если длиннее 50 символов
        print(f" {i:2}. {ua_short}")  # Вывод номера и укороченного User-Agent
        print(f"Кол-во: {count}")  # Вывод количества запросов
        
    print("\n6. Средний  размер ответа:")
    print("-" * 30)
    # Выводим средний размер ответа с форматированием
    print(f"Средний размер: {results['avg_response_size']:,.2f} байт")
    # Выводим общий трафик с форматированием
    print(f"Общий трафик:   {results['avg_response_size'] * results['total_requests']:,.0f} байт")
    
    print("\n" + "=" * 50)
    
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Анализатор логов сервера") # Создаем парсер аргументов командной строки
    parser.add_argument('filename', help='Путь к файлу логов') # Добавляем аргумент для файла логов
    
    args = parser.parse_args() # Парсим аргументы командной строки
    
    if not args.filename: # Проверяем, что файл указан
        print("Ошибка: необходимо указать файл логов")
        sys.exit(1)
        
    print(f"\nЗагрузка логов из файла: {args.filename}") # Выводим сообщение о загрузке файла
    results = analyze_log_file(args.filename) # Анализируем логи и получаем результаты
    print_result(results) # Выводим результаты в удобочитаемом формате
