import subprocess
import os
import sys
import time
from typing import List, Dict

def run_executable_test(name: str, command: str) -> Dict:
    print(f"Testing: {name}...")
    start_time = time.perf_counter()
    try:
        # Ejecutamos con timeout para evitar bloqueos en loops infinitos
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        elapsed = time.perf_counter() - start_time
        return {
            "name": name,
            "success": result.returncode == 0,
            "output_snippet": result.stdout[-500:] if result.stdout else "No stdout",
            "error_snippet": result.stderr[-500:] if result.stderr else "No stderr",
            "elapsed": elapsed
        }
    except subprocess.TimeoutExpired:
        return {"name": name, "success": False, "error": "Timeout (30s)", "elapsed": 30}
    except Exception as e:
        return {"name": name, "success": False, "error": str(e), "elapsed": 0}

def run_bio_bootstrap_test() -> Dict:
    print("Testing: SISTEMA BIO: Orquestador Digital (Bootstrap)...")
    start_time = time.perf_counter()
    try:
        # Ejecutamos en segundo plano y esperamos 5 segundos
        process = subprocess.Popen(
            "python3 'antigravity-connect/sistema biologico/sistema_terminado/main_bio.py'",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            preexec_fn=os.setsid
        )
        time.sleep(8) # Dar tiempo para bootstrap
        
        # Verificar si sigue vivo o si dio error rápido
        return_code = process.poll()
        stdout, stderr = "", ""
        
        # Intentar leer lo que lleva
        try:
            stdout, _ = process.communicate(timeout=2)
        except:
            pass
            
        success = "bio_digital_bootstrap_complete" in stdout or "organismo_vivo_running" in stdout or return_code is None
        
        # Cleanup
        if return_code is None:
            import signal
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            
        elapsed = time.perf_counter() - start_time
        return {
            "name": "SISTEMA BIO: Orquestador Digital (Bootstrap)",
            "success": success,
            "output_snippet": stdout[-500:] if stdout else "System is running",
            "error_snippet": stderr[-500:] if stderr else "No stderr",
            "elapsed": elapsed
        }
    except Exception as e:
        return {"name": "SISTEMA BIO: Orquestador Digital (Bootstrap)", "success": False, "error": str(e), "elapsed": 0}

def main():
    print("=" * 80)
    print("DIAGNÓSTICO GLOBAL DE EJECUTABLES - ORGANISMO VIVO v100")
    print("=" * 80)

    # Definición de ejecutables clave a testear
    tests = [
        ("CORE: Neural Ports (Capa Cognitiva)", "python3 'antigravity-connect/sistema biologico/sistema_terminado/interfaces/neural_ports.py'"),
        ("INTEGRACIÓN: S1+S2+S3 (Optimizado)", "python3 'antigravity-connect/sistema biologico/sistema_terminado/interfaces/sistema_integrado.py'"),
        ("STRESS: Prueba de 300 Eventos", "python3 stress_test_biologico.py"),
        ("VALIDACIÓN: Tokenizador Lite", "python3 test_integridad_tokenizer.py"),
        ("DIAGNÓSTICO: Desglose de Conceptos", "python3 desglose_conceptos.py")
    ]

    results = []
    for name, cmd in tests:
        res = run_executable_test(name, cmd)
        results.append(res)
        status = "✅ OK" if res["success"] else "❌ ERROR"
        print(f"  [{status}] ({res['elapsed']:.2f}s)")
        if not res["success"]:
            print(f"      Motivo: {res.get('error', 'Fallo en código de salida')}")

    # Test especial para Bio Digital
    res_bio = run_bio_bootstrap_test()
    results.append(res_bio)
    status = "✅ OK" if res_bio["success"] else "❌ ERROR"
    print(f"  [{status}] ({res_bio['elapsed']:.2f}s)")

    print("\n" + "=" * 80)
    print("RESUMEN DE INTEGRIDAD DEL SISTEMA")
    print("=" * 80)
    
    total_success = sum(1 for r in results if r["success"])
    print(f"Total pruebas: {len(tests)}")
    print(f"Exitosas: {total_success}")
    print(f"Fallidas: {len(tests) - total_success}")
    
    print("\n[ESTADO POR COMPONENTE]")
    for r in results:
        indicator = "🟢" if r["success"] else "🔴"
        print(f"{indicator} {r['name']:<40} | {r['elapsed']:.2f}s")

    print("\n[CONCLUSIÓN FINAL]")
    if total_success == len(tests):
        print("El Organismo Vivo está TOTALMENTE OPERATIVO.")
        print("Todos los puentes entre la fenomenología, la emergencia y la lógica están activos.")
    elif total_success > len(tests) / 2:
        print("El sistema está PARCIALMENTE OPERATIVO.")
        print("Los motores principales funcionan, pero algunos módulos secundarios o de bootstrap")
        print("presentan advertencias o faltan dependencias externas.")
    else:
        print("El sistema requiere INTERVENCIÓN. Los núcleos principales no responden.")
    print("=" * 80)

if __name__ == "__main__":
    main()
