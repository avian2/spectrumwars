/**
 * @file
 * @brief Firmware for SpectrumWars game
 * @author Tomaz Solc
 *
 * copyright (c) SensorLab, Jozef Stefan Institute
 */
#include <assert.h>
#include <stdio.h>
#include <string.h>

#include "vsn.h"
#include "vsnusart.h"
#include "vsnsetup.h"
#include "vsnpm.h"
#include "vsncc1101.h"
#include "vsnccradio.h"

int received_flag;

static int cc2500_patable[] = {
	0xfe,	//     0 dBm
	0xbb,	//    -2
	0xa9,	//    -4
	0x7f,	//    -6
	0x6e,	//    -8
	0x97,	//   -10
	0xc6,	//   -12
	0x8d,	//   -14
	0x55,	//   -16
	0x93,	//   -18
	0x46,	//   -20
	0x81,	//   -22
	0x84,	//   -24
	0xc0,	//   -26
	0x44,	//   -28
	0x50,	//   -30
	0x00	// < -55
};

static int cc2500_patable_len = sizeof(cc2500_patable)/sizeof(*cc2500_patable);

/* Main function prototypes */
void received();

static void ok()
{
	printf("O\n");
}

static void error(const char *msg)
{
	printf("E %s\n", msg);
}

static void cmd_set_addr(int addr)
{
	if(addr < 0 || addr > 255) {
		error("invalid address");
		return;
	}

	vsnCC1101_setMode(IDLE);

	vsnCC_write(CC1100_ADDR, addr);

	vsnCC1101_setMode(RX);
	ok();
}

static void cmd_transmit(int addr, char* data)
{
	char bindata[255];
	int binlen = 0;

	assert(strlen(data) <= 508);

	if(strlen(data) % 2 != 0) {
		error("length of transmit data not integer number of bytes");
		return;
	}

	if(addr < 0 || addr > 255) {
		error("invalid address");
		return;
	}

	bindata[0] = addr;
	binlen++;

	int i;
	for(i = 0; data[i] != 0; i += 2) {
		int c;
		if(sscanf(&data[i], "%2x", &c) != 1) {
			error("transmit data not valid hex");
			return;
		}
		bindata[binlen] = c;
		binlen += 1;
	}

	int resp = vsnCC1101_send(bindata, binlen);
	if(resp < 0) {
		error("error sending data");
	} else if(resp != binlen) {
		error("not all data bytes sent");
	} else {
		ok();
	}
}

static void cmd_config(int chan, int bw, int power)
{
	if(chan < 0 || chan > 255) {
		error("invalid channel");
		return;
	}

	if(bw < 0 || bw > 3) {
		error("invalid bandwidth");
		return;
	}

	if(power < 0 || power >= cc2500_patable_len) {
		error("invalid power");
		return;
	}

	vsnCC1101_setMode(IDLE);

	switch(bw) {
		case 0:
			// 50 kbps
			vsnCC_write(CC1100_MDMCFG4, 0xCA);
			vsnCC_write(CC1100_FSCAL3, 0xA9);
			vsnCC_write(CC1100_FSCAL0, 0x11);
			break;
		case 1:
			// 100 kbps
			vsnCC_write(CC1100_MDMCFG4, 0x8B);
			vsnCC_write(CC1100_FSCAL3, 0xA9);
			vsnCC_write(CC1100_FSCAL0, 0x11);
			break;
		case 2:
			// 200 kbps
			vsnCC_write(CC1100_MDMCFG4, 0x4C);
			vsnCC_write(CC1100_FSCAL3, 0xEA);
			vsnCC_write(CC1100_FSCAL0, 0x11);
			break;
		case 3:
			// 400 kbps
			vsnCC_write(CC1100_MDMCFG4, 0x0D);
			vsnCC_write(CC1100_FSCAL3, 0xEA);
			vsnCC_write(CC1100_FSCAL0, 0x19);
			break;
	}

	vsnCC_write(CC1100_CHANNR, chan);
	vsnCC_write(CC1100_PATABLE, cc2500_patable[power]);

	vsnCC1101_setMode(RX);

	ok();
}

static void recv()
{
	const int binlen_max = 256;
	char bindata[binlen_max];
	int binlen = vsnCC1101_receive(bindata, binlen_max);

	assert(binlen >= 2);

	printf("R ");

	int i;
	for(i = 1; i < binlen-2; i++) {
		printf("%02x", bindata[i]);
	}
	printf("\n");
}

#define CMD_BUFF_SIZE	1024
static char cmd_buff[CMD_BUFF_SIZE];
static int cmd_buff_len = 0;

static void cmd_buff_dispatch()
{
	int addr;
	int chan, bw, power;
	char data[511];

	if(sscanf(cmd_buff, "a %x", &addr) == 1) {
		cmd_set_addr(addr);
	} else if(sscanf(cmd_buff, "t %x %508s", &addr, data) == 2) {
		cmd_transmit(addr, data);
	} else if(sscanf(cmd_buff, "c %x %x %x", &chan, &bw, &power) == 3) {
		cmd_config(chan, bw, power);
	} else {
		error("unknown command");
	}
}

static void cmd_buff_input(char c)
{
	if(c == '\n' || cmd_buff_len >= CMD_BUFF_SIZE - 1) {
		cmd_buff[cmd_buff_len] = 0;
		cmd_buff_len = 0;
		cmd_buff_dispatch();
	} else {
		cmd_buff[cmd_buff_len] = c;
		cmd_buff_len++;
	}
}

#include "rfstudio/cc2500_50kbps.h"

static void radio_setup()
{
	vsnCC1101_init();
	vsnCC1101_setReceiveInterrupt(received);
	vsnCC1101_setMode(IDLE);

	int n;
	for(n = 0; init_seq[n] != 0xff; n += 2) {
		uint8_t reg = init_seq[n];
		uint8_t value = init_seq[n+1];

		vsnCC_write(reg, value);
	}

	vsnCC1101_setMode(RX);
}

/* Start of main */
int main(void)
{
	/* Start of Main code ----------------------------------------------- */
	/* Reset Clock configuration */
	SystemInit();
	/* Turn on power manager */
	vsnPM_init();
	/* Set SysClock frequency */
	vsnSetup_intClk(SNC_CLOCK_64MHZ);
	/* Initialize SNC */
	vsnSetup_initSnc();
	/* Configure debug port at USART1, 115200 kbaud, 8 data bit, no parity, one stop bit, no flow control */
	vsnUSART_init(USART_VCP, NULL);

	/* Make stdout unbuffered, just in case */
	setbuf(stdout, NULL);

	printf("boot\n");

	/* Get ADC one bit value in volts, call as last init function */
	vsnPM_mesureAdcBitVolt();

	/* Init functions for sensors, actuators,... */
	radio_setup();

	received_flag = 0;

	while(1)
	{
		char c;
		if(vsnUSART_read(USART_VCP, &c, 1)) {
			cmd_buff_input(c);
		}
		if(received_flag) {
			recv();
			received_flag = 0;
			vsnCC1101_setMode(RX);
		}
	}
}
/* End of main */

void received(){
    received_flag = 1;
}
