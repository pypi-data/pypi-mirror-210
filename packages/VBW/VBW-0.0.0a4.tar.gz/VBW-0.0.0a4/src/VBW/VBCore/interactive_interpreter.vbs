''''''''''' CONFIGURATION
'''''''''''''''''

WScript.StdIn.Read(0)
if NOT WScript.Arguments.Named.Exists("NoErrorHandling") then
    On Error Resume Next
end if

''''''''''' FUNCTIONS
'''''''''''''''''

' INTERPRET A SINGLE LINE
Function ParseLine (inputStr)
    inputStrLCase = LCase(inputStr)
    ' EXIT PROGRAM
    if inputStrLCase = "'e" then
        continueRun = False
    else
        ' EXECUTE
        if Right("  " & inputStrLCase,2) = "'x" then
            inputStrCommand = Left(inputStr, len(inputStr) - 2)
            Execute(inputStrCommand)
            wscript.echo inputStrCommand
        ' EVALUATE
        else
           wscript.echo Eval(inputStr)
        end if
        continueRun = True
    end if
    ' RETURN
        ParseLine = continueRun
End Function

' RECOVERY FUNCTION
ReDim recoveryCommandsArray(0)
recoveryCommandsArray(0) = ""
Function recoverFromError(errorNumber)
    continueRunningAfterRecovery = False
    x = UBound(recoveryCommandsArray)
    while x >= 0
        Execute(recoveryCommandsArray(x))
        x = x - 1
    wend
    if continueRunningAfterRecovery then
        wscript.echo "!>!>!>ERROR" & errorNumber
    else
        wscript.echo "!>!>!>ERROR"
        wscript.echo errorNumber
    end if
    ' RETURN
    recoverFromError = continueRunningAfterRecovery
End Function

' EXIT ARRAY
ReDim exitCommandsArray(0)
exitCommandsArray(0) = ""
Sub runExitArray()
    x = UBound(exitCommandsArray)
    while x >= 0
        Execute(exitCommandsArray(x))
        x = x - 1
    wend
End Sub

''''''''''' INTERPRETERS
'''''''''''''''''

' INTERACTIVE INTERPRETER
Sub interactiveInterpreter
    continueLoop = True
    While continueLoop
        inputStr = rtrim(WScript.StdIn.ReadLine())
        continueLoop = ParseLine(inputStr)
    wend
    runExitArray()
    wscript.echo "!>!>!>END"
End Sub

' FILE INTERPRETER
Sub fileInterpreter(fileWithCodePath)
    wscript.echo fileWithCodePath

    Set fso = CreateObject("Scripting.FileSystemObject")
    Set inputFile = fso.OpenTextFile (fileWithCodePath, 1)
    Do Until inputFile.AtEndOfStream
        debuggingCommandStr = trim(inputFile.Readline)
        wscript.echo debuggingCommandStr
        ignoredContinueLoop = ParseLine(inputStr)
    Loop
    inputFile.Close
End Sub

'''''''''' MAIN
'''''''''''''''''

doInteractiveRun = True


' FILE RUN
if WScript.Arguments.Unnamed.Count >= 1 then
    fileInterpreter(WScript.Arguments.Item(0))
    if Err.Number <> 0 then
        doInteractiveRun = False
        wscript.echo "!>!>!>ERROR"
        wscript.echo Err.Number
    else
        if WScript.Arguments.Named.Exists("EndAfterFile") then
            recoverFromError(0)
            doInteractiveRun = False
        end if
    end if
end if

' INTERACTIVE INTERPRETER RUN
while doInteractiveRun
    doInteractiveRun = False
    interactiveInterpreter()
    if Err.Number <> 0 then
        doInteractiveRun = recoverFromError(Err.Number)
    end if
wend
