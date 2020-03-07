"""
Convert Postfix notation (Reverse Polish Notation) back to Infix noation
"""
def getInfix(exp) : 
    s = []  
  
    for i in exp:      
        if i == 'NOT':
            operand1 = s[0]  
            s.pop(0)  
            s.insert(0, "" + i + ' ' + operand1 + "")  
        elif i == 'AND' or i == 'OR': 
            operand1 = s[0]  
            s.pop(0)  
            operand2 = s[0]  
            s.pop(0)  
            s.insert(0, "(" + operand2 + ' ' + i + ' ' + operand1 + ")")  
        else :          
            s.insert(0, i)  
              
    return s[0] 



exp = [',', 'the', 'AND', 'in', 'and', 'AND', 'for', 'come', 'AND', 'NOT', 'NOT', 'in', 'and', 'AND', 'in', 'or', 'AND', 'NOT', 'NOT', 'AND', 'AND', 'AND', 'AND']

print(getInfix(exp))
