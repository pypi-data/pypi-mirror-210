import numpy as np
import META_TOOLBOX.META_CO_LIBRARY as META_CO

def MUTATION_OPERATOR_DE_RAND_1(OF_FUNCTION, NULL_DIC, F_FACTOR, X_GAMA, X_BETA, X_ALFA, D, X_L, X_U):
    """
    This function creates a new solution using Differencial Evolution movement.

    See documentation in https://wmpjrufg.github.io/META_TOOLBOX/DE.html
    """
    # Start internal variables
    V_TI = []

    # Particle Differencial Evolution movement (Normal distribution)
    for I in range(D):
        V_I = X_GAMA[I] + F_FACTOR * (X_ALFA[I] - X_BETA[I])
        V_TI.append(V_I)

    # Check boundes
    V_TI = META_CO.CHECK_INTERVAL_01(V_TI, X_L, X_U)

    # Evaluation of the objective function and fitness
    OF_TI = OF_FUNCTION(V_TI, NULL_DIC)
    FIT_TI = META_CO.FIT_VALUE(OF_TI)
    NEOF = 1

    return V_TI, OF_TI, FIT_TI, NEOF

def BINOMIAL_CROSSOVER_OPERATOR(OF_FUNCTION, NULL_DIC, V, X_T0I, CR, D, X_L, X_U):
    """
    """
    # Start internal variables
    U_TI = []

    # Movement
    for I_COUNT in range(D):
        if np.random.random() < CR:
            U_TI.append(V[I_COUNT])
        else:
            U_TI.append(X_T0I[I_COUNT])
    
    # Check boundes
    U_TI = META_CO.CHECK_INTERVAL_01(U_TI, X_L, X_U) 
    
    # Evaluation of the objective function and fitness
    OF_TI = OF_FUNCTION(U_TI, NULL_DIC)
    FIT_TI = META_CO.FIT_VALUE(OF_TI)
    NEOF = 1
    
    return U_TI, OF_TI, FIT_TI, NEOF