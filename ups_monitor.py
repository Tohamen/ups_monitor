import subprocess
import re
from http.server import BaseHTTPRequestHandler, HTTPServer

# Создаем метрики
metrics = {
    'ups_battery_charge_percent': 0,  # Уровень заряда батареи в процентах
    'ups_load_watt': 0,               # Нагрузка в ваттах
    'ups_runtime_seconds': 0,         # Оставшееся время работы в секундах
    'ups_utility_voltage': 0,         # Входное напряжение (Utility Voltage)
    'ups_output_voltage': 0,          # Выходное напряжение (Output Voltage)
}

def parse_pwrstat_output():
    result = subprocess.run(['pwrstat', '-status'], capture_output=True, text=True, encoding='utf-8')
    output = result.stdout

    # Парсим данные
    charge = re.search(r'Battery Capacity\.+\s+(\d+) %', output)
    load = re.search(r'Load\.+\s+(\d+) Watt', output)
    runtime = re.search(r'Remaining Runtime\.+\s+(\d+) min', output)
    utility_voltage = re.search(r'Utility Voltage\.+\s+(\d+) V', output)
    output_voltage = re.search(r'Output Voltage\.+\s+(\d+) V', output)

    if charge:
        metrics['ups_battery_charge_percent'] = int(charge.group(1))
    if load:
        metrics['ups_load_watt'] = int(load.group(1))
    if runtime:
        metrics['ups_runtime_seconds'] = int(runtime.group(1)) * 60
    if utility_voltage:
        metrics['ups_utility_voltage'] = int(utility_voltage.group(1))
    if output_voltage:
        metrics['ups_output_voltage'] = int(output_voltage.group(1))

class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()

            # Обновляем данные перед отправкой
            parse_pwrstat_output()

            # Формируем ответ в формате Prometheus
            response = []
            for name, value in metrics.items():
                response.append(f"{name} {value}")
            self.wfile.write("\n".join(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    # Запускаем HTTP-сервер на порту 8000
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, MetricsHandler)
    print("Starting server on port 8000...")

    try:
        httpd.serve_forever()  # Запускаем сервер
    except KeyboardInterrupt:
        print("\nServer is shutting down gracefully...")
    finally:
        httpd.server_close()  # Закрываем сервер
        print("Server stopped.")