import subprocess
import sys
from time import sleep
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - KEEP_ALIVE - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('keep_alive.log'),
        logging.StreamHandler()
    ]
)

script_bot = "bot_script.py"
restart_count = 0
max_restarts_per_hour = 10

# Used to avoid overloading the server
def should_restart():
    global restart_count

    if restart_count >= max_restarts_per_hour:
        logging.warning(f"Demasiados reinicios ({restart_count}). Esperando 1 hora...")
        sleep(3600)
        restart_count = 0

    return True


logging.info("Keep Alive iniciado - Monitoreando bot...")

while True:
    try:
        if should_restart():
            logging.info(f"Inicializando bot (intento #{restart_count + 1})...")

            process = subprocess.run([sys.executable, script_bot])

            restart_count += 1

            if process.returncode == 0:
                logging.info("Bot terminó normalmente")
            else:
                logging.error(f"Bot terminó con código de error: {process.returncode}")

            logging.info("Esperando antes de reiniciar...")
            sleep(30)

    except KeyboardInterrupt:
        logging.info("Keep Alive detenido por el usuario")
        print("\nEl programa se ha detenido exitosamente")
        break

    except Exception as ex:
        logging.error(f"Error en keep_alive: {ex}")
        restart_count += 1
        sleep(60)