import subprocess
import os
import sys

# ==============================
# RUTAS DE LOS EJECUTABLES
# ==============================
melg = r"C:\MELCOR\MELCOR2.2r2025.0.0\bin\license\melgen_r2025.0.0.exe"
melc = r"C:\MELCOR\MELCOR2.2r2025.0.0\bin\license\melcor_r2025.0.0.exe"

# ==============================
# ARCHIVO DE ENTRADA
# ==============================
inp_file = r"C:\TFM DAVID\SBO\CASO BASE copia\Input_SBO_Mit.INP"
 
# Extraemos directorio y nombre
working_dir = os.path.dirname(inp_file)
inp_name = os.path.basename(inp_file)

# ==============================
# COMPROBACIONES PREVIAS
# ==============================
if not os.path.exists(melg):
    print("ERROR: No se encuentra MELGEN")
    sys.exit(1)

if not os.path.exists(melc):
    print("ERROR: No se encuentra MELCOR")
    sys.exit(1)

if not os.path.exists(inp_file):
    print("ERROR: No se encuentra el archivo .INP")
    sys.exit(1)

# ==============================
# EJECUCIÓN MELGEN
# ==============================
print("\n==============================")
print("Ejecutando MELGEN")
print("==============================")

result_melg = subprocess.run(
    [melg, inp_name],
    cwd=working_dir,
    input="o\n",
    text=True,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

print(f"Código de retorno MELGEN: {result_melg.returncode}")

if result_melg.returncode != 0:
    print("\n❌ ERROR: MELGEN ha fallado.")
    sys.exit(1)

print("✅ MELGEN completado correctamente")

# ==============================
# EJECUCIÓN MELCOR
# ==============================
print("\n==============================")
print("Ejecutando MELCOR")
print("==============================")

result_melc = subprocess.run(
    [melc, inp_name],
    cwd=working_dir,
    input="o\n",
    text=True,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

print(f"Código de retorno MELCOR: {result_melc.returncode}")

if result_melc.returncode != 0:
    print("\n❌ ERROR: MELCOR ha fallado.")
    sys.exit(1)

# ==============================
# FIN
# ==============================
print("\n🎉 Proceso finalizado correctamente")