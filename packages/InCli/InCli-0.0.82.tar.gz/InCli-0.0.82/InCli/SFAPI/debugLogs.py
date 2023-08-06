from . import restClient,query,file,utils,Sobjects,traceFlag,elementParser,debugLogsPrint

import colorama
import sys,time,os
import ansi2html,re
import threading,traceback
from queue import Queue

def printLogRecords(loguser=None,limit=50,whereClause=None):
    logUserId = get_loguser_id(loguser) if loguser != None else None
    if loguser != None:
        print(f'Logs for user {loguser}:')
    logs = get_apexLog_records_from_db(logUserId,limit=limit,whereClause=whereClause)
    logs = utils.deleteNulls(logs,systemFields=False)
    logs1 = []
    for log in logs:
        log['LastModifiedDate'] = log['LastModifiedDate'].split('.')[0]
        log['StartTime'] = log['StartTime'].split('.')[0]
        log['LogUserId'] =  f"{log['LogUserId']} ({get_username_and_cache(log['LogUserId'])})"

        logs1.append(log)

    utils.printFormated(logs1,fieldsString="Id:LogUserId:LogLength:DurationMilliseconds:LastModifiedDate:Request:Operation:Application:Status:Location", rename="LogLength%Len:DurationMilliseconds%ms:Application%App")
    return logs

def get_apexLog_records_from_db(logUserId=None,limit=50,whereClause=None):
    where = f" where {whereClause} " if whereClause != None else ''
    where = f" where logUserId='{logUserId}' " if logUserId is not None else where

    call = query.query(f"Select Id,LogUserId,LogLength,LastModifiedDate,Request,Operation,Application,Status,DurationMilliseconds,StartTime,Location,RequestIdentifier FROM ApexLog  {where} order by LastModifiedDate desc limit {limit}")
    return call

def get_apexLog_record_and_body_from_db(logId):
    logRecords = query.queryRecords(f"Select fields(all) FROM ApexLog where Id ='{logId}' limit 1")

    if logRecords == None or len(logRecords)==0:
        utils.raiseException(errorCode='NO_LOG',error=f'The requested log <{logId}> cannot be found in the Server.',other=f"No record in ApexLogwith Id {logId}")    
    logRecord = logRecords[0]

    action = f"/services/data/v56.0/sobjects/ApexLog/{logId}/Body/"
    logbody = restClient.callAPI(action)
    return logRecord,logbody

def get_apexLog_record_and_body_from_file(filename):
    if file.exists(filename):
        body = file.read(filename)
        logRecord = get_apexlog_file_header(body)
        return logRecord,body,filename

    return None,None,filename

def get_apexlog_file_header(body):
    def parse_header(pc,line):
        if 'LOGDATA' in line:
    #     print('old format')
            ch = line.split(' ')
            ch1 = []
            for c in ch:
                if c == '':continue
                if 'LOGDATA' in c: continue
                if c=='\x1b[0m':continue
                c = c.replace('\x1b[0;32m','')
                c = c.replace('\x1b[0m\x1b[2m','')
                c = c.replace('\x1b[0m','')
                ch1.append(c)
            if ch1[0] == 'Id:':
                pc['header'] = {
                    'Id':ch1[1],
                    'logId':ch[1],
                    'LogUserId':ch1[3],
                    'LogUserName':ch1[4].replace('(','').replace(')',''),
                    'Request':ch1[6],
                    'Operation':ch1[8],
                    'LogLength':ch1[10],
                    'DurationMilliseconds':ch1[12]
                }
            else:
                pc['header']['StartTime'] = ch1[1]
                pc['header']['Application'] = ch1[3]
                pc['header']['Status'] = ch1[5]
                pc['header']['Location'] = ch1[7]
                pc['header']['RequestIdentifier'] = ch1[9]
    if body == None or body == '':return None
    lines = body.splitlines()
    try:
        if 'LOGDATA' in lines[0]:
            pc ={}
            parse_header(pc,lines[0])
            parse_header(pc,lines[1])
            return pc['header']
        return None
    except Exception as e:
        print()

def get_apexLog_record_and_body_from_file_otherwise_db(logId,only_file=False):
    """Gets the log body for the provided logId from file (if exists) otherwise from the Org"""
    filename = f"{restClient.logFolder()}{logId}.log"

    if file.exists(filename) == True:
        logRecord,body,x = get_apexLog_record_and_body_from_file(filename)

        if body == None or len(body)==0:
            print("The file seems corrupted. Getting log from server.")
            file.delete(filename)
            return get_apexLog_record_and_body_from_file_otherwise_db(logId)
        return logRecord,body,filename
    else:
        if only_file == True:
            return None,None,filename
        logRecord,body = get_apexLog_record_and_body_from_db(logId) 
        body = apexLog_record_to_string(logRecord) + body  
        save_to_store(logId,body)
        return logRecord,body,filename

def apexLog_record_to_string(logRecord):
    log = logRecord
    username = get_username_and_cache(log['LogUserId'])

    logLine = f"""{utils.CFAINT}LOGDATA:    Id: {log['Id']}   LogUserId: {log['LogUserId']} {utils.CGREEN}({username}){utils.CEND}{utils.CFAINT}    Request: {log['Request']}  Operation: {utils.CGREEN}{log['Operation']}{utils.CEND}{utils.CFAINT}    lenght: {log['LogLength']}    duration:  {utils.CGREEN}{log['DurationMilliseconds']} {utils.CEND} 
 {utils.CFAINT}LOGDATA:      startTime: {log['StartTime']}    app: {log['Application']}      status: {log['Status']}     location: {log['Location']}     requestIdentifier: {log['RequestIdentifier']}{utils.CEND}
    """     
    return logLine

def save_to_store(logId,body):
    filename = f"{restClient.logFolder()}{logId}.log"
    file.write(filename,body) 

userCache = {}
def get_username_and_cache(Id):
    username_query = f"select Username from User where Id='{Id}'"
    if username_query not in userCache: userCache[username_query] = query.queryField(username_query) 
    return userCache[username_query]

def do_parse_storage(pc,search_dir=None):  
    if pc['store_logId'] != None:
       # pc['logId'] = pc['store_logId']
        pc['filepath'] = f"{restClient.logFolder()}{pc['store_logId']}.log"

        do_parse_logId(pc)
        return

    if search_dir==None:
        search_dir = restClient.logFolder()

    os.chdir(search_dir)
    files = filter(os.path.isfile, os.listdir(search_dir))
    files = [os.path.join(search_dir, f) for f in files] # add path to each file
    files.sort(key=lambda x: os.path.getmtime(x))
    log_files = [f for f in files if f.lower().endswith('.log')]
    fileNames = [os.path.basename(f) for f in log_files]

    print(f"Files to be parsed in the store {len(log_files)}")
    file_dates = []

    print(f"Ordering files by date...")
    total_records = len(log_files)
    num = 0
    for log_file in log_files:
        logRecord,body,x = get_apexLog_record_and_body_from_file(log_file)
        for line in body.splitlines():
            if '|' in line:
                _time = line.split(' ')[0]
                file_dates.append({
                    'time':_time,
                    'file':log_file
                })
                break

        num = num +1
        sys.stdout.write("\r%d%%" % int(100*num/total_records))
        sys.stdout.flush() 
    newlist = sorted(file_dates, key=lambda d: d['time'])

    sorted_log_file = [d['file'] for d in newlist]

    print(f"Ordered.")

    try:
        parse_apexlogs_by_Ids_or_filepaths(pc,logIds=None,filepaths=sorted_log_file,printProgress=True,threads=0)

    except KeyboardInterrupt:
        print('Interrupted')
    
    print_parsing_results(pc)

   # print(frequency)

def do_parse_tail(pc):
    def auto_renew_traceFlag(tf):
        try:
            while True:
                traceFlag.update_trace_flag_incli(tf['Id'],minutes=5)
                time.sleep(10)
        except Exception as e:
            print(f"InCli no longer in auto, due to exception")
            utils.printException(e)

    def deleteRecords(delete_queue):
        def divide_chunks(l, n):
            for i in range(0, len(l), n):
                yield l[i:i + n]
            
        while True:
            logIds = delete_queue.get()

            try :
                logIdsList= list(divide_chunks(logIds,200))
                for l in logIdsList:
                    res = Sobjects.deleteMultiple('ApexLog',l)
                restClient.glog().debug(f"deleted records {logIds}")
                delete_queue.task_done()
            except utils.InCliError as e:
                if e.args[0]['errorCode'] != 'NO_LOG':
                    utils.printException(e)
            except Exception as e:
                print(logIds)
                print(e)

    timefield = "LastModifiedDate"
    InCliUser = 'InCli'.lower()

    logRecords = query.queryRecords(f"Select fields(all) FROM ApexLog order by {timefield} desc limit 1")
    time0 = logRecords[0][timefield] if len(logRecords) > 0 else None
    timez = time0.split('.')[0] + "Z" if time0 != None else '2000-12-12T17:19:35Z'

    delete_queue= None
    restClient.glog().debug(f"deleteLogs-->{pc['deleteLogs']}")

    if pc['loguser'] != None and pc['loguser'].lower() == InCliUser:
        logUserId = InCliUser
        incli_debuglevel_ids = traceFlag.get_InCli_debuglevelIds()
        pc['auto'] = False
        pc['output_format'] = 'JSON'
        pc['printNum'] = False

    else:
        pc['printNum'] = True
        if (pc['deleteLogs'] or pc['auto']) and pc['loguser'] == None:  
            pc['loguser'] = f"username:{pc['connection']['Username']}"

        logUserId = get_loguser_id(pc['loguser']) if pc['loguser'] != None else None

    if pc['deleteLogs']==True:       
        restClient.glog().debug("Starting delete queue")
        delete_queue = Queue(maxsize=0)
        for x in range(0,1):
            threading.Thread(target=deleteRecords,args=(delete_queue,), daemon=True).start()
        print(f"ApexLog records for {pc['loguser']} {logUserId} will be automatically deleted.")

    if pc['auto']:
        tf = traceFlag.set_incli_traceFlag_for_user(f"Id:{logUserId}",pc['debug_level'])
        print(f"TraceFlag for user {pc['loguser']} {logUserId} set to Auto. Debug Level InCli{pc['debug_level']}.")

        utils.printFormated(tf,fieldsString="ApexCode,ApexProfiling,Callout,Database,LogType,System,Validation,Visualforce,Workflow",separator=',')

        threading.Thread(target=auto_renew_traceFlag,args=(tf,), daemon=True).start()

    try:
        waitingPrinted = False
        procesed = []
        greater = True

        while (True):
            if greater:    where = f" {timefield} > {timez} "
            else:          where = f" {timefield} >= {timez} "

            where = f" {pc['whereClause']} and {where}" if pc['whereClause'] is not None else where
            if logUserId is not None:
                if logUserId == InCliUser:
                    incli_user_ids = traceFlag.get_InCli_usersIds(incli_debuglevel_ids)
                    where = f" logUserId in ({query.IN_clause(incli_user_ids)}) and {where} "
                else:
                    where = f" logUserId='{logUserId}'and {where} "

            fields = "Id,LogUserId,LogLength,LastModifiedDate,Request,Operation,Application,Status,DurationMilliseconds,StartTime,Location,RequestIdentifier,SystemModstamp"
            logRecords = query.queryRecords(f"Select {fields} FROM ApexLog where {where} order by {timefield} asc")
            if len(logRecords) > 0:
                waitingPrinted = False

                logRecords_not_processed = [r for r in logRecords if r['Id'] not in procesed]
                ids_not_processed = [r['Id'] for r in logRecords_not_processed]
                if pc['noScreen']==False:
                    logIds = [r['Id'] for r in logRecords_not_processed]
                else:
                    records1 = []
                    for r in logRecords_not_processed:
                        if r['Operation'] not in ['<empty>','VFRemoting']: records1.append(r)
                        elif r['Operation'] == 'VFRemoting' and r['LogLength']>1000: records1.append(r)
                    logIds = [r['Id'] for r in records1 ]

                if len(ids_not_processed) == 0:
                    greater = True
                    continue
                greater = False
                procesed.extend(ids_not_processed)

                if len(logIds)>0:
                    parse_apexlogs_by_Ids_or_filepaths(logIds=logIds,pc=pc,raiseKeyBoardInterrupt=True,raise_no_log=False)

                time0 = logRecords[-1][timefield]
                timez = time0.split('.')[0] + "Z"

                if delete_queue!=None:
                    delete_queue.put(ids_not_processed)
                    restClient.glog().debug(f"{logIds} into queue...")

            elif  waitingPrinted == False:
                print()
                print(f"waiting for debug logs for user {pc['loguser']}")  if pc['loguser'] != None  else print(f"waiting for debug logs ")
                waitingPrinted = True

           # print_parsing_results(pc)
            time.sleep(2)
    except KeyboardInterrupt as e:
        print()
        print_parsing_results(pc)
        print("Terminating -tail..., cleaning up")
        if pc['auto']:
            print(f"Stopping -auto. Deleting InCli traceflag for user { pc['loguser']}")

        #traceFlag.update_trace_flag_incli(tf,minutes=1,start=-15)
    
        traceFlag.delete_trace_Flag(tf['Id'])
        if delete_queue != None: 
            while delete_queue.empty()==False:    time.sleep(1)
        print('Terminated')
        return

def do_parse_logs_lastN(pc):
    whereClause = pc['whereClause']
    loguser = pc['loguser']
    lastN = pc['lastN']
    pc['printNum'] = True

    if loguser ==None:
        loguser = restClient.getConfigVar('loguser')

    if loguser == None:
        print(f"{utils.CYELLOW}Getting logs for all users.{utils.CEND}")
    else:
        print(f"{utils.CYELLOW}Getting logs for {loguser}.{utils.CEND}")

    where = f" where {whereClause} " if whereClause is not None else ''
    where = f" where logUserId='{get_loguser_id(loguser)}' " if loguser is not None else where

    if lastN == None: lastN = 1
    q = f"Select Id FROM ApexLog {where} order by LastModifiedDate desc limit {lastN}"
    logIds = query.queryFieldList(q)
    if logIds == None or len(logIds)==0:   utils.raiseException(errorCode='NO_LOG',error=f'No logs can be found. ',other=q)

    parse_apexlogs_by_Ids_or_filepaths(logIds= logIds,pc=pc)
    print_parsing_results(pc)

def do_parse_from_file(parseContext):
    set_apexlog_body_in_pc(parseContext)

  #  parseContext['body'] = file.read(parseContext['filepath'])
    parseContext['operation'] = 'parsefile'
 #   name = os.path.basename(parseContext['filepath']).split('.')[0]
 #   parseContext['logId']=name
    name = os.path.basename(parseContext['filepath'])
    parseContext['logId'] = name.split('.')[0]
    context =  parse_apexlog_body(parseContext)
    debugLogsPrint.print_parsed_lines_to_output(parseContext)
    return context

def do_parse_logId(parseContext):
    set_apexlog_body_in_pc(parseContext)
    context =  parse_apexlog_body(parseContext)
    debugLogsPrint.print_parsed_lines_to_output(parseContext)

    return context

def parse_apexlogs_by_Ids_or_filepaths(pc,logIds=None,filepaths=None,raiseKeyBoardInterrupt=False,printProgress=False,threads=10,raise_no_log=True):
    def read_log_from_org(q):
      while True:
        try:
            Id = q.get()
            get_apexLog_record_and_body_from_file_otherwise_db(Id)
            restClient.glog().debug(f"Read body for Id {Id}")
            q.task_done()
        except Exception as e:
            if raise_no_log==False and e.args[0]['errorCode'] == 'NO_LOG':
                pass
            else:
                raise e

    if 'total_parsed'       not in pc:   pc['total_parsed'] = 0
    if 'parsed_Id_status'   not in pc:   pc['parsed_Id_status'] = []
    if 'errors' not in pc:   pc['errors'] = []
    if 'queue'  not in pc:   pc['queue'] = None

    if filepaths != None:
        threads = 0

    if threads >0: 
        threads = 1
        if pc['queue'] == None:
            pc['queue'] = Queue(maxsize=0)
            for x in range(0,threads):
                threading.Thread(target=read_log_from_org,args=(pc['queue'],), daemon=True).start()
        for logid in logIds:
            pc['queue'].put(logid)
            
    num = 0
    items = filepaths if filepaths != None else logIds
    for num,item in enumerate(items):
        if printProgress:
            sys.stdout.write("\r%d%%" % int(100*num/len(items)))
        try:
            if logIds!= None:
                parsed={ 'logId':item, 'status':'ok' }
                pc['logId'] = item
                pc['filepath'] = None
            else:
                parsed={ 'file':os.path.basename(item), 'status':'ok' }
                pc['filepath'] = item  
                pc['logId'] = None
             
            pc['parsed_Id_status'].append(parsed)
            set_apexlog_body_in_pc(pc)
            if 'logRecord' in pc and pc['logRecord'] != None:
                if 'logId' not in parsed : 
                    parsed['logId'] = pc['logRecord']['Id']
                    parsed['timeStamp'] = pc['logRecord']['StartTime']
            parse_apexlog_body(pc)
            debugLogsPrint.print_parsed_lines_to_output(pc)
            if 'printNum' in pc and pc['printNum']:    print( pc['total_parsed']+num+1)
            if 'logRecord' in pc:
                if pc['logRecord'] == None: parsed['timeStamp'] = 'No log record'
                else:
                    parsed['timeStamp'] = pc['logRecord']['StartTime']
                    if parsed['timeStamp'] == None: parsed['timeStamp'] = 'No time stamp'
            else:
                parsed['timeStamp'] = ''
            if pc['context']['exception'] == True:    
                parsed['status'] = pc['context']['exception_msg'][0:200]

        except KeyboardInterrupt:
            if raiseKeyBoardInterrupt:        raise
            break
        except utils.InCliError as e:
             parsed['status'] = f"Parse error: {e.args[0]['errorCode']}  "
             utils.printException(e)
             pc['errors'].append(e)
        except Exception as e:
            e1 = utils.exception_2_InCliException(e)
            parsed['status'] = f"{e1.args[0]['errorCode']}: {e1.args[0]['error']}"
        #    if 'header' in pc:
        #        if 'logId' not in parsed : 
        #            parsed['logId'] = pc['header']['Id']
        #            parsed['timeStamp'] = pc['header']['startTime']
            pc['errors'].append(e1)
            print(traceback.format_exc())

    pc['total_parsed'] = pc['total_parsed'] + num + 1
    
def print_parsing_results(pc):
    print()

    if 'parsed_Id_status' not in pc:
        print("No files parsed.")
        return 
    parsed = pc['parsed_Id_status']
    errors = pc['errors']

    print(f"{pc['total_parsed']} logs parsed")
   # print(parsed)
    parsed = [par for par in parsed if par['status']!='ok']

    if len(parsed) == 0:  print("No errors.")
    if len(parsed)>0:
        utils.printFormated(parsed,fieldsString='timeStamp:logId:status')
     #   errors = list({error.args[0] for error in errors})
        errors = list({error.args[0]['errorCode']:error for error in errors}.values())

        for error in errors:    utils.printException(error)  

def get_loguser_id(loguser):
    id = Sobjects.IdF('User',loguser)
    return id if id!= None else utils.raiseException('QUERY',f"User with field {loguser} does not exist in the User Object.") 

def set_apexlog_body_in_pc(pc):
    """if pc['filepath'] defined, reads from the file specified. Otherwiese logId needs to be set. 
    """
    if 'filepath' in pc and pc['filepath'] != None:
        pc['logRecord'],pc['body'],x = get_apexLog_record_and_body_from_file(pc['filepath'])
    else:
        pc['logRecord'],pc['body'],pc['filepath'] = get_apexLog_record_and_body_from_file_otherwise_db(pc['logId'])
    if pc['body'] == None :   utils.raiseException(errorCode='NO_LOG',error=f'The requested log <{pc["logId"]}> cannot be found. ')
    if len(pc['body'])==0:    utils.raiseException(errorCode='NO_LOG',error=f'The body for the requested log <{pc["logId"]}> is empty. ')
    
def createContext(lines):
    context = {
        'totalQueries' : 0,
        'timeZero':0,
        'ident':0,
        'DEF:SOQL queries' : 0,
        'DEF:CPU time' : 0,
        'CMT:SOQL queries' : 0,
        'CMT:CPU time' : 0,
        "exception":False,
        'LU':{}
    }
    context['totalQueries'] = 0
    context['timeZero'] = 0
    context['ident'] = 0
    context['DEF:SOQL queries'] = 0
    context['DEF:CPU time']=0
    context['CMT:SOQL queries'] = 0
    context['CMT:CPU time']=0
    context['exception'] = False
    context['file_exception'] = False
#    context['previousElapsedTime'] = 0
#    context['previousCPUTime'] = 0
    context['previousIsLimit'] = False
#    context['prevTimes'] = {
#        0:[0,0]
#    }
#    context['prevLevel'] = 0
    context['firstLineIn'] = True
    context['firstLineOut'] = True

    context['parsedLines'] = []
    context['openItemsList'] = []

    context['lines'] = lines

    return context

frequency = {}

def parse_apexlog_body(pc):
    if pc['body'] == None :  utils.raiseException(errorCode='NO_LOG',error=f'The requested log <{pc["logId"]}> cannot be found. ')
    if len(pc['body'])==0:    utils.raiseException(errorCode='NO_LOG',error=f'The body for the requested log <{pc["logId"]}> is empty. ')

    try:
        context = createContext(pc['body'].splitlines())
        context['output_format'] = pc['output_format']
        pc['context'] = context

        for num,line in enumerate(context['lines']):
            if context['firstLineIn'] == True:
                if 'APEX_CODE' in line:
                    context['firstLineIn'] = False
                    levels = line.strip().split(' ')[1].replace(',','=').replace(';','  ')
                    levels = f"{utils.CFAINT}{levels}{utils.CEND}"
                    obj = {  'type':'LOGDATA', 'output':levels  }
                    context['parsedLines'].append(obj)

                    continue      
                else:
            #        parse_header(pc,line)
                    obj = {    'type':'LOGDATA',   'output':line  }
                    context['parsedLines'].append(obj)
                    continue

            chunks = line.split('|')
            if len(chunks)<2:
                continue
            if len(chunks[0])<10:
                continue
            if len(chunks[1])>30:
                continue

            context['chunks'] = chunks
            context['chunks_lenght'] = len(chunks)
            context['line'] = line
            context['line_index'] = num

            if len(chunks)>1 and chunks[1] in ['SYSTEM_MODE_ENTER','SYSTEM_MODE_EXIT','HEAP_ALLOCATE','STATEMENT_EXECUTE','VARIABLE_SCOPE_BEGIN','HEAP_ALLOCATE','SYSTEM_METHOD_ENTRY','SYSTEM_METHOD_EXIT','SOQL_EXECUTE_EXPLAIN','ENTERING_MANAGED_PKG','SYSTEM_CONSTRUCTOR_ENTRY','SYSTEM_CONSTRUCTOR_EXIT']:    continue

            if len(chunks)>1 and chunks[1] in ['VALIDATION_RULE','VALIDATION_FORMULA','VALIDATION_PASS','WF_RULE_FILTER','WF_RULE_EVAL_VALUE','STATIC_VARIABLE_LIST','FLOW_CREATE_INTERVIEW_BEGIN','FLOW_CREATE_INTERVIEW_END','TOTAL_EMAIL_RECIPIENTS_QUEUED','CUMULATIVE_PROFILING_BEGIN','CUMULATIVE_PROFILING','CUMULATIVE_PROFILING_END','EXECUTION_STARTED','EXECUTION_FINISHED'] : continue

            if elementParser.parseVariableAssigment(context):      continue
            if elementParser.parseMethod(context):            continue
            if elementParser.parseSOQL(context)==True:        continue
            if elementParser.parse_limit_usage(context):     continue
            if elementParser.parseLimits(context):     continue
            if elementParser.parseUserDebug(context):  continue
            if elementParser.parseUserInfo(context):   continue
            if elementParser.parseExceptionThrown(context):   continue
            if elementParser.parseDML(context):               continue
            if elementParser.parseConstructor(context):       continue
            if elementParser.parseCodeUnit(context):          continue
            if elementParser.parseConstructor(context):       continue
            if elementParser.parseNamedCredentials(context): continue
            if elementParser.parseCallOutResponse(context): continue
            if elementParser.parseWfRule(context) : continue
            if elementParser.parseFlow(context) : continue
            
        if len(context['openItemsList']) > 0:
            a=1
        elementParser.appendEnd(context)

        return context

    except KeyboardInterrupt as e:
        print(f"Parsing for logI {pc['logId']} interrupted.")
        raise e
    except Exception as e:
        print(f"Exception while parsing for logI {pc['logId']} ")
        raise e
