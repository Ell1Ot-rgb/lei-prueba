"""
Panel de Control Web — Organismo Vivo v4.0
==========================================

App Flask que sirve una interfaz gráfica para controlar el sistema.
Ejecuta servicios en subprocesos y muestra su estado en tiempo real.

Uso:
    python panel_control.py
    → Abre http://localhost:5680
"""

import os
import sys
import json
import subprocess
import threading
import time
from pathlib import Path
from flask import Flask, render_template_string, jsonify, request
from dotenv import load_dotenv

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

app = Flask(__name__)

# Estado global de servicios
estado_servicios = {
    "watcher": {"pid": None, "proceso": None, "estado": "detenido"},
    "server":  {"pid": None, "proceso": None, "estado": "detenido"},
}

VAULT_PATH = os.environ.get("VAULT_PATH", r"C:\Users\Public\Robot\Zerg")


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Organismo Vivo v4.0 — Panel de Control</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0a0e1a;
            --bg-secondary: #111827;
            --bg-card: #1a2235;
            --bg-card-hover: #1f2a40;
            --accent: #6366f1;
            --accent-glow: rgba(99, 102, 241, 0.3);
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --border: rgba(99, 102, 241, 0.15);
            --border-active: rgba(99, 102, 241, 0.5);
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', -apple-system, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
        }
        .bg-grid {
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background-image:
                linear-gradient(rgba(99,102,241,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(99,102,241,0.03) 1px, transparent 1px);
            background-size: 40px 40px;
            z-index: 0;
        }
        .container {
            position: relative; z-index: 1;
            max-width: 1200px; margin: 0 auto; padding: 2rem;
        }
        /* Header */
        .header {
            text-align: center; margin-bottom: 2.5rem;
            padding: 2rem 0;
        }
        .header h1 {
            font-size: 2.2rem; font-weight: 800;
            background: linear-gradient(135deg, #818cf8, #6366f1, #4f46e5);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            letter-spacing: -0.02em;
        }
        .header .subtitle {
            color: var(--text-secondary); font-size: 0.95rem;
            margin-top: 0.5rem; font-weight: 400;
        }
        .header .version {
            display: inline-block; margin-top: 0.75rem;
            background: var(--bg-card); border: 1px solid var(--border);
            padding: 0.25rem 0.75rem; border-radius: 9999px;
            font-size: 0.75rem; color: var(--accent);
            font-family: 'JetBrains Mono', monospace;
        }
        /* Status bar */
        .status-bar {
            display: flex; gap: 1rem; margin-bottom: 2rem;
            flex-wrap: wrap;
        }
        .status-item {
            flex: 1; min-width: 180px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1rem 1.25rem;
        }
        .status-item .label {
            font-size: 0.7rem; text-transform: uppercase;
            letter-spacing: 0.05em; color: var(--text-muted);
            margin-bottom: 0.25rem;
        }
        .status-item .value {
            font-size: 1.05rem; font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
        }
        .status-item .value.online { color: var(--success); }
        .status-item .value.offline { color: var(--text-muted); }
        /* Grid */
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
            gap: 1.25rem;
        }
        /* Card */
        .card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1.5rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        .card:hover {
            border-color: var(--border-active);
            background: var(--bg-card-hover);
            transform: translateY(-2px);
            box-shadow: 0 8px 32px rgba(99, 102, 241, 0.1);
        }
        .card .icon {
            width: 48px; height: 48px;
            border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.5rem; margin-bottom: 1rem;
        }
        .card .icon.purple { background: rgba(99,102,241,0.15); }
        .card .icon.green  { background: rgba(16,185,129,0.15); }
        .card .icon.orange { background: rgba(245,158,11,0.15); }
        .card .icon.blue   { background: rgba(59,130,246,0.15); }
        .card .icon.red    { background: rgba(239,68,68,0.15); }
        .card h3 {
            font-size: 1.05rem; font-weight: 600;
            margin-bottom: 0.4rem;
        }
        .card p {
            font-size: 0.82rem; color: var(--text-secondary);
            line-height: 1.5; margin-bottom: 1.25rem;
        }
        .btn {
            display: inline-flex; align-items: center; gap: 0.5rem;
            padding: 0.6rem 1.2rem;
            border-radius: 10px;
            font-size: 0.82rem; font-weight: 500;
            cursor: pointer; border: none;
            transition: all 0.2s ease;
            font-family: 'Inter', sans-serif;
        }
        .btn-primary {
            background: var(--accent);
            color: white;
        }
        .btn-primary:hover {
            background: #4f46e5;
            box-shadow: 0 0 20px var(--accent-glow);
        }
        .btn-success {
            background: rgba(16,185,129,0.2);
            color: var(--success); border: 1px solid rgba(16,185,129,0.3);
        }
        .btn-success:hover { background: rgba(16,185,129,0.3); }
        .btn-danger {
            background: rgba(239,68,68,0.2);
            color: var(--danger); border: 1px solid rgba(239,68,68,0.3);
        }
        .btn-danger:hover { background: rgba(239,68,68,0.3); }
        .btn-outline {
            background: transparent;
            color: var(--text-secondary);
            border: 1px solid var(--border);
        }
        .btn-outline:hover {
            border-color: var(--accent);
            color: var(--accent);
        }
        .btn:disabled {
            opacity: 0.5; cursor: not-allowed;
        }
        /* Input */
        .input-group {
            margin-bottom: 1rem;
        }
        .input-group textarea {
            width: 100%;
            background: var(--bg-primary);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 0.75rem 1rem;
            color: var(--text-primary);
            font-family: 'Inter', sans-serif;
            font-size: 0.85rem;
            resize: vertical;
            min-height: 80px;
        }
        .input-group textarea:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 3px var(--accent-glow);
        }
        /* Log */
        .log {
            margin-top: 2rem;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1.5rem;
        }
        .log h3 {
            font-size: 0.95rem; margin-bottom: 1rem;
            display: flex; align-items: center; gap: 0.5rem;
        }
        .log-entries {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            max-height: 300px;
            overflow-y: auto;
            color: var(--text-secondary);
            line-height: 1.8;
        }
        .log-entry { padding: 0.15rem 0; }
        .log-entry .time { color: var(--text-muted); }
        .log-entry.ok .msg { color: var(--success); }
        .log-entry.error .msg { color: var(--danger); }
        .log-entry.info .msg { color: var(--accent); }
        /* Toast */
        .toast {
            position: fixed; bottom: 2rem; right: 2rem;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1rem 1.5rem;
            font-size: 0.85rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
            transform: translateY(100px);
            opacity: 0;
            transition: all 0.3s ease;
            z-index: 100;
        }
        .toast.show {
            transform: translateY(0);
            opacity: 1;
        }
        /* Dot indicator */
        .dot {
            display: inline-block;
            width: 8px; height: 8px;
            border-radius: 50%;
            margin-right: 0.4rem;
        }
        .dot.green { background: var(--success); box-shadow: 0 0 6px var(--success); }
        .dot.red   { background: var(--danger); }
        .dot.gray  { background: var(--text-muted); }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .dot.green { animation: pulse 2s infinite; }
    </style>
</head>
<body>
    <div class="bg-grid"></div>
    <div class="container">
        <div class="header">
            <h1>☉ Organismo Vivo</h1>
            <div class="subtitle">Panel de Control — Sistema Hexagonal Completo</div>
            <span class="version">v4.0 • Arquitectura Fenomenológica</span>
        </div>

        <div class="status-bar" id="statusBar">
            <div class="status-item">
                <div class="label">Vault Obsidian</div>
                <div class="value" id="vaultStatus">...</div>
            </div>
            <div class="status-item">
                <div class="label">Watcher</div>
                <div class="value" id="watcherStatus">...</div>
            </div>
            <div class="status-item">
                <div class="label">Webhook Server</div>
                <div class="value" id="serverStatus">...</div>
            </div>
            <div class="status-item">
                <div class="label">Último YO</div>
                <div class="value" id="lastYO">—</div>
            </div>
        </div>

        <div class="grid">
            <!-- Inicializar -->
            <div class="card">
                <div class="icon purple">🏗</div>
                <h3>Inicializar Vault</h3>
                <p>Crea toda la estructura de carpetas, templates Templater, dashboards Dataview y MOCs automáticos en Obsidian.</p>
                <button class="btn btn-primary" onclick="accion('init')">▶ Inicializar</button>
            </div>

            <!-- Pipeline -->
            <div class="card">
                <div class="icon green">◉</div>
                <h3>Ejecutar Pipeline</h3>
                <p>Procesa texto a través del pipeline completo: S1→S2→Fenómeno→Contexto→YO→Voluntad→Obsidian.</p>
                <div class="input-group">
                    <textarea id="inputTexto" placeholder="Escribe aquí el texto a procesar..."></textarea>
                </div>
                <button class="btn btn-success" onclick="accion('pipeline')">⚡ Procesar</button>
            </div>

            <!-- Watcher -->
            <div class="card">
                <div class="icon orange">👁</div>
                <h3>Monitor de Carpeta</h3>
                <p>Vigila la carpeta de entrada por archivos nuevos (.txt, .json, .md) y los procesa automáticamente.</p>
                <button class="btn btn-success" id="btnWatcher" onclick="accion('watcher_start')">▶ Iniciar</button>
                <button class="btn btn-danger" style="margin-left:0.5rem" onclick="accion('watcher_stop')">■ Detener</button>
            </div>

            <!-- Server -->
            <div class="card">
                <div class="icon blue">🌐</div>
                <h3>Servidor Webhook</h3>
                <p>Servidor HTTP en puerto 5679 que recibe señales de n8n para disparar el pipeline.</p>
                <button class="btn btn-success" id="btnServer" onclick="accion('server_start')">▶ Iniciar</button>
                <button class="btn btn-danger" style="margin-left:0.5rem" onclick="accion('server_stop')">■ Detener</button>
            </div>

            <!-- Obsidian -->
            <div class="card">
                <div class="icon purple">📖</div>
                <h3>Abrir Obsidian</h3>
                <p>Abre el vault "Zerg" directamente en Obsidian para visualizar fenómenos, YO, voluntad y lógica.</p>
                <button class="btn btn-outline" onclick="accion('open_obsidian')">📂 Abrir Vault</button>
            </div>

            <!-- Status -->
            <div class="card">
                <div class="icon red">🔍</div>
                <h3>Diagnóstico</h3>
                <p>Verifica el estado de todos los componentes: vault, dependencias, endpoints y archivos del sistema.</p>
                <button class="btn btn-outline" onclick="accion('status')">🔍 Verificar</button>
            </div>
        </div>

        <div class="log">
            <h3>📋 Log del Sistema</h3>
            <div class="log-entries" id="logEntries">
                <div class="log-entry info"><span class="time">[--:--:--]</span> <span class="msg">Panel de control iniciado. Esperando acciones...</span></div>
            </div>
        </div>
    </div>

    <div class="toast" id="toast"></div>

    <script>
        function now() {
            return new Date().toLocaleTimeString('es', {hour12: false});
        }

        function addLog(msg, tipo) {
            const el = document.getElementById('logEntries');
            const entry = document.createElement('div');
            entry.className = 'log-entry ' + (tipo || 'info');
            entry.innerHTML = '<span class="time">[' + now() + ']</span> <span class="msg">' + msg + '</span>';
            el.prepend(entry);
        }

        function showToast(msg) {
            const t = document.getElementById('toast');
            t.textContent = msg;
            t.classList.add('show');
            setTimeout(() => t.classList.remove('show'), 3000);
        }

        async function accion(tipo) {
            addLog('Ejecutando: ' + tipo + '...', 'info');

            try {
                let body = {action: tipo};
                if (tipo === 'pipeline') {
                    body.texto = document.getElementById('inputTexto').value;
                    if (!body.texto.trim()) {
                        addLog('Error: texto vacío', 'error');
                        return;
                    }
                }

                const res = await fetch('/api/action', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(body)
                });
                const data = await res.json();

                if (data.status === 'ok') {
                    addLog(data.mensaje || 'Completado', 'ok');
                    showToast('✅ ' + (data.mensaje || 'OK'));
                } else {
                    addLog('Error: ' + (data.mensaje || 'desconocido'), 'error');
                    showToast('❌ Error');
                }
            } catch(e) {
                addLog('Error de conexión: ' + e.message, 'error');
            }
            actualizarEstado();
        }

        async function actualizarEstado() {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();

                const vault = document.getElementById('vaultStatus');
                vault.textContent = data.vault_ok ? '✅ Online' : '❌ Sin crear';
                vault.className = 'value ' + (data.vault_ok ? 'online' : 'offline');

                const w = document.getElementById('watcherStatus');
                w.innerHTML = data.watcher === 'corriendo'
                    ? '<span class="dot green"></span>Activo'
                    : '<span class="dot gray"></span>Inactivo';
                w.className = 'value ' + (data.watcher === 'corriendo' ? 'online' : 'offline');

                const s = document.getElementById('serverStatus');
                s.innerHTML = data.server === 'corriendo'
                    ? '<span class="dot green"></span>:5679'
                    : '<span class="dot gray"></span>Inactivo';
                s.className = 'value ' + (data.server === 'corriendo' ? 'online' : 'offline');

                document.getElementById('lastYO').textContent = data.last_yo || '—';
            } catch(e) {}
        }

        setInterval(actualizarEstado, 5000);
        actualizarEstado();
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/status")
def api_status():
    vault = Path(VAULT_PATH)
    vault_ok = vault.exists() and (vault / "00_MOC").exists()

    # Leer último YO
    last_yo = "—"
    yo_dir = vault / "09_YO"
    if yo_dir.exists():
        yos = sorted(yo_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
        if yos:
            try:
                for linea in yos[0].read_text(encoding="utf-8", errors="replace").splitlines():
                    if linea.strip().startswith("tipo_yo:"):
                        last_yo = linea.split(":", 1)[1].strip().strip('"')
                        break
            except Exception:
                last_yo = "?"

    return jsonify({
        "vault_ok": vault_ok,
        "watcher": estado_servicios["watcher"]["estado"],
        "server": estado_servicios["server"]["estado"],
        "last_yo": last_yo,
    })


@app.route("/api/action", methods=["POST"])
def api_action():
    data = request.get_json(force=True, silent=True) or {}
    action = data.get("action", "")

    if action == "init":
        return _run_cmd(["python", "main.py", "init"], "Vault inicializado")

    elif action == "pipeline":
        texto = data.get("texto", "")
        return _run_cmd(
            ["python", "main.py", "pipeline", "--input", texto],
            "Pipeline ejecutado"
        )

    elif action == "status":
        return _run_cmd(["python", "main.py", "status"], "Diagnóstico completado")

    elif action == "watcher_start":
        return _start_servicio("watcher", ["python", "main.py", "watcher"])

    elif action == "watcher_stop":
        return _stop_servicio("watcher")

    elif action == "server_start":
        return _start_servicio("server", ["python", "main.py", "server"])

    elif action == "server_stop":
        return _stop_servicio("server")

    elif action == "open_obsidian":
        try:
            os.startfile(f"obsidian://open?path={VAULT_PATH}")
            return jsonify({"status": "ok", "mensaje": "Obsidian abierto"})
        except Exception as e:
            return jsonify({"status": "error", "mensaje": str(e)})

    return jsonify({"status": "error", "mensaje": f"Acción desconocida: {action}"})


def _run_cmd(cmd, msg_ok):
    """Ejecuta un comando y devuelve el resultado."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=60,
            cwd=str(ROOT), encoding="utf-8", errors="replace"
        )
        salida = (result.stdout + result.stderr).strip()[-500:]
        if result.returncode == 0:
            return jsonify({"status": "ok", "mensaje": msg_ok, "salida": salida})
        else:
            return jsonify({"status": "error", "mensaje": salida})
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)})


def _start_servicio(nombre, cmd):
    """Inicia un servicio en segundo plano."""
    if estado_servicios[nombre]["estado"] == "corriendo":
        return jsonify({"status": "ok", "mensaje": f"{nombre} ya está corriendo"})

    try:
        proceso = subprocess.Popen(
            cmd, cwd=str(ROOT),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
        estado_servicios[nombre]["proceso"] = proceso
        estado_servicios[nombre]["pid"] = proceso.pid
        estado_servicios[nombre]["estado"] = "corriendo"
        return jsonify({"status": "ok", "mensaje": f"{nombre} iniciado (PID: {proceso.pid})"})
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)})


def _stop_servicio(nombre):
    """Detiene un servicio en segundo plano."""
    proceso = estado_servicios[nombre].get("proceso")
    if proceso:
        try:
            proceso.terminate()
            proceso.wait(timeout=5)
        except Exception:
            proceso.kill()
    estado_servicios[nombre] = {"pid": None, "proceso": None, "estado": "detenido"}
    return jsonify({"status": "ok", "mensaje": f"{nombre} detenido"})


if __name__ == "__main__":
    print("=" * 50)
    print("  ORGANISMO VIVO v4.0 — Panel de Control Web")
    print(f"  → http://localhost:5680")
    print(f"  Vault: {VAULT_PATH}")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5680, debug=False)
