import subprocess
import sys
from time import sleep
import logging
import threading
import os
from flask import Flask, jsonify

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - KEEP_ALIVE - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('keep_alive.log'),
        logging.StreamHandler()
    ]
)

# Configuración del bot
script_bot = "bot_script.py"
restart_count = 0
max_restarts_per_hour = 10
current_process = None
bot_status = "starting"

# Flask app para health check
app = Flask(__name__)

@app.route('/')
def health():
    return jsonify({
        "status": "running",
        "bot": "LauchaAcostaBot", 
        "bot_status": bot_status,
        "restart_count": restart_count
    })

@app.route('/status')
def detailed_status():
    return jsonify({
        "service": "LauchaAcostaBot Keep Alive",
        "bot_status": bot_status,
        "restart_count": restart_count,
        "max_restarts_per_hour": max_restarts_per_hour,
        "process_running": current_process is not None and current_process.poll() is None
    })

# Función para verificar si debe reiniciar
def should_restart():
    global restart_count

    if restart_count >= max_restarts_per_hour:
        logging.warning(f"Demasiados reinicios ({restart_count}). Esperando 1 hora...")
        sleep(3600)
        restart_count = 0

    return True

# Función principal del bot (en hilo separado)
def bot_manager():
    global current_process, bot_status, restart_count

    logging.info("Keep Alive iniciado - Monitoreando bot...")
    bot_status = "running"

    while True:
        try:
            if should_restart():
                logging.info(f"Inicializando bot (intento #{restart_count + 1})...")
                bot_status = "starting"

                current_process = subprocess.run([sys.executable, script_bot])
                restart_count += 1

                if current_process.returncode == 0:
                    logging.info("Bot terminó normalmente")
                    bot_status = "stopped_normally"
                else:
                    logging.error(f"Bot terminó con código de error: {current_process.returncode}")
                    bot_status = "error"

                logging.info("Esperando antes de reiniciar...")
                bot_status = "waiting_restart"
                sleep(30)

        except KeyboardInterrupt:
            logging.info("Keep Alive detenido por el usuario")
            bot_status = "stopped_by_user"
            print("\nEl programa se ha detenido exitosamente")
            break

        except Exception as ex:
            logging.error(f"Error en keep_alive: {ex}")
            bot_status = f"error: {str(ex)}"
            restart_count += 1
            sleep(60)

if __name__ == "__main__":
    # Iniciar el bot manager en un hilo separado
    bot_thread = threading.Thread(target=bot_manager)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Iniciar el servidor Flask para Render
    port = int(os.environ.get('PORT', 5000))
    logging.info(f"Iniciando servidor HTTP en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=False)