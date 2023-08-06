import os
from VBW.VBCore.VBWrapperBase import VB_WRAPPER_BASE

"""WIP, please use simpleExcel instead"""

class VWCE_OBJECT():
    pass
    #def __init__(self,VWCE=None):
    #    self.VWCE = VWCE

    #def notLinkedToExcel(self):
    #    return self.VWCE is None

class VWCE_WORKBOOK(VWCE_OBJECT):
    ID_COUNTER = 1
    def __init__(self,VWCE, filepath):
        self.VWCE = VWCE
        self._VWCE_ID = f"WORKBOOK_FILE_WITH_ID_{VWCE_WORKBOOK.ID_COUNTER}"
        VWCE_WORKBOOK.ID_COUNTER += 1
        self._filepath = filepath
        self._loaded = False
        self._worksheets = []

    def notLinkedToExcel(self):
        return self.VWCE is None or not self._loaded

    def load(self):
        assert not self.VWCE is None
        assert not self._loaded
        self.VWCE.cLoadFile(self._VWCE_ID, self._filepath)
        self._loaded = True

    @property
    def sheets(self):
        if self.notLinkedToExcel() or not self._loaded:
            return self._worksheets
        else:
            return [VWCE_WORKSHEET(self, name) for name in self.VWCE.cGetSheetNames(self._VWCE_ID)]


class VWCE_WORKSHEET(VWCE_OBJECT):
    def __init__(self,book,name):
        self._book = book
        self._name = name
        self._cells = []
        self._ranges = []

    def notLinkedToExcel(self):
        return self._book is None or self._book.notLinkedToExcel()


class VWCE_RANGE(VWCE_OBJECT):
    pass

class VWCE_CELL(VWCE_OBJECT):
    def __init__(self,sheet,y,x):
        self._x = x
        self._y = y
        self._sheet = sheet
        self._value = 0

    def notLinkedToExcel(self):
        return self._sheet is None or self._sheet.notLinkedToExcel()

    @property
    def value(self):
        if self.notLinkedToExcel():
            return self._value
        else:
            print("X")
            return self._sheet._book.VWCE.cGetCellValue(self._y,self._x,self._sheet)
    


class VB_WRAPPER_COMPLEX_EXCEL(VB_WRAPPER_BASE):

    def __init__(self, path2CScript = None, path2InterpreterScript = None, silenceExceptions = True):
            self.fileLoaded = []
            super().__init__(path2CScript, path2InterpreterScript, silenceExceptions)

    def interpreterInitialization(self, startup_commands=None):
        super().interpreterInitialization(startup_commands)
        self.cLoadApp()

    def cLoadApp(self):
        self.cExec("""Set objExcel = CreateObject("Excel.Application")""")
        self.cAddRecoveryCommand("""objExcel.Quit""")

    def cLoadFile(self, fileid, filepath):
        assert os.path.exists(filepath)
        self.cExec(f"""Set {fileid} = objExcel.Workbooks.Open("{filepath}")""")
        self.cAddRecoveryCommandFirst("f""{fileid}.close""")

    #def cSaveFile(self):
    #    assert self.fileLoaded
    #    self.cExec("""objWorkbook.save""")

    def cGetSheetNames(self,fileid):
        count = self.cEval(f"""{fileid}.Sheets.Count""", printing=False)
        #name = self.cEval(f"""{fileid}.Sheets({str(1)}).name""", printing=False)
        #self.cEval(f"""{fileid}.Sheets(\"{name}\").name""")
        return [self.cEval(f"""{fileid}.Sheets({str(i)}).name""", printing=False) for i in range(1,int(count)+1)]
        #return i

#    def cActiveSheet(self, newActive):
#        assert self.fileLoaded
#        return self.cExec(f"""objWorkbook.Sheets("{newActive}").Activate""")

#    def cGetSheetNames(self):
#        assert self.fileLoaded
#        n = int(self.cEval("""objWorkbook.Sheets.count"""))
#        l = [self.cEval(f"""objWorkbook.Sheets({i}).Name""") for i in range(1,n+1)]
#        return l

    def cGetCellValue(self,y,x,worksheet):
        workbook = worksheet._book 
        return self.cEval(f"""{workbook._VWCE_ID}.Sheets(\"{worksheet._name}\").Cells({y},{x}).Value""", printing=True)

#    def cSetCellValue(self,y,x,value):
#        assert self.fileLoaded
#        return self.cExec(f"""objWorkbook.ActiveSheet.Cells({y},{x}) = "{value}" """)

#    def cRefreshAll(self):
#        assert self.fileLoaded
#        return self.cExec(f"""objWorkbook.RefreshAll()""")

#    def cExit(self):
#        self.cExec("""objExcel.Quit""")
#        self.cRemoveRecoveryCommand("""objExcel.Quit""")
#        super().cExit()