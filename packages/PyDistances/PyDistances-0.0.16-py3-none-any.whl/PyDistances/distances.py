import numpy as np
import pandas as pd

def Euclidean_Dist(x_i, x_r): 
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

def Euclidean_Dist_Matrix(Data):
    """
    Calcula la matriz de distancias Euclideas para un conjunto de datos.

    Parametros (inputs)
    ----------
    Data: un data-frame Pandas o un array Numpy.       

    Devuelve (outputs)
    -------
    M: la matriz de distancias Euclideas entrelas observaciones (filas) del data-frame Data.
    """
    if isinstance(Data, pd.DataFrame):
        Data = Data.to_numpy()
    else:
        pass
    n = len(Data)
    M =  np.zeros((n , n))   
    for i in range(0, n):
        for r in range(i+1, n):        
                M[i,r] = Euclidean_Dist(Data[i,:], Data[r,:])
    M = M + M.T
    return M 

def Minkowski_Dist(x_i, x_r, q):
    """
    Calcula la distancia de Minkowski entre dos vectores de observaciones.

    Parametros (inputs)
    ----------
    x_i , x_r: vectores de observaciones. Arrays de una dimension.   
    q : debe ser un numero entero positivo.    

    Devuelve (outputs)
    -------
    d: la distancia de Minkowski entre x_i y x_r.
    """
    Dist_Minkowski = ( ( ( abs( x_i - x_r) )**q ).sum() )**(1/q)
    return Dist_Minkowski

def Minkowski_Dist_Matrix(Data, q):
    """
    Calcula la matriz de distancias de Minkowski para un conjunto de datos.

    Parametros (inputs)
    ----------
    Data: un data-frame Pandas o un array Numpy.       

    Devuelve (outputs)
    -------
    M: la matriz de distancias de Minkowski entrelas observaciones (filas) del data-frame Data.
    """
    if isinstance(Data, pd.DataFrame):
        Data = Data.to_numpy()
    else:  
        pass
    n = len(Data)
    M =  np.zeros((n , n))   
    for i in range(0, n):
        for r in range(i+1, n):        
                M[i,r] = Minkowski_Dist(Data[i,:] , Data[r,:], q)   
    M = M + M.T          
    return M 

def Canberra_Dist(x_i, x_r):
    """
    Calcula la distancia de Canberra entre dos vectores de observaciones.

    Parametros (inputs)
    ----------
    x_i , x_r: vectores de observaciones. Arrays de una dimension.       

    Devuelve (outputs)
    -------
    d: la distancia de Canberra entre x_i y x_r.
    """
    numerator =  abs( x_i - x_r )
    denominator =  ( abs(x_i) + abs(x_r) )
    numerator=np.array([numerator], dtype=float)
    denominator=np.array([denominator], dtype=float)
    # Se usa np.divide para evitar problemas con la division. En el caso de denominator=0, devuelve numerator. En otro caso, efectua la division.
    Dist_Canberra = ( np.divide( numerator , denominator , out=np.zeros_like(numerator), where=denominator!=0) ).sum() 
    return Dist_Canberra

def Canberra_Dist_Matrix(Data):
    """
    Calcula la matriz de distancias de Canberra para un conjunto de datos.

    Parametros (inputs)
    ----------
    Data: un data-frame Pandas o un array Numpy.       

    Devuelve (outputs)
    -------
    M: la matriz de distancias de Canberra entrelas observaciones (filas) del data-frame Data.
    """
    if isinstance(Data, pd.DataFrame):
        Data = Data.to_numpy()
    else:
        pass
    n = len(Data)
    M =  np.zeros((n , n))
    for i in range(0, n):
         for r in range(i+1, n):
            M[i,r] = Canberra_Dist(Data[i,:] , Data[r,:])  
    M = M + M.T              
    return M 

def Pearson_Dist(x_i, x_r, variance) :
    """
    Calcula la distancia de Pearson entre dos vectores de observaciones.

    Parametros (inputs)
    ----------
    x_i , x_r: vectores de observaciones. Arrays de una dimension.    
    variance : vector de varianzas de las variables (columnas) de un data-frame o array.   

    Devuelve (outputs)
    -------
    d: la distancia de Pearson entre x_i y x_r.
    """
    Dist_Pearson = ( ( x_i - x_r )**2 / variance ).sum()
    Dist_Pearson = np.sqrt(Dist_Pearson)
    return Dist_Pearson

def Pearson_Dist_Matrix(Data):
    """
    Calcula la matriz de distancias de Pearson para un conjunto de datos.

    Parametros (inputs)
    ----------
    Data: un data-frame Pandas o un array Numpy.       

    Devuelve (outputs)
    -------
    M: la matriz de distancias de Pearson entre las observaciones (filas) del data-frame Data.
    """
    if isinstance(Data, pd.DataFrame):
        Data = Data.to_numpy()
    else:
        pass
    n = len(Data)
    M =  np.zeros((n , n))
    var = np.var(Data, axis=0, ddof=1)
    for i in range(0, n): 
         for r in range(i+1, n):
            M[i,r] = Pearson_Dist(Data[i,:] , Data[r,:], var)   
    M = M + M.T                 
    return M 

def Mahalanobis_Dist(x_i, x_r, S_inv):  
    """
    Calcula la distancia de Mahalanobis entre dos vectores de observaciones.

    Parametros (inputs)
    ----------
    x_i, x_r : son arrays de una dimension.
    S_inv : inversa de la matriz de covarianzas de un data-frame o array.
          
    Devuelve (outputs)
    ----------
    d: la distancia de Mahalanobis entre x_i y x_r.

    Comentarios
    ----------
    Todas las columnas del data-frame o array deben ser type = 'float' or 'int' (especialemtne no 'object'), en otro caso habra problema de dimensionalidad al calcular x @ S_inv @ x.T
    """
    x = np.array([x_i - x_r])
    Dist_Maha = np.sqrt( x @ S_inv @ x.T )
    Dist_Maha = float(Dist_Maha)
    return Dist_Maha

def Mahalanobis_Dist_Matrix(Data):
    """
    Calcula la matriz de distancias de Mahalanobis para un conjunto de datos.

    Parametros (inputs)
    ----------
    Data: un data-frame Pandas o un array Numpy.       

    Devuelve (outputs)
    -------
    M: la matriz de distancias de Mahalanobis entre las observaciones (filas) del data-frame Data.
    """
    if isinstance(Data, pd.DataFrame):
        Data = Data.to_numpy()
    else:
        pass
    n = len(Data)
    M =  np.zeros((n , n))
    S_inv=np.linalg.inv( np.cov(Data , rowvar=False) )
    for i in range(0, n):
         for r in range(i+1, n):
            M[i,r] = Mahalanobis_Dist(x_i=Data[i,:], x_r=Data[r,:], S_inv=S_inv ) 
    M = M + M.T
    return M 

def a_b_c_d_Matrix(Data):
    """
    Calcula las matrices con los parametros a,b,c y d usados en las distancias de Jaccard, Sokal y Gower.

    Parametros (inputs)
    ----------
    Data: un data-frame Pandas o un array Numpy.       

    Devuelve (outputs)
    -------
    a,b,c,d : matrices con los parametros a,b,c y d calculados para Data.
    p : numero de columnas de Data.
    """
    if isinstance(Data, pd.DataFrame):
        X = Data.to_numpy()
    else:
        X = Data
    a = X @ X.T
    n = X.shape[0]
    p = X.shape[1]
    ones_matrix = np.ones((n, p)) 
    b = (ones_matrix - X) @ X.T
    c = b.T
    d = (ones_matrix - X) @ (ones_matrix - X).T
    return a , b , c , d , p

def Sokal_Similarity(i , r, a , d, p):
    """
    Calcula la similaridad de Sokal entre dos vectores de observaciones.

    Parametros (inputs)
    ----------
    i , r: numeros enteros no negativos. Son los indices de las observaciones entre las que se quiere calcular la similaridad.
    a, d: matrices con los parametros a y d usados en la similaridad de Sokal.
    p : numero de columnas del conjunto de datos.       

    Devuelve (outputs)
    -------
    d: la similaridad de Sokal entre las observaciones con indice i y r.
    """
    if a[i,r] + d[i,r] == 0 :
        Sokal_Similarity = 0
    else :
        Sokal_Similarity = (a[i,r] + d[i,r]) / p
    return Sokal_Similarity

def Sokal_Dist(i, r, a, d, p):
    """
    Calcula la distancia de Sokal entre dos vectores de observaciones.

    Parametros (inputs)
    ----------
    i , r: numeros enteros no negativos. Son los indices de las observaciones entre las que se quiere calcular la similaridad.
    a, d: matrices con los parametros a y d usados en la similaridad de Sokal.
    p : numero de columnas del conjunto de datos.       

    Devuelve (outputs)
    -------
    d: la distancia de Sokal entre las observaciones con indice i y r.
    """
    dist_Sokal = np.sqrt( Sokal_Similarity(i , i, a , d, p) + Sokal_Similarity(r , r, a , d, p) - 2*Sokal_Similarity(i , r, a , d, p) )
    return dist_Sokal  

def Sokal_Dist_Matrix(Data):
    """
    Calcula la matriz de distancias de Sokal para un conjunto de datos.

    Parametros (inputs)
    ----------
    Data: un data-frame Pandas o un array Numpy.       

    Devuelve (outputs)
    -------
    M: la matriz de distancias de Sokal entre las observaciones (filas) del data-frame Data.
    """
    n = len(Data)
    M =  np.zeros((n , n))
    a, b, c, d, p = a_b_c_d_Matrix(Data)
    for i in range(0, n):
         for r in range(i+1, n):
            M[i,r] = Sokal_Dist(i=i, r=r, a=a, d=d, p=p)  
    M = M + M.T                    
    return M 

def Jaccard_Similarity(i , r, a, d, p):
    """
    Calcula la similaridad de Jaccard entre dos vectores de observaciones.

    Parametros (inputs)
    ----------
    i , r: numeros enteros no negativos. Son los indices de las observaciones entre las que se quiere calcular la similaridad.
    a, d: matrices con los parametros a y d usados en la similaridad de Sokal.
    p : numero de columnas del conjunto de datos.       

    Devuelve (outputs)
    -------
    d: la similaridad de Jaccard entre las observaciones con indice i y r.
    """
    if a[i,r] == 0 and  (p-d[i,r]) == 0 :
        Jaccard_Similarity = 1
    else :
        Jaccard_Similarity = a[i,r] / (p-d[i,r])
    return Jaccard_Similarity

def Jaccard_Dist(i , r, a, d, p):
    """
    Calcula la distancia de Jaccard entre dos vectores de observaciones.

    Parametros (inputs)
    ----------
    i , r: numeros enteros no negativos. Son los indices de las observaciones entre las que se quiere calcular la similaridad.
    a, d: matrices con los parametros a y d usados en la similaridad de Sokal.
    p : numero de columnas del conjunto de datos.       

    Devuelve (outputs)
    -------
    d: la distancia de Jaccard entre las observaciones con indice i y r.
    """
    Dist_Jaccard = np.sqrt( Jaccard_Similarity(i , i, a, d, p) + Jaccard_Similarity(r , r, a, d, p) - 2*Jaccard_Similarity(i , r, a, d, p) )
    return Dist_Jaccard 
 
def Jaccard_Dist_Matrix(Data):
    """
    Calcula la matriz de distancias de Jaccard para un conjunto de datos.

    Parametros (inputs)
    ----------
    Data: un data-frame Pandas o un array Numpy.       

    Devuelve (outputs)
    -------
    M: la matriz de distancias de Jaccard entrelas observaciones (filas) del data-frame Data.
    """
    n = len(Data)
    M =  np.zeros((n , n))
    a, b, c, d, p = a_b_c_d_Matrix(Data)
    for i in range(0, n):
        for r in range(i+1, n):
            M[i,r] = Jaccard_Dist(i=i, r=r, a=a, p=p, d=d)
    M = M + M.T                  
    return M 

def alpha(x_i, x_r):
    """
    Calcula el parametro alpha usado en la similaridad Matching.

    Parametros (inputs)
    ----------
    x_i , x_r: vectores de observaciones. Arrays de una dimension.   
    Data: un data-frame Pandas o un array Numpy.       

    Devuelve (outputs)
    -------
    alpha : valor del parametro alpha para las observaciones x_i y x_r.
    """
    alpha = sum(x_i == x_r)
    return(alpha) 
  
def Matching_Similarity(x_i, x_r, Data):
    """
    Calcula la similaridad Matching entre dos vectores de observaciones.

    Parametros (inputs)
    ----------
    x_i , x_r: vectores de observaciones. Arrays de una dimension.     
     

    Devuelve (outputs)
    -------
    d: la distancia de Matching entre x_i y x_r.
    """
    p = Data.shape[1]
    matching_similarity = alpha(x_i, x_r) / p
    return(matching_similarity)

def Matching_Dist(x_i, x_r, Data):
    """
    Calcula la distancia de Matching entre dos vectores de observaciones.

    Parametros (inputs)
    ----------
    x_i , x_r: vectores de observaciones. Arrays de una dimension.       

    Devuelve (outputs)
    -------
    d: la distancia de Matching entre x_i y x_r.
    """
    Dist_Matching = np.sqrt(Matching_Similarity(x_i, x_i, Data) +  Matching_Similarity(x_r, x_r, Data) - 2*Matching_Similarity(x_i, x_r, Data) )
    return( Dist_Matching )

def Matching_Dist_Matrix(Data):
    """
    Calcula la matriz de similaridades Matching para un conjunto de datos.

    Parametros (inputs)
    ----------
    Data: un data-frame Pandas o un array Numpy.       

    Devuelve (outputs)
    -------
    M: la matriz de similaridades Matching entre las observaciones (filas) del data-frame Data.
    """
    if isinstance(Data, pd.DataFrame):
        Data = Data.to_numpy()
    else:
        pass
    n = len(Data)
    M =  np.zeros((n , n))
    for i in range(0, n):
      for r in range(i+1, n):
         M[i,r] = Matching_Dist(x_i=Data[i,:], x_r=Data[r,:], Data=Data)
    M = M + M.T                  
    return M 

def Gower_Similarity_Matrix(Data, p1, p2, p3):
    """
    Calcula la matriz de similaridades de Gower  para un conjunto de datos.
    Se ha seguido a Gower (1971).

    Parametros (inputs)
    ----------
    Data: un data-frame Pandas o un array Numpy.  Data debe tener las primeras p1 t variables (columnas) cuantitativas, las siguientes p2 binarias y las restantes p3 multiclase.     
    p1, p2, p3 : numeros enteros no negativos.

    Devuelve (outputs)
    -------
    M: la matriz de similaridades de Gower entre las observaciones (filas) del data-frame Data.

    Comentarios 
    -------
    Si Data no contiene variables cuantitativas: p1=0.
    Si Data no contiene variables binarias: p2=0.
    Si Data no contiene variables multiclase: p3=0.
    """
    if isinstance(Data, pd.DataFrame):
        Data = Data.to_numpy()
    else:
        pass
    n = len(Data)
    M =  np.zeros((n , n))

    G_vector = np.repeat(0.5, p1)
    for k in range(0, p1):
        G_vector[k] = Data[:,k].max() - Data[:,k].min()

    ones = np.repeat(1, p1)
    Quant_Data = Data[: , 0:p1]
    Binary_Data = Data[: , (p1):(p1+p2)]
    Multiple_Data = Data[: , (p1+p2):(p1+p2+p3) ]

    a, b, c, d, p = a_b_c_d_Matrix(Binary_Data)

    for i in range(0, n):
         for r in range(i+1, n):
                numerator_part_1 = ( ones - ( abs(Quant_Data[i,:] - Quant_Data[r,:]) / G_vector ) ).sum() 
                numerator_part_2 = a[i,r]               
                numerator_part_3 = alpha(Multiple_Data[i,:], Multiple_Data[r,:])
                numerator = numerator_part_1 + numerator_part_2 + numerator_part_3
                denominator = p1 + (p2 - d[i,r]) + p3
                if denominator == 0:
                    M[i,r] = 0
                else:    
                    M[i,r] = numerator / denominator
    M = M + M.T
    M = M + np.identity(n)
    return M  

def Gower_Dist_Matrix(Data, p1, p2, p3 ):
    """
    Calcula la matriz de distancias de Gower para un conjunto de datos.

    Parametros (inputs)
    ----------
    Data: un data-frame Pandas o un array Numpy.  Data debe tener las primeras p1 t variables (columnas) cuantitativas, las siguientes p2 binarias y las restantes p3 multiclase.     
    p1, p2, p3 : enteros no negativos.    
    
    Devuelve (outputs)
    -------
    M: la matriz de distancias de Gower entre las observaciones (filas) del data-frame Data.

    Comentarios 
    -------
    Si Data no contiene variables cuantitativas: p1=0.
    Si Data no contiene variables binarias: p2=0.
    Si Data no contiene variables multiclase: p3=0.
    """
    M = Gower_Similarity_Matrix(Data, p1, p2, p3)
    M = np.sqrt( 1 - M )
    return M





def MAD(X_j) :
    """
    Calcula la desviacion absoluta mediana de una variable.

    Parametros (inputs)
    ----------
    X_j: un vector de observaciones de una variable. Debe ser un numpy array de una dimension o una pandas series.  

    Devuelve (outputs)
    -------
    MAD: la desviacion absoluta median de X_j.
    """
    MAD = np.median( np.abs( X_j - np.median(X_j) ) )
    return MAD

def Variable_alpha_trimmed(X_j, alpha) : 
    """
    Genera la variable alpha-recortada (trimmed) de una variable pasada como argumento.

    Parametros (inputs)
    ----------
    X_j : un vector de observaciones de una variable. Debe ser un numpy array de una dimension o una pandas series.  
    alpha : debe ser un numero en el intervalo cerrado [0,1]. 

    Devuelve (outputs)
    -------
    result: la variable alpha-trimmed obtenida a partir de X_j.
    """
    # Se calcula la cota inferior
    lower_bound = np.quantile(X_j, q=alpha/2)  
    # Se calcula la cota superior
    upper_bound = np.quantile(X_j, q=1-alpha/2) 
    # Se usa np.logical_and para generar un vector booleano, cuyo valor i-esimo es True  si la observacion i de X_j esta entre la cota inferior y la superior, y False en otro caso.
    mask = np.logical_and(X_j >= lower_bound, X_j <= upper_bound)
    # Seleccionamos las observaciones de X_j que cumplen la condicion pasada como argumento a np.logical_and. 
    result = X_j[mask]
    return result

def Variable_alpha_winsorized(X_j, alpha) :
    """
    Genera la variable alpha-winsorized de una variable pasada como argumento.

    Parametros (inputs)
    ----------
    X_j : un vector de observaciones de una variable. Debe ser un numpy array de una dimension o una pandas series.  
    alpha : debe ser un numero en el intervalo cerrado [0,1]. 

    Devuelve (outputs)
    -------
    result: la variable alpha-winsorized obtenida a partir de X_j.
    """
    # Si X_j es un vector de ceros, la version winsorized de X_j es la propia X_j.
    if np.all(X_j == 0) :  
        variable_alpha_winsorized = X_j
        variable_alpha_winsorized = pd.Series(variable_alpha_winsorized)
    # Si X_j no es un vector de ceros.
    else :
        # Calculamos las cotas inferiores y superiores.
        lower_bound = np.quantile(X_j, q=alpha/2)
        upper_bound = np.quantile(X_j, q=1-alpha/2)
        # Definimos los vectores A y B, y los valores a  y b. Para mas detalles ver la seccion 7.2.1.
        A = X_j[X_j <= lower_bound]  
        B = X_j[X_j >= upper_bound] 
        a = np.min( X_j[X_j > lower_bound] )
        b = np.max( X_j[X_j < upper_bound] )
       # Se define la funcion h de la varianza winsorizada. Ver la seccion 7.2.1 para mas detalles.
        def h(x):
            # Para que la sentencia 'x in A' funcione se debe usar A.tolist(), que es una lista con los elementos del array A. Y lo mismo para B.
            if x in A.tolist() : 
                  result = a 
            elif x in B.tolist() : 
                  result = b
            else : 
                  result = x
            return result
        # Se vectoriza la funcion h para aplicara poder aplicarla de forma eficiente a cada elemento de X_j
        h_vec = np.vectorize(h)
        # Se aplica h vectorizada sobre el array X_j y con ello se obtiene la variable winsorizada.
        variable_alpha_winsorized = h_vec(X_j)   
        variable_alpha_winsorized = pd.Series(variable_alpha_winsorized)
    return variable_alpha_winsorized

def robust_variance(X_j, Method, alpha=None) :
    """
    Calcula la varianza robusta de una variable, considerando tres metodos diferentes.

    Parametros (inputs)
    ----------
    X_j : un vector de observaciones de una variable. Debe ser un numpy array de una dimension o una pandas series. 
    Method : es el metodo empleado para calcular la varianza robusta. Los metodos disponibles son 'trimmed', 'winsorized' y 'MAD'. 
    alpha : debe ser un numero en el intervalo cerrado [0,1]. Solo debe especificarse si Method es 'trimmed' o 'winsorized'.

    Devuelve (outputs)
    -------
    result: la varianza robusta de la variable X_j.
    """
    if Method == 'MAD' :
        result = MAD(X_j)**2
    if Method == 'trimmed' :
        result = np.var( Variable_alpha_trimmed(X_j, alpha) )
    if Method == 'winsorized' :
        result = np.var( Variable_alpha_winsorized(X_j, alpha) )
    return result

def robust_correlation(X_j, X_r, Method, alpha=None) :
    """
    Calcula la correlacion robusta de una variable.

    Parametros (inputs)
    ----------
    X_j , X_r: vectores de observaciones de dos variables. Deben ser   numpy arrays de una dimension o pandas series. 
    Method : es el metodo empleado para calcular la varianza robusta. Los metodos disponibles son 'trimmed', 'winsorized' y 'MAD'. 
    alpha : debe ser un numero en el intervalo cerrado [0,1]. Solo debe especificarse si Method es 'trimmed' o 'winsorized'.

    Devuelve (outputs)
    -------
    result: la correlacion robusta entre las variables X_j y X_r.
    """
    # Si la varianza robusta de X_j es cero, la version estandarizada de X_j es la propia X_j.
    if np.sqrt(robust_variance(X_j, Method, alpha)) == 0 :
        X_j_std = X_j
    # Si la varianza robusta de X_j es distinta de cero.
    else :
       # Se estandariza X_j como se especifica en la seccion 7.2.2.
        X_j_std = X_j / np.sqrt(robust_variance(X_j, Method, alpha))
    # Si la varianza robusta de X_r es cero, la version estandarizada de X_r es la propia X_r.
    if np.sqrt(robust_variance(X_r, Method, alpha)) == 0 :
        X_r_std = X_r
    # Si la varianza robusta de X_res distinta de cero.
    else :
      # Se estandariza X_j como se especifica en la seccion 7.2.2.  
      X_r_std = X_r / np.sqrt(robust_variance(X_r, Method, alpha))
    # Se calcula la correlacion robusta como se especifica en la seccion 7.2.2, evitando problemas de divisionalidad.
    robust_var_3 = robust_variance(X_j_std + X_r_std, Method, alpha)
    robust_var_4 = robust_variance(X_j_std - X_r_std, Method, alpha)
    if (robust_var_3 + robust_var_4) == 0 :
        robust_corr = (robust_var_3 - robust_var_4) 
    else : 
        robust_corr = (robust_var_3 - robust_var_4) / (robust_var_3 + robust_var_4)
    return robust_corr

def robust_correlation_matrix(Data, Method, alpha=None) :
    """
    Calcula la matriz de correlaciones robusta de un conjunto de datos, utilizando la funcion robust_correlation.

    Parametros (inputs)
    ----------
    Data : debe ser un data-frame de Pandas o un array de Numpy. 
    Method : es el metodo empleado para calcular la varianza robusta. Los metodos disponibles son 'trimmed', 'winsorized' y 'MAD'. 
    alpha : debe ser un numero en el intervalo cerrado [0,1]. Solo debe especificarse si Method es 'trimmed' o 'winsorized'.

    Devuelve (outputs)
    -------
    M : la matriz de correlaciones robusta para el conjunto de datos Data.
    """
    p = len(Data.columns)
    M =  np.zeros((p , p))
    for i in zip(range(0,p), Data.columns) :
        for j in zip(range(0,p), Data.columns) :
            M[i[0],j[0]] = robust_correlation(X_j=Data[i[1]], X_r=Data[j[1]], Method=Method, alpha=alpha)
    M = pd.DataFrame(M, columns=Data.columns, index=Data.columns)
    return M 
 
def robust_correlation_matrix(Data, Method, alpha=None) :
    """
    Calcula la matriz de correlaciones robusta de un conjunto de datos, utilizando la funcion robust_correlation.

    Parametros (inputs)
    ----------
    Data : debe ser un data-frame de Pandas o un array de Numpy. 
    Method : es el metodo empleado para calcular la varianza robusta. Los metodos disponibles son 'trimmed', 'winsorized' y 'MAD'. 
    alpha : debe ser un numero en el intervalo cerrado [0,1]. Solo debe especificarse si Method es 'trimmed' o 'winsorized'.

    Devuelve (outputs)
    -------
    M : la matriz de correlaciones robusta para el conjunto de datos Data.
    """
    p = len(Data.columns)
    M =  np.zeros((p , p))
    for i in zip(range(0,p), Data.columns) :
        for j in zip(range(0,p), Data.columns) :
            M[i[0],j[0]] = robust_correlation(X_j=Data[i[1]], X_r=Data[j[1]], Method=Method, alpha=alpha)
    M = pd.DataFrame(M, columns=Data.columns, index=Data.columns)
    return M 
 
def Delvin_transformation(matrix, epsilon) : 
    """
    Calcula la matriz de correlaciones robusta de un conjunto de datos.

    Parametros (inputs)
    ----------
    Matrix : debe ser un data-frame de Pandas o un array de Numpy. 
    epsilon : debe ser un numero positivo cercano a cero. Se recomienda epsilon=0.05.

    Devuelve (outputs)
    -------
    M : la version tranformada de matrix, tras aplicarle la transformacion de Delvin.
    """
    # Se define la funcion z tal y como se especifica en la seccion POR ANADIR.
    def z(x) : 
       return np.arctanh(x)
    # Se define la funcion z ^{-1} tal y como se especifica en la seccion POR ANADIR.
    def z_inv(x) :  
       # La arctanh es la inversa de tanh, por tanto, la inversa de arctanh es tanh.
       return np.tanh(x) 
    # Se define la funcion g tal y como se especifica en la seccion POR ANADIR.
    def g(i,j, matrix) :
        if isinstance(matrix, pd.DataFrame) : 
            R = matrix.to_numpy()
        else : 
            R = matrix
        if i == j :             
            result = 1
        else:
            if np.abs(R[i,j]) <= z(epsilon) :  
                    result = 0
            elif R[i,j] < - z(epsilon) : 
                    result = z_inv( R[i,j] + epsilon )
            elif R[i,j] > z(epsilon) : 
                    result = z_inv( R[i,j] - epsilon )
        return result
    # Se crea una matriz cuyos elementos osn el resultado de aplicar la funcion g sobre matrix elemento a elemento.
    p = matrix.shape[0]
    M =  np.zeros((p , p))
    for i in range(0,p) :
        for j in range(0,p) :
            M[i,j] = g(i,j, matrix)
    if isinstance(matrix, pd.DataFrame) :
        M = pd.DataFrame(M, columns=matrix.columns, index=matrix.columns)
    else :
        pass
    return M  
      
def Delvin_algorithm(matrix, epsilon, n_iters):
    """
    Aplica el algoritmo de Delvin a una matriz.

    Parametros (inputs)
    ----------
    matrix : debe ser un data-frame de Pandas o un array de Numpy. 
    epsilon : debe ser un numero positivo cercano a cero. Se recomienda epsilon=0.05.
    n_iter : debe ser un numero entero positivo. Es el numero maximo de iteraciones que utiliza el algoritmo de Delvin.

    Devuelve (outputs)
    -------
    new_matrix : la matriz que resulta de aplicar el algoritmo de Delvin a la matriz matrix.
    """
    new_matrix = matrix.copy()
    # Se inicializa  i=0 para entrar en el bucle while
    i = 0
    # Mientras i sea inferior o igual a n_iter, el bucle continua ejecutandose.
    while i < n_iters:
        # Si new_matrix ya es definida positiva (todos sus autovalores son positivos), se devuelve new_matrix. En otro caso, se le aplica la transformacion de Delvin y se vuelve a comprobar si es definida positiva.
        if np.all(np.linalg.eigvals(new_matrix) > 0):
            return new_matrix , i
        else:
            new_matrix = Delvin_transformation(matrix=new_matrix, epsilon=epsilon)
            i = i + 1
    return new_matrix , i


def Robust_Mahalanobis_Dist(x_i, x_r, Data, Method, epsilon, alpha=None, n_iters=20) :
    """
    Calcula la matriz de distancias de Mahalanobis robusta para un conjunto de datos dado.
    Se ha seguido a Gnanadesikan (1997) y Delvin et al. (1975).

    Parametros (inputs)
    ----------
    Data : debe ser un data-frame de Pandas o un array de Numpy. 
    Method : es el metodo empleado para calcular la varianza robusta. Los metodos disponibles son 'trimmed', 'winsorized' y 'MAD'. 
    alpha : debe ser un numero en el intervalo cerrado [0,1]. Solo debe especificarse si Method es 'trimmed' o 'winsorized'.
    epsilon : debe ser un numero positivo cercano a cero. Se recomienda epsilon=0.05.
    n_iters : debe ser un numero entero positivo. Es el numero maximo de iteraciones que utiliza el algoritmo de Delvin.

    Devuelve (outputs)
    -------
    M :  la matriz de distancias de Mahalanobis robusta entre las observaciones (filas) de Data.
    """
    # Se calcula la matriz de correlaciones robustas para Data.
    robust_corr_matrix = robust_correlation_matrix(Data, Method, alpha)
    # Se aplica el algoritmo de Delvin a la matriz de correlaciones robustas calculada.
    robust_corr_matrix_Delvin_algorithm , i = Delvin_algorithm(matrix=robust_corr_matrix, epsilon=epsilon, n_iters=n_iters)
    # Se calcula la matriz de covarianzas robustas a partir de la matriz de correlaciones robustas.
    robust_cov_matrix_Delvin_algorithm = np.diag(Data.std()) @ robust_corr_matrix_Delvin_algorithm @ np.diag(Data.std()) 
    # Se calcula la inversa de la matriz de covarianzas robusta.
    S_inv = np.linalg.inv( robust_cov_matrix_Delvin_algorithm )

    Dist_Robust_Mahalanobis = Mahalanobis_Dist(x_i=x_i, x_r=x_r, S_inv=S_inv)

    return Dist_Robust_Mahalanobis



def Robust_Mahalanobis_Dist_Matrix(Data, Method, epsilon, alpha=None, n_iters=20):
    """
    Calcula la matriz de distancias de Mahalanobis robusta para un conjunto de datos dado.

    Parametros (inputs)
    ----------
    Data : debe ser un data-frame de Pandas o un array de Numpy. 
    Method : es el metodo empleado para calcular la varianza robusta. Los metodos disponibles son 'trimmed', 'winsorized' y 'MAD'. 
    alpha : debe ser un numero en el intervalo cerrado [0,1]. Solo debe especificarse si Method es 'trimmed' o 'winsorized'.
    epsilon : debe ser un numero positivo cercano a cero. Se recomienda epsilon=0.05.
    n_iters : debe ser un numero entero positivo. Es el numero maximo de iteraciones que utiliza el algoritmo de Delvin.

    Devuelve (outputs)
    -------
    M :  la matriz de distancias de Mahalanobis robusta entre las observaciones (filas) de Data.
    """
    # Se calcula la matriz de correlaciones robustas para Data.
    robust_corr_matrix = robust_correlation_matrix(Data, Method, alpha)
    # Se aplica el algoritmo de Delvin a la matriz de correlaciones robustas calculada.
    robust_corr_matrix_Delvin_algorithm , i = Delvin_algorithm(matrix=robust_corr_matrix, epsilon=epsilon, n_iters=n_iters)
    # Se calcula la matriz de covarianzas robustas a partir de la matriz de correlaciones robustas.
    robust_cov_matrix_Delvin_algorithm = np.diag(Data.std()) @ robust_corr_matrix_Delvin_algorithm @ np.diag(Data.std()) 
    # Se calcula la inversa de la matriz de covarianzas robusta.
    S_inv = np.linalg.inv( robust_cov_matrix_Delvin_algorithm )
    if isinstance(Data, pd.DataFrame): 
        Data = Data.to_numpy()
    else :
        pass
    n = len(Data)
    M =  np.zeros((n , n))
    # Se calcula la distancia de Mahalanobis entre cada par de filas de Data usando como S_inv la inversa de la matriz de covarianzas robusta.
    for i in range(0, n):
         for r in range(i+1, n):        
             M[i,r] = Mahalanobis_Dist(x_i=Data[i,:], x_r=Data[r,:], S_inv=S_inv) 
    M = M + M.T                     
    return M 



class GeneralizedGowerDistance: 
    """
    Calcula la matriz de distancias de Gower generalizada y RMS para un conjunto de datos. 
    Se ha seguido Cuadras and Fortiana (1998), Albarrán et al. (2015) and Grané et al. (2021).

    Parametros (inputs)
    ----------
      Data : un data-frame Pandas o un array Numpy.  Data debe tener las primeras p1 variables (columnas) cuantitativas, las siguientes p2 binarias y las restantes p3 multiclase.  
     p1, p2, p3 : numeros enteros no negativos.
          - Si Data no contiene variables cuantitativas: p1=0.
          - Si Data no contiene variables binarias: p2=0.
          - Si Data no contiene variables multiclase: p3=0.
     d1 : nombre de la distancias que se desea calcular para las variables cuantitativas.
     d2 : nombre de la distancias que se desea calcular para las variables binarias. 
     d3 : nombre de la distancias que se desea calcular para las variables multiclase. 
          - Para un correcto funcionamiento de la clase, deben definirse prefiamente funciones que calculen matrices de distancia, tales como las que se han presentado en las anteriores secciones. Un requerimiento sintactico de la clase es que dichas funciones tengan como nombre Matrix_Dist_x, donde x debe ser el nombre de la distancia que sera introducido en d1, d2 o d3. Por ejemplo, si d1='Pearson', para que la clase funcione correctamente debe de haber una funcion llamada Matrix_Dist_Pearson definida en nuestro entorno de trabajo, la cual debe calcular la matriz de distancias de Pearson para un data-frame pandas o array numpy pasado como parametro.
     epsilon : deberia ser un numero positivo pequeno. Se recomienda el valor por defecto, que es 0.05. Este parametro solo es usado si d1='Mahalanobis_Robust', y es el parametro epsilon que aparece en la transformacion de Delvin, definida con la funcion Delvin_transformation, la cual es usada en la funcion Matrix_Dist_Mahalanobis_Robust.. Para mas detalles ver el capitulo 7 de este trabajo.
      n_iters : debe ser un numero entero no negativo. Es el numero de iteraciones maximas del algoritmo de Delvin, definido con la funcion Delvin_algorithm, que es usada en la funcion Matrix_Dist_Mahalanobis_Robust.  Para mas detalles ver el capitulo 7 de este trabajo.
     Method : es el nombre del metodo empleado para el calculo de la distancia de Mahalanobis robusta. Solo debe usarse si d1='Mahalanobis_Robust'.  Las tres opciones disponibles para Method si se usa la funcion Matrix_Dist_Mahalanobis_Robust son 'trimmed', 'winsorized' y 'MAD'. Para mas detalles ver el capitulo 7 de este trabajo.
     alpha : debe ser un numero en el intervalo cerrado [0,1]. Solo es necesario especificarlo si d1='Mahalanobis_Robust' y Method es 'trimmed' o 'winsorized'. Es el parametro alpha usado por la funcion Matrix_Dist_Mahalanobis_Robust  para calcular las distancias de Mahalanobis robusta con los metodos trimmed y winsorized. Para mas detalles ver el capitulo 7 de este trabajo.
     q : solo debe especificarse si d1='Minkowski'. Es el parametro que aparece en la definicion de la distancia de Minkowski y es usado por la funcion Matrix_Dist_Minkowski presentada en la seccion anterior.
     Related_Metric_Scaling : toma como valor True o False. Si es False la clase calcula la matriz de distancias de Gower generalizada, con el resto de parametros especificados. Si es True calcula la matriz de distancias RMS con el resto de parametros especificados.
     tol : Solo debe ser especificado si Related_Metric_Scaling=False=True. Debe ser un numero no negativo. Se emplea en algunos procedimientos para comprobar condiciones de manera aproximada.
     d : Debe ser un numero mayor o igual que 2. Solo debe especificarse si Related_Metric_Scaling=False=True. Es el parametro que aparece en la definicion de omega, parametro que aparece en la transformacion que se utiliza para el caso en el que G_h no es semidefinida positiva. Para ver mas detalles puede verse la seccion 6.1.3 de este trabajo.

    Devuelve (outputs)
    -------
    D: la matriz de distancias de Gower generalizada (Related_Metric_Scaling=False) o RMS (Related_Metric_Scaling=True) entre las observaciones (filas) del data-frame Data, teniendo en cuenta el resto de parametros especificados.
    D_2: la matriz de distancias al cuadrado de Gower generalizada (Related_Metric_Scaling=False) o RMS (Related_Metric_Scaling=True) entre las observaciones (filas) del data-frame Data,  teniendo en cuenta el resto de parametros especificados
    
    Comentarios 
    -------
    Para un correcto funcionamiento de la clase, deben definirse prefiamente funciones que calculen matrices de distancia, tales como las que se han presentado en las anteriores secciones. Un requerimiento sintactico de la clase es que dichas funciones tengan como nombre Matrix_Dist_x, donde x debe ser el nombre de la distancia que sera introducido en d1, d2 o d3. Por ejemplo, si d2='Jaccard', para que la clase funcione correctamente debe de haber una funcion llamada Matrix_Dist_Jaccard definida en nuestro entorno de trabajo, la cual debe calcular la matriz de distancias de Jaccard para un data-frame pandas o array numpy pasado como parametro.
    """

    
    def __init__(self,Data,p1,p2,p3,d1,d2,d3,q=None,epsilon=None,Method=None,alpha=None,n_iters=20):
        # Funcion que inicializa la clase. Se inicializan la mayoria de los parametros.
        self.Data = Data
        self.p1 = p1 ; self.p2 = p2 ; self.p3 = p3
        self.d1 = d1 ; self.d2 = d2 ; self.d3 = d3
        self.q = q  
        self.Method = Method ; self.epsilon = epsilon 
        self.alpha = alpha ; self.n_iters = n_iters 
        self.n = len(Data)
        self.Quant_Data = Data.iloc[:,0:p1] 
        self.Binary_Data = Data.iloc[: , (p1):(p1+p2)]
        self.Multiple_Data = Data.iloc[:,(p1+p2):(p1+p2+p3) ]
        self.Matrix_Dist_d1 = globals()[d1+"_Dist_Matrix"]  
        self.Matrix_Dist_d2 = globals()[d2+"_Dist_Matrix"] 
        self.Matrix_Dist_d3 = globals()[d3+"_Dist_Matrix"]

    def compute(self,Related_Metric_Scaling=False,tol=0.009,d=2):
        # Funcion que calcula la distancia de Gower generalizada (Related_Metric_Scaling=False) o RMS (Related_Metric_Scaling=True). para los parametros especificados en la inicializacion.
        self.Related_Metric_Scaling = Related_Metric_Scaling
        self.tol = tol ; n = self.n ; q = self.q 
        Method = self.Method ; epsilon = self.epsilon 
        alpha = self.alpha ; n_iters = self.n_iters
        d1 = self.d1 
        p1 = self.p1 ; p2 = self.p2 ; p3 = self.p3
        Matrix_Dist_d1 = self.Matrix_Dist_d1 
        Matrix_Dist_d2 = self.Matrix_Dist_d2 
        Matrix_Dist_d3 = self.Matrix_Dist_d3   
        Quant_Data = self.Quant_Data  
        Binary_Data = self.Binary_Data 
        Multiple_Data = self.Multiple_Data
        # Se calculan las matrices de distancias D1, D2 y D3, para las variables cuantitativas, binarias y multiclase, respectivamente. Se contemplan los casos en los que el conjunto de datos no tiene alguno/s de estos tipos.
        if p1 == 0 and p2 != 0 and p3 != 0 : 
            D1 = np.zeros((n,n)) 
            D2 = Matrix_Dist_d2(Binary_Data) 
            D3 = Matrix_Dist_d3(Multiple_Data)
        if p2 == 0 and p1 != 0 and p3 != 0 : 
            if d1 == 'Minkowski' :  
                   D1 = Matrix_Dist_d1(Quant_Data, q)
            elif d1 == 'Robust_Mahalanobis' :  
                   D1 = Matrix_Dist_d1(Quant_Data, Method, epsilon, alpha, n_iters)
            else: 
                   D1 = Matrix_Dist_d1(Quant_Data)
            D2 = np.zeros((n,n)) 
            D3 = Matrix_Dist_d3(Multiple_Data)
        if p3 == 0 and p1 != 0 and p2 != 0 : 
            if d1 == 'Minkowski' :  
                   D1 = Matrix_Dist_d1(Quant_Data, q)
            elif d1 == 'Robust_Mahalanobis' :  
                   D1 = Matrix_Dist_d1(Quant_Data, Method, epsilon, alpha, n_iters)
            else: 
                   D1 = Matrix_Dist_d1(Quant_Data)
            D2 = Matrix_Dist_d2(Binary_Data) 
            D3 = np.zeros((n,n))
        if p1 == 0 and p2 == 0 and p3 != 0 : 
            D1 = np.zeros((n,n)) 
            D2 = np.zeros((n,n)) 
            D3 = Matrix_Dist_d3(Multiple_Data)
        if p1 == 0 and p3 == 0 and p2 != 0 : 
            D1 = np.zeros((n,n)) 
            D2 = Matrix_Dist_d2(Binary_Data) 
            D3 = np.zeros((n,n))
        if p2 == 0 and p3 == 0 and p1 != 0 : 
            if d1 == 'Minkowski' :  
                    D1 = Matrix_Dist_d1(Quant_Data, q)
            elif d1 == 'Robust_Mahalanobis' :   
                    D1 = Matrix_Dist_d1(Quant_Data, Method, epsilon, alpha, n_iters)
            else: 
                    D1 = Matrix_Dist_d1(Quant_Data)
            D2 = np.zeros((n,n)) 
            D3 = np.zeros((n,n))
        if p1 != 0 and p2 != 0 and p3 != 0 : 
            if d1 == 'Minkowski' :  
                    D1 = Matrix_Dist_d1(Quant_Data, q)
            elif d1 == 'Robust_Mahalanobis' :  
                    D1 = Matrix_Dist_d1(Quant_Data, Method, epsilon, alpha, n_iters)
            else: 
                    D1 = Matrix_Dist_d1(Quant_Data)
            D2 = Matrix_Dist_d2(Binary_Data) 
            D3 = Matrix_Dist_d3(Multiple_Data)
        # Una vez calculadas D1, D2 y D3, se calculan las matrices de cuadrados de distancias, aplicando np.square sobre ellas.
        D1_2 = np.square(D1) 
        D2_2 = np.square(D2)  
        D3_2 = np.square(D3)
        # Se define una funcion que calcula la  variabilidad geometrica para una matriz pasada como parametro.
        def var_geom(M):
            n = len(M)
            VG = (1/(2*(n**2)))*np.sum(M)
            return VG
        # Se calcula la variabilidad geometrica de D1_2, D2_2 y D3_2 aplicando la funcion  var_geom.
        VG1 = var_geom(D1_2)  
        VG2 = var_geom(D2_2) 
        VG3 = var_geom(D3_2)
        # Se estandarizan las matrices de distancias al cuadrado (D1_2, D2_2 y D3_2) con la variabilidad geometrica. Se contemplan los casos en los que la variabilidad geometrica es nula, para evitar problemas con la division. Notese que si el conjunto de datos no tiene algun tipo de variables, la variabilidad geometrica para ese tipo es nula, porque la matriz de distancias para ese tipo de variables es una matriz nula, tal y como se ha definido anteriormente el codigo.
        if VG1 == 0 : 
            D1_2_standard = D1_2  
        else : 
            D1_2_standard = D1_2 / VG1
        if VG2 == 0 : 
            D2_2_standard = D2_2  
        else : 
            D2_2_standard = D2_2 / VG2
        if VG3 == 0 : 
            D3_2_standard = D3_2  
        else : 
            D3_2_standard = D3_2 / VG3
        
        # Si Related_Metric_Scaling == False, se calcula la distancia de Gower generalizada usando los elementos antes definidos.
        if Related_Metric_Scaling == False :    
           # Se combinan las matrices de cuadrados de distancias estandarizadas   para obtener la matriz de cuadrados de distancias de Gower generalizada.
           D_2 = D1_2_standard + D2_2_standard + D3_2_standard 
           # Se establecen como cero aquellos valores de la matriz D_2 que son aproximadamente cero, con una tolerancia de 0.005.
           D_2[np.isclose(D_2, 0, atol=0.005)] = 0
           # Se calcula la matriz de distancias de Gower generalizada (D) a partir de la matriz de cuadrados de distancias de Gower generalizada (D_2), aplicando la raiz cuadrada a cada elemento de D_2 con la funcion np.sqrt.
           D = np.sqrt(D_2)
           # Se devuelven como outputs D y D_2.
           return D, D_2

        # Si Related_Metric_Scaling == True, se calcula la distancia de Gower generalizada usando los elementos antes definidos.
        elif Related_Metric_Scaling == True :
            # Se define un vector de unos fila y otro columna.
            ones = np.ones((n, 1)) ; ones_T = np.ones((1, n))
            # Se calcula la matriz de centrado
            H = np.identity(n) - (1/n)*(ones @ ones_T)
            # Se calcula G_1, G_2 y G_3.
            G_1 = -(1/2)*(H @ D1_2_standard @ H) ; G_2 = -(1/2)*(H @ D2_2_standard @ H) ; G_3 = -(1/2)*(H @ D3_2_standard @ H)
            # Se comprueba si G_1, G_2 y G_3 son simetricas o aproximadamanete simetricas (usando una tolerancia tol, que se da como input). Deberian serlo por construccion, salvo que haya algun error en el calculo de alguna de las matrices de distancias (por haber usado una funcion Matrix_Dist_x inadecuada).
            G_1_symmetric = np.allclose(G_1, G_1.T, atol=tol) ; G_2_symmetric = np.allclose(G_2, G_2.T, atol=tol) ; G_3_symmetric = np.allclose(G_3, G_3.T, atol=tol)
            
            # Se calculan los autovalores y autovectores de G_1, G_2 y G_3 usando la funcion  np.linalg.eig. vi es el vector con los autovalores de G_i, mientras que Wi es la matriz con los autovectores de G_i.
            v1, W1 = np.linalg.eig(G_1) ; v2, W2 = np.linalg.eig(G_2) ; v3, W3 = np.linalg.eig(G_3)
            # Al calcular autovalores con np.linalg.eig estos pueden aparecer con parte compleja pese a que esta sea nula o aproximadamente nula, por ello solo se considera la parte real de los autovalores, puesto que en la mayoria de casos la parte compleja es inexistente (nula) o despreciable (aprox. nula).
            v1 = np.real(v1) ; v2 = np.real(v2) ;  v3 = np.real(v3)
            # Se establecen como cero aquellos autovalores que son aproximadamente cero, dada una tolerancia tol fijada por el usuario como input.
            v1[np.isclose(v1, 0, atol=tol)] = 0 ; v2[np.isclose(v2, 0, atol=tol)] = 0 ; v3[np.isclose(v3, 0, atol=tol)] = 0
            # Se comprueba si los autovalores de G_1, G_2 y G_3 son mayores o iguales que cero, es decir, si esas matrices son semidefinidas positivas (SDP).
            G1_SDP = np.all(v1 >= 0) ; G2_SDP = np.all(v2 >= 0) ; G3_SDP = np.all(v3 >= 0)
 
             # Si alguna matriz G_1, G_2 o G_3 no es SDP, se aplica una transformacion sobre ella/s para obtener una version transformada que sea SDP.  
            if  not (G1_SDP and G2_SDP and G3_SDP) : 
                # Si G_1 no es SDP, aplicamos la transformacion exxpuesta en la seccion 6.1.3 sobre G_1. 
                if not G1_SDP :
                    # Se calculan los autovalores de G_1, se toma su parte real, se establecen en cero los que son aproximadamente cero.
                    v1, W1 = np.linalg.eig(G_1) 
                    v1 = np.real(v1) 
                    v1[np.isclose(v1, 0, atol=tol)] = 0
                    # Se crea una lista con los autovalores de G_1 que son negativos (sgnificativamente, es decir, mas alla de la tolerancia tol).
                    v1_neg = [x  for x in v1  if x < 0]
                    print(f'Al calcular {d1} se ha comprobado que G_1 no es semidefinida positiva, y debe serlo. Se le aplicara una transformacion.')
                    print(f'Autovalores negativos de G_1 (primeros 7): {v1_neg[0:7]}')           
                    # Se define el parametro omega de la transformacion, con un parametro d especificado por el usuario y que por defecto es el minimo recomendable, d=2.
                    omega = d*np.abs(np.min(v1))  
                    # Se aplica la transformacion y se obtiene G_1 transformada.
                    D1_2_standard = D1_2_standard + omega*np.ones((n, n)) - omega*np.identity(n)
                    G_1 = -(1/2)*(H @ D1_2_standard @ H)
                    
                   # Se comprueba si G_1 transformada es SDP, lo cual debe serlo siempre que se haya fijado un d >= 2.
                    v1, W1 = np.linalg.eig(G_1) 
                    v1 = np.real(v1) 
                    v1[np.isclose(v1, 0, atol=tol)] = 0
                    G1_SDP = np.all(v1 >= 0)
                    if G1_SDP :
                        print('G_1 ha sido transformada y ahora es SDP') 
                    else :
                       print('G_1 ha sido transformada y aun no es SDP. Debes haber fijado un d inferior a 2')
 
               # Si G_2 no es SDP, aplicamos la transformacion exxpuesta en la seccion 6.1.3 sobre G_2. Mismo procedimiento que el explicado para el caso de G_1.
                if not G2_SDP :
                    v2, W2 = np.linalg.eig(G_2) 
                    v2 = np.real(v2) 
                    v2[np.isclose(v2, 0, atol=tol)] = 0
                    v2_neg = [x  for x in v2  if x < 0]
                    print(f'Al calcular {d2} se ha comprobado que G_2 no es semidefinida positiva, y debe serlo. Se le aplicara una transformacion.')
                    print(f'Autovalores negativos de G_2 (primeros 7): {v2_neg[0:7]}')               
                    omega = d*np.abs(np.min(v2))  
                    D2_2_standard = D2_2_standard + omega*np.ones((n, n)) - omega*np.identity(n)
                    G_2 = -(1/2)*(H @ D2_2_standard @ H)

                    v2, W2 = np.linalg.eig(G_1) 
                    v2 = np.real(v2) 
                    v2[np.isclose(v2, 0, atol=tol)] = 0
                    G2_SDP = np.all(v2 >= 0)
                    if G2_SDP  :
                        print('G_2 ha sido transformada y ahora es SDP') 
                    else :
                       print('G_2 ha sido transformada y aun no es SDP. Debes haber fijado un d inferior a 2')

                # Si G_3 no es SDP, aplicamos la transformacion exxpuesta en la seccion 6.1.3 sobre G_3. Mismo procedimiento que el explicado para el caso de G_1.
                if not G3_SDP :
                    v3, W3 = np.linalg.eig(G_3) 
                    v3 = np.real(v3) 
                    v3[np.isclose(v3, 0, atol=tol)] = 0
                    v3_neg = [x  for x in v3  if x < 0]
                    print(f'Al calcular {d3} se ha comprobado que G_3 no es semidefinida positiva, y debe serlo. Se le aplicara una transformacion.')
                    print(f'Autovalores negativos de G_3 (primeros 7): {v3_neg[0:7]}')               
                    omega = d*np.abs(np.min(v3))  
                    D3_2_standard = D3_2_standard + omega*np.ones((n, n)) - omega*np.identity(n)
                    G_1 = -(1/2)*(H @ D1_2_standard @ H)

                    v3, W3 = np.linalg.eig(G_3) 
                    v3 = np.real(v3) 
                    v3[np.isclose(v3, 0, atol=tol)] = 0
                    G3_SDP = np.all(v3 >= 0)
                    if G3_SDP :
                        print('G_3 ha sido transformada y ahora es SDP') 
                    else :
                       print('G_3 ha sido transformada y aun no es SDP. Debes haber fijado un d inferior a 2')
   
           # Si G_1, G_2 o G_3 no son simentricas, se informa de ello al usuario, puesto que deberian serlo.
            elif (G_1_symmetric and G_2_symmetric and G_3_symmetric) :
                if not G_1_symmetric : 
                        'G_1 deberia ser simetrica, debe haber algun error en las matriz de distancia D1.',
                elif not G_2_symmetric : 
                        'G_2 deberia ser simetrica, debe haber algun error en las matriz de distancia D2.',
                elif not G_3_symmetric : 
                        'G_3 deberia ser simetrica, debe haber algun error en las matriz de distancia D3.'

         # Se aplica la descomposicion en valores singulares (SVD) sobre G_1, G_2 y G_3, y se calcula la raiz cuadrada de G_1, G_2 y G_3.
            U1, S1, V1 = np.linalg.svd(G_1) 
            U2, S2, V2 = np.linalg.svd(G_2)   
            U3, S3, V3 = np.linalg.svd(G_3)
            # Calculo de las raices cuadradas de G_1, G_2 y G_3
            sqrtG1 = U1 @ np.diag(np.sqrt(S1)) @ V1 
            sqrtG2 = U2 @ np.diag(np.sqrt(S2)) @ V2 
            sqrtG3 = U3 @ np.diag(np.sqrt(S3)) @ V3
 
          # Se calcula la matriz G definida en RMS (ver seccion 6.1).  
            G = G_1 + G_2 + G_3 - (1/3)*(sqrtG1@sqrtG2 + sqrtG1@sqrtG3 + sqrtG2@sqrtG1 + sqrtG2@sqrtG3 + sqrtG3@sqrtG1 + sqrtG3@sqrtG2)
          # Se calcula la matriz de cuadrados de distancia RMS asi como la matriz de distancias RMS.
            # Se calcula g como el vector columna que contene la diagonal principal de G
            g = np.diag(G) 
            g =  np.reshape(g, (len(g), 1))  
            g_T = np.reshape(g, (1, len(g)))   
            # Se calcula la matriz de cuadrados de distancias RMS.             
            D_2 = g @ ones_T + ones @ g_T - 2*G
            # Se establecen como cero aquellas distancias que son aproximadamente cero, para la tolerancia 0.001.
            D_2[np.isclose(D_2, 0, atol=0.001)] = 0
            # Se calcula la matriz de distancias RMS aplicando la funcion np.sqrt sobre D_2, la cual aplica la raiz cuadrada a cada elemento de la matriz pasada como parametro.
            D = np.sqrt(D_2)
 
        # Se devuelven como outputs D y D_2.
        return D, D_2


## Bibliography

# Albarrán, I.,  P. Alonso, and A. Grané  “Profile Identification via Weighted Related Metric Scaling: An Application to Dependent Spanish Children.” Journal of the Royal Statistical Society. Series A, Statistics in Society 178, no. 3 (2015): 593–618. https://doi.org/10.1111/rssa.12084stex:B88856BB540BB0134A72028E02D7B00CBED08217.

# Cuadras, C. M., and J. Fortiana. “Chapter 25 - Visualizing Categorical Data with Related Metric Scaling.” In Visualization of Categorical Data, 365–76. Academic Press, 1998. https://doi.org/10.1016/B978-012299045-8/50028-0.

# Devlin, S. J., R. Gnanadesikan, and J. R. Kettenring. “Robust Estimation and Outlier Detection with Correlation Coefficients.” Biometrika 62, no. 3 (1975): 531–45. https://doi.org/10.1093/biomet/62.3.531.

# Grané, A.,  Manzi G. and S. Salini. "Smart Visualization of Mixed Data". Stats   n.º 4 (2021): 472–485. https://doi.org/10.3390/stats4020029.

# Gower, J. C. “A General Coefficient of Similarity and Some of Its Properties.” Biometrics  27, no. 4 (1971): 857–71.  https://doi.org/10.2307/2528823.

# Gnanadesikan, R. Methods for Statistical Data Analysis of Multivariate Observations. 2nd ed. New York  etc.: : John Wiley and Sons, 1997.



