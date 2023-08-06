import numpy as np
import META_TOOLBOX.META_CO_LIBRARY as META_CO

def HC_MOVEMENT(OF_FUNCTION, NULL_DIC, X_IOLD, X_L, X_U, D, SIGMA):
    """ 
    This function creates a new solution using Hill Climbing movement.

    See documentation in https://wmpjrufg.github.io/META_TOOLBOX/HC.html
    """
    # Start internal variables
    X_INEW = []
    OF_INEW = 0
    FIT_INEW = 0
    
    # Particle Hill Climbing movement (Normal distribution)
    for I in range(D):
        MEAN_VALUE = X_IOLD[I]
        SIGMA_VALUE = abs(MEAN_VALUE * SIGMA)
        NEIGHBOR = np.random.normal(MEAN_VALUE, SIGMA_VALUE, 1)
        X_INEW.append(NEIGHBOR[0])
    
    # Check bounds
    X_INEW = META_CO.CHECK_INTERVAL_01(X_INEW, X_L, X_U) 
    
    # Evaluation of the objective function and fitness
    OF_INEW = OF_FUNCTION(X_INEW, NULL_DIC)
    FIT_INEW = META_CO.FIT_VALUE(OF_INEW)
    NEOF = 1
    
    return X_INEW, OF_INEW, FIT_INEW, NEOF