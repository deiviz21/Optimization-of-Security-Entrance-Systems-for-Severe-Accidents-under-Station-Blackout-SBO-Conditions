import re
import os
import sys

# ==============================
# This script will help us to modify the activation time of security systems in the INPUT file 
# ==============================

# We define a function which call two variables called tcss (sprays) and tfc (fan coolers)
def reemplazar_valores_txt(tcss, tfc, caudal):
    ruta_archivo = r"C:\TFM DAVID\SBO\CASO BASE copia\tcss_tfc_caudal\Input_SBO_Mit.INP"    # We define the INPUT path where we will change the activation values
    
    # It verifies that the file exists

    if not os.path.exists(ruta_archivo):
        print(f" Error: El archivo no existe en:\n{ruta_archivo}")
        return False
    
    try:
        # We read the file
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            contenido = archivo.read()
        
        # We only change the desirable number (It needs decimals with a dot)
    
        contenido = re.sub(
            r'(?<=\{\{\{tcss=)\d+(?:\.\d+)?(?=\}\}\})',
            str(float(tcss)),  # ← Convertir a float, no a int
            contenido
        )

        contenido = re.sub(
            r'(?<=\{\{\{tfc=)\d+(?:\.\d+)?(?=\}\}\})',
            str(float(tfc)),   # ← Convertir a float, no a int
            contenido
        )
        
        contenido = re.sub(
            r'(?<=\{\{\{caudal=)\d+(?:\.\d+)?(?=\}\}\})',
            str(float(caudal)),  # ← Convertir a float, no a int
            contenido
        )
        
        # It save the changes in the file
        with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
            archivo.write(contenido)
        
        print(f" Actualizado: tcss={tcss}, tfc={tfc}, caudal={caudal}")
        return True
        
    except Exception as e:
        print(f" Error: {e}")
        return False
    
#  IMPORTANT: This will allow us to call the script from a subprocess
if __name__ == "__main__":
    if len(sys.argv) == 4:
        tcss = float(sys.argv[1])
        tfc = float(sys.argv[2])
        caudal = float(sys.argv[3])
        reemplazar_valores_txt(tcss, tfc, caudal)
    else:
        # ✅ CORREGIDO: Mensaje actualizado a 3 argumentos
        print(" Uso: python mod_txt.py <tcss> <tfc> <caudal>")
        print("Ejemplo: python mod_txt.py 0.5 0.8 1000")
       
        
      
reemplazar_valores_txt(90.40, 50.3, 0.19)