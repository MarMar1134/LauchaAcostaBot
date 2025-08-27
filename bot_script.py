import os
import random
import re
from time import sleep
import logging

import praw
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    password=os.getenv("REDDIT_PASSWORD"),
    username=os.getenv("REDDIT_USERNAME"),
    user_agent="Laucha-Acosta-v1",
    ratelimit_seconds=300
)

subreddit = reddit.subreddit("ClubLanus")

# All these words will be searched to activate the bot
matching_cases = re.compile(r"\b(el\s+laucha|lautaro\s+acosta|laucha\s+acosta)\b", re.IGNORECASE)

phrases = [
    "es todo lo que yo no soy",
    "Madurar es alcanzar un equilibrio, y en ese camino estoy, aprendiendo, escuchando a los que saben",
    "Los jugadores de fútbol vivimos dentro de una burbuja",
    "Mi ídolo no es ni Maradona, ni Messi... ¿Sabés quién es mi ídolo? Batistuta",
    "No unifican criterios",
    "Es un referí complicado. Depende quién lo necesite, dirige Hernán",
    "No hay que confundirse y creer que todos somos millonarios",
    "La gambeta me salvó la vida, y hacer terapia, la carrera"
]

# File where the answered comments are stored
answered_comments_file = "comments.txt"
current_comments = set()

#Load already replied comments
if os.path.exists(answered_comments_file):
    try:
        with open(answered_comments_file, "r", encoding="utf-8") as f:
            current_comments = set(line.strip() for line in f.readlines())
        logging.info(f"Cargados {len(current_comments)} comentarios ya respondidos")
    except Exception as e:
        logging.error(f"Error cargando comentarios: {e}")

#Used to avoid replying to the same comments eternally
def save_comment_id(comment_id):
    try:
        with open(answered_comments_file, "a", encoding="utf-8") as f:
            f.write(f"{comment_id}\n")
        current_comments.add(comment_id)
    except Exception as e:
        logging.error(f"Error guardando comment ID: {e}")

#If there were only one phrase, what would be the joke?
def get_random_phrase():
    return random.choice(phrases)

logging.info("Bot iniciado - Monitoreando r/ClubLanus")

try:
    for comment in subreddit.stream.comments(skip_existing=True):
        try:
            if comment.id in current_comments:
                continue

            if matching_cases.search(comment.body):
                phrase_to_reply = get_random_phrase()

                # Responder al comentario
                comment.reply(phrase_to_reply)
                save_comment_id(comment.id)

                logging.info(f"Respondido a comentario {comment.id} con: '{phrase_to_reply[:50]}...'")
                sleep(60)

        except Exception as e:
            logging.error(f"Error procesando comentario: {e}")
            sleep(30)
            continue

except KeyboardInterrupt:
    logging.info("Bot detenido por el usuario")
except Exception as e:
    logging.error(f"Error crítico en el bot: {e}")
    raise