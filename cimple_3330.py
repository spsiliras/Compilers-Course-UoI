#Spyridon Siliras 3330 (cs03330)

import string
import sys

alphaUpper = list(string.ascii_uppercase)
alphaLower = list(string.ascii_lowercase)
digits = list(string.digits)

keyword = ['program','declare','if','else','while','switchcase','forcase','incase','case','default','not','and','or','function','procedure','call','return','in','inout','input','print']
addOperator = ['+','-']
mulOperator = ['*','/']
relOperator = ['<','>','=','<=','>=','<>']
assignment = ':='
delimiter = [';',',',':']
groupSymbol = ['[',']','(',')','{','}']
comment = '#'
programFin = '.'

#keep the current position for lex
position = 0
#fill the Token with the right line
line = 1

#write symbols table to file
symbolsTable = open('scopes.txt', 'w')

class Token:

	def __init__(self, tokenType, tokenString, lineNo):
		self.tokenType = tokenType
		self.tokenString = tokenString
		self.lineNo = lineNo

class Entity:

	def __init__(self, *args):

		if args[0] == 'variable':
			self.type = args[0]
			self.name = args[1]
			self.offset = args[2]

		elif args[0] == 'function':
			self.type = args[0]
			self.name = args[1]
			self.startQuad = args[2]
			self.nestingLevel = args[3]
			self.argument = []
			self.framelength = 0

		elif args[0] == 'parameter':
			self.type = args[0]
			self.name = args[1]
			self.parMode = args[2]
			self.offset = args[3]

		elif args[0] == 'tmpvar':
			self.type = args[0]
			self.name = args[1]
			self.offset = args[2]

class Scope:

	def __init__(self, nestingLevel):
		self.entities = []
		self.nestingLevel = nestingLevel
		self.offset = 12

class Argument:

	def __init__(self, parMode):
		self.parMode = parMode

#this variable is responsible for the number of nextquad
countQuads = 0

#keeps the intermediate code quads
programQuads = []

#temporary variables counter
countTemp = 0

#this is the symbol's table
scopes = []

#this global variable keeps the nesting level of table scopes
nesting = 0

#this global variable keeps the final code quads (MIPS)
mipsQuads = []

def nextquad():
	return countQuads

def genquad(op, x, y, z):
	global countQuads
	
	label = countQuads
	quad = [label, op, x, y, z]
	programQuads.append(quad)
	countQuads += 1

def newtemp():
	global countTemp
	countTemp += 1
	tmp = "T_" + str(countTemp)

	#add new entity
	e = Entity('tmpvar', tmp, scopes[nesting].offset)
	scopes[nesting].entities.append(e)
	scopes[nesting].offset += 4

	return tmp

def emptylist():
	return []

def makelist(x):
	return [x]

def merge(list1, list2):
	return list1+list2

def backpatch(list, z):
	for i in list:
		programQuads[i][4] = str(z)

#this function returns an array of this format [nestingLevel, Entity]
#where Entity is the searching Entity class item, and nestingLevel his nesting level
def search_entity(name):
	global nesting

	count = nesting
	while count >= 0:

		for entity in scopes[count].entities:
			if entity.name == name:
				if entity.type == 'function':
					return [entity.nestingLevel, entity]
				else:
					return [count, entity]

		#if we not find something with that name , print error message
		if count == 0:
			print("There is no Entity with the name "+name+"!\n\n")

		count -= 1

#check if calling function parameters match with the formal parameters
def check_function_parameters(name, index):
	e = search_entity(name)
	#e = [nestingLevel, Entity]
	entity = e[1]

	start = index-1
	count = 0

	if programQuads[start][3] == 'RET':
		start = index-2

	while programQuads[start][1] == 'par':
		start -= 1
		count += 1

	if count != len(entity.argument):
		print("Function named "+name+" arguments differ from formal function parameters!")

	i = 0
	while(programQuads[start][1] == 'par' and programQuads[start][3] != 'RET'):
		if(programQuads[start][3] != entity.argument[i]):
			print("Call of function "+name+" has wrong actual parameters!")

		start += 1
		i += 1

#check if there are two or more entities with the same name, in the same level
def is_unique(name):
	global nesting

	for entity in scopes[nesting].entities:
		index = scopes[nesting].entities.index(entity)
		for i in scopes[nesting].entities:
			if index != scopes[nesting].entities.index(i):
				if entity.name == i.name:
					if nesting != 0:
						print("Error in declaration of function "+name+"! Two or more different entities with the name "+entity.name+"!")
					else:
						print("Two or more entities with the same name in main function!")

def gnlvcode(x):

	global nesting
	#find nesting level of this entity
	#search_entity returns an array of this format [nestingLevel, Entity]
	arr = search_entity(x)
	nestingLevel = arr[0]
	offset = arr[1].offset

	q = ['lw','$t0','-4($sp)']
	mipsQuads.append(q)
	while(nesting - nestingLevel > 1):

		mipsQuads.append(['lw','$t0','-4($t0)'])

	mipsQuads.append(['addi','$t0','$t0','-'+str(offset)])

def loadvr(v,r):

	global nesting

	#check if constant
	if(v.isdigit()):
		mipsQuads.append(['li', r, str(v)])
		return 0

	#arr[0] = nesting level of v, and arr[1] = item of class Entity
	arr = search_entity(v)
	nestingLevel = arr[0]
	entity = arr[1]

	if(nestingLevel == 0 and nesting != 0):
		mipsQuads.append(['lw', r, '-'+str(entity.offset)+'($s0)'])

	elif(nesting-nestingLevel == 0 and ((entity.type == 'parameter' and entity.parMode == 'in') or entity.type == 'tmpvar' or entity.type == 'variable')):
		mipsQuads.append(['lw', r, '-'+str(entity.offset)+'($sp)'])

	elif(entity.type == 'parameter' and entity.parMode == 'inout'):
		mipsQuads.append(['lw', '$t0', '-'+str(entity.offset)+'($sp)'])
		mipsQuads.append(['lw', r, '($t0)'])

	elif(nesting-nestingLevel >= 1 and (entity.type == 'variable' or (entity.type == 'parameter' and entity.parMode == 'in'))):
		gnlvcode(v)
		mipsQuads.append(['lw', r, '($t0)'])

	elif(nesting-nestingLevel >= 1 and entity.type == 'parameter' and entity.parMode == 'inout'):
		gnlvcode(v)
		mipsQuads.append(['lw', '$t0', '($t0)'])
		mipsQuads.append(['lw', r, '($t0)'])

def storerv(r,v):

	global nesting

	#arr[0] = nesting level of v, and arr[1] = item of class Entity
	arr = search_entity(v)
	nestingLevel = arr[0]
	entity = arr[1]

	if(nestingLevel == 0 and nesting != 0):
		mipsQuads.append(['sw', r, '-'+str(entity.offset)+'($s0)'])

	elif(nesting-nestingLevel == 0 and (entity.type == 'variable' or (entity.type == 'parameter' and entity.parMode == 'in') or entity.type == 'tmpvar')):
		mipsQuads.append(['sw', r, '-'+str(entity.offset)+'($sp)'])

	elif(nesting-nestingLevel == 0 and (entity.type == 'parameter' and entity.parMode == 'inout')):
		mipsQuads.append(['lw', '$t0', '-'+str(entity.offset)+'($sp)'])
		mipsQuads.append(['sw', r, '($t0)'])

	elif(nesting-nestingLevel >= 1 and (entity.type == 'variable' or (entity.type == 'parameter' and entity.parMode == 'in'))):
		gnlvcode(v)
		mipsQuads.append(['sw', r, '($t0)'])

	elif(nesting-nestingLevel >= 1 and (entity.type == 'parameter' and entity.parMode == 'inout')):
		gnlvcode(v)
		mipsQuads.append(['lw', '$t0', '($t0)'])
		mipsQuads.append(['sw', r, '($t0)'])

#countPar is used for counting the current par number, so as print only once in start the mips command 'addi $fp $sp framelength;
countPar = 0
#used to define the place of the command addi $fp $sp framelength in mipsQuads
index = 0

programName = None

def generate_mips_code(quad):
	global nesting, countPar, index, programName

	#its the first line of intermediate code
	#jump to main function
	if quad[0] == 0:
		mipsQuads.append(['L'])
		mipsQuads.append(['b', 'Lmain'])

	if quad[1] == 'jump':
		mipsQuads.append(['L'+str(quad[0])])
		mipsQuads.append(['b', 'L'+str(quad[4])])

	elif quad[1] in relOperator:
		mipsQuads.append(['L'+str(quad[0])])
		loadvr(quad[2], '$t1')
		loadvr(quad[3], '$t2')

		if quad[1] == '<':
			mipsQuads.append(['blt', '$t1', '$t2', 'L'+str(quad[4])])

		elif quad[1] == '>':
			mipsQuads.append(['bgt', '$t1', '$t2', 'L'+str(quad[4])])

		elif quad[1] == '<=':
			mipsQuads.append(['ble', '$t1', '$t2', 'L'+str(quad[4])])

		elif quad[1] == '>=':
			mipsQuads.append(['bge', '$t1', '$t2', 'L'+str(quad[4])])

		elif quad[1] == '=':
			mipsQuads.append(['beq', '$t1', '$t2', 'L'+str(quad[4])])

		elif quad[1] == '<>':
			mipsQuads.append(['bne', '$t1', '$t2', 'L'+str(quad[4])])

	elif quad[1] == ':=':
		mipsQuads.append(['L'+str(quad[0])])
		loadvr(quad[2], '$t1')
		storerv('$t1', quad[4])

	elif quad[1] in addOperator+mulOperator:
		mipsQuads.append(['L'+str(quad[0])])
		loadvr(quad[2], '$t1')
		loadvr(quad[3], '$t2')

		if quad[1] == '+':
			mipsQuads.append(['add', '$t1', '$t1', '$t2'])

		elif quad[1] == '-':
			mipsQuads.append(['sub', '$t1', '$t1', '$t2'])

		elif quad[1] == '*':
			mipsQuads.append(['mul', '$t1', '$t1', '$t2'])

		elif quad[1] == '/':
			mipsQuads.append(['div', '$t1', '$t1', '$t2'])

		storerv('$t1', quad[4])

	elif quad[1] == 'out':
		mipsQuads.append(['L'+str(quad[0])])
		mipsQuads.append(['li', '$v0', '1'])
		loadvr(quad[2], '$a0')
		mipsQuads.append(['syscall'])

	elif quad[1] == 'inp':
		mipsQuads.append(['L'+str(quad[0])])
		mipsQuads.append(['li', '$v0', '5'])
		mipsQuads.append(['syscall'])
		storerv('$v0', quad[2])

	elif quad[1] == 'retv':
		mipsQuads.append(['L'+str(quad[0])])
		loadvr(quad[2], '$t1')
		mipsQuads.append(['lw', '$t0', '-8($sp)'])
		mipsQuads.append(['sw', '$t1', '($t0)'])

	elif quad[1] == 'par':

		#the right offset of each parameter
		offset = 12 + 4*countPar

		mipsQuads.append(['L'+str(quad[0])])

		if countPar == 0:
			#just keep the index so when we know the name of the calling function
			#add to mipsQuads the command addi $fp, $sp, function.framelength
			mipsQuads.append([])
			index = len(mipsQuads)-1

		if quad[3] == 'CV':
			loadvr(quad[2], '$t0')
			mipsQuads.append(['sw', '$t0', '-'+str(offset)+'($fp)'])

		elif quad[3] == 'REF':
			arr = search_entity(quad[2])
			nestingLevel = arr[0]
			entity = arr[1]

			if(nesting-nestingLevel == 0 and (entity.type == 'variable' or entity.type == 'tmpvar' or (entity.type == 'parameter' and entity.parMode == 'in'))):
				mipsQuads.append(['addi', '$t0', '$sp', '-'+str(entity.offset)])
				mipsQuads.append(['sw', '$t0', '-'+str(offset)+'($fp)'])

			elif(nesting-nestingLevel == 0 and (entity.type == 'parameter' and entity.parMode == 'inout')):
				mipsQuads.append(['lw', '$t0', '-'+str(entity.offset)+'($fp)'])
				mipsQuads.append(['sw', '$t0', '-'+str(offset)+'($fp)'])

			elif((nesting-nestingLevel >= 1) and (entity.type == 'variable' or (entity.type == 'parameter' and entity.parMode == 'in') or entity.type == 'tmpvar')):
				gnlvcode(quad[2])
				misQuads.append(['sw', '$t0', '-'+str(offset)+'($fp)'])

			elif(nesting-nestingLevel >= 1 and (entity.type == 'parameter' and entity.parMode == 'inout')):
				gnlvcode(quad[2])
				mipsQuads.append(['lw', '$t0', '($t0)'])
				mipsQuads.append(['sw', '$t0', '-'+str(offset)+'($fp)'])

		elif quad[3] == 'RET':
			arr = search_entity(quad[2])
			entity = arr[1]
			mipsQuads.append(['addi', '$t0', '$sp', '-'+str(entity.offset)])
			mipsQuads.append(['sw', '$t0', '-8($fp)'])

		countPar += 1

	elif quad[1] == 'call':

		#countPar = 0, because it must be 0 for the next function call
		countPar = 0
		#search entity with function name
		arr = search_entity(quad[2])

		nestingLevel = arr[0]
		entity = arr[1]

		quadIndex = programQuads.index(quad)

		#check if parameters matching
		check_function_parameters(quad[2], quadIndex)

		#here we have to check either function have parameters or not
		if(programQuads[quadIndex - 1][1] == 'par'):

			#now we know the calling function name
			mipsQuads[index] = ['addi', '$fp', '$sp', str(entity.framelength)]
			mipsQuads.append(['L'+str(quad[0])])

		else:
			mipsQuads.append(['L'+str(quad[0])])
			mipsQuads.append(['addi', '$fp', '$sp', str(entity.framelength)])

		if(nesting - nestingLevel == 0):
			mipsQuads.append(['lw', '$t0', '-4($sp)'])
			mipsQuads.append(['sw', '$t0', '-4($fp)'])

		elif(nesting - nestingLevel != 0):
			mipsQuads.append(['sw', '$sp', '-4($fp)'])

		mipsQuads.append(['addi', '$sp', '$sp', str(entity.framelength)])
		mipsQuads.append(['jal', 'L'+str(entity.startQuad)])
		mipsQuads.append(['addi', '$sp', '$sp', '-'+str(entity.framelength)])

	elif quad[1] == 'begin_block':

		if quad[2] == programName:
			mipsQuads.append(['Lmain'])
			mipsQuads.append(['L'+str(quad[0])])

			#here we can find framelength of main function
			framelength = scopes[0].offset

			mipsQuads.append(['addi', '$sp', '$sp', str(framelength)])
			mipsQuads.append(['move', '$s0', '$sp'])

		else:
			mipsQuads.append(['L'+str(quad[0])])

			mipsQuads.append(['sw', '$ra', '($sp)'])

	elif quad[1] == 'end_block':
		if quad[2] != programName:
			mipsQuads.append(['L'+str(quad[0])])
			mipsQuads.append(['lw', '$ra', '($sp)'])
			mipsQuads.append(['jr', '$ra'])

	elif quad[1] == 'halt':
		mipsQuads.append(['L'+str(quad[0])])
		mipsQuads.append(['li', '$v0', '10'])
		mipsQuads.append(['syscall'])

#LEXER
def lex():
	global position
	global line
	f = open(str(sys.argv[1]), 'r')
	f.seek(position)

	tk = ''
	state = 'start'

	while(state != 'ok' and state != 'error'):
		input = f.read(1)

		if(state == 'start' and input in string.whitespace and input != ''):
			position = f.tell()
			if(input == '\n'):
				line += 1

		elif(state == 'start' and input in addOperator):
			position += 1
			state = 'ok'
			return Token('addOperator',input,line)
		
		elif(state == 'start' and input in mulOperator):
			position += 1
			state = 'ok'
			return Token('mulOperator',input,line)
		
		elif(state == 'start' and input in groupSymbol):
			position = f.tell()
			state = 'ok'
			return Token('groupSymbol',input,line)

		elif(state == 'start' and input in digits):
			state = 'dig'
			tk += input

		elif(state == 'dig' and input in digits):
			state = 'dig'
			tk += input

		elif(state == 'dig' and input not in digits):
			if(int(tk) > -(pow(2,32)-1) and int(tk) < pow(2,32)-1):
				state = 'ok'
				#it is f.tell()-1 because we check a character from the next token
				position = f.tell() - 1
				return Token('number',tk,line)
			else:
				state = 'error'
				print("Number out of range in line " + str(line))

		elif(state == 'start' and input in alphaUpper+alphaLower):
			state = 'idk'
			tk += input

		elif(state == 'idk' and input in alphaUpper+alphaLower+digits):
			state = 'idk'
			tk += input

		elif(state == 'idk' and input not in alphaUpper+alphaLower+digits):
			if(len(tk) > 30):
				state = 'error'
				print('Identifier greater than 30 chars in line ' + str(line))
			else:
				state = 'ok'
				position = f.tell() - 1
				if(tk in keyword):
					return Token('keyword',tk,line)
				else:
					return Token('identifier',tk,line)

		
		elif(state == 'start' and input == comment):
			state = 'rem'

		elif(state == 'rem' and input != comment):
			#check EOF
			if(input != ''):
				state = 'rem'
			if(input == '\n'):
				state = 'rem'
				line += 1
			if(input == ''):
				state = 'error'
				print("Close comment delimiter (#) missing in line " + str(line))

		elif(state == 'rem' and input == comment):
			state = 'start'
			position = f.tell()
		
		elif(state == 'start' and input == '<'):
			state = 'smaller'

		elif(state == 'smaller' and input in ['=','>']):
			state = 'ok'
			position = f.tell()
			if(input == '='):
				return Token('relOperator','<=',line)
			else:
				return Token('relOperator','<>',line)

		elif(state == 'smaller' and input not in ['=','>']):
			state = 'ok'
			position = f.tell()-1
			return Token('relOperator','<',line)

		elif(state == 'start' and input == '>'):
			state = 'larger'

		elif(state == 'larger' and input == '='):
			state = 'ok'
			position = f.tell()
			return Token('relOperator','>=',line)

		elif(state == 'larger' and input != '='):
			state = 'ok'
			position = f.tell()-1
			return Token('relOperator','>',line)

		elif(state == 'start' and input == '='):
			state = 'ok'
			position += 1
			return Token('relOperator','=',line)
				
		elif(state == 'start' and input in delimiter):
			if(input == ':'):
				state = 'asgn'
			else:
				state = 'ok'
				position += 1
				return Token('delimiter',input,line)

		elif(state == 'asgn'):
			if(input == '='):
				state = 'ok'
				position = f.tell()
				return Token('assignment',':=',line)
			else:
				state = 'ok'
				position = f.tell()-1
				return Token('delimiter',':',line)

		elif(state == 'start' and input == '.'):
			state == 'ok'
			break;

		elif(input == '\n'):
			line += 1

#used to check if a function has at least one return statement
hasFunctionReturn = 0
#to check if main subroutine has a return statement
hasMainReturn = 0

#create or not, C code file?
hasFunction = 0

#used to show us the current intermediate code quad
start = 0

#The following global variables used to detect something like this:
# max(in max(in a, in b), in max(in c, in d))

#has a function as argument another function
isFunction = 0

#for example, if we have max(in max(in a)) and we are in second function max
#nest is equal to 2
nest = 0

#if isFunction == 1 then dont genquad just keep variables to this args array
#and print them in the right place
args = []

######################################

#CREATE SYNTAX TREE
token = lex()
def program():
	global token, nesting, programName, hasMainReturn
	if(token.tokenString == 'program'):
		line = token.lineNo
		token = lex()
		name = token.tokenString

		programName = name

		#identifier means that is not a keyword
		if(token.tokenType == 'identifier'):
			token = lex()

			scope = Scope(nesting)
			scopes.append(scope)

			block(name)
			genquad("halt","_","_","_")
			genquad("end_block",name,"_","_")


			if hasMainReturn == 1:
				print("Error! Main function has a return statement!")

			for q in programQuads[start:]:
				generate_mips_code(q)

			is_unique(programName)

			symbolsTable.write('######### ' + str(nesting) + ' ########\n')

			for i in scopes[nesting].entities:
				if i.type == 'function':
					symbolsTable.write('('+i.type+' '+i.name+' '+str(i.framelength)+')\n')
				elif i.type == 'parameter':
					symbolsTable.write('('+i.type+' '+i.name+' '+i.parMode+' '+ str(i.offset)+')\n')
				else:
					symbolsTable.write('('+i.type+' '+i.name+' '+ str(i.offset)+')\n')

			symbolsTable.write('#######################')

			scopes.pop()

		else:
			print("Program name expected in line " + str(line)+'!')
	else:
		print("Program in C-imple must starts with the keyword --program--")

def block(name):
	global programName

	declarations()
	subprograms()
	genquad("begin_block",name,"_","_")

	if name != programName:
		arr = search_entity(name)
		#arr[1] = Entity class item
		entity = arr[1]
		entity.startQuad = nextquad() - 1

	statements()

def declarations():
	global token
	while(token.tokenString == 'declare'):
		#Keep the right line
		line = token.lineNo
		token = lex()
		varlist()
		#varlist returns the next token so we must check if is ';'
		#and then we take the next token
		if(token.tokenString == ';'):
			token = lex()
		else:
			print("Declare statement in line " + str(line)+" must ends with ';'!")

def varlist():
	global token, nesting
	while(token.tokenType == 'identifier'):

		e = Entity('variable', token.tokenString, scopes[nesting].offset)
		scopes[nesting].entities.append(e)
		scopes[nesting].offset += 4

		line = token.lineNo
		token = lex()
		
		if(token.tokenString == ','):
			line2 = token.lineNo
			token = lex()
			#here we check the case many declarations not separated with ','
			if(token.tokenType == 'identifier'):
				continue
			else:
				print("Unexpected ',' at the end of the variable list in line "+str(line2))
		elif(token.tokenType == 'identifier'):
			print("Variables in varlist must separated with ','. Error in line "+str(line))

def subprograms():
	global token, nesting, start
	while(token.tokenString == 'function' or token.tokenString == 'procedure'):
		global hasFunction
		hasFunction = 1
		#we dont have to take the next token here so we 'll 
		#be able to check for 'function' or 'procedure' keyword
		#in subprogram() subroutine
		functionName = subprogram()

		#this is the index of entity table of the previous scope (used for filling framelength of the current function)
		place = len(scopes[nesting-1].entities) - 1

		scopes[nesting-1].entities[place].framelength = scopes[nesting].offset

		for q in programQuads[start:]:
			generate_mips_code(q)

		s = len(programQuads[start:])
		start += s

		is_unique(functionName)

		symbolsTable.write('######### ' + str(nesting) + ' ########\n')

		for i in scopes[nesting].entities:
			if i.type == 'function':
				symbolsTable.write('('+i.type+' '+i.name+' '+str(i.framelength)+')\n')
			elif i.type == 'parameter':
				symbolsTable.write('('+i.type+' '+i.name+' '+i.parMode+' '+ str(i.offset)+')\n')
			else:
				symbolsTable.write('('+i.type+' '+i.name+' '+ str(i.offset)+')\n')

		symbolsTable.write('#######################\n\n')

		scopes.pop(nesting)
		nesting -= 1

def subprogram():
	global token, nesting, hasFunctionReturn

	subprogramType = token.tokenString
	
	line1 = token.lineNo
	token = lex()
	name = token.tokenString

	#append function entity in the previous scope
	#i add one more attribute to function ( or procedure entity type) , nesting level
	#because when call a function we keep the current nestingLevel and not 
	#the actual function nesting level
	e = Entity('function', name, nextquad(), nesting + 1)
	scopes[nesting].entities.append(e)

	nesting += 1
	scope = Scope(nesting)
	scopes.append(scope)

	if(token.tokenType == 'identifier'):
		line2 = token.lineNo
		token = lex()
		
		if(token.tokenString == '('):
			token = lex()
			formalparlist()
			line3 = token.lineNo
			if(token.tokenString == ')'):
				token = lex()
				hasFunctionReturn = 0
				block(name)

				if(subprogramType == 'function' and hasFunctionReturn == 0):
					print("Function ", name, "has not a return statement!")
				if(subprogramType == 'procedure' and hasFunctionReturn == 1):
					print("Error! Procedure", name, "has as a statement 'return'!")

				genquad("end_block",name,"_","_")
			else:
				print("Close of function arguments list expected with ')' in line " + str(line3))
		else:
			print("The relational operator '(' expected after the declaration of function or procedure name in line" + str(line2))
	else:
		print("Function or Procedure name expected in line " + str(line1))
	
	return name

def formalparlist():
	global token
	if(token.tokenString == 'in' or token.tokenString == 'inout'):
		formalparitem()
	
		while(token.tokenString == ','):
			token = lex()
			line = token.lineNo
			if(token.tokenString == 'in' or token.tokenString == 'inout'):
				formalparitem()
			else:
				print("Delimiter ',' don't needed it in line "+str(line)+' or function arguments must be --in-- or --inout-- type!')

def formalparitem():
	global token, nesting
	line = token.lineNo

	#this is the index of entity table of the previous scope (used for filling the argument list)
	place = len(scopes[nesting-1].entities) - 1

	if(token.tokenString == 'in'):
		line1 = token.lineNo
		token = lex()
		if(token.tokenType == 'identifier'):

			e = Entity('parameter', token.tokenString, 'in', scopes[nesting].offset)
			scopes[nesting].entities.append(e)
			scopes[nesting].offset += 4

			arg = Argument('CV')
			scopes[nesting-1].entities[place].argument.append(arg)

			token = lex()
		else:
			print("Argument name must be a alpha string not included in keywords. Error in line " + str(line1))

	elif(token.tokenString == 'inout'):
		line2 = token.lineNo
		token = lex()
		if(token.tokenType == 'identifier'):

			e = Entity('parameter', token.tokenString, 'inout', scopes[nesting].offset)
			scopes[nesting].entities.append(e)
			scopes[nesting].offset += 4

			arg = Argument('REF')
			scopes[nesting-1].entities[place].argument.append(arg)
			
			token = lex()
		else:
			print("Argument name must be a alpha string not included in keywords. Error in line " + str(line2))
	#here , we dont check if arguments is not type in or inout, because this check take place in previous subroutine

def statements():
	global token
	if(token.tokenString == '{'):
		
		token = lex()
		statement()
		line1 = token.lineNo
		
		while(token.tokenString == ';'):
			token = lex()
			statement()
			line1 = token.lineNo
				
		if(token.tokenString == '}'):
			token = lex()
		
		else:
			print("Missing '}' or delimiter ';' missing in line "+str(line1)+" or line "+str(line1-1)+"!")

	else:
		line2 = token.lineNo
		statement()
		line3 = token.lineNo
		if(token.tokenString == ';'):
			token = lex()
			#if(token.tokenType ==  'identifier' or token.tokenType == 'keyword' or token.tokenString == '}'):
			#	print("Error in line "+str(line2)+". '{' missing. If you have many statements must enclosed in '{...}'!!")
		else:
			print("End statement character ';' expected in line "+str(line3)+'!')

def statement():
	global token, hasFunctionReturn, hasMainReturn

	hasMainReturn = 0

	if(token.tokenType == 'identifier'):
		assignStat()
	elif(token.tokenString == 'if'):
		ifStat()
	elif(token.tokenString == 'while'):
		whileStat()
	elif(token.tokenString == 'switchcase'):
		switchcaseStat()
	elif(token.tokenString == 'forcase'):
		forcaseStat()
	elif(token.tokenString == 'incase'):
		incaseStat()
	elif(token.tokenString == 'call'):
		callStat()
	elif(token.tokenString == 'return'):
		hasFunctionReturn = 1
		hasMainReturn = 1
		returnStat()
	elif(token.tokenString == 'input'):
		inputStat()
	elif(token.tokenString == 'print'):
		printStat()

def assignStat():
	global token
	line = token.lineNo
	#the previous token has the variable name
	ID = token.tokenString

	token = lex()
	if(token.tokenString == ':='):
		token = lex()
		Eplace = expression()
	else:
		print("Assign character ':=' missing in line "+str(line)+'!')

	genquad(":=",str(Eplace),"_",ID)

def ifStat():
	global token
	line1 = token.lineNo
	token = lex()
	if(token.tokenString == '('):
		token = lex()

		C = condition()
		Ctrue = C[0]
		Cfalse = C[1]

		line2 = token.lineNo
		if(token.tokenString == ')'):
			token = lex()

			backpatch(Ctrue, nextquad())

			statements()
			
			ifList = makelist(nextquad())
			genquad("jump","_","_","_")
			backpatch(Cfalse, nextquad())

			elsepart()

			backpatch(ifList, nextquad())
		else:
			print("Conditions inside if statement must be enclosed by '(', ')'. Error in line "+str(line2))
	else:
		print("'(' missing after keyword --if-- in line "+str(line1)+"!")

def elsepart():
	global token
	if(token.tokenString == 'else'):
		token = lex()
		statements()

def whileStat():
	global token
	line1 = token.lineNo
	token = lex()
	if(token.tokenString == '('):
		token = lex()

		Cquad = nextquad()
		C = condition()
		Ctrue = C[0]
		Cfalse = C[1]

		line2 = token.lineNo
		if(token.tokenString == ')'):
			token = lex()

			backpatch(Ctrue, nextquad())
			statements()
			genquad("jump","_","_",str(Cquad))
			backpatch(Cfalse, nextquad())
		else:
			print("While conditions must enclosed in '( )'. ') missing in line "+str(line2)+"!")
	else:
		print("While conditions must enclosed in '( )'. '(' missing in line "+str(line1)+"!")

def switchcaseStat():
	global token
	line = token.lineNo
	token = lex()

	exitlist = emptylist()

	if(token.tokenString == 'case'):
		while(token.tokenString == 'case'):
			line1 = token.lineNo
			token = lex()
			if(token.tokenString == '('):
				token = lex()

				C = condition()
				Ctrue = C[0]
				Cfalse = C[1]

				line2 = token.lineNo
				if(token.tokenString == ')'):

					backpatch(Ctrue, nextquad())

					token = lex()
					statements()

					e = makelist(nextquad())
					genquad("jump","_","_","_")
					exitlist = merge(exitlist, e)
					backpatch(Cfalse, nextquad())
					#keep the right line number if the --default-- keyword missing
					#for compile error message
					line = token.lineNo
				else:
					print("')' missing in line "+str(line2))
			else:
				print("'(' missing in line "+str(line1))

	if(token.tokenString == 'default'):
		token = lex()
		statements()

		backpatch(exitlist, nextquad())

	else:
		print("Keyword --default-- missing in line "+str(line)+"!")

def forcaseStat():
	global token
	line = token.lineNo
	token = lex()

	p1Quad = nextquad()

	if(token.tokenString == 'case'):
		while(token.tokenString == 'case'):
			line1 = token.lineNo
			token = lex()
			if(token.tokenString == '('):
				token = lex()

				C = condition()
				Ctrue = C[0]
				Cfalse = C[1]

				line2 = token.lineNo
				if(token.tokenString == ')'):
					token = lex()

					backpatch(Ctrue, nextquad())
					statements()
					genquad("jump","_","_",str(p1Quad))
					backpatch(Cfalse, nextquad())

					line = token.lineNo
				else:
					print("')' missing in line "+str(line2))
			else:
				print("'(' missing in line "+str(line1))

	if(token.tokenString == 'default'):
		token = lex()
		statements()
	else:
		print("Keyword --default-- missing in line "+str(line)+"!")

def incaseStat():
	global token
	token = lex()

	w = newtemp()
	p1Quad = nextquad()
	genquad(":=","1","_",w)

	while(token.tokenString == 'case'):
		line1 = token.lineNo
		token = lex()
		if(token.tokenString == '('):
			token = lex()

			C = condition()
			Ctrue = C[0]
			Cfalse = C[1]

			line2 = token.lineNo
			if(token.tokenString == ')'):
				token = lex()

				backpatch(Ctrue, nextquad())
				genquad(":=","0","_",w)
				statements()
				backpatch(Cfalse, nextquad())

			else:
				print("')' missing in line "+str(line2))
		else:
			print("'(' missing in line "+str(line1))

	genquad("=",w,"0",str(p1Quad))

def returnStat():
	global token
	line1 = token.lineNo
	token = lex()
	if(token.tokenString == '('):
		token = lex()

		Eplace = expression()
		genquad("retv",str(Eplace), "_","_")

		line2 = token.lineNo
		if(token.tokenString == ')'):
			token = lex()
		else:
			print("')' missing in line "+str(line2))
	else:
		print("'(' missing in line "+str(line1))

def callStat():
	global token
	line1 = token.lineNo
	token = lex()

	function_name = token.tokenString

	if(token.tokenType == 'identifier'):
		line2 = token.lineNo
		token = lex()
		if(token.tokenString == '('):
			token = lex()
			actualparlist()

			genquad("call",function_name,"_","_")

			line3 = token.lineNo
			if(token.tokenString == ')'):
				token = lex()
			else:
				print("Call arguments must enclosed in '( )'. ')' missing in line "+str(line3)+'!')
		else:
			print("Call arguments must enclosed in '( )'. '(' missing in line "+str(line2)+'!')
	else:
		print("Callee function name missing in line "+str(line1))

def printStat():
	global token
	line1 = token.lineNo
	token = lex()
	if(token.tokenString == '('):
		token = lex()

		Eplace = expression()

		line2 = token.lineNo
		if(token.tokenString == ')'):
			token = lex()

			genquad("out",str(Eplace),"_","_")

		else:
			print("')' missing in line "+str(line2))
	else:
		print("'(' missing in line "+str(line1))

def inputStat():
	global token
	line1 = token.lineNo
	token = lex()
	if(token.tokenString == '('):
		line2 = token.lineNo
		token = lex()

		idplace = token.tokenString

		if(token.tokenType == 'identifier'):
			line3 = token.lineNo
			token = lex()
			if(token.tokenString == ')'):
				token = lex()

				genquad("inp",idplace,"_","_")

			else:
				print("')' expected at the end of input statement in line "+str(line3)+'!')
		else:
			print("Input missing inside --input-- or the given input is a keyword. Error in line "+str(line2)+'1')
	else:
		print("The given input must enclosed in '( )'. Error in line "+str(line1)+'!')

def actualparlist():
	global token, nest
	nest += 1
	if(token.tokenString == 'in' or token.tokenString == 'inout'):
		actualparitem()
		while(token.tokenString == ','):
			token = lex()
			actualparitem()
			nest -= 1

def actualparitem():
	global token, isFunction
	if(token.tokenString == 'in'):
		token = lex()

		Eplace = expression()

		if isFunction == 1:
			args.append(Eplace)
		else:
			genquad("par",str(Eplace),"CV","_")

	elif(token.tokenString == 'inout'):
		line = token.lineNo
		token = lex() 

		var_name = token.tokenString

		if(token.tokenType == 'identifier'):
			token = lex()

			genquad("par",var_name,"REF","_")

		else:
			print("Variable name missing in line "+str(line))
	else:
		print("Function parameters missing or the parameter list has as last character ',' or ',' missing. Error in line "+str(token.lineNo)+'!')

def condition():
	global token
	#we suppose the first list item is true list and second the false list
	BT1 = boolterm()
	Ctrue = BT1[0]
	Cfalse = BT1[1]

	while(token.tokenString == 'or'):
		backpatch(Cfalse, nextquad())

		token = lex()

		BT2 = boolterm()
		Ctrue = merge(Ctrue, BT2[0])
		Cfalse = BT2[1]

	return [Ctrue, Cfalse]

def boolterm():
	global token
	BF1 = boolfactor()
	BTtrue = BF1[0]
	BTfalse = BF1[1]

	while(token.tokenString == 'and'):
		backpatch(BTtrue, nextquad())

		token = lex()

		BF2 = boolfactor()
		#BF2[0] = true list
		#BF2[1] = false list
		BTfalse = merge(BTfalse, BF2[1])
		BTtrue = BF2[0]

	return [BTtrue, BTfalse]

def boolfactor():
	global token
	if(token.tokenString == 'not'):
		line1 = token.lineNo
		token = lex()
		if(token.tokenString == '['):
			token = lex()

			C = condition()
			#C[0] = true list
			#C[1] = false list
			BFtrue = C[1]
			BFfalse = C[0]

			line2 = token.lineNo
			if(token.tokenString == ']'):
				token = lex()
			else:
				print("--not-- operator conditions must enclosed in '[ ]'. Error in line "+str(line2)+'!')
		else:
			print("--not-- operator conditions must enclosed in '[ ]'. Error in line "+str(line1)+'!')

		return [BFtrue, BFfalse]

	elif(token.tokenString == '['):
		token = lex()

		C = condition()
		BFtrue = C[0]
		BFfalse = C[1]

		line = token.lineNo
		if(token.tokenString == ']'):
			token = lex()
		else:
			print("The character ']' missing in line "+str(line)+'!')

		return [BFtrue, BFfalse]

	else:
		E1place = expression()
		line3 = token.lineNo

		if(token.tokenType == 'relOperator'):
			relop = token.tokenString

			token = lex()

			E2place = expression()
		else:
			print("Relational operator missing in line "+str(line3)+'!')

		BFtrue = makelist(nextquad())
		genquad(relop, str(E1place), str(E2place), "_")

		BFfalse = makelist(nextquad())
		genquad("jump","_","_","_")

		return [BFtrue, BFfalse]

def expression():
	global token
	sign = optionalSign()
	T1place = term()

	if(sign != 'non'):
		w = newtemp()
		genquad(str(sign),str(T1place),"_",w)
		T1place = w

	while(token.tokenType == 'addOperator'):
		operator = token.tokenString

		token = lex()
		T2place = term()

		w = newtemp()
		genquad(operator,str(T1place),str(T2place),w)
		T1place = w

	return T1place

def term():
	global token
	F1place = factor()
	while(token.tokenType == 'mulOperator'):
		operator = token.tokenString
		token = lex()
		F2place = factor()

		w = newtemp()
		genquad(operator,str(F1place),str(F2place),w)
		F1place = w

	return F1place

def factor():
	global token, isFunction, nest
	line = token.lineNo
	if(token.tokenType == 'number'):
		numPlace = token.tokenString
		token = lex()

		return numPlace

	elif(token.tokenString == '('):
		token = lex()

		Eplace = expression()

		line1 = token.lineNo
		if(token.tokenString == ')'):
			token = lex()
		else:
			print("Parenthesis close symbol ')' missing in line "+str(line1)+'!')

		return Eplace

	elif(token.tokenType == 'identifier'):

		name = token.tokenString

		token = lex()

		#if idtail() returns 0 its just a variable, else if returned 1
		#this means we have a function or procedure
		check = idtail()
		isFunction = check
		if(check == 1):
			w = newtemp()
			if nest >= 1:
				genquad("par",w,"RET","_")
				genquad("call",name,"_","_")
			else:
				for i in args:
					genquad("par",i,"CV","_")

				genquad("par",w,"RET","_")
				genquad("call",name,"_","_")

			return w
		else:
			return name
	else:
		print("Variable or constant missing in line "+str(line)+'!')

def idtail():
	global token
	if(token.tokenString == '('):
		token = lex()
		actualparlist()
		line = token.lineNo
		if(token.tokenString == ')'):
			token = lex()
			return 1
		else:
			print("')' missing in line "+str(line)+'!')

	return 0

def optionalSign():
	global token
	if(token.tokenType == 'addOperator'):
		sign = token.tokenString
		token = lex()
		return sign

	else:
		return 'non'


##### GENERATE INTERMEDIATE && MIPS CODE AND C FILE #######
def generate_int_file():

	code = open('code.int', 'w')

	for quad in programQuads:
		code.write(str(quad[0]) + ':\t' + quad[1] + '\t' + quad[2] + '\t' + quad[3] + '\t' + quad[4] + '\n')

	code.close()

def find_variables():
	variables = []
	for i in programQuads:
		if(i[1] not in ['begin_block', 'end_block']):
			if(i[2].isdigit() == False and i[2] != '_'):
				if(i[2] not in variables):
					variables.append(i[2])

			if(i[3].isdigit() == False and i[3] != '_'):
				if(i[3] not in variables):
					variables.append(i[3])

			if(i[4].isdigit() == False and i[4] != '_'):
				if(i[4] not in variables):
					variables.append(i[4])

	return variables

def generate_c_file():
	fp = open('code.c', 'w')
	fp.write('#include <stdio.h> \n\n')
	fp.write('int main()'+'\n')
	fp.write('{' + '\n')

	var = find_variables()
	fp.write('int ')
	for v in range(0, len(var)-1):
		fp.write(var[v]+',')

	fp.write(var[len(var)-1] + ';\n\n')

	for i in programQuads:
		if(i[1] == ':='):
			fp.write('L_'+str(i[0])+': '+i[4]+'='+i[2]+';\n')

		elif(i[1] in relOperator):
			if(i[1] == '<>'):
				fp.write('L_'+str(i[0])+': if ('+i[2]+'!='+i[3]+') goto L_' +i[4]+';\n')
			elif(i[1] == '='):
				fp.write('L_'+str(i[0])+': if ('+i[2]+'=='+i[3]+') goto L_' +i[4]+';\n')
			else:
				fp.write('L_'+str(i[0])+': if ('+i[2]+i[1]+i[3]+') goto L_' +i[4]+';\n')

		elif(i[1] in addOperator+mulOperator):
			fp.write('L_'+str(i[0])+': '+i[4]+'='+i[2]+i[1]+i[3]+';\n')

		elif(i[1] == 'jump'):
			fp.write('L_'+str(i[0])+': goto L_'+i[4]+';\n')

		elif(i[1] == 'inp'):
			fp.write('L_'+str(i[0])+': scanf("%d", &'+i[2]+');\n')

		elif(i[1] == 'out'):
			fp.write('L_'+str(i[0])+': printf("%d", '+i[2]+');\n')

		elif(i[1] == 'halt'):
			fp.write('L_'+str(i[0])+': {}\n')
		elif(i[1] == 'begin_block'):
			fp.write('L_'+str(i[0])+':\n')

	fp.write('}\n')

	fp.close()

def write_asm_to_file():
	code = open('code.asm', 'w')

	for q in mipsQuads:

		if(len(q) == 1 and q[0] != 'syscall'):
			code.write(q[0]+':\n')

		elif(q[0] == 'syscall'):
			code.write('\t'+q[0]+'\n')

		elif(len(q) == 2):
			code.write('\t'+q[0]+' '+q[1]+'\n')

		elif(len(q) == 3):
			code.write('\t'+q[0]+' '+q[1]+','+q[2]+'\n')

		elif(len(q) == 4):
			code.write('\t'+q[0]+' '+q[1]+','+q[2]+','+q[3]+'\n')

	code.close()

#start the lexer and the syntax analysis
program()

#create intermediate code file and fill array programQuads with intermediate code quads
generate_int_file()

#if file only includes a function (main), then create c file
if(hasFunction == 0):
	generate_c_file()

#write to code.asm the final MIPS code
write_asm_to_file()





