# Sistema Vivo Hexagonal — Final v2
# README Definitivo

## ¿Qué es este sistema?

**Sistema Vivo Hexagonal Final v2** es la versión refinada y completa del Organismo Vivo,
un pipeline cognitivo de 9 niveles ontológicos basado en arquitectura hexagonal, motores
fenomenológicos S1-S4 + Bio + Chaos + YO, y 5 sistemas lógicos integrados.

El sistema convierte datos brutos (`:-....yo...`) en proyecciones intencionales (Voluntad),
sincronizando todo el proceso con un Cerebro Digital en Obsidian.

---

## Estructura del Proyecto

```
sistema_vivo_final_v2/
│
├── core_new/                        ← Dominio hexagonal (S1-S4 + Bio + Chaos + YO)
│   ├── domain/                      ← Entidades ontológicas (9 niveles)
│   │   ├── preinstancia.py          ← ø  Nivel -4
│   │   ├── instancia.py             ← •  Nivel -3
│   │   ├── vohexistencia.py         ← ◊  Nivel -1
│   │   ├── fenomeno.py              ← ◉  Nivel  0  ← punto de emergencia
│   │   ├── contexto.py              ← ⊞  Nivel +1
│   │   ├── metacontexto.py          ← ⊡⊠ Nivel +2/+3
│   │   └── simbologia.py            ← Simbología completa del sistema
│   └── engines/
│       ├── pipeline_evolucionado.py ← Orquestador principal v4.0
│       ├── yo_emergente/            ← ☉ MotorYoEmergente (6 tipos de TipoYO)
│       ├── relaciones/              ← 12 tipos de relaciones fenomenológicas
│       ├── retroalimentacion/       ← ⟳ Ciclo hermenéutico YO→Instancias
│       ├── voluntad/                ← → Proyecciones Entwurf (heideggeriano)
│       ├── logica_extendida/        ← Modal + Mereológica + Deóntica
│       ├── logica_pura/             ← Axiomas Horn + Mundos Hipotéticos
│       ├── s1_fenomenologia/        ← ∂ Motor S1
│       ├── s2_emergencia/           ← ∫ Motor S2
│       ├── s3_logica/               ← ⊢ Motor S3
│       ├── s4_prediccion/           ← ⊗ Motor S4 (ESN)
│       ├── bio/                     ← ♺ Motor biológico
│       └── chaos/                   ← ⚡ Motor caos (Regla 110)
│
├── adapters/
│   ├── inbound/
│   │   ├── webhook_handler.py       ← Endpoint n8n → pipeline
│   │   └── carpeta_watcher.py       ← Watcher carpeta R de entrada
│   └── outbound/
│       ├── obsidian_sync.py         ← ✅ v4.0: 12 carpetas + 5 sistemas lógicos
│       ├── neo4j_repository.py      ← Persistencia en Neo4j Azure
│       ├── n8n_integrator.py        ← Webhooks n8n
│       └── gemini_client.py         ← Embeddings Gemini
│
├── core/                            ← Sistema original v1 (Bio, Emotion, etc.)
│
├── inicializar_vault_v4.py          ← ✅ NUEVO: Inicializa vault Obsidian
├── panel_control.py                 ← Panel de control del sistema
├── main.py                          ← Punto de entrada principal
├── .env.template                    ← Variables de entorno
└── requirements.txt                 ← Dependencias
```

---

## Pipeline Completo (v4.0)

```
:-....yo...        ← ENTRADA DEL SISTEMA

     ↓ S1 ∂
ø PreInstancia      Nivel -4   Dato crudo sin forma
     ↓
• Instancia         Nivel -3   Primer punto de existencia
     ↓
∇ Gradiente         Nivel -2   Dirección relacional
     ↓ S2 ∫
◊ Vohexistencia     Nivel -1   Coexistencia cristalizada
     ↓
◉ Fenomeno          Nivel  0   Lo que se muestra ← punto de lectura
     ↓ S3 ⊢ + Lógica
⊞ Contexto          Nivel +1   Totalidad referencial
     ↓
⊡ Macrocontexto     Nivel +2   Agrupación de contextos
     ↓ □◇ Modal (Kripke)
⊠ Metacontexto      Nivel +3   Reflexión sobre contextos
     ↓ ∞ YO
☉ YO Emergente      Nivel +4   Autoconciencia (6 tipos: PROTO→NARRATIVO)
     ↓ ⟳ Retroalimentación
•* Resignificación  → YO resignifica instancias que lo generaron
     ↓ → Voluntad
→ Proyección        Entwurf heideggeriano (dirección + acciones)
     ↓ OFP Deóntica
✅ Obsidian Sync    → 12 carpetas + 5 sistemas lógicos
```

---

## Sistemas Lógicos Integrados (v4.0)

| Sistema | Símbolo | Motor | Vault Target |
|:--------|:-------:|:------|:-------------|
| Axiomas Horn | ⊢ | S3 | 12_Logica/Pura/axiomas/ |
| Mundos Hipotéticos | □◇ | S3+∫ | 12_Logica/Pura/mundos_hipoteticos/ |
| Modal (Kripke) | □ ◇ | MotorModal | 12_Logica/Modal/ |
| Mereológica | ⊂ ∪ | MotorMereologico | 12_Logica/Mereologica/ |
| Deóntica | O F P | MotorDeontico | 12_Logica/Deontica/ |

---

## Doce Relaciones Fenomenológicas

| Símbolo | Tipo | Bidireccional |
|:-------:|:-----|:-------------:|
| ≈ | SE_PARECE_A | ✓ |
| ⊕ | AGRUPA | — |
| ↗ | SURGE_DE | — |
| ⊘ | CONTRADICE | ✓ |
| ⊙ | OBSERVA | — |
| → | ACTUA_EN | — |
| ⊃ | INCLUYE | — |
| — | RELACION | — |
| ⇒ | TRANSFORMA_EN | — |
| ⤴ | EMERGE_COMO | — |
| ⊳ | GENERA | — |
| ⊶ | DECIDE | — |

---

## Instalación Rápida

### 1. Variables de entorno

```bash
cp .env.template .env
# Editar con tus credenciales:
# NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
# LIGHTRAG_API_URL
# VAULT_PATH (ruta al vault de Obsidian)
```

### 2. Dependencias

```bash
pip install -r requirements.txt
```

### 3. Inicializar vault Obsidian

```bash
python inicializar_vault_v4.py --vault "C:/Users/Public/Robot/Zerg"
```

### 4. Ejecutar sistema

```bash
python main.py
```

### 5. Panel de control

```bash
python panel_control.py
```

---

## Cerebro Digital en Obsidian

Abrir Obsidian → Open folder as vault → seleccionar la ruta en `VAULT_PATH`.

Plugins requeridos:
- **Dataview** — Queries dinámicas en `_Dashboard/`
- **Templater** — Templates en `_Templates/`
- **Graph View** — Visualización del grafo ontológico

---

## Simbología del Sistema

```
Niveles:  ø • ∇ ◊ ◉ ⊞ ⊡ ⊠ ☉ →
Motores:  ∂ ∫ ⊢ ⊗ ♺ ⚡ ∞
Relac.:   ≈ ⊕ ↗ ⊘ ⊙ → ⊃ — ⇒ ⤴ ⊳ ⊶
Lógica:   ⊢ □ ◇ ⊂ ∪ O F P
Ciclo:    :-....yo...
```

---

## Versiones

| Versión | Descripción |
|:--------|:------------|
| v1.0 | Sistema hexagonal base (S1-S4 + Bio + Chaos) |
| v2.0 | Niveles ontológicos completos (ø → ☉) |
| v3.0 | Cerebro Digital Obsidian (PARA + Zettelkasten) |
| **v4.0** | **5 sistemas lógicos + ciclo ⟳ + simbología corregida** |

---

*Sistema Vivo Hexagonal Final v2 — 2026*
*Arquitectura: Hexagonal (Ports & Adapters)*
*Base teórica: Heidegger (Ser y Tiempo) + Husserl + Wolfram*
