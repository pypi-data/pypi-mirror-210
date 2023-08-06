from VBW.VBCore.VBWrapperBase import VB_WRAPPER_BASE

"""
This shell uses a recoverAfterFailure command to save the shell from failure after an error.
In case the flag onlyRecoverError1002 is activated, only the invalid input error will be allowed to continue
"""
class VB_WRAPPER_SHELL(VB_WRAPPER_BASE):

    def __init__(self, path2CScript = None, path2InterpreterScript = None, silenceExceptions = True, recoverAfterFailure = True, onlyRecoverError1002 = True):
        assert silenceExceptions or not recoverAfterFailure # Can not recover if exceptions have not been silenced
        assert recoverAfterFailure or not onlyRecoverError1002 # Only Error 1002 is not allowed if there is no recovery after failure
        self.recoverAfterFailure = recoverAfterFailure
        self.onlyRecoverError1002 = onlyRecoverError1002
        super().__init__(path2CScript, path2InterpreterScript, silenceExceptions)

    def run(self):
        assert self.interpreter is not None
        assert self.interpreter.errorStatus == 0
        if self.recoverAfterFailure:
            if self.onlyRecoverError1002:
                command = """if errorNumber=1002 then: continueRunningAfterRecovery = True: else: wscript.echo \"\"!>!>!>INVALID-INPUT\"\": end if"""
            else:
                command = """continueRunningAfterRecovery = True"""
        else:
            command = """wscript.echo \"\"!>!>!>INVALID-INPUT\"\" """
        if command not in self.cGetRecoveryCommandsArray():
            self.cAddRecoveryCommandFirst(command)
        answer = ""
        while answer not in ["!>!>!>END\n","!>!>!>INVALID-INPUT\n"]:
            answer = self.communicateWithInterpreter(input())

"""
This shell uses the startup_commands to create a new shell with the same status as the previous one BEFORE restart.
Take into consideration that all operations are going to be done once again, so operations that are not idempotent
(for example, create a new document) can lead to potential issues when retrying them.
"""
class VB_WRAPPER_SHELL2(VB_WRAPPER_BASE):

    def __init__(self, path2CScript = None, path2InterpreterScript = None, silenceExceptions = True, recoverAfterFailure = True):
        assert silenceExceptions or not recoverAfterFailure # Can not recover if exceptions have not been silenced
        self.recoverAfterFailure = recoverAfterFailure
        super().__init__(path2CScript, path2InterpreterScript, silenceExceptions)

    def run(self):
        assert self.interpreter is not None
        assert self.interpreter.errorStatus == 0
        answer = ""
        while answer != "!>!>!>END\n":
            answer = self.communicateWithInterpreter(input())
            if self.recoverAfterFailure and self.interpreter.errorStatus != 0:
                self.createInterpreter(startup_commands=self.history[:-1])
                answer = ""

    def doRecordMessage(self,message,recording):
        return recording and self.recoverAfterFailure