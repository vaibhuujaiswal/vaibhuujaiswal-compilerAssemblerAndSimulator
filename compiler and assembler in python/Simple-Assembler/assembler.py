from sys import stdin 
assembly_program_lines = []
instructions = []

# Dictionary containing opcodes for instructions
opcodes = {
    'add': '00000' ,
    'sub': '00001' ,
    'mov':('00010' , '00011'),
    'ld':  '00100' ,
    'st':  '00101' ,
    'mul': '00110' ,
    'div': '00111' ,
    'rs':  '01000' ,
    'ls':  '01001' ,
    'xor': '01010' ,
    'or':  '01011' ,
    'and': '01100' ,
    'not': '01101' ,
    'cmp': '01110' ,
    'jmp': '01111' ,
    'jlt': '10000' ,
    'jgt': '10001' ,
    'je':  '10010' ,
    'hlt': '10011'
}

# Dictionary containing types of instructions
types = {
    'add': 'A', 
    'sub': 'A', 
    'mov': 'X', 
    'ld':  'D',  
    'st':  'D', 
    'mul': 'A', 
    'div': 'C',
    'rs':  'B',
    'ls':  'B', 
    'xor': 'A', 
    'or':  'A', 
    'and': 'A', 
    'not': 'C', 
    'cmp': 'C', 
    'jmp': 'E', 
    'jlt': 'E', 
    'jgt': 'E', 
    'je':  'E', 
    'hlt': 'F'
}

# Dictionaries with label/variable names as keys and addresses as values
labels = dict()
variables = dict()

# Function for converting an int to a binary string of defined length
def convert_to_bin(val, noOfBits):
    bit_str = ""
    while val > 0:
        if(val % 2 == 0):
            bit_str = '0' + bit_str
        else:
            bit_str = '1' + bit_str
        val >>= 1
    while len(bit_str) < noOfBits:
        bit_str = '0' + bit_str
    return bit_str

# Function for taking register value (string) and returning its value (int)
# Returns -1 if register is invalid or called illegally
def identify_register(regName, lineNo, flagsAllowed = False):
    if(regName == "FLAGS"):
        if(flagsAllowed):
            return 7
        print("Error (Line " + str(lineNo) + "): Illegal use of FLAGS register")
        return -1
    regVal = -1
    if(regName[0] == 'R'):
        try:
            regVal = int(regName[1:])
            if(regVal < 0 or regVal > 6):
                regVal = -1
        except:
            regVal = -1
    if(regVal == -1):
        print("Error (Line " + str(lineNo) + "): Invalid register name '" + regName + "'")
    return regVal

# Function to assemble the split input code and store binary code in instructions[]
# Returns True if assembly is successful, False otherwise
def assemble():
    gettingVar = True
    exit = False
    lineNo = 0
    varCount = 0
    halt_check = 0
    
    # Identifying non-var instructions and assigning addresses to them
    line_addresses = []
    for cmd in assembly_program_lines:
        if(cmd[0] == "var"):
            line_addresses.append(-1)
        else:
            break
    noOfInstructions = 0
    while(len(line_addresses) < len(assembly_program_lines)):
        line_addresses.append(noOfInstructions)
        noOfInstructions += 1
    
    # Identifying and saving Labels
    address = 0
    lineNo = len(assembly_program_lines) - noOfInstructions + 1
    for cmd_split in assembly_program_lines[len(assembly_program_lines) - noOfInstructions:]:
        if(cmd_split[0][-1] == ':'):
            labelName = cmd_split.pop(0)[0:-1]
            for character in labelName:
                if not character.isalnum() and not character == '_':
                    print("Error (Line " + str(lineNo) + "): Invalid label name '" + labelName + "'")
                    return False
            if(labelName in labels):
                print("Error (Line " + str(lineNo) + "): Label '" + labelName + "' already exists")
                return False
            if(labelName in types):
                print("Error (Line " + str(lineNo) + "): '" + labelName + "' is an instruction name. Cannot be used as label")
                return False
            if(labelName in ['R0','R1','R2','R3','R4','R5','R6','FLAGS']):
                print("Error (Line " + str(lineNo) + "): '" + labelName + "' is a register name. Cannot be used as label")
                return False
            else:
                labels[labelName] = address
        address += 1
        lineNo += 1
    lineNo = 0
 
    # Checking 'hlt' at the end
    if assembly_program_lines[len(assembly_program_lines) - 1][0] != 'hlt':  #check whether the last element is halt or not
        print("Error (Line " + str(len(assembly_program_lines)) + "): halt statement not present in the end")
        return False
 
    for cmd_split in assembly_program_lines:
        lineNo += 1
 
        if(len(cmd_split) <= 0):
            print("Error (Line " + str(lineNo) + "): Label not pointing to a valid address")
            return False
        
        # Identifying and saving Variables
        if(cmd_split[0] == "var"):
            if(gettingVar):
                if(len(cmd_split) != 2):
                    print("Error (Line " + str(lineNo) + "): Invalid syntax for 'var' instruction")
                    return False
                for character in cmd_split[1]:
                    if not character.isalnum() and not character == '_':
                        print("Error (Line " + str(lineNo) + "): Invalid variable name '" + cmd_split[1] + "'")
                        return False
                if(cmd_split[1] in variables):
                    print("Error (Line " + str(lineNo) + "): Variable '" + cmd_split[1] + "' already exists")
                    return False
                if(cmd_split[1] in types):
                    print("Error (Line " + str(lineNo) + "): '" + cmd_split[1] + "' is an instruction name. Cannot be used as variable")
                    return False
                if(cmd_split[1].isdigit()):
                    print("Error (Line " + str(lineNo) + "): Variable name '" + cmd_split[1] + "' cannot be numeric")
                    return False
                variables[cmd_split[1]] = noOfInstructions + varCount
                varCount += 1
 
            else:
                print("Error (Line " + str(lineNo) + "): Variable not declared at the beginning")
                return False
        
        else:
            gettingVar = False
 
            machine_code = ""
            if cmd_split[0] in types.keys():
              opcode = opcodes[cmd_split[0]]
              inst_type = types[cmd_split[0]]
              input_type = '?'
            else:
              print("Error (Line " + str(lineNo) + "): Invalid instruction name '" + cmd_split[0] + "'")
              return False

            # Detecting the instruction type used in input
            if(len(cmd_split) == 1):
                input_type = 'F'
            elif(len(cmd_split) == 2):
                input_type = 'E'
            elif(len(cmd_split) == 3):
                if(cmd_split[2][0] == '$'):
                    input_type = 'B'
                elif(cmd_split[2] in ['R0','R1','R2','R3','R4','R5','R6','FLAGS']):
                    input_type = 'C'
                else:
                    input_type = 'D'
            elif(len(cmd_split) == 4):
                input_type = 'A'
            if(input_type == '?'):
                print("Error (Line " + str(lineNo) + "): Instruction Type not identified")
                return False

            # 'mov' instructions are assigned Types B or C depending on input
            if (inst_type == 'X'):
                if (len(cmd_split) != 3):
                    print("Error (Line " + str(lineNo) + "): '" + cmd_split[0] + "' is not a Type " + input_type + " instruction")
                    return False
                if(cmd_split[2][0] == '$'):
                    if(cmd_split[2][1:].isdigit()):
                        opcode="00010"
                        inst_type="B"
                    else:
                        print("Error (Line " + str(lineNo) + "): Invalid immediate")
                        return False
                else:
                    opcode="00011"
                    inst_type="C"
            
            if(inst_type != input_type):
                print("Error (Line " + str(lineNo) + "): '" + cmd_split[0] + "' is not a Type " + input_type + " instruction")
                return False
            
            machine_code = opcode
 
            # Type A: 3 Register type
            if (inst_type == 'A'):
                reg1 = identify_register(cmd_split[1], lineNo)
                reg2 = identify_register(cmd_split[2], lineNo)
                reg3 = identify_register(cmd_split[3], lineNo)
                if(reg1 < 0 or reg2 < 0 or reg3 < 0):
                    return False
                machine_code += "00" + convert_to_bin(reg1,3) + convert_to_bin(reg2,3) + convert_to_bin(reg3,3)
            
            # Type B: Register and Immediate type
            elif (inst_type == 'B'):
                reg1 = identify_register(cmd_split[1], lineNo)
                imm = ''
                imm = int(cmd_split[2][1:])
                if(imm < 0 or imm > 255):
                    print("Error (Line " + str(lineNo) + "): Illegal immediate value '" + cmd_split[2] + "'")
                    return False
                machine_code += convert_to_bin(reg1, 3) +convert_to_bin(imm, 8)
      
            # Type C: 2 Register type
            elif (inst_type == 'C'):
                reg1 = identify_register(cmd_split[1], lineNo)
                reg2 = identify_register(cmd_split[2], lineNo, flagsAllowed = True)
                if(reg1 < 0 or reg2 < 0 ):
                    return False
                machine_code += '00000' + convert_to_bin(reg1, 3) + convert_to_bin(reg2, 3)
 
            # Type D: Register and Memory Address type
            elif (inst_type == 'D'):
                reg1 = identify_register(cmd_split[1], lineNo)
                if(reg1 < 0):
                    return False
                memory_addr = -1
                if(cmd_split[2] in variables):
                    memory_addr = variables[cmd_split[2]]
                else:
                    print("Error (Line " + str(lineNo) + "): Variable '" + cmd_split[2] + "' not found")
                    return False
                machine_code += convert_to_bin(reg1, 3) + convert_to_bin(memory_addr, 8)
 
            # Type E: Memory Address type
            elif (inst_type == 'E'): 
                memory_addr = -1
                if(cmd_split[1] in labels):
                    memory_addr = labels[cmd_split[1]]
                else:
                    print("Error (Line " + str(lineNo) + "): Label '" + cmd_split[1] + "' not found")
                    return False
                machine_code += '000' + convert_to_bin(memory_addr, 8)
                                 
            # Type E: Halt
            elif (inst_type == 'F'): 
                if halt_check > 0 :
                    print("Error (Line " + str(lineNo) + "): Multiple 'hlt' statements detected")
                    return False
                else:
                    halt_check += 1
                    machine_code += '00000000000'
 
            instructions.append(machine_code)
 
    return True

# Function for output of assembled code
def display_machine_code(instructions):
    for i in instructions:
        print(i)

# Function for input of assembly code
def input_func(assembly_program_lines):
    for inp in stdin:
        cmd_list = [str(assembly_line) for assembly_line in inp.split()]
        if len(cmd_list) == 0: #if there are any empty lists
            continue
        assembly_program_lines.append(cmd_list)
 
def main():
    input_func(assembly_program_lines)
    successfulExecution = assemble()
 
    if(successfulExecution):
        display_machine_code(instructions)
 
main()