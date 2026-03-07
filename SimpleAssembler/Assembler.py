import re
import sys
REG={
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
    "add":{"opcode" : "0110011", "func3":"000", "func7":"0000000"},
    "sub":{"opcode" : "0110011", "func3":"000", "func7":"0100000"},
    "sll":{"opcode" : "0110011", "func3":"001", "func7":"0000000"},
    "slt":{"opcode" : "0110011", "func3":"010", "func7":"0000000"},
    "sltu":{"opcode" : "0110011", "func3":"011", "func7":"0000000"},
    "xor":{"opcode" : "0110011", "func3":"100", "func7":"0000000"},
    "srl":{"opcode" : "0110011", "func3":"101", "func7":"0000000"},
    "or":{"opcode" : "0110011", "func3":"110", "func7":"0000000"},
    "and":{"opcode" : "0110011", "func3":"111", "func7":"0000000"}
}

I_type ={
    "lw":{"opcode":"0000011", "func3":"010"},
    "addi":{"opcode":"0010011","func3":"000"},
    "sltiu":{"opcode":"0010011","func3":"000"}
}

S_type ={
    "sw":{"opcode":"0100011", "fucn3":"010"}
}

B_type ={
    "beq":{"opcode": "1100011", "func3": "000"},
    "bne":{"opcode": "1100011", "func3": "001"},
    "blt":{"opcode": "1100011", "func3": "100"},
    "bge":{"opcode": "1100011", "func3": "101"},
    "bltu":{"opcode": "1100011", "func3": "110"},
    "bgeu":{"opcode": "1100011", "func3": "111"}
}

U_type ={
    "lui":{"opcode":"0110111"},
    "auipc":{"opcode":"0010111"}
}

J_type ={
    "jal":{"opcode":"1101111"}
}

additional_type ={
    "mul":{"opcode":"0110011", "func3":"000", "func7":"0000001"},
    "rst":{"opcode": "00000000000000000000000000000000"},
    "halt":{"opcode":"11111111111111111111111111111111"},
    "rvrs":{"opcode":"0110011"}
}

# binary conversion
def conv_to_bin(val,bits):
    val = int(val)  # converting value to integeral value
    if val<0:
        val=(2**bits) + val   # converting negative number to 2's complement form
    binary = bin(val)[2:]  # converting number to binary and remove '0b'

    zeroes=bits-len(binary)
    binary=("0"*zeroes)+binary
    return binary

#register conversion

def reg_bits(regi):
    numb=REG[regi] #check for the register name in the REG directory
    binary=bin(numb)[2:] #convert register number into binary

    zeroes = 5- len(binary) #if binary is shorter than 5 bits(RISC-V), this will calculate  the zeroes needed
    binary =("0"*zeroes)+binary #add the required number of zeroes in the starting of the binary

    return binary

#To identiy labels in input
def label_identify(lines):
    labels={}
    pc=0

    for l in lines:
        l=l.strip()
        if l=="":
            continue
        if ":" in l:
            parts=l.split()
            lbl=parts[0]

            labels[lbl]=pc
        pc+=4
    return labels

#To Parse instructions
def parse_lines(l):
    l=l.strip()
    if ":" in l:
        parts=l.split(":")
        l=parts[1]
        l=l.strip()
    l=l.replace(","," ")
    tkns=l.split()
    return tkns
