import sympy as sym

# brass
inp_dict={
    "D_{o}":3.17*10**-3,
    "D_{u}":2.73*10**-3,
    "D_{f}":2.01*10**-3,
    "L_{o}":20*10**-3,
    "L_{f}":28.6*10**-3,
    "F_{y}":1570,
    "F_{u}":3140,
    "F_{f}":2750,
    "L_{y}":0.49*10**-3,
    "L_{p}":8.95*10**-3,
    "L_{u}":6.95*10**-3,
    "E_{true}":101*10**9
}

unit_dict={
    
}

uncert_dict={
    "D_{o}":0.01*10**-3,
    "D_{u}":0.01*10**-3,
    "D_{f}":0.01*10**-3,
    "L_{o}":0.2*10**-3,
    "L_{f}":0.2*10**-3,
    "F_{y}":10,
    "F_{u}":10,
    "F_{f}":10,
    "L_{y}":0.01*10**-3,
    "L_{p}":0.01*10**-3,
    "L_{u}":0.01*10**-3,
}

execution_queue=[
    ("A_{o}",sym.pi*(sym.Symbol("D_{o}")/2)**2),
    ("A_{u}",sym.pi*(sym.Symbol("D_{u}")/2)**2),
    ("A_{f}",sym.pi*(sym.Symbol("D_{f}")/2)**2),
    ("~sigma~_{y}",sym.Symbol("F_{y}")/sym.Symbol("A_{o}")),
    ("~sigma~_{u}",sym.Symbol("F_{u}")/sym.Symbol("A_{o}")),
    ("~sigma~_{tu}",sym.Symbol("F_{u}")/sym.Symbol("A_{u}")),
    ("~sigma~_{f}",sym.Symbol("F_{f}")/sym.Symbol("A_{f}")),
    ("percent_reduction_in_area",100*(sym.Symbol("A_{o}")-sym.Symbol("A_{f}"))/sym.Symbol("A_{o}")),
    ("measured_total_percent_elongation",100*(sym.Symbol("L_{f}")-sym.Symbol("L_{o}"))/sym.Symbol("L_{o}")),
    ("chart_total_percent_elongation",100*(sym.Symbol("L_{p}"))/sym.Symbol("L_{o}")),
    ("E",sym.Symbol("~sigma~_{y}")/(sym.Symbol("L_{y}")/sym.Symbol("L_{o}"))),
    ("T_{R}",(sym.Symbol("~sigma~_{y}")**2)/(2*sym.Symbol("E_{true}"))),
    ("T_{U}",sym.Symbol("L_{p}")*(sym.Symbol("~sigma~_{y}")+sym.Symbol("~sigma~_{u}"))/(2*sym.Symbol("L_{o}"))),
    ("~epsilon~_{u}",sym.ln(sym.Symbol("A_{o}")/sym.Symbol("A_{u}"))),
    ("~epsilon~_{f}",sym.ln(sym.Symbol("A_{o}")/sym.Symbol("A_{f}"))),
    ("~epsilon~_{une}",sym.exp(sym.Symbol("~epsilon~_{u}"))-1),
]


log=True

log_board=[]

def purifyed_latex(func):
    txt=sym.latex(func)
    ret=""
    counter=0
    for i in range(len(txt)):
        if(txt[i]=="~"):
            ret+="\\" if counter%2==0 else " "
            counter+=1
        else:
            ret+=txt[i]
    return ret
    
    
def execute_computation(result_name,expression):
    if log: log_entry = ["\Delta "+result_name]
    final_value=expression
    for (k,v) in inp_dict.items(): 
        final_value=final_value.subs(sym.Symbol(k),v)
    final_value=sym.N(final_value,20)

    final_error=0
    for symbol in expression.free_symbols:
        key=str(symbol)
        if not key in uncert_dict: continue
        partial="~frac~{~delta~"+result_name+"}{~delta~"+key+"}"
        final_error = final_error + (sym.Symbol(partial)*( sym.Symbol("~Delta~"+key)))**2
    final_error=sym.sqrt(final_error)

    if log: log_entry[0]+="&="+purifyed_latex(final_error)

    for symbol in expression.free_symbols:
        key=str(symbol)
        if not key in uncert_dict: continue
        partial="~frac~{~delta~"+result_name+"}{~delta~"+key+"}"
        final_error = final_error.subs(sym.Symbol(partial),sym.diff(expression,sym.Symbol(key)))

    if log: log_entry.append(purifyed_latex(final_error))

    for (k,v) in inp_dict.items(): 
        final_error=final_error.subs(sym.Symbol(k),v)

    for (k,v) in uncert_dict.items(): 
        final_error=final_error.subs(sym.Symbol("~Delta~"+k),v)
    final_error=sym.N(final_error,20)
    
    if log: log_board.append("\\begin{align*}%s\\end{align*}\n"%("\\\\&=".join(log_entry)))
    return(final_value,final_error)

for computation_entry in execution_queue:
    result_name,expression = computation_entry
    key_value, key_uncertainty = execute_computation(result_name,expression)
    inp_dict[result_name]=key_value
    uncert_dict[result_name]=key_uncertainty
    print("%-50s:%20.9f ± %20.9f"%(result_name,key_value,key_uncertainty))

if log:
    with open("log.txt","w+") as fi:
        for l in log_board:
            fi.write(l)