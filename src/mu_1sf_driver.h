/**
 ******************************************************************************
 * @file    mu_1sf_driver.h
 * @author  iC-Haus GmbH
 * @version 1.1.0
 * @note Designed according to iC-MU datasheet release F2 for chip revision Y2/Y2H.
 * @note Designed according to iC-MU150 datasheet release D2 for chip revision 1.
 * @note Designed according to iC-MU200 datasheet release B2 for chip revision 0.
 ******************************************************************************
 * @attention
 *
 *	Software and its documentation is provided by iC-Haus GmbH or contributors "AS IS" and is
 *	subject to the ZVEI General Conditions for the Supply of Products and Services with iC-Haus
 *	amendments and the ZVEI Software clause with iC-Haus amendments (http://www.ichaus.de/EULA).
 *
 ******************************************************************************
 */


#ifndef MU_1SF_DRIVER_H
#define MU_1SF_DRIVER_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>

/**
 * @defgroup Wrapper_Functions
 * @brief Functions declared as `extern` have to be defined by the user according to the specific hardware used.
 *
 * @note The definition of those functions is mandatory to use this driver.
 * @{
 */
/**
 * @brief This function is a wrapper to be defined with the MCU-specific SPI-transmit-receive-function.
 *
 * @param data_tx is a pointer to the data buffer that is transmitted.
 * @param data_rx is a pointer to the buffer the received data is written to.
 * @param datasize is the length of all bytes transmitted.
 * @retval None
 */
extern void mu_spi_transfer(uint8_t *data_tx, uint8_t *data_rx, uint16_t datasize);

/**
 * @brief This function is a wrapper to be defined with the MCU-specific wait function.
 *
 * @param time_us is the time to wait in microseconds.
 * @retval None
 */
extern void mu_wait_us(uint16_t time_us);
/**
 * @}
 */

/**
 * @defgroup CMD_MU
 * @brief Commands that can be sent to iC-MU CMD register at address 0x75.
 * @{
 */
typedef enum {
	CMD_MU_WRITE_ALL = 0x01,
	CMD_MU_WRITE_OFF = 0x02,
	CMD_MU_ABS_RESET = 0x03,
	CMD_MU_NON_VER = 0x04,
	CMD_MU_MT_RESET = 0x05,
	CMD_MU_MT_VER = 0x06,
	CMD_MU_SOFT_RESET = 0x07,
	CMD_MU_SOFT_PRES = 0x08,
	CMD_MU_SOFT_E2P_PRES = 0x09,
	CMD_MU_I2C_COM = 0x0A,
	CMD_MU_EVENT_COUNT = 0x0B,
	CMD_MU_SWITCH = 0x0C,
	CMD_MU_CRC_VER = 0x0D,
	CMD_MU_CRC_CALC = 0x0E,
	CMD_MU_SET_MTC = 0x0F,
	CMD_MU_RES_MTC = 0x10,

	CMD_MU_MODEA_SPI = 0x12,		// exclusively supported by iC-MU150 and iC-MU200
	CMD_MU_ROT_POS = 0x13,			// exclusively supported by iC-MU150 and iC-MU200
	CMD_MU_ROT_POS_E2P = 0x14,		// exclusively supported by iC-MU150 and iC-MU200
} CMD_MU;
/**
 * @}
 */

/**
 * @defgroup MU_Parameters
 * @{
 */
/**
 * @addtogroup MU_Parameters_Struct
 * @brief Structure implemented to represent an iC-MU parameter.
 * @{
 */
struct mu_param {
	uint8_t bank;
	uint8_t addr[6];
	uint8_t pos;
	uint8_t len;
};
/**
 * @}
 */

/**
 * @addtogroup MU_Parameters_List
 * @brief List of parameters according to iC-MU register map represented as @ref MU_Parameters_Struct.
 * @{
 */
extern const struct mu_param MU_GF_M;
extern const struct mu_param MU_GC_M;
extern const struct mu_param MU_GX_M;
extern const struct mu_param MU_VOSS_M;
extern const struct mu_param MU_VOSC_M;
extern const struct mu_param MU_PH_M;
extern const struct mu_param MU_CIBM;
extern const struct mu_param MU_ENAC;
extern const struct mu_param MU_GF_N;
extern const struct mu_param MU_GC_N;
extern const struct mu_param MU_GX_N;
extern const struct mu_param MU_VOSS_N;
extern const struct mu_param MU_VOSC_N;
extern const struct mu_param MU_PH_N;
extern const struct mu_param MU_MODEA;
extern const struct mu_param MU_MODEB;
extern const struct mu_param MU_CFGEW;
extern const struct mu_param MU_EMTD;
extern const struct mu_param MU_ACRM_RES;
extern const struct mu_param MU_NCHK_NON;
extern const struct mu_param MU_NCHK_CRC;
extern const struct mu_param MU_ACC_STAT;
extern const struct mu_param MU_FILT;
extern const struct mu_param MU_LIN;
extern const struct mu_param MU_ROT_MT;
extern const struct mu_param MU_ESSI_MT;
extern const struct mu_param MU_MPC;
extern const struct mu_param MU_SPO_MT;
extern const struct mu_param MU_MODE_MT;
extern const struct mu_param MU_SBL_MT;
extern const struct mu_param MU_CHK_MT;
extern const struct mu_param MU_GET_MT;
extern const struct mu_param MU_OUT_MSB;
extern const struct mu_param MU_OUT_ZERO;
extern const struct mu_param MU_OUT_LSB;
extern const struct mu_param MU_MODE_ST;
extern const struct mu_param MU_RSSI;
extern const struct mu_param MU_GSSI;
extern const struct mu_param MU_RESABZ;
extern const struct mu_param MU_FRQAB;
extern const struct mu_param MU_ENIF_AUTO;
extern const struct mu_param MU_SS_AB;
extern const struct mu_param MU_ROT_ALL;
extern const struct mu_param MU_INV_Z;
extern const struct mu_param MU_INV_B;
extern const struct mu_param MU_INV_A;
extern const struct mu_param MU_PP60UVW;
extern const struct mu_param MU_CHYS_AB;
extern const struct mu_param MU_LENZ;
extern const struct mu_param MU_PPUVW;
extern const struct mu_param MU_RPL;
extern const struct mu_param MU_TEST;
extern const struct mu_param MU_OFF_ABZ;
extern const struct mu_param MU_OFF_POS;
extern const struct mu_param MU_OFF_COM;
extern const struct mu_param MU_PA0_CONF;
extern const struct mu_param MU_AFGAIN_M;
extern const struct mu_param MU_ACGAIN_M;
extern const struct mu_param MU_AFGAIN_N;
extern const struct mu_param MU_ACGAIN_N;
extern const struct mu_param MU_BANKSEL;
extern const struct mu_param MU_EDSBANK;
extern const struct mu_param MU_PROFILE_ID;
extern const struct mu_param MU_SERIAL;
extern const struct mu_param MU_OFF_UVW;
extern const struct mu_param MU_PRES_POS;
extern const struct mu_param MU_SPO_BASE;
extern const struct mu_param MU_SPO_0;
extern const struct mu_param MU_SPO_1;
extern const struct mu_param MU_SPO_2;
extern const struct mu_param MU_SPO_3;
extern const struct mu_param MU_SPO_4;
extern const struct mu_param MU_SPO_5;
extern const struct mu_param MU_SPO_6;
extern const struct mu_param MU_SPO_7;
extern const struct mu_param MU_SPO_8;
extern const struct mu_param MU_SPO_9;
extern const struct mu_param MU_SPO_10;
extern const struct mu_param MU_SPO_11;
extern const struct mu_param MU_SPO_12;
extern const struct mu_param MU_SPO_13;
extern const struct mu_param MU_SPO_14;
extern const struct mu_param MU_RPL_RESET;
extern const struct mu_param MU_I2C_DEV_START;
extern const struct mu_param MU_I2C_RAM_START;
extern const struct mu_param MU_I2C_RAM_END;
extern const struct mu_param MU_I2C_DEVID;
extern const struct mu_param MU_I2C_RETRY;
extern const struct mu_param MU_EVENT_COUNT;
extern const struct mu_param MU_HARD_REV;
extern const struct mu_param MU_CMD_MU;
extern const struct mu_param MU_STATUS0;
extern const struct mu_param MU_STATUS1;
extern const struct mu_param MU_DEV_ID;
extern const struct mu_param MU_MFG_ID;

/**
 * @addtogroup MU_Parameters_SPI_RAM_Access_Exclusive
 * @brief Parameters exclusively available for SPI RAM access.
 * @{
 */
extern const struct mu_param MU_CRC16;
extern const struct mu_param MU_CRC8;
/**
 * @}
 */

/**
 * @addtogroup MU_Parameters_MU150_MU200_Exclusive
 * @brief Parameters exclusively available in iC-MU150 and iC-MU200.
 * @{
 */
extern const struct mu_param MU_PHR_M;
extern const struct mu_param MU_PHR_N;
extern const struct mu_param MU_NTOA;
extern const struct mu_param MU_ROT_POS;
/**
 * @}
 */

/**
 * @}
 */

/**
 * @}
 */

/**
 * @defgroup MU_Functions
 * @{
 */
/**
 * @addtogroup MU_Functions_Basic
 * @brief Functions according to iC-MU SPI opcodes.
 * @{
 */
void mu_activate(const uint8_t *active_vector, uint8_t vector_size);
void mu_sdad_transmission(uint8_t *data_rx, uint8_t datasize);
void mu_sdad_status(uint8_t *svalid_vector, uint8_t vector_size);
void mu_read_register(uint8_t addr);
void mu_write_register(uint8_t addr, uint8_t data_tx);
void mu_register_status_data(uint8_t *status_rx, uint8_t *data_rx);
/**
 * @}
 */

/**
 * @addtogroup MU_Functions_Advanced
 * @brief Functions going through a sequence of @ref MU_Functions_Basic with enhanced data handling.
 * @{
 */
void mu_write_command(CMD_MU command);
void mu_switch_bank(uint8_t bank);
uint64_t mu_read_param(const struct mu_param *param);
void mu_write_param(const struct mu_param *param, uint64_t param_val);
/**
 * @}
 */

/**
 * @}
 */

#ifdef __cplusplus
}
#endif

#endif /* MU_1SF_DRIVER_H */
