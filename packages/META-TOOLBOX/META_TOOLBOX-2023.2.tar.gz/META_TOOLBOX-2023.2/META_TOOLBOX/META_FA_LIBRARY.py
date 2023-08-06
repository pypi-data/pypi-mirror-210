import numpy as np
import META_TOOLBOX.META_CO_LIBRARY as META_CL

# CHAOTIC SEARCH
def CHAOTIC_SEARCH(OF_FUNCTION, ITER, X_BEST, OF_BEST, FIT_BEST, N_CHAOTICSEARCHS, ALPHA_CHAOTIC, D, N_ITER, X_L, X_U, NULL_DIC):
    # INITIALIZATION VARIABLES
    K = N_CHAOTICSEARCHS
    CH = []
    X_BESTNEW = X_BEST
    OF_BESTNEW = OF_BEST
    FIT_BESTNEW = FIT_BEST
    # CSI UPDATE
    CSI = (N_ITER - ITER + 1) / N_ITER
    # CHAOTIC SEARCHS
    for I_COUNT in range(0, K):
        CH_XBEST = np.zeros((1, D))
        X_BESTTEMPORARY = np.zeros((1, D))
        if I_COUNT == 0:
            # CHAOTIC UPDATE
            CH.append(np.random.random())
        else:
            # CHAOTIC UPDATE POSITION, OF AND FIT
            CH.append(ALPHA_CHAOTIC * CH[I_COUNT - 1] * (1 - CH[I_COUNT - 1]))
        # CREATING THE CHAOTIC POSITION
        for J_COUNT in range(D): 
            CH_XBEST[0, J_COUNT] = X_L[J_COUNT] + (X_U[J_COUNT] - X_L[J_COUNT]) * CH[I_COUNT]
            # print('aqui', type(X_BESTNEW), X_BESTNEW)
            X_BESTTEMPORARY[0, J_COUNT] = (1 - CSI) * X_BESTNEW[J_COUNT] + CSI * CH_XBEST[0, J_COUNT]
        X_BESTTEMPORARY[0, :] = META_CL.CHECK_INTERVAL_01(X_BESTTEMPORARY[0, :], X_L, X_U) 
        OF_BESTTEMPORARY = OF_FUNCTION(X_BESTTEMPORARY[0, :], NULL_DIC)
        FIT_BESTTEMPORARY = META_CL.FIT_VALUE(OF_BESTTEMPORARY)
        # STORING BEST VALUE
        if FIT_BESTTEMPORARY > FIT_BEST:
            X_BESTNEW = X_BESTTEMPORARY[0, :]
            OF_BESTNEW = OF_BESTTEMPORARY
            FIT_BESTNEW = FIT_BESTTEMPORARY
    return X_BESTNEW, OF_BESTNEW, FIT_BESTNEW

# CALCULATION OF THE DISCRIMINATING FACTOR OF THE MALE AND FEMALE FIREFLIES POPULATION
def DISCRIMINANT_FACTOR_MALE_MOVIMENT(FIT_XI, FIT_YK):
    """ COMENTÁRIO NATIVO VOU FAZER"""
    # COMPARISON OF FIREFLY BRIGHTNESS
    if FIT_XI > FIT_YK:
        D_1 = 1
    else:
        D_1 = -1
    return D_1

# DETERMINAÇÃO DO FATOR DE ATRATIVIDADE BETA
def ATTRACTIVENESS_FIREFLY_PARAMETER(BETA_0, GAMMA, X_I, X_J, D):
    """
    This function calculates distance between X_I and X_J fireflies.

    Input:
    BETA_0  | Attractiveness at r = 0                             | Float
    GAMMA   | Light absorption coefficient  1 / (X_U - X_L) ** M  | Py list[D]
    X_I     | I Firefly                                           | Py list[D]
    X_J     | J Firefly                                           | Py list[D]
    D       | Problem dimension                                   | Integer

    Output:
    BETA    | Attractiveness                                      | Py list[D]
    """
    AUX = 0
    
    # Firefly distance
    for I_COUNT in range(D):
        AUX += (X_I[I_COUNT] - X_J[I_COUNT]) ** 2
    R_IJ = np.sqrt(AUX)
    
    # Beta attractiveness
    BETA = []
    for J_COUNT in range(D):
        BETA.append(BETA_0 * np.exp(- GAMMA[J_COUNT] * R_IJ))
    
    return BETA

# MOVIMENTO DE UM VAGALUME TRADICIONAL
def FIREFLY_MOVEMENT(OF_FUNCTION, X_T0I, X_J, BETA, ALPHA, SCALING, D, X_L, X_U, NULL_DIC):
    """
    This function creates a new solution using FA movement algorithm.

    Input:
    OF_FUNCTION  | External def user input this function in arguments       | Py function
    X_T0I        | Design variable I particle before movement               | Py list[D]
    X_J          | J Firefly                                                | Py list[D]
    BETA         | Attractiveness                                           | Py list[D]
    ALPHA        | Randomic factor                                          | Float
    D            | Problem dimension                                        | Integer
    X_L          | Lower limit design variables                             | Py list[D]
    X_U          | Upper limit design variables                             | Py list[D]
    NULL_DIC     | Empty variable for the user to use in the obj. function  | ? 
    
    Output:
    X_T1I        | Design variable I particle after movement                | Py list[D]
    OF_T1I       | Objective function X_T1I (new particle)                  | Float
    FIT_T1I      | Fitness X_T1I (new particle)                             | Float
    NEOF         | Number of objective function evaluations                 | Integer
    """
    # Start internal variables
    X_T1I = []
    OF_T1I = 0
    FIT_T1I = 0
    for I_COUNT in range(D):
        EPSILON_I = np.random.random() - 0.50
        if SCALING:
            S_D = X_U[I_COUNT] - X_L[I_COUNT]
        else:
            S_D = 1
        NEW_VALUE = X_T0I[I_COUNT] + BETA[I_COUNT] * (X_J[I_COUNT] - X_T0I[I_COUNT]) + ALPHA * S_D * EPSILON_I
        X_T1I.append(NEW_VALUE) 
    # Check boundes
    X_T1I = META_CL.CHECK_INTERVAL_01(X_T1I, X_L, X_U) 
    # Evaluation of the objective function and fitness
    OF_T1I = OF_FUNCTION(X_T1I, NULL_DIC)
    FIT_T1I = META_CL.FIT_VALUE(OF_T1I)
    NEOF = 1
    return X_T1I, OF_T1I, FIT_T1I, NEOF

# MALE FIREFLY MOVEMENT
def MALE_FIREFLY_MOVEMENT(OF_FUNCTION, X_MALECURRENTI, FIT_MALECURRENTI, Y_FEMALECURRENTK, FIT_FEMALECURRENTK, Y_FEMALECURRENTJ, FIT_FEMALECURRENTJ, BETA_0, GAMMA, D, X_L, X_U, NULL_DIC):
    """ COMENTÁRIO NATIVO VOU FAZER"""
    # INITIALIZATION VARIABLES
    SECOND_TERM = []
    THIRD_TERM = []
    X_MALENEWI = []
    # DISCRIMINANT D FACTOR
    D_1 = DISCRIMINANT_FACTOR_MALE_MOVIMENT(FIT_MALECURRENTI, FIT_FEMALECURRENTK)
    D_2 = DISCRIMINANT_FACTOR_MALE_MOVIMENT(FIT_MALECURRENTI, FIT_FEMALECURRENTJ)
    # ATTRACTIVENESS AMONG FIREFLIES
    BETA_1 = ATTRACTIVENESS_FIREFLY_PARAMETER(BETA_0, GAMMA, X_MALECURRENTI, Y_FEMALECURRENTK, D)
    BETA_2 = ATTRACTIVENESS_FIREFLY_PARAMETER(BETA_0, GAMMA, X_MALECURRENTI, Y_FEMALECURRENTJ, D)
    # LAMBDA AND MU RANDOM PARAMETERS
    LAMBDA = np.random.random()
    MU = np.random.random()
    for I_COUNT in range(D):
        SECOND_TERM.append(D_1 * BETA_1[I_COUNT] * LAMBDA * (Y_FEMALECURRENTK[I_COUNT] - X_MALECURRENTI[I_COUNT]))
        THIRD_TERM.append(D_2 * BETA_2[I_COUNT] * MU * (Y_FEMALECURRENTJ[I_COUNT] - X_MALECURRENTI[I_COUNT]))
    # UPDATE FEMALE POSITION, OF AND FIT
    for J_COUNT in range(D):
        X_MALENEWI.append(X_MALECURRENTI[J_COUNT] + SECOND_TERM[J_COUNT] + THIRD_TERM[J_COUNT])
    X_MALENEWI = META_CL.CHECK_INTERVAL_01(X_MALENEWI, X_L, X_U) 
    OF_MALENEWI = OF_FUNCTION(X_MALENEWI, NULL_DIC)
    FIT_MALENEWI = META_CL.FIT_VALUE(OF_MALENEWI)
    return X_MALENEWI, OF_MALENEWI, FIT_MALENEWI

# FEMALE FIREFLY MOVEMENT
def FEMALE_FIREFLY_MOVEMENT(OF_FUNCTION, Y_FEMALECURRENTI, X_MALEBEST, FIT_MALEBEST, BETA_0, GAMMA, D, X_L, X_U, NULL_DIC):
    """ COMENTÁRIO NATIVO VOU FAZER"""
    # INITIALIZATION VARIABLES
    Y_FEMALENEWI = []
    # ATTRACTIVENESS AMONG FIREFLIES (Y_FEMALE AND X_BEST)
    BETA = ATTRACTIVENESS_FIREFLY_PARAMETER(BETA_0, GAMMA, Y_FEMALECURRENTI, X_MALEBEST, D)
    # PHI RANDOM PARAMETER
    PHI = np.random.random()
    # UPDATE FEMALE POSITION, OF AND FIT
    for I_COUNT in range(D):
        Y_FEMALENEWI.append(Y_FEMALECURRENTI[I_COUNT] + BETA[I_COUNT] * PHI * (X_MALEBEST[I_COUNT] - Y_FEMALECURRENTI[I_COUNT]))
    Y_FEMALENEWI = META_CL.CHECK_INTERVAL(Y_FEMALENEWI, X_L, X_U)
    OF_FEMALENEWI = OF_FUNCTION(Y_FEMALENEWI, NULL_DIC)
    FIT_FEMALENEWI = META_CL.FIT_VALUE(OF_FEMALENEWI)
    return Y_FEMALENEWI, OF_FEMALENEWI, FIT_FEMALENEWI

# FATOR DE ABSORÇÃO DE LUZ GAMMA
def GAMMA_ASSEMBLY(X_L, X_U, D, M):
    """
    This function calculates the light absorption coefficient.

    Input:
    X_L    | Lower limit design variables                        | Py list[D]
    X_U    | Upper limit design variables                        | Py list[D]
    D      | Problem dimension                                   | Integer
    M      | Exponent value in distance                          | Float  

    Output:
    GAMMA  | Light absorption coefficient  1 / (X_U - X_L) ** M  | Py list[D] 
    """
    
    GAMMA = []
    for I_COUNT in range(D):
        DISTANCE = X_U[0] - X_L[0]
        GAMMA.append(1 / DISTANCE ** M)
    
    return GAMMA

def GDFA_MALE_MOVEMENT(OF_FUNCTION, X_T0I, Y_T0J, Y_T0K, GAMMA, BETA_0, D, X_L, X_U, NULL_DIC):
    """
    This function creates a new solution using FA movement algorithm.

    Input:
    OF_FUNCTION  | External def user input this function in arguments       | Py function
    X_T0I        | Design variable I particle before movement               | Py list[D]
    X_J          | J Firefly                                                | Py list[D]
    BETA         | Attractiveness                                           | Py list[D]
    ALPHA        | Randomic factor                                          | Float
    D            | Problem dimension                                        | Integer
    X_L          | Lower limit design variables                             | Py list[D]
    X_U          | Upper limit design variables                             | Py list[D]
    NULL_DIC     | Empty variable for the user to use in the obj. function  | ? 
    
    Output:
    X_T1I        | Design variable I particle after movement                | Py list[D]
    OF_T1I       | Objective function X_T1I (new particle)                  | Float
    FIT_T1I      | Fitness X_T1I (new particle)                             | Float
    NEOF         | Number of objective function evaluations                 | Integer
    """

    # Start internal variables
    X_T1I = []
    OF_T1I = 0
    FIT_T1I = 0
    BETA_J = ATTRACTIVENESS_FIREFLY_PARAMETER(BETA_0, GAMMA, X_T0I, Y_T0J, D)
    BETA_K = ATTRACTIVENESS_FIREFLY_PARAMETER(BETA_0, GAMMA, X_T0I, Y_T0K, D)
    
    #D_1 
    if Y_T0J < X_T0I:
        D_1 = 1
    else:
        D_1 = -1
    #D_2
    if Y_T0K < X_T0I:
        D_2 = 1
    else:
        D_2 = -1

    for I_COUNT in range(D):
        LAMBDA = np.random.random()
        MICRO = np.random.random()
        NEW_VALUE = X_T0I[I_COUNT] + D_1 * BETA_J[I_COUNT] * LAMBDA * (Y_T0J[I_COUNT] - X_T0I[I_COUNT])   
        AUX_VALUE =  D_2 * BETA_K[I_COUNT] * MICRO * (Y_T0K[I_COUNT] - X_T0I[I_COUNT])    
        NEW_VALUE += AUX_VALUE
        X_T1I.append(NEW_VALUE) 
    # Check boundes
    X_T1I = META_CL.CHECK_INTERVAL_01(X_T1I, X_L, X_U) 
    # Evaluation of the objective function and fitness
    OF_T1I = OF_FUNCTION(X_T1I, NULL_DIC)
    FIT_T1I = META_CL.FIT_VALUE(OF_T1I)
    NEOF = 1
    return X_T1I, OF_T1I, FIT_T1I, NEOF
def GDFA_FEMALE_MOVEMENT(OF_FUNCTION, X_T0I, Y_T0J, Y_T0K, GAMMA, BETA_0, D, X_L, X_U, NULL_DIC):
    """
    This function creates a new solution using FA movement algorithm.

    Input:
    OF_FUNCTION  | External def user input this function in arguments       | Py function
    X_T0I        | Design variable I particle before movement               | Py list[D]
    X_J          | J Firefly                                                | Py list[D]
    BETA         | Attractiveness                                           | Py list[D]
    ALPHA        | Randomic factor                                          | Float
    D            | Problem dimension                                        | Integer
    X_L          | Lower limit design variables                             | Py list[D]
    X_U          | Upper limit design variables                             | Py list[D]
    NULL_DIC     | Empty variable for the user to use in the obj. function  | ? 
    
    Output:
    X_T1I        | Design variable I particle after movement                | Py list[D]
    OF_T1I       | Objective function X_T1I (new particle)                  | Float
    FIT_T1I      | Fitness X_T1I (new particle)                             | Float
    NEOF         | Number of objective function evaluations                 | Integer
    """

    # Start internal variables
    X_T1I = []
    OF_T1I = 0
    FIT_T1I = 0
    BETA_J = ATTRACTIVENESS_FIREFLY_PARAMETER(BETA_0, GAMMA, X_T0I, Y_T0J, D)
    BETA_K = ATTRACTIVENESS_FIREFLY_PARAMETER(BETA_0, GAMMA, X_T0I, Y_T0K, D)
    
    #TENHO QUE MEXER AINDA
    #D_1 
    if Y_T0J < X_T0I:
        D_1 = 1
    else:
        D_1 = -1
    #D_2
    if Y_T0K < X_T0I:
        D_2 = 1
    else:
        D_2 = -1

    for I_COUNT in range(D):
        LAMBDA = np.random.random()
        MICRO = np.random.random()
        NEW_VALUE = X_T0I[I_COUNT] + D_1 * BETA_J[I_COUNT] * LAMBDA * (Y_T0J[I_COUNT] - X_T0I[I_COUNT])   
        AUX_VALUE =  D_2 * BETA_K[I_COUNT] * MICRO * (Y_T0K[I_COUNT] - X_T0I[I_COUNT])    
        NEW_VALUE += AUX_VALUE
        X_T1I.append(NEW_VALUE) 
    # Check boundes
    X_T1I = META_CL.CHECK_INTERVAL_01(X_T1I, X_L, X_U) 
    # Evaluation of the objective function and fitness
    OF_T1I = OF_FUNCTION(X_T1I, NULL_DIC)
    FIT_T1I = META_CL.FIT_VALUE(OF_T1I)
    NEOF = 1
    return X_T1I, OF_T1I, FIT_T1I, NEOF




#   /$$$$$$  /$$$$$$$  /$$$$$$$$ /$$$$$$$$       /$$$$$$$$ /$$$$$$$$  /$$$$$$  /$$   /$$ /$$   /$$  /$$$$$$  /$$        /$$$$$$   /$$$$$$  /$$$$$$ /$$$$$$$$  /$$$$$$ 
#  /$$__  $$| $$__  $$| $$_____/| $$_____/      |__  $$__/| $$_____/ /$$__  $$| $$  | $$| $$$ | $$ /$$__  $$| $$       /$$__  $$ /$$__  $$|_  $$_/| $$_____/ /$$__  $$
# | $$  \__/| $$  \ $$| $$      | $$               | $$   | $$      | $$  \__/| $$  | $$| $$$$| $$| $$  \ $$| $$      | $$  \ $$| $$  \__/  | $$  | $$      | $$  \__/
# | $$ /$$$$| $$$$$$$/| $$$$$   | $$$$$            | $$   | $$$$$   | $$      | $$$$$$$$| $$ $$ $$| $$  | $$| $$      | $$  | $$| $$ /$$$$  | $$  | $$$$$   |  $$$$$$ 
# | $$|_  $$| $$____/ | $$__/   | $$__/            | $$   | $$__/   | $$      | $$__  $$| $$  $$$$| $$  | $$| $$      | $$  | $$| $$|_  $$  | $$  | $$__/    \____  $$
# | $$  \ $$| $$      | $$      | $$               | $$   | $$      | $$    $$| $$  | $$| $$\  $$$| $$  | $$| $$      | $$  | $$| $$  \ $$  | $$  | $$       /$$  \ $$
# |  $$$$$$/| $$      | $$$$$$$$| $$$$$$$$         | $$   | $$$$$$$$|  $$$$$$/| $$  | $$| $$ \  $$|  $$$$$$/| $$$$$$$$|  $$$$$$/|  $$$$$$/ /$$$$$$| $$$$$$$$|  $$$$$$/
#  \______/ |__/      |________/|________/         |__/   |________/ \______/ |__/  |__/|__/  \__/ \______/ |________/ \______/  \______/ |______/|________/ \______/ 