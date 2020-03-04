import aiml
import os
import datetime
import speech_recognition as sr
import pyttsx
import flask, urllib

from collections import Counter
from flask import Flask, request
from flask_cache import Cache
from flask_classy import FlaskView, route

"""
    - Supported web service
    - Supported communication to human by sound
    - Record and process sound of human
    - Organize code to class method
"""

__author__ = "Chau.Tran"
__version__ = "1.4"


# TO DO LISTS
# 1. Add web interface
# 2. Add to process and support sound from human

flask_chatbot = Flask(__name__)

cache = Cache(flask_chatbot, config = {'CACHE_TYPE' : 'simple'})
cache.init_app(flask_chatbot)

def make_cached_key_post():

    args = request.form
    key = flask.request.path + '?' + urllib.urlencode([(k, v) for k in sorted(args) for v in sorted(args.getlist(k))])
    return key

def make_cached_key_get():

    args = request.args
    key = flask.request.path + '?' + urllib.urlencode([(k, v) for k in sorted(args) for v in sorted(args.getlist(k))])
    return key


def make_cached_key():
    get_args = request.args
    post_args = request.form

    if post_args:
        return flask.request.path + '?' + urllib.urlencode(
            [(k, v) for k in sorted(post_args) for v in sorted(post_args.getlist(k))])

    if get_args:
        return flask.request.path + '?' + urllib.urlencode(
            [(k, v) for k in sorted(get_args) for v in sorted(get_args.getlist(k))])

def storeFile(data, file):
    with open(file, 'w+') as f1:
        data_string = "\n".join(data)
        f1.write(data_string)

def writeDict(data, file):
    import csv

    with open(file, 'w+') as f1:
        writer = csv.writer(f1)
        for k, v in data.items():
            writer.writerow([k, v])


class ChatBot(FlaskView):
    route_base = '/'

    # @route('/event/userexplorer/action', methods=['GET', 'POST'])
    # @cache.cached(timeout=72000, key_prefix=make_cached_key)
    def __init__(self):
        pass


    # @flask_chatbot.before_first_request
    def getConfig(self):
        self.speech_engine = pyttsx.init('espeak')
        self.speech_engine.setProperty('rate', 150)
        self.speech_engine.setProperty('voice', 'english-us')

        self.voices = self.speech_engine.getProperty('voices')

        self.recognizer = sr.Recognizer()

        # Create the kernel and learn AIML files
        self.kernel = aiml.Kernel()
        # self.kernel.verbose(False)
        # Get current working path
        path = os.getcwd()

        xml_path = "%s/config" % (path)
        self.xml_file = "%s/%s" % (xml_path, "std-startup.xml")
        self.aiml_file = "%s/data/%s" % (path, "example_info.aiml")
        self.conversation_file = "%s/conversations/%s" % (path, "conversation.txt")
        self.conversation_statistics = "%s/conversations/%s" % (path, "conversation_statistics.txt")

        self.bot_brain = "%s/model/bot_brain.brn" % path

        self.data_store = []

        if os.path.isfile(path=self.bot_brain):
            self.kernel.bootstrap(brainFile=self.bot_brain)
        else:
            self.kernel.bootstrap(learnFiles=self.xml_file, commands="LOAD CHATBOT")
        self.kernel.saveBrain(self.bot_brain)

    # for voice in voices:
#     print "Using voice:", repr(voice)
#     print("void_id = %s" % voice.id)
#     speech_engine.setProperty('voice', voice.id)
#     speech_engine.say("Sunday Monday Tuesday Wednesday Thursday Friday Saturday")
#     speech_engine.say("Violet Indigo Blue Green Yellow Orange Red")
#     speech_engine.say("Apple Banana Cherry Date Guava")
#     speech_engine.say("Us President.")
#     speech_engine.runAndWait()



    def speak(self, text):
        self.speech_engine.say(text=text)
        self.speech_engine.say(" ")
        self.speech_engine.runAndWait()

    def listen(self):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source=source)
            audio = self.recognizer.listen(source=source)

        try:
            return self.recognizer.recognize_sphinx(audio_data=audio)

        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as re:
            print("Recog Error; {}".format(re))

        return ""


    def normalizeString(self, pattern_msg, type=1):
        import re

        if type == 1:
            # if '.' == pattern_msg[-1]:
            #     pattern_msg = pattern_msg.replace(".", "")
            # elif '!' == pattern_msg[-1]:
            #     pattern_msg = pattern_msg.replace("!", "")
            # elif '?' == pattern_msg[-1]:
            #     pattern_msg = pattern_msg.replace("?", "")
            normalized_string = re.sub('\W+', " ", pattern_msg)
            return normalized_string.upper()


    def createBasicFormat(self, type, pattern_msg, template_msg):
        if type == 1:
            normalized_msg = self.normalizeString(pattern_msg=pattern_msg, type=type)
            string_format = "<category><pattern>%s</pattern><template>%s</template></category>\n" % \
                            (normalized_msg, template_msg)
            return string_format
        else:
            return ""


    def removeAndInsertAIML(self, previous_msg, current_msg, file):

        with open(file, 'r+') as f1:
            contents = f1.readlines()
            normalized_msg = self.normalizeString(pattern_msg=previous_msg)
            contents = [i for i in contents if normalized_msg not in i]

            msg = self.createBasicFormat(type=1, pattern_msg=previous_msg, template_msg=current_msg)
            contents.insert(-2, msg)

        # Write to a new file
        with open(file, 'w') as f2:
            contents = "".join(contents)
            f2.write(contents)

    def insertAIML(self, previous_msg, current_msg, file):
        # Open current files and add to content
        with open(file, 'r+') as f1:
            contents = f1.readlines()
            msg = self.createBasicFormat(type=1, pattern_msg=previous_msg, template_msg=current_msg)
            contents.insert(-2, msg)

        # Write to a new file
        with open(file, 'w') as f2:
            contents = "".join(contents)
            f2.write(contents)

    @route('/chatbot/action', methods=['GET', 'POST'])
    @cache.cached(timeout=72000, key_prefix=make_cached_key)
    def getBotMsg(self):
        import simplejson as json
        from flask import request

        if request.method == 'GET':
            print("GET %s" % request.args)
            msg = request.args.get('message')
        else:
            print("POST %s" % request.form)
            msg = request.form.get('message')

        if msg:
            # msg = msg.encode('ascii', 'ignore')
            # print(msg)
            # print(chat_bot.data_store)
        # while True:
            # speak("Please speak something")
            # msg = listen()

            # msg = raw_input("Human: ")

            # print(data_store)
            if msg == "exit":
                if chat_bot.data_store:
                    storeFile(data=chat_bot.data_store, file=chat_bot.conversation_file)

                exit(0)
            elif msg == "save_brain":
                chat_bot.kernel.saveBrain(chat_bot.bot_brain)
                learn_msg = "Thanks! I saved new information to my brain" % msg[9:]
                chat_bot.speak(learn_msg)
                return json.dumps({'message': learn_msg})

            elif msg.startswith("learn_bot_again"):
                chat_bot.removeAndInsertAIML(previous_msg=chat_bot.data_store[-1], current_msg=msg[15:],
                                             file=chat_bot.aiml_file)
                chat_bot.kernel.learn(chat_bot.aiml_file)
                learn_msg = "Thanks! I learned that %s" % msg[9:]
                chat_bot.speak(learn_msg)
                return json.dumps({'message': learn_msg})

            elif msg.startswith("learn_bot"):
                chat_bot.insertAIML(previous_msg=chat_bot.data_store[-1], current_msg=msg[9:],
                                    file=chat_bot.aiml_file)
                chat_bot.kernel.learn(chat_bot.aiml_file)
                learn_msg = "Thanks! I learned that %s" % msg[9:]
                chat_bot.speak(learn_msg)
                return json.dumps({'message': learn_msg})

            # To do: Check whether msg include date today?
            # elif msg
            else:
                if msg not in chat_bot.data_store and "learn_bot" not in msg and "learn_bot_again" not in msg:
                    chat_bot.data_store.append(msg)

                if "date" in msg and "today" in msg:
                    today = datetime.datetime.now().strftime(format="%Y-%m-%d")
                    date_msg = "Date of today is %s" % today
                    chat_bot.speak(date_msg)
                    print("Bot: Date of today is %s" % today)
                    return json.dumps({'message': date_msg})
                else:
                    # Normalize string before processing
                    msg = chat_bot.normalizeString(pattern_msg=msg)
                    print(msg)
                    bot_response = chat_bot.kernel.respond(msg)
                    print(bot_response)
                    chat_bot.speak(bot_response)
                    print("Bot: %s" % bot_response)

                    return json.dumps({'message': bot_response})


if __name__ == "__main__":

    with flask_chatbot.test_request_context():

        chat_bot = ChatBot()
        chat_bot.getConfig()
        chat_bot.register(flask_chatbot)
        flask_chatbot.run(host="10.0.0.39", port=10003, debug=True, threaded=True, use_reloader=False)

        # print("Bot: Hello! What can I do for you?")
        # chat_bot.speak("Hello! What can I do for you?")
        msg = chat_bot.getBotMsg()


    cache.clear()
