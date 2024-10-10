import glob
import os
import csv 

print('Salutations my fellow humanoids')
print()


_3byteinstructions = ['0x0032', '0x0034', '0x0035', '0x0036', '0x0037', 
                      '0x0038', '0x0045', '0x0048', '0x0049', '0x004A', 
                      '0x004B', '0x004C', '0x004D', '0x004E', '0x004F', 
                      '0x0050', '0x0051', '0x0052', '0x0053', '0x0054', 
                      '0x0055', '0x0056', '0x0057', '0x0058', '0x0059']#machine code of all the instructions that needs a 3 bytes of instruction even if the immediate value is less than a byte because im lazy, also why this line sooo loooongggggggggggggggggggggggggggggggggggggggggggg..................


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
    linNO = 0
    
    for line in lines:
        line = line.strip()

        if not line: #EMPTY LINE HANDLING
            continue 

        token = {'lineNumber':linNO}

        #%#%#%#%#%#%#%# COMMENT HANDLING #%#%#%#%%%#%#%#    

        commentPos = line.find('/')
        if commentPos != -1:
            token['comment'] = line[commentPos +1 :].strip()
            line = line[:commentPos].strip()

        #%#%#%#%#%#%#%# LABEL HANDLING #%#%#%#%%%#%#%#  
        '''
        The label handeling is wrong instead of returning the address in which 
        the instruction is stored this snippet returns the line number of the 
        loop label THIS MUST BE CHANGED. this was my error in understanding this 
        implementation
        '''
        if line.startswith('$') and ':' in line:
            labelPos = line.find(':')
            label = line[1:labelPos].strip()
            token['label'] = label
            line = line[labelPos +1:].strip()

        #%#%#%#%#%#%#%# INSTRUCTION HANDLING #%#%#%#%%%#%#%#  

        if line: token['instruction'] = line
        tokens.append(token)
        linNO += 1

    return tokens

assemblyFile = 'Example_Assembly_code/FACTORIAL.asm' 

def loadCSV(csv_file):#load the csv file to use as a instruction set
    instructionSet = {}
    instructionSize = {}
    with open(csv_file,mode = 'r') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            key = f'{row['OPCODE']} {row['OPERAND']}'.strip()
            instructionSet[key] = row['MACHINE CODE']
            instructionSize[key] = row['BYTES']

    return instructionSet,instructionSize

def setLabel_addr(tokens,instructionSize):
    labelTable = {}
    memAddr = 0

    for token in tokens:
        currentInstr = token['instruction']
        index = currentInstr.find('0x')
        currentInstr = currentInstr[:index - 1].strip()
        
        if token['label']:
            label = token['label']
            labelTable[label] = memAddr
            memAddr += int(instructionSize[currentInstr],16)
    
    return labelTable

def lookUp(instr):#takes the instruction and generates the corresponding mnemonics
    index = instr.find('0x') #checks if an instruction contains an address/immediate values
    
    labelindex = instr.find('$') #checks if an instruction has a label
    instruction,label = instr[:labelindex - 1],instr[labelindex + 1:]

    lowByte = None
    highByte = None
    
    if label in labelTable and labelindex != -1:#if a label is found then replace it with the address where it is defined
        try:
            address = labelTable[label]
            lowByte = hex(address & 0xff)
            highByte = hex((address >> 8) & 0xff)
            machineCode = instructionSet[instruction]
            return [machineCode,lowByte,highByte]
        
        except KeyError:
            print(f'Error: {label} => lable not defined')
            
    else:#if label not found then ignore
        pass

    if index != -1:#if an instruction containg a address/immediate value then split it into high and low byte
        instruction,data = instr[:index - 1].strip(),instr[index:].strip()
        machineCode = instructionSet[instruction]
        data = int(data,16)

        if data > 0xff or machineCode in _3byteinstructions:#if the current instruction in the list of 3 byte instructions then return high byte even if its 0
            highByte = hex(data >> 8 & 0xff)
            lowByte = hex(data & 0xff)

        elif data <= 0xff and data >= 0x00:#if not then just return the low byte
            lowByte = hex(data & 0xff)
            
        if highByte is not None:#if the highByte is not empty then return it in the list
            return [machineCode,lowByte,highByte]
        else:#if not not empty then ignore it in the list
            return [machineCode,lowByte]

    else:#if no address/immediate values are found in an instruction the just return its machine code
        machineCode = instructionSet[instr]
        machineCode = hex(int(machineCode,16))
        return [machineCode]
    
    #%#%#%#%#%#%#%#%#% THE ACTUAL ASSEMBLER #%#%#%#%#%#%#%#%#%#

filePath,fileName = getFile()
inputFile = open(filePath).read()
lines = inputFile.splitlines()
tokens = tokenize(lines)
for token in tokens:
    print(token)
instructionSet,instructionSize= loadCSV('files/Instructions.csv')
print(instructionSet,instructionSize)
labelTable = setLabel_addr(tokens,instructionSize)

#%#%#%#%#% CODE GENERATION #%#%#%#%#%#%#%

def main():
    for token in tokens:
        inst = token['instruction']
        MC = lookUp(inst)
        if MC:
            for i in MC:
                print(i)
        else:
            print('Error instruction not found')

if __name__ == '__main__':
    main() 
    

