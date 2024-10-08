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

        #Boolean variable that keeps track of the MPU's current state
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
        self.flags['C'] = (target >= 255)
        self.flags['S'] = ((target & 0x80) != 0x00)
        self.flags['Z'] = (target == 0)
        self.flags['P'] = (bin(target).count('1') % 2 == 0)
    
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
        
        if currentInstruction == 0x00: #NOPE instructions (No Operation)
            pass

        elif currentInstruction == 0x01: #HLT instruction (halt executions)
            self._halted = True

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
            self.dataMemory[address] = self.M
            self.programCounter +=2

        elif currentInstruction == 0x38:#STA instruction
            high_byte = self.instructionMemory[self.programCounter + 1]
            low_byte = self.instructionMemory[self.programCounter]
            address = (high_byte << 8) | low_byte      
            self.dataMemory[address] = self.A
            self.programCounter +=2

        elif currentInstruction in range(0x39,0x3e): #PUSH instructions
            regindex = currentInstruction - 0x38
            regindex = 6 if currentInstruction == 0x3d else regindex
            regValue = getattr(self,(self.registerMap[regindex]))
            self.stack.Push(regValue)

        elif currentInstruction in range(0x3e,0x43): #POP instructions
            regindex = currentInstruction - 0x003d
            regindex = 6 if currentInstruction == 0x42 else regindex
            register = self.registerMap[regindex]
            data = self.stack.Pop()
            setattr(self,register,data)
        
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
            self.H = self.instructionMemory[self.programCounter + 1]
            self.L = self.instructionMemory[self.programCounter]
            self.programCounter += 2
        
        elif currentInstruction == 0x46: #PCHL instruction
            high_byte = self.H
            low_byte = self.L
            address = (high_byte << 8) | low_byte      
            self.programCounter = address
        
        elif currentInstruction == 0x47: #SPHL instruction
            high_byte = self.H
            low_byte = self.L
            address = (high_byte << 8) | low_byte      
            self.stackPointer = address
        
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
                    self.programCounter = returnAddress
                case 2: 
                    if self.flags['C'] == True: #RC instruction 
                        self.programCounter = returnAddress
                case 3:
                    if self.flags['C'] == False: #RNC instruction 
                        self.programCounter = returnAddress
                case 4:
                    if self.flags['Z'] == True: #RZ instruction
                        self.programCounter = returnAddress
                case 5:
                    if self.flags['Z'] == False: #RNZ instructioN
                        self.programCounter = returnAddress
                case 6:
                    if self.flags['S'] == False: #RP instructioN
                        self.programCounter = returnAddress
                case 7:
                    if self.flags['S'] == True: #RM instructioN
                        self.programCounter = returnAddress
                case 8:
                    if self.flags['P'] == True: #RE instructioN
                        self.programCounter = returnAddress
                case 9:
                    if self.flags['P'] == False: #RO instructioN
                        self.programCounter = returnAddress

        elif currentInstruction in range(0x63,0x67):#ADD instruction
            regindex = currentInstruction - 0x0062
            regindex = 6 if currentInstruction == 0x66 else regindex
            register = getattr(self,self.registerMap[regindex])
            self.A = self.A + register 
            self.handleFlags(self.A)
            if self.A >= 256:
                self.A = self.A & 0xff

        elif currentInstruction in range(0x67,0x6b): #ADC instruction
            regindex = currentInstruction - 0x0066
            regindex = 6 if currentInstruction == 0x6a else regindex
            register = getattr(self,self.registerMap[regindex])
            self.A = self.A + register + self.flags['C']
            self.handleFlags(self.A)
            if self.A >= 256:
                self.A = self.A & 0xff
        
        elif currentInstruction == 0x6b: #ADI instruction
            data = self.instructionMemory[self.programCounter]
            self.A = data
            self.programCounter += 1
            self.handleFlags(self.A)
            if self.A >= 256:
                self.A = self.A & 0xff
        
        elif currentInstruction in range(0x6c,0x70): #SUB instruction
            regindex = currentInstruction - 0x006b
            regindex = 6 if currentInstruction == 0x6f else regindex
            register = getattr(self,self.registerMap[regindex])
            self.A = self.A - register 
            self.handleFlags(self.A)
            if self.A  < 0:
                self.A = (self.A + 256) & 0xff
                self.flags['C'] = True
            else:
                self.A = self.A & 0xff
                self.flags['C'] = False

        elif currentInstruction in range(0x70,0x74): #SUC instruction
            regindex = currentInstruction - 0x6f
            regindex = 6 if currentInstruction == 0x73 else regindex
            register = getattr(self,self.registerMap[regindex])
            self.A = self.A - (register + (1 - self.flags['C']))
            self.handleFlags(self.A)
            if self.A  < 0:
                self.A = (self.A + 256) & 0xff
                self.flags['C'] = True
            else:
                self.A = self.A & 0xff
                self.flags['C'] = False
        
        elif currentInstruction == 0x74: #SUI instruction
            data = self.instructionMemory[self.programCounter]
            self.A = self.A = data
            self.programCounter += 1
            self.handleFlags(self.A)
            if self.A  < 0:
                self.A = (self.A + 256) & 0xff
                self.flags['C'] = True
            else:
                self.A = self.A & 0xff
                self.flags['C'] = False

        elif currentInstruction in range(0x75,0x79): #INC instruction
            regindex = currentInstruction - 0x0074
            regindex = 6 if currentInstruction == 0x6f else regindex
            register = getattr(self,self.registerMap[regindex])
            setattr(self,self.registerMap[regindex],register + 1)
            self.handleFlags(self.A)
        
        elif currentInstruction in range(0x79,0x7d): #DCR instruction
            regindex = currentInstruction - 0x0078
            regindex = 6 if currentInstruction == 0x6f else regindex
            register = getattr(self,self.registerMap[regindex])
            setattr(self,self.registerMap[regindex],register - 1)
            self.handleFlags(self.A)
        
        elif currentInstruction == 0x7d: #INX  instruction
            high_byte = self.H
            low_byte = self.L
            data = (high_byte << 8) | low_byte
            data = data + 1 
            self.H = (data >> 8) & 0xff  
            self.L = data & 0xff

        elif currentInstruction == 0x7e: #DCX instruction
            high_byte = self.H
            low_byte = self.L
            data = (high_byte << 8) | low_byte
            data = data - 1 
            self.H = (data >> 8) & 0xff          
            self.L = data & 0xff

        elif currentInstruction in range(0x007f,0x0087): #Bitwise Rotate and Shift instructions          
            Type = currentInstruction - 0x7e
            match (Type):
                case 1:#RS instructions
                    self.bitwise.Logic_rightShift(self.A) 
                case 2:#ARS instructions
                    self.bitwise.Arithmetic_rightShift(self.A) 
                case 3:#LS instructions
                    self.bitwise.Logic_leftShift(self.A) 
                case 4:#ALS instructions
                    self.bitwise.Arithmetic_leftShift(self.A) 
                case 5:#LR instructions
                    self.bitwise.Logic_leftRotate(self.A) 
                case 6:#ALR instructions
                    self.bitwise.Arithmetic_leftRotate(self.A)  
                case 7:#RR instructions
                    self.bitwise.Logic_rightRotate(self.A)  
                case 8:#ARR instructions
                    self.bitwise.Arithmetic_rightRotate(self.A)
            self.handleFlags(self.A)
            self.programCounter +=1 

        elif currentInstruction in range(0x87,0x8b): #AND instruction
            regindex = currentInstruction - 0x0086
            regindex = 6 if currentInstruction == 0x8a else regindex
            register = self.registerMap[regindex]
            register = self.A & register
        
        elif currentInstruction == 0x8b: #ANI instruction
            data = self.instructionMemory[self.programCounter]
            self.A = self.A & data
            self.programCounter += 1

        elif currentInstruction in range(0x8f,0x93): #OR instruction
            regindex = currentInstruction - 0x008e
            regindex = 6 if currentInstruction == 0x92 else regindex
            register = self.registerMap[regindex]
            register = self.A | register
        
        elif currentInstruction == 0x93: #ORI instruction
            data = self.instructionMemory[self.programCounter]
            self.A = self.A | data
            self.programCounter += 1

        elif currentInstruction in range(0x97,0x9b): #XOR instruction
            regindex = currentInstruction - 0x0096
            regindex = 6 if currentInstruction == 0x9a else regindex
            register = getattr(self,self.registerMap[regindex])
            register = self.A ^ register
        
        elif currentInstruction == 0x9b: #XRI instruction
            data = self.instructionMemory[self.programCounter]
            self.A = self.A ^ data  
            self.programCounter += 1

        elif currentInstruction in range(0x9f,0xa3): #CMP instruction
            regindex = currentInstruction - 0x0086
            regindex = 6 if currentInstruction == 0xa2 else regindex
            register = self.registerMap[regindex]
            temp = self.A - register
            self.handleFlags(temp)

        elif currentInstruction == 0xa3: #CMI instruction
            data = self.instructionMemory[self.programCounter]
            temp = self.A - data
            self.handleFlags(temp)

        elif currentInstruction == 0xa7: #CMC instruction
            self.flags['C'] = not self.flags['C']
        
        elif currentInstruction == 0xa8: #STC instruction
            self.setFlag('C',True)

        elif currentInstruction == 0xa9: #STC instruction
            self.setFlag('C',False)

        elif currentInstruction == 0xaa: #CMA instruction
            self.A = not self.A
                                                                                                                                                        
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