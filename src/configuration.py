import os
import sys
from loguru import logger
import helpers.logger_config
import cv2
import requests
import pandas as pd
import google.generativeai as genai
import RPi.GPIO as GPIO
import time
from datetime import datetime

from Garden import *
from open_meteo import fetch_weather_data
from hum_read import *
from motor import *
from secrets_tokens import *





PUMP_PIN = 17  # Pin GPIO donde está conectado el relé

# Configuración de GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(PUMP_PIN, GPIO.OUT)
GPIO.output(PUMP_PIN, GPIO.LOW)


def take_picture(plant):
    cap = cv2.VideoCapture(0)
    time.sleep(1)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        exit()

    # Capture a single frame
    ret, frame = cap.read()

    # If frame is read correctly, save the image
    if ret:
        logger.info("Frame captured")
        cv2.imwrite(plant.image_path, frame)
        logger.info(f"Image saved at {plant.image_path}.")
    else:
        logger.error("Error: Failed to capture frame.")
    
    cap.release()
    cv2.destroyAllWindows()
    

def identify_plant(picture_path):
    logger.info("Identifying plant type using Pl@ntNet API...")
    url = "https://my-api.plantnet.org/v2/identify/all"
     

    files = {"images": open(picture_path, "rb")}
    data = {"organs": "auto"}  
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        response = requests.post(url, files=files, data=data, headers=headers)
        response.raise_for_status()
        results = response.json()

        if "results" in results and results["results"]:
            plant_name = results["results"][0]["species"]["scientificNameWithoutAuthor"]
            logger.info(f"Plant identified as: {plant_name}")
            return plant_name
        else:
            logger.error("Could not identify the plant.")
            return None
    except Exception as e:
        logger.error(f"Error identifying plant: {e}")
        return None

# Function to create a Plant object from user input
def get_humidity(plant_name):
    genai.configure(api_key=GEMINI_TOKEN)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(f"Give me humidity percentage that this plant needs {plant_name}. Return just one number")
    return response.text.replace('\r', '').replace('\n', '')

def regar():
    GPIO.output(PUMP_PIN, GPIO.HIGH)
    time.sleep(3)
    GPIO.output(PUMP_PIN, GPIO.LOW)



def check_conditions(latitude, longitude, plant):
    logger.info("------------------------------------------------")
    logger.info("Starting plant check...")
    weather_df = fetch_weather_data(latitude, longitude, forecast_days=1)
    #logger.info(weather_df.head())
    
    current_hour = datetime.now().hour
    precipitation = weather_df[weather_df["date"].dt.hour == current_hour]["rain"].iloc[0]
    rain_prediction = precipitation > 0
    plant.estado_motor = activate_motor(rain_prediction, plant.estado_motor)
    
    humidity_current = read_data()

    
    if float(humidity_current) <= float(plant.humidity):
        regar()
    
    logger.info("------------------------------------------------")