*******************
How to use NoLoadj ?
*******************

NoLoadj stands for Non-Linear Optimization using Automatic
Differentiation with Jax package. It aims to be a light non-linear optimization
tool for energy components and systems. It is an Open Source project located on
GitLab : https://gricad-gitlab.univ-grenoble-alpes.fr/design_optimization/NoLoad_v2.

.. contents:: Table of Contents

Model computation
=================

Writing the model
-----------------

The first thing to do is to write the equations of your physical model
in a Python function. See the example below with the Rosenbrock
function.

.. figure:: images/bar2.png
.. figure:: images/Rosenbrock.PNG

.. code-block:: python


    def rosenbrock(x,y):
        fobj=(1-x)*(1-x)+100*(y-x*x)**2
        ctr1=(x-1)**3-y+1
        ctr2=x+y-2
        return locals().items()

"locals().items()" returns all the variables defined in the function.
NoLoadj will select those you will write in specifications.
If you use mathematical functions, you must call the
jax.numpy library at the beginning of the code :

.. code-block:: python


    import jax.numpy as np

The mathematical functions are "np.exp(x),np.log(x),np.cos(x),... ".
Examples in the following parts will illustre this point.

You also have rules to respect when you create your function because of Jax :

- For assignment to arrays, use JAX pure fonctional operators instead of A[0] = x : https://jax.readthedocs.io/en/latest/jax.ops.html.
- Do not put a JAX array in a numpy method, and do not put a numpy array in a JAX method.
- Assignements on dataframe (from pandas library) do not work with JAX array.
- "if" structure does not work with JIT functionnality, use cond function from jax.lax package : https://jax.readthedocs.io/en/latest/jax.lax.html#control-flow-operators
- Implicit casting of lists to arrays A = np.sum([x, y]), use A = np.sum(np.array([x, y])) instead.

ComputeOnce
-----------

To see how the outputs of your model react to the inputs, you may use
ComputeOnce function. In the example below, we use Rosenbrock function
defined above. The "inputs" attribute is a dictionary with the names and
the values of your inputs, the "outputs" attribute is a list with the
outputs names you want to compute. Then, the "model" attribute is the
name of your function, and it returns a list of the outputs values.

.. code-block:: python

    from noloadj.analyse.simulation import computeOnce

    inputs={'x':1.0, 'y':2.0}
    outputs=['fobj','ctr1','ctr2']
    results = computeOnce(model=rosenbrock, inputs=inputs, outputs=outputs)
    print(outputs, '=', results)


.. parsed-literal::

    ['fobj', 'ctr1', 'ctr2'] = [100.0, -1.0, 1.0]


If there are fixed parameters in your model, they must be put in the
inputs attribute.

ComputeParametric
-----------------

ComputeParametric is a useful function to compute outputs values
according to an input varying in a range of values. In the example below
with the Rosenbrock function, the "inputs" attribute is a dictionary
with the names and the values of the non-varying inputs. The "outputs"
attribute is a list with outputs names you want to compute. The
"variable" attribute is the name of the varying input, and the "values"
attribute is the range of values the input can take. Then, the "model"
attribute is the name of your model function.

.. code-block:: python

    from noloadj.analyse.simulation import computeParametric
    inputs={'y':2.0}
    outputs=['fobj','ctr1','ctr2']

    variable = 'x'
    values = np.arange(-1.5, 1.5, 0.1) #[-1.5, -1.4, ..., 1.5]
    iter = computeParametric(rosenbrock, variable, values, inputs, outputs)

It returns an "Iteration class" with all outputs values. To print all
the values numerically, you may use print function.

.. code-block:: python

    df=iter.print()
    print(df)
.. parsed-literal::

    |    |            x |   fobj |    ctr1 |         ctr2 |
    |---:|-------------:|-------:|--------:|-------------:|
    |  0 | -1.5         |  12.5  | -16.625 | -1.5         |
    |  1 | -1.4         |   5.92 | -14.824 | -1.4         |
    |  2 | -1.3         |  14.9  | -13.167 | -1.3         |
    |  3 | -1.2         |  36.2  | -11.648 | -1.2         |
    |  4 | -1.1         |  66.82 | -10.261 | -1.1         |
    |  5 | -1           | 104    |  -9     | -1           |
    |  6 | -0.9         | 145.22 |  -7.859 | -0.9         |
    |  7 | -0.8         | 188.2  |  -6.832 | -0.8         |
    |  8 | -0.7         | 230.9  |  -5.913 | -0.7         |
    |  9 | -0.6         | 271.52 |  -5.096 | -0.6         |
    | 10 | -0.5         | 308.5  |  -4.375 | -0.5         |
    | 11 | -0.4         | 340.52 |  -3.744 | -0.4         |
    | 12 | -0.3         | 366.5  |  -3.197 | -0.3         |
    | 13 | -0.2         | 385.6  |  -2.728 | -0.2         |
    | 14 | -0.1         | 397.22 |  -2.331 | -0.1         |
    | 15 |  1.33227e-15 | 401    |  -2     |  1.33227e-15 |
    | 16 |  0.1         | 396.82 |  -1.729 |  0.1         |
    | 17 |  0.2         | 384.8  |  -1.512 |  0.2         |
    | 18 |  0.3         | 365.3  |  -1.343 |  0.3         |
    | 19 |  0.4         | 338.92 |  -1.216 |  0.4         |
    | 20 |  0.5         | 306.5  |  -1.125 |  0.5         |
    | 21 |  0.6         | 269.12 |  -1.064 |  0.6         |
    | 22 |  0.7         | 228.1  |  -1.027 |  0.7         |
    | 23 |  0.8         | 185    |  -1.008 |  0.8         |
    | 24 |  0.9         | 141.62 |  -1.001 |  0.9         |
    | 25 |  1           | 100    |  -1     |  1           |
    | 26 |  1.1         |  62.42 |  -0.999 |  1.1         |
    | 27 |  1.2         |  31.4  |  -0.992 |  1.2         |
    | 28 |  1.3         |   9.7  |  -0.973 |  1.3         |
    | 29 |  1.4         |   0.32 |  -0.936 |  1.4         |


You can also use the plotXY function to print it graphically.

.. code-block:: python

    iter.plotXY()

.. figure:: images/output_20_0.png

.. figure:: images/output_20_2.png


ComputeJacobian
---------------

To compute the gradient of the objective and constraints of your model,
you may use computeJacobian function. The "model" attribute is the name
of your model function. The "inputs" attribute is a dictionary with the
names and the values of inputs. The "objectives","eq_cstr" and
"ineq_cstr" attributes are lists with respectively the names of the
objective function, equality constraints and inequality constraints. The
"parameters" attribute corresponds to fixed parameters and is empty for
this example.

.. code-block:: python

    from noloadj.analyse.simulation import computeJacobian

    inputs={'x':1.0, 'y':2.0}
    computeJacobian(model=rosenbrock,inputs=inputs,objectives=['fobj'],
                    eq_cstr=[],ineq_cstr=['ctr1','ctr2'],parameters={})


.. parsed-literal::

    f_val : [100.]
    f_grad : [-400.  200.]
    ineq_cstr_val : [-1.  1.]
    ineq_cstr_grad : [array([ 0., -1.]), array([1., 1.])]


The "f_grad" line gives the gradient of the objective function. The
"ineq_cstr_grad" gives the gradient of the inequality constraints.

Unconstrained Optimization
==========================

To solve an unconstrained optimization problem, see the example below
with the Ackley function.

Ackley function
---------------
.. figure:: images/bar.png
.. figure:: images/Ackley.png

The objective is written in the Python function below. Note the use of
jax.numpy mathematical functions such as np.square, np.exp, …

.. code-block:: python

    import jax.numpy as np
    import math

    def ackley(x,y):
        fobj = -20 * np.exp(-0.2 * np.sqrt(0.5 * (np.square(x) + np.square(y)))) \
               - np.exp(0.5 * (np.cos(2 * math.pi * x) + np.cos(2 * math.pi * y))) \
               + math.exp(1) + 20
        return locals().items()

The specifications of the optimization problem are written in the Spec
class. The "variables" attribute is a dictionary with the names and the
inital values of the variables to optimize. The "bounds" attribute is
also a dictionary which represents the search domain for the variables.
The "objective" attribute is a dictionary with the name of the objective
function and a gap of values that can take this function.

.. code-block:: python

    from noloadj.optimization.optimProblem import Spec, OptimProblem

    spec = Spec(variables={'x':2, 'y':2}, bounds={'x':[-5, 5], 'y':[-5, 5]},
                objectives={'fobj':[0.,15.]})

We define the optimization problem with the OptimProblem class. The
"model" attribute is the name of your model function, and the
"specifications" attribute corresponds to the class defined before.

.. code-block:: python

    optim = OptimProblem(model=ackley, specifications=spec)

We start the optimization with the "run" function of the OptimProblem
class. It returns a "result" class.

.. code-block:: python

    result = optim.run()


.. parsed-literal::

    Optimization terminated successfully    (Exit mode 0)
                Current function value: [6.64437582e-05]
                Iterations: 9
                Function evaluations: 20
                Gradient evaluations: 9


The optimization was successfully done. The "Current objective function"
is the objective function evaluated at the optimal point (here
f(opt)=0). We print the optimized variable with the "printResults"
function.

.. code-block:: python

    result.printResults()


.. parsed-literal::

    {'x': 1.5781116638803522e-05, 'y': 1.739422385733534e-05}
    {'fobj': 6.644375817899117e-05}


We find the global minimum expected : f(0,0)=0.

Actually, there are attributes for the "run" function such as the
tolerance wanted for the objective function (ftol) and the name of the
optimization algorithm (method). By default, ftol=1e-5 and the method is
'SLSQP' (Sequential Least Square Quadratic Programming). But we can
rerun the optimization with an other method ('Least Square' or 'IPOPT' for Interior point method)
and/or a better tolerance. 'Least Square' works only for unconstrained optimization.

.. code-block:: python

    result = optim.run(ftol=1e-7,method='LeastSquare')


.. parsed-literal::

    `gtol` termination condition is satisfied.
    Solution found:  [-4.4408921e-16  8.8817842e-16]
    Value of the cost function at the solution:  6.310887241768095e-30
    Vector of residuals at the solution:  [3.55271368e-15]
    Gradient of the cost function at the solution:  [-4.49386684e-15  8.98773368e-15]


We find the same results as before.

Display results
---------------

There are several functions to print or return the results of the
optimization. Note that all these functions are methods of the result
class.

At first, the "printResults" method to print optimized variables and
outputs (objective function + constraints) as dictionaries.

.. code-block:: python

    result.printResults()


.. parsed-literal::

    {'x': -4.440892098500626e-16, 'y': 8.881784197001252e-16}
    {'fobj': 3.552713678800501e-15}


"plotResults" shows graphically values of inputs and outputs for each iteration
 of the optimization. Outputs are choosen by the user with a list.

.. code-block:: python

    result.plotResults(['fobj'])

.. figure:: images/output_48_0.png

.. figure:: images/output_48_2.png

solution returns a list with the values of optimized variables.

.. code-block:: python

    sol=result.solution()
    print('sol=',sol)

.. parsed-literal::

    sol= [-4.440892098500626e-16, 8.881784197001252e-16]


getLastInputs returns a dictionary of the optimized variables.

.. code-block:: python

    inp=result.getLastInputs()
    print('inp=',inp)

.. parsed-literal::

    inp= {'x': -4.440892098500626e-16, 'y': 8.881784197001252e-16}


getLastOutputs returns a dictionary of the optimized outputs.

.. code-block:: python

    out=result.getLastOutputs()
    print('out=',out)

.. parsed-literal::

    out= {'fobj': 3.552713678800501e-15}


printAllResults prints the different variables of inputs during each
iteration of the optimization.

.. code-block:: python

    result.printAllResults()

.. parsed-literal::

    {'x': 2.0, 'y': 2.0}
    {'x': 0.6593599079287253, 'y': 0.6593599079287253}
    {'x': 0.4104981710953608, 'y': 0.41049817109536085}
    {'x': -5.0, 'y': -5.0}
    {'x': -1.6440850614698304, 'y': -1.6440850614698304}
    {'x': -0.33810682730902497, 'y': -0.3381068273090249}
    {'x': 0.09148338273764894, 'y': 0.09148338273764844}
    {'x': -0.1799196026243623, 'y': -0.17991960262435064}
    {'x': -0.00895860673980714, 'y': -0.008958606739803143}
    {'x': 0.02067226145979892, 'y': 0.020672261459031463}
    {'x': 0.0012982860687560573, 'y': 0.0012982860684930125}
    {'x': -0.00337098703976194, 'y': -0.003370986812025232}
    {'x': -0.0003054604929685332, 'y': -0.0003054604149209264}
    {'x': 0.0004861656298466346, 'y': 0.0004859049562408854}
    {'x': 1.6682393036306098e-05, 'y': 1.657636128318536e-05}
    {'x': -0.0033402599064650375, 'y': 0.0030628310706608134}
    {'x': -0.0003190118369138283, 'y': 0.0003212018322209482}
    {'x': -1.6887029958707345e-05, 'y': 4.703890837696164e-05}
    {'x': 1.3325450736804753e-05, 'y': 1.9622615992562988e-05}
    {'x': 1.5781116638803522e-05, 'y': 1.739422385733534e-05}
    {'x': 2.0, 'y': 2.0}
    {'x': -4.440892098500626e-16, 'y': 8.881784197001252e-16}


getIteration returns the variables and outputs values at an Iteration
given in parameter (the 3rd one in the code below).

.. code-block:: python

    inp,out=result.getIteration(3)
    print('inp=',inp)
    print('out=',out)

.. parsed-literal::

    inp= {'x': 0.4104981710953608, 'y': 0.41049817109536085}
    out= {'fobj': 3.865550771773872}


Ackley function with fixed parameters
-------------------------------------

We add fixed parameters, for which values are given before the optimization,
to the Ackley function :'a','b','c' are added to Ackley function inputs with x,y
variables.

We fix the parameters values in the 'p' dictionnary.

.. code-block:: python

    def ackley(x,y,a,b,c):
        fobj = -a * np.exp(-b * np.sqrt(0.5 * (np.square(x) + np.square(y)))) \
               - np.exp(0.5 * (np.cos(c * x) + np.cos(c* y))) \
               + math.exp(1) + 20
        return locals().items()

    p={'a':20.0,'b':0.2,'c':2*math.pi}

We do the same procedure as in the previous chapter, to define the
optimization problem, except that we add the parameters dictionary to
the OptimProblem class.

.. code-block:: python

    spec = Spec(variables={'x':2, 'y':2}, bounds={'x':[-5, 5], 'y':[-5, 5]},
                objectives={'fobj':[0.,15.]})
    optim = OptimProblem(model=ackley, specifications=spec,parameters=p)
    result = optim.run()
    result.printResults()


.. parsed-literal::

    Optimization terminated successfully    (Exit mode 0)
                Current function value: [6.64437582e-05]
                Iterations: 9
                Function evaluations: 20
                Gradient evaluations: 9
    {'x': 1.5781116638803522e-05, 'y': 1.739422385733534e-05}
    {'fobj': 6.644375817899117e-05}


Optimization with input vector
------------------------------

Instead of using scalar variables, we can rewrite the model function
with vector variables. In the example below,a 2-dimensions vector X is used
instead of the 2 scalar variables x,y.

.. code-block:: python

    def ackley(X,a,b,c):
        x=X[0]
        y=X[1]
        fobj = -a * np.exp(-b * np.sqrt(0.5 * (np.square(x) + np.square(y)))) \
               - np.exp(0.5 * (np.cos(c * x) + np.cos(c* y))) \
               + math.exp(1) + 20
        return locals().items()

    p={'a':20.0,'b':0.2,'c':2*math.pi}

Therefore, there are changes in the Spec class : the initial values of
variables are defined in a list, and their bounds with the following
form : [ [min coordinate1, max coordinate1], [min coordinate2, max
coordinate2] ].

.. code-block:: python

    spec = Spec(variables={'X':[2,2]}, bounds={'X':[[-5, 5],[-5, 5]]},
                objectives={'fobj':[0.,15.]})
    optim = OptimProblem(model=ackley, specifications=spec,parameters=p)
    result = optim.run()
    result.printResults()


.. parsed-literal::

    Optimization terminated successfully    (Exit mode 0)
                Current function value: [6.64437582e-05]
                Iterations: 9
                Function evaluations: 20
                Gradient evaluations: 9
    {'X': [[1.5781116638803522e-05, 1.739422385733534e-05]]}
    {'fobj': 6.644375817899117e-05}


You can mix scalar and vector variables in the same optimization
problem.

Constrained Optimization
========================

Optimization problems with constraints (equality or inequality ones) are
treated in the following chapter. See the example below with the
Rosenbrock function.

Constrained Rosenbrock function
-------------------------------

We want to minimize the Rosenbrock function subjected to 2 inequality
constraints with upper bound equals to 0 and no lower bound.

.. figure:: images/bar2.png
.. figure:: images/Rosenbrock.PNG

We define the model function below :

.. code-block:: python

    def rosenbrock(x,y):
        fobj=(1-x)*(1-x)+100*(y-x*x)**2
        ctr1=(x-1)**3-y+1
        ctr2=x+y-2
        return locals().items()

We add the inequality constraints to the problem by using the
"ineq_cstr" attribute in the Spec class. It's a dictionary with the
names and the gap of the inequality constraints ("None" indicates that
there is no lower (or upper) bound as in this example).

.. code-block:: python

    spec = Spec(variables={'x':2.0, 'y':2.0},
                bounds={'x':[-1.5, 1.5],'y':[-0.5, 2.5]},
                objectives={'fobj':[0.,15.]},
                ineq_cstr={'ctr1':[None, 0],'ctr2':[None, 0]})

    optim = OptimProblem(model=rosenbrock, specifications=spec)
    result = optim.run()
    result.printResults()


.. parsed-literal::

    Optimization terminated successfully    (Exit mode 0)
                Current function value: [2.88481749e-24]
                Iterations: 7
                Function evaluations: 14
                Gradient evaluations: 7
    {'x': 1.0000000000000566, 'y': 0.9999999999999435}
    {'fobj': 2.8848174917769927e-24, 'ctr1': 5.651035195342047e-14, 'ctr2': 0.0}


We can also define ctr1 as an equality constraint that must be equal to
0. We do this by using the "eq_cstr" of the Spec class :

.. code-block:: python

    spec = Spec(variables={'x':2.0, 'y':2.0},
                bounds={'x':[-1.5, 1.5],'y':[-0.5, 2.5]},
                objectives={'fobj':[0.,15.]}, eq_cstr={'ctr1':0},
                ineq_cstr={'ctr2':[None, 0]})

    optim = OptimProblem(model=rosenbrock, specifications=spec)
    result = optim.run()
    result.printResults()


.. parsed-literal::

    Optimization terminated successfully    (Exit mode 0)
                Current function value: [5.42085619e-09]
                Iterations: 7
                Function evaluations: 8
                Gradient evaluations: 7
    {'x': 0.9999975471448505, 'y': 1.0000024528551497}
    {'fobj': 5.420856190159052e-09, 'ctr1': -2.4528551496594275e-06, 'ctr2': 0.0}


Optimization with constrained vector
------------------------------------

Instead of using scalar constraints, we can rewrite the model function
with a constraint vector.

.. code-block:: python

    def rosenbrock(x,y):
        fobj=(1-x)*(1-x)+100*(y-x*x)**2
        ctr=[(x-1)**3-y+1 , x+y-2]
        return locals().items()

We define the gap admissible for the inequality constraints in the
"ineq_cstr" attribute of the Spec class. The syntax is the following : [
[min coordinate1, max coordinate1], [min coordinate2, max coordinate2]
].

.. code-block:: python

    spec = Spec(variables={'x':2.0, 'y':2.0},
                bounds={'x':[-1.5, 1.5],'y':[-0.5, 2.5]},
                objectives={'fobj':[0.,15.]},
                ineq_cstr={'ctr':[[None, 0],[None, 0]]})

    optim = OptimProblem(model=rosenbrock, specifications=spec)
    result = optim.run()
    result.printResults()


.. parsed-literal::

    Optimization terminated successfully    (Exit mode 0)
                Current function value: [2.88481749e-24]
                Iterations: 7
                Function evaluations: 14
                Gradient evaluations: 7
    {'x': 1.0000000000000566, 'y': 0.9999999999999435}
    {'fobj': 2.8848174917769927e-24, 'ctr': [5.651035195342047e-14, 0.0]}


OptimizeParam
-------------

OptimizeParam is a function that solves all optimization problems
according to an input varying in a range of values, while the others
remain constants.

The model function is defined below.

.. code-block:: python

    def rosenbrock(x,y):
        fobj=(1-x)*(1-x)+100*(y-x*x)**2
        ctr1=(x-1)**3-y+1
        ctr2=x+y-2
        return locals().items()

We define the Spec class with only constant variables (not the varying
one) in the "variables" and "bounds" attributes, and only the objective
(not the constraints). The attributes for the optimizeParam function are
: the "model" function, the "specifications" defined by the Spec class,
the fixed parameters (optional) in "parameters", the name of the varying
variable in "variable", a vector with all the values that the "variable"
can take in "range", and the names of the objective function and
constraints in "outputs".

.. code-block:: python

    from noloadj.optimization.optimProblem import optimizeParam

    spec = Spec(variables={'y':2.0}, bounds={'y':[-0.5, 2.5]}, objectives={'fobj':[0.,15.]})

    iter = optimizeParam(model=rosenbrock, specifications=spec,
                         parameters={}, variable='x',
                         range=np.arange(-1.5, 2.0, 0.5), #[-1.5,-1,...,1.5]
                         outputs=['fobj', 'ctr1', 'ctr2'])


We display the results with the "print" function.

.. code-block:: python

    df=iter.print()
    print(df)
.. parsed-literal::

    |    |    x |   fobj |    ctr1 |   ctr2 |
    |---:|-----:|-------:|--------:|-------:|
    |  0 | -1.5 |   6.25 | -16.875 |  -1.25 |
    |  1 | -1   |   4    |  -8     |  -2    |
    |  2 | -0.5 |   2.25 |  -2.625 |  -2.25 |
    |  3 |  0   |   1    |   0     |  -2    |
    |  4 |  0.5 |   0.25 |   0.625 |  -1.25 |
    |  5 |  1   |   0    |   0     |   0    |
    |  6 |  1.5 |   0.25 |  -1.125 |   1.75 |

We display the results graphically with the "plotXY" function.

.. code-block:: python

    iter.plotXY()

.. figure:: images/output_96_0.png

.. figure:: images/output_96_2.png


FreeOutputs(XML)
----------------

Suppose that in your problem, there are outputs you want to see the values
accross iterations but you don't want to constraint them.
These are called "freeOutputs".

.. code-block:: python

    def rosenbrock(x,y):
        fobj=(1-x)*(1-x)+100*(y-x*x)**2
        ctr1=(x-1)**3-y+1
        ctr2=x+y-2
        return locals().items()

Back to the Rosenbrock optimization problem, we define ctr1 as an
equality constraint and ctr2 as a freeOutput. It is done by using the
"freeOutputs" attribute in the Spec class.

.. code-block:: python

    spec = Spec(variables={'x':2.0, 'y':2.0},
                bounds={'x':[-1.5, 1.5],'y':[-0.5, 2.5]},
                objectives={'fobj':[0.,15.]},
                eq_cstr={'ctr1': 0},freeOutputs=['ctr2'])

.. code-block:: python

    optim = OptimProblem(model=rosenbrock, specifications=spec)
    result = optim.run()
    result.printResults()

.. parsed-literal::

    Optimization terminated successfully    (Exit mode 0)
                Current function value: [5.19862556e-09]
                Iterations: 10
                Function evaluations: 11
                Gradient evaluations: 10
    {'x': 0.9999963993636343, 'y': 0.9999999998935956}
    {'fobj': 5.198625557105132e-09, 'ctr1': 1.0640444081388978e-10, 'ctr2': -3.6007427701711947e-06}


The getIteration function is very useful to print the value of the
freeOutput at a certain iteration (for instance, the 4th one in the code
below).

.. code-block:: python

    inp,out,fp=result.getIteration(4)
    print('inp=',inp)
    print('out=',out)
    print('fp=',fp)

.. parsed-literal::

    inp= {'x': 0.7239575043144895, 'y': 0.9974823725823181}
    out= {'fobj': 22.483916763247052, 'ctr1': -0.01851666153168452}
    fp= {'ctr2': -0.27856012310319245}


You can export the results in the XML format by using the
"exportToXML" function.

.. code-block:: python

    result.exportToXML("rosenbrock.result")

In your work folder, a XML file named 'rosenbrock.result' will appear.
You can open it and see that all inputs and outputs values are printed for each
iteration of the optimization.

Multi-Objective Optimization
============================

NoLoad can also solve multi-objective optimization problems. See the
example below with the Binh and Korn function.

Binh and Korn function
----------------------

.. figure:: images/BinhAndKorn.png

We define the Binh and Korn function with 2 objective functions and 2
inequality constraints.

.. code-block:: python

    def BinhAndKorn(x, y):
        f1 = 4*x**2+4*y**2
        f2 = (x-5)**2+(y-5)**2
        g1 = (x-5)**2+y
        g2 = (x-8)**2+(y+3)**2
        return locals().items()

We do the procedure described in the previous parts, except that the
"objectives" attribute is a list of 2 elements, each one is the name of
an objective function.

.. code-block:: python

    spec = Spec(variables={'x':0, 'y':0}, bounds={'x':[0, 5], 'y':[0, 3]},
                objectives={'f1':[0.,140.],'f2':[0.,50.]},
                ineq_cstr={'g1':[None, 25],'g2':[7.7, None]})

    optim = OptimProblem(model=BinhAndKorn, specifications=spec)
    result = optim.run()


.. parsed-literal::

    Optimization terminated successfully    (Exit mode 0)
                Current function value: 0.0
                Iterations: 1
                Function evaluations: 1
                Gradient evaluations: 1
    Optimization terminated successfully    (Exit mode 0)
                Current function value: [4.]
                Iterations: 2
                Function evaluations: 2
                Gradient evaluations: 2
    Singular matrix C in LSQ subproblem    (Exit mode 6)
                Current function value: 50.0
                Iterations: 1
                Function evaluations: 1
                Gradient evaluations: 1
    WARNING : Optimization doesn't converge... Trying random inital guess
    Optimization terminated successfully    (Exit mode 0)
                Current function value: [13.72381047]
                Iterations: 8
                Function evaluations: 10
                Gradient evaluations: 8
    Optimization terminated successfully    (Exit mode 0)
                Current function value: [5.69821164]
                Iterations: 5
                Function evaluations: 6
                Gradient evaluations: 5
    Optimization terminated successfully    (Exit mode 0)
                Current function value: [8.13884001]
                Iterations: 7
                Function evaluations: 7
                Gradient evaluations: 7


| To print the Pareto front, we use the "plotPareto" function of the result class.
| ['Pareto'] is the legend of the graph and 'Pareto Front' its title.

.. code-block:: python

    result.plotPareto(['BinhAndKorn'],'Pareto Front')

.. figure:: images/output_117_0.png


To get the inputs and outputs at a point, "getIteration" function is
useful. For instance, the 2nd point from the left corresponds to the 2nd
iteration of the multi-objective optimization, as shown below.

.. code-block:: python

    inp,out=result.getIteration(2)
    print('inp=',inp)
    print('out=',out)

.. parsed-literal::

    inp= {'x': 1.0086280321907704, 'y': 1.0086523159535503}
    out= {'f1': 8.138840007197945, 'f2': 31.861906520356282, 'g1': 16.939702501366874, 'g2': 64.94857538246845}


You can select the number of Pareto points to print in the graph with
the "nbParetoPoints" attribute of the optim.run function (by default,
nbParetoPts=5). With the "disp" attribute set to False, the message
"Optimization terminated successfully" is not printed. You can also change solving
method ('epsconstr' by default, or 'ponderation').

.. code-block:: python

    optim = OptimProblem(model=BinhAndKorn, specifications=spec)

    result = optim.run(disp=False,nbParetoPts=6,method2d='ponderation')

    result.plotPareto(['6points'],'Pareto Front',nb_annotation=6)

.. parsed-literal::

    WARNING : Optimization doesn't converge... Trying random inital guess



.. figure:: images/output_121_1.png


Display several curves in the same graph
----------------------------------------

You can print several Pareto fronts in the same graph. For example,
suppose we add a parameter "a" to the Binh and Korn function and we want
to do 3 Pareto fronts with differents values of a.

.. code-block:: python

    def BinhAndKorn(x, y, a):
        f1 = a*x**2+a*y**2
        f2 = (x-5)**2+(y-5)**2
        g1 = (x-5)**2+y
        g2 = (x-8)**2+(y+3)**2
        return locals().items()

.. code-block:: python

    p = {'a':4}
    optim = OptimProblem(BinhAndKorn, spec, p)
    result1 = optim.run(disp=False)

    p = {'a':6}
    optim = OptimProblem(BinhAndKorn, spec, p)
    result2 = optim.run(disp=False)

    p = {'a':8}
    optim = OptimProblem(BinhAndKorn, spec, p)
    result3 = optim.run(disp=False)

.. parsed-literal::

    WARNING : Optimization doesn't converge... Trying random inital guess
    WARNING : Optimization doesn't converge... Trying random inital guess
    WARNING : Optimization doesn't converge... Trying random inital guess


We plot the final results after adding the previous result classes in the
addParetoList method.

.. code-block:: python

   result3.addParetoList(result1,result2)
   result3.plotPareto(['a=4','a=6','a=8'],'Comparaison')

.. figure:: images/output_128_0.png


To avoid annotations on the graph, you can hide them by
putting with the "nb_annotation" attribute of the plotPareto.function
equal to 0. The "joinDots" attribute put to False do not connect dots on the graph.

.. code-block:: python

    result3.plotPareto(['a=4','a=6','a=8'],'Comparaison',nb_annotation = 0)

.. figure:: images/output_130_0.png

