from Ra8_Emulator import *

emulator = Ra8_MPU()

dataMemory = emulator.dataMemory
instructionMemory = emulator.instructionMemory

programCounter = emulator.programCounter
stackPointer = emulator.stackPointer

machineCode = 'Machine_code/factorial.txt'

lines = open(machineCode).read().splitlines()

for index,value in enumerate(lines):
    instructionMemory[index] = int(value,16)

#%#%#%#%#% INPUT DATA #%#%#%#%#%



#%#%#%#%#% EXECUTE #%#%#%#%#%

emulator.run(debug=True)

#%#%#%#%#% OUTPUT #%#%#%#%#%

print("OUTPUT:")
print(dataMemory[0x0000])
print(bin(dataMemory[0x0000]))
print('___________________________________________________________________')



