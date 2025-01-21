import schedule
from configuration import *
from loguru import logger


class Plant:
    def __init__(self, plant_id = None,name= None, humidity= None, sensor_pin= None, motor_pin= None):
        self.name = name
        self.plant_id = plant_id
        self.humidity = humidity
        self.sensor_pin = sensor_pin
        self.motor_pin = motor_pin
        self.estado_motor = 'D'
        # self.image_path = f"images/plant_{plant_id}.jpg"
        self.image_path = f"./images/plant_{plant_id}.jpg"
    
    def __str__(self):
        return (f"Plant ID: {self.plant_id}\n"
                f"Plant Name: {self.name}\n"
                f"Humidity Level Required: {self.humidity}\n")

    
    def schedule_tasks(self, latitude, longitude):
        global hourly_dataframe
        
        if self.name != None:
            schedule.every(1).minutes.do(check_conditions, latitude = latitude, longitude = longitude,
                                          plant = self)
            

            # Start the scheduling
            while True:
                schedule.run_pending()
                time.sleep(1)


# Class for the Garden
class Garden:
    def __init__(self):
        self.plants = {}
        self.next_id = 1  # Counter for automatic plant IDs

    def new_plant(self):
        plant_id = str(self.next_id)
        self.plants[plant_id] = Plant(plant_id = plant_id)
        self.next_id += 1
        return self.plants[plant_id]

    def get_plant(self, plant_id):
        return self.plants.get(plant_id)

    def delete_all_plants(self):
        self.plants.clear()
        self.next_id = 1  # Reset the ID counter
