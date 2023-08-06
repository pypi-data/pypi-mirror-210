import os
from nlp2fn.utils.colorpriniting import info, warning
from nlp2fn.sourcehandler import SourceModel
from nlp2fn.utils.fncloader import run_function_from_file

WELCOME_PROMPT = '''Welcome to the NLP2FN

NLP2FN is a powerful software for natural language processing. It converts statements into function calls, making it easy to execute commands based on user input. Simply enter your statement, and NLP2FN will handle the rest.

To use:

Enter a statement.
NLP2FN will analyze it and identify the corresponding function call.
Execute the function call to perform the desired action.
For more information, visit github : https://github.com/dextrop/nlp2fn

Get started and unleash the power of NLP2FN!
Press any key to continue, press c to cancel.
'''

EXIT_PROMPT = '''Thank you for using the NLP2FN!

We hope that NLP2FN has been helpful in simplifying your natural language processing tasks. If you have any feedback or suggestions, please feel free to share them with us.

Remember, NLP2FN is always here to assist you with converting statements into function calls. Keep exploring the possibilities and enjoy your continued journey in NLP.

Goodbye and have a fantastic day!'''

ADD_SOURCE_PROMPT = '''Welcome to the Interface!

To proceed, please provide a source for the interface.

Example Sources:
1. Local Library Path: /path/to/library
2. GitHub Repository: https://github.com/dextrop/evt-langchain

If you have a specific source in mind, enter it below. Otherwise, leave it blank and press Enter to continue.

Source:

Note: If you are interested in creating your own automation library using NLP2FN, check out this helpful tutorial: 
"Creating Your Own Automation Library with NLP2FN" (https://blog.devgenius.io/creating-your-own-automation-library-with-nlp2fn-6657b1276361)
'''

class NLP2FnInterface():
    def __init__(self):
        self.source = None
        self.sourceModel = SourceModel()
        # self.sourceHandler = SourceHandler()

    def show_statements(self, statement):
        info("Available Automations:\n")
        for key in statement:
            info(f"- {key.title()}")

        print("\n")

    def clear_screen(self):
        """
        Clears the screen in a Python console application.
        """

        # Clear screen for Windows
        if os.name == 'nt':
            os.system('cls')

        # Clear screen for Unix/Linux/MacOS
        else:
            os.system('clear')

    def welcome(self):
        """
        This method prints a welcome message for the user and also takes input from user
        if user wish to continue, if not it exit the interface with an exit message

        Usage: Used as soon as interface is inilised after welcome message is shown
        :return:
        """
        self.clear_screen()
        info(WELCOME_PROMPT)
        doContinue = input("")

        if doContinue.lower().replace(" ", "") == "c":
            info(EXIT_PROMPT)
            return True

        self.clear_screen()
        return True

    def do_wish_to_continue(self):
        warning("\n\nDo you wish to continue (y/n)?")
        choice = input(">> ")

        self.clear_screen()
        if choice.replace(" ", "").lower() == "y":
            return True

        info(EXIT_PROMPT)
        return False

    def execute(self, dir, params):
        function_name = "execute"

        # @todo Instead of passing Arr pass Dict.
        paramsArr = []
        for key in params:
            paramsArr.append(params[key])


        run_function_from_file(
            dir, function_name, paramsArr
        )

    def run(self):
        """
            Run the interface
        :return:
        """
        self.welcome()
        sources = self.sourceModel.get_sources()
        if len(sources.keys()) < 1:
            info(ADD_SOURCE_PROMPT)
            source = input("\nEnter the source URL or local directory path: ")
            self.sourceModel.add(source)

        doContinue = True
        while(doContinue):
            statement = input("What can I do for you?\n>> ")
            if statement[:4] == "exit":
                doContinue = False

            elif statement == "reset":
                self.sourceModel.reset()

            elif statement == "remove":
                self.sourceModel.remove()

            elif statement == "help":
                self.show_statements(
                    self.sourceModel.get_statements()
                )
            elif statement == "update":
                self.update()
            else:
                function_name, params = self.sourceModel.match(statement)
                if function_name != None:
                    self.execute(function_name, params)

    def run_single_command(self, statement):
        function_name, params = self.sourceModel.match(statement)
        self.execute(function_name, params)

    def update(self):
        sources = self.sourceModel.get_sources()
        for key in sources:
            self.sourceModel.add(sources[key])





