import glob
import os
import csv 

print('Salutations my fellow humanoids')
print()

def getFile(directory = 'Example_Assembly_code'):
    asm_files = glob.glob(directory + '/*.asm')

    if not asm_files:
        print(f'No .asm files found in {directory}.')
        return None
    
    print('-----------------------------------------------------------------------------')    
    print('Choose a program to assemble:')
    print('-----------------------------------------------------------------------------')    
    
    for i,file in enumerate(asm_files):
        print(f'{i} => {os.path.basename(file)}')
    print('-----------------------------------------------------------------------------')    
    
    while True:
        try:
            choice = int(input('Enter the index of your choice:'))
            if 0 <= choice < len(asm_files):
                path = asm_files[choice]
                name = os.path.basename(path)
                print(f'{name} will be assembled into Machine_code directory.')
                return path,name 
            else:
                print('Invalid choice enter a valid index!')
        except:
            print('Invalid choice enter a number!')

def tokenize(lines):
    tokens = []
    labelTable = {}
    memAddr = 0
    
    for line in lines:
        line = line.strip()

        if not line: #EMPTY LINE HANDLING
            continue 

        token = {'lineNumber':memAddr}

        #%#%#%#%#%#%#%# COMMENT HANDLING #%#%#%#%%%#%#%#    

        commentPos = line.find('/')
        if commentPos != -1:
            token['comment'] = line[commentPos +1 :].strip()
            line = line[:commentPos].strip()

        #%#%#%#%#%#%#%# LABEL HANDLING #%#%#%#%%%#%#%#  

        if line.startswith('$') and ':' in line:
            labelPos = line.find(':')
            label = line[1:labelPos].strip()
            labelTable[label] = memAddr
            token['label'] = label
            line = line[labelPos +1:].strip()

        #%#%#%#%#%#%#%# COMMENT HANDLING #%#%#%#%%%#%#%#  

        if line: token['instruction'] = line
        tokens.append(token)
        memAddr += 1

    return tokens,labelTable

assemblyFile = 'Example_Assembly_code/FACTORIAL.asm' 
def loadCSV(csv_file):
    instruction_set = {}
    with open(csv_file,mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            key = f'{row['OPCODE']} {row['OPERAND']}'.strip()
            instruction_set[key] = row['MACHINE CODE']
    return instruction_set

def lookUp(instr):
    index = instr.find('0x')
    if index != -1:
        instruction,data = instr[:index - 1].strip(),instr[index:].strip()
        machineCode = instructionSet[instruction]
        data = int(data,16)
        if data > 0xff:
            highByte = hex(data >> 8 & 0xff)
            lowByte = hex(data & 0xff)

        elif data <= 0xff and data >= 0x00:
            lowByte = hex(data & 0xff)
            highByte = hex(0)
        return [machineCode,lowByte,highByte]
    else:
        machineCode = instructionSet[instr]
        machineCode = hex(int(machineCode,16))
        return [machineCode]
    
filePath,fileName = getFile()
inputFile = open(filePath).read()
lines = inputFile.splitlines()
tokens,lableTable = tokenize(lines)
#for i in tokens:
#    print(f'"{i['instruction']}"')

instructionSet = loadCSV('files/Instructions.csv')

for token in tokens:
    inst = token['instruction']
    MC = lookUp(inst)
    if MC:
        for i in MC:
            print(i)
    else:
        print('Error instruction not found')
    

