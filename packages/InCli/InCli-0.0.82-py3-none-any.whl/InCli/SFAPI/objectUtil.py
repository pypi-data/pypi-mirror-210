from cmath import log
import logging
import simplejson

ident = -1
treeObjects = []
keyPath = []
def reset():
    global ident,treeObjects
    ident = -1
    treeObjects = []
    keyPath = []

def getChild(json,name):
    for key in json.keys():
        if key == name:
            return json[key]
    return ''

#renaiming and return root Json dict. 
def setKeyValue(json, selectKey, selectKeyValue,setKey, setKeyValue,logValues=False):
    sibling = parse(json, selectKey, selectKeyValue,setKey, setKeyValue,logValues)
    return json

def Id(obj):
    sibbling = getSibling(obj,'Id')
    Id = sibbling['Id']
    if 'value' in Id:
        Id = Id['value']
    return Id

def getSiblingEx(obj, selectKey, selectKeyValue,logValues=False):
    reset()
    retObject = []
    if isinstance(obj,list)==True:
        for element in obj:
            ret = parseEx(element, selectKey=selectKey, selectKeyValue=selectKeyValue,logValues=logValues)
            retObject.append(ret)
        return retObject
    return parseEx(obj, selectKey=selectKey, selectKeyValue=selectKeyValue,logValues=logValues)

def getSibling(obj, selectKey, selectKeyValue='',logValues=False,multiple=False):
    global treeObjects,keyPath
    reset()
    if isinstance(obj,list)==True:
        rets = []

        for element in obj:
            ret = parse(element, selectKey=selectKey, selectKeyValue=selectKeyValue,logValues=logValues,rets=rets)
            if ret != '':
                if multiple is False:
                    return ret
                rets.append(ret)
        if multiple is False:
            return None
        return rets
    p = parse(obj, selectKey=selectKey, selectKeyValue=selectKeyValue,logValues=logValues)
    treeObjects = treeObjects[0:ident+1]
    keyPath = keyPath[0:ident+1]

    return p

def getSibling_atPath(obj,path,field='ProductCode'):
    for p in path.split(':'):
        obj = getSibling(obj,field,p)  
    return obj

def getSiblingWhere_path(obj, selectKey,selectKeyValuePath, whereKey=None,whereValue=None,logValues=False):
    paths = selectKeyValuePath.split(':')

    result = {
        'level':-1,
        'keys':[],
        'objects':[],
        'object':None,
        'object_list':[]
    }
    for path in paths:
        index = 0
        if '|' in path:
            index = int(path.split('|')[1])
            path = path.split('|')[0]

        r = getSiblingWhere(obj, selectKey,path, whereKey,whereValue,logValues,onlyOne=False)

        if len(r['object_list'])==0:
            return None
        
        result['object'] = r['object_list'][index]
        result['object_list'] = r['object_list']
        result['objects'].extend(r['objects'])


        obj = result['object']
        
    return result

def getSiblingWhere(obj, selectKey,selectKeyValue=None, whereKey=None,whereValue=None,logValues=False,onlyOne=True):

    result = {
        'level':-1,
        'keys':[],
        'objects':[],
        'object':None,
        'object_list':[]
    }

    if isinstance(obj,list)==True:
        for element in obj:
            ret = parseWhere(element, selectKey=selectKey,selectKeyValue=selectKeyValue, whereKey=whereKey, whereValue=whereValue,logValues=logValues,result=result,onlyOne=onlyOne)
            if ret['object'] != None:
                return ret
        return None
    ret = parseWhere(obj, selectKey=selectKey, selectKeyValue=selectKeyValue,whereKey=whereKey, whereValue=whereValue,logValues=logValues,result=result,onlyOne=onlyOne)
    if ret['level']<0:
        ret['level'] = 0
    ret['keys'] = ret['keys'][0:ret['level']]
    ret['objects'] = ret['objects'][0:ret['level']]

    return ret
#------------------------
def check(json,text):
    found = False
    data = simplejson.dumps(json, indent=2)
    if text in data:
        print(text)

def getValue(obj,name):
    value = obj[name]
    if 'value' in obj[name]:
        value = obj[name]['value']  
    return value


def _match_obj(obj,key,selectKey,selectKeyValue,whereKey,whereValue):
    if key == selectKey:
        if selectKeyValue == None:
            if whereKey == None:
                return obj[key]

        else:
            value = getValue(obj,selectKey) 
            if value == selectKeyValue:
                if whereKey == None:
                    return obj
                elif whereKey in obj:
                    if whereValue == None:
                        return obj
                    if obj[whereKey] == whereValue:
                        return obj
    return None
             
#set selecte key where keyvalue is selectKeyValue and return jsonDic 
# if set Key provided, will replace the setKeyValue
def parseWhere(obj,result,selectKey='', selectKeyValue=None,whereKey=None, whereValue=None,logValues=False,onlyOne=True,_level=-1,_objects=[]):
    """
    if selectKeyValue = None, if the obj contains the selectKey is a match. 
    if whereValue = None, if the obj contains the whereKey is a match. 
    """
    #result['level']=result['level']+1
    _level = _level+1
    if len(_objects) > _level:
        _objects[_level] = obj
    else:
        _objects.append(obj)
    if len(_objects) > _level:
        _objects = _objects[0:_level+1]
  #  result['objects'].insert(result['level'], obj)
  #  if len(result['objects']) > _level:
  #      result['objects'] = result['objects'][0:_level+1]
    _object_list = []


    if isinstance(obj,dict)==False and isinstance(obj,list)==False:
        result['object'] = None
        return result

    matchfields = ['records','lineItems','childProducts','productGroups','result']
    if selectKey not in matchfields: matchfields.append(selectKey) 

    _keys = list(obj.keys())
    for key in obj.keys():
        if key not in matchfields: continue
        if 1==2:
            if len(result['keys']) > _level:
                result['keys'][_level] = key
            else:
                result['keys'].append(key)
            if len(result['keys']) > _level:
                result['keys'] = result['keys'][0:_level+1]
            print(result['keys'])
        match_obj = _match_obj(obj,key,selectKey,selectKeyValue,whereKey,whereValue)
        if match_obj!= None:
            result['object'] = match_obj
            result['level'] = _level
            result['objects'] = _objects
            return result         

        if isinstance(obj[key],dict):
            ret = parseWhere(obj[key],result,selectKey, selectKeyValue,whereKey,whereValue,logValues,onlyOne=onlyOne,_level=_level)
            if ret['object'] != None:  
                return ret

        if isinstance(obj[key],list):
            for x,l in enumerate(obj[key]):
                ret = parseWhere(l,result,selectKey,selectKeyValue,whereKey,whereValue,logValues,onlyOne=onlyOne,_level=_level)
                if ret['object'] != None :
                    if onlyOne or len(ret['object_list'])>0:
                        return ret
                    else:
                        _object_list.append(ret['object'])    

            if len(_object_list)>0:
                result['object_list'] = _object_list
                return result
   # result['level'] = result['level']-1

    result['object'] = None
    return result

def parse(json, selectKey='', selectKeyValue='',setKey='', setKeyValue='',logValues=False,rets=None):
    global ident,treeObjects
    ident=ident+1
    treeObjects.insert(ident, json)
#    print(ident)


    if isinstance(json,dict)==False and isinstance(json,list)==False:
        return ''  #continue

    for key in json.keys():
        keyPath.insert(ident,key)
        if key == 'PricebookEntry':
            continue

        if key == 'ProductCode' and logValues == True:
            printIdent(f'{key}  {json[key]}')

        if key == selectKey:
            if selectKeyValue == '':
                return json
            value = getValue(json,selectKey) 

         #   printIdent(f'{key}  {value}')

            if value == selectKeyValue:
                if setKey!='':
                    if setKeyValue == None:
                        return json[setKey]
                    if json[setKey] != None and type(json[setKey]) is dict and 'value' in json[setKey]:
                        json[setKey]['value'] = setKeyValue
                    else:
                        json[setKey] = setKeyValue
           #     ident = ident-1

                return json 

        if isinstance(json[key],dict):
            ret = parse(json[key],selectKey, selectKeyValue,setKey,setKeyValue)
          #  ident = ident-1

            if ret != '':
                return ret if rets is None else rets.append(json)

        if isinstance(json[key],list):
            for l in json[key]:
                ret = parse(l,selectKey,selectKeyValue,setKey,setKeyValue)
            #    ident = ident-1
  
                if ret != '':
                    return ret if rets is None else rets.append(json)
    ident = ident-1

    return ''

#set selecte key where keyvalue is selectKeyValue and return jsonDic 
# if set Key provided, will replace the setKeyValue
def parseEx(json, selectKey='', selectKeyValue='',setKey='', setKeyValue='',logValues=False,retObjects=[]):
    global ident
    ident=ident+1
  
    #check(json,"AttributeCategory")
    #check(json,"attributeCategories")

    if isinstance(json,dict)==False and isinstance(json,list)==False:
        return ''  #continue

    for key in json.keys():
        if key == 'PricebookEntry':
            continue

        if key == 'ProductCode' and logValues == True:
            printIdent(f'{key}  {json[key]}')

        if key == selectKey:
            value = json[selectKey]
            if 'value' in json[selectKey]:
                value = json[selectKey]['value']
            if value == selectKeyValue:
                if setKey!='':
                    if setKeyValue == None:
                        return json[setKey]
                    if json[setKey] != None and type(json[setKey]) is dict and 'value' in json[setKey]:
                        json[setKey]['value'] = setKeyValue
                    else:
                        json[setKey] = setKeyValue
                #return json     
                retObjects.append(json[selectKey])

        if isinstance(json[key],dict):
            ret = parse(json[key],selectKey, selectKeyValue,setKey,setKeyValue,retObjects)
            if ret != '':
                retObjects.append(ret)
                #return ret
            ident = ident-1

        if isinstance(json[key],list):
            for l in json[key]:
                ret = parse(l,selectKey,selectKeyValue,setKey,setKeyValue,retObjects)
                if ret != '':
                    retObjects.append(json)
                    #return ret
                ident = ident-1
    return retObjects

def addNode(path,node,level):
    if len(path) > level:
        path[level] = node
    else:
        path.append(node) 

def getField(obj,path,separator=':'):
    """
    Get field in object for a path. 
    - path: the path
    - separator: for the path. a:b:c by default. 
    """
    paths = path.split(separator)
    _obj = obj
    for p in paths:
        if p in _obj:
            _obj = _obj[p]
        else:
            return None
    return _obj

def getpaths_toField(json,fieldValue,level=0,paths=[],path=[]):
    try:
        if type(json) is dict:
            for key in json.keys():
                addNode(path,key,level)

                if isinstance(json[key],dict):
                    getpaths_toField(json[key],fieldValue,level+1,paths,path)
                if isinstance(json[key],list):
                    for element in json[key]:
                        getpaths_toField(element,fieldValue,level+1,paths,path)
                if (json[key]==fieldValue):
                    addNode(path,key,level+1)
                    path =  path[0:level+1]
                    str = ".".join(path)
                    paths.append(str)
    except Exception as e:
        logging.error(f'{e}')
    return paths

def printIdent(string):
    global ident
    str = ''
    for x in range(ident):
        str = str + ' '
    print(str + string)


def getNode(obj,path):
    if (path == ""):
        return obj
    
    nodeNames = path.split(".")

    for nodeName in nodeNames:
        if '*' in nodeName:
            print()
        if nodeName.isnumeric():
            index = int(nodeName)
            if index>len(obj):
                return "Error"
            obj = obj[index]

        else:
            if nodeName in obj:
                obj = obj[nodeName]
            else:
                return "Error: " + nodeName + " not present in Object"

    return obj


def replace_everywhere_in_obj(obj,find,replace):
    strAll = simplejson.dumps(obj)
    stItems2 = strAll.replace(find,replace)
    return simplejson.loads(stItems2)


