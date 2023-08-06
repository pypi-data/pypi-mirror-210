from VBW.VBCore.VBInterpreterProcess import INTERPRETER_PROCESS


class VB_WRAPPER_BASE:

    # WRAPPER

    def __init__(self, path2CScript=None, path2InterpreterScript=None,
                 silenceExceptions=True, default_startup_commands=None):
        self.cScript = path2CScript
        self.iScript = path2InterpreterScript
        self.silenceExceptions = silenceExceptions
        self.history = []
        self.interpreter = None
        self.default_startup_commands = default_startup_commands

    def has_healthy_interpreter(self):
        return self.interpreter is not None and self.interpreter.healthy()

    # Interpreter Manipulation

    def createInterpreter(self,  startup_commands=None):
        if self.interpreter is not None:
            self.interpreter.kill()
        if startup_commands is None:
            startup_commands = self.default_startup_commands
        self.history = []
        self.interpreter = INTERPRETER_PROCESS(self.cScript, self.iScript, self.silenceExceptions)
        self.interpreterInitialization(startup_commands=[] if startup_commands is None else startup_commands)

    def communicateWithInterpreter(self, message, printing=True, recording=True):
        assert self.has_healthy_interpreter()
        if self.doRecordMessage(message,recording):
            self.history.append(message)
        return self.interpreter.communicate(message,printing)

    def doRecordMessage(self,message,recording):
        return recording

    def interpreterInitialization(self, startup_commands):
        assert self.has_healthy_interpreter()
        for sc in startup_commands:
            self.communicateWithInterpreter(sc, printing=False, recording=False)

    def destroyInterpreter(self, noisy=False):
        assert self.has_healthy_interpreter()
        exitmsg = self.cExit()
        if noisy:
            print(exitmsg)
        self.interpreter.kill()
        self.history = []
        self.interpreter = None

    # Core Commands

    def cExec(self,message, printing=False, recording=True):
        assert self.has_healthy_interpreter()
        message_sent = self.communicateWithInterpreter(message + "'x", printing= printing, recording= recording)
        return (message+"'x\n") == message_sent

    def cEval(self,message, printing=True, recording=True):
        assert self.has_healthy_interpreter()
        answer = self.communicateWithInterpreter(message, printing= printing, recording= recording)[:-1]
        return answer

    def cExit(self):
        assert self.has_healthy_interpreter()
        return self.communicateWithInterpreter("'e", printing=False, recording=False)

    # Recovery/Exiting commands

    def _cGetCommandsArray(self, array):
        n = self.cEval(f"UBound({array})", printing=False, recording=False)
        arrayCommands = [self.cEval(f"{array}({n})", printing=False, recording=False) for n in range(int(n)+1)]
        return arrayCommands

    def _cAddArrayCommand(self, array, command):
        commandsArray = self._cGetCommandsArray(array)
        try:
            index = commandsArray.index("")
        except ValueError:
            index = len(commandsArray)
            self.cExec(f"ReDim Preserve {array}({index})")
        self.cExec(f"{array}({index}) = \"{command}\"")

    def _cAddArrayCommandFirst(self, array, command):
        commandsArray = self._cGetCommandsArray(array)
        index = len(commandsArray)
        self.cExec(f"ReDim {array}({index})")
        self.cExec(f"{array}(1) = \"{command}\"")
        for x in range(len(commandsArray)):
            self.cExec(f"{array}({x+1}) = \"{commandsArray[x]}\"")

    def _cRemoveArrayCommand(self, array, command):
        commandsArray = self._cGetCommandsArray(array)
        if command in commandsArray:
            index = commandsArray.index(command)
            for i in range(index+1, len(commandsArray)):
                self.cExec(f"{array}({i-1}) = \"{commandsArray[i]}\"")
            if len(commandsArray) > 1:
                self.cExec(f"ReDim Preserve {array}({len(commandsArray)-2})")
            else:
                self.cExec(f"{array}({index}) = \"\"")
            return True

        return False

    def cGetRecoveryCommandsArray(self):
        return self._cGetCommandsArray("recoveryCommandsArray")
    def cAddRecoveryCommand(self, recoveryCommand):
        return self._cAddArrayCommand("recoveryCommandsArray", recoveryCommand)
    def cAddRecoveryCommandFirst(self, recoveryCommand):
        return self._cAddArrayCommandFirst("recoveryCommandsArray", recoveryCommand)
    def cRemoveRecoveryCommand(self, recoveryCommand):
        return self._cRemoveArrayCommand("recoveryCommandsArray", recoveryCommand)

    def cGetExitCommandsArray(self):
        return self._cGetCommandsArray("exitCommandsArray")
    def cAddExitCommand(self, exitCommand):
        return self._cAddArrayCommand("exitCommandsArray", exitCommand)
    def cAddExitCommandFirst(self, exitCommand):
        return self._cAddArrayCommandFirst("exitCommandsArray", exitCommand)
    def cRemoveExitCommand(self, exitCommand):
        return self._cRemoveArrayCommand("exitCommandsArray", exitCommand)

    # Context managers

    def __enter__(self):
        if not self.has_healthy_interpreter():
            self.createInterpreter()
        return self

    def __exit__(self, _type, _value, _traceback):
        if self.has_healthy_interpreter():
            self.destroyInterpreter()
