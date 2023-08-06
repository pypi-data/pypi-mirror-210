from pathlib import Path

hns_calib = """
* FICHERO DE ESPEFICIACION DE ALGORITMOS Y PARAMETROS DE CALIBRACIÓN PARA MODELADO DE QUÍMICOS (HNS) TENIENDO EN CUENTA ENSAYOS CEPSA 2020
*--------------------------------------------------
* SPREADING:
* Dos opciones de algoritmos para evaluar spreading de HNS: 1)la utilizada en TESEO-FUEL y 2)la utilizada para químicos en MOHID
*--------------------------------------------------
* ALGORTIMO_SPREADING_HNS(1=ALG_DIF.EQUIVALENTE[ADIOS2],3=ALG_RABEH-KOLLURU[MOHID-HNS])
3
* PARAMETRO: CONSTANTE DE TASA DE ESPARCIMIENTO LATERAL K1(días-1). VALORES POR DEFECTO: SI ALGORITMO-1, K1=1.21; SI ALGORITMO-3, K1=5787.037
5787.037
*--------------------------------------------------
* EVAPORATION:
* Única formulación para evaluar evapoación de HNS, la utilizada para químicos en MOHID, pero dos opciones de calibración: 1) calibrar la cte que aparece en la formulación del coeficiente de transferencia; 2) calibrar directamente el valor del coeficiente de transferencia
*--------------------------------------------------
* OPCIÓN_DE_CALIBRACIÓN EVAPORACION(1=CALIBRACIÓN DE LA ECUACIÓN PLANTEADA POR [MACKAY AND MATSUGU 1973] PARA EL CÁLCULO DEL COEFICIENTE DE TRANSFERENCIA DE MASA Km(m/s); 2=CALIBRACIÓN DIRECTA DEL COEFICIENTE DE TRANSFERENCIA DE MASA Km(m/s)
1
* PARAMETRO: SI OPCIÓN CALIBRACIÓN-1 CONSTANTE QUE APARECE EN EL CÁLCULO DEL COEFICIENTE DE TRANSFERENCIA DE MASA (VALOR POR DEFECTO 0.0292); SI OPCIÓN CALIBRACIÓN-2 COEFICIENTE DE TRANSFERENCIA DE MASA-Km (m/s) (VALOR POR DEFECTO ?? (a extraer de ensayos)
0.0292
* Si viento nulo, velocidad mínima de viento (si finalmente se calibra el parámetro anterior de evaporación para viento nulo gracias a los ensayos, poner 0 aquí)
0.001
*--------------------------------------------------
*--------------------------------------------------
* DISOLUTION:
* Única formulación para evaluar evapoación de HNS, la utilizada para químicos en MOHID, pero dos opciones de calibración: 1) calibrar la cte que aparece en la formulación del coeficiente de transferencia; 2) calibrar directamente el valor del coeficiente de transferencia
* Ojo porque esta calibración solo está implicada en la disolución que ocurre en superficie, la disolución en columna se ha dejado por defecto en el código (como está en MOHID) puesto que los ensayos son válidos solo para vertido superficial de HNS de flotabilidad positiva
*--------------------------------------------------
* OPCIÓN_DE_CALIBRACIÓN DISOLUCION(1=CALIBRACIÓN DE LA ECUACIÓN PLANTEADA POR [HAYDUCK AND LAUDIE 1974] PARA EL CÁLCULO DE LA DIFUSIVIDAD QUE APARECE EN EL COEFICIENTE DE TRANSFERENCIA DE MASA Kd(m/s); 2=CALIBRACIÓN DIRECTA DEL COEFICIENTE DE TRANSFERENCIA DE MASA Kd(m/s)
1
* PARAMETRO: SI OPCIÓN CALIBRACIÓN-1 CONSTANTE QUE APARECE EN LA DIFUSIVIDAD EN EL CÁLCULO COEFICIENTE DE TRANSFERENCIA DE MASA (VALOR POR DEFECTO 13.26); SI OPCIÓN CALIBRACIÓN-2 COEFICIENTE DE TRANSFERENCIA DE MASA Kd(m/s) (VALOR POR DEFECTO ?? (a extraer de ensayos)
13.26"""


def write_hns_calib(dir_path: str, simulation_keyword: str = "cas1"):
    """write TESEO's hns-calibration-file at the requested path

    Args:
        dir_path (str): _description_
        simulation_keyword (str, optional): _description_. Defaults to "cas1".
    """

    path = Path(dir_path, simulation_keyword + "_HNS.calib")

    with open(path, "w") as f:
        f.write(hns_calib)
