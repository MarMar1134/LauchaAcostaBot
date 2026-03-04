import os
import random
import re
from time import sleep
import logging

import praw
from dotenv import load_dotenv
from supabase import create_client, Client

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

load_dotenv()

# Reddit instance
redditEnv = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    password=os.getenv("REDDIT_PASSWORD"),
    username=os.getenv("REDDIT_USERNAME"),
    user_agent="Laucha-Acosta-v2.0",
    ratelimit_seconds=300
)

# Supabase, used to store comments id's and avoid duplications
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

subreddits = redditEnv.subreddit("ClubLanus+fulbo")

matchingCases = re.compile(r"\b(el\s+laucha|lautaro\s+acosta|laucha\s+acosta|al\s+laucha)\b", re.IGNORECASE)

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

# Returns a random phrase from the phrase list
def getRandomPhrase():
    return random.choice(phrases)

def isAnswered(item_id: str) -> bool:
    try:
        result = supabase.table("answered_ids").select("id").eq("id", item_id).execute()
        return len(result.data) > 0
    except Exception as e:
        logging.error(f"Error consultando Supabase para ID {item_id}: {e}")
        return False

def saveId(item_id: str, item_type: str):
    try:
        supabase.table("answered_ids").insert({"id": item_id, "type": item_type}).execute()
    except Exception as e:
        logging.error(f"Error guardando ID {item_id} en Supabase: {e}")

# Bot
logging.info("Bot iniciado - Monitoreando r/ClubLanus y r/fulbo")

try:
    for comment in subreddits.stream.comments(skip_existing=True):
        if isAnswered(comment.id):
            continue

        if matchingCases.search(comment.body):
            phrase = getRandomPhrase()
            try:
                comment.reply(phrase)
                saveId(comment.id, "comment")
                logging.info(f"Respondido comentario {comment.id}: '{phrase[:50]}...'")
                sleep(30)
            except Exception as e:
                logging.error(f"Error respondiendo comentario {comment.id}: {e}")
                sleep(60)

except KeyboardInterrupt:
    logging.info("Bot detenido por el usuario")
except Exception as e:
    logging.error(f"Error crítico: {e}")
    raise