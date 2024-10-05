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
                name = os.path.basename(file)
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
            memAddr += 1
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

    return tokens,labelTable

filePath,fileName = getFile()
inputFile = open(filePath).read()
lines = inputFile.splitlines()
tokens,lableTable = tokenize(lines)
print(f'tokens:',tokens)
print(f'LableTable:',lableTable)


