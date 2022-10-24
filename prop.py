import sympy as sym

from input_data import *

log=True

log_board=[]

def purifyed_latex(expression,is_expression=True):
    if is_expression: txt=sym.latex(expression)
    else: txt=expression
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
    if log: 
        log_entry=[purifyed_latex(result_name,False)+"&="+purifyed_latex(expression)]
        delta_log_entry = ["\Delta "+purifyed_latex(result_name,False)]
    final_value=expression
    for (k,v) in inp_dict.items(): 
        final_value=final_value.subs(sym.Symbol(k),v)
    final_value=sym.N(final_value,20)

    final_error=0
    for symbol in expression.free_symbols:
        key=str(symbol)
        if not key in uncert_dict: continue
        partial="~left~(~frac~{~delta~"+result_name+"}{~delta~"+key+"}~right~)"
        final_error = final_error + (sym.Symbol(partial)*( sym.Symbol("~Delta~"+key)))**2
    final_error=sym.sqrt(final_error)

    if log: delta_log_entry[0]+="&="+purifyed_latex(final_error)

    for symbol in expression.free_symbols:
        key=str(symbol)
        if not key in uncert_dict: continue
        partial="~left~(~frac~{~delta~"+result_name+"}{~delta~"+key+"}~right~)"
        final_error = final_error.subs(sym.Symbol(partial),sym.diff(expression,sym.Symbol(key)))

    if log: delta_log_entry.append(purifyed_latex(final_error))

    for (k,v) in inp_dict.items(): 
        final_error=final_error.subs(sym.Symbol(k),v)

    for (k,v) in uncert_dict.items(): 
        final_error=final_error.subs(sym.Symbol("~Delta~"+k),v)
    final_error=sym.N(final_error,20)
    
    if log: 
        log_entry.append(str(final_value))
        delta_log_entry.append(str(final_error))
        log_board.append("\\begin{align*}%s\\end{align*}\n"%("\\\\&=".join(log_entry)))
        log_board.append("\\begin{align*}%s\\end{align*}\n"%("\\\\&=".join(delta_log_entry)))
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