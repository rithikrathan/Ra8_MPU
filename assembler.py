import glob
import os

print('salutations my fellow humanoids')
print()

def getFile(directory = 'Assembly_code'):
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

filePath,fileName = getFile()




