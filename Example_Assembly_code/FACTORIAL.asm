$START: LDI 04

MOV B,A
LOOP: DCR B /loop that does n*(n-1)
JZ END
MOV C,A
MOV D,B
XOR C
$LOOP1: ADD C /loop that multiplies two numbers
DCR D 
JNZ LOOP1
JZ LOOP
$END: STA 00 /End if completed
HLT