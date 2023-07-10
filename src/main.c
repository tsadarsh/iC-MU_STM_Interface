#include "main.h"
#include "spi.h"
#include "usart.h"
#include "gpio.h"
#include "tim.h"

#include <stdio.h>
#include <inttypes.h>
#include <stdbool.h>
#include "mu_1sf_driver.h"

#define ENC_SPI_NCS_PORT GPIOC
#define ENC_SPI_NCS_PIN GPIO_PIN_1
#define ENC_SPI &hspi3
#define ENC_SPI_TIMEOUT 100
#define ENC_RX_DATA_SIZE_BYTES 3

#ifdef __GNUC__
#define PUTCHAR_PROTOTYPE int __io_putchar(int ch)
#else
#define PUTCHAR_PROTOTYPE int fputc(int ch, FILE *f)
#endif

PUTCHAR_PROTOTYPE
{
  HAL_UART_Transmit(&huart2, (uint8_t *)&ch, 1, HAL_MAX_DELAY);
  return ch;
}

bool CMD_RECEIVED = false;
uint8_t cmdData[3]= {};
uint8_t status_rx;
uint8_t data_rx;
uint8_t sdadStatus;
uint8_t DATA_RX[ENC_RX_DATA_SIZE_BYTES] = {};

void SystemClock_Config(void);

uint8_t readCMD(void);

void mu_spi_transfer(uint8_t *data_tx, uint8_t *data_rx, uint16_t datasize)
{
  HAL_GPIO_WritePin(ENC_SPI_NCS_PORT, ENC_SPI_NCS_PIN, GPIO_PIN_RESET);
  HAL_SPI_TransmitReceive(ENC_SPI, data_tx, data_rx, sizeof(*data_tx)*datasize, ENC_SPI_TIMEOUT);
  HAL_GPIO_WritePin(ENC_SPI_NCS_PORT, ENC_SPI_NCS_PIN, GPIO_PIN_SET);
}

void mu_wait_us(uint16_t time_us)
{
  __HAL_TIM_SET_COUNTER(&htim4, 0);
  while(__HAL_TIM_GET_COUNTER(&htim4) < time_us);
}

int main(void)
{
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();
  MX_USART2_UART_Init();
  MX_SPI3_Init();
  MX_USART1_UART_Init();
  MX_TIM4_Init();

  HAL_TIM_Base_Start(&htim4);
  HAL_UART_Receive_IT(&huart2, cmdData, sizeof(cmdData));

  while (1)
  {
    //uint8_t status_rx;
    //uint8_t data_rx;
    //mu_sdad_transmission(DATA_RX, sizeof(DATA_RX)/sizeof(DATA_RX[0]));
    //mu_read_register(MU_SPO_1.addr[0]);
    //mu_register_status_data(&status_rx, &data_rx);
    //printf("%d %d\r\n", status_rx, data_rx);
    /* USER CODE BEGIN 3 */
    readCMD();
    //HAL_GPIO_TogglePin(LD2_GPIO_Port, LD2_Pin);
    //HAL_Delay(100);
    //printf("%d\r\n", sizeof(cmdData));
    /* USER CODE END 3 */

  }
}

uint32_t get_encoder_data() {
  mu_sdad_transmission(DATA_RX, sizeof(DATA_RX)/sizeof(DATA_RX[0]));
  uint32_t val = (
      (((uint32_t)DATA_RX[2]) >> 5) | 
      (((uint32_t)DATA_RX[1]) << 3) | 
      (((uint32_t)DATA_RX[0]) << 11)
  );
  return val;
}

uint8_t readCMD()
{
  uint8_t retVal = -1;
  if (CMD_RECEIVED==true)
  {
    //Making a local copy so that the new value if received
    //while the following code is executed is not used
    if (cmdData[0] == 0xB0)
    {
      // ACTIVATE
    }
    else if(cmdData[0] == 0xA6)
    {
      // SDAD Transmission
      printf("%lu\r\n", get_encoder_data());
    }
    else if(cmdData[0] == 0xF5)
    {
      // SDAD Status (No latch)
      mu_sdad_status(&sdadStatus, 1);
      printf("%d\r\n", sdadStatus);
    }
    else if (cmdData[0] == 0x97)
    {
      // Read REGISTER (single)
      //printf("%d %d %d\r\n", cmdData[0], cmdData[1], cmdData[2]);
      mu_read_register(cmdData[1]);
      mu_register_status_data(&status_rx, &data_rx);
      printf("%d,%d\r\n", status_rx, data_rx);
    }
    else if (cmdData[0] == 0xD2)
    {
      // Write REGISTER (single)
    }
    else if (cmdData[0] == 0xAD)
    {
      // REGISTER status/data
    }
    else
      printf("Error!\r\n");
    retVal = 1;

    CMD_RECEIVED = false;
    HAL_UART_Receive_IT(&huart2, cmdData, sizeof(cmdData));
  }
  return retVal;
}

void HAL_UART_RxCpltCallback (UART_HandleTypeDef * huart)
{
  CMD_RECEIVED = true;
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE2);

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
  RCC_OscInitStruct.PLL.PLLM = 16;
  RCC_OscInitStruct.PLL.PLLN = 336;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV4;
  RCC_OscInitStruct.PLL.PLLQ = 7;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
