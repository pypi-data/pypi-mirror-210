import numpy as np
import pandas as pd

def INITIAL_POPULATION_01(N_POP, D, X_L, X_U):
    """ 
    This function initializes the population randomically between the limits X_L and X_U.

    See documentation in https://wmpjrufg.github.io/META_TOOLBOX/CO.html
    """
    
    X_NEW = np.zeros((N_POP, D))

    for I in range(N_POP):
        for J in range(D):
            RANDON_NUMBER = np.random.random()
            X_NEW[I, J] = X_L[J] + (X_U[J] - X_L[J]) * RANDON_NUMBER
    
    return X_NEW

def CHECK_INTERVAL_01(X_IOLD, X_L, X_U):
    """
    This function checks if a design variable is out of the limits established X_L and X_U.

    See documentation in https://wmpjrufg.github.io/META_TOOLBOX/CO.html
    """
    
    X_INEW = np.clip(X_IOLD, X_L, X_U)
    
    return X_INEW

def FIT_VALUE(OF_VALUEI):
    """ 
    This function calculates the fitness of a value of the objective function.

    See documentation in https://wmpjrufg.github.io/META_TOOLBOX/CO.html
    """
    # Positive OF
    if OF_VALUEI >= 0:
        FIT_VALUEI = 1 / (1 + OF_VALUEI)
    # Negative OF
    elif OF_VALUEI < 0:
        FIT_VALUEI = 1 + abs(OF_VALUEI)
    
    return FIT_VALUEI

def BEST_VALUES(X, OF, FIT, N_POP):
    """ 
    This function determines the best and worst particle. It also determines the average value (OF and FIT) of the population.

    See documentation in https://wmpjrufg.github.io/META_TOOLBOX/CO.html
    """
    
    # Best and worst ID in population
    SORT_POSITIONS = np.argsort(OF.T)
    BEST_POSITION = SORT_POSITIONS[0, 0]
    WORST_POSITION = SORT_POSITIONS[0, N_POP - 1]

    # Global best values
    X_BEST = X[BEST_POSITION, :]
    OF_BEST = OF[BEST_POSITION, 0]
    FIT_BEST = FIT[BEST_POSITION, 0]
    
    # Global worst values
    X_WORST = X[WORST_POSITION, :]
    OF_WORST = OF[WORST_POSITION, 0]
    FIT_WORST = FIT[WORST_POSITION, 0]
    
    # Average values
    OF_AVERAGE = np.mean(OF)
    FIT_AVERAGE = np.mean(FIT)

    return BEST_POSITION, WORST_POSITION, X_BEST, X_WORST, OF_BEST, OF_WORST, FIT_BEST, FIT_WORST, OF_AVERAGE, FIT_AVERAGE

def PROGRESS_BAR(REP, TOTAL, PREFIX = 'Progress:', SUFFIX = 'Complete', DECIMALS = 1, LENGTH = 50, FILL = '█', PRINT_END = "\r"):
    """
    This function create terminal progress bar.
    
    Input:
    REP        | Current iteration (required)                     | Integer
    TOTAL      | Total iterations (required)                      | Integer
    PREFIX     | Prefix string                                    | String
    SUFFIX     | Suffix string                                    | String
    DECIMALS   | Positive number of decimals in percent complete  | Integer
    LENGTH     | Character length of bar                          | Integer
    FILL       | Bar fill character                               | String
    PRINT_END  | End character (e.g. "\r", "\r\n")                | String
    
    Output:
    N/A
    """
    
    # Progress bar
    PERCENT = ("{0:." + str(DECIMALS) + "f}").format(100 * (REP / float(TOTAL)))
    FILLED_LENGTH = int(LENGTH * REP // TOTAL)
    BAR = FILL * FILLED_LENGTH + '-' * (LENGTH - FILLED_LENGTH)
    print(f'\r{PREFIX} |{BAR}| {PERCENT}% {SUFFIX}', end = PRINT_END)
    
    # Print new line on complete
    if REP == TOTAL: 
        print()
    
    return

def SUMMARY_ANALYSIS(BEST_REP, N_REP, N_ITER):
    """ 
    This function presents a written summary of the best simulation. 

    Input:
    BEST_REP         | Best population results by repetition                            | Py dictionary
                     |   Dictionary tags                                                |
                     |     'X_POSITION'    = Design variables by iteration              | Py Numpy array[N_ITER + 1 x D]
                     |     'OF'            = Obj function value by iteration            | Py Numpy array[N_ITER + 1 x 1]
                     |     'FIT'           = Fitness value by iteration                 | Py Numpy array[N_ITER + 1 x 1]
                     |     '??_PARAMETERS' = Algorithm parametrs                        | Py Numpy array[N_ITER + 1 x 1]
                     |     'NEOF'          = Number of objective function evaluations   | Py Numpy array[N_ITER + 1 x 1]
                     |     'ID_PARTICLE'   = ID best particle by iteration              | Integer 
    N_REP            | Number of repetitions                                            | Integer
    N_ITER           | Number of iterations                                             | Integer

    Output:
    STATUS_PROCEDURE | Process repetition ID - from lowest OF value to highest OF value | Py list[N_REP]
    """ 
    
    # Start reserved space for repetitions
    OF_MINVALUES = []
    
    # Checking which is the best process 
    for I_COUNT in range(N_REP):
        ID = I_COUNT
        OF_MIN = BEST_REP[ID]['OF'][N_ITER]
        OF_MINVALUES.append(OF_MIN)
    STATUS_PROCEDURE = np.argsort(OF_MINVALUES)    
    
    return STATUS_PROCEDURE

def EXCEL_WRITER_ITERATION(NAME, D, DATASET):
    """
    This function create output Excel files by iteration.
    
    Input:
    NAME       | Filename                                         | String
    D          | Problem dimension                                | Integer
    DATASET    | Best results I repetition                        | Py Numpy array
    
    Output:
    Save xls file in current directory
    """
    
    # Individual results
    X = DATASET['X_POSITION']
    COLUMNS = []
    for I_COUNT in range(D):
        COLUMNS_X = 'X_' + str(I_COUNT)
        COLUMNS.append(COLUMNS_X)
    DATA1 = pd.DataFrame(X, columns = COLUMNS)
    OF = DATASET['OF']
    DATA2 = pd.DataFrame(OF, columns = ['OF'])
    FIT = DATASET['FIT']
    DATA3 = pd.DataFrame(FIT, columns = ['FIT'])
    NEOF = DATASET['NEOF']
    DATA4 = pd.DataFrame(NEOF, columns = ['NEOF'])
    FRAME = [DATA1, DATA2, DATA3, DATA4]
    DATA = pd.concat(FRAME, axis = 1)
    NAME += '.xlsx' 
    print(NAME)
    WRITER = pd.ExcelWriter(NAME, engine = 'xlsxwriter')
    DATA.to_excel(WRITER, sheet_name = 'Sheet1')
    WRITER.close()

def EXCEL_PROCESS_RESUME(NAME, D, DATASET, N_ITER, N_REP):
    """
    This function create output Excel files complete process.

    Input:
    NAME       | Filename                                         | String
    D          | Problem dimension                                | Integer
    DATASET    | Best results I repetition                        | Py Numpy array
    N_REP      | Number of repetitions                            | Integer
    N_ITER     | Number of iterations                             | Integer

    Output:
    Save xls file in current directory
    """
    
    # Resume process in arrays
    X = np.zeros((N_REP, D))
    OF = np.zeros((N_REP, 1))
    FIT = np.zeros((N_REP, 1))
    NEOF = np.zeros((N_REP, 1))
    for REP in range(N_REP):
        X_I = DATASET[REP]['X_POSITION'][N_ITER]
        X[REP, :] = X_I
        OF[REP, :] = DATASET[REP]['OF'][N_ITER]
        FIT[REP, :] = DATASET[REP]['FIT'][N_ITER]
        NEOF[REP, :] = DATASET[REP]['NEOF'][N_ITER]
    
    # Save output in Excel file
    COLUMNS = []
    for I in range(D):
        COLUMNS_X = 'X_' + str(I)
        COLUMNS.append(COLUMNS_X)
    DATA1 = pd.DataFrame(X, columns = COLUMNS)
    DATA2 = pd.DataFrame(OF, columns = ['OF'])
    DATA3 = pd.DataFrame(FIT, columns = ['FIT'])
    DATA4 = pd.DataFrame(NEOF, columns = ['NEOF'])
    FRAME = [DATA1, DATA2, DATA3, DATA4]
    DATA = pd.concat(FRAME, axis = 1)
    NAME += '.xlsx' 
    print(NAME)
    WRITER = pd.ExcelWriter(NAME, engine = 'xlsxwriter')
    DATA.to_excel(WRITER, sheet_name = 'Sheet1')
    WRITER.close()

def CONVERT_CONTINUOUS_DISCRETE(X, DATA_DISCRETE):
    """
    """
    X_NEW = []
    for I in range(len(X)):
        AUX = round(X[I])
        X_NEW.append(DATA_DISCRETE[I]['X'][AUX])
    return X_NEW