import ast
import pathlib

p1 = pathlib.Path('adapters/outbound/obsidian_sync.py')
p2 = pathlib.Path('core_new/engines/pipeline_evolucionado.py')

results = []

for p in [p1, p2]:
    src = p.read_text(encoding='utf-8')
    try:
        ast.parse(src)
        results.append(f'OK {p.name}')
    except SyntaxError as e:
        results.append(f'ERROR {p.name}: {e}')

src1 = p1.read_text(encoding='utf-8')
metodos = [
    'guardar_axioma', 'guardar_mundo_hipotetico', 'guardar_estado_modal',
    'guardar_estado_deontico', 'guardar_composicion_mereologica',
    'agregar_resignificacion_a_instancia', 'generar_moc_relaciones',
    'generar_moc_pipeline', 'generar_moc_niveles', 'actualizar_estado',
]
for m in metodos:
    estado = 'PRESENTE' if ('def ' + m) in src1 else 'FALTA'
    results.append(f'  [{estado}] {m}')

src2 = p2.read_text(encoding='utf-8')
for campo in ['_sincronizar_logica_extendida', 'generar_moc_relaciones']:
    estado = 'PRESENTE' if campo in src2 else 'FALTA'
    results.append(f'  pipeline [{estado}] {campo}')

for r in results:
    print(r)
