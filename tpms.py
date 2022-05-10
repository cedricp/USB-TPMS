import serial

ser = serial.Serial("/dev/ttyUSB0", 19200, stopbits=serial.STOPBITS_ONE)

T_RF=0x01
T_LF=0x00
T_LR=0x10
T_RR=0x11
T_SP=0x05

TIREMAP = {T_RF: "RF",
           T_LF: "LF",
           T_RR: "RR",
           T_LR: "LR",
           T_SP: "SP"}

heartbeat_cmd       = [0x55, 0xaa, 0x06, 0x19, 0x00, 0x00]
heartbeatack_cmd    = [0x55, 0xaa, 0x06, 0x00, 0x00, 0x00]
resetdevice_cmd     = [0x55, 0xaa, 0x06, 0x58, 0x55, 0x00]
queryid_cmd         = [0x55, 0xaa, 0x06, 0x07, 0x00, 0x00]
encrypt_cmd         = [0x55, 0xaa, 0x06, 0x5b, 0x20, 0x00]

pairrl_cmd          = [0x55, 0xaa, 0x06, 0x01, T_LR, 0x00]
pairrr_cmd          = [0x55, 0xaa, 0x06, 0x01, T_RR, 0x00]
pairfl_cmd          = [0x55, 0xaa, 0x06, 0x01, T_LF, 0x00]
pairfr_cmd          = [0x55, 0xaa, 0x06, 0x01, T_RF, 0x00]
pairspare_cmd       = [0x55, 0xaa, 0x06, 0x01, T_SP, 0x00]
stoppair_cmd        = [0x55, 0xaa, 0x06, 0x06, 0x00, 0x00]

ex_lfrf_cmd         = [0x55, 0xaa, 0x07, 0x03, T_LF, T_RF, 0x00]
ex_lflr_cmd         = [0x55, 0xaa, 0x07, 0x03, T_LF, T_LR, 0x00]
ex_lfrr_cmd         = [0x55, 0xaa, 0x07, 0x03, T_LF, T_RR, 0x00]
ex_rflr_cmd         = [0x55, 0xaa, 0x07, 0x03, T_RF, T_LR, 0x00]
ex_rfrr_cmd         = [0x55, 0xaa, 0x07, 0x03, T_RF, T_RR, 0x00]
ex_lrrr_cmd         = [0x55, 0xaa, 0x07, 0x03, T_LR, T_RR, 0x00]
ex_splr_cmd         = [0x55, 0xaa, 0x07, 0x03, T_LR, T_SP, 0x00]
ex_sprr_cmd         = [0x55, 0xaa, 0x07, 0x03, T_RR, T_SP, 0x00]
ex_splf_cmd         = [0x55, 0xaa, 0x07, 0x03, T_LF, T_SP, 0x00]
ex_splr_cmd         = [0x55, 0xaa, 0x07, 0x03, T_LR, T_SP, 0x00]

def calcCC(arr):
    b = arr[2]
    b2 = arr[0]
    for i in range(1, b-1):
        b2 = b2 ^ arr[i]
    return b2

def send_cmd(cmd):
    cmd[-1] =  calcCC(cmd)
    ser.write(bytes(cmd))
    
send_cmd(queryid_cmd)
while 1:
    array = ser.read(3)
    array += ser.read(array[2]-3)
    command = array[2]
    cc = calcCC(array)
    if cc != array[-1]:
        print("Checksum error")
    if command == 0x08:
        tireCode = array[3]
        
        # Tire pressure conversion to bar unit
        pressure = int(array[4] * 3.44) / 100
        # Tire temperature to celcius degrees
        temp = array[5] - 50
        
        nosignal = array[6] & 0b10000000
        leakage  = array[6] & 0b00001000
        lowbattery = array[6] & 0b00010000
        
        print("OK", TIREMAP[tireCode], pressure, temp, nosignal, leakage, lowbattery)
    elif command == 0x09:
        print("Tire ID:", array[3], hex(array[4]), hex(array[5]), hex(array[6]), hex(array[7]))
    elif command == 0x06:
        if array[3] == 0x18:
            print("Paired tire: ", TIREMAP[array[4]])
        else:
            print("Paring tire: ", TIREMAP[array[4]])
    else:
        print("Unknown frame >> ", array)

