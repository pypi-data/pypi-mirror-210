from subprocess import PIPE, Popen
from VBW.VBCore.VBError import VB_ERROR
import os


class INTERPRETER_PROCESS:

    def __init__(self, cScript, iScript, silenceExceptions):

        if cScript is None:  # It goes to the default path of CScript.exe in the most common configurations
            cScript = "C:/Windows/System32/CScript.exe"

        if iScript is None:  # By default it looks for the interactive interpreter in the same directory as this file
            iScript = os.path.join(os.path.split(os.path.realpath(__file__))[0], "interactive_interpreter.vbs")

        self.p = Popen([cScript,
                        '//nologo',
                        iScript],
                       stdout=PIPE,
                       stdin=PIPE,
                       encoding='ascii')

        self.errorStatus = 0
        self.errorNumber = 0
        self.silenceExceptions = silenceExceptions

    def communicate(self, message, printing=True):
        assert self.p is not None
        assert self.errorStatus == 0
        self.p.stdin.write(message + "\n")
        self.p.stdin.flush()
        answer = self.p.stdout.readline()
        abrupt_ending = "\n" not in answer
        if abrupt_ending or answer == "!>!>!>ERROR\n":
            if abrupt_ending:
                self.errorStatus = 1
                self.errorNumber = -1
                errorMessage = f"No response from VBS interpreter after message: \"{message}\""
            else: # Error message returned
                self.errorStatus = 2
                self.errorNumber = self.p.stdout.readline()[:-1]
                error = VB_ERROR.errorDictionary[self.errorNumber] \
                        if self.errorNumber in VB_ERROR.errorDictionary \
                        else self.errorNumber
                errorMessage = f"VBS interpreter failed with error({error}) after receiving message: \"{message}\""
            self.kill()
            if not self.silenceExceptions:
                raise VB_ERROR(errorMessage, self.errorNumber)
            return "!>!>!>END\n"
        else:
            if printing:
                print(answer, end="")
            return answer

    def kill(self):
        if self.healthy():
            self.p.kill()
        self.p = None

    def healthy(self):
        return self.p is not None
