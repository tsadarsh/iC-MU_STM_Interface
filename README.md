# Usage
Clone and install python deps in a virtual environment using:
```
pip install -r requirements.txt
```

1. Connect STM32's Nucleo-F401RE and upload the firmware (in `lib/` and `src/`) (PlatformIO).
2. Connect the encoder PCB to SPI3 pins (see Pinouts below).
3. Run python `main.py`

Run using python3:
```
python3 gui/main.py
```

# Pinouts
| Pin | Function |
|-----|----------|
| PC1 | SPI3_NCS |
| PC10 | SPI3_CLK |
| PC11 | SPI3_MISO |
| PC12 | SPI3_MOSI |
| PA2 | UART2_TX |
| PA3 | UART2_RX |
