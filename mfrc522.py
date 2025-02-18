import time # for loop timings
import signal # for rfid
import spidev # for spi communication

BITS_0_AND_7_MASK   = 0x7E        # 0111_1110
SPI_READ_MODE_MASK  = 0x80        # 1000_0000
ANTENNAE_MASK       = 0x03        # 0000_0011; bit0=tx1, bit1=tx2

class mfrc522:

    MAX_LEN = 16


    PCD_IDLE       = 0x00
    PCD_AUTHENT    = 0x0E
    PCD_RECEIVE    = 0x08
    PCD_TRANSMIT   = 0x04
    PCD_TRANSCEIVE = 0x0C
    PCD_RESETPHASE = 0x0F
    PCD_CALCCRC    = 0x03

    PICC_REQIDL    = 0x26
    PICC_REQALL    = 0x52
    PICC_ANTICOLL1  = 0x93
    PICC_ANTICOLL2  = 0x95
    PICC_ANTICOLL3  = 0x97
    PICC_AUTHENT1A = 0x60
    PICC_AUTHENT1B = 0x61
    PICC_READ      = 0x30
    PICC_WRITE     = 0xA0
    PICC_DECREMENT = 0xC0
    PICC_INCREMENT = 0xC1
    PICC_RESTORE   = 0xC2
    PICC_TRANSFER  = 0xB0
    PICC_HALT      = 0x50

    MI_OK       = 0
    MI_NOTAGERR = 1
    MI_ERR      = 2

    Reserved00     = 0x00
    CommandReg     = 0x01
    CommIEnReg     = 0x02
    DivlEnReg      = 0x03
    CommIrqReg     = 0x04
    DivIrqReg      = 0x05
    ErrorReg       = 0x06
    Status1Reg     = 0x07
    Status2Reg     = 0x08
    FIFODataReg    = 0x09
    FIFOLevelReg   = 0x0A
    WaterLevelReg  = 0x0B
    ControlReg     = 0x0C
    BitFramingReg  = 0x0D
    CollReg        = 0x0E
    Reserved01     = 0x0F

    Reserved10     = 0x10
    ModeReg        = 0x11
    TxModeReg      = 0x12
    RxModeReg      = 0x13
    TxControlReg   = 0x14
    TxAutoReg      = 0x15
    TxSelReg       = 0x16
    RxSelReg       = 0x17
    RxThresholdReg = 0x18
    DemodReg       = 0x19
    Reserved11     = 0x1A
    Reserved12     = 0x1B
    MifareReg      = 0x1C
    Reserved13     = 0x1D
    Reserved14     = 0x1E
    SerialSpeedReg = 0x1F

    Reserved20        = 0x20
    CRCResultRegM     = 0x21
    CRCResultRegL     = 0x22
    Reserved21        = 0x23
    ModWidthReg       = 0x24
    Reserved22        = 0x25
    RFCfgReg          = 0x26
    GsNReg            = 0x27
    CWGsPReg          = 0x28
    ModGsPReg         = 0x29
    TModeReg          = 0x2A
    TPrescalerReg     = 0x2B
    TReloadRegH       = 0x2C
    TReloadRegL       = 0x2D
    TCounterValueRegH = 0x2E
    TCounterValueRegL = 0x2F

    Reserved30      = 0x30
    TestSel1Reg     = 0x31
    TestSel2Reg     = 0x32
    TestPinEnReg    = 0x33
    TestPinValueReg = 0x34
    TestBusReg      = 0x35
    AutoTestReg     = 0x36
    VersionReg      = 0x37
    AnalogTestReg   = 0x38
    TestDAC1Reg     = 0x39
    TestDAC2Reg     = 0x3A
    TestADCReg      = 0x3B
    Reserved31      = 0x3C
    Reserved32      = 0x3D
    Reserved33      = 0x3E
    Reserved34      = 0x3F

    serial_number_arr = []

    # constructor for MFRC522 class
    def __init__(self, bus=0, dev=0, spd=1000000):
        self.spi=spidev.SpiDev()
        self.spi.open(bus=bus,device=dev)
        self.spi.max_speed_hz=spd
        self.MFRC522Init()

    # reset MFRC522
    def Reset(self):
        self.Write(self.CommandReg, self.PCD_RESETPHASE)

    # write data over spi
    def Write(self, address, value):
        self.spi.writebytes(((address<<1)&BITS_0_AND_7_MASK,value))
    
    # read data via spi
    def Read(self, address):
        val = self.spi.xfer2((((address<<1)&BITS_0_AND_7_MASK) | SPI_READ_MODE_MASK,0)) # xfer2 to send all bytes at once
        return val[1]
    
    # masks a register
    # reg = reg | mask
    def SetBitMask(self, reg, mask):
        tmp = self.Read(reg)
        self.Write(reg, tmp | mask)

    # unmasks a register
    # reg = reg & ~mask
    def ClearBitMask(self, reg, mask):
        tmp = self.Read(reg)
        self.Write(reg, tmp & (~mask))
    
    # turns on RF antennas tx1 and tx2
    def EnableAntenna(self):
        tmp = self.Read(self.TxControlReg)
        if(~(tmp & ANTENNAE_MASK)):
            self.SetBitMask(self.TxControlReg, ANTENNAE_MASK)
    
    # turns off RF antennas tx1 and tx2
    def DisableAntenna(self):
        self.ClearBitMask(self.TxControlReg,ANTENNAE_MASK)


    # write to card from MFRC522
    # waits for a response
    def MFRC522WriteCard(self, command, data):
        backData = []
        backLen = 0
        status = self.MI_ERR
        irqEn = 0x00
        waitIrq = 0x00
        lastBits = None
        n = 0
        i = 0

        if command == self.PCD_AUTHENT:
            irqEn = 0x12
            waitIrq = 0x10
        elif command == self.PCD_TRANSCEIVE:
            irqEn = 0x77
            waitIrq = 0x30
        
        self.Write(self.CommIEnReg, irqEn | SPI_READ_MODE_MASK)
        self.ClearBitMask(self.CommIrqReg, SPI_READ_MODE_MASK)
        self.SetBitMask(self.FIFOLevelReg, SPI_READ_MODE_MASK)

        self.Write(self.CommandReg, self.PCD_IDLE)

        for byte in data:
            self.Write(self.FIFODataReg, byte)
        
        self.Write(self.CommandReg, command)

        if command == self.PCD_TRANSCEIVE:
            self.SetBitMask(self.BitFramingReg, SPI_READ_MODE_MASK)
        
        i = 2000
        while i > 0:
            n = self.Read(self.CommIrqReg)
            if (n & 0x01) or (n & waitIrq):
                # interrupt
                break
            i -= 1
        
        self.ClearBitMask(self.BitFramingReg, SPI_READ_MODE_MASK)

        if i != 0:
            # if no errors
            if (self.Read(self.ErrorReg) & 0x1B) == 0x00:
                status = self.MI_OK
        
            if n & irqEn & 0x01:
                status = self.MI_NOTAGERR

        if command == self.PCD_TRANSCEIVE:
            n = self.Read(self.FIFOLevelReg)
            lastBits = self.Read(self.ControlReg) & 0x07
            if lastBits != 0:
                backLen = (n - 1) * 8 + lastBits
            else:
                backLen = n * 8

            n = max(1, min(n, self.MAX_LEN))

            backData.extend(self.Read(self.FIFODataReg) for _ in range(n))

        else:
            status = self.MI_ERR

        return (status,backData,backLen)

    def MFRC522Request(self, reqMode):
        status = None
        backBits = None
        TagType = []

        self.Write(self.BitFramingReg, 0x07)

        TagType.append(reqMode)
        (status, backData, backBits) = self.MFRC522WriteCard(self.PCD_TRANSCEIVE, TagType)

        if ((status != self.MI_OK) | (backBits != 0x10)):
            status = self.MI_ERR

        return (status, backBits)

    # handle if multiple RFID tags are detected.
    # processes them sequentially
    def MFRC522AntiCollisions(self, anticolN):
        backData = []
        serNumCheck = 0

        serNum = []
        self.Write(self.BitFramingReg, 0x00)

        serNum.append(anticolN)
        serNum.append(0x20)

        (status, backData, backBits) = self.MFRC522WriteCard(self.PCD_TRANSCEIVE, serNum)

        if (status == self.MI_OK):
            if len(backData) == 5:
                serNumCheck = 0
                for byte in backData[:4]:
                    serNumCheck ^= byte
                if (serNumCheck != backData[4]):
                    status = self.MI_ERR
            else:
                status = self.MI_ERR

        return (status, backData)

    # anti collision algorithms
    def MFRC522AntiCollide1(self):
        return self.MFRC522AntiCollisions(self.PICC_ANTICOLL1)
    def MFRC522AntiCollide2(self):
        return self.MFRC522AntiCollisions(self.PICC_ANTICOLL2)
    def MFRC522AntiCollide3(self):
        return self.MFRC522AntiCollisions(self.PICC_ANTICOLL3)

    # cyclic redundancy check
    def CalculateCRC(self, pIn):
        pOut = []

        self.ClearBitMask(self.DivIrqReg, 0x04)
        self.SetBitMask(self.FIFOLevelReg, 0x80)

        for byte in pIn:
            self.Write(self.FIFODataReg, byte)
        
        self.Write(self.CommandReg, self.PCD_CALCCRC)

        i = 0xFF
        while True:
            n = self.Read(self.DivIrqReg)
            i -= 1
            if not ((i != 0) and not (n&0x04)):
                break
        
        pOut.extend([self.Read(self.CRCResultRegL), self.Read(self.CRCResultRegM)])

        return pOut
    
    # chooses a tag from a detected collision
    def MFRC522SelectTagFromCollision(self, serNum, anticolN):
        backData = []
        buf = []
        buf.append(anticolN)
        buf.append(0x70)

        buf.extend(serNum[:5])

        pOut = self.CalculateCRC(buf)
        buf.append(pOut[0])
        buf.append(pOut[1])
        (status, backData, backLen) = self.MFRC522WriteCard(self.PCD_TRANSCEIVE, buf)
        if (status == self.MI_OK) and (backLen == 0x18):
            return  1
        else:
            return 0

    # anti collision algorithms
    def MFRC522SelectTagAlg1(self, serNum):
        return self.MFRC522SelectTagFromCollision(serNum, self.PICC_ANTICOLL1)
    def MFRC522selectTagAlg2(self, serNum):
        return self.MFRC522SelectTagFromCollision(serNum, self.PICC_ANTICOLL2)
    def MFRC522SelectTagAlg3(self, serNum):
        return self.MFRC522SelectTagFromCollision(serNum, self.PICC_ANTICOLL3)
    
    
    def MFRC522Authenticate(self, authMode, blockAddr, sectorkey, serNum):
        buf = []

        # auth mode = first byte
        buf.append(authMode)
        # trail block = second byte
        buf.append(blockAddr)

        buf.extend(sectorkey)
        buf.extend(serNum[:4])

        # authenticate with card
        (status, backData, backLen) = self.MFRC522WriteCard(self.PCD_AUTHENT, buf)

        return status

    # stop crypto :)
    def MFRC522StopCryptoOpeartions(self):
        self.ClearBitMask(self.Status2Reg, 0x08)

    # read from RFID tag
    def MFRC522ReadTag(self, blockAddr):
        recvData = []
        recvData.append(self.PICC_READ)
        recvData.append(blockAddr)

        pOut = self.CalculateCRC(recvData)

        recvData.append(pOut[0])
        recvData.append(pOut[1])

        (status, backData, backLen) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, recvData)

        if not (status == self.MI_OK):
            print("Error while reading!")
        
        # i'm pretty certain this does absolutely nothing so i'm commenting it out for fear of being wrong and causing catastrophic suffering later
        #i = 0
        
        if len(backData) == 16:
            print("Sector "+str(blockAddr)+" "+str(backData))

    # write to RFID tag
    def MFRC522WriteTag(self, blockAddr, writeData):
        buff = []
        buff.extend([self.PICC_WRITE, blockAddr])

        crc = self.CalculateCRC(buff)

        buff.extend([crc[0], crc[1]])
        
        (status, backData, backLen) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, buff)
        
        if not(status == self.MI_OK) or not(backLen == 4) or not((backData[0] & 0x0F) == 0x0A):
            status = self.MI_ERR
        
        print("%s backdata &0x0F == 0x0A %s" % (backLen, backData[0]&0x0F))

        if status == self.MI_OK:
            buf = writeData[:16]
            crc = self.CalculateCRC(buf)
            buf.extend([crc[0], crc[1]])

            (status, backData, backLen) = self.MFRC522WriteCard(self.PCD_TRANSCEIVE,buf)

            if not(status == self.MI_OK) or not(backLen == 4) or not((backData[0] & 0x0F) == 0x0A):
                print("Error while writing")
            if status == self.MI_OK:
                print("Data written")

    # authenticates and dumps all data from blocks 0 - 63 from the 1k Classic MIFARE card
    def MFRC522DumpClassic1K(self, key, uid):
        for i in range(64):
            status = self.MFRC522Authenticate(self.PICC_AUTHENT1A, i, key, uid)
            if status == self.MI_OK:
                self.MFRC522ReadTag(i)
            else:
                print("Authentication error")
    
    # basic initialization stuffs separate from the constructor __init__ but is called within
    def MFRC522Init(self):
        self.Reset()
        self.Write(self.TModeReg, 0x8D)
        self.Write(self.TPrescalerReg, 0x3E)
        self.Write(self.TReloadRegL, 30)
        self.Write(self.TReloadRegH, 0)
        self.Write(self.TxAutoReg, 0x40)
        self.Write(self.ModeReg, 0x3D)
        self.EnableAntenna()
    
    # select a tag by its UID
    def MFRC522_SelectTagSN(self):
        valid_uid=[]
        (status,uid)= self.MFRC522AntiCollide1()

        if status != self.MI_OK:
            return  (self.MI_ERR,[])

        if self.MFRC522SelectTagAlg1(uid) == 0:
            return (self.MI_ERR,[])

        # check if first byte is 0x88 which indicates a different type of card
        if uid[0] == 0x88 :
            valid_uid.extend(uid[1:4])
            (status,uid) = self.MFRC522AntiCollide2()
            if status != self.MI_OK:
                return (self.MI_ERR,[])
            rtn =  self.MFRC522selectTagAlg2(uid)
            if rtn == 0:
                return (self.MI_ERR,[])
            # check again if first byte is 0x88
            if uid[0] == 0x88 :
                valid_uid.extend(uid[1:4])
            (status , uid) = self.MFRC522AntiCollide3()
            if status != self.MI_OK:
                return (self.MI_ERR,[])
            if self.MFRC522selectTagAlg3(uid) == 0:
                return (self.MI_ERR,[])
        valid_uid.extend(uid[0:4])

        return (self.MI_OK,valid_uid)

# --------------------------------------------------------------------------------------------------------------------

import signal
import time

continue_reading = True


def uidToString(uid):
    return ''.join(format(i, '02X') for i in reversed(uid))

def end_read(signal, frame):
    global continue_reading
    print("\nCtrl+C captured, ending read.")
    continue_reading = False

signal.signal(signal.SIGINT, end_read)
MIFAREReader = mfrc522()

def scan_rfid(mode="once", time_limit=10, match_uid=None):
    """
    Scanning Modes:
    - "once": Scan only once and return
    - "time": Scan repeatedly until `time_limit` seconds have elapsed
    - "match_or_time": Scan until a match is found OR `time_limit` seconds have elapsed
    - "match": Scan until a match is found, ignoring time
    - "first_match": Scan until any UID is found, then exit
    - "first_match_or_time": Scan until any UID is found OR `time_limit` seconds have elapsed
    - "forever": Scan forever (must manually interrupt program to stop)
    """
    start_time = time.time()
    global continue_reading
    continue_reading = True
    uid_str = None
    while continue_reading:
        if mode == "once":
            continue_reading = False  # Exit after one scan
        
        if mode in ["time", "match_or_time", "first_match_or_time"] and (time.time() - start_time) > time_limit:
            print("Time limit reached.")
            break
        
        status, TagType = MIFAREReader.MFRC522Request(MIFAREReader.PICC_REQIDL)
        if status == MIFAREReader.MI_OK:
            #print("Card detected")
            status, uid = MIFAREReader.MFRC522_SelectTagSN()
            if status == MIFAREReader.MI_OK:
                uid_str = uidToString(uid)
                print("Card read UID:", uid_str)
                
                if mode in ["first_match", "first_match_or_time"]:
                    return uid_str
                    #break
                
                if match_uid and uid_str == match_uid:
                    print("Match found!")
                    return uid_str
                    #break
                
                if mode == "once":
                    return uid_str
        
        

# Example usages:
# scan_rfid(mode="once")  # Scan only once
# scan_rfid(mode="time", time_limit=10)  # Scan until 10 seconds pass
# scan_rfid(mode="match_or_time", time_limit=10, match_uid="12345678")  # Scan until match or time runs out
# scan_rfid(mode="match", match_uid="12345678")  # Scan indefinitely until a match is found
# scan_rfid(mode="first_match")  # Scan until any UID is found
# scan_rfid(mode="first_match_or_time", time_limit=10)  # Scan until any UID is found or time runs out
# scan_rfid(mode="forever")  # Scan forever (must manually interrupt program to stop)