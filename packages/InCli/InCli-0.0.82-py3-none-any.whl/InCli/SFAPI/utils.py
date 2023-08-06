from datetime import datetime,timedelta
from logging import log
import logging
from . import objectUtil
import inspect,simplejson
import os,sys
from posixpath import dirname
import time
#import pytz
import subprocess,traceback


CBLACK = "\033[0;30m"
CRED = "\033[0;31m"
CGREEN = "\033[0;32m"
CBROWN = "\033[0;33m"
CBLUE = "\033[0;34m"
CPURPLE = "\033[0;35m"
CCYAN = "\033[0;36m"
CLIGHT_GRAY = "\033[0;37m"
CDARK_GRAY = "\033[1;30m"
CLIGHT_RED = "\033[1;31m"
CLIGHT_GREEN = "\033[1;32m"
CYELLOW = "\033[1;33m"
CLIGHT_BLUE = "\033[1;34m"
CLIGHT_PURPLE = "\033[1;35m"
CLIGHT_CYAN = "\033[1;36m"
CLIGHT_WHITE = "\033[1;37m"
CWHITE = '\33[37m'
CBOLD = "\033[1m"
CFAINT = "\033[2m"
CITALIC = "\033[3m"
CUNDERLINE = "\033[4m"
CBLINK = "\033[5m"
CNEGATIVE = "\033[7m"
CCROSSED = "\033[9m"
CEND = "\033[0m"

CBGBLUE = "\033[104m"

#https://stackoverflow.com/questions/287871/how-do-i-print-colored-text-to-the-terminal
#----------------------------------------------------------------------------------------------------
def stringifyUrlParameters(parameters,exclude,initSeparator='?'):
  isFirst = True

  ret = ''
  for name in parameters:
    if name in exclude:
      continue
    if(parameters[name] == None):
      continue
    separator = initSeparator if isFirst == True else '&'
    value = parameters[name]
    if isinstance(value, str) == False:
      value = simplejson.dumps(value)
    paramStr = f'{separator}{name}={value}'
    ret = ret + paramStr
    isFirst = False

  return ret

def executeCommand(command):
    is_windows = sys.platform.startswith('win')
    if is_windows == True:
        list_files = subprocess.run(command,capture_output=True,text=True,shell=True)
    else:
        list_files = subprocess.run(command,capture_output=True,text=True)

    print(f"{CFAINT}{list_files.stderr}{CEND}")
    if "ERROR" in list_files.stderr:
        error = list_files.stderr.split('ERROR')[1]
        raiseException("SFDXError",f"ERROR{error}")
    return list_files

def execute_force_org_display(userName_or_orgAlias):
    def getValue(field):
        if field in line:
            chunks = line.split(field)
            val = chunks[1].strip()
            obj[field]=val
    output = executeCommand(["sfdx","force:org:display","-u", userName_or_orgAlias])
    if output.stdout == '':
        return False,None,output

    lines = output.stdout.splitlines()

    obj = {}
    for line in lines:
        getValue('Access Token')
        getValue('Connected Status')
        getValue('Instance Url')
        getValue('Username')


    return True,obj,output

def executeCommandParse(command):
    output = executeCommand(command)

    if output.stdout == '':
        return False,output

    obj = {}

    sl = output.stdout.splitlines()
    namesline = sl[1]
    lenLine = sl[2]
    lenLines = lenLine.split(' ')
    ll =[0]
    ll = ll+[len(lenline)+2 for lenline in lenLines if lenline!='']
    ll[-1] = ll[-1]-2

    pos = []
    position = 0
    for l in ll:
        position = position + l
        pos.append(position)


    names = []
    for x in range(len(pos)-1):
        name = namesline[pos[x]:pos[x+1]].strip()
      #  print(namesline[pos[x]:pos[x+1]])
        if name == '':
            name = f"{x}"
        names.append(name)

    objs =[]
    for y in range(3,len(sl)-1):
        obj = {}
        objs.append(obj)
        for x in range(len(pos)-1):
            value = sl[y][pos[x]:pos[x+1]].strip()
            obj[names[x]] = value

    return True,objs
#----------------------------------------------------------------------------------------------------
def extendedField(field):
    """
    An extended field is a field defined as "field:value"
    returns a json containing {'field':field,'value':value}
    If the parameter is just a value, the field is set to Id  'value' --> 'Id:value'
    """
    if field is None:
        return None

    sp = field.split(':')
    if len(sp) == 1:
        return {
            'field':'Id',
            'value':sp[0]
        }
    return {
        'field':sp[0],
        'value':sp[1]
    }
#----------------------------------------------------------------------------------------------------
class InCliError(Exception):
    pass

def exception_2_InCliException(exception):
  #  aa = inspect.stack()[2]

    error = {
        'errorCode':'CODE',
        'error':exception.args[0]
    }   
    error['json'] = message = simplejson.dumps(error, indent=2, ensure_ascii=False)
#    print(traceback.format_exc())
    return InCliError(error)

def raiseException(errorCode,error,module=None,other=None):
    aa = inspect.stack()[1]
    error = {
        'errorCode':errorCode,
        'error':error,
        'module':f"{aa[1].split('/')[-1]}  {aa[3]}  {aa[2]}",
    }
    if other is not None:
        error['other'] = other
    
    error['json'] = message = simplejson.dumps(error, indent=2, ensure_ascii=False)

    raise InCliError(error)

def to_CliError(e):
    if type(e) == InCliError: return e
    er = {
        'errorCode':'',
        'error':'',
        'module':''
    }
    er['error'] = e.args[0]['error'] if 'error' in e.args[0] else e.args[0]
    er['errorCode'] = e.args[0]['errorCode'] if 'errorCode' in e.args[0] else ''

    return InCliError(er)

def printException(exception):
    print()
    print(type(exception).__name__)
    if type(exception) == InCliError:
        _str = exception.args[0]['json']
    else:
        error = {
            "errorCode":type(exception).__name__,
            "error":str(exception)
        }
        _str = simplejson.dumps(error, indent=2, ensure_ascii=False)
    logging.error(_str)

def print_json(obj,filename=None):
   # input_data = simplejson.loads(obj)
    json_formatted_str = simplejson.dumps(obj, indent=2, ensure_ascii=False)

    if filename != None:
        original_stdout = sys.stdout
        _filename = f"{filename}.json"
        with open(_filename, 'w') as f:
            sys.stdout = f 
            print(json_formatted_str)
            sys.stdout = original_stdout 
            print()
            print(f"   File {_filename} created.")
    else:  
        print(json_formatted_str)
#----------------------------------------------------------------------------------------------------

def throwOrLog(message,raiseEx=True,dumps=False):
    """
    if raiseEx is True, it raises an error. IF not logs the error. 
    - message: the error messages. Can be a dictionary
    - raiseEx: boolean
    """
    if dumps == True:
        message = simplejson.dumps(message, indent=2)

    if raiseEx == True:
        logging.error(message)
        raise ValueError(message)
    else:
        logging.info(message)
        return None
#----------------------------------------------------------------------------------------------------
def printJSON(obj,delNull=False):
    if delNull == True:
        obj = deleteNulls(obj)
    d = simplejson.dumps(obj, indent=2)
    logging.debug(d)
    print()

def deleteNulls(obj,systemFields=True,nulls=True,delAttributes=True):
    systemFields= ['OwnerId','IsDeleted','CreatedDate','CreatedById','LastModifiedDate','LastModifiedById','LastViewedDate','LastReferencedDate','SystemModstamp','attributes']
  #  if systemFields == False:
  #      systemFields = True
  #      systemFields = ['attributes']

    if systemFields == True and nulls == True:
        return obj
    if 'records' in obj:
        obj = obj['records']
    if type(obj) is list:
        res = []
        for ob in obj:
            res.append(deleteNulls(ob,systemFields,nulls))
        return res

    res = {}
    for key in obj.keys():
        if systemFields == False:
            if key in systemFields:
                continue
        if delAttributes == True:
            if key in ['attributes']:
                continue
        if type(obj[key]) is dict:
            res[key] = deleteNulls(obj[key],systemFields,nulls)
        else:
            if obj[key] is None and nulls is False:
                continue
            res[key] = obj[key]
    return res

def printFormated(records,fieldsString=None,rename=None,exclude=None,checkNumber=False,separator=':',print_renames=True):
    """
    - fieldsString: format field%name:field2%name2:field3
        field is the field in the obj. Name is how it will be printed (the short version). 
        name3 is equivalent to field3-field3
    - rename : field%name:field2%name2
    """
    if records is None or len(records) == 0:
        print('No records to print')
        return

    if type(records) is dict:
        records = [records]
    print()
    if 'records' in records:
        records = records['records']

    if fieldsString == None:
        fieldsString = separator.join(records[0].keys())
    fields = fieldsString.split(separator)
    if exclude != None:
        fields2 = [field for field in fields if field not in exclude.split(separator)]
        fields = fields2

    _renames = {}
    if rename != None:
        renames = rename.split(':')
        for ren in renames:
            chunks = ren.split('%')
            _renames[chunks[0]] = chunks[1]
            if print_renames: print( CFAINT +  f"Column {chunks[0]} as {chunks[1]}" +CEND)
        print()
    
    _fields = {}
    for field in fields:
        v = {}
        v['obj_name'] = field
        v['print_name'] = _renames[field] if field in _renames else field
        v['size'] = len(v['print_name'])
        _fields[field] = v

    #calculate _fileds size based in value.
    for record in records:
        for key in _fields.keys():
            size = 0
            value = objectUtil.getField(record,key,'.')
            if value is not None:
                size = len(str(value))
                if size > _fields[key]['size']:
                    _fields[key]['size'] = size

    #print header
    spacing = 2    
    line = ''
    for key in _fields.keys():
        if key == "__color__":
            continue
        field = _fields[key]        
        value = field['print_name']

        line =  f"{line}{value:{int(field['size']+spacing)}}" 
    print(CUNDERLINE+line+CEND)

    for record in records:
        line = ''
        for key in _fields.keys():
            field = _fields[key]    

            if key == "__color__":
                continue

            val = objectUtil.getField(record,key,'.')
            val = '' if val is None else str(val) 
            padding = int(field['size']+spacing)
 #           print(f"{padding}  {field['size']}")
            if checkNumber and _isInt(val):
                line = f"{line}{int(val):>{padding-1}} "
            elif checkNumber and _isFloat(val):
                line = f"{line}{float(val):>{padding-1}.2f} "
            else:
                line = f"{line}{val:{padding}}"
        if '__color__' in record:
            if record['__color__'] != '':
                line = record['__color__'] + line + CEND

        print(line)

def _isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

def _isFloat(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def datetimeString_now(format = '%Y-%m-%dT%H:%M:%S'):
    ts = time.time()
    dt = datetime.fromtimestamp(ts).strftime(format)
    return dt

def datetimeString_to_timestamp(str,format=None):
    if str == None: 
        return None
    if format == None:
        format = '%Y-%m-%dT%H:%M:%S.%f%z'
    #str = '2021-08-31T22:23:24.000+0000'   '%Y-%m-%dT%H:%M:%S.%f%z'
    dt = datetime.strptime(str,format)
    ts = datetime.timestamp(dt) * 1000
    
    return int(ts)

def today_date(format="%Y-%m-%d"):
    today = datetime.today()
    return today.strftime(format)  

def datetimestr_around(str,minutes,format = '%Y-%m-%dT%H:%M:%S'):
    dt = datetime.strptime(str,format)
    dt_before = dt - timedelta(minutes=minutes) 
    dt_after = dt + timedelta(minutes=minutes) 
    return dt_before.strftime(format),dt_after.strftime(format)

def future_date(years=None,days=None,minutes=None,format="%Y-%m-%d"):
    today = datetime.today()
    if years!=None:  future = today.replace(year=today.year + years)
    if days!=None:    future = today.replace(day=today.day + days)
    return future.strftime(format)  

def callerPythonFileFolder():
    caller_filepath = inspect.currentframe().f_back.f_code.co_filename
    caller_filefolder = os.path.dirname(caller_filepath)
    if caller_filefolder.endswith('SFAPI'):
        caller_filefolder = dirname(caller_filefolder)
    return caller_filefolder

def getEntryDirectory():
    return sys.path[0]

def currentFilePath():
    frame = inspect.stack()[1]
    filename = frame[0].f_code.co_filename
    dirname = os.path.dirname(filename)
    return dirname

def getFieldc(var,field,onlyOne=True):
    return Id(var,field=field,onlyOne=True)

def getRecord(obj):

    if 'records' in obj:
        return getRecord(obj['records'])
    if 'result' in obj:
        return getRecord(obj['result'])
    if 'fields' in obj:
        return getRecord(obj['fields'])
    return obj

def Id(var):
    return selectField(var,field='Id',onlyOne=True)

def selectField(var,field='Id',onlyOne=True):
    if type(var) is str:
        return var
    if (type(var) is dict):
        if field in var:
            if 'value' in var[field]:
                return var[field]['value']
            return var[field]

        if 'records' in var:
            return selectField(var['records'],field,onlyOne)
        if 'result' in var:
            return selectField(var['result'],field,onlyOne)
        if 'fields' in var:
            return selectField(var['fields'],field,onlyOne)
    if type(var) == list:
        if onlyOne == True:
            if len(var)>1:
                logging.warn(f"There is more than 1 element in the list {len(var)}, returning Id from first one")
            return selectField(var[0],field,onlyOne)
        else:
            _ids = []
            i=0
            while i<len(var):
                _ids.append(selectField(var[i],field,onlyOne))
                i = i + 1
            return _ids

def Obj(var,onlyOne=True):
    if (type(var) is dict):
        if 'records' in var:
            return Obj(var['records'],onlyOne)
        else :
            return var

    if type(var) == list:
        if onlyOne == True:
            if len(var)>1:
                logging.warn(f"There is more than 1 element in the list {len(var)}, returning Id from first one")
            return Obj(var[0],onlyOne)
        else:
            _objs = []
            i=0
            while i<len(var):
                _objs.append(Obj(var[i],onlyOne))
                i = i + 1
            return _objs

def computeTimes(call,name,times,_type=None):
    global _counter

    debugTimes = {}

    time = call['elapsedTime']
    sec = time.microseconds + time.seconds * 1000000 
    times[name]=sec

    debugTimes['ElapsedCall'] = sec

    if 'debugIP' == _type and 'IPResult' in call:

        if 'debugLog' in call['IPResult']:
            for key in call['IPResult']:
                if key.endswith('Debug'):
                    debugTimes[f'{key}_ElapsedTime'] = call['IPResult'][key]['deltaTime'] * 1000
                    debugTimes[f'{key}_ElapsedTimeCPU'] = call['IPResult'][key]['ElapsedTimeCPU'] * 1000

        if 'elapsedTimeActual' in call['IPResult']:
            debugTimes['elapsedTimeActual'] = call['IPResult']['elapsedTimeActual'] * 1000
        if 'elapsedTimeCPU' in call['IPResult']:
            debugTimes['elapsedTimeCPU'] = call['IPResult']['elapsedTimeCPU'] * 1000
            #print(f" {_counter} , {sec}  , {elapsedTimeActual}  , {sec-timeActual} ,{apigeeTime}")
            #_counter = _counter + 1
            #return
        print(debugTimes)

    print (sec)
    return debugTimes

def _is_match(objs,x,y,field):
    ox = objs[x]
    oy = objs[y]

    if 'ident' not in ox: return False
    if 'ident' not in oy: return False

    if ox['ident'] != oy['ident'] : return False

    if ox[field] != oy[field]:  return False
    return True
def _is_next_link(objs,field,chain_start,link_lenght,posible_link_start):
    for z in range(0,link_lenght):
        if posible_link_start+z >= len(objs): return False
        if _is_match(objs,chain_start+z,posible_link_start+z,field) == False: return False

    return True

def get_all_loops(objs,field):

    all_loops = []
    _all_loops = []

    lastX = 0

    for x,val in enumerate(objs):
        if x < lastX:    continue
        if objs[x]['type'] == 'SOQL':continue
        loop_lenght = None
        lastDelta = 0
        loop = []

        max = 30
        is_loop = False
        
        ox = objs[x]
        if 'timeStamp' in ox and ox['timeStamp'][0] == 10189843723:
            a=1
        for y in range(x+1,len(objs)):
            if is_loop == False and y-x>=max:
                break
            oy = objs[y]
            if 'ident' in ox and ox['ident'] > oy['ident']:
                break        
            #    print(f"{x}:{ox['output']} {y}:{oy['output']}")
  
            
            if _is_match(objs,x,y,field):
                chain_start = x
                next_link_start = y
                link_lenght = y-x
                loop = []

                while True:
                    if _is_next_link(objs,field,chain_start,link_lenght,next_link_start):
                        if len(loop) == 0: loop.append(x)
                        loop.append(next_link_start)
                        next_link_start = next_link_start + link_lenght
                        lastX = next_link_start
                    else:
                        break
                if len(loop) > 0:  
                    all_loops.append(loop)
                    break


    return all_loops
    print(all_loops)
def get_all_loops1(objs,field):

    all_loops = []
    lastX = 0
  #  if objs==None:
  #      a=1
 #   lenObj = len(objs)
    for x,val in enumerate(objs):
        if x <= lastX:    continue
        loop_lenght = None
        lastDelta = 0
        loop = []
   #     if 'output' not in objs[x]:
   #         oo = objs[x]
   #     objx = objs[x]['output']

        max = 30
        is_loop = False

        for y in range(x+1,len(objs)):
            if is_loop == False and y-x>=max:
                break
     #       if 'output' not in objs[y]:
     #           oo = objs[y]
     #       objy=objs[y]['output']

     #       if field not in objs[y]:
     #           _o = objs[y]
            ox = objs[x]
            oy = objs[y]
            if _is_match(objs,x,y,field):
          #  if 'ident' in objs[y] and 'ident' in objs[x] and objs[y]['ident'] == objs[x]['ident'] and objs[y][field] == objs[x][field]:
      #          line = objs[y][field]
                posible_link_start = x
                posible_link_end = y
                if y == 1445:
                    a=1
                if y == 1575:
                    a=1
                if loop_lenght == None:
                    loop_lenght = y-x
                    lastDelta = loop_lenght
                else:   lastDelta = y - lastX
                
                is_loop = True
                if lastDelta == loop_lenght:
                    for z in range(0,loop_lenght):
                        if y+z >= len(objs): is_loop=False
                        elif objs[y+z][field] != objs[x+z][field]: is_loop = False

                    if is_loop == False:   break
                    if is_loop == True:
                        if len(loop) == 0:   loop.append(y-loop_lenght)
                        loop.append(y)
                else:  break
                if is_loop == True:     lastX = y 
         #   else:
         #       if is_loop:
         #           is_loop = False
         #           break
        if len(loop) > 0:  all_loops.append(loop)

    return all_loops
def datetime_now_string(format = '%Y-%m-%dT%H:%M:%S%z',addMinutes=0,addDays=0):
    tz2 = datetime.now().astimezone()
    if addMinutes != 0:
        tz2 = tz2 + timedelta(minutes = addMinutes)
    if addDays != 0:
        tz2 = tz2 + timedelta(days= addDays)
    st = tz2.strftime(format)

    return st
