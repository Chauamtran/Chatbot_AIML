import aiml
import os
import datetime

__author__ = "Chau.Tran"
__version__ = "1.0"

def createBasicFormat(type, pattern_msg, template_msg):
    if type == 1:

        if '.' == pattern_msg[-1]:
            pattern_msg = pattern_msg.replace(".", "")
        elif '!' == pattern_msg[-1]:
            pattern_msg = pattern_msg.replace("!", "")
        elif '?' == pattern_msg[-1]:
            pattern_msg = pattern_msg.replace("?", "")

        pattern_msg = pattern_msg.upper()

        string_format = "<category><pattern>%s</pattern><template>%s</template></category>\n" % \
                        (pattern_msg, template_msg)
        return string_format
    else:
        return ""

def insertAIML(previous_msg, current_msg, file):
    # Open current files and add to content
    with open(file, 'r+') as f1:
        contents =f1.readlines()
        msg = createBasicFormat(type=1, pattern_msg=previous_msg, template_msg=current_msg)
        contents.insert(-2, msg)

    # Write to a new file
    with open(file, 'w') as f2:
        contents = "".join(contents)
        f2.write(contents)

def storeFile(data, file):
    with open(file, 'w+') as f1:
        data_string = "".join(data)
        f1.write(data_string)

# Create the kernel and learn AIML files
kernel = aiml.Kernel()
kernel.verbose(False)
# Get current working path
path = os.getcwd()
xml_path = "%s/config" % (path)
xml_file = "%s/%s" % (xml_path, "std-startup.xml")
aiml_file = "%s/data/%s" % (path, "example_info.aiml")
conversation_file = "%s/conversations/%s" % (path, "conversation.txt")
bot_brain = "%s/model/bot_brain.brn" % path

data_store = []

if os.path.isfile(path=bot_brain):
    kernel.bootstrap(brainFile=bot_brain)
else:
    kernel.bootstrap(learnFiles=xml_file, commands="LOAD CHATBOT")
    kernel.saveBrain(bot_brain)

# kernel.learn(learn_aiml_file)
# os.chdir(xml_path)
# kernel.learn(xml_file)
# kernel.respond("LOAD CHATBOT")

# Press CTRL-C to break this loop
while True:

    msg = raw_input("Human: ")

    # print(data_store)
    if msg == "exit":
        if data_store:
            storeFile(data=data_store, file=conversation_file)
        exit(0)
    elif msg == "save":
        kernel.saveBrain(bot_brain)

    elif msg.startswith("learn_bot"):
        insertAIML(previous_msg=data_store[-1], current_msg=msg[9:], file=aiml_file)
        kernel.learn(aiml_file)

    # To do: Check whether msg include date today?
    # elif msg
    else:
        if msg not in data_store and "learn_bot" not in msg:
            data_store.append(msg)

        if "date" in msg and "today" in msg:
            today = datetime.datetime.now()
            print("Bot: Date of today is %s" % today)
        else:
            bot_response = kernel.respond(msg)
            print("Bot: %s" % bot_response)


