import copy

class equation():
    def __init__(self, operand, operations = None):
        self.operand = operand
        self.operations = operations

    def __str__(self):
        out =  "Operand : " + self.operand +'\n'
        out += "Operations :" + ','.join(self.operations)
        return out


    def __eq__(self, other):
        if self.operand != other.operand:
            print " "*8,
            print "Operand mismatch :",self.operand, " != ",other.operand
        if self.operations != other.operations:
            print " "*8,
            print "Operations mismatch for operand:", self.operand, '(',\
                len(self.operations), ') != ', other.operand,' (',len(other.operations),')'
        return self.operand == other.operand and self.operations == other.operations

class ocamlOutputFile():
    def __init__(self, filename, verbose=False):
        self.filename = filename
        self.verbose = verbose
        self.eqList = []

    def parseFile(self):
        f = open(self.filename, 'r')
        contents = f.read()
        f.close()
        contents = contents.split('\n')

        for line in contents:

            if line.startswith('[EQLIST]'):
                self.eqList.append([])
                line = line.split()
                line = ' '.join(line[1:])

            if line.strip().startswith('EQL->'):
                line = line.split()
                if line[0] == 'EQL->':
                    temp = line[1].split(':')
                    operand = temp[0][1:]
                    operations = temp[1].split(',')
                    operations[-1] = operations[-1][:-1]
                    eq = equation(operand=operand, operations=operations)
                    self.eqList[-1].append(eq)


class subSumptionClass():
    def __init__(self, filename, verbose=False):
        self.filename = filename
        self.verbose = verbose
        self.eqList = []

    def parseFile(self):
        f = open(self.filename, 'r')
        contents = f.read()
        f.close()
        contents = contents.split('\n')

        for line in contents:

            if line.startswith('**[SSO]'):
                self.eqList.append([])
                line = line.split()
                line = ' '.join(line[1:])
                #print "SSO line: ", line
                temp = line.split(':')
                operand = temp[0][1:]
                operations = temp[1].split(',')
                operations[-1] = operations[-1][:-1]
                eq = equation(operand=operand, operations=operations)
                self.eqList[-1].append(eq)

            if line.strip().startswith('-> [Subsumes]'):
                line = line.split()
                line = ' '.join(line[1:])
                line = line.split()
                if line[0] == '[Subsumes]':
                    temp = line[1].split(':')
                    operand = temp[0][1:]
                    operations = temp[1].split(',')
                    operations[-1] = operations[-1][:-1]
                    eq = equation(operand=operand, operations=operations)
                    self.eqList[-1].append(eq)



class hook():
    def __init__(self, hookName, secSensitiveOper=[]):
        self.hookName = hookName
        self.secSensitiveOper = secSensitiveOper

class function():
    def __init__(self, functionName, hook=[]):
        self.functionName = functionName
        self.hook = hook

class ocamlFunctionFile():
    def __init__(self, filename, verbose = False):
        self.filename = filename
        self.verbose = verbose
        self.functions = []

    def parseFile(self):
        f = open(self.filename, 'r')
        contents = f.read()
        f.close()
        contents = contents.split('\n')

        for line in contents:
            if line.strip().startswith('Function'):
                name = line.split()
                name = line[0].split(':')[1][1:-1]
                self.functions.append(function(functionName=name))

            if line.split()[1] == 'Hook':
                line = line.split()
                if line[0] == 'EQL->':
                    temp = line[1].split(':')
                    operand = temp[0]
                    operations = temp[1].split(',')
                    eq = equation(operand=operand, operations=operations)
                    self.eqList[-1].append(eq)

class AutoHook():
    def __init__(self, hook, fileName, line,stmt=None):
        self.hook = hook
        self.fileName = fileName
        self.line = line
        self.ifStmt = False
        self.stmt = stmt
        self.SSOs = []
        self.domHooks = []

    # def __eq__(self, other):
    #
    #     selfOperands = [s.operand for s in self.SSOs]
    #     otherOperands = [s.operand for s in other.SSOs]
    #
    #     for operand in selfOperands:
    #         if operand not in otherOperands:
    #             print " "*8,
    #             print "Operand Removed:", operand
    #     for operand in otherOperands:
    #         if operand not in selfOperands:
    #             print " "*8,
    #             print "Operand Added:", operand
    #
    #     ssoMatch = self.SSOs == other.SSOs
    #
    #     return ssoMatch #and self.domHooks == other.domHooks


class ManualHook():
    def __init__(self, hook, fileName, line):
        self.hook = hook
        self.fileName = fileName
        self.line = line
        self.Autohooks = []

    def __eq__(self, other):
        return self.hook == other.hook and self.fileName == other.fileName

class ocamlMaualHooks():
    def __init__(self, filename, verbose=False):
        self.filename = filename
        self.verbose = verbose
        self.ManHooks = []
        self.unmediatedHooks = []
        self.fileMap ={}

    def createFilemap(self):
        manHooks = []
        for hook in self.ManHooks:
            try:
                self.fileMap[hook.fileName]
            except KeyError:
                self.fileMap[hook.fileName] = []
            self.fileMap[hook.fileName].append(hook)

            #self.fileMap[hook.fileName].append(hook)

        for fileHooks in self.fileMap:
            hooks = self.fileMap[fileHooks]
            hooks = hooks.sort(key=lambda x: int(x.line), reverse=False)
            #self.fileMap[fileHooks] = hooks



    def parseFile(self):
        f = open(self.filename, 'r')
        contents = f.read()
        f.close()
        contents = contents.split('\n')
        isDom = False
        Autohooklist = []
        for line in contents:

            #print len(Autohooklist)
            if line.startswith('[ManualHook]'):
                Autohooklist = []
                #self.ManHooks.append([])
                line = line.split()
                hookCall = line[2].split('@')[0]
                filename = line[4].split('@')[0]
                lineNumber = line[4].split('@')[1]
                ManHook = ManualHook(hook=hookCall,fileName=filename,line=lineNumber)
                self.ManHooks.append(ManHook)
                #print line
                line = ' '.join(line[1:])
                #print "Manual Hook: ", line

            if line.strip().startswith('[AutoHook]'):
                isDom = False
                line = line.split()
                hookCall = line[1]
                filename = line[3].split('@')[0]
                lineNumber = line[3].split('@')[1]
                if hookCall.startswith('stm'):
                    stmt = line[5]
                    ahook = AutoHook(hookCall,filename,lineNumber,stmt)
                else:
                    ahook = AutoHook(hookCall, filename, lineNumber)
                self.ManHooks[len(self.ManHooks) - 1].Autohooks.append(ahook)
                #Autohooklist.append(ahook)
                # if line[0] == '[AutoHook]':
                #     print "Auto hook: ", line
                line = ' '.join(line[1:])

            if line.strip().startswith('[SSO]'):
                line = line.split()
                temp = line[1].split(':')
                operand = temp[0]
                operations = temp[1].split(',')
                eq = equation(operand=operand, operations=operations)
                line = ' '.join(line[1:])
                manHooklength = len(self.ManHooks)
                hooklength = len(self.ManHooks[manHooklength - 1].Autohooks)
                domLength = len(self.ManHooks[manHooklength - 1].Autohooks[hooklength-1].domHooks)
                if(isDom):
                    self.ManHooks[manHooklength - 1].Autohooks[hooklength - 1].domHooks[domLength-1].SSOs.append(eq)
                else:
                    self.ManHooks[manHooklength - 1].Autohooks[hooklength-1].SSOs.append(eq)

            if line.strip().startswith('- [Dom]'):
                isDom = True
                line = line.split()
                manHooklength = len(self.ManHooks)
                hooklength = len(self.ManHooks[manHooklength - 1].Autohooks)
                hookCall = line[2]
                filename = line[4].split('@')[0]
                lineNumber = line[4].split('@')[1]
                if hookCall.startswith('stm'):
                    stmt = line[5]
                    ahook = AutoHook(hookCall, filename, lineNumber, stmt)
                else:
                    ahook = AutoHook(hookCall, filename, lineNumber)
                self.ManHooks[len(self.ManHooks) - 1].Autohooks[hooklength-1].domHooks.append(ahook)
                line = ' '.join(line[1:])

            if line.strip().startswith('[Unmediated Hook]'):
                line = line.split()
                #print line
                hookName = line[2]
                fileName = line[4].split('@')[0]
                lineNumber = line[4].split('@')[1]
                if hookName.startswith('Stm'):
                    stmt = line[6].split('@')[0]
                    ahook = AutoHook(hookName, fileName, lineNumber, stmt)
                    ahook.ifStmt = True
                else:
                    ahook = AutoHook(hookName, fileName, lineNumber)
                self.unmediatedHooks.append(ahook)
        self.createFilemap()




class ocamlAutoHooks():
    def __init__(self, filename, verbose=False):
        self.filename = filename
        self.verbose = verbose
        self.eqList = []

    def parseFile(self):
        f = open(self.filename, 'r')
        contents = f.read()
        f.close()
        contents = contents.split('\n')

        for line in contents:

            if line.startswith('[EQLIST]'):
                self.eqList.append([])
                line = line.split()
                line = ' '.join(line[1:])

            if line.strip().startswith('EQL->'):
                line = line.split()
                if line[0] == 'EQL->':
                    temp = line[1].split(':')
                    operand = temp[0][1:]
                    operations = temp[1].split(',')
                    operations[-1] = operations[-1][:-1]
                    eq = equation(operand=operand, operations=operations)
                    self.eqList[-1].append(eq)



if __name__ == '__main__':
    file1 = '../server13_ifiles/results/OUT-MHOOK-AHOOK1.txt'
    o = ocamlMaualHooks(filename=file1)
    o.parseFile()

    # print "Man Hooks : ", len(o.ManHooks)
    # for manHook in o.ManHooks:
    #     #print manHook
    #     print manHook.hook, manHook.fileName, manHook.line
    #     print len(manHook.Autohooks)
    #     for hook in manHook.Autohooks:
    #         print hook.hook, hook.fileName, hook.line
    #         print "SSO :",len(hook.SSOs)
    #
    # print "Unmediated Hooks : ", len(o.unmediatedHooks)
        #print manHook.hook, manHook.fileName, manHook.line
        #print "Dominated Autohooks :",len(manHook.Autohooks)
        #print manHook.Autohooks


    # print "Number of lists :", len(o.eqList)
    # for i in range(len(o.eqList)):
    #     print "List Number ", i
    #     print "Equations :", len(o.eqList[i])