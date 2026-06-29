import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Cargar el vector
todos_los_puntos = np.load('todos_los_puntos_evaluados.npy')

print("="*60)
print("VISUALIZADOR DE PUNTOS EVALUADOS")
print("="*60)

print(f"\n📊 Total de puntos: {len(todos_los_puntos)}")
print(f"📊 Dimensiones: {todos_los_puntos.shape}")
print(f"📊 Columnas: [tcss, tfc, valor]")

# Ver todos los puntos
print("\n" + "="*60)
print("LISTA COMPLETA DE PUNTOS:")
print("="*60)
print(f"{'#':<4} {'tcss':>12} {'tfc':>12} {'valor':>15}")
print("-"*60)

for i, punto in enumerate(todos_los_puntos):
    print(f"{i+1:<4} {punto[0]:>12.2f} {punto[1]:>12.2f} {punto[2]:>15.6f}")

# Ordenar por mejor valor (ahora por seguridad = 1 - riesgo)
riesgo = todos_los_puntos[:, 2]
seguridad = 1 - riesgo
ordenados = todos_los_puntos[seguridad.argsort()[::-1]]  # Orden descendente (mayor seguridad primero)

print("\n" + "="*60)
print("TOP 10 MEJORES PUNTOS (más seguros):")
print("="*60)
print(f"{'#':<4} {'tcss':>12} {'tfc':>12} {'riesgo':>15} {'seguridad':>15}")
print("-"*60)

for i in range(min(10, len(ordenados))):
    punto = ordenados[i]
    riesgo_val = punto[2]
    seguridad_val = 1 - riesgo_val
    print(f"{i+1:<4} {punto[0]:>12.2f} {punto[1]:>12.2f} {riesgo_val:>15.6f} {seguridad_val:>15.6f}")

# Guardar como CSV (para Excel)
df = pd.DataFrame(todos_los_puntos, columns=['tcss', 'tfc', 'riesgo'])
df['seguridad'] = 1 - df['riesgo']
df.to_csv('todos_los_puntos.csv', index=False)
print("\n✅ Guardado como CSV: 'todos_los_puntos.csv' (abre con Excel)")

# Guardar como TXT legible
with open('todos_los_puntos_legible.txt', 'w') as f:
    f.write("tcss\ttfc\triesgo\tseguridad\n")
    f.write("="*50 + "\n")
    for punto in todos_los_puntos:
        riesgo_val = punto[2]
        seguridad_val = 1 - riesgo_val
        f.write(f"{punto[0]:.2f}\t{punto[1]:.2f}\t{riesgo_val:.6f}\t{seguridad_val:.6f}\n")
print("✅ Guardado como TXT: 'todos_los_puntos_legible.txt'")

# ==========================================
# GRÁFICA 1: GRÁFICA 3D CON COLORES Y PROYECCIONES
# ==========================================


# Separar datos
tcss = todos_los_puntos[:, 0]
tfc = todos_los_puntos[:, 1]
riesgo = todos_los_puntos[:, 2]
seguridad = 1 - riesgo  # Seguridad = 1 - riesgo

# Identificar puntos especiales
seguridad_alta = seguridad > 0.99  # Seguridad cercana a 1 (riesgo ≈ 0) - VERDES
riesgo_alto = riesgo > 0.99  # Riesgo cercano a 1 (seguridad ≈ 0) - ROJOS
indices_mejores = seguridad.argsort()[-10:]  # Los 10 con mayor seguridad - VERDES BRILLANTES

# Crear filtro para puntos normales (ni riesgo alto ni seguridad alta)
puntos_normales = ~(seguridad_alta | riesgo_alto)

# Crear figura 3D con proyecciones
fig1 = plt.figure(figsize=(14, 12))
ax1 = fig1.add_subplot(111, projection='3d')

# Obtener límites del gráfico
tfc_max_val = tfc.max() * 1.1

# ===== PROYECCIONES: HACIA ABAJO Y LÍNEA ROTADA 90° A LA DERECHA =====
# Para cada punto, dibujar líneas de proyección
for i in range(len(tcss)):
    # Línea perpendicular al plano horizontal (hacia abajo) - desde el punto hasta z=0
    ax1.plot([tcss[i], tcss[i]], [tfc[i], tfc[i]], [0, seguridad[i]], 
             'gray', linestyle=':', linewidth=0.8, alpha=0.3)
    
    # Línea ROTADA 90° A LA DERECHA: va en dirección del eje tfc
    # Desde el punto (tcss, tfc, seguridad) hasta (tcss, tfc_max_val, seguridad)
    # Mantiene tcss y seguridad constantes, varía tfc hacia el límite del gráfico
    ax1.plot([tcss[i], tcss[i]], [tfc[i], tfc_max_val], [seguridad[i], seguridad[i]], 
             'gray', linestyle=':', linewidth=0.8, alpha=0.3)

# Graficar SOLO los puntos normales en azul (excluyendo rojos y verdes especiales)
if np.any(puntos_normales):
    ax1.scatter(tcss[puntos_normales], tfc[puntos_normales], seguridad[puntos_normales], 
                c='blue', s=40, alpha=0.6, label='Puntos normales')

# Graficar puntos con seguridad alta en VERDE
if np.any(seguridad_alta):
    ax1.scatter(tcss[seguridad_alta], tfc[seguridad_alta], seguridad[seguridad_alta], 
                c='green', s=100, marker='^', label='Seguridad alta - VERDE', alpha=0.9, edgecolors='darkgreen', linewidth=1)

# Graficar puntos con riesgo alto en ROJO
if np.any(riesgo_alto):
    ax1.scatter(tcss[riesgo_alto], tfc[riesgo_alto], seguridad[riesgo_alto], 
                c='red', s=100, marker='v', label='Riesgo alto - ROJO', alpha=0.9, edgecolors='darkred', linewidth=1)

# Graficar los 10 más seguros en verde brillante
ax1.scatter(tcss[indices_mejores], tfc[indices_mejores], seguridad[indices_mejores], 
            c='lime', s=150, marker='*', label='10 más seguros', alpha=0.9, edgecolors='darkgreen', linewidth=1)

# Dibujar proyecciones de los puntos especiales con líneas más visibles
# Para los 10 más seguros
for idx in indices_mejores:
    ax1.plot([tcss[idx], tcss[idx]], [tfc[idx], tfc[idx]], [0, seguridad[idx]], 
             'green', linestyle='--', linewidth=2, alpha=0.6)
    ax1.plot([tcss[idx], tcss[idx]], [tfc[idx], tfc_max_val], [seguridad[idx], seguridad[idx]], 
             'green', linestyle='--', linewidth=2, alpha=0.6)

# Para puntos con seguridad alta
if np.any(seguridad_alta):
    indices_seg = np.where(seguridad_alta)[0]
    for idx in indices_seg:
        ax1.plot([tcss[idx], tcss[idx]], [tfc[idx], tfc[idx]], [0, seguridad[idx]], 
                 'green', linestyle='--', linewidth=1.5, alpha=0.5)
        ax1.plot([tcss[idx], tcss[idx]], [tfc[idx], tfc_max_val], [seguridad[idx], seguridad[idx]], 
                 'green', linestyle='--', linewidth=1.5, alpha=0.5)

# Para puntos con riesgo alto - LÍNEAS DISCONTINUAS ROJAS
if np.any(riesgo_alto):
    indices_riesgo = np.where(riesgo_alto)[0]
    for idx in indices_riesgo:
        ax1.plot([tcss[idx], tcss[idx]], [tfc[idx], tfc[idx]], [0, seguridad[idx]], 
                 'red', linestyle='--', linewidth=1.5, alpha=0.5)
        ax1.plot([tcss[idx], tcss[idx]], [tfc[idx], tfc_max_val], [seguridad[idx], seguridad[idx]], 
                 'red', linestyle='--', linewidth=1.5, alpha=0.5)

# Para puntos normales - LÍNEAS DISCONTINUAS AZULES
if np.any(puntos_normales):
    indices_normales = np.where(puntos_normales)[0]
    for idx in indices_normales:
        ax1.plot([tcss[idx], tcss[idx]], [tfc[idx], tfc[idx]], [0, seguridad[idx]], 
                 'blue', linestyle='--', linewidth=1.0, alpha=0.3)
        ax1.plot([tcss[idx], tcss[idx]], [tfc[idx], tfc_max_val], [seguridad[idx], seguridad[idx]], 
                 'blue', linestyle='--', linewidth=1.0, alpha=0.3)

# Dibujar plano horizontal en z=0 (sombra)
tcss_range = np.linspace(tcss.min(), tcss.max(), 10)
tfc_range = np.linspace(tfc.min(), tfc.max(), 10)
Tcss, Tfc = np.meshgrid(tcss_range, tfc_range)
Z_zero = np.zeros_like(Tcss)
ax1.plot_surface(Tcss, Tfc, Z_zero, alpha=0.05, color='gray')

# Dibujar un plano vertical en tfc_max_val para visualizar donde terminan las líneas
tcss_vals = np.linspace(tcss.min(), tcss.max(), 10)
seg_vals = np.linspace(seguridad.min(), seguridad.max(), 10)
Tcss_plane, Seg_plane = np.meshgrid(tcss_vals, seg_vals)
Tfc_max_plane = np.ones_like(Tcss_plane) * tfc_max_val
ax1.plot_surface(Tcss_plane, Tfc_max_plane, Seg_plane, alpha=0.05, color='lightcoral')

# ===== INVERTIR EL EJE TCSS (orden inverso) =====
# Para invertir el eje X (tcss), intercambiamos los límites
ax1.set_xlim([tcss.max(), tcss.min()])
ax1.set_ylim([tfc.min(), tfc_max_val])

# Etiquetas y título
ax1.set_xlabel('tcss (s)', fontsize=12, fontweight='bold')
ax1.set_ylabel('tfc (s)', fontsize=12, fontweight='bold')
ax1.set_zlabel('Seguridad', fontsize=12, fontweight='bold')
ax1.set_title('GRÁFICA 3D CON PROYECCIONES - SEGURIDAD\nVerde: más seguro | Rojo: más riesgo', 
              fontsize=14, fontweight='bold')

# Leyenda en la esquina superior izquierda para evitar solapamiento
ax1.legend(loc='upper left', bbox_to_anchor=(0.02, 0.98), fontsize=10, framealpha=0.9)

# Ajustar vista
ax1.view_init(elev=25, azim=-60)

plt.tight_layout()
plt.savefig('grafica_3d_puntos.png', dpi=300, bbox_inches='tight')


# ==========================================
# GRÁFICA 2: DIAGRAMA DE CONTORNO
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
fig2, ax2 = plt.subplots(figsize=(12, 10))

# Crear el gráfico de contorno (ahora mostrando seguridad)
contour = ax2.contourf(Tcss_grid, Tfc_grid, seguridad_grid, levels=20, 
                       cmap='RdYlGn', alpha=0.7)  # RdYlGn: rojo=menos seguro, verde=más seguro

# Añadir líneas de contorno
contour_lines = ax2.contour(Tcss_grid, Tfc_grid, seguridad_grid, levels=10, 
                            colors='black', linewidths=0.5, alpha=0.3)
ax2.clabel(contour_lines, inline=True, fontsize=8, fmt='%.3f')

# Graficar SOLO los puntos normales en azul (excluyendo rojos y verdes especiales)
if np.any(puntos_normales):
    ax2.scatter(tcss[puntos_normales], tfc[puntos_normales], 
                c='blue', s=20, alpha=0.4, label='Puntos normales')

# Puntos con seguridad alta en VERDE
if np.any(seguridad_alta):
    ax2.scatter(tcss[seguridad_alta], tfc[seguridad_alta], 
                c='green', s=50, marker='^', label='Seguridad alta - VERDE', alpha=0.8, edgecolors='darkgreen')

# Puntos con riesgo alto en ROJO
if np.any(riesgo_alto):
    ax2.scatter(tcss[riesgo_alto], tfc[riesgo_alto], 
                c='red', s=50, marker='v', label='Riesgo alto - ROJO', alpha=0.8, edgecolors='darkred')

# Los 10 más seguros en verde brillante
ax2.scatter(tcss[indices_mejores], tfc[indices_mejores], 
            c='lime', s=100, marker='*', label='10 más seguros', alpha=0.9, edgecolors='darkgreen')

# Etiquetas y título
ax2.set_xlabel('tcss (s)', fontsize=12, fontweight='bold')
ax2.set_ylabel('tfc (s)', fontsize=12, fontweight='bold')
ax2.set_title('DIAGRAMA DE CONTORNO - SEGURIDAD \nVerde: más seguro (cercano a 1) | Rojo: menos seguro (cercano a 0)', 
              fontsize=14, fontweight='bold')

# Añadir barra de color
cbar = plt.colorbar(contour, ax=ax2, label='Seguridad (1 - riesgo)', 
                    orientation='vertical', pad=0.02)
cbar.set_label('Seguridad', fontsize=11, fontweight='bold')

# Leyenda
ax2.legend(loc='upper right', fontsize=10)

# Ajustar límites - el 0 en ambos ejes está abajo a la izquierda
ax2.set_xlim([tcss_min, tcss_max])
ax2.set_ylim([tfc_min, tfc_max])
ax2.grid(True, alpha=0.2, linestyle='--')

plt.tight_layout()
plt.savefig('diagrama_contorno.png', dpi=300, bbox_inches='tight')



# Mostrar estadísticas finales
print("\n" + "="*60)
print("ESTADÍSTICAS DE LAS GRÁFICAS:")
print("="*60)
print(f"Total de puntos graficados: {len(todos_los_puntos)}")
print(f"Rango de tcss: [{tcss.min():.2f}, {tcss.max():.2f}]")
print(f"Rango de tfc: [{tfc.min():.2f}, {tfc.max():.2f}]")
print(f"Rango de riesgo: [{riesgo.min():.6f}, {riesgo.max():.6f}]")
print(f"Rango de seguridad: [{seguridad.min():.6f}, {seguridad.max():.6f}]")


# Mostrar los 10 puntos más seguros
print("\n🏆 10 PUNTOS MÁS SEGUROS ENCONTRADOS:")
print(f"{'#':<4} {'tcss':>12} {'tfc':>12} {'riesgo':>15} {'seguridad':>15}")
print("-"*60)
for i in range(min(10, len(ordenados))):
    punto = ordenados[i]
    riesgo_val = punto[2]
    seguridad_val = 1 - riesgo_val
    print(f"{i+1:<4} {punto[0]:>12.2f} {punto[1]:>12.2f} {riesgo_val:>15.6f} {seguridad_val:>15.6f}")

print("\n" + "="*60)
print("✅ PROCESO COMPLETADO - TODAS LAS GRÁFICAS GUARDADAS")
print("="*60)
print("📊 Archivos generados:")
print("   - grafica_3d_puntos.png (3D mostrando SEGURIDAD = 1 - riesgo)")
print("   - diagrama_contorno.png (Contorno mostrando SEGURIDAD, verde = más seguro, rojo = más riesgo)")
print("   - todos_los_puntos.csv (Datos con riesgo y seguridad)")
print("   - todos_los_puntos_legible.txt (Datos con riesgo y seguridad)")
print("="*60)
