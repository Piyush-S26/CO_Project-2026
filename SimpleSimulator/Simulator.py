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

