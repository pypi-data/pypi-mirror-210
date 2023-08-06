import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import META_TOOLBOX.META_FUNCTIONS as META_FN

def CONVERT_SI_TO_INCHES(WIDTH, HEIGHT):
    """ 
    This function convert figure size meters to inches.
    
    Input:
    WIDTH    |  Figure width in SI units       | Float
    HEIGHT   |  Figure height in SI units      | Float
    
    Output:
    WIDTH    |  Figure width in INCHES units   | Float
    HEIGHT   |  Figure height in INCHES units  | Float
    """
    WIDTH = WIDTH / 0.0254
    HEIGHT = HEIGHT / 0.0254
    return WIDTH, HEIGHT

def SAVE_GRAPHIC(NAME, EXT, DPI):
    """ 
    This function save graphics on a specific path extensions options.

    Input: 
    NAME  | Path + name figure               | String
    EXT   | File extension                   | String
		  |   'svg'                         |
          |   'png'                         |
          |   'eps'                         |
          |   'pdf'                         |
    DPI   | The resolution in dots per inch  | Integer
    
    Output:
    N/A
    """
    plt.savefig(NAME + '.' + EXT, dpi = DPI, bbox_inches='tight', transparent=True)

def META_PLOT_001(DATASET, PLOT_SETUP):
	"""
    OF + FIT chart - Line chart

    Input:  
    DATASET     | META Optimization toolbox results                        | Py dictionary
	            |  Dictionary tags                                         |
				|    'X'   = Values NEOF or Iterations                     | Py Numpy array[N_ITER + 1 x 1]
	            |    'OF'  = Obj function value by iteration               | Py Numpy array[N_ITER + 1 x 1]
                |    'FIT' = Fitness value by iteration                    | Py Numpy array[N_ITER + 1 x 1]
    PLOT_SETUP  | Contains specifications of each model of chart           | Py Dictionary
                |  Dictionary tags                                         |
                |    'NAME'          == Filename output file               | String 
                |    'WIDTH'         == Width figure                       | Float
                |    'HEIGHT         == Height figure                      | Float
                |    'EXTENSION'     == Extension output file              | String 
                |    'DPI'           == Dots Per Inch - Image quality      | Integer   
                |    'COLOR OF'      == OF line color                      | String
				|    'MARKER OF'     == OF line marker                     | String
                |    'COLOR FIT'     == FIT line color                     | String
				|    'MARKER FIT'    == FIT line marker                    | String
				|    'MARKER SIZE'   == Marker size                        | Float
				|    'LINE WIDTH'    == Line width                         | Float
				|    'LINE STYLE'    == Line style                         | String
                |    'OF AXIS LABEL' == OF Y axis label name               | String
                |    'X AXIS LABEL'  == X label name                       | String
				|    'LABELS COLOR'  == Labels color                       | String
				|    'LABELS SIZE'   == Labels size                        | Float
                |    'X AXIS SIZE'   == X axis size                        | Float
                |    'Y AXIS SIZE'   == Y axis size                        | Float
                |    'AXISES COLOR'  == Axis color                         | String
                |    'ON GRID?'      == Grid in chart                      | Boolean    
				|    'Y LOG'         == Y axis logscale                    | Boolean     
				|    'X LOG'         == X axis logscale                    | Boolean 
    
    Output:
    The image is saved in the current directory 
	"""
	NAME = PLOT_SETUP['NAME']
	W = PLOT_SETUP['WIDTH']
	H = PLOT_SETUP['HEIGHT']
	EXT = PLOT_SETUP['EXTENSION']
	DPI = PLOT_SETUP['DPI']
	COLOR_OF = PLOT_SETUP['COLOR OF']
	MARKER_OF = PLOT_SETUP['MARKER OF']
	COLOR_FIT = PLOT_SETUP['COLOR FIT']
	MARKER_FIT = PLOT_SETUP['MARKER FIT']
	MARKER_SIZE = PLOT_SETUP['MARKER SIZE']
	LINE_WIDTH = PLOT_SETUP['LINE WIDTH']
	LINE_STYLE = PLOT_SETUP['LINE STYLE']
	Y_OF_AXIS_LABEL = PLOT_SETUP['OF AXIS LABEL']
	X_AXIS_LABEL = PLOT_SETUP['X AXIS LABEL']
	LABELS_SIZE = PLOT_SETUP['LABELS SIZE']     
	LABELS_COLOR = PLOT_SETUP['LABELS COLOR']
	X_AXIS_SIZE = PLOT_SETUP['X AXIS SIZE']
	Y_AXIS_SIZE = PLOT_SETUP['Y AXIS SIZE']
	AXISES_COLOR = PLOT_SETUP['AXISES COLOR']
	YLOGSCALE = PLOT_SETUP['Y LOG']
	XLOGSCALE = PLOT_SETUP['X LOG']
	GRID = PLOT_SETUP['ON GRID?']
	X = DATASET['X']
	Y_0 = DATASET['OF']
	Y_1 = DATASET['FIT']
	
	# Convert units of size figure
	W, H = CONVERT_SI_TO_INCHES(W, H)
	
	# Plot
	FIG, AX = plt.subplots(2, 1, figsize = (W, H), sharex = True)
	AX[0].plot(X, Y_0, marker = MARKER_OF, color = COLOR_OF, linestyle = LINE_STYLE, linewidth = LINE_WIDTH, markersize = MARKER_SIZE)
	AX[1].plot(X, Y_1, marker = MARKER_FIT, color = COLOR_FIT, linestyle = LINE_STYLE, linewidth = LINE_WIDTH, markersize = MARKER_SIZE)
	if YLOGSCALE:
		AX[0].semilogy()
		AX[1].semilogy()
	if XLOGSCALE:
		AX[0].semilogx()
		AX[1].semilogx()
	font = {'fontname': 'Arial',
			'color':  LABELS_COLOR,
			'weight': 'normal',
			'size': LABELS_SIZE}
	AX[0].set_ylabel(Y_OF_AXIS_LABEL, fontdict = font)
	AX[1].set_xlabel(X_AXIS_LABEL, fontdict = font)
	AX[1].set_ylabel('$Fitness$', fontdict = font)          
	AX[0].tick_params(axis = 'x', labelsize = X_AXIS_SIZE, colors = AXISES_COLOR)
	AX[0].tick_params(axis = 'y', labelsize = Y_AXIS_SIZE, colors = AXISES_COLOR)
	AX[1].tick_params(axis = 'x', labelsize = X_AXIS_SIZE, colors = AXISES_COLOR)
	AX[1].tick_params(axis = 'y', labelsize = Y_AXIS_SIZE, colors = AXISES_COLOR)
	if GRID == True:
		AX[0].grid(color = 'grey', linestyle = '-.', linewidth = 1, alpha = 0.20)
		AX[1].grid(color = 'grey', linestyle = '-.', linewidth = 1, alpha = 0.20)
	SAVE_GRAPHIC(NAME, EXT, DPI)

def META_PLOT_002(DATASET, PLOT_SETUP):
	"""
    OF or FIT chart - Line chart

    Input:  
    DATASET     | META Optimization toolbox results                        | Py dictionary
	            |  Dictionary tags                                         |
				|    'X'   = Values NEOF or Iterations                     | Py Numpy array[N_ITER + 1 x 1]
	            |    'Y'  = Obj, Fit, Worst or average value by iteration  | Py Numpy array[N_ITER + 1 x 1]
    PLOT_SETUP  | Contains specifications of each model of chart           | Py Dictionary
                |  Dictionary tags                                         |
                |    'NAME'          == Filename output file               | String 
                |    'WIDTH'         == Width figure                       | Float
                |    'HEIGHT         == Height figure                      | Float
                |    'EXTENSION'     == Extension output file              | String 
                |    'DPI'           == Dots Per Inch - Image quality      | Integer   
                |    'COLOR'         == Line color                         | String
				|    'MARKER'        == Line marker                        | String
				|    'MARKER SIZE'   == Marker size                        | Float
				|    'LINE WIDTH'    == Line width                         | Float
				|    'LINE STYLE'    == Line style                         | String
                |    'Y AXIS LABEL'  == Y axis label name                  | String
                |    'X AXIS LABEL'  == X axis label name                  | String
				|    'LABELS COLOR'  == Labels color                       | String
				|    'LABELS SIZE'   == Labels size                        | Float
                |    'X AXIS SIZE'   == X axis size                        | Float
                |    'Y AXIS SIZE'   == Y axis size                        | Float
                |    'AXISES COLOR'  == Axis color                         | String
                |    'ON GRID?'      == Grid in chart                      | Boolean  
				|    'Y LOG'         == Y axis logscale                    | Boolean     
				|    'X LOG'         == X axis logscale                    | Boolean 
    
    Output:
    The image is saved in the current directory 
	"""
	NAME = PLOT_SETUP['NAME']
	W = PLOT_SETUP['WIDTH']
	H = PLOT_SETUP['HEIGHT']
	EXT = PLOT_SETUP['EXTENSION']
	DPI = PLOT_SETUP['DPI']
	COLOR = PLOT_SETUP['COLOR']
	MARKER = PLOT_SETUP['MARKER']
	MARKER_SIZE = PLOT_SETUP['MARKER SIZE']
	LINE_WIDTH = PLOT_SETUP['LINE WIDTH']
	LINE_STYLE = PLOT_SETUP['LINE STYLE']
	Y_AXIS_LABEL = PLOT_SETUP['Y AXIS LABEL']
	X_AXIS_LABEL = PLOT_SETUP['X AXIS LABEL']
	LABELS_SIZE = PLOT_SETUP['LABELS SIZE']     
	LABELS_COLOR = PLOT_SETUP['LABELS COLOR']
	X_AXIS_SIZE = PLOT_SETUP['X AXIS SIZE']
	Y_AXIS_SIZE = PLOT_SETUP['Y AXIS SIZE']
	AXISES_COLOR = PLOT_SETUP['AXISES COLOR']
	GRID = PLOT_SETUP['ON GRID?']
	YLOGSCALE = PLOT_SETUP['Y LOG']
	XLOGSCALE = PLOT_SETUP['X LOG']
	X = DATASET['X']
	Y = DATASET['Y']
	
	# Convert units of size figure
	W, H = CONVERT_SI_TO_INCHES(W, H)
	
	# Plot
	FIG, AX = plt.subplots(1, 1, figsize = (W, H), sharex = True)
	AX.plot(X, Y, marker = MARKER, color = COLOR, linestyle = LINE_STYLE, linewidth = LINE_WIDTH, markersize = MARKER_SIZE)
	if YLOGSCALE:
		AX.semilogy()
	if XLOGSCALE:
		AX.semilogx()
	font = {'fontname': 'Arial',
			'color':  LABELS_COLOR,
			'weight': 'normal',
			'size': LABELS_SIZE}
	AX.set_ylabel(Y_AXIS_LABEL, fontdict = font)
	AX.set_xlabel(X_AXIS_LABEL, fontdict = font)   
	AX.tick_params(axis = 'x', labelsize = X_AXIS_SIZE, colors = AXISES_COLOR)
	AX.tick_params(axis = 'y', labelsize = Y_AXIS_SIZE, colors = AXISES_COLOR)
	if GRID == True:
		AX.grid(color = 'grey', linestyle = '-.', linewidth = 1, alpha = 0.20)
	SAVE_GRAPHIC(NAME, EXT, DPI)

def META_PLOT_003(DATASET, PLOT_SETUP):
	"""
    OF or FIT - Line chart

    Input:  
    DATASET     | META Optimization toolbox results                        | Py dictionary
	            |  Dictionary tags                                         |
				|    'X'     = Values NEOF or Iterations                   | Py Numpy array[N_ITER + 1 x 1]
	            |    'BEST'  = Best value by iteration                     | Py Numpy array[N_ITER + 1 x 1]
	            |    'WORST'  = Best value by iteration                    | Py Numpy array[N_ITER + 1 x 1]
	            |    'AVERAGE'  = Best value by iteration                  | Py Numpy array[N_ITER + 1 x 1]
    PLOT_SETUP  | Contains specifications of each model of chart           | Py Dictionary
                |  Dictionary tags                                         |
                |    'NAME'          == Filename output file               | String 
                |    'WIDTH'         == Width figure                       | Float
                |    'HEIGHT         == Height figure                      | Float
                |    'EXTENSION'     == Extension output file              | String 
                |    'DPI'           == Dots Per Inch - Image quality      | Integer   
                |    'COLOR BEST'    == Line color - Best results          | String
            	|    'COLOR WORST'   == Line color - Worst results         | String	
                |    'COLOR AVERAGE' == Line color - Average results       | String
				|    'MARKER'        == Line marker                        | String
				|    'MARKER SIZE'   == Marker size                        | Float
				|    'LINE WIDTH'    == Line width                         | Float
				|    'LINE STYLE'    == Line style                         | String
                |    'Y AXIS LABEL'  == Y axis label name                  | String
                |    'X AXIS LABEL'  == X axis label name                  | String
				|    'LABELS COLOR'  == Labels color                       | String
				|    'LABELS SIZE'   == Labels size                        | Float
                |    'X AXIS SIZE'   == X axis size                        | Float
                |    'Y AXIS SIZE'   == Y axis size                        | Float
                |    'AXISES COLOR'  == Axis color                         | String
                |    'GRID'          == Grid in chart                      | Boolean  
				|    'Y LOG'         == Y axis logscale                    | Boolean 
				|    'X LOG'         == X axis logscale                    | Boolean 
				|    LOC LEGEND      == Legend location                    | String
				|    SIZE LEGEND     == Legend size                        | Float
    
    Output:
    The image is saved in the current directory 
	"""
	NAME = PLOT_SETUP['NAME']
	W = PLOT_SETUP['WIDTH']
	H = PLOT_SETUP['HEIGHT']
	EXT = PLOT_SETUP['EXTENSION']
	DPI = PLOT_SETUP['DPI']
	COLOR_1 = PLOT_SETUP['COLOR BEST']
	COLOR_2 = PLOT_SETUP['COLOR WORST']
	COLOR_3 = PLOT_SETUP['COLOR AVERAGE']
	MARKER = PLOT_SETUP['MARKER']
	MARKER_SIZE = PLOT_SETUP['MARKER SIZE']
	LINE_WIDTH = PLOT_SETUP['LINE WIDTH']
	LINE_STYLE = PLOT_SETUP['LINE STYLE']
	Y_AXIS_LABEL = PLOT_SETUP['Y AXIS LABEL']
	X_AXIS_LABEL = PLOT_SETUP['X AXIS LABEL']
	LABELS_SIZE = PLOT_SETUP['LABELS SIZE']     
	LABELS_COLOR = PLOT_SETUP['LABELS COLOR']
	X_AXIS_SIZE = PLOT_SETUP['X AXIS SIZE']
	Y_AXIS_SIZE = PLOT_SETUP['Y AXIS SIZE']
	AXISES_COLOR = PLOT_SETUP['AXISES COLOR']
	GRID = PLOT_SETUP['ON GRID?']
	YLOGSCALE = PLOT_SETUP['Y LOG']
	XLOGSCALE = PLOT_SETUP['X LOG']
	LOC = PLOT_SETUP['LOC LEGEND']
	SIZE_LEGEND = PLOT_SETUP['SIZE LEGEND']
	X = DATASET['X']
	Y_1 = DATASET['BEST']
	Y_2 = DATASET['WORST']
	Y_3 = DATASET['AVERAGE']
	
	# Convert units of size figure
	W, H = CONVERT_SI_TO_INCHES(W, H)
	
	# Plot
	FIG, AX= plt.subplots(1, 1, figsize = (W, H), sharex = True)
	AX.plot(X, Y_1, marker = MARKER, color = COLOR_1, linestyle = LINE_STYLE, linewidth = LINE_WIDTH, markersize = MARKER_SIZE, label='Best')
	AX.plot(X, Y_2, marker = MARKER, color = COLOR_2, linestyle = LINE_STYLE, linewidth = LINE_WIDTH, markersize = MARKER_SIZE, label='Worst')
	AX.plot(X, Y_3, marker = MARKER, color = COLOR_3, linestyle = LINE_STYLE, linewidth = LINE_WIDTH, markersize = MARKER_SIZE, label='Average')
	if YLOGSCALE:
		AX.semilogy()
	if XLOGSCALE:
		AX.semilogx()
	font = {'fontname': 'Arial',
			'color':  LABELS_COLOR,
			'weight': 'normal',
			'size': LABELS_SIZE}
	AX.set_ylabel(Y_AXIS_LABEL, fontdict = font)
	AX.set_xlabel(X_AXIS_LABEL, fontdict = font)   
	AX.tick_params(axis = 'x', labelsize = X_AXIS_SIZE, colors = AXISES_COLOR)
	AX.tick_params(axis = 'y', labelsize = Y_AXIS_SIZE, colors = AXISES_COLOR)
	if GRID == True:
		AX.grid(color = 'grey', linestyle = '-.', linewidth = 1, alpha = 0.20)
	plt.legend(loc = LOC, prop = {'size': SIZE_LEGEND})
	SAVE_GRAPHIC(NAME, EXT, DPI)

def META_PLOT_004(DATASET, PLOT_SETUP):
    """
    OF or FIT - Boxplot and histogram

	Input:
    DATASET     | Results from a RASD Toolboox                              | Py dataframe or Py Numpy array[N_POP x 1]
                |    Dictionary tags                                        |
                |    'DATA'          == Complete data                       | Py Numpy array[N_POP x 1]
                |    'COLUMN'        == Dataframe column                    | String
    PLOT_SETUP  | Contains specifications of each model of chart            | Py dictionary
                |    Dictionary tags                                        |
                |    'NAME'          == Filename output file                | String 
                |    'WIDTH'         == Width figure                        | Float
                |    'HEIGHT         == Height figure                       | Float
                |    'X AXIS SIZE'   == X axis size                         | Float
                |    'Y AXIS SIZE'   == Y axis size                         | Float
                |    'AXISES COLOR'  == Axis color                          | String
                |    'X AXIS LABEL'  == X label name                        | String
                |    'LABELS SIZE'   == Labels size                         | Float
                |    'LABELS COLOR'  == Labels color                        | String
                |    'CHART COLOR'   == Boxplot and histogram color         | String
                |    'BINS'          == Range representing the width of     | Float
                |                       a single bar                        | 
                |    'KDE'           == Smooth of the random distribution   | Boolean      
                |    'DPI'           == Dots Per Inch - Image quality       | Integer   
                |    'EXTENSION'     == Extension output file               | String ('.svg, '.png', '.eps' or '.pdf')

    Output:
    The image is saved in the current directory 
    """
    
	# Checking which is the best process 
    MINVALUES = []
    N_REP = DATASET['NUMBER OF REPETITIONS']
    N_ITER = DATASET['NUMBER OF ITERATIONS']
    TYPE = DATASET['OF OR FIT']
    BEST_REP = DATASET['BEST']
    for ID in range(N_REP):
        if TYPE == 'OF':
            X = BEST_REP[ID]['OF'][N_ITER]
        else:
            X = BEST_REP[ID]['FIT'][N_ITER]
        MINVALUES.append(X)
    NAME = PLOT_SETUP['NAME']
    W = PLOT_SETUP['WIDTH']
    H = PLOT_SETUP['HEIGHT']
    EXT = PLOT_SETUP['EXTENSION']
    DPI = PLOT_SETUP['DPI']
    X_AXIS_LABEL = PLOT_SETUP['X AXIS LABEL']
    X_AXIS_SIZE = PLOT_SETUP['X AXIS SIZE']
    Y_AXIS_SIZE = PLOT_SETUP['Y AXIS SIZE']
    AXISES_COLOR = PLOT_SETUP['AXISES COLOR']
    LABELS_SIZE = PLOT_SETUP['LABELS SIZE']     
    LABELS_COLOR = PLOT_SETUP['LABELS COLOR']
    CHART_COLOR = PLOT_SETUP['COLOR']
    BINS = PLOT_SETUP['BINS']
    KDE = PLOT_SETUP['KDE']

    sns.set(style = 'ticks')

    # Convert units of size figure
    [W, H] = CONVERT_SI_TO_INCHES(W, H)
    
	# Plot
    FIG, (AX_BOX, AX_HIST) = plt.subplots(2, figsize = (W, H), sharex = True, gridspec_kw = {'height_ratios': (.15, .85)})
    sns.boxplot(x = MINVALUES, ax = AX_BOX, color = CHART_COLOR)
    sns.histplot(MINVALUES, ax = AX_HIST, kde = KDE, color = CHART_COLOR, bins = BINS)
    AX_BOX.set(yticks = [])
    AX_BOX.set(xlabel='')
    font = {'fontname': 'Arial',
            'color':  LABELS_COLOR,
            'weight': 'normal',
            'size': LABELS_SIZE}
    AX_HIST.set_xlabel(X_AXIS_LABEL, fontdict = font)
    AX_HIST.set_ylabel('$Frequency$', fontdict = font)
    AX_HIST.tick_params(axis= 'x', labelsize = X_AXIS_SIZE, colors = AXISES_COLOR)
    AX_HIST.tick_params(axis= 'y', labelsize = Y_AXIS_SIZE, colors = AXISES_COLOR)
    sns.despine(ax = AX_HIST)
    sns.despine(ax = AX_BOX, left = True)
    SAVE_GRAPHIC(NAME, EXT, DPI)

def META_PLOT_005(FUNCTION,X_L, X_U):
    """
	wsss
	asas
	"""
	# Convert units of size figure
    [W, H] = CONVERT_SI_TO_INCHES(W, H)
	
    N = 100
    X_AUX = np.linspace(X_L, X_U, N)
    Y_AUX = np.linspace(X_L, X_U, N)
    A, B = np.meshgrid(X_AUX, Y_AUX)
    Z = np.zeros((N,N))
    for I in range(N):
        for J in range(N):
            X = [A[I, J], B[I, J]]
            if FUNCTION == "ACKLEY":
                Z[I, J] = META_FN.ACKLEY(X)
            if FUNCTION == "SPHERE":
                Z[I, J] = META_FN.SPHERE(X)
            if FUNCTION == "ROSENBROCK":
                Z[I, J] = META_FN.ROSENBROCK(X)
            if FUNCTION == "RASTRIGIN":
                Z[I, J] = META_FN.RASTRIGIN(X)
            if FUNCTION == "GRIEWANK":
                Z[I, J] = META_FN.GRIEWANK(X)
            if FUNCTION == "ZAKHAROV":
                Z[I, J] = META_FN.ZAKHAROV(X)
            if FUNCTION == "EASOM":
                Z[I, J] = META_FN.EASOM(X)
            if FUNCTION == "MICHALEWICS":
                Z[I, J] = META_FN.MICHALEWICS(X)
    fig = plt.figure()
    ax = plt.axes(projection = '3d')
    ax.contour3D(A, B, Z, 100, cmap = 'jet')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
