from . import utils,Sobjects

def setTimes(context,line,obj=None,field=None,value=None,chunkNum=None,type=None):
    def addList(obj,field,val):
        if field in obj:
            obj[field].append(val)
        else:
            obj[field] = [val]

    chunks = line.split('|')

    if obj == None:
        obj = {
            'type' : type,
            'ident' : context['ident'],
            'exception' :False
        }
       
        if len(chunks)>3:  obj['Id'] = chunks[3]

    addList(obj,'lines',line)
    addList(obj,'CPUTime',context['DEF:CPU time'])
    addList(obj,'SOQLQueries',context['DEF:SOQL queries'])
    addList(obj,'cmtCPUTime',context['CMT:CPU time'])
    addList(obj,'cmtSOQLQueries',context['CMT:SOQL queries'])
    addList(obj,'totalQueries',context['totalQueries'])
    addList(obj,'time',chunks[0].split(' ')[0])

    limits = {}
    for key in context['LU'].keys():
        limits[key] = len(context['LU'][key])-1
    addList(obj,'LU',limits)

    if len(chunks)>1:  addList(obj,'timeStamp',int ((chunks[0].split('(')[1]).split(')')[0]))
    else:  addList(obj,'timeStamp',0)

    if obj['type'] is None:
        print()

    if field is not None:  obj[field] = chunks[chunkNum] if value is None else value

    if context['timeZero'] == 0:  context['timeZero'] = obj['timeStamp'][0]

    obj['elapsedTime'] = obj['timeStamp'][0] #- _context['timeZero']

    return obj

def append_and_increaseIdent(context,obj,increase=True):
    context['openItemsList'].append(obj)
    if increase == True: context['ident'] = context['ident'] + 1
    context['parsedLines'].append(obj)

def decreaseIdent_pop_setFields(context,type,value,key='key',endsWith=None,decrease=True):
    obj = popFromList(context,type=type,key=key,value=value,endsWith=endsWith)
    if obj == None:
        a=1
    else:
        if decrease == True:   context['ident'] = obj['ident']
        setTimes(context,context['line'],obj)
    return obj

def getFromDebugList(context,values):
    for line in reversed(context['parsedLines']):
        for key in values.keys():
            if key not in line:
                break
            if line[key]!=values[key]:
                break
        return line
    return None    

def popFromList(context,type,value,key='key',endsWith=False):
    openItemsList = context['openItemsList']
    try:
        #for i,obj in enumerate(openItemsList):

        for i,obj in reversed(list(enumerate(openItemsList))):
            if obj['type'] == type:
                if endsWith == True:
                    if key not in obj:      continue
                    if obj[key].endswith(value) or obj[key].startswith(value):
                        openItemsList.pop(i)
                        return obj    
                else:
                    if key not in obj:     continue
                    if obj[key] == value:
                        openItemsList.pop(i)
                        return obj
    except Exception as e:    print(e) 

    return None           

def getFromList(theList,field,value,endsWith=False,delete=True,startsWith=False):
    try:
        rvs = theList
        for i,obj in reversed(list(enumerate(rvs))):
            if field in obj:
                if startsWith == True:
                    if obj[field].startswith(value):
                        if delete == True:
                            rvs.pop(i)
                        return obj    
                if endsWith == True:
                    if obj[field].endswith(value):
                        if delete == True:
                            rvs.pop(i)
                        return obj    
                else:
                    if obj[field] == value:
                        if delete==True:
                            rvs.pop(i)
                        return obj
    except Exception as e:
        print(e) 
    return None

def is_in_operation(context,text,contains=False):
    if context['chunks_lenght']<2: return False
    if contains and text in context['chunks'][1]: return True
    elif context['chunks'][1] == text: return True
    return False

def create_LU_limits():
  LU = {
    'SOQL queries': {'v': 0},
    'query rows': {'v': 0},
    'SOSL queries': {'v': 0},
    'DML statements': {'v': 0},
    'Publish Immediate DML': {'v': 0},
    'DML rows': {'v': 0},
    'CPU time': {'v': 0},
    'heap size': {'v': 0},
    'callouts': {'v': 0},
    'Email Invocations': {'v': 0},
    'future calls': {'v': 0},
    'queueable jobs added to the queue': {'v': 0},
    'Mobile Apex push calls': {'v': 0}
  }
  return LU

def append_LU_default(context,limit,value,package='(default)'):
  #  package = '(default)'

    if package not in context['LU']:
        context['LU'][package] = []
    if len(context['LU'][package])>0:
        if len(context['LU'][package]) == 152:
            a=1
        limits = context['LU'][package][-1].copy()
    else:
        limits = create_LU_limits()
    limits[limit] = {'v':value}
    context['LU'][package].append(limits)

def parseWfRule(context):
    line = context['line']
    chunks = context['chunks'] 

    if is_in_operation(context,'WF_RULE_EVAL',contains=True):
        if 'BEGIN' in chunks[1]:
            obj = setTimes(context,line,field='output',value='Workflow',type='RULE_EVAL')
            append_and_increaseIdent(context,obj)
            return True

        if 'END' in chunks[1]:
            decreaseIdent_pop_setFields(context,type='RULE_EVAL',key='output',value='Workflow')
            return True

    if is_in_operation(context,'WF_CRITERIA',contains=True):
        if 'BEGIN' in chunks[1]:
            obj = setTimes(context,line,type='WF_CRITERIA')

            colon_split=chunks[2].split(':')
            colon_space = colon_split[1].strip().split(' ')
            obj['ObjectName'] = colon_split[0][1:]
            obj['RecordName'] = colon_space[0]
            if len(colon_space)>1:
                obj['RecordID'] = colon_space[1]
            else:
                obj['RecordID'] = ""

            obj['rulename'] = chunks[3]
            obj['rulenameId'] = chunks[4]
            obj['output'] = obj['rulename']

            append_and_increaseIdent(context,obj)
            return True

        if 'END' in chunks[1]:
            obj =decreaseIdent_pop_setFields(context,type='WF_CRITERIA',key='type',value='WF_CRITERIA')   
            obj['result'] = chunks[2]
            obj['output'] = f"{obj['ObjectName']}: {obj['rulename']} --> {obj['result']}"
            return True
  
    if is_in_operation(context,'WF_RULE_NOT_EVALUATED'):
        obj =decreaseIdent_pop_setFields(context,type='WF_CRITERIA',key='type',value='WF_CRITERIA')   
        obj['output'] = f"{obj['rulename']} --> Rule Not Evaluated"
        return True

    if is_in_operation(context,'WF_ACTION'):
        obj = getFromList(context['openItemsList'],'output','Workflow',delete=False)
        obj['action'] = chunks[2]
        return True

def parseExceptionThrown(context):
    line = context['line']
    chunks = context['chunks']

  #  if context['chunks_lenght']>1 and chunks[1] == 'EXCEPTION_THROWN':
    if is_in_operation(context,'EXCEPTION_THROWN'):
        obj = setTimes(context,line,type='EXCEPTION',field='output',value=chunks[3])
        context['exception'] = True
        context['exception_msg'] = obj['output']

        context['parsedLines'].append(obj)
        context['file_exception'] = True
        next = 1
        nextline = context['lines'][context['line_index']+next]
        while '|' not in nextline:
            if nextline != '':
                obj = context['parsedLines'][-1].copy()
                context['parsedLines'].append(obj)
                obj['output'] = nextline
            next = next + 1
            nextline = context['lines'][context['line_index']+next]
        return True

    if is_in_operation(context,'FATAL_ERROR'):
   # if context['chunks_lenght']>1 and chunks[1] == 'FATAL_ERROR':
        obj = setTimes(context,line,type='EXCEPTION',field='output',value=chunks[2])
        context['exception'] = True
        context['exception_msg'] = obj['output']

        context['parsedLines'].append(obj)
        context['file_exception'] = True
        next = 1
        nextline = context['lines'][context['line_index']+next]
        while '|' not in nextline:
            if nextline != '':
                obj = context['parsedLines'][-1].copy()
                context['parsedLines'].append(obj)
                obj['output'] = nextline
            next = next + 1
            nextline = context['lines'][context['line_index']+next]
        return True

    return False

def parseUserDebug(context):
    line = context['line']
    chunks = context['chunks']

    if is_in_operation(context,'USER_DEBUG'):
        obj = setTimes(context,line,type='DEBUG')
        obj['timeStamp'].append(obj['timeStamp'][0])
        obj['type'] = 'DEBUG'
        obj['subType'] = chunks[3]
        obj['output'] = chunks[4]
        if obj['subType'] == 'ERROR':
            context['exception'] = True
            context['exception_msg'] = obj['output']
        obj['apexline'] = chunks[2][1:-1]
        context['parsedLines'].append(obj)
        if context['line_index']<(len(context['lines'])-1):
            next = 1
            nextline = context['lines'][context['line_index']+next]
            while '|' not in nextline:
                obj = context['parsedLines'][-1].copy()
                context['parsedLines'].append(obj)
                obj['output'] = nextline
                next = next + 1
                nextline = context['lines'][context['line_index']+next]
        if  obj['output'].startswith('*** '):
            def add_to_LU(string,limit):
                if obj['output'].startswith(string):
                    chs = chunks[4].split(' ')
                    append_LU_default(context,limit,chs[4])
                    return True
                return False

            if  add_to_LU('*** getCpuTime() ***','CPU time'): return True
            if  add_to_LU('*** getQueries() ***','SOQL queries'): return True
            if  add_to_LU('*** getQueryRows() ***','query rows'): return True
            if  add_to_LU('*** getDmlStatements() ***','DML statements'): return True
            if  add_to_LU('*** getDmlRows() ***','DML rows'): return True

        if  obj['output'].startswith('CPU Time:'):
            chs = chunks[4].split(' ')
            context[f'DEF:CPU time'] = chs[2]  
            append_LU_default(context,'CPU time',chs[2])
        if obj['output'].startswith('CPQCustomHookImplementation'):
            if obj['output'].endswith('PreInvoke'):
                context['CPQCustomHookImplementation'] = 'Started'
            if obj['output'].endswith('PostInvoke'):
                context['CPQCustomHookImplementation'] = 'Finished'

        return True

    return False

def parse_limit_usage(context):
    line = context['line']
    chunks = context['chunks']   
    if is_in_operation(context,'CUMULATIVE_LIMIT_USAGE') or is_in_operation(context,'CUMULATIVE_LIMIT_USAGE_END'):
        context['TESTING_LIMITS'] = False

    if is_in_operation(context,'TESTING_LIMITS'):
        context['TESTING_LIMITS'] = True

    if is_in_operation(context,'LIMIT_USAGE_FOR_NS'):
        if 'TESTING_LIMITS' in context and context['TESTING_LIMITS'] == True: 
            return
        obj = setTimes(context,line,type='LU')
        package = chunks[2]
  #      if 'TESTING_LIMITS' in context and context['TESTING_LIMITS'] == True: 
  #          package = 'test-'+package
        if package not in context['LU']:context['LU'][package]=[]
        next = 1
        nextline = context['lines'][context['line_index']+next]
        limits = {}
        while '|' not in nextline:
            if 'out of' in nextline:
                sp1 = nextline.split(':')
                limit = sp1[0].strip()
                if 'Number of' in limit: limit = limit.split('Number of ')[1]
                else: limit = limit.split('Maximum ')[1]
                sp2 = sp1[1].strip().split(' ')

                limits[limit] = {'v':int(sp2[0]),'m':int(sp2[3])}
            next = next + 1
            nextline = context['lines'][context['line_index']+next]
        context['LU'][package].append(limits)

def parseLimits(context):
    line = context['line']
    chunks = context['chunks'] 

    if is_in_operation(context,'LIMIT_USAGE'):
        if chunks[3] == 'SOQL':
            context[f'DEF:SOQL queries'] = chunks[4]
            append_LU_default(context,'SOQL queries',chunks[4])
            return True
        if chunks[3] == 'SOQL_ROWS':
            append_LU_default(context,'query rows',chunks[4])

        return True

 #   if '|LIMIT_USAGE|' in line and '|SOQL|' in line: 
 #       context[f'DEF:SOQL queries'] = chunks[4]
 #       return True

    if is_in_operation(context,'LIMIT_USAGE_FOR_NS'):
        obj = setTimes(context,line,type='LIMIT')
        obj['output'] = f"{chunks[1].lower()}  {chunks[2]}"
        context['parsedLines'].append(obj)

        limits = chunks[2]
        if limits == '(default)':         limitsNS = 'DEF:'
        elif limits == 'vlocity_cmt':     limitsNS = 'CMT:'
        else:                             limitsNS = f"{limits}:"

        next = 1
        nextline = context['lines'][context['line_index']+next]
        while '|' not in nextline:
            if 'SOQL queries' in nextline:
                nlchunks = nextline.split(' ')
                if f'{limitsNS}SOQL queries' not in context:
                    context[f'{limitsNS}SOQL queries'] = 0
                if int(context[f'{limitsNS}SOQL queries']) < int(nlchunks[6]):
                    context[f'{limitsNS}SOQL queries'] = nlchunks[6]
            if 'CPU time' in nextline:
                nlchunks = nextline.split(' ')
                if f'{limitsNS}CPU time' not in context:
                    context[f'{limitsNS}CPU time'] = 0
                if int(context[f'{limitsNS}CPU time']) < int(nlchunks[5]):
                    context[f'{limitsNS}CPU time'] = nlchunks[5]
            next = next + 1
            nextline = context['lines'][context['line_index']+next]
        return True

def parseSOQL(context):
    line = context['line']
    chunks = context['chunks']
    if is_in_operation(context,'SOQL_EXECUTE_BEGIN'):
        obj = setTimes(context,line,type="SOQL")
        obj['query'] = chunks[4]
        obj['object'] = chunks[4].lower().split(' from ')[1].strip().split(' ')[0]
        obj['apexline'] = chunks[2][1:-1]

        soql = obj['query'].lower()
        ch_so = obj['query'].split("'")
        if len(ch_so)>1:
            posibles = ch_so[1::2]

            ids = [posible for posible in posibles if Sobjects.checkId(posible) ]
            idss = set(ids)
            if len(idss)>0:
                obj['where_ids'] = ",".join(idss)


        obj['for_update'] = ' for update' in soql

        if 'where' in soql:
            soql = soql.split('where')[0]
        _from = soql.split(' from ')[-1].strip()
        _from = _from.split(' ')[0]

        obj['from'] = _from
        obj['output'] = f"Select: {obj['from']} --> No SOQL_EXECUTE_END found"

        append_and_increaseIdent(context,obj,increase=False)
        return True

    if context['chunks_lenght']>1 and chunks[1] == 'SOQL_EXECUTE_END':
        context['totalQueries'] = context['totalQueries'] + 1
        obj = decreaseIdent_pop_setFields(context,type="SOQL",key='type',value='SOQL',decrease=False)
        obj['rows'] = chunks[3].split(':')[1]
        for_uptate = "for update" if obj['for_update'] else ""
        ids = f"w:{obj['where_ids']}" if 'where_ids' in obj else ""
        if context['output_format']=='JSON':
            obj['output'] = f"Select {for_uptate}: {obj['from']} --> {obj['rows']} rows {ids}"
        else:
            obj['output'] = f"Select {for_uptate}: {obj['from']} --> {obj['rows']} rows {utils.CFAINT}{utils.CYELLOW}{ids}{utils.CEND}"

        return True

    return False

def parseMethod(context):
    line = context['line']
    chunks = context['chunks'] 
    if context['chunks_lenght']>1 and 'METHOD_' in  chunks[1]:
        if len(chunks)<4:
            print(line)
            return

        operation = chunks[1]
       ## method = getMethod(line)
        method = chunks[3] if len(chunks) == 4 else chunks[4]
        if '(' in method:
            method = method.split('(')[0]

        if 'ENTRY' in operation:
            obj = setTimes(context,line,type='METHOD')
            obj['method'] = method
            obj['apexline'] = chunks[2][1:-1] if chunks[2]!='[EXTERNAL]' else 'EX'
            obj['output'] = obj['method']
            context['parsedLines'].append(obj)

            if '.getInstance' in obj['method']:
                pass
            else:
                context['openItemsList'].append(obj)
                context['ident'] = context['ident'] + 1
            return True

        else:
            obj = getFromList(context['openItemsList'],'method',method)
            if obj == None:
                obj = getFromList(context['openItemsList'],'method',f"{method}",endsWith=True)
                apexline = chunks[2][1:-1]
                if obj != None and apexline != obj['apexline']:
                    obj == None
            if obj == None:
                obj = getFromList(context['openItemsList'],'method',f"{method}",startsWith=True)
                apexline = chunks[2][1:-1]
                if obj != None and apexline != obj['apexline']:
                    obj == None
            if obj is not None:
                context['ident'] = obj['ident']
                setTimes(context,line,obj)

            else:
                obj = setTimes(context,line,type='NO_ENTRY')
                obj['method'] = chunks[-1]
                obj['apexline'] = chunks[2][1:-1] if chunks[2]!='[EXTERNAL]' else 'EX'
                context['parsedLines'].append(obj)

            if 'method' in obj:
                obj['output']=obj['method']
            else:
                obj['output']=obj['Id']
            return True

    return False

def parseVariableAssigment(context):
    line = context['line']
    chunks = context['chunks'] 

    if 'EXP_VAR' in context and context['EXP_VAR'] == True:
        if chunks[1] == 'VARIABLE_ASSIGNMENT' and chunks[2] == '[EXTERNAL]':
            obj = setTimes(context,line,type='VAR_ASSIGN')
            obj['type'] = 'VAR_ASSIGN'
            obj['subType'] = 'EXCEPTION'
         #   obj['string'] = chunks[4]
            obj['apexline'] = chunks[2][1:-1] if chunks[2]!='[EXTERNAL]' else 'EX'

            context['parsedLines'].append(obj)         
            obj['output'] = chunks[4]

        else:   context['EXP_VAR'] = False
        return False #why False???

    if is_in_operation(context,'VARIABLE_ASSIGNMENT'):
        if len(chunks) >= 5:
            if 'ExecutionException' in chunks[4] or 'ExecutionException' in chunks[4]:
                obj = setTimes(context,line,type='VAR_ASSIGN')
                obj['type'] = 'VAR_ASSIGN'
                obj['subType'] = 'EXCEPTION'
                obj['string'] = chunks[4]
                obj['apexline'] = chunks[2][1:-1] if chunks[2]!='[EXTERNAL]' else 'EX'

                context['parsedLines'].append(obj)
                obj['output'] = obj['string'] 

                context['EXP_VAR'] = True
        return True
    return False

def parseDML(context):
    line = context['line']
    chunks = context['chunks']

    if is_in_operation(context,'DML_BEGIN'):
        obj = setTimes(context,line,type="DML")
        obj['OP'] = chunks[3]
        obj['Type'] = chunks[4]
        obj['Id'] = chunks[2]
        obj['Rows'] = chunks[5]
        obj['apexline'] = chunks[2][1:-1]
        obj['output'] = f"{obj['OP']} {obj['Type']} --> {obj['Rows']}" 
        append_and_increaseIdent(context,obj)
        return True

    if is_in_operation(context,'DML_END'):
        decreaseIdent_pop_setFields(context,'DML',key='Id',value=chunks[2])
        return True

    return False

def parseCallOutResponse(context):
    line = context['line']
    chunks = context['chunks']

    if is_in_operation(context,'CALLOUT_RESPONSE'):
        obj = setTimes(context,line,type='CALLOUT')
     #   obj['string'] = chunks[3]
        obj['apexline'] = chunks[2][1:-1]

        context['parsedLines'].append(obj)  
        obj['output'] = chunks[3]
        return True

    return False

def parseConstructor(context):
    line = context['line']
    chunks = context['chunks']

    if is_in_operation(context,'CONSTRUCTOR_ENTRY'):
        obj = setTimes(context,line,field='output',value=chunks[5],type='CONSTRUCTOR')
        obj['apexline'] = chunks[2][1:-1] if chunks[2]!='[EXTERNAL]' else 'EX'

        append_and_increaseIdent(context,obj)
        return True

    if is_in_operation(context,'CONSTRUCTOR_EXIT'):

        decreaseIdent_pop_setFields(context,type='CONSTRUCTOR',key='output',value=chunks[5])
        return True

    return False

def parseCodeUnit(context):
    line = context['line']
    chunks = context['chunks']

    if is_in_operation(context,'CODE_UNIT_STARTED'):
        obj = setTimes(context,line,type='CODE_UNIT')
        obj['output'] = chunks[4] if len(chunks)>4 else chunks[3]
        append_and_increaseIdent(context,obj)
        return True

    if is_in_operation(context,'CODE_UNIT_FINISHED'):
        decreaseIdent_pop_setFields(context,'CODE_UNIT',key='output',value=chunks[2])
        return True

    return False

def parseNamedCredentials(context):
    line = context['line']
    chunks = context['chunks']

    if is_in_operation(context,'NAMED_CREDENTIAL_REQUEST'):
        obj = setTimes(context,line,field='output',value=chunks[2],type='NAMED_CRD')
        append_and_increaseIdent(context,obj)
        return True

    if is_in_operation(context,'NAMED_CREDENTIAL_RESPONSE'):
        obj = decreaseIdent_pop_setFields(context,type='NAMED_CRD',key='type',value='NAMED_CRD')
        return True

    return False

def parseFlow(context):
    line = context['line']
    chunks = context['chunks']
    debugList = context['parsedLines']

    if 1==2:
        if '|FLOW_START_INTERVIEWS_BEGINxx|' in line:
            obj = setTimes(context,line,type='FLOW_START_INTERVIEWS',field='output',value='FLOW_START_INTERVIEWS')
            append_and_increaseIdent(context,obj)

        if '|FLOW_START_INTERVIEWS_ENDxx|' in line:
            decreaseIdent_pop_setFields(context,'FLOW_START_INTERVIEWS',key='output',value='FLOW_START_INTERVIEWS')

    if is_in_operation(context,'FLOW_START_INTERVIEW_BEGIN'):
        obj = setTimes(context,line,type='FLOW_START_INTERVIEW')
        obj['interviewId'] = chunks[2]
        obj['Name'] = chunks[3]
        obj['output'] = obj['Name']
        append_and_increaseIdent(context,obj)
        return True

    if is_in_operation(context,'FLOW_START_INTERVIEW_END'):
        interviewId = chunks[2]
        decreaseIdent_pop_setFields(context,'FLOW_START_INTERVIEW',key='interviewId',value=interviewId)
        return True

    if is_in_operation(context,'FLOW_ELEMENT_ERROR'):
        obj = setTimes(context,line,type='FLOW_ELEMENT_ERROR')
        obj['message'] = chunks[2]
        obj['elementType'] = chunks[3]
        obj['elementName'] = chunks[4]
        obj['output'] = utils.CRED+ f"{obj['message']} in {obj['elementType']}:{obj['elementName']}" + utils.CEND
        debugList.append(obj)
        context['exception'] = True
        context['exception_msg'] = obj['output']
        return True
    
    if is_in_operation(context,'FLOW_ELEMENT_BEGIN'):
        obj = setTimes(context,line,type='FLOW_ELEMENT')
        obj['interviewId'] = chunks[2]
        obj['elementType'] = chunks[3]
        obj['elementName'] = chunks[4]
        obj['output'] = f"{obj['elementType']}-{obj['elementName']}"
        append_and_increaseIdent(context,obj)
        return True

    if is_in_operation(context,'FLOW_ELEMENT_END'):
        interviewId = chunks[2]
        decreaseIdent_pop_setFields(context,'FLOW_ELEMENT',key='interviewId',value=interviewId)

    if is_in_operation(context,'FLOW_RULE_DETAIL'):
        values = {
            'type':'FLOW_ELEMENT',
            'elementType':'FlowDecision',
            'interviewId':chunks[2],
            'elementName':chunks[3]
        }
        obj = getFromDebugList(context,values)
        obj['ruleName'] = chunks[3]
        obj['result'] = chunks[4]
        obj['output'] = f"{obj['elementType']}-{obj['elementName']} -- {obj['ruleName']}->{obj['result']}"
        return True

    return False

def parseUserInfo(context):
    if is_in_operation(context,'USER_INFO'):
   # if '|USER_INFO|' in context['line']:
        obj = setTimes(context,context['line'],field='output',value=context['chunks'][4],type='USER_INFO')
        context['parsedLines'].append(obj)
        return True
    return False

def appendEnd(context):

    for line in reversed(context['lines']):
        if '|' in line:
            break

    if 'CPQCustomHookImplementation' in context and  context['CPQCustomHookImplementation'] == 'Started':
        obj = setTimes(context,line,type='EXCEPTION',field='output',value="CPQCustomHookImplementation did not finish")
        context['exception'] = True
        context['exception_msg'] = obj['output']

        context['parsedLines'].append(obj)
        context['file_exception'] = True
        
    lastline = line
    obj = setTimes(context,lastline,type="END")
    obj['output'] = 'Final Limits'
    context['parsedLines'].append(obj)