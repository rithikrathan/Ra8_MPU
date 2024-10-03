MACHINE DESCRIPTION:

    Features:
        >Turing complete
        >8-bit data width
        >16-bit address width
        >9-registers (5- general puropse registers, 2-indirect addressing registers, 1-flags register, 1-instruction register)       
        >16-bit programCounter
        >16-bit stackPointer
        >Memory_mapped I/O
        >Harvard Architecture

    Registers:
        >General purpose (8-bit):
             Register : Value stored
             --------------------------   
                    A : argument 0 (accumulator)
                    B : argument 1
                    C : argument 2
                    D : argument 3
                    M : return value
                    H : index_highByte
                    L : index_lowByte

        >Flags:
             Flags in flags register (8-bit):       [S|-|Z|-|P|-|C|-]
                                               MSB >[8|7|6|5|4|3|2|1]< LSB

             Flag : Condition   
             ----------------------------------      
                S : negative = 1     | positive = 0
                Z : isZero = 1       | isnotZero = 0
                P : even = 1         | odd = 0
                C : carry/borrow = 1 | else 0 

        >Instruction register: Stores the current instruction (8-bit)

        >Stack pointer: Stores address that points the top of the stack (16-bit)

        >Program counter: Stores the current address of the instructions memory (16-bit)

    Instruction Set:
        MACHINE CONTROL:

                    OPCODE: DESCRIPTION
                    ---------------------
                    >NOPE : No operation
                    >HLT  : halt
         
        DATA TRANSFER:

                   OPCODE :           OPERAND
                   ------------------------------------------------------
                    >MOV  : reg/reg
                    >MVI  : reg/8-bit immediate value
                    >LDA  : accumulator/mem (direct addressing)
                    >LDI  : accumulator/8-bit immediate value
                    >STR  : mem/register(A,B,C,D,M)
                    >PUSH : mem[--sp]/register(A,B,C,D,M)/HL pair
                    >POP  : register(A,B,C,D,M)/HL pair
                    >LDX  : accumulator/mem(HL pair indirect addressing) 
                    >STX  : mem(HL pair)/accumulator
                    >LDHL : HL pair/16-bit address
                    >PCHL : programCounter/HL pair
                    >SPHL : stackPointer/HL pair
                
        BRANCHING:

         OPCODE | OPERAND : DESCRIPTION
         -------------------------------------------------------
               >JMP  addr : programCounter = addr (unconditional)
               >JZ   addr : if zero programCounter = addr
               >JNZ  addr : if not zero programCounter = addr
               >JC   addr : if zero programCounter = addr
               >JNZ  addr : if not zero programCounter = addr
               >JE   addr : if even programCounter = addr
               >JO   addr : if odd programCounter = addr
               >JP   addr : if positive programCounter = addr
               >JM   addr : if negative programCounter = addr
               >CALL addr : call a subroutine (unconditional)  
               >CZ   addr : call a subroutine if zero
               >CNZ  addr : call a subroutine if not zero
               >CC   addr : call a subroutine if carry 
               >CNC  addr : call a subroutine if not carry
               >CE   addr : call a subroutine if even
               >CO   addr : call a subroutine if odd
               >CP   addr : call a subroutine if positive
               >CM   addr : call a subroutine if negative
               >RET       : return from subroutine (unconditional)
               >RZ        : return from subroutine if zero
               >RNZ       : return from subroutine if not zero
               >RC        : return from subroutine if carry 
               >RNC       : return from subroutine if not carry
               >RE        : return from subroutine if even
               >RO        : return from subroutine if odd
               >RP        : return from subroutine if positive
               >RM        : return from subroutine if negative

        LOGICAL:

         OPCODE | OPERAND : DESCRIPTION
         ----------------------------------------------------------------
               >AND reg   : accumulator = accumulator & register
               >ANI reg   : accumulator = accumulator & immediate value
               >OR  reg   : accumulator = accumulator | register
               >ORI reg   : accumulator = accumulator | immediate value
               >XOR reg   : accumulator = accumulator ^ register
               >XRI reg   : accumulator = accumulator ^ immediate value
               >CMP reg   : compare register with accumulator
               >CMI reg   : compare immediate value with accumulator
               >CMC       : complement the carry flag
               >STC       : set the carry flag
               >CLC       : clear carry flag
               >CMA       : complement the accumulator (without affecting the flags)

        ARITHMETIC:

         OPCODE | OPERAND : DESCRIPTION
         ---------------------------------------------------------------------------------
               >ADD reg   : accumulator = accumulator + register 
               >ADC reg   : accumulator = accumulator + register  + carry
               >ADI imm8  : accumulator = accumulator + 8bit immediate value
               >SUB reg   : accumulator = accumulator - register 
               >SUC reg   : accumulator = accumulator - (register+(1-carry))
               >SUI imm8  : accumulator = accumulator - 8bit immediate value
               >INC reg   : register = register + 1
               >DEC reg   : register = register - 1
               >INX       : HL pair = HL pair + 1  
               >DEX       : HL pair = HL pair - 1 

        BITWISE:

         OPCODE | OPERAND : DESCRIPTION
         -------------------------------------------------------
               >RS  reg   : Logical right shift
               >LS  reg   : Logical left shift
               >ARS reg   : Arthmetic right shift
               >ALS reg   : Arithmetic left shift
               >RR  reg   : Logic right rotate
               >LR  reg   : Logic left rotate
               >ARR reg   : Arithmetic right rotate
               >ALR reg   : Arithmetic left rotate
    
    Assembler:
            
            >Lexical Analyzer  : Breaks down input assembly code into tokens
            >Praser            : Validates the systax of the tokens
            >Code Generator    : Converts mnemonics into machine code by looking them up in the CSV-based opcode table
            >Lable             : A label is identified by the '$' followed by the label name, Everytime a 
                                           label is created the corresoponding address is stored  dictionary.
            >Macros            : 

            



























