/**
 * @file
 * @brief 	VSN drivers configuration settings
 *
 * This header file contains driver configuration defines and function
 * prototypes for VSN drivers library.
 *
 * @author 	Marko Mihelin
 * @date 	05.07.2011
 *
 * copyright (c) SensorLab, Jozef Stefan Institute
 */

#ifndef VSNDRIVERSCONF_H_
#define VSNDRIVERSCONF_H_

#define STDOUT_USART USART_VCP
#define STDIN_USART USART_VCP

/* !YOU SHOULD NOT CHANGE THIS! Indicator led functions and power management rely on this settings */
/* Set SysTick interrupt period = 1 second / SYS_TICK_DIV */
#define SYS_TICK_DIV	1000    /* SysTick interrupt set to millisecond */

/* ------------------------------ Driver configuration ------------------------------ */
/* ------------------------------ FRAM driver configuration ------------------------- */
/* Uncomment ONE of the following three lines to select the FRAM driver mode,
 * if none is defined the driver defaults to DMA mode */
//#define NVRAM_DRIVER_MODE_POLLING
//#define NVRAM_DRIVER_MODE_INTERRUPT
#define NVRAM_DRIVER_MODE_DMA

/* ------------------------------ SD driver configuration --------------------------- */
/* Uncomment ONE of the following three lines to select the mode
 * in which the SD driver should be working, if none is defined
 * the driver defaults to DMA mode */
//#define SD_POLLING_MODE
//#define SD_INTERRUPT_MODE
#define SD_DMA_MODE
/* ------------------------------ SPI NEW driver configuration --------------------------- */
/* Uncomment ONE of the following three lines to select the mode
 * in which the SPI driver should be working, if none is defined
 * the driver defaults to DMA mode */
#define SPI1_NEW_DRIVER_MODE_POLLING
//#define SPI1_NEW_DRIVER_MODE_INTERRUPT
//#define SPI1_NEW_DRIVER_MODE_DMA

#define SPI2_NEW_DRIVER_MODE_POLLING
//#define SPI2_NEW_DRIVER_MODE_INTERRUPT
//#define SPI2_NEW_DRIVER_MODE_DMA

#define SPI3_NEW_DRIVER_MODE_POLLING
//#define SPI3_NEW_DRIVER_MODE_INTERRUPT
//#define SPI3_NEW_DRIVER_MODE_DMA
/* ------------------------------ USART driver configuration ------------------------ */
/* Uncomment ONE of the following lines for each USART to select
 * the mode in which the USART driver should be working, if none is defined
 * the driver defaults to interrupt mode */
#define USART1_DMA_MODE
//#define USART1_INTERRUPT_MODE
//#define USART2_DMA_MODE
#define USART2_INTERRUPT_MODE
//#define USART3_DMA_MODE
#define USART3_INTERRUPT_MODE
//#define UART4_DMA_MODE
#define UART4_INTERRUPT_MODE

/* Set the desired USART buffer sizes, if nothing is defined here
 * buffer size defaults to 128 bytes */
/* RX buffer size for USARTs, USARTx_RX_BUFFER_LEN - 1 chars can be stored */
#define USART1_RX_BUFFER_LEN  128
#define USART2_RX_BUFFER_LEN  128
#define USART3_RX_BUFFER_LEN  128
#define UART4_RX_BUFFER_LEN   128
/* TX buffer size for USARTs, USARTx_TX_BUFFER_LEN - 1 chars can be stored */
#define USART1_TX_BUFFER_LEN  128
#define USART2_TX_BUFFER_LEN  128
#define USART3_TX_BUFFER_LEN  128
#define UART4_TX_BUFFER_LEN   128

/* Function prototypes */
void vsnDriversConf_nvic(void);


/* ------------------- CC 1101 / 2500 driver configuration ----------------- */

/**
 * Physical location where the radio chip is connected.
 * Only 1 value has to be set to 1 from these:
 */
#define VSNCCRADIO_868 1

#define VSNCC1101_DEBUG 0 /* comment out this line for fewer messages */

#define VSNCCRADIO_DEBUG 0 /* comment out this line for fewer messages */

#define CC_RADIO_ON_RADIO_CONNECTOR 0
#define CC_RADIO_ON_EXPANSION_CONNECTOR 1

#endif /* VSNDRIVERSCONF_H_ */
