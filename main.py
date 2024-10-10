from Ra8_Emulator import *

emulator = Ra8_MPU()

dataMemory = emulator.dataMemory
instructionMemory = emulator.instructionMemory

programCounter = emulator.programCounter
stackPointer = emulator.stackPointer

machineCode = 'Machine_code/test is it working?.txt'

lines = open(machineCode).read().splitlines()

for index,value in enumerate(lines):
    instructionMemory[index] = int(value,16)

#%#%#%#%#% INPUT DATA #%#%#%#%#%
emulator.dataMemory[0x6] = 0x4
#%#%#%#%#% EXECUTE #%#%#%#%#%

emulator.run(debug=False)

#%#%#%#%#% OUTPUT #%#%#%#%#%

print("OUTPUT:")
print(dataMemory[0x0000])
print(dataMemory[0x0001])
print('___________________________________________________________________')



