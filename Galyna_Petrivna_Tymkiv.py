import speech_recognition as sr
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import wikipedia
import sqlite3
import random


names = ['Галя ', 'Галю', 'Галина', 'Галино', 'Галька']
wiki = ['пошук', 'знайти', 'інформація', 'деталі', 'Вікіпедія', 'Вікіпедії']
amount = ["скільки", "кількість"]
yes = ['так', 'давай', 'можна', 'добре']
no = ['ні', 'не цікавить', 'відстань',]
by = ['добраніч', 'вирубись', 'бувай']
rand = ['випадкове число', "рандомне число", "рандом"]
def create_db():
    conn = sqlite3.connect('commands_and_responses.db')
    c = conn.cursor()
    try:
        c.execute('''
        CREATE TABLE commands (
            id INTEGER PRIMARY KEY,
            command TEXT UNIQUE
        )
        ''')

        c.execute('''
        CREATE TABLE wikipedia_queries (
            id INTEGER PRIMARY KEY,
            command_id INTEGER,
            query TEXT,
            response TEXT,
            FOREIGN KEY(command_id) REFERENCES commands(id)
        )
        ''')

        print("Підключення до бази даних пройшло успішно.")
    except:
        print("Підключення до бази даних пройшло успішно.")

    conn.commit()

    conn.close()


def listen_to_speech():
    r = sr.Recognizer() 
    text = ''
    with sr.Microphone() as source:
        print("Я Вас слухаю...")
        audio = r.listen(source)
    try:
        print("Розпізнавання...")
        text = r.recognize_google(audio, language='uk-UA')
        print(f"Ви сказали: {text}\n")

    except Exception as e:
        print("Я Bac не розумію, повторіть будь ласка")

    return text

def speak_ukrainian(text):
    speech = gTTS(text=text, lang='uk', slow=False)
    speech.save("text.mp3")
    audio = AudioSegment.from_mp3("text.mp3")
    play(audio)

def check_elements_in_string(string, elements):
    for element in elements:
        if element in string:
            return True
    return False

def greeting():
    text = 'Вітаю! Мене звати Галина Петрівна Тимків, чим я можу Вам допомогти?'
    speak_ukrainian(text)

def search_wikipedia(text):
    text = text.replace('пошук ', '').replace('Галя ', '')
    wikipedia.set_lang("uk")
    try:
        page = wikipedia.summary(text, sentences=3)
        conn = sqlite3.connect('commands_and_responses.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO commands (command) VALUES ('Вікіпедія')")
            command_id = c.lastrowid
        except sqlite3.IntegrityError:
            command_id = 1
        c.execute("INSERT INTO wikipedia_queries (command_id, query, response) VALUES (?, ?, ?)", (command_id, text, page))
        conn.commit()
        conn.close()
        return page
    except wikipedia.exceptions.PageError:
        return "No page found on Wikipedia"
    except Exception as e:
        return str(e)

def get_wikipedia_queries():
    conn = sqlite3.connect('commands_and_responses.db')
    c = conn.cursor()
    c.execute("SELECT query FROM wikipedia_queries")
    queries = c.fetchall()
    conn.close()
    num_queries = len(queries)
    text = 'Ви зробили ' + str(num_queries) + 'запитів до Вікіпедії. Озвучити 5 останніх?'
    speak_ukrainian(text)
    text = listen_to_speech()
    if check_elements_in_string(text, yes):
        last_queries = queries[-5:]
        for query in last_queries:
            speak_ukrainian(query[0])
    if check_elements_in_string(text, no):
        return 

def generate_random_number(text):
    for i in names:
        text = text.replace(i, '')
    for i in rand:
        text = text.replace(i, '')
    for t in text:
        text = text.replace('-', '')
    t = text.split(' ')
    min_value = int(text[0])
    max_value = int(text[1])
    text = str(random.randint(min_value, max_value))
    speak_ukrainian('Ваше випадкове число - ' + text)


def main():
    greeting()
    create_db()
    while True:
        text = listen_to_speech()
        if check_elements_in_string(text, names):
            if check_elements_in_string(text, by):
                speak_ukrainian("Припиняю роботу")
                exit()
            if check_elements_in_string(text, wiki) and not check_elements_in_string(text, amount):
                wiki_info = search_wikipedia(text)
                print(wiki_info)
                speak_ukrainian(wiki_info)
            if check_elements_in_string(text, wiki) and check_elements_in_string(text, amount):
                get_wikipedia_queries()
            if check_elements_in_string(text, rand):
                generate_random_number(text)

if __name__ == "__main__":
    main()
