from VBW.VBCore.VBWrapperBase import VB_WRAPPER_BASE


class VB_OBJECT_WRAPPER(VB_WRAPPER_BASE):

    def __init__(self, path2CScript=None, path2InterpreterScript=None, silenceExceptions=True,
                 default_startup_commands=None):
        super().__init__(path2CScript, path2InterpreterScript, silenceExceptions, default_startup_commands)
        self.dynamic_counter = 0
        self.objects = []

    @classmethod
    def start_with(cls, *objects, path2CScript=None, path2InterpreterScript=None,
                     silenceExceptions=True, default_startup_commands=None):
        instance = VB_OBJECT_WRAPPER(path2CScript,path2InterpreterScript, silenceExceptions, default_startup_commands)
        instance.createInterpreter()
        for _object in objects:
            name = instance.create_dynamic_object(_object)
            instance.objects.append(name)
        return instance

    def create_dynamic_object(self, _object):
        dynamic_object = "dynamicObject{}".format(self.dynamic_counter)
        self.dynamic_counter += 1

        create_command = "Set {} = CreateObject(\"{}\")".format(dynamic_object, _object)
        quit_command = "{}.Quit".format(dynamic_object)

        self.cExec(create_command)
        self.cAddExitCommand(quit_command)
        self.cAddRecoveryCommand(quit_command)

        return dynamic_object
