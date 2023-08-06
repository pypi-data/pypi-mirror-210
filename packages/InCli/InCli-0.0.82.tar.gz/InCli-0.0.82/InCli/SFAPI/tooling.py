from . import restClient,Sobjects,utils,thread
import simplejson

v = 'v51.0'
def query(q):
    action = f"/services/data/{v}/tooling/query/?q={q}"
    call = restClient.callAPI(action)
    checkError()
    for r in call['records']: r.pop('attributes')

    return call

def query_threaded(q,values,search="$$$",raiseEx=True,th=10):
    result = []

    def do_work(value):
        q1 = q.replace(search,value)
        res = query(q1)
        return res

    def on_done(res,result):
        result.append(res['records'][0])

    thread.execute_threaded(values,result,do_work,on_done,threads=th)

    return result

def get(sobject,id):
    action = f"/services/data/{v}/tooling/sobjects/{sobject}/{id}"
    call = restClient.callAPI(action)
    return call

def checkError():
    call = restClient.lastCall()['response']
    if 'serverResponse' in call:
        sr = call.split('serverResponse:')[1]
        srj = simplejson.loads(str(sr))
        utils.raiseException(srj[0]['errorCode'],srj[0]['message'])  

def post(sobject,data):
    action = f"/services/data/{v}/tooling/sobjects/{sobject}"
    call = restClient.callAPI(action,method='post',data=data)
    checkError()
    return call

def delete(sobject,id):
    action = f"/services/data/{v}/tooling/sobjects/{sobject}/{id}"
    call = restClient.callAPI(action,method='delete')
    checkError()
    return call

def patch(sobject,id,data):
    action = f"/services/data/{v}/tooling/sobjects/{sobject}/{id}"
    call = restClient.callAPI(action,method='patch',data=data)
    checkError()
    return call

def IdF(object,fieldF,multiple=False):
    chunks = fieldF.split(":")
    if len(chunks)<2:
        utils.raiseException("fieldF error",f"Not a valid fieldF name:value  {fieldF}")
    q = f"select id from {object} where {chunks[0]} = '{chunks[1]}'"
    call = query(q)   
    if len(call['records']) == 0:
        return None
    if multiple:
        return call['records']
    return call['records'][0]['Id']

def describe(sobject):
    action =f"/services/data/{v}/tooling/sobjects/{sobject}/describe/"
    call = restClient.callAPI(action)
    utils.printFormated(call['fields'],"label:name:type")

    print()
    

def queryTraceFlg(q):
    q = "select id, TracedEntityId,logtype, startdate, expirationdate, debuglevelid, debuglevel.apexcode, debuglevel.visualforce from TraceFlag limit 10"
    call = query(q)
    print()
    
def completions():
    action =f"/services/data/{v}/tooling/completions?type=apex"

    allheaders = {
        'Content-type': 'application/json',
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, br'
        ,'Accept':'application/json'
    }
    call = restClient.callAPI(action,headers=allheaders)
    filename = restClient.callSave("completions.json")
    print()

    'serverResponse: [{"message":"Invalid Accept header */*. Must be one of the following values: [com.force.swag.rest.format.FormatImpl@fd630a47, com.force.swag.rest.format.FormatImpl@b5980ad8]","errorCode":"INVALID_TYPE"}]'

def executeAnonymous(code=None):
    if code == None:
        code ="System.debug('Test');"
  #  code = """
  #  Map<String, Object> input = new Map<String, Object>{'methodName' => 'refreshBatchJobLists'};
  #  vlocity_cmt.TelcoAdminConsoleController controllerClass = new vlocity_cmt.TelcoAdminConsoleController();
  #  controllerClass.setParameters(JSON.serialize(input));
  #  System.debug(controllerClass.invokeMethod());
  #  """
    action =f"/services/data/{v}/tooling/executeAnonymous?anonymousBody={code}"
    call = restClient.callAPI(action)
    print()
