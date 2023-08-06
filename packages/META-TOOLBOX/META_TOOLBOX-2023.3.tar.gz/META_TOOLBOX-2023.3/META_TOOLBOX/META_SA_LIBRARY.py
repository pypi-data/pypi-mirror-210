import numpy as np
import META_TOOLBOX.META_HC_LIBRARY as META_HC

def START_TEMPERATURE(OF_FUNCTION, NULL_DIC, N_POP, D, X_L, X_U, X, OF, SIGMA):
    """ 
    This function calculates the initial temperature in function of a probability of acceptance of 50% of the initial solutions.  

    Input:
    OF_FUNCTION        | External def user input this function in arguments           | Py function
    N_POP              | Number of population                                         | Integer
    D                  | Problem dimension                                            | Integer
    X                  | Design variables                                             | Py Numpy array[N_POP x D]
    X_L                | Lower limit design variables                                 | Py list[D]
    X_U                | Upper limit design variables                                 | Py list[D]
    OF                 | All objective function values                                | Py Numpy array[N_POP x 1]
    SIGMA              | Standard deviation the normal distribution in percentage     | Float
    TEMP               | Initial temperature or automatic temperature value that has  | Float
                       | an 80% probability of accepting the movement of particles    |
    STOP_CONTROL_TEMP  | Stop criteria about initial temperature try                  | Float
                       | or automatic value = 1000                   
        
    Output:
    T_INITIAL          | Initial temperature SA algorithm                             | Float
    """
    
    # Atiqullah, M. M. (2004). An Efficient Simple Cooling Schedule for Simulated Annealing. Lecture Notes in Computer Science, 396–404. doi:10.1007/978-3-540-24767-8_41 
    T_0TRIAL = []
    TRIAL = 10

    # Population movement 
    for POP in range(N_POP):

        DELTAC = []
        
        # Trial
        for I in range(TRIAL):
            
            # Simulated Annealing particle movement (Same Hill Climbing movement)
            X_ITEMP, OF_ITEMP, FIT_ITEMP, NEOF = META_HC.HC_MOVEMENT(OF_FUNCTION, NULL_DIC, X[POP, :], X_L, X_U, D, SIGMA) 

            # Energy
            AUX = np.abs(OF_ITEMP - OF[POP, 0])
            DELTAC.append(AUX)

        # Total energy
        DELTAC_MEAN = np.mean(DELTAC)
        DELTAC_STD = np.std(DELTAC)
        
        # Save temperature
        AUX = - (DELTAC_MEAN + 3 * DELTAC_STD) / np.log(0.5)
        T_0TRIAL.append(AUX)

    # Initital temperature
    T_0 = np.max(T_0TRIAL)
    
    return T_0