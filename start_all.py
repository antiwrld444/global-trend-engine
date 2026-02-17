import subprocess
import sys
import time
import os
import threading

def stream_logs(pipe, prefix):
    for line in iter(pipe.readline, b''):
        print(f"{prefix} {line.decode().strip()}")

def start():
    print("🚀 GTOE: Launching full system...")
    
    # Создаем папку логов если нет
    os.makedirs("logs", exist_ok=True)
    
    # 1. Запуск пайплайна сбора данных
    print("📦 Starting Data Pipeline...")
    # Запускаем пайплайн так, чтобы мы могли читать его вывод
    pipeline = subprocess.Popen([sys.executable, "main.py"], 
                                stdout=subprocess.PIPE, 
                                stderr=subprocess.STDOUT)
    
    # Запускаем поток для проброса логов в консоль
    log_thread = threading.Thread(target=stream_logs, args=(pipeline.stdout, "[PIPELINE]"), daemon=True)
    log_thread.start()
    
    # Даем немного времени на инициализацию
    time.sleep(3)
    
    # 2. Запуск дашборда Streamlit
    print("📊 Starting Visual Dashboard...")
    try:
        # Streamlit сам забирает управление консолью, но логи пайплайна будут пробрасываться потоком
        subprocess.run(["streamlit", "run", "src/dashboard.py"])
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        pipeline.terminate()

if __name__ == "__main__":
    start()
