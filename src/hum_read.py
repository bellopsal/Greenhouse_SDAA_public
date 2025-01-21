import smbus2
import time
from loguru import logger

DEVICE_ADDRESS = 0x48
REGISTER_ADDRESS = 0x00
bus = smbus2.SMBus(1)

def scan_i2c_bus():
    print("seacrhing")
    for address in range(128):
        try:
            bus.write_byte(address,0)
            logger.info(f"0x{address:02X}")
        except OSError:
            pass
        
def read_data():
    config = [0x83, 0x85]
    bus.write_i2c_block_data(DEVICE_ADDRESS, 0x01, config)
    config = bus.read_i2c_block_data(DEVICE_ADDRESS, 0x01, 2)
    data = bus.read_i2c_block_data(DEVICE_ADDRESS, REGISTER_ADDRESS, 2)
    try:
 
        data = bus.read_i2c_block_data(DEVICE_ADDRESS, REGISTER_ADDRESS, 2)
        
        msb = data[0]
        lsb = data[1]
        raw_data = (msb << 8) | lsb
        
        if raw_data > 0x7FFF:
            raw_data -= 0x10000
        
        voltage = (raw_data / 32768) *3.3
#         soil_moisture = (1 -(voltage /3.3))*100
        soil_moisture = (-74.63 * voltage) + 160
        soil_moisture = max (0, min(100, soil_moisture))
# 
#         print(f"Raw Data: {raw_data}")
#         print(f"voltage: {voltage:.2f}")
        logger.info(f"soil moist: {soil_moisture:.2f}")
        return soil_moisture
        
    
        
    except Exception as e:
        logger.error(e)
        
        
     
        
if __name__ =="__main__":
    scan_i2c_bus()
    while True:
        read_data()
        time.sleep(1)