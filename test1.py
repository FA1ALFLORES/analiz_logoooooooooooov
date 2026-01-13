"""
Тесты для модуля analyzer.py
"""

import unittest
import tempfile
import os
from analizator import parse_log_line, analyze_log_file, print_result


class TestLogAnalyzer(unittest.TestCase):
    """Тесты для анализатора логов"""
    
    def test_parse_log_line_correct(self):
        """Тест парсинга корректной строки лога"""
        test_line = '192.168.1.1 - - [01/Jan/2024:00:00:01 +0000] "GET /index.html HTTP/1.1" 200 1234 "Mozilla/5.0"'
        result = parse_log_line(test_line)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['ip'], '192.168.1.1')
        self.assertEqual(result['method'], 'GET')
        self.assertEqual(result['url'], '/index.html')
        self.assertEqual(result['status_code'], '200')
        self.assertEqual(result['response_size'], '1234')
        self.assertEqual(result['user_agent'], 'Mozilla/5.0')
    
    def test_parse_log_line_incorrect(self):
        """Тест парсинга некорректной строки"""
        test_line = "некорректная строка лога"
        result = parse_log_line(test_line)
        self.assertIsNone(result)
    
    def test_parse_log_line_empty_user_agent(self):
        """Тест парсинга строки с пустым User-Agent"""
        test_line = '192.168.1.1 - - [01/Jan/2024:00:00:01 +0000] "GET /index.html HTTP/1.1" 200 1234 "-"'
        result = parse_log_line(test_line)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['user_agent'], "")
    
    def test_analyze_log_file(self):
        """Тест анализа файла логов"""
        test_logs = [
            '192.168.1.1 - - [01/Jan/2024:00:00:01 +0000] "GET /index.html HTTP/1.1" 200 1234 "Mozilla/5.0"',
            '192.168.1.2 - - [01/Jan/2024:00:00:02 +0000] "POST /api/data HTTP/1.1" 201 567 "PostmanRuntime/7.32.3"',
            '192.168.1.1 - - [01/Jan/2024:00:00:03 +0000] "GET /about.html HTTP/1.1" 200 2345 "Mozilla/5.0"',
            '192.168.1.3 - - [01/Jan/2024:00:00:04 +0000] "GET /nonexistent HTTP/1.1" 404 123 "-"',
            '192.168.1.1 - - [01/Jan/2024:00:00:05 +0000] "GET /index.html HTTP/1.1" 200 1234 "Mozilla/5.0"',
            '192.168.1.4 - - [01/Jan/2024:00:00:06 +0000] "GET /api/users HTTP/1.1" 500 789 "curl/7.68.0"',
            '192.168.1.2 - - [01/Jan/2024:00:00:07 +0000] "PUT /api/update HTTP/1.1" 403 256 "PostmanRuntime/7.32.3"',
            '192.168.1.5 - - [01/Jan/2024:00:00:08 +0000] "DELETE /api/resource HTTP/1.1" 204 0 "CustomClient/1.0"',
        ]
        
        print("\n🔍 Отладочная информация:")
        print(f"Всего строк в тесте: {len(test_logs)}")
        
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False, encoding='utf-8') as f:
            f.write('\n'.join(test_logs))
            temp_filename = f.name
        
        try:
            # Анализируем файл
            results = analyze_log_file(temp_filename)
            
            # Проверяем результаты
            print(f"Всего запросов: {results['total_requests']}")
            print(f"Ошибки 4xx: {results['error_4xx']}")
            print(f"Ошибки 5xx: {results['error_5xx']}")
            print(f"Статус-коды: {results['status_counter']}")
            print(f"Методы: {results['methods']}")
        
            # Проверяем результаты
            self.assertEqual(results['total_requests'], 8)
            self.assertEqual(results['error_4xx'], 2)  # 404 и 403
            self.assertEqual(results['error_5xx'], 1)  # 500
            # Проверяем топ IP
            top_ips = dict(results['top_ips'])
            self.assertEqual(top_ips['192.168.1.1'], 3)
            
        finally:
            # Удаляем временный файл
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
    
    def test_analyze_empty_file(self):
        """Тест анализа пустого файла"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False, encoding='utf-8') as f:
            f.write('')  # Пустой файл
            temp_filename = f.name
        
        try:
            results = analyze_log_file(temp_filename)
            self.assertEqual(results['total_requests'], 0)
            self.assertEqual(results['avg_response_size'], 0)
            self.assertEqual(len(results['top_ips']), 0)
            self.assertEqual(len(results['top_user_agents']), 0)
        finally:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
    
    def test_analyze_file_with_invalid_lines(self):
        """Тест анализа файла с некорректными строками"""
        test_logs = [
            '192.168.1.1 - - [01/Jan/2024:00:00:01 +0000] "GET /index.html HTTP/1.1" 200 1234 "Mozilla/5.0"',
            'НЕКОРРЕКТНАЯ СТРОКА',  # Некорректная строка
            '192.168.1.2 - - [01/Jan/2024:00:00:02 +0000] "POST /api/data HTTP/1.1" 201 567 "PostmanRuntime/7.32.3"',
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False, encoding='utf-8') as f:
            f.write('\n'.join(test_logs))
            temp_filename = f.name
        
        try:
            results = analyze_log_file(temp_filename)
            self.assertEqual(results['total_requests'], 2)  # Только 2 корректные строки
        finally:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)


class TestPrintResult(unittest.TestCase):
    """Тесты функции вывода результатов"""
    
    def test_print_result_format(self):
        """Тест форматирования вывода"""
        test_results = {
            'total_requests': 100,
            'methods': {'GET': 60, 'POST': 30, 'PUT': 10},
            'top_ips': [('192.168.1.1', 25), ('192.168.1.2', 15)],
            'top_user_agents': [('Mozilla/5.0', 40), ('PostmanRuntime/7.32.3', 20)],
            'status_counter': {200: 70, 404: 10, 500: 5},
            'error_4xx': 10,
            'error_5xx': 5,
            'avg_response_size': 1234.56
        }
        
        # Проверяем, что функция не вызывает исключений
        try:
            print_result(test_results)
            self.assertTrue(True)  # Если дошли сюда, значит исключений не было
        except Exception as e:
            self.fail(f"print_result вызвала исключение: {e}")


def run_all_tests():
    """Запускает все тесты с красивым выводом"""
    print("=" * 60)
    print("ЗАПУСК ТЕСТОВ АНАЛИЗАТОРА ЛОГОВ".center(60))
    print("=" * 60)
    
    # Создаем тестовый набор
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLogAnalyzer)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPrintResult))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 60)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ".center(60))
    print("=" * 60)
    
    if result.wasSuccessful():
        print("\n✅ ВСЕ ТЕСТЫ УСПЕШНО ПРОЙДЕНЫ!")
        print(f"Выполнено тестов: {result.testsRun}")
    else:
        print("\n❌ ОБНАРУЖЕНЫ ОШИБКИ В ТЕСТАХ:")
        for test, error in result.failures:
            print(f"\nСбой в тесте: {test}")
            print(f"Ошибка: {error}")
        for test, error in result.errors:
            print(f"\nОшибка в тесте: {test}")
            print(f"Ошибка: {error}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    # Можно запустить все тесты или отдельные
    import argparse
    
    parser = argparse.ArgumentParser(description='Тестирование анализатора логов')
    parser.add_argument('--test', type=str, help='Запустить конкретный тест (например: TestLogAnalyzer.test_parse_log_line_correct)')
    
    args = parser.parse_args()
    
    if args.test:
        # Запуск конкретного теста
        suite = unittest.TestSuite()
        suite.addTest(unittest.defaultTestLoader.loadTestsFromName(args.test))
        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(suite)
    else:
        # Запуск всех тестов
        run_all_tests()