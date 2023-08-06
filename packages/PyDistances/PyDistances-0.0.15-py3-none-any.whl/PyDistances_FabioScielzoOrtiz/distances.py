def Dist_Euclidea(x_i, x_r): 
    """
    Calcula la distancia Euclidea entre dos vectores de observaciones.

    Parametros (inputs)
    ----------
    x_i , x_r: vectores de observaciones. Arrays de una dimension.       

    Devuelve (outputs)
    -------
    d: la distancia Euclidea entre x_i y x_r.
    """
    Dist_Euclidea = ( ( x_i - x_r )**2 ).sum()
    Dist_Euclidea = np.sqrt(Dist_Euclidea)
    return Dist_Euclidea