// Sync word qualifier mode = 30/32 sync word bits detected 
// CRC autoflush = false 
// Channel spacing = 99.906921 
// Data format = Normal mode 
// Data rate = 399.628 
// RX filter BW = 843.750000 
// Preamble count = 8 
// Whitening = true
// Address config = No address check 
// Carrier frequency = 2399.999908 
// Device address = 0 
// TX power = 0 
// Manchester enable = false 
// CRC enable = true 
// Phase transition time = 0 
// Packet length mode = Variable packet length mode. Packet length configured by the first byte after sync word 
// Packet length = 255 
// Modulation format = MSK 
// Base frequency = 2399.999908 
// Modulated = true 
// Channel number = 0 
const uint8_t init_seq[] = {
	CC1100_IOCFG2,         0x29,     // GDO2Output Pin Configuration 
	CC1100_IOCFG1,         0x2E,     // GDO1Output Pin Configuration 
	CC1100_IOCFG0,         0x06,     // GDO0Output Pin Configuration 
	CC1100_FIFOTHR,        0x07,     // RX FIFO and TX FIFO Thresholds
	CC1100_SYNC1,          0xD3,     // Sync Word, High Byte 
	CC1100_SYNC0,          0x91,     // Sync Word, Low Byte 
	CC1100_PKTLEN,         0xFF,     // Packet Length 
	CC1100_PKTCTRL1,       0x04,     // Packet Automation Control
	CC1100_PKTCTRL0,       0x45,     // Packet Automation Control
	CC1100_ADDR,           0x00,     // Device Address 
	CC1100_CHANNR,         0x00,     // Channel Number 
	CC1100_FSCTRL1,        0x0C,     // Frequency Synthesizer Control 
	CC1100_FSCTRL0,        0x00,     // Frequency Synthesizer Control 
	CC1100_FREQ2,          0x58,     // Frequency Control Word, High Byte 
	CC1100_FREQ1,          0xE3,     // Frequency Control Word, Middle Byte 
	CC1100_FREQ0,          0x8E,     // Frequency Control Word, Low Byte 
	CC1100_MDMCFG4,        0x0D,     // Modem Configuration 
	CC1100_MDMCFG3,        0xE5,     // Modem Configuration 
	CC1100_MDMCFG2,        0x73,     // Modem Configuration
	CC1100_MDMCFG1,        0x41,     // Modem Configuration
	CC1100_MDMCFG0,        0xE5,     // Modem Configuration 
	CC1100_DEVIATN,        0x00,     // Modem Deviation Setting 
	CC1100_MCSM2,          0x07,     // Main Radio Control State Machine Configuration 
	CC1100_MCSM1,          0x30,     // Main Radio Control State Machine Configuration
	CC1100_MCSM0,          0x18,     // Main Radio Control State Machine Configuration 
	CC1100_FOCCFG,         0x1D,     // Frequency Offset Compensation Configuration
	CC1100_BSCFG,          0x1C,     // Bit Synchronization Configuration
	CC1100_AGCCTRL2,       0xC7,     // AGC Control
	CC1100_AGCCTRL1,       0x40,     // AGC Control
	CC1100_AGCCTRL0,       0xB0,     // AGC Control
	CC1100_WOREVT1,        0x87,     // High Byte Event0 Timeout 
	CC1100_WOREVT0,        0x6B,     // Low Byte Event0 Timeout 
	CC1100_WORCTRL,        0xF8,     // Wake On Radio Control
	CC1100_FREND1,         0xB6,     // Front End RX Configuration 
	CC1100_FREND0,         0x10,     // Front End TX configuration 
	CC1100_FSCAL3,         0xEA,     // Frequency Synthesizer Calibration 
	CC1100_FSCAL2,         0x0A,     // Frequency Synthesizer Calibration 
	CC1100_FSCAL1,         0x00,     // Frequency Synthesizer Calibration 
	CC1100_FSCAL0,         0x19,     // Frequency Synthesizer Calibration 
	CC1100_RCCTRL1,        0x41,     // RC Oscillator Configuration 
	CC1100_RCCTRL0,        0x00,     // RC Oscillator Configuration 
	CC1100_FSTEST,         0x59,     // Frequency Synthesizer Calibration Control 
	CC1100_PTEST,          0x7F,     // Production Test 
	CC1100_AGCTEST,        0x3F,     // AGC Test 
	CC1100_TEST2,          0x88,     // Various Test Settings 
	CC1100_TEST1,          0x31,     // Various Test Settings 
	CC1100_TEST0,          0x0B,     // Various Test Settings 
	CC1100_PARTNUM,        0x80,     // Chip ID 
	CC1100_VERSION,        0x03,     // Chip ID 
	CC1100_FREQEST,        0x00,     // Frequency Offset Estimate from Demodulator 
	CC1100_LQI,            0x00,     // Demodulator Estimate for Link Quality 
	CC1100_RSSI,           0x00,     // Received Signal Strength Indication 
	CC1100_MARCSTATE,      0x00,     // Main Radio Control State Machine State 
	CC1100_WORTIME1,       0x00,     // High Byte of WOR Time 
	CC1100_WORTIME0,       0x00,     // Low Byte of WOR Time 
	CC1100_PKTSTATUS,      0x00,     // Current GDOxStatus and Packet Status 
	CC1100_VCO_VC_DAC,     0x00,     // Current Setting from PLL Calibration Module 
	CC1100_TXBYTES,        0x00,     // Underflow and Number of Bytes 
	CC1100_RXBYTES,        0x00,     // Underflow and Number of Bytes 
	CC1100_RCCTRL1_STATUS, 0x00,     // Last RC Oscillator Calibration Result 
	CC1100_RCCTRL0_STATUS, 0x00,     // Last RC Oscillator Calibration Result 
	0xFF, 0x0FF
};
