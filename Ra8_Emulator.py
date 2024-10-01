class Ra8_MPU:
    def __init__(self) -> None:
        #Setting up the device memory 64kb each(16 bit address lines)
        self.dataMemory = [0] * 0xffff
        self.instructionMemory = [0] * 0xffff

        #Special 16-bit registers that holds the address of data and instruction memory
        self.stackPointer = 0xffff
        self.programCounter = 0x0000

        #Accumulator and other genreal pupose registers (8-bit)
        self.A = 0
        self.B = 0
        self.C = 0
        self.D = 0
        self.H = 0
        self.L = 0
        self.M = 0
        self.instructionRegister = 0

        #Setting up  flags register
        self.flags = {
            'S':False,
            'C':False,
            'P':False,
            'Z':False    
        }

        #Dictionary used to map a register to a value
        self.registerMap = {
            0:'A',
            1:'B',
            2:'C',
            3:'D',
            4:'H',
            5:'L',
            6:'M'

        }

        #Class objects
        self.bitwise = bitwise()
        self.stack = Stack(self.dataMemory,self.stackPointer)

        self._halted = False
    
    def setFlag(self,flag,val:bool): #sets the flag to the given value
        if flag in self.flags:
            self.flags[flag] = val

    def resetFlags(self): #reset flags to initial values
        self.flags = {
            'S':False,
            'C':False,
            'P':False,
            'Z':False    
        }
    
    def handleFlags(self,target):
        self.resetFlags()
        if target >= 256:
            self.setFlag('C',True)
            target = target & 0xff
        else:
            self.setFlag('C',False)
        if target == 0:
            self.setFlag('Z',True)
        else:
            self.setFlag('Z',False)
        if target < 0:
            self.setFlag('S',True)
        else:
            self.setFlag('S',False)
        if target % 2:
            self.setFlag('P',False)
        else:
            self.setFlag('P',True)
    
    def run(self,debug:bool):
        cycle = 0
        while 1:
            if self._halted:
                break
            else:
                if debug:
                    print(f'programCounter: {hex(self.programCounter)}')

                self.Fetch()
                self.decodeANDexecute()

                if debug:
                    cycle += 1
                    print(f'currentCycle: {cycle}')
                    print(f'current Instruction: {hex(self.instructionRegister)}')
                    print('----------------------------------------------------------')
                    print(f'Flags:| {self.flags}')
                    print(f'Register A: {self.A}')
                    print(f'Register B: {self.B}')
                    print(f'Register C: {self.C}')
                    print(f'Register D: {self.D}')
                    print(f'Register E: {self.E}')
                    print(f'Register H: {self.H}')
                    print(f'Register L: {self.L}')
                    print(f'Register M: {self.M}')
                    print(f'Halted?: {self._halted}')
                    print(f'programCounter after execution: {hex(self.programCounter)}')
                    print(f'stackPointer: {hex(self.stackPointer)}')
                    print(f'stackTop: {hex(self.stack.topElement(),)}') 
                    print(f'stackPreviousElement: {hex(self.stack.previousElement())}')           
                    print('___________________________________________________________')
    
    ################# FETCH, DECODE AND EXECUTE CYCLE ##################

    def Fetch(self):
        self.instructionRegister = self.instructionMemory[self.programCounter]
        self.programCounter += 1

    def decodeANDexecute(self):
        currentInstruction = self.instructionRegister
        
        if currentInstruction == 0x00:
            pass

        elif currentInstruction == 0x02:
            self._halted = False

        elif currentInstruction in range(0X02,0X2C):
            hex1 = currentInstruction
            hex1 = hex1 - 0x02    #expression to decode the registers from the hex instruction
            Xreg = hex1 // 6
            Yreg = hex1 % 6
            if Yreg >= Xreg:
                Yreg += 1
            Value_to_be_moved = getattr(self,(self.registerMap[Yreg]))#gets the value from the source register 
            setattr(self,(self.registerMap[Xreg]),Value_to_be_moved)#load the value to the destination register
            #print(f'The value moved from {self.registerMap[Yreg]} to {self.registerMap[Xreg]} is {getattr(self,(self.registerMap[Xreg]))}')

        elif currentInstruction in range(0x2c,0x32): #MVI instructions
            hex = currentInstruction - 0x2b
            register = self.registerMap[hex] 
            immediate_value = self.instructionMemory[self.programCounter]
            setattr(self,register,immediate_value)
            self.programCounter += 1
            #print(f'The immediate value {immediate_value} has been moved to {self.registerMap[hex]}')
        
        elif currentInstruction == 0x32: #LDA instruction (load accumulator from memory)
            high_byte = self.instructionMemory[self.programCounter + 1]
            low_byte = self.instructionMemory[self.programCounter]
            address = (high_byte << 8) | low_byte
            self.A = self.dataMemory[address]
            self.programCounter += 2

        elif currentInstruction == 0x33: #LDI instruction
            immediate_value = self.instructionMemory[self.programCounter]
            self.A = immediate_value
            self.programCounter += 1
        
        elif currentInstruction in range(0x34,0x37): #STR instructions (store B,C,D register values to memory)
            regindex = currentInstruction - 0x0033
            high_byte = self.instructionMemory[self.programCounter + 1]
            low_byte = self.instructionMemory[self.programCounter]
            address = (high_byte << 8) | low_byte      
            self.dataMemory[address] = getattr(self,(self.registerMap[regindex]))
            self.programCounter +=2
        elif currentInstruction == 0x37: #STR instructions (store M register values to memory)
            high_byte = self.instructionMemory[self.programCounter + 1]
            low_byte = self.instructionMemory[self.programCounter]
            address = (high_byte << 8) | low_byte      
            self.dataMemory[address] = getattr(self,(self.registerMap['M']))
            self.programCounter +=2

        elif currentInstruction == 0x38:#STA instruction
            high_byte = self.instructionMemory[self.programCounter + 1]
            low_byte = self.instructionMemory[self.programCounter]
            address = (high_byte << 8) | low_byte      
            self.dataMemory[address] = getattr(self,(self.registerMap['A']))
            self.programCounter +=2

        elif currentInstruction in range(0x39,0x3e): #PUSH instructions
            regindex = currentInstruction - 0x38
            regindex = 6 if currentInstruction == 0x3d else regindex
            regValue = getattr(self,(self.registerMap[regindex]))
            self.stack.Push(regValue)
            self.programCounter += 1

        elif currentInstruction in range(0x3e,0x43): #POP instructions
            regindex = currentInstruction - 0x003d
            regindex = 6 if currentInstruction == 0x42 else regindex
            register = self.registerMap[regindex]
            data = self.stack.Pop()
            setattr(self,register,data)
            self.programCounter += 1
        
        elif currentInstruction == 0x43:#LDX instruction
            high_byte = self.H
            low_byte = self.L
            address = (high_byte << 8) | low_byte      
            self.A = self.dataMemory[address] 

        elif currentInstruction == 0x44:#STX instruction
            high_byte = self.H
            low_byte = self.L
            address = (high_byte << 8) | low_byte      
            self.dataMemory[address] = getattr(self,(self.registerMap['A']))

        elif currentInstruction == 0x45: #LDHL instruction
            self.H = self.dataMemory[self.programCounter + 1]
            self.L = self.dataMemory[self.programCounter]
            self.programCounter += 2
        
        elif currentInstruction == 0x46: #PCHL instruction
            high_byte = self.H
            low_byte = self.L
            address = (high_byte << 8) | low_byte      
            self.programCounter = self.dataMemory[address]
        
        elif currentInstruction == 0x47: #SPHL instruction
            high_byte = self.H
            low_byte = self.L
            address = (high_byte << 8) | low_byte      
            self.stackPointer = self.dataMemory[address]
        
        elif currentInstruction in range(0x48,0x51): #Unconditional and Conditional jump instructions
            Type = currentInstruction - 0x47
            match (Type):
                case 1: #JMP instruction (Unconditional jump to the specified instruction memory address)
                    high_byte = self.instructionMemory[self.programCounter + 1]
                    low_byte = self.instructionMemory[self.programCounter]
                    address = (high_byte << 8) | low_byte
                    self.programCounter = address
                case 2: 
                    if self.flags['C'] == True: #JC instruction (jump if carry)
                        high_byte = self.instructionMemory[self.programCounter + 1]
                        low_byte = self.instructionMemory[self.programCounter]
                        address = (high_byte << 8) | low_byte
                        self.programCounter = address
                case 3:
                    if self.flags['C'] == False: #JNC instruction (jump if carry)
                        high_byte = self.instructionMemory[self.programCounter + 1]
                        low_byte = self.instructionMemory[self.programCounter]
                        address = (high_byte << 8) | low_byte
                        self.programCounter = address
                case 4:
                    if self.flags['Z'] == True: #JZ instruction
                        high_byte = self.instructionMemory[self.programCounter + 1]
                        low_byte = self.instructionMemory[self.programCounter]
                        address = (high_byte << 8) | low_byte
                        self.programCounter = address
                case 5:
                    if self.flags['Z'] == False: #JNZ instruction
                        high_byte = self.instructionMemory[self.programCounter + 1]
                        low_byte = self.instructionMemory[self.programCounter]
                        address = (high_byte << 8) | low_byte
                        self.programCounter = address
                case 6:
                    if self.flags['S'] == False: #JP instruction
                        high_byte = self.instructionMemory[self.programCounter + 1]
                        low_byte = self.instructionMemory[self.programCounter]
                        address = (high_byte << 8) | low_byte
                        self.programCounter = address
                case 7:
                    if self.flags['S'] == True: #JM instruction 
                        high_byte = self.instructionMemory[self.programCounter + 1]
                        low_byte = self.instructionMemory[self.programCounter]
                        address = (high_byte << 8) | low_byte
                        self.programCounter = address
                case 8:
                    if self.flags['P'] == True: #JE instructipm (jump if even)
                        high_byte = self.instructionMemory[self.programCounter + 1]
                        low_byte = self.instructionMemory[self.programCounter]
                        address = (high_byte << 8) | low_byte
                        self.programCounter = address
                case 9:
                    if self.flags['P'] == False: #JO instructipm (jump if odd)
                        high_byte = self.instructionMemory[self.programCounter + 1]
                        low_byte = self.instructionMemory[self.programCounter]
                        address = (high_byte << 8) | low_byte
                        self.programCounter = address

        elif currentInstruction in range(0x51,0x5a): #Conditional and Unconditional call subroutine instructions
            Type = currentInstruction - 0x50
            inst_highBYTE = (currentInstruction >> 8) & 0x00ff
            inst_lowBYTE = (currentInstruction & 0xff)
            self.stack.Push(inst_highBYTE)
            self.stack.Push(inst_lowBYTE)
            match (Type):
                case 1:
                    high_byte = self.instructionMemory[self.programCounter + 1]
                    low_byte = self.instructionMemory[self.programCounter]
                    address = (high_byte << 8) | low_byte
                    self.programCounter = address
                case 2: 
                    if self.flags['C'] == True: #CC instruction 
                        high_byte = self.instructionMemory[self.programCounter + 1]
                        low_byte = self.instructionMemory[self.programCounter]
                        address = (high_byte << 8) | low_byte
                        self.programCounter = address
                case 3:
                    if self.flags['C'] == False: #CNC instruction 
                        high_byte = self.instructionMemory[self.programCounter + 1]
                        low_byte = self.instructionMemory[self.programCounter]
                        address = (high_byte << 8) | low_byte
                        self.programCounter = address
                case 4:
                    if self.flags['Z'] == True: #CZ instruction
                        high_byte = self.instructionMemory[self.programCounter + 1]
                        low_byte = self.instructionMemory[self.programCounter]
                        address = (high_byte << 8) | low_byte
                        self.programCounter = address
                case 5:
                    if self.flags['Z'] == False: #CNZ instruction
                        high_byte = self.instructionMemory[self.programCounter + 1]
                        low_byte = self.instructionMemory[self.programCounter]
                        address = (high_byte << 8) | low_byte
                        self.programCounter = address
                case 6:
                    if self.flags['P'] == True:#CE instruction
                        high_byte = self.instructionMemory[self.programCounter + 1]
                        low_byte = self.instructionMemory[self.programCounter]
                        address = (high_byte << 8) | low_byte
                        self.programCounter = address
                
                case 7:
                    if self.flags['P'] == False:#CO instruction
                        high_byte = self.instructionMemory[self.programCounter + 1]
                        low_byte = self.instructionMemory[self.programCounter]
                        address = (high_byte << 8) | low_byte
                        self.programCounter = address
                
                case 8:
                    if self.flags['S'] == False:#CP instruction
                        high_byte = self.instructionMemory[self.programCounter + 1]
                        low_byte = self.instructionMemory[self.programCounter]
                        address = (high_byte << 8) | low_byte
                        self.programCounter = address
                
                case 9:
                    if self.flags['S'] == True:#CM instruction
                        high_byte = self.instructionMemory[self.programCounter + 1]
                        low_byte = self.instructionMemory[self.programCounter]
                        address = (high_byte << 8) | low_byte
                        self.programCounter = address


        elif currentInstruction in range(0x5a,0x63): #Conditional and Unconditional return from subroutine instructions
            low_byte = self.stack.Pop()
            high_byte = self.stack.Pop()
            returnAddress = (high_byte << 8) | low_byte
            Type = currentInstruction - 0x59
            match (Type):
                case 1: #Unconditional RET instructions
                    self.programcounter = returnAddress
                case 2: 
                    if self.flags['C'] == True: #RC instruction 
                        self.programcounter = returnAddress
                case 3:
                    if self.flags['C'] == False: #RNC instruction 
                        self.programcounter = returnAddress
                case 4:
                    if self.flags['Z'] == True: #RZ instruction
                        self.programcounter = returnAddress
                case 5:
                    if self.flags['Z'] == False: #RNZ instructioN
                        self.programcounter = returnAddress
                case 6:
                    if self.flags['S'] == False: #RP instructioN
                        self.programcounter = returnAddress
                case 7:
                    if self.flags['S'] == True: #RM instructioN
                        self.programcounter = returnAddress
                case 8:
                    if self.flags['P'] == True: #RE instructioN
                        self.programcounter = returnAddress
                case 9:
                    if self.flags['P'] == False: #RO instructioN
                        self.programcounter = returnAddress

        elif 1:
            pass

class bitwise: #To perform bitwise operations
    def Logic_rightShift(self,value:int):
        val = (value >> 1) & 0xff
        return val
    
    def Logic_leftShift(self,value:int):
        val = (value << 1) & 0xff
        return val 
    
    def Logic_rightRotate(self,value:int):
        val = ((value >> 1)|(value << 7)) & 0xff
        return  val
    
    def Logic_leftRotate(self,value:int):
        val = ((value << 1)|(value >>7)) & 0xff
        return val

    def Arithmetic_rightShift(self,value:int):
        msb = value & 0x80
        lower7bits = value & 0x7f
        val = (lower7bits >> 1) & 0x7f
        result = msb | val
        return result

    def Arithmetic_leftShift(self,value:int):
        msb = value & 0x80
        lower7bits = value & 0x7f
        val = (lower7bits << 1) & 0x7f
        result = msb | val
        return result
    
    def Arithmetic_rightRotate(self,value:int):
        msb = value & 0x80
        lower7bits = value & 0x7f
        val = ((lower7bits >> 1)|(lower7bits << 6)) & 0x7f
        result = msb | val
        return result
    
    def Arithmetic_leftRotate(self,value:int):
        msb = value & 0x80
        lower7bits = value & 0x7f
        val = ((lower7bits << 1)|(lower7bits >> 6)) & 0x7f
        result = msb | val
        return result

class Stack: #To perform stack operations
    def __init__(self,dta,sp) -> None:

        self.dataMemory = dta
        self.stackPointer = sp
        
    def Push(self,data):
        self.dataMemory[self.stackPointer] = data
        self.stackPointer -= 1

    def Pop(self):
        self.stackPointer += 1
        data = self.dataMemory[self.stackPointer]
        self.dataMemory[self.stackPointer] = 0x0000
        #print(data) #comment this line when not needed
        return data

    def topElement(self):
        if self.stackPointer < 0xffff:
            data = self.dataMemory[self.stackPointer + 1]
            #print(data) #comment this line when not needed
            return data
        else:
            data = 0x0000
            #print(data) #comment this line when not needed
            return data 
    
    def previousElement(self):
        if self.stackPointer < 0xffff:
            data = self.dataMemory[self.stackPointer + 2]
            #print(data) #comment this line when not needed
            return data
        else:
            data = 0x0000
            #print(data) #comment this line when not needed
            return data