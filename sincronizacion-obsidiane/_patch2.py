import pathlib, re

p = pathlib.Path('core_new/engines/pipeline_evolucionado.py')
src = p.read_text(encoding='utf-8')

# Agrega generar_moc_relaciones justo después de generar_moc_niveles
old = "            self.obsidian.generar_moc_niveles()"
new = old + "\n            self.obsidian.generar_moc_relaciones()"

if "generar_moc_relaciones" not in src:
    src = src.replace(old, new, 1)
    p.write_text(src, encoding='utf-8')
    print("OK: generar_moc_relaciones() agregado al pipeline")
else:
    print("Ya presente, sin cambios")
