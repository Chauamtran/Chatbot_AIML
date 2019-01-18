import aiml
import os
import datetime
from collections import Counter



def normalizeString(pattern_msg, type=1):
    if type == 1:
        if '.' == pattern_msg[-1]:
            pattern_msg = pattern_msg.replace(".", "")
        elif '!' == pattern_msg[-1]:
            pattern_msg = pattern_msg.replace("!", "")
        elif '?' == pattern_msg[-1]:
            pattern_msg = pattern_msg.replace("?", "")

        return pattern_msg.upper()


def createBasicFormat(type, pattern_msg, template_msg):
    if type == 1:
        normalized_msg = normalizeString(pattern_msg=pattern_msg, type=type)
        string_format = "<category><pattern>%s</pattern><template>%s</template></category>\n" % \
                        (normalized_msg, template_msg)
        return string_format
    else:
        return ""


def removeAndInsertAIML(previous_msg, current_msg, file):

    with open(file, 'r+') as f1:
        contents = f1.readlines()
        normalized_msg = normalizeString(pattern_msg=previous_msg)
        contents = [i for i in contents if normalized_msg not in i]

        msg = createBasicFormat(type=1, pattern_msg=previous_msg, template_msg=current_msg)
        contents.insert(-2, msg)

    # Write to a new file
    with open(file, 'w') as f2:
        contents = "".join(contents)
        f2.write(contents)

def insertAIML(previous_msg, current_msg, file):
    # Open current files and add to content
    with open(file, 'r+') as f1:
        contents = f1.readlines()
        msg = createBasicFormat(type=1, pattern_msg=previous_msg, template_msg=current_msg)
        contents.insert(-2, msg)

    # Write to a new file
    with open(file, 'w') as f2:
        contents = "".join(contents)
        f2.write(contents)


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

# Create the kernel and learn AIML files
kernel = aiml.Kernel()
kernel.verbose(False)
# Get current working path
path = os.getcwd()
xml_path = "%s/config" % (path)
xml_file = "%s/%s" % (xml_path, "std-startup.xml")
aiml_file = "%s/data/%s" % (path, "gianty_info.aiml")
conversation_file = "%s/conversations/%s" % (path, "conversation.txt")
conversation_statistics = "%s/conversations/%s" % (path, "conversation_statistics.txt")

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
    print("Bot: Hello! What can I do for you?")
    msg = raw_input("Human: ")

    # print(data_store)
    if msg == "exit":
        if data_store:
            storeFile(data=data_store, file=conversation_file)
            # writeDict(data=data_dict, file=)
        exit(0)
    elif msg == "save":
        kernel.saveBrain(bot_brain)

    elif msg.startswith("learn_bot_again"):
        removeAndInsertAIML(previous_msg=data_store[-1], current_msg=msg[15:], file=aiml_file)
        kernel.learn(aiml_file)

    elif msg.startswith("learn_bot"):
        insertAIML(previous_msg=data_store[-1], current_msg=msg[9:], file=aiml_file)
        kernel.learn(aiml_file)



    # To do: Check whether msg include date today?
    # elif msg
    else:
        if msg not in data_store and "learn_bot" not in msg and "learn_bot_again" not in msg:
            data_store.append(msg)

        if "date" in msg and "today" in msg:
            today = datetime.datetime.now()
            print("Bot: Date of today is %s" % today)
        else:
            bot_response = kernel.respond(msg)
            print("Bot: %s" % bot_response)


