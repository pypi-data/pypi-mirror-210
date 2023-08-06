from VBW.VBCore.VBWrapperBase import VB_WRAPPER_BASE
from VBW.VBCore.VBObjectWrapper import VB_OBJECT_WRAPPER
import glob
from VBW.VBWrappers.VBWrapperShell import VB_WRAPPER_SHELL, VB_WRAPPER_SHELL2
from VBW.VBWrappers.VBWrapperSimpleExcel import VB_WRAPPER_SIMPLE_EXCEL
from VBW.VBWrappers.VBWrapperComplexExcel import *

##1

# Count the ammount of Excel files that have a "max_sheet" sheet




#
# return ammount_of_excels_with_max_sheet


##2


if __name__ == "__main__":
    with VB_WRAPPER_BASE(silenceExceptions=False) as shell:
        print(shell.cExec("Set x = CreateObject(\"Excel.Application\")", printing=False))

    ammount_of_excels_with_sheets_named_barkeep = 0

    for excelFile in glob.glob("excel/*.xlsx"):
        filepath = os.path.join(os.path.split(os.path.realpath(__file__))[0], excelFile)
        with VB_OBJECT_WRAPPER.start_with("Excel.Application", silenceExceptions=False) as shell:
            shell.cExec(f"Set objWorkbook = {shell.objects[0]}.Workbooks.Open(\"{filepath}\") ")
            shell.cAddExitCommand("objWorkbook.close")
            n = int(shell.cEval("objWorkbook.Sheets.count", printing=False))
            names = [shell.cEval(f"objWorkbook.Sheets({i}).Name", printing=False) for i in range(1, n + 1)]
            if "barkeep" in names:
                ammount_of_excels_with_sheets_named_barkeep += 1

    print(ammount_of_excels_with_sheets_named_barkeep)

    #with VB_OBJECT_WRAPPER.start_with("Excel.Application") as shell:
    #    print(shell.cEval("1", printing=False))

    if False:
        wrapper = VB_WRAPPER_COMPLEX_EXCEL(silenceExceptions=False)
        wrapper.createInterpreter()
        book = VWCE_WORKBOOK(wrapper, "a.xlsx")
        book.load()
        wrapper.cExec(f"""Set t1 = WORKBOOK_FILE_WITH_ID_1.Sheets(2)""", printing = True)
        wrapper.cExec(f"""Set t2 = t1.Cells.Item({1},{2})""", printing = True)
        wrapper.cEval(f"""t1.Name""", printing = True)
        wrapper.cExec(f"""t2.Value = 15""", printing = True)
        wrapper.cExec("""WORKBOOK_FILE_WITH_ID_1.Activate""")
        wrapper.cExec("""WORKBOOK_FILE_WITH_ID_1.Save""")
        #wrapper.cEval(f"""WORKBOOK_FILE_WITH_ID_1.Sheets(1).Cells({1},{2}).Value""", printing = True)
        #wrapper.cExec(f"""wscript.echo 1""", printing=True)
        #wrapper.cExec(f"""WORKBOOK_FILE_WITH_ID_1.Sheets(\"{"Hoja2"}\").Cells({1},{2}).Value = 12223""", printing = True)
        #print(*map(lambda k:k._name, book.sheets))
        #print(VWCE_CELL(book.sheets[1],2,2).value)

    if False:
        wrapper.setFile("a.xlsx")
        wrapper.createInterpreter()
        print("x")
        wrapper.cGetCellValue(1,1)
        wrapper.cGetCellValue(2,1)
        wrapper.cGetCellValue(1,2)
        wrapper.cGetCellValue(3,3)
        wrapper.cGetCellValue(5,3)
        wrapper.cRefreshAll()
        wrapper.cSaveFile()
        print("y")

    if False:
        #wrapper.cGetSheets()
        wrapper.cGetRecoveryCommandsArray()
        wrapper.cAddRecoveryCommand("A")
        wrapper.cAddRecoveryCommand("B")
        wrapper.cAddRecoveryCommand("C")
        wrapper.cAddRecoveryCommand("D")
        wrapper.cAddRecoveryCommand("E")
        wrapper.cGetRecoveryCommandsArray()
        wrapper.cRemoveRecoveryCommand("A")
        wrapper.cRemoveRecoveryCommand("C")
        wrapper.cGetRecoveryCommandsArray()
        wrapper.cEval("a")