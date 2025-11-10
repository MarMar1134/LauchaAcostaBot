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

redditEnv = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    password=os.getenv("REDDIT_PASSWORD"),
    username=os.getenv("REDDIT_USERNAME"),
    user_agent="Laucha-Acosta-v1.1",
    ratelimit_seconds=300
)

subreddits = redditEnv.subreddit("ClubLanus+fulbo")

# All these words will be searched to activate the bot
matchingCases = re.compile(r"\b(el\s+laucha|lautaro\s+acosta|laucha\s+acosta|al\s+laucha)\b", re.IGNORECASE)

#All phrase candidates
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

def getRandomPhrase():
    return random.choice(phrases)

# File where the answered comments are stored
answeredCommentsFile = "comments.txt"
answeredComments = set()

answeredSubmissionsFile = "submissions.txt"
answeredSubmissions = set()

#Inicializes the files that contains answered posts and comments.
def setUpFiles():
    pComments = set()
    pSubmissions = set()

    if os.path.exists(answeredCommentsFile):
        try:
            with open(answeredCommentsFile, "r", encoding="utf-8") as f:
                pComments = set(line.strip() for line in f.readlines())
            logging.info(f"Cargados {len(pComments)} comentarios ya respondidos")
        except Exception as e:
            logging.error(f"Error cargando comentarios: {e}")

    if os.path.exists(answeredSubmissionsFile):
        try:
            with open(answeredSubmissionsFile, "r", encoding="utf-8") as f:
                pSubmissions = set(line.strip() for line in f.readlines())
            logging.info(f"Cargados {len(pSubmissions)} posts ya respondidos")
        except Exception as e:
            logging.error(f"Error cargando posps: {e}")

    return pComments, pSubmissions

def isCommentAnswered(pCommentId) -> bool:
    return pCommentId in answeredComments

#Used to avoid replying to the same comments eternally
def saveCommentId(pCommentId):
    try:
        with open(answeredCommentsFile, "a", encoding="utf-8") as f:
            f.write(f"{pCommentId}\n")
        answeredComments.add(pCommentId)
    except Exception as error:
        logging.error(f"Error guardando comentario con ID:{pCommentId}, codigo de error: {error}")

def isSubmissionAnswered(pSubmissionId) -> bool:
    return pSubmissionId in answeredSubmissions

#Used to avoid replying to the same submissions eternally
def saveSubmissionId(pSubmissionId):
    try:
        with open(answeredSubmissionsFile, "a", encoding="utf-8") as f:
            f.write(f"{pSubmissionId}\n")
        answeredSubmissions.add(pSubmissionId)
    except Exception as error:
        logging.error(f"Error guardando post con ID:{pSubmissionId}, codigo de error: {error}")

#Start of the bot logic
logging.info("Bot iniciado - Monitoreando r/ClubLanus  y r/fulbo")

try:
    answeredComments, answeredSubmissions = setUpFiles()

    #Iterates for each post on the scoped subreddits
    for submission in subreddits.stream.submissions():
        #Inside every post, iterates on every comment searching any match
        for comment in submission.comments:
            if isCommentAnswered(comment.id):
                continue

            if matchingCases.search(comment.body):
                phrase = getRandomPhrase()

                comment.reply(phrase)
                saveCommentId(comment.id)

                logging.info(f"Respondido a comentario {comment.id} con: '{phrase[:50]}...'")
                sleep(30)

        #Once the comments of the post are reviewed, checks if the post title contains a keyword
        if isSubmissionAnswered(submission.id):
            continue

        if matchingCases.search(submission.title):
            phrase = getRandomPhrase()

            submission.reply(phrase)
            saveSubmissionId(submission.id)

            logging.info(f"Respondido al post {submission.id} con: {phrase[:50]}...")
            sleep(30)

except KeyboardInterrupt:
    logging.info("Bot detenido por el usuario")
except Exception as e:
    logging.error(f"Error crítico en el bot: {e}")
    raise