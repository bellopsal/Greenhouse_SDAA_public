import telebot
import time
import serial


from Garden import *
from configuration import *
from hum_read import *
from time import sleep
from loguru import logger
import os
from secrets_tokens import *


ser = serial.Serial('/dev/serial0', 38400, timeout=100)

# Bot token


# Initialize the bot
bot = telebot.TeleBot(TOKEN)

# Initialize the garden
garden = Garden()


# Add new plant command
@bot.message_handler(commands=["add_new_plant"])
def add_new_plant(message):
#     try:
    plant = garden.new_plant()
    bot.reply_to(message, "Preparing to take a picture of the new plant...")
    take_picture(plant)

    # Identify the plant and retrieve its humidity
    plant.name = identify_plant(plant.image_path)
    plant.humidity = get_humidity(plant.name)

    bot.reply_to(
        message,
        f"New plant added successfully!\n{plant}\n Picture taken and stored."
    )

    # Send the photo back to the user
    with open(plant.image_path, "rb") as photo:
        bot.send_photo(message.chat.id, photo)
        
    plant.schedule_tasks(lat, lon)

#     except Exception as e:
#         bot.reply_to(message, f"Unexpected error: {e}")

# Show plant command
@bot.message_handler(commands=["show_plant"])
def show_plant(message):
    try:
        args = message.text.split()[1:]
        if len(args) != 1:
            bot.reply_to(
                message,
                "Invalid input. Use: /show_plant <id>. Example: /show_plant 1",
            )
            return

        plant_id = args[0]
        plant = garden.get_plant(plant_id)
        if not plant:
            bot.reply_to(message, "Plant not found.")
            return

        # Simulate humidity measurement (replace with real sensor code if available)
        humidity = read_data()

        take_picture(plant)

        bot.reply_to(
            message,
            f"Plant Details:\n{plant}\nCurrent Humidity: {humidity:.2f}%",
        )
                
        with open(plant.image_path, "rb") as photo:
            bot.send_photo(message.chat.id, photo)
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")
        
# Show plant command
@bot.message_handler(commands=["water_plant"])
def water_plant(message):
    try:
        args = message.text.split()[1:]
        if len(args) != 1:
            bot.reply_to(
                message,
                "Invalid input. Use: /water_plant <id>. Example: /water_plant 1",
            )
            return

        plant_id = args[0]
        plant = garden.get_plant(plant_id)
        if not plant:
            bot.reply_to(message, "Plant not found.")
            return

        regar()
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

# Show plant command
@bot.message_handler(commands=["toggle_cover_plant"])
def togglecover_plant(message):
    try:
        args = message.text.split()[1:]
        if len(args) != 1:
            bot.reply_to(
                message,
                "Invalid input. Use: /cover_plant <id>. Example: /cover_plant 1",
            )
            return

        plant_id = args[0]
        plant = garden.get_plant(plant_id)
        if not plant:
            bot.reply_to(message, "Plant not found.")
            return

        plant.estado_motor = activate_motor_telebot(plant.estado_motor)
        if plant.estado_motor == "C":
            bot.reply_to(message, "Covering plant")
        else:
            bot.reply_to(message, "Uncovering plant")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")
        
# Delete all stored data command
@bot.message_handler(commands=["delete_all_data"])
def delete_all_data(message):
    try:
        garden.delete_all_plants()
        bot.reply_to(message, "All data deleted successfully.")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

# Start command
coordinates = None  # Variable to store the coordinates

@bot.message_handler(commands=["start"])
def start(message):
    logger.info("Telegram bot started")
    global coordinates
    if not coordinates:
        bot.reply_to(
            message,
            "Welcome to the Garden Bot! I see that you haven't provided your coordinates yet. Please send me your coordinates (latitude, longitude) in the format: 'latitude,longitude'.\n"
            "Use the following commands:\n"
            "/add_new_plant - Add a new plant.\n"
            "/show_plant <id> - Show plant details and picture.\n"
            "/delete_all_data - Delete all stored data.\n"
            "/water_plant <id> - Waters the plant.\n"
            "/toggle_cover_plant <id> - Change state of the cover.\n"
        )
        bot.register_next_step_handler(message, save_coordinates)
    else:
        bot.reply_to(
            message,
            "Welcome back to the Garden Bot! Your coordinates are already stored. You can now use the following commands:\n"
            "/add_new_plant - Add a new plant.\n"
            "/show_plant <id> - Show plant details and picture.\n"
            "/delete_all_data - Delete all stored data.\n"
            "/water_plant <id> - Waters the plant.\n"
            "/toggle_cover_plant <id> - Change state of the cover.\n"
        )

# Function to save the coordinates input by the user
def save_coordinates(message):
    global lat, lon
    try:
        lat, lon = map(float, message.text.split(','))
        coordinates = (lat, lon)
        bot.reply_to(
            message,
            f"Thank you! Your coordinates have been stored as: Latitude = {lat}, Longitude = {lon}.\n"
            "Now you can use the following commands:\n"
            "/add_new_plant - Add a new plant.\n"
            "/show_plant <id> - Show plant details and picture.\n"
            "/delete_all_data - Delete all stored data.\n"
            "/water_plant <id> - Waters the plant.\n"
            "/toggle_cover_plant <id> - Change state of the cover.\n"
        )
    except ValueError:
        bot.reply_to(
            message,
            "Sorry, the coordinates you provided are not in the correct format. Please try again using the format: 'latitude,longitude'."
        )
        bot.register_next_step_handler(message, save_coordinates)

# Polling loop to run the bot
bot.infinity_polling()
