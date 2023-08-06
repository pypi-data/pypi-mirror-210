import os,sys,sys,gc
from xmlrpc.client import Boolean
from . import Sobjects, jsonFile,file, objectUtil,utils,timeStats
import requests,threading
import logging,datetime,enum
import simplejson as json

_initializedConnections = []
_allThreadsContext = {}
_currentConnectionName = None

def _create_thread_context(connection_name):
    global _currentConnectionName
    _currentConnectionName = connection_name if connection_name != None else _currentConnectionName
    if _currentConnectionName == None:
        utils.raiseException('ConnectionError',"Current Connection is no set.")
    th = {
            'connectionName': _currentConnectionName,
            'calls':[]
        }
    _allThreadsContext[threading.get_native_id()] = th

    return th

def _get_thread_context(setConnectionName=None):
    """
    Threads can share a connection. However the call stack belongs to each thread.
    When a thread calls this function, it can set the connection for the thread (if especified) or get the connection previously set if setConnectionName=None
    If a connection has not been set fot the thread, the current one (the latest one set for any previous thread) is assigned to the thread   
    """
    global _allThreadsContext,_currentConnectionName
    thread_id = threading.get_native_id()
    if thread_id not in _allThreadsContext:
    #    _currentConnectionName = setConnectionName if setConnectionName != None else _currentConnectionName
    #    if _currentConnectionName == None:
    #        utils.raiseException('ConnectionError',"Current Connection is no set.")
        return _create_thread_context(setConnectionName)

     #   _allThreadsContext[thread_id] = th
     #   return th
    if setConnectionName != None:   #change the connection for the thread
        _allThreadsContext[thread_id]['connectionName'] = setConnectionName
        _currentConnectionName = setConnectionName
    return _allThreadsContext[thread_id]

##################################################################
def _pushThreadCall(call):
    max_calls = 5
    _calls = _get_thread_context()['calls']
    if len(_calls) == max_calls:
        _calls.pop(0)
    _calls.append(call)

def _updateThreadCall(call):
    _calls = _get_thread_context()['calls']
    _calls[-1] = call

def lastCall(field=None):
    return _thread_lastCall(field)

def thread_get_calls():
    return _get_thread_context()['calls']

def _thread_lastCall(field=None,index=-1):
    """
    Returns the last rest call data (request, response, others).
    """
    _calls = _get_thread_context()['calls']
    if field == None:
        return _calls[index]
    return _calls[index][field]

def checklastThreadCallError(caller,index=-1):
    """
    Raises and Exception if the last call has an error. """
    lc = _thread_lastCall(index)
    if 'error' in lc and lc['error'] is not None:
        utils.raiseException(lc['errorCode'],lc['error'],caller)

def _get_call_times(call):
    et = call['elapsedTime']
    delta = call['deltaTime']
    times = {
        'elapsed':(et.microseconds + et.seconds * 1000000 )/1000,
        'delta':(delta.microseconds + delta.seconds * 1000000 )/1000,
    }
    return times 

def _thread_lastCall_time(index=-1):
    t = _thread_lastCall('elapsedTime',index=index)
    return (t.microseconds + t.seconds * 1000000 )/1000

def getLastCallAllTimes(index=-1):
    call = _thread_lastCall(index=index)
    return _get_call_times(call)

def getLastCallElapsedTime(index=-1):
    return _thread_lastCall_time(index=index)

def getConfigOrgsNames():
    """
    Get all names for the org in the config file."""
    return [configOrg['name'] for configOrg in loadConfigData()['orgs']]

##################################################################


#/Users/uormaechea/Documents/Dev/python/Industries/input/ConnectionsParams.json
_configData = None
_configDataName = None
#def setLoggingLevel(loggingLevel=logging.INFO):
#    glog().level = loggingLevel

def loadConfigData():
    global _configData,_configDataName

    if _configData is not None:
        return _configData
    
    incli = os.environ.get('INCLI')
    if incli is not None:
        setConfigFile(incli)
        return _configData
    
    root_folder = "incli"

    _configDataName = os.path.abspath(f"{root_folder}/IncliConf.json")

    if file.exists(_configDataName) == False:
        configData = {
            "folders": {
                "input":os.path.abspath(f"{root_folder}/input"),
                "debug":os.path.abspath(f"{root_folder}/debug"),
                "output":os.path.abspath(f"{root_folder}/output"),
                "log":os.path.abspath(f"{root_folder}/logs")
            },
            "orgs": []
        }

        jsonFile.write(_configDataName,configData)

    _configData = jsonFile.read(_configDataName)

    return _configData
    #utils.raiseException('NoConfigFile',"No config file has been defined.")

def getConfigVar(name):
    cd = loadConfigData()
    if name in cd:
        return cd[name]
    return None

def setConfigVar(name,value):
    cd = loadConfigData()
    cd[name] = value
    jsonFile.write(_configDataName,cd)

def delConfigVar(name):
    cd = loadConfigData()
    try:
        del cd[name]
    except KeyError:
        glog().info(f'Variable {name} is not set.')
        return
    jsonFile.write(_configDataName,cd)
    glog().info(f'Variable {name} deleted.')

def saveOrg_inConfigFile(orgName,instance_url,token=None):
    """to save in the config file Guest or Bearer Org connection params."""
    isGuest = True if token == None else False

    cd = loadConfigData()

    for org in cd['orgs']:
        if org['name'] == orgName:
            org['instance_url'] = instance_url
            if token != None:
                org['bearer'] = token
            jsonFile.write(_configDataName,cd)
            return
    
    org =     {
        "name":orgName,
        "instance_url": instance_url,
        "nameSpace": "vlocity_cmt"
    }
    if token!=None:
        org['bearer'] = token

    cd['orgs'].append(org)
    jsonFile.write(_configDataName,cd)

def deleteOrg_inConfigFile(orgName):
    cd = loadConfigData()
    cd2 = [i for i in cd['orgs'] if not (i['name'] == orgName)]
    cd['orgs'] = cd2
    jsonFile.write(_configDataName,cd)
    loadConfigData()

loggerName = 'restClient'
def glog():
    return logging.getLogger(loggerName)
def setLoggingLevel(level=logging.INFO):
    log = logging.getLogger(loggerName)
    logging.basicConfig()
    log.setLevel(level)
    pass

def setConfigFile(configFile):
    """
    Set the config file to use, and the log level"""
    global _configData,_configDataName

    if file.exists(configFile):
        _configData = jsonFile.read(configFile)
    else:
        utils.raiseException("NO_CONFIG",f"Cannot open the configuration file <{configFile}>, please provide a valid configuration file (path and name).")

    _configDataName = configFile

sfdx_lock = threading.Lock()
####CONECTION
def init(userName_or_orgAlias,connectionName=None):
    if userName_or_orgAlias  != 'ConnectionLess' and userName_or_orgAlias != None:
        print(f"Initializing connection for {userName_or_orgAlias}")
    if userName_or_orgAlias == 'ConnectionLess':
        _initMain(userName_or_orgAlias,None)
        return
    with sfdx_lock:
        inConf = False
        if userName_or_orgAlias == None:
            userName_or_orgAlias = getConfigVar('u')
            if userName_or_orgAlias == None:
                utils.raiseException('Configuration',f"No userName or Org Alias specified. Please specify a user name or org alias -> InCli -u orgAlias ...")
            inConf = True    
            print(f"{utils.CFAINT}Using default connection,{utils.CEND}{utils.CGREEN} {userName_or_orgAlias}.{utils.CEND}")

        connectionName = connectionName if connectionName is not None else userName_or_orgAlias
        if _checkAndSetConnectionIfExists(connectionName):
            return

        try:
            glog().debug(f"Calling sfdx")
            success,obj,outputs = utils.execute_force_org_display(userName_or_orgAlias)
            if success == False:
                utils.raiseException('SFDXError',f"Connection failed. {outputs.stderr}")

            if obj['Connected Status'] != 'Connected':
                utils.raiseException('SFDXError',f"Connection failed. Connected Status:{obj['Connected Status']}")

            glog().debug(f"post sfdx")

        except utils.InCliError as e:
                raise e
        except Exception as e:
                if e.strerror == 'No such file or directory':
                    utils.raiseException('SFDXError',"SFDX is not installed or it is not accesible.",other='https://developer.salesforce.com/docs/atlas.en-us.sfdx_setup.meta/sfdx_setup/sfdx_setup_install_cli.htm')
                utils.raiseException('SFDXError',e.strerror)

        if success is False:
            error = outputs.stderr.split('force:org:display')[1]
            if 'No AuthInfo found' in error:
                addText = " set in the configuration " if inConf==True else ''
                utils.raiseException('ConnectionError',f"{error}. Please authorize the org for the {userName_or_orgAlias}{addText}: sfdx auth:web:login",other="Check Connection status: sfdx force:org:list --verbose --all")
            else:
                utils.raiseException('SFDX Error',error,other='')

        if obj['Connected Status'] != 'Connected':
            utils.raiseException("ConnectionStatus",f"Connected Status for client Id {userName_or_orgAlias} is {obj['Connected Status']}",other=f"Execute the following command to refresh the token.  -")

        assert(connectionName!=None)
        assert(obj['Instance Url']!=None)
        assert(obj['Access Token']!=None)

        _initMain(connectionName,obj['Instance Url'],obj['Access Token'],username= obj['Username'])
        return obj

def initWithToken(name,url,token=None,input=None,output=None,debug=None):
    _initMain(name,url,token,input,output,debug)

def initWithConfig(orgName,isGuest=False,connectionName=None)->Boolean:
    """
    Reads the ConnectionsParams.json configuration specified by environment. If isGuest=False it will authenticate with Salesforce and obtain the token and url. If isGuest=True, it will not authenticate and the url must be provided in the ConnectionsParams.

    - environment: a string identifying the connection in the ConnectionsParams file.
    - isGuest: if True, authentication will not be performed and the ConnectionsParam requires to provide the url. 
    - name: the name of the connection. If not provided name=environment. Used when 2 connections are established for the same environment. 
    - configFolder: The folder with the ConnectionsParams file.
    - configFileName: the name of the config file. 
    - outputFolder: folder for the debuglogs
    - outputFolder: output folder. 
    """

    if orgName not in getConfigOrgsNames():
        utils.raiseException("NO_ORG",f"Org name {orgName} is not valid. Does not exist in the Configuration file.")

    if connectionName == None:
        connectionName = orgName

    orgConfig = objectUtil.getSibling(_configData['orgs'],"name",orgName).copy()

    url = orgConfig['instance_url'] if 'instance_url' in orgConfig else None
    token = orgConfig['bearer'] if 'bearer' in orgConfig else None

    if token is None:
        if 'login' in orgConfig:
           # raise ValueError(f"Environment connection parameters missing login parameters. {connectionName}")      
            url,token = _authenticate(orgConfig['login'],orgConfig['isSandBox'])

    if token is None and url is None:
        raise ValueError(f"Provide a instance_url for guest users (onboarding). {connectionName}") 

    _initMain(connectionName,url=url,token=token)

    return True

def _checkAndSetConnectionIfExists(connectionName):
    for con in _initializedConnections:
        if con['connectionName'] == connectionName:
            _get_thread_context(connectionName)
            if connectionName != 'ConnectionLess':
                glog().info(f"Connection {connectionName} set.")
            return True
    return False

def _initMain(name,url,token=None,input=None,output=None,debug=None,username=None):
    if _checkAndSetConnectionIfExists(name):
        return

    loadConfigData()

  #  currentDir = os.getcwd()
    connection = {
        'connectionName':name,
        'isGuest': True if token is None else False,
        'access_token':token,
        'instance_url':url,
        'input':input if input is not None else _configData['folders']['input'],
        'output':output if input is not None else _configData['folders']['output'],
        'debug':debug if input is not None else _configData['folders']['debug'],
        'log':debug if input is not None else _configData['folders']['log'],

        'nameSpace':'vlocity_cmt'
    }
    if username != None:
        connection['username'] = username
    _initializedConnections.append(connection)
    _get_thread_context(connection['connectionName'])
    if name != 'ConnectionLess':
        if connection['connectionName'] == username:
             print(f"{utils.CYELLOW}Connection {connection['connectionName']} initialized.{utils.CEND}")

        else:
            print(f"Connection {connection['connectionName']} initialized for username {username}.")

def getCurrentThreadConnection():
    """
    Retrieves the connectionParams for the current org. 
    """
    global _initializedConnections
    connectionName = _get_thread_context()['connectionName']
    if connectionName == None:
        utils.raiseException('ConnectionError',"No connection has been established for current thread.",other="Make sure the connection is established.")
    connection = [con for con in _initializedConnections if con['connectionName']==connectionName][0]
    #connection = objectUtil.getSibling(_initializedConnections,"name",name)
    return connection

def getNamespace():
    connection = getCurrentThreadConnection()
    return connection['nameSpace']
def inputFolder():
    return _gerFolder('input')
def outputFolder():
    return _gerFolder('output')
def debugFolder():
    return _gerFolder('debug')
def logFolder():
    return _gerFolder('log')
def _gerFolder(name):
    try:
        folder =  getCurrentThreadConnection()[name]
    except Exception as e:
        if e.args[0]['error'] == 'No default connection for thread' or e.args[0]['error'] == 'Current Connection is no set.':
            loadConfigData()
            folder = _configData['folders'][name]
        else:
            raise

    if folder[-1] != '/':
        folder = folder + '/'
    if file.exists(folder) == False:
        os.makedirs(folder)
    return folder

def _authenticate(login,isSandbox):
    if 'isSandBox' == None:
        raise ValueError(f"Environment connection parameters missing isSandBox field.")

    headers = {
        'Content-type': 'application/x-www-form-urlencoded'
    }
    server = 'test' if isSandbox else 'login'
    _get_thread_context('oauth2')
    call = requestRaw(url=f"https://{server}.salesforce.com/services/oauth2/token",method='post', parameters= login,headers=headers)
    
    lc = _thread_lastCall()
    if lc['error'] is not None:
        utils.raiseException(lc['errorCode'],lc['error'],other=lc['errorOther'])

   # connection['access_token'] = call["access_token"]
   # connection['instance_url'] = call["instance_url"]

    glog().info('getting token')
    glog().info(f"Authenticated. Instance URL is {call['instance_url'] }")
    glog().info(f"Authenticated. Bearer token {call['access_token']}")

    return call["instance_url"],call["access_token"]
#################################################################################################################################

ts = timeStats.TimeStats()
def new_time_record():
    global ts
    ts.new()

def time_print():
    global ts
    ts.print()

def checkError():
    lc = lastCall()

    if 'error' in lc and lc['error'] != None and len(lc['error'])>10:
        if 'response' in lc:
            if 'serverResponse:' in lc['response']:
                s = '{"a":' + lc['response'].split('serverResponse:')[-1] + "}"
                obj = json.loads(s)
                utils.raiseException(obj['a'][0]['errorCode'],obj['a'][0]['message'])
        utils.raiseException(lc['errorCode'],lc['error'])

def requestRaw(url,action=None,method = 'get',parameters = {},data={},headers={},access_token=None,ts_name=None):
    """
    Basic request Call. 
    
    No need to perform init(), as it does not use the connectionParams and all information needs to be provided. 
    Method parameters are self explanatory. 

    """
    
    completeUrl = url
    if action!=None:
        completeUrl = url + action

    allheaders = {
        'Content-type': 'application/json',
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, br'
    }

    if headers:
        allheaders.update(headers)

    if access_token != None:
        allheaders['Authorization'] = 'Bearer %s' % access_token

    method = method.lower()

    call = {
        'action':action,
        'url':url,
        'parameters':parameters,
        'method':method,
        'data':data,
        'error':None,
        'errorCode':None,
        'callTime':datetime.datetime.now(),
        'errorOther' : ''
    }

    if _currentConnectionName != 'ConnectionLess':
        glog().debug(f"Current Connection {_currentConnectionName}")
        _pushThreadCall(call)

    r = None

    glog().debug(f"{call['url']}{call['action']}")
    try:
        if method in ['get','delete']:
            r = requests.request(method, completeUrl, headers=allheaders, params=parameters, timeout=300)
            r.raise_for_status()
        elif method in ['post', 'patch','put']:
            r = requests.request(method, completeUrl, headers=allheaders, json=data, params=parameters, timeout=300)
            r.raise_for_status()
        else:
            utils.raiseException('NO_METHOD',f'Method {method} is not implemented in restClient.','restClient')

    except requests.exceptions.HTTPError as errh:
        call['error'] = f'serverResponse: {r.text}'
        call['errorCode'] = f"HTTPs Error: {r.status_code}"
        call['errorOther'] = f"httpError:':{errh}"
    except requests.exceptions.ConnectionError as errc:
        call['error'] = {'ConnectionError':f"{errc}"}
        call['errorCode'] = f"ConnectionError"
    except requests.exceptions.Timeout as errt:
        call['error'] = {'Timeout':f"{errt}"}
        call['errorCode'] = f"Timeout Error"    
    except requests.exceptions.RequestException as err:
        call['error'] = {'RequestException':f"{err}"}
        call['errorCode'] = f"RequestException"

    call['responseTime'] = datetime.datetime.now()
    call['deltaTime'] = call['responseTime'] - call['callTime']

    if r != None:
        glog().debug(f'Debug: API {method} call: {r.url}  status Code:{r.status_code}' ) 
        
        call['status_code'] = r.status_code
        call['elapsedTime'] = r.elapsed
        call['elapsedTimeCall'] = r.elapsed

        if ts_name != None:
            ts.time_inner(ts_name,r.elapsed)

        if r.status_code < 300 :
            if r.text == '':
                call['response'] = ''
            else:
                try:
                    call['response'] = r.json()
            
                except Exception as e:
                    glog().debug(f"warn. Response is not json  --> {e}")
                    call['response'] = {}
                    call['response'] = r.text
                
        else:
          #  glog().warn('API error when calling %s : %s' % (r.url, r.content))
            call['response'] = call['error']
    else:
        call['elapsedTime'] = call['deltaTime']
        call['elapsedTimeCall'] = call['deltaTime']
        call['status_code'] = 600
        call['response'] = 'No Response'
        if ts_name != None:
            ts.time_inner(ts_name,call['error'])

    if _currentConnectionName != 'ConnectionLess':
        _updateThreadCall(call)

    return call['response']

def requestWithConnection(action,  parameters = {}, method = 'get', data = {},headers = {},ts_name=None):
    """
    Performs a request using the current connection as configured in the file. 
    """
    connection = getCurrentThreadConnection()

    if connection == None:
        raise ValueError('restClient current org is not set. Have you init restClient?')

    return requestRaw(  url=connection['instance_url'],
                        action=action, 
                        parameters=parameters , 
                        method = method , 
                        data = data ,
                        headers  =headers,
                        access_token=connection['access_token'] if 'access_token' in connection else None,
                        ts_name=ts_name)

def callAPI_multi(action,params={} , method = 'get', data = {},headers={},ts_name=None):
    done = False

   # parameters = params
    totalElepsedTime = datetime.timedelta(microseconds=0)
    totalCalls = 0

    while done==False:
        call = requestWithConnection(action,parameters = params,method=method, data=data, headers=headers,ts_name=ts_name)

        totalElepsedTime = _thread_lastCall('elapsedTime') + totalElepsedTime
        totalCalls = totalCalls + 1

        if  call == None or _thread_lastCall('status_code')>=300:
            break
        
        glog().debug(f"callAPI_multi: <{action}>  ts:{_thread_lastCall('elapsedTime')}") 

        #For chainable integration procedures
        if type(call) is dict and 'IPResult' in call and 'vlcStatus' in call['IPResult'] and call['IPResult']['vlcStatus'] == 'InProgress':
            data['input'] = "{}"
            data['options'] = json.loads(data['options'])
            data['options']['vlcIPData'] = call['IPResult']['vlcIPData']
            data['options'] = json.dumps(data['options'])
            print(call['IPResult']['vlcIPData'])

        elif type(call) is dict and 'nexttransaction' in call :
            multiTransactionKey = call['nexttransaction']['rest']['params']['multiTransactionKey']
            data['multiTransactionKey'] = multiTransactionKey  
        else:
            done = True

    lc = _thread_lastCall()
    lc['elapsedTime'] = totalElepsedTime
    lc['totalCalls'] = totalCalls    
    _updateThreadCall(lc)

    return call

#def callAPI(action, parameters = {}, method = 'get', data = {}, headers={}):    
#    call = callAPI_multi(action,parameters,method,data,headers)
#    return call
##-------------------------------------------------------------------------------------------
# stores the request input and the reply into files in the output directory
# The file name is provided by the calling function tree "debugFile(filename)", or calculated if not provided
# the request add _req to the file name, while the reply adds _rep to the file name
# The reply can be processed -> change the json to take out data, or compute additional fields before storing it
#def callAPI_debug(action, parameters = {}, method = 'get', data = {}, headers={}):    
    return callAPI(action,parameters,method,data,headers)

def callAPI(action, parameters = {}, method = 'get', data = {}, headers={},ts_name=None):    
    call = callAPI_multi(action,parameters,method,data,headers,ts_name=ts_name)
    return call

def callSave(logFileName,logRequest=False,logReply=True,timeStamp=False,responseProcessing=None,requestProcessing=None):
    if logRequest == False and logReply == False:
        return  

    now =f"{utils.datetimeString_now('%H:%M:%S')}--"
    if  timeStamp == False:
        now = ''
    filename = f"{now}{logFileName}"
    request_filename = None
    response_filename = None

    lc = _thread_lastCall()

    if logRequest == True:
        fn = f'{filename}_req'
        request_filename = writeFile(fn,lc['data'])
        lc['requestFilePath'] = request_filename

    if logReply == True:
        if requestProcessing != None:
            requestProcessing(lc['data'])
        
        fn = f'{filename}_res'
        try:
            response_filename = writeFile(fn,lc['response'])
        except Exception as e:
            response_filename = writeFile(fn,str(lc['response']))  
        lc['responseFilePath'] = response_filename

    _updateThreadCall(lc)
    return request_filename,response_filename

def writeFile(filename,content):
    connection = getCurrentThreadConnection()

    try:
        cont = content
        if (type(content) is dict or type(content) is list ):
            return jsonFile.writeFileinFolder(outputFolder(),filename,cont)
        else:
            cont = json.dumps(cont)

    except ValueError as e:
        return file.writeFileinFolder(outputFolder(),filename,str(content))        
        
def initTest():
    init("DEVNOSCAT2",configFolder="../input")     



