import numpy as np
import sys
import subprocess

# ==========================================
# 1. FUNCIÓN DE HIPERCUBO LATINO
# ==========================================
def generar_hipercubo_latino(dim, n_particiones, a, b):
    """Genera muestras de Hipercubo Latino."""
    permutaciones = np.array([np.random.permutation(n_particiones) for _ in range(dim)]).T
    posiciones_aleatorias = np.random.random((n_particiones, dim))
    hipercubo = a + (b - a) * (permutaciones + posiciones_aleatorias) / n_particiones
    return hipercubo

# ==========================================
# 2. FUNCIÓN DE NELDER-MEAD (SIMPLEX)
# ==========================================
def nelder_mead(x0, alpha=1.0, gamma=2.0, rho=0.5, sigma=0.5, tol=1e-6, max_iter=1000):
    """Implementación del método de Nelder-Mead (Simplex)."""
    n = len(x0)
    simplex = [np.array(x0)]
    for i in range(n):
        point = np.array(x0)
        point[i] += 7200
        simplex.append(point)
    simplex = np.array(simplex)
    
    # 🔄 CAMBIO: vector ahora tendrá 3 columnas [tcss, tfc, valor_objetivo]
    vector = []  # Lista para acumular resultados
    
    # Obtener límites globales para clamp
    bounds_global = [(float('inf'), float('inf'))] * n  # Por defecto sin límites
    
    # 🔄 NUEVA: Función auxiliar para evaluar puntos
    def evaluar_punto(tcss, tfc):
        """Ejecuta simulación y devuelve valor objetivo"""
        resultado_mod = subprocess.run(
            ["python", r"C:\Users\e6211\Programas David\mod_txt.py", 
             str(tcss), str(tfc)],
            capture_output=True,
            text=True
        )
        
        if resultado_mod.returncode != 0:
            print(f" Error en mod_txt: {resultado_mod.stderr}")
            return 1e10  # Valor alto si hay error
        
        # Corremos el programa de Melgen y Melcor (comentado por ahora)
        subprocess.run(["python", r"C:\Users\e6211\Programas David\Melg_Melc.py"])
        
        # Leer resultados
        resultado_val = subprocess.run(
            ["python", r"C:\Users\e6211\Programas David\val_max_txt.py"],
            capture_output=True,
            text=True
        )
        
        try:
            return float(resultado_val.stdout.strip())
        except:
            print(f" Error al leer valor: {resultado_val.stdout}")
            return 1e10

    # Evaluar puntos iniciales del simplex
    for i, punto in enumerate(simplex):
        tcss = max(0, punto[0])  # 🔧 CLAMP: Evitar negativos
        tfc = max(0, punto[1])   # 🔧 CLAMP: Evitar negativos
        
        # Evaluar el punto con la simulación
        valor_objetivo = evaluar_punto(tcss, tfc)
        
        #  CAMBIO: Guardar [tcss, tfc, valor_objetivo]
        vector.append([tcss, tfc, valor_objetivo])
        print(f"Punto {i}: tcss={tcss}, tfc={tfc} -> Valor={valor_objetivo}")
    
    # Convertir a numpy array
    vector = np.array(vector)
    
    # Bucle principal de Nelder-Mead
    for iteration in range(max_iter):
        #  CAMBIO: f_values es la columna de valores objetivo (columna 2)
        f_values = vector[:, 2]
        indices = np.argsort(f_values)
        
        # 🔄 CAMBIO: puntos son las coordenadas (columnas 0 y 1)
        puntos = vector[:, :2][indices]
        f_values = f_values[indices]
        
        print("\n----------------------------------")
        print(f"Iteración {iteration}")

        print(f"MEJOR   -> x = {puntos[0]} | f = {f_values[0]}")
        print(f"MEDIO   -> x = {puntos[1]} | f = {f_values[1]}")
        print(f"PEOR    -> x = {puntos[-1]} | f = {f_values[-1]}")
        print("----------------------------------")
        
        x_best = puntos[0]
        f_best = f_values[0]
        x_worst = puntos[-1]
        f_worst = f_values[-1]
        x_second_worst = puntos[-2]
        f_second_worst = f_values[-2]
        
        centroid = np.mean(puntos[:-1], axis=0)
        
        x_reflect = centroid + alpha * (centroid - x_worst)
        # 🔧 CLAMP: Evitar negativos en reflexión
        x_reflect = np.maximum(x_reflect, 0)
        f_reflect = evaluar_punto(x_reflect[0], x_reflect[1])
        
        if f_reflect < f_best:
            x_expand = centroid + gamma * (x_reflect - centroid)
            # 🔧 CLAMP: Evitar negativos en expansión
            x_expand = np.maximum(x_expand, 0)
            f_expand = evaluar_punto(x_expand[0], x_expand[1])
            if f_expand < f_reflect:
                puntos[-1] = x_expand
                f_values[-1] = f_expand
            else:
                puntos[-1] = x_reflect
                f_values[-1] = f_reflect
        elif f_reflect < f_second_worst:
            puntos[-1] = x_reflect
            f_values[-1] = f_reflect
        else:
            if f_reflect < f_worst:
                x_contract = centroid + rho * (x_reflect - centroid)
            else:
                x_contract = centroid + rho * (x_worst - centroid)
            # 🔧 CLAMP: Evitar negativos en contracción
            x_contract = np.maximum(x_contract, 0)
            f_contract = evaluar_punto(x_contract[0], x_contract[1])
            if f_contract < f_worst:
                puntos[-1] = x_contract
                f_values[-1] = f_contract
            else:
                for i in range(1, n+1):
                    puntos[i] = x_best + sigma * (puntos[i] - x_best)
                    # 🔧 CLAMP: Evitar negativos en reducción
                    puntos[i] = np.maximum(puntos[i], 0)
                    f_values[i] = evaluar_punto(puntos[i][0], puntos[i][1])
        
        # 🔄 CAMBIO: Actualizar vector con nuevos valores
        vector = np.column_stack([puntos, f_values])
        
        if np.std(f_values) < tol:
            break
    
    x_opt = puntos[0]
    f_opt = f_values[0]
    return x_opt, f_opt, iteration + 1

# ==========================================
# 3. INTERFAZ PRINCIPAL
# ==========================================
print("="*60)
print("OPTIMIZADOR GLOBAL - HIPERCUBO LATINO + SIMPLEX")
print("="*60)

# Número de variables
while True:
    try:
        n_variables = int(input("\n¿Cuántas variables tiene tu función? (ej. 2, 3, 4): "))
        if n_variables <= 0:
            print("Error: Debe ser un número positivo.")
            continue
        break
    except ValueError:
        print("Error: Por favor, introduce un número entero.")

# Límites de la región
print("\nDefine los límites de búsqueda para cada variable:")
bounds = []
for i in range(n_variables):
    while True:
        try:
            min_val = float(input(f"  Límite mínimo para x{i+1}: "))
            max_val = float(input(f"  Límite máximo para x{i+1}: "))
            if min_val >= max_val:
                print("Error: El mínimo debe ser menor que el máximo.")
                continue
            bounds.append((min_val, max_val))
            break
        except ValueError:
            print("Error: Por favor, introduce números válidos.")

# Cantidad de puntos iniciales
while True:
    try:
        n_puntos = int(input("\n¿Cuántos puntos iniciales generar con Hipercubo Latino? (ej. 50, 100): "))
        if n_puntos <= 0:
            print("Error: Debe ser un número positivo.")
            continue
        break
    except ValueError:
        print("Error: Por favor, introduce un número entero.")

# Criterios de convergencia del Simplex
while True:
    try:
        tol = float(input("\nTolerancia para la convergencia (tol) (ej. 1e-6): "))
        if tol <= 0:
            print("Error: La tolerancia debe ser positiva.")
            continue
        break
    except ValueError:
        print("Error: Por favor, introduce un número válido.")

# ==========================================
# 4. GENERAR PUNTOS (HIPERCUBO)
# ==========================================
print("\n" + "="*60)
print("GENERANDO PUNTOS INICIALES")
print("="*60)

dim = n_variables
n_particiones = n_puntos

# 🔧 CLAMP: Usar límites reales de cada dimensión y evitar negativos
puntos_iniciales = generar_hipercubo_latino(dim=dim, n_particiones=n_particiones, 
                                          a=np.array([max(0, bounds[i][0]) for i in range(dim)]),
                                          b=np.array([bounds[i][1] for i in range(dim)]))

# 🔧 CLAMP adicional: asegurar que todos los puntos estén en límites
for i in range(len(puntos_iniciales)):
    for j in range(dim):
        puntos_iniciales[i,j] = np.clip(puntos_iniciales[i,j], 
                                       max(0, bounds[j][0]), 
                                       bounds[j][1])

if puntos_iniciales is None:
    print("Error al generar puntos. Abortando.")
    sys.exit(1)

print(f"\n✓ Se generaron {len(puntos_iniciales)} puntos iniciales.")

# ==========================================
# 5. OPTIMIZACIÓN (SIMPLEX)
# ==========================================
print("\n" + "="*60)
print("INICIANDO BÚSQUEDA SIMPLEX DESDE CADA PUNTO")
print("="*60)

mejor_minimo_global = None
mejor_valor_global = float('inf')
total_puntos = len(puntos_iniciales)

for i, punto in enumerate(puntos_iniciales):
    try:
        # 🔧 CLAMP punto inicial
        punto_clamp = np.maximum(punto, 0)
        x_opt, f_opt, iters = nelder_mead(punto_clamp, tol=tol)
        
        if f_opt < mejor_valor_global:
            mejor_valor_global = f_opt
            mejor_minimo_global = x_opt
            print(f"[{i+1}/{total_puntos}] Valor = {f_opt:.6f} -> Nuevo Mejor Global")
        else:
            print(f"[{i+1}/{total_puntos}] Valor = {f_opt:.6f} (Ignorado)")
            
    except Exception as e:
        print(f"[{i+1}/{total_puntos}] Error en punto: {e}")

# ==========================================
# 6. RESULTADO FINAL
# ==========================================
print("\n" + "="*60)
print("RESULTADO FINAL")
print("="*60)
if mejor_minimo_global is not None:
    print(f"Coordenadas del Mínimo Global: {mejor_minimo_global}")
    print(f"Valor de la Función en el Mínimo: {mejor_valor_global}")
    print(f"Se probaron {total_puntos} puntos iniciales.")
else:
    print("No se encontró ningún mínimo válido.")

print("\n" + "="*60)
print("FIN DEL PROCESO")
print("="*60)

#-----------------------------------------------------------------------------------------------------2

# import numpy as np
# import sys
# import subprocess

# # ==========================================
# # 1. FUNCIÓN DE HIPERCUBO LATINO
# # ==========================================
# def generar_hipercubo_latino(dim, n_particiones, a, b):
#     """Genera muestras de Hipercubo Latino."""
#     permutaciones = np.array([np.random.permutation(n_particiones) for _ in range(dim)]).T
#     posiciones_aleatorias = np.random.random((n_particiones, dim))
#     hipercubo = a + (b - a) * (permutaciones + posiciones_aleatorias) / n_particiones
#     return hipercubo

# # ==========================================
# # 2. FUNCIÓN DE NELDER-MEAD (SIMPLEX)
# # ==========================================
# def nelder_mead(x0, alpha=1.0, gamma=2.0, rho=0.5, sigma=0.5, tol=1e-6, max_iter=1000):
#     """Implementación del método de Nelder-Mead (Simplex)."""
#     n = len(x0)
#     simplex = [np.array(x0)]
#     for i in range(n):
#         point = np.array(x0)
#         point[i] += 32400
#         simplex.append(point)
#     simplex = np.array(simplex)
    
#     # 🔄 CAMBIO: vector ahora tendrá 3 columnas [tcss, tfc, valor_objetivo]
#     vector = []  # Lista para acumular resultados
    
#     # 🔄 NUEVA: Función auxiliar para evaluar puntos
#     def evaluar_punto(tcss, tfc):
#         """Ejecuta simulación y devuelve valor objetivo"""
#         resultado_mod = subprocess.run(
#             ["python", r"C:\Users\e6211\Programas David\mod_txt.py", 
#              str(tcss), str(tfc)],
#             capture_output=True,
#             text=True
#         )
        
#         if resultado_mod.returncode != 0:
#             print(f" Error en mod_txt: {resultado_mod.stderr}")
#             return 1e10  # Valor alto si hay error
        
#         # Corremos el programa de Melgen y Melcor (comentado por ahora)
#         subprocess.run(["python", r"C:\Users\e6211\Programas David\Melg_Melc.py"])
        
#         # Leer resultados
#         resultado_val = subprocess.run(
#             ["python", r"C:\Users\e6211\Programas David\val_max_txt.py"],
#             capture_output=True,
#             text=True
#         )
        
#         try:
#             return float(resultado_val.stdout.strip())
#         except:
#             print(f" Error al leer valor: {resultado_val.stdout}")
#             return 1e10

#     # Evaluar puntos iniciales del simplex
#     for i, punto in enumerate(simplex):
#         tcss = punto[0]
#         tfc = punto[1]
        
#         # Evaluar el punto con la simulación
#         valor_objetivo = evaluar_punto(tcss, tfc)
        
#         #  CAMBIO: Guardar [tcss, tfc, valor_objetivo]
#         vector.append([tcss, tfc, valor_objetivo])
#         print(f"Punto {i}: tcss={tcss}, tfc={tfc} -> Valor={valor_objetivo}")
    
#     # Convertir a numpy array
#     vector = np.array(vector)
    
#     # Bucle principal de Nelder-Mead
#     for iteration in range(max_iter):
#         #  CAMBIO: f_values es la columna de valores objetivo (columna 2)
#         f_values = vector[:, 2]
#         indices = np.argsort(f_values)
        
#         # 🔄 CAMBIO: puntos son las coordenadas (columnas 0 y 1)
#         puntos = vector[:, :2][indices]
#         f_values = f_values[indices]
        
#         print("\n----------------------------------")
#         print(f"Iteración {iteration}")

#         print(f"MEJOR   -> x = {puntos[0]} | f = {f_values[0]}")
#         print(f"MEDIO   -> x = {puntos[1]} | f = {f_values[1]}")
#         print(f"PEOR    -> x = {puntos[-1]} | f = {f_values[-1]}")
#         print("----------------------------------")
        
#         x_best = puntos[0]
#         f_best = f_values[0]
#         x_worst = puntos[-1]
#         f_worst = f_values[-1]
#         x_second_worst = puntos[-2]
#         f_second_worst = f_values[-2]
        
#         centroid = np.mean(puntos[:-1], axis=0)
        
#         x_reflect = centroid + alpha * (centroid - x_worst)
#         # 🔄 CAMBIO: Usar evaluar_punto en lugar de func()
#         f_reflect = evaluar_punto(x_reflect[0], x_reflect[1])
        
#         if f_reflect < f_best:
#             x_expand = centroid + gamma * (x_reflect - centroid)
#             f_expand = evaluar_punto(x_expand[0], x_expand[1])
#             if f_expand < f_reflect:
#                 puntos[-1] = x_expand
#                 f_values[-1] = f_expand
#             else:
#                 puntos[-1] = x_reflect
#                 f_values[-1] = f_reflect
#         elif f_reflect < f_second_worst:
#             puntos[-1] = x_reflect
#             f_values[-1] = f_reflect
#         else:
#             if f_reflect < f_worst:
#                 x_contract = centroid + rho * (x_reflect - centroid)
#             else:
#                 x_contract = centroid + rho * (x_worst - centroid)
#             f_contract = evaluar_punto(x_contract[0], x_contract[1])
#             if f_contract < f_worst:
#                 puntos[-1] = x_contract
#                 f_values[-1] = f_contract
#             else:
#                 for i in range(1, n+1):
#                     puntos[i] = x_best + sigma * (puntos[i] - x_best)
#                     f_values[i] = evaluar_punto(puntos[i][0], puntos[i][1])
        
#         # 🔄 CAMBIO: Actualizar vector con nuevos valores
#         vector = np.column_stack([puntos, f_values])
        
#         if np.std(f_values) < tol:
#             break
    
#     x_opt = puntos[0]
#     f_opt = f_values[0]
#     return x_opt, f_opt, iteration + 1

# # ==========================================
# # 3. INTERFAZ PRINCIPAL
# # ==========================================
# print("="*60)
# print("OPTIMIZADOR GLOBAL - HIPERCUBO LATINO + SIMPLEX")
# print("="*60)

# # Número de variables
# while True:
#     try:
#         n_variables = int(input("\n¿Cuántas variables tiene tu función? (ej. 2, 3, 4): "))
#         if n_variables <= 0:
#             print("Error: Debe ser un número positivo.")
#             continue
#         break
#     except ValueError:
#         print("Error: Por favor, introduce un número entero.")

# # Límites de la región
# print("\nDefine los límites de búsqueda para cada variable:")
# bounds = []
# for i in range(n_variables):
#     while True:
#         try:
#             min_val = float(input(f"  Límite mínimo para x{i+1}: "))
#             max_val = float(input(f"  Límite máximo para x{i+1}: "))
#             if min_val >= max_val:
#                 print("Error: El mínimo debe ser menor que el máximo.")
#                 continue
#             bounds.append((min_val, max_val))
#             break
#         except ValueError:
#             print("Error: Por favor, introduce números válidos.")

# # Cantidad de puntos iniciales
# while True:
#     try:
#         n_puntos = int(input("\n¿Cuántos puntos iniciales generar con Hipercubo Latino? (ej. 50, 100): "))
#         if n_puntos <= 0:
#             print("Error: Debe ser un número positivo.")
#             continue
#         break
#     except ValueError:
#         print("Error: Por favor, introduce un número entero.")

# # Criterios de convergencia del Simplex
# while True:
#     try:
#         tol = float(input("\nTolerancia para la convergencia (tol) (ej. 1e-6): "))
#         if tol <= 0:
#             print("Error: La tolerancia debe ser positiva.")
#             continue
#         break
#     except ValueError:
#         print("Error: Por favor, introduce un número válido.")

# # ==========================================
# # 4. GENERAR PUNTOS (HIPERCUBO)
# # ==========================================
# print("\n" + "="*60)
# print("GENERANDO PUNTOS INICIALES")
# print("="*60)

# dim = n_variables
# n_particiones = n_puntos
# a = bounds[0][0]
# b = bounds[0][1]

# puntos_iniciales = generar_hipercubo_latino(dim=dim, n_particiones=n_particiones, a=a, b=b)

# if puntos_iniciales is None:
#     print("Error al generar puntos. Abortando.")
#     sys.exit(1)

# print(f"\n✓ Se generaron {len(puntos_iniciales)} puntos iniciales.")

# # ==========================================
# # 5. OPTIMIZACIÓN (SIMPLEX)
# # ==========================================
# print("\n" + "="*60)
# print("INICIANDO BÚSQUEDA SIMPLEX DESDE CADA PUNTO")
# print("="*60)

# mejor_minimo_global = None
# mejor_valor_global = float('inf')
# total_puntos = len(puntos_iniciales)

# for i, punto in enumerate(puntos_iniciales):
#     try:
#         # 🔄 CAMBIO: Ya no se pasa funcion_objetivo
#         x_opt, f_opt, iters = nelder_mead(punto, tol=tol)
        
#         if f_opt < mejor_valor_global:
#             mejor_valor_global = f_opt
#             mejor_minimo_global = x_opt
#             print(f"[{i+1}/{total_puntos}] Valor = {f_opt:.6f} -> Nuevo Mejor Global")
#         else:
#             print(f"[{i+1}/{total_puntos}] Valor = {f_opt:.6f} (Ignorado)")
            
#     except Exception as e:
#         print(f"[{i+1}/{total_puntos}] Error en punto: {e}")

# ==========================================
# 6. RESULTADO FINAL
# ==========================================
# print("\n" + "="*60)
# print("RESULTADO FINAL")
# print("="*60)
# if mejor_minimo_global is not None:
#     print(f"Coordenadas del Mínimo Global: {mejor_minimo_global}")
#     print(f"Valor de la Función en el Mínimo: {mejor_valor_global}")
#     print(f"Se probaron {total_puntos} puntos iniciales.")
#  else:
#     print("No se encontró ningún mínimo válido.")

# print("\n" + "="*60)
# print("FIN DEL PROCESO")
# print("="*60)
