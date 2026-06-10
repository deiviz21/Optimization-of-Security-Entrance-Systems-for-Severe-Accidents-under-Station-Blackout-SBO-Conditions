import numpy as np
import os

# ==============================
# This script will help us to read the results file
# ==============================

def procesar_archivo(ruta):
    if not os.path.exists(ruta):
        return np.nan

    try:
        datos = np.loadtxt(ruta, usecols=(0,1,2,3))    # Which columns we want to read.

        if datos.size == 0:
            return np.nan

        tiempo = datos[:, 0]                           # We associate column 0 to time steps values
        tiempo = np.insert(tiempo, 0, 0)

        h2_co_suma = datos[:, 1]                       # We associate column 1 to (H2 + CO) concentration values to each time step
        o2 = datos[:, 2]                               # We associate column 2 to O2 concentration values to each time step
        Presion = datos[:, 3]                          # We associate column 3 to presion values to each time step

        P_ref = 500000                                 # Design pressure of the cointainment, which will be used as the reference value and must not be exceeded

        # 🔥 Dc calculation: We will calculate de concentration deseability term. Here it will be necessary to respect the limitations that we put into the system to avoid any deflagration process.
        Dc = []
        for i in range(len(h2_co_suma)):
            if h2_co_suma[i] > 0.09:                   # The inflamable gases concentration must be under 0.09
                return 1                               # If inflamable gases concentration is over 0.09 we will consider the simulation very dangerous and we will discard it.
            elif o2[i] < 0.05:                         # The oxigen concentration must be higher than 0.05, otherwise it will be imposible to have deflagration 
                resultadoDc = 1                        # If oxigen concentration is under 0.05 we will consider this time step really safe 
            else:
                resultadoDc = ((0.09 - np.minimum(h2_co_suma[i], 2*(o2[i]-0.05))) / 0.09)  # We calculate the concentration deseability for each column term. Concentration deseability for each time step.

            Dc.append(resultadoDc)

        Dc = np.array(Dc)

        # 🔥 Dp calculation: We will calculate de preassure deseability term. Here it will be necessary to respect the limitations that we put into the system to avoid any breack in the contention.
        Dp = []
        for i in range(len(Presion)):
            if Presion[i] > P_ref:                    # The preassure needs to be under our reference preasure to be in a safe conditions
                return 1                              # If preassure is over reference preassure the whole simulation will be consider  very dangerous and we will discard it.
            else:
                resultadoDp = (P_ref - Presion[i]) / (P_ref - 100000)   # We calculate the preassure deseability for each column term. Concentration deseability for each time step.
                Dp.append(resultadoDp)

        Dp = np.array(Dp)

        # 🔥 Time step: We will need to know the value of each time step
        paso_t = []
        for i in range(len(tiempo) - 1):
            resultadot = tiempo[i+1] - tiempo[i]
            paso_t.append(resultadot)

        paso_t = np.array(paso_t)

        # 🔥 We will calculate the total deseability for every time step
        Dt_col = []
        for i in range(len(paso_t)):
            resultadoDt = (Dc[i] * Dp[i]) * paso_t[i]
            Dt_col.append(resultadoDt)

        Dt_col = np.array(Dt_col)

        # 🔥 Deseability integration over the time.
        D_tem = np.sum(Dt_col) / (tiempo[-1] - tiempo[0])
        
        # Total deseability term
        D_tot = D_tem * min(Dp) * min(Dc)
        
        #Risk
        Riesgo = 1 - D_tot

        return Riesgo

    except Exception as e:
        return np.nan


# 🔥 EXECUTION AND RESULTS PATHS WHERE WE READ THE DIFFERENT COLUMNS WITH THE RESULTS
if __name__ == "__main__":

    ruta = r"C:\TFM DAVID\SBO\CASO BASE copia\RESULTADOS.TXT"  # Results path that will allow us to read the concentration and presion values of different gases

    resultado = procesar_archivo(ruta)

    print(resultado)
