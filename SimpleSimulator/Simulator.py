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

def decode_r(bits): #R-Type instructions
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