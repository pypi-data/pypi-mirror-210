import os
from VBW.VBCore.VBWrapperBase import VB_WRAPPER_BASE

class VB_WRAPPER_SIMPLE_EXCEL(VB_WRAPPER_BASE):

    def __init__(self, path2CScript = None, path2InterpreterScript = None, silenceExceptions = True):
            self.fileLoaded = False
            super().__init__(path2CScript, path2InterpreterScript, silenceExceptions)

    def interpreterInitialization(self, startup_commands=None):
        super().interpreterInitialization([] if startup_commands is None else startup_commands)
        self.cLoadApp()
        self.cLoadFile()

    def setFile(self,filepath, relative = True):
        self.filepath = os.path.join(os.path.split(os.path.realpath(__file__))[0],filepath) if relative else filepath

    def cLoadApp(self):
        self.cExec("""Set objExcel = CreateObject("Excel.Application")""")
        self.cAddRecoveryCommand("""objExcel.Quit""")

    def cLoadFile(self):
        assert self.filepath is not None
        assert os.path.exists(self.filepath)
        assert not self.fileLoaded
        self.cExec(f"""Set objWorkbook = objExcel.Workbooks.Open("{self.filepath}")""")
        self.fileLoaded = True

    def cUnloadFile(self):
        assert self.fileLoaded
        self.cExec("""objWorkbook.close""")
        self.fileLoaded = False

    def cSaveFile(self):
        assert self.fileLoaded
        self.cExec("""objWorkbook.save""")

    def cGetActiveSheet(self):
        assert self.fileLoaded
        return self.cEval("""objWorkbook.ActiveSheet.Name""")

    def cActiveSheet(self, newActive):
        assert self.fileLoaded
        return self.cExec(f"""objWorkbook.Sheets("{newActive}").Activate""")

    def cGetSheets(self):
        assert self.fileLoaded
        n = int(self.cEval("""objWorkbook.Sheets.count"""))
        l = [self.cEval(f"""objWorkbook.Sheets({i}).Name""") for i in range(1,n+1)]
        return l

    def cGetCellValue(self,y,x):
        assert self.fileLoaded
        return self.cEval(f"""objWorkbook.ActiveSheet.Cells({y},{x})""")

    def cSetCellValue(self,y,x,value):
        assert self.fileLoaded
        return self.cExec(f"""objWorkbook.ActiveSheet.Cells({y},{x}) = "{value}" """)

    def cRefreshAll(self):
        assert self.fileLoaded
        return self.cExec(f"""objWorkbook.RefreshAll()""")

    def cExit(self):
        if self.fileLoaded:
            self.cUnloadFile()
        self.cExec("""objExcel.Quit""")
        self.cRemoveRecoveryCommand("""objExcel.Quit""")
        super().cExit()