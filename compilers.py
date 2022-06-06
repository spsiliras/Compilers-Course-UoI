#Spiridon Siliras 3330


import string



alphaUpper = list(string.ascii_uppercase)
alphaLower = list(string.ascii_lowercase)
digits = list(string.digits)
operators = ['+','-','*','/']
logical_op = ['<','>','<=','>=','<>']
separators = [':']
identifiers = ['+','-','=',';',',','(', ')', '[', ']', '{', '}']
comms = ['/*','*/','//']
whitespace = list(string.whitespace)

pos = 0
programtk = 'program'
declaretk = 'declare'
iftk = 'if'
elsetk = 'else'
whiletk = 'while'
doublewhiletk = 'doublewhile'
looptk = 'loop'
exittk = 'exit'
forcasetk = 'forcase'
incasetk = 'incase'
whentk = 'when'
defaulttk = 'default'
nottk = 'not'
andtk = 'and'
ortk = 'or'
functiontk = 'function'
proceduretk = 'procedure'
calltk = 'call'
returntk = 'return'
intk = 'in'
inouttk = 'inout'
inputtk = 'input'
printtk = 'print'

def lex():
    global pos
    f = open('test.txt', 'r')
    f.seek(pos)
    lexeme = ''
    state0 = 0
    state1 = 1
    state2 = 2
    state3 = 3
    state4 = 4
    state5 = 5
    state6 = 6
    state7 = 7
    state8 = 8

    OK = -1
    error = -2

    state = state0

    

    keywords = ['program','declare','if','else','while','doublewhile','loop','exit','forcase','incase','when','default','not','and','or','function','procedure','call','return','in','inout','input','print']

    while(state != OK and state != error):
    
            input = f.read(1)
            if(state == state0 and (input in alphaUpper+alphaLower)):
            
                    state = state1
                    lexeme += input
            
            elif(state == state0 and input in digits):
            
                    state = state2
                    lexeme += input
            
            elif(state == state0 and input in identifiers):
                    
                    pos = f.tell()
                    return input
            
            elif(state == state0 and input == '*'):
            
                    state = state3
                    lexeme += '*'
            
            elif(state == state0 and input == '/'):
            
                    state = state4
            
            elif(state == state0 and input == '<'):
            
                    state = state5
                    lexeme += '<'
            
            elif(state == state0 and input == '>'):
            
                    state = state6
                    lexeme += '>'
            
            elif(state == state0 and input == ':'):
            
                    state = state7
                    lexeme += ':'
            
            elif(state == state1 and input in alphaUpper+alphaLower+digits):
            
                    state = state1
                    lexeme += input
            
            elif(state == state1 and input not in alphaUpper+alphaLower+digits):
            
                    pos = f.tell() - 1
                    return lexeme[:30]
            
            elif(state == state2 and input in digits):
            
                    state = state2
                    lexeme += input
            
            elif(state == state2 and input not in digits):
            
                    pos = f.tell() - 1
                    return lexeme[:17]
            
            elif(state == state3 and input == '/'):	
            
                    state = state0
                    
            
            elif(state == state3):
            
                    pos = f.tell() - 1
                    return lexeme[:30]
            
            elif(state == state4 and input == '*'):
            
                    state = state8
            
            elif(state == state8 and input != '*'):
            	state = state8

            elif(state == state8 and input == '*'):
                if(f.read(1) == '/'):
                    state = state0
                else:
                    state = state8
                    pos = f.tell() - 1
            
            elif(state == state4 and input == '/'):
            
                    f.readline()
                    state = state0
            
            elif(state == state4):
            
                    pos = f.tell() - 1
                    return lexeme[:30]
            
            elif(state == state5 and input == '='):
            
                    pos = f.tell()
                    return '<='
            
            elif(state == state5 and input == '>'):
            
                    pos = f.tell()
                    return '<>'
            
            elif(state == state5):
            
                    pos = f.tell() - 1
                    return lexeme[:30]
            
            elif(state == state6 and input == '='):
            
                    pos = f.tell()
                    return '<='
            
            elif(state == state6):
                    
                    pos = f.tell() - 1
                    return lexeme[:30]
            
            elif(state == state7 and input == '='):
                    
                    pos = f.tell()
                    return ':='
            
            elif(state == state7):
                    
                    pos = f.tell() - 1
                    return lexeme[:30]
            
            elif(state == state0 and input in whitespace):
                state = state0
            else:
                state == error
            


def program():
    token = lex()
    if(token == programtk):
        token = lex()
        if(token[0] in alphaUpper+alphaLower):
            token = lex()
            if(token == '{'):
                token = lex()
                block()
                if(token == '}'):
                    token = lex()
                else:
                    print("} expected")
            else:
                print("{ expected")
        else:
            print("Program name expected")
    else:
        print("Keyword program expected")

def block():
    declarations()
    subprograms()
    statements()

def declarations():
    while(token == declaretk):
        token = lex()
        varlist()
        if(token == ';'):
            token = lex()
        else:
            print("; expected")

def varlist():
    if(token[0] in alphaLower + alphaUpper):
        token = lex()
        while(token != ';'):
            if(token == ','):
                token = lex()
                if(token[0] in alphaUpper + alphaLower):
                    token = lex()
                else:
                    print("Variable name expected")
            else:
                print(", expected")

def subprograms():
    while(token == functiontk or token == proceduretk):
        subprogram()

def subprogram():
    if(token == functiontk):
        token = lex()
        if(token[0] in alphaLower+alphaUpper):
            token = lex()
            funcbody()
        else:
            print("Function name expected")
    else:
        print("Keyword function expected")

    elif(token == proceduretk):
        token = lex()
        if(token[0] in alphaUpper+alphaLower):
            token = lex()
            funcbody()
        else:
            print("Procedure name expected")
    else:
        print("Keyword procedure expected")

def funcbody():
    formalpars()
    if(token == '{'):
        token = lex()
        block()
        if(token == '}'):
            token = lex()
        else:
            print("} expected")
    else:
        print("{ expected")

def formalpars():
    if(token == '('):
        token = lex()
        formalparlist()
        if(token == ')'):
            token = lex()
        else:
            print(") missing")
    else:
        print("( expected")

def formalparlist():
    if(token != ')'):
        formalparitem()
        while(token == ','):
            token = lex()
            formalparitem()

def formalparitem():
    if(token == intk):
        token = lex()
        if(token[0] in alphaUpper+alphaLower):
            token = lex()
        else:
            print("Parameter name expected")
    else:
        print("Keyword in expected")

    elif(token == inouttk):
        token = lex()
        if(token[0] in alphaUpper+alphaLower):
            token = lex()
        else:
            print("Parameter name expected")
    else:
        print("Keyword inout expected")

def statements():
    if(token == '{'):
        token = lex()
        statement()
        while(token != '}'):
            if(token == ';'):
                token = lex()
                statement()
            else:
                print("; expected")
    else:
        statement()

def statement():
    if(token == iftk):
        if_stat()
    elif(token == whiletk):
        while_stat()
    elif(token == doublewhiletk):
        doublewhile_stat()
    elif(token == looptk):
        loop_stat()
    elif(token == exittk):
        exit_stat()
    elif(token == forcasetk):
        forcase_stat()
    elif(token == incasetk):
        incase_stat()
    elif(token == calltk):
        call_stat()
    elif(token == returntk):
        return_stat()
    elif(token == inputtk):
        input_stat()
    elif(token == printtk):
        print_stat()
    else:
        assignment_stat()
    
def assignment_stat():
    if(token[0] in alphaUpper+alphaLower):
        token = lex()
        if(token == ':='):
            token = lex()
            expression()
        else:
            print(":= expected")
    else:
        print("Assignment name expected")

def if_stat():
    token = lex()
    if(token == '('):
        token = lex()
        condition()
        if(token == ')'):
            token = lex()
            if(token == 'then'):
                token = lex()
                statements()
                elsepart()
            else:
                print("Missing keyword then")
        else:
            print(") expected")
    else:
        print("( expected")

def elsepart():
    if(token == elsetk):
        token = lex()
        statements()

def while_stat():
    token = lex()
    if(token == '('):
        token = lex()
        condition()
        if(token == ')'):
            token = lex()
            statements()
        else:
            print(") missing")
    else:
        print("( missing")

def doublewhile_stat():
    token = lex()
    if(token == '('):
        token = lex()
        condition()
        if(token == ')'):
            token = lex()
            statements()
            if(token == elsetk):
                token = lex()
                statements()
            else:
                print("Keyword else missing")
        else:
            print(") expected")
    else:
        print("( expected")

def loop_stat():
    token = lex()
    statements()

def exit_stat():
    token = lex()

def forcase_stat():
    token = lex()
    while(token == whentk):
        token = lex()
        if(token == '('):
            token = lex()
            condition()
            if(token == ')'):
                token = lex()
                if(token == ':'):
                    token = lex()
                    statements()
                else:
                    print(": expected")
            else:
                print(") expected")
        else:
            print("( expected")

    if(token == defaulttk):
        token = lex()
        if(token == ':'):
            token = lex()
            statements()
        else:
            print(": expected")
    else:
        print("Keyword default expected")

def incase_stat():
    token = lex()
    while(token == whentk):
        token = lex()
        if(token == '('):
            token = lex()
            condition()
            if(token == ')'):
                token = lex()
                if(token == ':'):
                    token = lex()
                    statements()
                else:
                    print(": expected")
            else:
                print(") expected")
        else:
            print("( expected")

def return_stat():
    token = lex()
    expression()

def call_stat():
    token = lex()
    if(token[0] in alphaUpper+alphaLower):
        token = lex()
        actualpars()
    else:
        print("Call name expected")

def print_stat():
    token = lex()
    if(token == '('):
        token = lex()
        expression()
        if(token == ')'):
            token = lex()
        else:
            print(") expected")
    else:
        print("( expected")

def input_stat():
    token = lex()
    if(token == '('):
        token = lex()
        if(token[0] in alphaUpper+alphaLower):
            token = lex()
            if(token == ')'):
                token = lex()
            else:
                print(") missing")
        else:
            print("Wrong type of input")
    else:
        print("( missing")

def actualpars():
    if(token == '('):
        token = lex()
        actualparlist()
        if(token == ')'):
            token = lex()
        else:
            print(") expected")
    else:
        print("( expected")

def actualparlist():
    if(token != ')'):
        actualparitem()
        while(token == ','):
            token = lex()
            actualparitem()

def actualparitem():
    if(token == intk):
        token = lex()
        expression()
    elif(token == inouttk):
        token = lex()
        if(token[0] in alphaUpper+alphaLower):
            token =lex()
        else:
            print("inout name expected")

def condition():
    boolterm()
    while(token == ortk):
        token = lex()
        boolterm()

def boolterm():
    boolfactor()
    while(token == andtk):
        token = lex()
        boolfactor()

def boolfactor():
    if(token == nottk):
        token = lex()
        if(token == '['):
            token = lex()
            condition()
            if(token == ']'):
                token = lex()
            else:
                print("] expected")
        else:
            print("[ expected")
    
    elif(token == '['):
        token = lex()
        condition()
        if(token == ']'):
            token = lex()
        else:
            print("] expected")

    else:
        expression()
        relational_oper()
        expression()

def expression():
    optional_sign()
    term()
    while(token == '+' or token == '-'):
        add_oper()
        term()

def term():
    factor()
    while(token == '*' or token == '/'):
        mul_oper()
        factor()

def factor():
    if(token[0] in digits):
        token = lex()
    elif(token == '('):
        token = lex()
        expression()
        if(token == ')'):
            token = lex()
        else:
            print(") expected")
    else:
        if(token[0] in alphaUpper+alphaLower):
            token = lex()
            idtail()
        else:
            print("factor name expected")

def idtail():
    actualpars()

def relational_oper():
    if(token == '='):
        token = lex()
    elif(token == '<='):
        token = lex()
    elif(token == '>='):
        token = lex()
    elif(token == '>'):
        token = lex()
    elif(token == '<'):
        token = lex()
    elif(token = '<>'):
        token = lex()

def add_oper():
    if(token == '+'):
        token = lex()
    elif(token == '-'):
        token = lex()

def mul_oper():
    if(token == '*'):
        token = lex()
    elif(token == '/'):
        token = lex()

def optional_sign():
    if(token == '+' or token == '-'):
        add_oper()
