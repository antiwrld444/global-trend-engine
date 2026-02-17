import subprocess
import sys
import time
import os

def start():
    print("🚀 GTOE: Launching full system...")
    
    # 1. Запуск пайплайна сбора данных в фоновом режиме
    print("📦 Starting Data Pipeline (Background)...")
    pipeline = subprocess.Popen([sys.executable, "main.py"], 
                                stdout=open("logs/pipeline_out.log", "a"), 
                                stderr=open("logs/pipeline_err.log", "a"))
    
    # Даем немного времени на инициализацию БД
    time.sleep(3)
    
    # 2. Запуск дашборда Streamlit
    print("📊 Starting Visual Dashboard...")
    try:
        subprocess.run(["streamlit", "run", "src/dashboard.py"])
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        pipeline.terminate()

if __name__ == "__main__":
    start()
