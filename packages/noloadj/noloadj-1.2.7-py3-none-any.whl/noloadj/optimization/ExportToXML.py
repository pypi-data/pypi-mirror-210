from xml.dom import minidom
from noloadj.optimization.wrapper import Iterations

def resultsToXML(iter: Iterations, fileName):
    """
    Return an XMLfile compatible with CADES. This can be used to plot geometry
    in GeomMaker.
    :param fileName: the filename to save XML tree
    :return: /
    """
    iterNb = len(iter.solutions)
    root = minidom.Document()
    xml = root.createElement('Optimization')
    root.appendChild(xml)
    #<Iterations Number="12">
    iterations = root.createElement('Iterations')
    iterations.setAttribute('Number', str(iterNb))
    xml.appendChild(iterations)

    #<Iteration Number="0" isBestSolution="false" isSolution="false">
    number = 0  # numéro de l'itération
    for sol in iter.solutions:
        if len(iter.iNames) == iterNb:
            isBestSolution="true"   #on suppose qu'un algo type SQP est utilisé
            # conduisant à avoir la meilleure solution à la dernière itération
        else:
            isBestSolution="false"
        isSolution = "true" #true par défaut, il faudrait verifier si les
        # contraintes sont violées ou pas.
        iteration = root.createElement('Iteration')
        iteration.setAttribute('Number', str(number))
        iteration.setAttribute('isBestSolution', isBestSolution)
        iteration.setAttribute('isSolution', isSolution)
        iterations.appendChild(iteration)
        number = number + 1

        #<Inputs Number="22">
        inputs = root.createElement('Inputs')
        inputs.setAttribute('Number', str(len(iter.iNames)))
        iteration.appendChild(inputs)
        iCmpt = 0
        #<Input Value="250000.0" Name="S"/>
        for inputVal in sol.iData:
            input = root.createElement('Input')
            input.setAttribute('Value', str(inputVal))
            input.setAttribute('Name', iter.iNames[iCmpt])
            inputs.appendChild(input)
            iCmpt=iCmpt+1

        #<Outputs Number="116">
        outputs = root.createElement('Outputs')
        outputs.setAttribute('Number', str(len(iter.oNames)+len(iter.fNames)))
        iteration.appendChild(outputs)
        oCmpt = 0
        #<Output Value="1.25663704E-6" Name="mu0"/>
        for outputVal in sol.oData:
            output = root.createElement('Output')
            output.setAttribute('Value', str(outputVal))
            output.setAttribute('Name', iter.oNames[oCmpt])
            outputs.appendChild(output)
            oCmpt=oCmpt+1
        oCmpt = 0
        for outputVal in sol.fData:
            output = root.createElement('Output')
            output.setAttribute('Value', str(outputVal))
            output.setAttribute('Name', iter.fNames[oCmpt])
            outputs.appendChild(output)
            oCmpt=oCmpt+1
    #< SPECIFICATIONS >
    spec = root.createElement('SPECIFICATIONS') #not used but required
    xml.appendChild(spec)

    objs = root.createElement('Objective functions')
    objs.setAttribute('Number',str(len(iter.objectives)))
    spec.appendChild(objs)

    for name,value in iter.objectives.items():
        obj = root.createElement('Objective')
        obj.setAttribute('Value', str(value))
        obj.setAttribute('Name', name)
        objs.appendChild(obj)

    if iter.eq_cstr!={}:
        eqs = root.createElement('Equality Constraints')
        eqs.setAttribute('Number', str(len(iter.eq_cstr)))
        spec.appendChild(eqs)

        for name,value in iter.eq_cstr.items():
            eq = root.createElement('Equality Constraint')
            eq.setAttribute('Value', str(value))
            eq.setAttribute('Name', name)
            eqs.appendChild(eq)

    if iter.ineq_cstr!={}:
        ineqs = root.createElement('Inequality Constraints')
        ineqs.setAttribute('Number', str(len(iter.ineq_cstr)))
        spec.appendChild(ineqs)

        for name, value in iter.ineq_cstr.items():
            ineq = root.createElement('Inequality Constraint')
            ineq.setAttribute('Value', str(value))
            ineq.setAttribute('Name', name)
            ineqs.appendChild(ineq)

    if iter.fNames!=[]:
        fOuts = root.createElement('Free Outputs')
        fOuts.setAttribute('Number', str(len(iter.fNames)))
        spec.appendChild(fOuts)

        for name in iter.fNames:
            fOut=root.createElement('Free Output')
            fOut.setAttribute('Name', name)
            fOuts.appendChild(fOut)

    xml_str = root.toprettyxml(indent ="\t")
    with open(fileName, "w") as f:
        f.write(xml_str)
