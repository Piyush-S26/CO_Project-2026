import sys
reg_map={
    "zero":0, "x0":0, 
    "ra":1, "x1":1, 
    "sp":2, "x2":2, 
    "gp":3, "x3":3, 
    "tp":4, "x4":4,
    "t0":5, "x5":5, 
    "t1":6, "x6":6, 
    "t2":7, "x7":7, 
    "s0":8, "fp":8, "x8":8, 
    "s1":9, "x9":9, 
    "a0":10, "x10":10,
    "a1":11, "x11":11, 
    "a2":12, "x12":12, 
    "a3":13, "x13":13, 
    "a4":14, "x14":14, 
    "a5":15, "x15":15,
    "a6":16, "x16":16, 
    "a7":17, "x17":17, 
    "s2":18, "x18":18, 
    "s3":19, "x19":19, 
    "s4":20, "x20":20, 
    "s5":21, "x21":21,
    "s6":22, "x22":22,
    "s7":23, "x23":23, 
    "s8":24, "x24":24, 
    "s9":25, "x25":25, 
    "s10":26, "x26":26, 
    "s11":27, "x27":27, 
    "t3":28, "x28":28,
    "t4":29, "x29":29, 
    "t5":30, "x30":30,
    "t6":31, "x31":31,
}

R_type ={
    "add":{
        "opcode":"0110011", 
        "func3":"000", 
        "func7":"0000000"}, 
    "sub":{
        "opcode":"0110011", 
        "func3":"000", 
        "func7":"0100000"},
    "sll":{
        "opcode":"0110011", 
        "func3":"001", 
        "func7":"0000000"}, 
    "slt":{
        "opcode":"0110011", 
        "func3":"010", 
        "func7":"0000000"},
    "sltu":{
        "opcode":"0110011", 
        "func3":"011", 
        "func7":"0000000"}, 
    "xor":{
        "opcode":"0110011", 
        "func3":"100", 
        "func7":"0000000"},
    "srl":{
        "opcode":"0110011", 
        "func3":"101", 
        "func7":"0000000"}, 
    "or":{
        "opcode":"0110011", 
        "func3":"110", 
        "func7":"0000000"},
    "and":{
        "opcode":"0110011", 
        "func3":"111", 
        "func7":"0000000"}
}

I_type ={
    "lw":{
        "opcode":"0000011", 
        "func3":"010"}, 
    "addi":{
        "opcode":"0010011",
        "func3":"000"}, 
    "sltiu":{
        "opcode":"0010011",
        "func3":"011"},
    "jalr":{
        "opcode":"1100111",
        "func3":"000"}
}

S_type ={
    "sw":{
        "opcode":"0100011", 
        "func3":"010"}
}

B_type ={
    "beq":{
        "opcode":"1100011", 
        "func3":"000"}, 
    "bne":{
        "opcode":"1100011", 
        "func3":"001"}, 
    "blt":{
        "opcode":"1100011", 
        "func3":"100"},
    "bge":{
        "opcode":"1100011", 
        "func3":"101"}, 
    "bltu":{
        "opcode":"1100011", 
        "func3":"110"}, 
    "bgeu":{
        "opcode":"1100011", 
        "func3":"111"}
}

U_type ={
    "lui":{
        "opcode":"0110111"}, 
    "auipc":{
        "opcode":"0010111"}
}

J_type ={
    "jal":{
        "opcode":"1101111"}
}

additional_type ={
    "mul":{
        "opcode":"0110011", 
        "func3":"000", 
        "func7":"0000001"}, 
    "rst":{
        "opcode":"00000000000000000000000000000000"},
    "halt":{
        "opcode":"11111111111111111111111111111111"}, 
    "rvrs":{
        "opcode":"0110011",
        "func3":"000",
        "func7":"0100000"}
}

# binary conversion
def conv_to_bin(val,bits):
    val = int(val)  # converting value to integeral value
    if val<0:
        val=(2**bits) + val   # converting negative number to 2's complement form
    binary = bin(val)[2:]  # converting number to binary and remove '0b'

    if len(binary)>bits:
        starting= len(binary)-bits
        binary=binary[starting:len(binary)]
    zeroes=bits-len(binary)
    binary=("0"*zeroes)+binary
    return binary

#register conversion

def reg_bits(regi):

    #register error check
    if regi not in reg_map:
        print("error: invalid register")
        sys.exit()
    
    #regitser checking 

    numb=reg_map[regi] #check for the register name in the reg_map directory
    binary=bin(numb)[2:] #convert register number into binary

    zeroes = 5- len(binary) #if binary is shorter than 5 bits(RISC-V), this will calculate  the zeroes needed
    binary =("0"*zeroes)+binary #add the required number of zeroes in the starting of the binary

    return binary



#To identiy labels in input
def label_identify(lines):
    labels={}
    pc=0 #Program counter starting from 0

    for l in lines:
        l=l.strip() #To remove leading or trailing spaces
        if l=="":
            continue
        if ":" in l: #To check if label exists
            parts=l.split(":")
            lbl=parts[0].strip() #To extracting label name from input
            
            if lbl in labels:
                print("error: duplicate labels")
                sys.exit()
            labels[lbl]=pc
            if parts[1].strip() == "":
                continue

        pc+=4 #Moving pc to next instruction 
    return labels

#To Parse instructions
def parse_lines(l):
    l=l.strip() #This removes extra spaces
    if ":" in l:
        parts=l.split(":") #This splits labels and instructions
        l=parts[1]
        l=l.strip() 
    l=l.replace(","," ") #Replace commas with blank spaces
    l=l.replace("("," ") #Replace brackets with blank spaces
    l=l.replace(")"," ")
    tkns=l.split() #This breaks into instruction tokens
    return tkns

def encode_instruction(instruct,operands,pc,labels):
    
    #encoding instruction error checking
    if (instruct not in R_type and instruct not in I_type and instruct not in S_type and instruct not in B_type and instruct not in U_type 
        and instruct not in J_type and instruct not in additional_type):
        print("error: invalid instruction")
        sys.exit()
    
    #operand count error checking
    try :
        if instruct in R_type:
            rd = operands[0]
            rs1 = operands[1]
            rs2 = operands[2]
        elif instruct in I_type:
            rd = operands[0]
            rs1 = operands[1]
            imm = operands[2]
        elif instruct in S_type:
            rs2 = operands[0]
            imm = operands[1]
            rs1 = operands[2]
        elif instruct in J_type:
            rd = operands[0]
            imm = operands[1]   
        elif instruct in B_type:
            rs1 = operands[0]
            rs2 = operands[1]
            imm = operands[2]
        elif instruct in U_type:
            rd = operands[0]
            imm = operands[1]
      
    except :
        print("error: invalid operands")
        sys.exit()

    #R-type
    #func7[31:25]|rs2[24:20]|rs1[19:15]|func3[14:12]|rd[11:7]|opcode[6:0]

    if instruct in R_type: #checks whether instruction belongs to r-type dictionary
        rd=operands[0]
        rs1=operands[1]
        rs2=operands[2]
        encoding= R_type[instruct] #get opcode, func3, func7 for this instruction
        return(
            encoding["func7"] #add func7 bits
            +reg_bits(rs2)
            +reg_bits(rs1)
            +encoding["func3"] #add func3 bits
            +reg_bits(rd)
            +encoding["opcode"] #add opcode bits
        )
    

     #I-type 
     #imm[31:20]|rs1[19:15]|func3[14:12]|rd[11:7]|opcode[6:0]

    elif instruct in I_type: #checks whether instruction belongs to I-type dictionary 
        rd=operands[0] #destination register

        if instruct=="lw":
            imm_val=operands[1]
            rs1=operands[2]
        else:
            rs1=operands[1]
            imm_val=operands[2]
        if imm_val in labels:
            imm=labels[imm_val]-pc
        else:
            try:
                imm=int(imm_val)
            except:
                print("error: invalid immediate value")
                sys.exit()

        encoding=I_type[instruct]
        imm_bin=conv_to_bin(imm,12)

        return(
            imm_bin
            +reg_bits(rs1)
            +encoding["func3"]
            +reg_bits(rd)
            +encoding["opcode"]
        )
    
    #S-type
    #imm[31:25]|rs2[24:20]|rs1[19:15]|funct3[14:12]|imm[11:7]|opcode[6:0]

    elif instruct in S_type: #checks whether instruction belongs to S-type dictionary
        rs2=operands[0] #Value register
        try:
            imm=int(operands[1]) #Immediate offset
        except:
            print("error: invalid immediate value")
            sys.exit()
        
        rs1=operands[2]
        
        encoding=S_type[instruct] #This fetches opcode and func3
        imm_bin=conv_to_bin(imm,12) #Convert immediate to 12-bit binary number
        if imm_bin is None:
            return "INVALID"
        imm_high=imm_bin[:7] #imm[11:5]
        imm_low=imm_bin[7:] #imm[4:0]

        return(imm_high+reg_bits(rs2)+reg_bits(rs1)+encoding["func3"]+imm_low+encoding["opcode"])

    #J type
    # imm[20]|imm[10:1]|imm[11]|imm[19:12]|rd[11:7]|opcode[6:0]
    elif instruct in J_type:
        rd=operands[0]
        if operands[1] in labels:
            imm = labels[operands[1]] - pc
        else:
            try:
                imm = int(operands[1])
            except:
                print("error: invalid immediate value")
                sys.exit()
            
        encoding=J_type[instruct]  #getting opcide information from dictionary
        imm_bin=conv_to_bin(imm,21) #converting immediate value to 21 binary

        if imm_bin is None:
            return "error: invalid numbers"

        immediate = (
            imm_bin[0]+ imm_bin[10:20]+ imm_bin[9]+imm_bin[1:9]
        )

        return immediate+ reg_bits(rd) +J_type[instruct]["opcode"]
    
    #B type 
    #imm[31:25]|rs2[24:20]|rs1[19:15]|func3[14:12]|imm[11:7]|opcode[6:0]

    elif instruct in B_type:

        rs1= operands[0]
        rs2= operands[1]
        if operands[2] in labels:
            imm = labels[operands[2]] - pc
        else:
            try:
                imm = int(operands[2])
            except:
                print("error: invalid immediate value")
                sys.exit()

        imm_bin=conv_to_bin(imm,13)

        if imm_bin==None:
            return "error: invalid instruction"
        
        bit_12=imm_bin[0]
        bit_10_to_5=imm_bin[2:8]
        bit_4_to_1=imm_bin[8:12]
        bit_11=imm_bin[1]

        func3=B_type[instruct]["func3"]
        opcode=B_type[instruct]["opcode"]

        return (
            bit_12 + bit_10_to_5 + reg_bits(rs2) + reg_bits(rs1) + func3 + bit_4_to_1 + bit_11 + opcode
        )
        
    #U type
    #imm[31:12]|rd[11:7]|opcode[6:0]

    elif instruct in U_type:
        
        rd=operands[0] #Dest Reg

        try:
            imm=int(operands[1])
        except:
            print("error: invalid immediate value")
            sys.exit()

        encoding=U_type[instruct] #This fetches opcode

        imm_bin=conv_to_bin(imm,20) #Converts immediate to 20-bit binary number

        if imm_bin is None:
            return "INVALID"
        return(imm_bin+reg_bits(rd)+encoding["opcode"])
    
    else:
        return "error: invalid instruction"

input_files=sys.argv[1] #this load the entire program from standard input
output_files=sys.argv[2]
with open(input_files,"r") as f:
    program_lines=f.readlines()

out=open(output_files,"w")

labels = label_identify(program_lines) # this is first pass

#Virtual Halt check
# last_line=None
# for i in reversed(program_lines):
#     if i.strip() != "":
#         last_line=parse_lines(i)
#         break 

# instr=last_line[0]
# r1=last_line[1]
# r2=last_line[2]
# imme=last_line[3].strip()

# if instr=="beq" and r1 in ["zero","x0"] and r2 in ["zero","x0"] and imme=="0":
#     pass
# else:
#     print("error: virtual halt is missing")
#     sys.exit()
last_instr = None

for line in reversed(program_lines):
    tokens = parse_lines(line)
    if len(tokens) > 0:
        last_instr = tokens
        break

if not (last_instr[0] == "beq"
        and last_instr[1] in ["zero","x0"]
        and last_instr[2] in ["zero","x0"]
        and last_instr[3] == "0"):
    print("error: virtual halt is missing")
    sys.exit()
pc=0
for raw_line in program_lines:
    cleaned_line = raw_line.strip() #this remove extra whiteespace
    if cleaned_line == "": #this ignore blank line
        continue
    parts = parse_lines(cleaned_line) #this covert line into tokens 
    if len(parts) ==0:
        continue
    opcode = parts[0] #instruction name 
    args = parts[1:]  # operands
    machine_code = encode_instruction(opcode, args, pc, labels) # this does binary encoding
    out.write(machine_code)
    out.write("\n")
    pc += 4

out.close()
