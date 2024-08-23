I2C must be enabled in the raspberry pi config
The left sensor is connected to bus1
the right sensor is connected to bus3 (sda = 27, scl = 22). This bus must be created by adding this line to /boot/firmware/config.txt:
```
dtoverlay=i2c-gpio,bus=3,i2c_gpio_delay_us=1,i2c_gpio_sda=27,i2c_gpio_scl=22
```
