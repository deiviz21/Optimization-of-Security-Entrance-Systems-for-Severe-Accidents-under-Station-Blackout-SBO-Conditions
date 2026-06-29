import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# ==========================================
# FUNCIÓN PARA LEER EL ARCHIVO DE TEXTO
# ==========================================
def leer_archivo_txt(nombre_archivo):
    """
    Lee el archivo de texto con el formato específico:
    #   |   TCSS   |   TFC    |  CAUDAL  |   VALOR   
    """
    datos = []
    
    with open(nombre_archivo, 'r', encoding='utf-8') as f:
        lineas = f.readlines()
        
        # Buscar dónde comienzan los datos (línea con números)
        for i, linea in enumerate(lineas):
            # Saltar líneas vacías y líneas de encabezado/separadores
            if not linea.strip() or linea.startswith('=') or linea.startswith('--') or linea.startswith('  #'):
                continue
            
            # Intentar parsear la línea
            try:
                # Dividir por '|' y limpiar espacios
                partes = [p.strip() for p in linea.split('|')]
                
                # Filtrar partes vacías
                partes = [p for p in partes if p]
                
                # Verificar que tenemos al menos 5 valores (incluyendo el número de punto)
                if len(partes) >= 5:
                    # El formato es: # | TCSS | TFC | CAUDAL | VALOR
                    # partes[0] = número de punto, partes[1] = TCSS, partes[2] = TFC, 
                    # partes[3] = CAUDAL, partes[4] = VALOR
                    tcss = float(partes[1].replace(',', '').strip())
                    tfc = float(partes[2].replace(',', '').strip())
                    caudal = float(partes[3].replace(',', '').strip())
                    valor = float(partes[4].replace(',', '').strip())
                    
                    datos.append([tcss, tfc, caudal, valor])
            except (ValueError, IndexError) as e:
                # Si falla el parseo, continuar con la siguiente línea
                continue
    
    return np.array(datos, dtype=float)

# Cargar datos desde el archivo de texto
print("="*60)
print("VISUALIZADOR DE PUNTOS EVALUADOS (CON CAUDAL)")
print("="*60)
print("\n📂 Leyendo archivo: todos_los_puntos_completos.txt")

try:
    todos_los_puntos = leer_archivo_txt('todos_los_puntos_completos.txt')
    
    if len(todos_los_puntos) == 0:
        print("❌ No se encontraron datos en el archivo.")
        print("🔍 Verificando el contenido del archivo...")
        
        # Imprimir las primeras líneas del archivo para depuración
        with open('todos_los_puntos_completos.txt', 'r', encoding='utf-8') as f:
            lineas = f.readlines()
            print("\nPrimeras 10 líneas del archivo:")
            for i, linea in enumerate(lineas[:10]):
                print(f"  Línea {i+1}: {repr(linea)}")
        exit()
        
    print(f"✅ Datos cargados exitosamente!")
except FileNotFoundError:
    print("❌ Archivo no encontrado. Verifica el nombre y la ubicación.")
    print("   El archivo debe llamarse 'todos_los_puntos_completos.txt'")
    print("   y estar en la misma carpeta que este script.")
    exit()

print(f"\n📊 Total de puntos: {len(todos_los_puntos)}")
print(f"📊 Dimensiones: {todos_los_puntos.shape}")
print(f"📊 Columnas: [tcss, tfc, caudal, valor]")

# Verificar que tenemos datos
if len(todos_los_puntos) == 0:
    print("❌ No se pudieron leer los datos del archivo.")
    exit()

# ==========================================
# SEPARAR DATOS (AHORA CON 4 COLUMNAS)
# ==========================================
tcss = todos_los_puntos[:, 0]
tfc = todos_los_puntos[:, 1]
caudal = todos_los_puntos[:, 2]  # <--- NUEVA COLUMNA
riesgo = todos_los_puntos[:, 3]   # <--- AHORA ES LA COLUMNA 3
seguridad = 1 - riesgo  # Seguridad = 1 - riesgo

# Ver todos los puntos
print("\n" + "="*60)
print("LISTA COMPLETA DE PUNTOS:")
print("="*60)
print(f"{'#':<4} {'TCSS':>12} {'TFC':>12} {'CAUDAL':>12} {'RIESGO':>15} {'SEGURIDAD':>15}")
print("-"*80)

for i, punto in enumerate(todos_los_puntos):
    riesgo_val = punto[3]
    seguridad_val = 1 - riesgo_val
    print(f"{i+1:<4} {punto[0]:>12.2f} {punto[1]:>12.2f} {punto[2]:>12.2f} {riesgo_val:>15.6f} {seguridad_val:>15.6f}")

# Ordenar por mejor valor (seguridad = 1 - riesgo)
ordenados = todos_los_puntos[seguridad.argsort()[::-1]]  # Orden descendente (mayor seguridad primero)

print("\n" + "="*60)
print("🏆 TOP 10 MEJORES PUNTOS (más seguros):")
print("="*60)
print(f"{'#':<4} {'TCSS':>12} {'TFC':>12} {'CAUDAL':>12} {'RIESGO':>15} {'SEGURIDAD':>15}")
print("-"*80)

for i in range(min(10, len(ordenados))):
    punto = ordenados[i]
    riesgo_val = punto[3]
    seguridad_val = 1 - riesgo_val
    print(f"{i+1:<4} {punto[0]:>12.2f} {punto[1]:>12.2f} {punto[2]:>12.2f} {riesgo_val:>15.6f} {seguridad_val:>15.6f}")

# Guardar como CSV (para Excel) - AHORA CON CAUDAL
df = pd.DataFrame(todos_los_puntos, columns=['tcss', 'tfc', 'caudal', 'riesgo'])
df['seguridad'] = 1 - df['riesgo']
df.to_csv('todos_los_puntos.csv', index=False)
print("\n✅ Guardado como CSV: 'todos_los_puntos.csv' (abre con Excel)")

# Guardar como TXT legible - AHORA CON CAUDAL
with open('todos_los_puntos_legible.txt', 'w') as f:
    f.write("tcss\ttfc\tcaudal\triesgo\tseguridad\n")
    f.write("="*60 + "\n")
    for punto in todos_los_puntos:
        riesgo_val = punto[3]
        seguridad_val = 1 - riesgo_val
        f.write(f"{punto[0]:.2f}\t{punto[1]:.2f}\t{punto[2]:.2f}\t{riesgo_val:.6f}\t{seguridad_val:.6f}\n")
print("✅ Guardado como TXT: 'todos_los_puntos_legible.txt'")

# ==========================================
# GRÁFICA 1: RELACIÓN CAUDAL VS TCSS CON DEGRADADO DE SEGURIDAD
# ==========================================

# Identificar puntos especiales
seguridad_alta = seguridad > 0.99  # Seguridad cercana a 1 (riesgo ≈ 0) - VERDES
riesgo_alto = riesgo > 0.99  # Riesgo cercano a 1 (seguridad ≈ 0) - ROJOS
indices_mejores = seguridad.argsort()[-10:]  # Los 10 con mayor seguridad - VERDES BRILLANTES

# Crear filtro para puntos normales (ni riesgo alto ni seguridad alta)
puntos_normales = ~(seguridad_alta | riesgo_alto)

# Figura 1: Caudal vs TCSS con degradado de colores según seguridad
fig1, ax1 = plt.subplots(figsize=(12, 8))

# Scatter plot de caudal vs tcss con degradado de colores
scatter = ax1.scatter(caudal, tcss, c=seguridad, cmap='RdYlGn', 
                     s=80, alpha=0.7, edgecolors='black', linewidth=0.5)

# Destacar los 10 mejores
ax1.scatter(caudal[indices_mejores], tcss[indices_mejores], 
           c='lime', s=200, marker='*', label='10 más seguros', 
           alpha=0.9, edgecolors='darkgreen', linewidth=2)

# Etiquetas y título
ax1.set_xlabel('CAUDAL', fontsize=12, fontweight='bold')
ax1.set_ylabel('TCSS (s)', fontsize=12, fontweight='bold')
ax1.set_title('RELACIÓN CAUDAL VS TCSS\nColor = Seguridad (verde: alta, rojo: baja)', 
              fontsize=14, fontweight='bold')

# Barra de color
cbar = plt.colorbar(scatter, ax=ax1, label='Seguridad')
cbar.set_label('Seguridad', fontsize=11, fontweight='bold')

ax1.grid(True, alpha=0.3, linestyle='--')
ax1.legend(loc='best')

plt.tight_layout()
plt.savefig('grafica_caudal_vs_tcss.png', dpi=300, bbox_inches='tight')

# ==========================================
# GRÁFICA 2: 3D CON TCSS, TFC, CAUDAL - EJE TCSS INVERTIDO
# ==========================================

fig2 = plt.figure(figsize=(14, 12))
ax2 = fig2.add_subplot(111, projection='3d')

# Graficar puntos con colores según seguridad
scatter2 = ax2.scatter(tcss, tfc, caudal, c=seguridad, cmap='RdYlGn', 
                       s=60, alpha=0.6, edgecolors='black', linewidth=0.5)

# Destacar los 10 mejores
ax2.scatter(tcss[indices_mejores], tfc[indices_mejores], caudal[indices_mejores], 
           c='lime', s=200, marker='*', label='10 más seguros', 
           alpha=0.9, edgecolors='darkgreen', linewidth=2)

# INVERTIR EL EJE TCSS (orden inverso) - el 0 de TCSS y TFC convergen en la misma esquina
ax2.set_xlim([tcss.max(), tcss.min()])  # Invertido: de mayor a menor
ax2.set_ylim([tfc.min(), tfc.max()])

# Etiquetas y título
ax2.set_xlabel('TCSS (s)', fontsize=12, fontweight='bold')
ax2.set_ylabel('TFC (s)', fontsize=12, fontweight='bold')
ax2.set_zlabel('CAUDAL', fontsize=12, fontweight='bold')
ax2.set_title('RELACIÓN 3D: TCSS, TFC, CAUDAL\nColor = Seguridad (verde: alta, rojo: baja) - TCSS invertido', 
              fontsize=14, fontweight='bold')

# Barra de color
cbar2 = plt.colorbar(scatter2, ax=ax2, label='Seguridad', pad=0.1)
cbar2.set_label('Seguridad', fontsize=11, fontweight='bold')

ax2.legend(loc='upper left', fontsize=10)
ax2.view_init(elev=25, azim=-60)

plt.tight_layout()
plt.savefig('grafica_3d_tcss_tfc_caudal.png', dpi=300, bbox_inches='tight')

# ==========================================
# GRÁFICA 3: DIAGRAMA DE CONTORNO DE SEGURIDAD (EJE SIN INVERTIR)
# ==========================================

# Determinar límites para la malla
tcss_min, tcss_max = tcss.min(), tcss.max()
tfc_min, tfc_max = tfc.min(), tfc.max()

# Añadir un margen del 10%
tcss_range = tcss_max - tcss_min
tfc_range = tfc_max - tfc_min
tcss_min -= tcss_range * 0.1
tcss_max += tcss_range * 0.1
tfc_min -= tfc_range * 0.1
tfc_max += tfc_range * 0.1

# Crear malla para el contorno
grid_resolution = 30
tcss_grid = np.linspace(tcss_min, tcss_max, grid_resolution)
tfc_grid = np.linspace(tfc_min, tfc_max, grid_resolution)
Tcss_grid, Tfc_grid = np.meshgrid(tcss_grid, tfc_grid)

# Interpolar usando vecino más cercano (ahora interpolamos la seguridad)
seguridad_grid = np.zeros_like(Tcss_grid)
for i in range(grid_resolution):
    for j in range(grid_resolution):
        distancias = np.sqrt((tcss - Tcss_grid[i,j])**2 + (tfc - Tfc_grid[i,j])**2)
        idx_cercano = np.argmin(distancias)
        seguridad_grid[i,j] = seguridad[idx_cercano]

# Crear figura para el contorno
fig3, ax3 = plt.subplots(figsize=(12, 10))

# Crear el gráfico de contorno (ahora mostrando seguridad)
contour = ax3.contourf(Tcss_grid, Tfc_grid, seguridad_grid, levels=20, 
                       cmap='RdYlGn', alpha=0.7)  # RdYlGn: rojo=menos seguro, verde=más seguro

# Añadir líneas de contorno
contour_lines = ax3.contour(Tcss_grid, Tfc_grid, seguridad_grid, levels=10, 
                            colors='black', linewidths=0.5, alpha=0.3)
ax3.clabel(contour_lines, inline=True, fontsize=8, fmt='%.3f')

# Graficar SOLO los puntos normales en azul (excluyendo rojos y verdes especiales)
if np.any(puntos_normales):
    ax3.scatter(tcss[puntos_normales], tfc[puntos_normales], 
                c='blue', s=20, alpha=0.4, label='Puntos normales')

# Puntos con seguridad alta en VERDE
if np.any(seguridad_alta):
    ax3.scatter(tcss[seguridad_alta], tfc[seguridad_alta], 
                c='green', s=50, marker='^', label='Seguridad alta - VERDE', alpha=0.8, edgecolors='darkgreen')

# Puntos con riesgo alto en ROJO
if np.any(riesgo_alto):
    ax3.scatter(tcss[riesgo_alto], tfc[riesgo_alto], 
                c='red', s=50, marker='v', label='Riesgo alto - ROJO', alpha=0.8, edgecolors='darkred')

# Los 10 más seguros en verde brillante
ax3.scatter(tcss[indices_mejores], tfc[indices_mejores], 
            c='lime', s=100, marker='*', label='10 más seguros', alpha=0.9, edgecolors='darkgreen')

# EJE TCSS EN ORDEN NORMAL (sin invertir)
ax3.set_xlim([tcss_min, tcss_max])
ax3.set_ylim([tfc_min, tfc_max])

# Etiquetas y título
ax3.set_xlabel('TCSS (s)', fontsize=12, fontweight='bold')
ax3.set_ylabel('TFC (s)', fontsize=12, fontweight='bold')
ax3.set_title('DIAGRAMA DE CONTORNO - SEGURIDAD\nVerde: más seguro (cercano a 1) | Rojo: menos seguro (cercano a 0)', 
              fontsize=14, fontweight='bold')

# Añadir barra de color
cbar3 = plt.colorbar(contour, ax=ax3, label='Seguridad (1 - riesgo)', 
                    orientation='vertical', pad=0.02)
cbar3.set_label('Seguridad', fontsize=11, fontweight='bold')

# Leyenda
ax3.legend(loc='upper right', fontsize=10)

ax3.grid(True, alpha=0.2, linestyle='--')

plt.tight_layout()
plt.savefig('diagrama_contorno.png', dpi=300, bbox_inches='tight')

# ==========================================
# ESTADÍSTICAS FINALES
# ==========================================

print("\n" + "="*60)
print("ESTADÍSTICAS DE LAS GRÁFICAS:")
print("="*60)
print(f"Total de puntos graficados: {len(todos_los_puntos)}")
print(f"Rango de TCSS: [{tcss.min():.2f}, {tcss.max():.2f}]")
print(f"Rango de TFC: [{tfc.min():.2f}, {tfc.max():.2f}]")
print(f"Rango de CAUDAL: [{caudal.min():.2f}, {caudal.max():.2f}]")
print(f"Rango de riesgo: [{riesgo.min():.6f}, {riesgo.max():.6f}]")
print(f"Rango de seguridad: [{seguridad.min():.6f}, {seguridad.max():.6f}]")

# Mostrar el mejor punto
idx_mejor = np.argmax(seguridad)
print(f"\n🌟 MEJOR PUNTO ENCONTRADO:")
print(f"   TCSS    = {tcss[idx_mejor]:.2f}")
print(f"   TFC     = {tfc[idx_mejor]:.2f}")
print(f"   CAUDAL  = {caudal[idx_mejor]:.2f}")
print(f"   RIESGO  = {riesgo[idx_mejor]:.6f}")
print(f"   SEGURIDAD = {seguridad[idx_mejor]:.6f}")

# Mostrar los 10 puntos más seguros
print("\n🏆 10 PUNTOS MÁS SEGUROS ENCONTRADOS:")
print(f"{'#':<4} {'TCSS':>12} {'TFC':>12} {'CAUDAL':>12} {'RIESGO':>15} {'SEGURIDAD':>15}")
print("-"*80)
for i in range(min(10, len(ordenados))):
    punto = ordenados[i]
    riesgo_val = punto[3]
    seguridad_val = 1 - riesgo_val
    print(f"{i+1:<4} {punto[0]:>12.2f} {punto[1]:>12.2f} {punto[2]:>12.2f} {riesgo_val:>15.6f} {seguridad_val:>15.6f}")

print("\n" + "="*60)
print("✅ PROCESO COMPLETADO - TODAS LAS GRÁFICAS GUARDADAS")
print("="*60)
print("📊 Archivos generados:")
print("   1. todos_los_puntos.csv (Datos con riesgo y seguridad - abrir con Excel)")
print("   2. todos_los_puntos_legible.txt (Datos con riesgo y seguridad - texto)")
print("   3. grafica_caudal_vs_tcss.png (Caudal vs TCSS con degradado de seguridad)")
print("   4. grafica_3d_tcss_tfc_caudal.png (3D: TCSS, TFC, CAUDAL - TCSS invertido)")
print("   5. diagrama_contorno.png (Contorno de seguridad - TCSS normal)")
print("="*60)

# Mostrar gráficas
plt.show()