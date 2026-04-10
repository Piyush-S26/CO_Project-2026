#GROUP NO 66

#PIYUSH BHAMBRI - 2025371
#PIYUSH - 2025370
#RUDRA PALIWAL - 2025435
#PRAGYA PAL - 2025379

import sys
# memory configuration
DATA_BASE_addr = 0x00010000
total_data = 32

stack_pointer_init = 0x0000017C
max_prog_size = 64

#custom exception for invalid mem access
class invld_mem_acc(Exception):
    pass

#helper functions
def to_unsign32(val): #for val to stay within 32-bit unsigned range
    return val & 0xFFFFFFFF


def to_sign32(val): #coverts unsigned 32-bit to signed 2's complement
    val = to_unsign32(val)
    if val >= (1<<31):
        return val - (1<<32)
    
    return val

def sign_ext(val,bits): #extends sign for immeediate vals
    sign_bit = 1<<(bits-1)

    return (val^sign_bit) - sign_bit

def bin_to_integ(bits): #converts binary to integer 
    return int(bits,2)

def form_bin32(val):
    return "0b" + format(to_unsign32(val),"032b") #formats val as 32-bit binary string 

def form_hex32(val):

    return "0x" + format(to_unsign32(val),"08X") #formats val as 32-bit hexadecimal string 

#Decoders
#R-Type instructions
def decode_r(bits):
    return {
        "func7": bits[0:7],
        "rs2": bin_to_integ(bits[7:12]),

        "rs1": bin_to_integ(bits[12:17]),
        "func3": bits[17:20],
        "rd": bin_to_integ(bits[20:25]),
    }

def decode_i(bits):  #I- type instructions
    return {
        "imme": sign_ext(bin_to_integ(bits[0:12]), 12),
        "rs1": bin_to_integ(bits[12:17]),

        "func3": bits[17:20],

        "rd": bin_to_integ(bits[20:25]),
    }

def decode_b(bits):  #B type instrcution
    imm_bits=bits[0]+bits[24]+bits[1:7]+bits[20:24]+"0"

    return {
        "imme":sign_ext(bin_to_integ(imm_bits),13),
        "rs2":bin_to_integ(bits[7:12]),
        "rs1":bin_to_integ(bits[12:17]),
        "func3": bits[17:20],
    }

def decode_u(bits):  #U type instructions
    return {

        "imme":bin_to_integ(bits[0:20])<<12,
        "rd":bin_to_integ(bits[20:25]),
    }

def decode_s(bits):  #S type instructions
    imm_bits=bits[0:7]+bits[20:25]
    return {

        "imme": sign_ext(bin_to_integ(imm_bits), 12),
        
        "rs2": bin_to_integ(bits[7:12]),
        "rs1": bin_to_integ(bits[12:17]),
        "func3": bits[17:20],
    }

def decode_j(bits): # J type instruction
    imm_bits = bits[0]+bits[12:20]+bits[11]+bits[1:11]+"0"
    return {

        "imme": sign_ext(bin_to_integ(imm_bits), 21),
        "rd": bin_to_integ(bits[20:25]),
    }

#mem helpers
#This ensures address is valid and word aligned
def check_mem_add(address):
    address=to_unsign32(address)

    if address%4 != 0:
        raise invld_mem_acc()
    return address

#Load word from memor(default=0)
def lw(mem,address):

    address=to_unsign32(address)

    return mem.get(address,0) #(default=0 if not presuent)

#Stores word in memory
def sw(mem,address,val):
    address=to_unsign32(address)

    mem[address]=to_unsign32(val)

def app_state(state,pc,registers):
    #PC + all registers 
    line=[form_bin32(pc)] 

    line.extend(form_bin32(r)for r in registers)
    state.append(" ".join(line)+" ")

def execute_step(pc,registers,mem,instruc,state):
    #check PC alignment
    if pc%4 != 0:
        raise Exception("invalid nstruction address")
    idx=pc//4
    if idx < 0 or idx >= len(instruc):
        raise Exception("PC is out of range")
    bits=instruc[idx]
    opcode=bits[25:32] 
    halt=False

    #R Type
    if opcode=="0110011":
        f = decode_r(bits)  #This decode R-type fields
        val1 = registers[f["rs1"]]
        val2 = registers[f["rs2"]]
        #These Convert to signed for arithmetic ops
        val1_s = to_sign32(val1)
        val2_s = to_sign32(val2)
        #ALU operations based on func3 & func7
        if f["func7"]=="0000000" and f["func3"]=="000":
            res = val1_s + val2_s  #ADD
        elif f["func7"]=="0100000" and f["func3"]=="000":
            res = val1_s-val2_s    #SUB
        elif f["func3"]=="001":
            res = val1 << (val2 &0x1F)  #SLL
        elif f["func3"]=="010":
            res = 1 if val1_s < val2_s else 0  #SLT
        elif f["func3"]=="011":
            res = 1 if val1 <val2 else 0  #SLTU
        elif f["func3"]=="100":
            res = val1^val2  #XOR
        elif f["func3"]=="101":
            res = val1 >> (val2 & 0x1F) #SRL
        elif f["func3"]=="110":
            res = val1|val2  #OR
        elif f["func3"]=="111":
            res = val1&val2  #AND
        else:
            raise Exception("Unsupported R-type")
        
        if f["rd"]!= 0:    # Write resuult to destination register(except x0)
            registers[f["rd"]] = to_unsign32(res)
        pc+=4

    #I Type
    elif opcode=="0010011":
        f=decode_i(bits)
        src=registers[f["rs1"]]
        src_s=to_sign32(src)
    #ALU immeediate operations
        if f["func3"]=="000":
            res = src_s+f["imme"]
        elif f["func3"] =="011":
            res=1 if src < to_unsign32(f["imme"]) else 0
        else:
            raise Exception("Unsupported I-type")
        if f["rd"] != 0:
            registers[f["rd"]]=to_unsign32(res)

        pc+=4

    #Store
    elif opcode=="0100011":
        f=decode_s(bits)
        addr = check_mem_add(registers[f["rs1"]]+f["imme"])
        sw(mem,addr,registers[f["rs2"]])
        pc+=4
 
    #LOAD type
    elif opcode =="0000011":
        f=decode_i(bits)
        #effective address= base + offset
        addr=check_mem_add(registers[f["rs1"]] + f["imme"])  #effective address
        val=lw(mem, addr)
        if f["rd"]!= 0:

            registers[f["rd"]]=val
        pc+=4

    #Branch type
    elif opcode=="1100011":
        f=decode_b(bits)

        a=registers[f["rs1"]]
        b=registers[f["rs2"]]


        val1_s=to_sign32(val1)
        val2_s=to_sign32(val2)

    #  checking Branch condition
        if f["func3"]=="000":
            branch_take= val1_s == val2_s   #BEQ
            
        elif f["func3"]=="001":
            branch_take= val1_s!=val2_s   #BNE
        elif f["func3"]=="100":
            branch_take= val1_s<val2_s     #BLT
        elif f["func3"]=="101":
            branch_take= val1_s>=val2_s   #BGE 
        elif f["func3"]=="110":
            branch_take= val1<val2        #BLTU
        elif f["func3"]=="111":
            branch_take= val1>=val2      #BGEU
        else:
            raise Exception("unsupported branch")
        # pc = pc + f["imme"] if branch_take else pc + 4
        if branch_take:
            pc = pc + f["imm"]
        else:
            pc = pc + 4
#Detect halt condition(all zero instruction)
        halt = (
            f["func3"]=="000" and f["rs1"]==0 and f["rs2"]== 0 and f["imme"]== 0
        )
#LUI
    elif opcode=="0110111":
        f = decode_u(bits)
        if f["rd"]!=0:
            registers[f["rd"]] =f["imme"] #load upper immeediate
        pc += 4

    #AUIPC
    elif opcode =="0010111":
        f = decode_u(bits)
        if f["rd"]!=0:
            registers[f["rd"]] = pc + f["imme"] #PC-relative add
        pc += 4

    #JAL
    elif opcode =="1101111":
        f = decode_j(bits)
        next_pc = pc + 4
        if f["rd"] !=0:
            registers[f["rd"]] = next_pc
        pc += f["imme"]

    #JALR
    elif opcode=="1100111":
        f = decode_i(bits)
        next_pc = pc+4
        target = (registers[f["rs1"]] + f["imme"]) & 0xFFFFFFFE  #aligned target

        if f["rd"]!=0:
            registers[f["rd"]] = next_pc
        pc= target

    else:
        raise Exception("Unsupported opcode")

    registers[0]=0
    app_state(state,pc,registers)
    return pc,halt
# RUN
def run_prog(instruc):
    pc=0
    registers=[0]*32
    registers[2]=stack_pointer_init  #initialize stack pointer
    mem={}
    state=[]
    try:
        for _ in range(100000):  #execution limit(avoid infinite loop)
            pc, halt = execute_step(pc, registers, mem, instruc, state)
            if halt:
                break
        else:
            raise Exception("Program did not halt")
    except invld_mem_acc:
        return state  

    #dump memory contens
    for i in range(total_data):
        addr = DATA_BASE_addr + i * 4
        val = mem.get(addr, 0)
        state.append(f"{form_hex32(addr)}:{form_bin32(val)}")
    return state
#INPUT
def load_instruc(path):
    instruc=[]
    with open(path,"r") as f:
        for line_num, line in enumerate(f, start=1):
            line=line.strip()
            if not line:
                continue
            #validate 32-bit binary instruction
            if len(line)!=32 or any(c not in "01" for c in line):
                raise Exception(f"Invalid instruction at line {line_num}")
            instruc.append(line)
    if not instruc:
        raise Exception("Empty program")
    if len(instruc)>max_prog_size:
        raise Exception("Program too large")
    return instruc
# Main 
def main():
    if len(sys.argv) < 3:
        print("Usage: python3 sim.py <input> <output>")
        sys.exit(1)
    instruc=load_instruc(sys.argv[1])
    state=run_prog(instruc)
    with open(sys.argv[2], "w") as f:
        f.write("\n".join(state) + "\n")

if __name__ == "__main__":
    main()