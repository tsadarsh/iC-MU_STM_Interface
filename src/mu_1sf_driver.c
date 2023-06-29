/**
 ******************************************************************************
 * @file    mu_1sf_driver.c
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

#include "mu_1sf_driver.h"

/* iC-MU opcodes */
enum MU_OPCODE {
	MU_OPCODE_ACTIVATE = 0xB0,
	MU_OPCODE_SDAD_TRANSMISSION = 0xA6,
	MU_OPCODE_SDAD_STATUS = 0xF5,
	MU_OPCODE_READ_REGISTER = 0x97,
	MU_OPCODE_WRITE_REGISTER = 0xD2,
	MU_OPCODE_REGISTER_STATUS_DATA = 0xAD,
};

/* iC-MU parameters */
const struct mu_param MU_GF_M = { .bank = 0x00, .addr = { 0x00 }, .pos = 5, .len = 6 };
const struct mu_param MU_GC_M = { .bank = 0x00, .addr = { 0x00 }, .pos = 7, .len = 2 };
const struct mu_param MU_GX_M =  { .bank = 0x00, .addr = { 0x01 }, .pos = 6, .len = 7 };
const struct mu_param MU_VOSS_M = { .bank = 0x00, .addr = { 0x02 }, .pos = 6, .len = 7 };
const struct mu_param MU_VOSC_M = { .bank = 0x00, .addr = { 0x03 }, .pos = 6, .len = 7 };
const struct mu_param MU_PH_M = { .bank = 0x00, .addr = { 0x04 }, .pos = 6, .len = 7 };
const struct mu_param MU_CIBM = { .bank = 0x00, .addr = { 0x05 }, .pos = 3, .len = 4 };
const struct mu_param MU_ENAC = { .bank = 0x00, .addr = { 0x05 }, .pos = 7, .len = 1 };
const struct mu_param MU_GF_N = { .bank = 0x00, .addr = { 0x06 }, .pos = 5, .len = 6 };
const struct mu_param MU_GC_N = { .bank = 0x00, .addr = { 0x06 }, .pos = 7, .len = 2 };
const struct mu_param MU_GX_N = { .bank = 0x00, .addr = { 0x07 }, .pos = 6, .len = 7 };
const struct mu_param MU_VOSS_N = { .bank = 0x00, .addr = { 0x08 }, .pos = 6, .len = 7 };
const struct mu_param MU_VOSC_N = { .bank = 0x00, .addr = { 0x09 }, .pos = 6, .len = 7 };
const struct mu_param MU_PH_N = { .bank = 0x00, .addr = { 0x0A }, .pos = 6, .len = 7 };
const struct mu_param MU_MODEA = { .bank = 0x00, .addr = { 0x0B }, .pos = 2, .len = 3 };
const struct mu_param MU_MODEB = { .bank = 0x00, .addr = { 0x0B }, .pos = 6, .len = 3 };
const struct mu_param MU_CFGEW = { .bank = 0x00, .addr = { 0x0C }, .pos = 7, .len = 8 };
const struct mu_param MU_EMTD = { .bank = 0x00, .addr = { 0x0D }, .pos = 2, .len = 3 };
const struct mu_param MU_ACRM_RES = { .bank = 0x00, .addr = { 0x0D }, .pos = 4, .len = 1 };
const struct mu_param MU_NCHK_NON = { .bank = 0x00, .addr = { 0x0D }, .pos = 5, .len = 1 };
const struct mu_param MU_NCHK_CRC = { .bank = 0x00, .addr = { 0x0D }, .pos = 6, .len = 1 };
const struct mu_param MU_ACC_STAT = { .bank = 0x00, .addr = { 0x0D }, .pos = 7, .len = 1 };
const struct mu_param MU_FILT = { .bank = 0x00, .addr = { 0x0E }, .pos = 2, .len = 3 };
const struct mu_param MU_LIN = { .bank = 0x00, .addr = { 0x0E }, .pos = 4, .len = 1 };
const struct mu_param MU_ROT_MT = { .bank = 0x00, .addr = { 0x0E }, .pos = 5, .len = 1 };
const struct mu_param MU_ESSI_MT = { .bank = 0x00, .addr = { 0x0E }, .pos = 7, .len = 2 };
const struct mu_param MU_MPC = { .bank = 0x00, .addr = { 0x0F }, .pos = 3, .len = 4 };
const struct mu_param MU_SPO_MT = { .bank = 0x00, .addr = { 0x0F }, .pos = 7, .len = 4 };
const struct mu_param MU_MODE_MT = { .bank = 0x00, .addr = { 0x10 }, .pos = 3, .len = 4 };
const struct mu_param MU_SBL_MT = { .bank = 0x00, .addr = { 0x10 }, .pos = 5, .len = 2 };
const struct mu_param MU_CHK_MT = { .bank = 0x00, .addr = { 0x10 }, .pos = 6, .len = 1 };
const struct mu_param MU_GET_MT = { .bank = 0x00, .addr = { 0x10 }, .pos = 7, .len = 1 };
const struct mu_param MU_OUT_MSB = { .bank = 0x00, .addr = { 0x11 }, .pos = 4, .len = 5 };
const struct mu_param MU_OUT_ZERO = { .bank = 0x00, .addr = { 0x11 }, .pos = 7, .len = 3 };
const struct mu_param MU_OUT_LSB = { .bank = 0x00, .addr = { 0x12 }, .pos = 3, .len = 4 };
const struct mu_param MU_MODE_ST = { .bank = 0x00, .addr = { 0x12 }, .pos = 5, .len = 2 };
const struct mu_param MU_RSSI = { .bank = 0x00, .addr = { 0x12 }, .pos = 6, .len = 1 };
const struct mu_param MU_GSSI = { .bank = 0x00, .addr = { 0x12 }, .pos = 7, .len = 1 };
const struct mu_param MU_RESABZ = { .bank = 0x00, .addr = { 0x14, 0x13 }, .pos = 7, .len = 16 };
const struct mu_param MU_FRQAB = { .bank = 0x00, .addr = { 0x15 }, .pos = 2, .len = 3 };
const struct mu_param MU_ENIF_AUTO = { .bank = 0x00, .addr = { 0x15 }, .pos = 3, .len = 1 };
const struct mu_param MU_SS_AB = { .bank = 0x00, .addr = { 0x15 }, .pos = 5, .len = 2 };
const struct mu_param MU_ROT_ALL = { .bank = 0x00, .addr = { 0x15 }, .pos = 7, .len = 1 };
const struct mu_param MU_INV_Z = { .bank = 0x00, .addr = { 0x16 }, .pos = 0, .len = 1 };
const struct mu_param MU_INV_B = { .bank = 0x00, .addr = { 0x16 }, .pos = 1, .len = 1 };
const struct mu_param MU_INV_A = { .bank = 0x00, .addr = { 0x16 }, .pos = 2, .len = 1 };
const struct mu_param MU_PP60UVW =  { .bank = 0x00,.addr = { 0x16 }, .pos = 3, .len = 1 };
const struct mu_param MU_CHYS_AB = { .bank = 0x00, .addr = { 0x16 }, .pos = 5, .len = 2 };
const struct mu_param MU_LENZ = { .bank = 0x00, .addr = { 0x16 }, .pos = 7, .len = 2 };
const struct mu_param MU_PPUVW = { .bank = 0x00, .addr = { 0x17 }, .pos = 5, .len = 6 };
const struct mu_param MU_RPL = { .bank = 0x00, .addr = { 0x17 }, .pos = 7, .len = 2 };
const struct mu_param MU_TEST = { .bank = 0x00,  .addr = { 0x18 }, .pos = 7, .len = 8 };
const struct mu_param MU_OFF_ABZ = { .bank = 0x00, .addr = { 0x4A, 0x49, 0x48, 0x1F, 0x1E }, .pos = 7, .len = 36 };
const struct mu_param MU_OFF_POS = { .bank = 0x00, .addr = { 0x22, 0x21, 0x20 }, .pos = 7, .len = 24 };
const struct mu_param MU_OFF_COM = { .bank = 0x00, .addr = { 0x24, 0x23 }, .pos= 7, .len = 12 };
const struct mu_param MU_PA0_CONF = { .bank = 0x00, .addr = { 0x25 }, .pos = 7, .len = 8 };
const struct mu_param MU_AFGAIN_M = { .bank = 0x00, .addr = { 0x2B }, .pos = 2, .len = 3 };
const struct mu_param MU_ACGAIN_M = { .bank = 0x00, .addr = { 0x2B }, .pos = 4, .len = 2 };
const struct mu_param MU_AFGAIN_N = { .bank = 0x00, .addr = { 0x2F }, .pos = 2, .len = 3 };
const struct mu_param MU_ACGAIN_N = { .bank = 0x00, .addr = { 0x2F }, .pos = 4, .len = 2 };
const struct mu_param MU_BANKSEL = { .addr = { 0x40 }, .pos = 4, .len = 5 };
const struct mu_param MU_EDSBANK = { .addr = { 0x41 }, .pos = 7, .len = 8 };
const struct mu_param MU_PROFILE_ID = { .addr = { 0x42, 0x43 }, .pos = 7, .len = 16 };
const struct mu_param MU_SERIAL = { .addr = { 0x44, 0x45, 0x46, 0x47 }, .pos = 7, .len = 32 };
const struct mu_param MU_OFF_UVW = { .addr = { 0x4C, 0x4B }, .pos = 7, .len = 12 };
const struct mu_param MU_PRES_POS = { .addr = { 0x51, 0x50, 0x4F, 0x4E, 0x4D }, .pos = 7, .len = 36 };
const struct mu_param MU_SPO_BASE = { .addr = { 0x52 }, .pos = 3, .len = 4 };
const struct mu_param MU_SPO_0 = { .addr = { 0x52 }, .pos = 7, .len = 4 };
const struct mu_param MU_SPO_1 = { .addr = { 0x53 }, .pos = 3, .len = 4 };
const struct mu_param MU_SPO_2 = { .addr = { 0x53 }, .pos = 7, .len = 4 };
const struct mu_param MU_SPO_3 = { .addr = { 0x54 }, .pos = 3, .len = 4 };
const struct mu_param MU_SPO_4 = { .addr = { 0x54 }, .pos = 7, .len = 4 };
const struct mu_param MU_SPO_5 = { .addr = { 0x55 }, .pos = 3, .len = 4 };
const struct mu_param MU_SPO_6 = { .addr = { 0x55 }, .pos = 7, .len = 4 };
const struct mu_param MU_SPO_7 = { .addr = { 0x56 }, .pos = 3, .len = 4 };
const struct mu_param MU_SPO_8 = { .addr = { 0x56 }, .pos = 7, .len = 4 };
const struct mu_param MU_SPO_9 = { .addr = { 0x57 }, .pos = 3, .len = 4 };
const struct mu_param MU_SPO_10 = { .addr = { 0x57 }, .pos = 7, .len = 4 };
const struct mu_param MU_SPO_11 = { .addr = { 0x58 }, .pos = 3, .len = 4 };
const struct mu_param MU_SPO_12 = { .addr = { 0x58 }, .pos = 7, .len = 4 };
const struct mu_param MU_SPO_13 = { .addr = { 0x59 }, .pos = 3, .len = 4 };
const struct mu_param MU_SPO_14 = { .addr = { 0x59 }, .pos = 7, .len = 4 };
const struct mu_param MU_RPL_RESET = { .addr = { 0x5A }, .pos = 7, .len = 8 };
const struct mu_param MU_I2C_DEV_START =  { .addr = { 0x5B }, .pos = 7, .len = 8 };
const struct mu_param MU_I2C_RAM_START =  { .addr = { 0x5C }, .pos = 7, .len = 8 };
const struct mu_param MU_I2C_RAM_END =  { .addr = { 0x5D }, .pos = 7, .len = 8 };
const struct mu_param MU_I2C_DEVID =  { .addr = { 0x5E }, .pos = 7, .len = 8 };
const struct mu_param MU_I2C_RETRY =  { .addr = { 0x5F }, .pos = 7, .len = 8 };
const struct mu_param MU_EVENT_COUNT =  { .addr = { 0x73 }, .pos = 7, .len = 8 };
const struct mu_param MU_HARD_REV = { .addr = { 0x74 }, .pos = 7, .len = 8 };
const struct mu_param MU_CMD_MU = { .addr = { 0x75 }, .pos = 7, .len = 8 };
const struct mu_param MU_STATUS0 = { .addr = { 0x76 }, .pos = 7, .len = 8 };
const struct mu_param MU_STATUS1 = { .addr = { 0x77 }, .pos = 7, .len = 8 };
const struct mu_param MU_DEV_ID = { .addr = { 0x78, 0x79, 0x7A, 0x7B, 0x7C, 0x7D }, .pos = 7, .len = 48 };
const struct mu_param MU_MFG_ID = { .addr = { 0x7E, 0x7F }, .pos = 7, .len = 16 };

/* SPI RAM access exclusive parameters */
const struct mu_param MU_CRC16 =  { .bank =0x00, .addr = { 0x81, 0x80 }, .pos = 7, .len = 16 };
const struct mu_param MU_CRC8 = { .addr = { 0x82 }, .pos = 7, .len = 8 };

/* iC-MU150/iC-MU200 exclusive parameters */
const struct mu_param MU_PHR_M = { .bank = 0x00, .addr = { 0x04 }, .pos = 7, .len = 1 };
const struct mu_param MU_PHR_N = { .bank = 0x00, .addr = { 0x0A }, .pos = 7, .len = 1 };
const struct mu_param MU_NTOA = { .bank = 0x00, .addr = { 0x0B }, .pos = 3, .len = 1 };
const struct mu_param MU_ROT_POS = { .bank = 0x00, .addr = { 0x1E }, .pos = 0, .len = 1 };

/* iC-MU defines */
#define MU_REGISTER_SIZE	8

/* local function declarations */
static uint8_t get_start_bit_number(uint8_t bit_pos, uint8_t bit_len);

/* globals */
static uint8_t buf_tx[0xFF + 1];
static uint8_t buf_rx[0xFF + 1];
static uint16_t bufsize;

/**
 * @brief This function can be used to switch the register and sensor data channels of the connected slaves on and off.
 *
 * @note After startup of iC-MU RACTIVE and PACTIVE are set to 1.
 *
 * @param active_vector is a pointer to a buffer containing the ractive/pactive vector to be transmitted.
 * @param vector_size is the length of the vector in byte.
 * @retval None
 */
void mu_activate(const uint8_t *active_vector, uint8_t vector_size) {
	bufsize = vector_size + 1;
	buf_tx[0] = MU_OPCODE_ACTIVATE;

	for (uint8_t i = 0; i < vector_size; ++i) {
		buf_tx[i + 1] = active_vector[i];
	}

	mu_spi_transfer(buf_tx, buf_rx, bufsize);
}

/**
 * @brief This function directly transmits SDAD data.
 *
 * @param data_rx is a pointer to a buffer the received SDAD data is written to.
 * @param datasize is the number of bytes transmitted.
 * @retval None
 */
void mu_sdad_transmission(uint8_t *data_rx, uint8_t datasize) {
	bufsize = datasize + 1;
	buf_tx[0] = MU_OPCODE_SDAD_TRANSMISSION;

	for (uint16_t i = 1; i < bufsize; i++) {
		buf_tx[i] = 0x00;
	}

	mu_spi_transfer(buf_tx, buf_rx, bufsize);

	for (uint8_t i = 0; i < datasize; i++) {
		data_rx[i] = buf_rx[i + 1];
	}
}

/**
 * @brief This function can be used to request sensor data.
 *
 * @param svalid_vector is a pointer to a buffer the received svalid vector is written to.
 * @param vector_size is the length of the vector in byte.
 * @retval None
 */
void mu_sdad_status(uint8_t *svalid_vector, uint8_t vector_size) {
	bufsize = vector_size + 1;
	buf_tx[0] = MU_OPCODE_SDAD_STATUS;

	for (uint8_t i = 1; i < bufsize; i++) {
		buf_tx[i] = 0x00;
	}

	mu_spi_transfer(buf_tx, buf_rx, bufsize);

	for (uint8_t i = 0; i < (bufsize - 1); i++) {
		svalid_vector[i] = buf_rx[i + 1];
	}
}

/**
 * @brief This function enables register data to be read out from the slave byte by byte.
 *
 * @param addr is the address of the register to be read.
 * @retval None
 */
void mu_read_register(uint8_t addr) {
	bufsize = 2;
	buf_tx[0] = MU_OPCODE_READ_REGISTER;
	buf_tx[1] = addr;

	mu_spi_transfer(buf_tx, buf_rx, bufsize);
}

/**
 * @brief This function enables data to be written to the slave byte by byte.
 *
 * @param addr is the address of the register to be written to.
 * @param data_tx is the byte written to the register.
 * @retval None
 */
void mu_write_register(uint8_t addr, uint8_t data_tx) {
	bufsize = 3;
	buf_tx[0] = MU_OPCODE_WRITE_REGISTER;
	buf_tx[1] = addr;
	buf_tx[2] = data_tx;

	mu_spi_transfer(buf_tx, buf_rx, bufsize);
}

/**
 * @brief This function can be used to request the status of the last register communication and/or the last data transmission.
 *
 * @note It can be used to poll until the validity of the DATA following the SPI-STATUS byte is signaled via SPI-STATUS.
 *
 * @param status_rx is a pointer the received status byte is written to.
 * @param data_rx is a pointer the received data byte is written to.
 * @retval None
 */
void mu_register_status_data(uint8_t *status_rx, uint8_t *data_rx) {
	bufsize = 3;
	buf_tx[0] = MU_OPCODE_REGISTER_STATUS_DATA;
	buf_tx[1] = 0x00;
	buf_tx[2] = 0x00;

	mu_spi_transfer(buf_tx, buf_rx, bufsize);

	*status_rx = buf_rx[1];
	*data_rx = buf_rx[2];
}

/**
 * @brief This function is used to execute a command.
 *
 * @param command has to be one element of @ref CMD_MU.
 * @retval None
 */
void mu_write_command(CMD_MU command) {
	mu_write_register(MU_CMD_MU.addr[0], (uint8_t) command);
}

/**
 * @brief This function switches the active memory bank.
 *
 * @param bank number to be switched to.
 * @retval None
 */
void mu_switch_bank(uint8_t bank) {
	mu_write_register(MU_BANKSEL.addr[0], bank);
}

/**
 * @brief This function reads a specific chip parameter.
 *
 * @note A sequence of SPI communications is executed that will increase transmission time compared to direct register access.
 *
 * @param param has to be one of the parameters defined in @ref MU_Parameters_List.
 * @retval Value of the parameter read.
 */
uint64_t mu_read_param(const struct mu_param *param) {
	uint8_t datasize = 0;

	if (param->len <= 8) {
		datasize = 1;
	}
	else if (param->len <= 16) {
		datasize = 2;
	}
	else if (param->len <= 24) {
		datasize = 3;
	}
	else if (param->len <= 32) {
		datasize = 4;
	}
	else if (param->len <= 40) {
		datasize = 5;
	}
	else {
		datasize = 6;
	}

	uint8_t startbit = get_start_bit_number(param->pos, param->len);
	uint8_t status = 0;
	uint8_t data_rx = 0;
	uint64_t param_val = 0;
	uint64_t param_mask = 0;

	if (param->addr[datasize - 1] < 0x40) {
		mu_switch_bank(param->bank);
	}

	for (uint8_t i = 0; i < datasize; i++) {
		mu_read_register(param->addr[i]);
		mu_wait_us(1);
		mu_register_status_data(&status, &data_rx);
		mu_wait_us(1);
		param_val |= ((uint64_t) data_rx << ((datasize - 1 - i) * 8));
	}

	param_val >>= startbit;

	for (uint8_t i = 0; i < param->len; i++) {
		param_mask |= ((uint64_t) 1 << i);
	}

	param_val &= param_mask;

	return param_val;
}

/**
 * @brief This function writes a specific chip parameter.
 *
 * @note A sequence of SPI communications is executed that will increase transmission time compared to direct register access.
 *
 * @param param has to be one of the parameters defined in @ref MU_Parameters_List.
 * @param param_val is the value to be written to the parameter.
 * @retval None
 */
void mu_write_param(const struct mu_param *param, uint64_t param_val) {
	uint8_t datasize = 0;

	if (param->len <= 8) {
		datasize = 1;
	}
	else if (param->len <= 16) {
		datasize = 2;
	}
	else if (param->len <= 24) {
		datasize = 3;
	}
	else if (param->len <= 32) {
		datasize = 4;
	}
	else if (param->len <= 40) {
		datasize = 5;
	}
	else {
		datasize = 6;
	}

	uint8_t startbit = get_start_bit_number(param->pos, param->len);
	uint8_t status = 0;
	uint8_t data_rx = 0;
	uint64_t reg_val = 0;
	uint64_t param_mask = 0;

	if (param->addr[datasize - 1] < 0x40) {
		mu_switch_bank(param->bank);
	}

	for (uint8_t i = 0; i < datasize; i++) {
		mu_read_register(param->addr[i]);
		mu_wait_us(1);
		mu_register_status_data(&status, &data_rx);
		mu_wait_us(1);
		reg_val |= ((uint64_t) data_rx << ((datasize - 1 - i) * 8));
	}

	for (uint8_t i = 0; i < (datasize * 8); i++) {
		if ((i < startbit) ^ (i > (startbit + param->len - 1))) {
			param_mask |= ((uint64_t) 0 << i);
		} else {
			param_mask |= ((uint64_t) 1 << i);
		}
	}

	reg_val &= ~param_mask;

	param_val <<= startbit;
	param_val &= param_mask;
	param_val |= reg_val;

	for (uint8_t i = 0; i < datasize; i++) {
		uint8_t data_tx = ((param_val >> (datasize - 1 - i) * 8)) & 0xFF;
		mu_write_register(param->addr[i], data_tx);
		mu_wait_us(1);
	}
}

/* local function definitions */
static uint8_t get_start_bit_number(uint8_t bit_pos, uint8_t bit_len) {
	bit_len = (bit_len - 1) % MU_REGISTER_SIZE;

	return (bit_pos - bit_len);
}
