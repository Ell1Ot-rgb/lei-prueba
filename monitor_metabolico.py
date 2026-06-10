import psutil
import time
import os
import json
from datetime import datetime

def monitor_salud_metabolica(duration_sec=60, interval=1):
    print(f"Iniciando Monitoreo Metabólico (Duración: {duration_sec}s)...")
    print("-" * 60)
    print(f"{'Timestamp':<20} | {'CPU %':<10} | {'RAM (MB)':<10} | {'Load 1m':<10}")
    print("-" * 60)
    
    stats = []
    
    start_time = time.time()
    while time.time() - start_time < duration_sec:
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().used / (1024 * 1024)
        load = os.getloadavg()[0]
        ts = datetime.now().strftime("%H:%M:%S")
        
        print(f"{ts:<20} | {cpu:<10.1f} | {ram:<10.1f} | {load:<10.2f}")
        
        stats.append({
            "ts": ts,
            "cpu": cpu,
            "ram": ram,
            "load": load
        })
        
        time.sleep(interval)
    
    print("-" * 60)
    with open("metabolismo_report.json", "w") as f:
        json.dump(stats, f, indent=2)
    print("Reporte guardado en metabolismo_report.json")

if __name__ == "__main__":
    monitor_salud_metabolica()
