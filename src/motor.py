import RPi.GPIO as GPIO
import time
from loguru import logger
#Estado inicial del motor DESCUBIERTO
estado_motor='D'        

# Pines GPIO conectados al motor del techo
techo_pins = [5,6,13,19]  # Cambia estos pines según la conexión física

# Secuencia Half-Step
step_sequence = [
    [1, 0, 0, 0],  # Paso 1
    [1, 1, 0, 0],  # Paso 2
    [0, 1, 0, 0],  # Paso 3
    [0, 1, 1, 0],  # Paso 4
    [0, 0, 1, 0],  # Paso 5
    [0, 0, 1, 1],  # Paso 6
    [0, 0, 0, 1],  # Paso 7
    [1, 0, 0, 1],  # Paso 8
]

# Configuración de los pines GPIO
GPIO.setmode(GPIO.BCM)
for pin in techo_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, 0)

# Función para mover el motor
def move_motor(steps, direction, delay=0.002):
    #print(f"Moviendo motor ({'Cubrir' if direction == 'cubrir' else 'Descubrir'})...")
    if direction == "descubrir":
        step_sequence.reverse()
    for _ in range(steps):
        for step in step_sequence:
            for pin in range(4):
                GPIO.output(techo_pins[pin], step[pin])
            time.sleep(delay)
    if direction == "cubrir":
        step_sequence.reverse()
    #print("Movimiento completado.\n")

# Configuración inicial
print("Sistema automático de techo para plantas")

def activate_motor(rain_prediction, estado_motor):
    if rain_prediction:
        logger.info("Se predice lluvia. Preparando para cubrir la planta...")         
    
        if(estado_motor == 'D'):
            # Activar motor para cubrir
            logger.info("Activando el motor para cubrir la planta.")
            move_motor(260, "cubrir")  # 260 pasos para cubrir
            estado_motor='C'
        else:
            #Si ya estaba cubierto, no moveremos el motor
            logger.info("Dejamos planta cubierta.")
    else:
        if(estado_motor=='C'):
            # Activar motor para descubrir
            logger.info("No se predice lluvia. Quitar techo de la planta.")
            move_motor(260, "descubrir")  # 260 pasos para descubrir
            estado_motor='D'
        else:
            #ya estaba descurbierto, mo movemos motor
            logger.info("Dejamos planta descubierta.")
        
    return estado_motor

def activate_motor_telebot(estado_motor):
    if(estado_motor == 'D'):
            # Activar motor para cubrir
        logger.info("TT Activando el motor para cubrir la planta.")
        move_motor(260, "cubrir")  # 260 pasos para cubrir
        estado_motor='C'
    else:
        # Activar motor para descubrir
        logger.info("TT Quitar techo de la planta.")
        move_motor(260, "descubrir")  # 260 pasos para descubrir
        estado_motor='D'
        
    return estado_motor