from . import restClient,utils,query,thread
import simplejson,sys
#------------------------------------------------------------------------------------------------------------------------------------------------
def dr(bundleName,inputData):
   """
   - bundleName: Name of the Data Raptor Bundle
   - inputData: input Data to the DR
   """
   action = f'/services/apexrest/{restClient.getNamespace()}/v2/DataRaptor'

   data = {
       "bundleName" : bundleName, 
       "objectList": inputData
   }
   call = restClient.callAPI(action, method="post", data=data)
   return call
#------------------------------------------------------------------------------------------------------------------------------------------------
def ipResponse(name,input,options=None,field=None):
   """
   Calls the IP and returns the response object
   - name: type_subtype
   - input: input data json.
   - options: the options json. 
   - field: if specified will return the value of the 'field' in response.  
   """
   res = ip(name,input,options)
   IPResult = res['IPResult']
   if 'response' in IPResult:
      IPResult = IPResult['response']

   if field != None and field in IPResult:
      return IPResult[field]
   return IPResult
#------------------------------------------------------------------------------------------------------------------------------------------------
def ip(name,input,options=None):
   """
   Calls the IP 
   - name: type_subtype
   - input: input data json.
   - options: the options json. 
   """
   action = f'/services/apexrest/vlocity_cmt/v1/GenericInvoke/vlocity_cmt.IntegrationProcedureService/{name}'
   data = {
      "sMethodName":name,
      "sClassName":"vlocity_cmt.IntegrationProcedureService",
      }

   if type(input) is dict:
      input = simplejson.dumps(input)

   data['input'] = input
   if options == None:
      options = "{}"
   else:
      if type(options) is dict:
         options = simplejson.dumps(options)      
   data['options'] =  options


   call = restClient.callAPI(action=action,data=data,method='post')
   lc = restClient.callSave('data1234',logRequest=True,logReply=False)
   utils.printJSON(call)
   #print(call)
   return call
#------------------------------------------------------------------------------------------------------------------------------------------------
def ip_response(call,field=None):
   """
   Get the response from the IP call response. 
   """
   IPResult = call['IPResult']
   if 'response' in IPResult:
      IPResult = IPResult['response']

   if field != None and field in IPResult:
      return IPResult[field]
   return IPResult
#------------------------------------------------------------------------------------------------------------------------------------------------
def get_IP_definitions():
   """
   Get the IP definitions. 
   Returns the procedure name, the IP name and the steps as strings. 
   """
   q = f"""select 
               Id,
               vlocity_cmt__Content__c,
               vlocity_cmt__OmniScriptId__r.name,
               vlocity_cmt__OmniScriptId__r.vlocity_cmt__ProcedureKey__c 
               from vlocity_cmt__OmniScriptDefinition__c 
               where vlocity_cmt__OmniScriptId__c in (select Id from vlocity_cmt__OmniScript__c where vlocity_cmt__OmniProcessType__c = 'Integration Procedure' and vlocity_cmt__IsActive__c = TRUE) """

   res = query.query(q)

   ip_definitions = []

   for record in res['records']:
      ip_definition = {
            'vlocity_cmt__ProcedureKey__c': record['vlocity_cmt__OmniScriptId__r']['vlocity_cmt__ProcedureKey__c'],
            'Name':                         record['vlocity_cmt__OmniScriptId__r']['Name'],
            'steps':                        []
      }
      ip_definitions.append(ip_definition)
      content = simplejson.loads(record['vlocity_cmt__Content__c'])
      for child in content['children']:
            ip_definition['steps'].append(child['name'])

   return ip_definitions

def call_chainable_ip(name,input,options=None):
   action = f'/services/apexrest/callipasynch/v1/{name}'
   action = f'/services/apexrest/callip/v1/{name}'
   action = f'/services/apexrest/callip/v2/{name}'
   action = f'/services/apexrest/callip/v3/{name}'

   data = {
      "sMethodName":name,
      "sClassName":"vlocity_cmt.IntegrationProcedureService",
      }

   data['input'] = input
   if options == None:
      options = {}
   data['options'] =  options


   call = restClient.callAPI(action=action,data=data,method='post')
   return call
#------------------------------------------------------------------------------------------------------------------------------------------------
def remoteClass(className,method,input,options=None):
   """
   Calls a remote APEX class inside Salesforce 
   - className: the callable APEX class name
   - method: the method to invoke.
   - input: the options json. 
   - options: the options json 
   """
   action = f'/services/apexrest/vlocity_cmt/v1/GenericInvoke/{className}/{method}'

   if type(input) is dict:
      input = simplejson.dumps(input)

   if options == None:
      options = {
         "postTransformBundle":"",
         "preTransformBundle":"",
         "useQueueableApexRemoting":False,
         "ignoreCache":False,
         "vlcClass":"B2BCmexAppHandler",
         "useContinuation":False
         }         
      
   data = {
      "sMethodName":method,
      "sClassName":className,
      "input":input,
      "options":simplejson.dumps(options)
      }

   call = restClient.callAPI(action=action,data=data,method='post')
   return call
#------------------------------------------------------------------------------------------------------------------------------------------------
def get_attachments(limit=100):
   q = f"select Id,Name,Body,CreatedById,BodyLength,LastModifiedDate from attachment where Name = 'OmniScriptFullJSON.json' limit {limit}"
   res = query.query(q)

   return res

def get_ip_attachments(date1=None,date2=None,limit=None,Id=None):
   #date1 = "2023-01-01T00:00:00"
   #date2 = "2023-02-01T00:00:00"
   if date1 == None and limit == None and Id == None:
       return False
   
   if date1 != None:
      w2 = f" and LastModifiedDate<{date2}.00Z " if date2 != None else ''
      where = f" where vlocity_cmt__DRBundleName__c = 'None Specified' and vlocity_cmt__AsyncApexJobId__c = null and vlocity_cmt__GlobalKey__c != null and LastModifiedDate>{date1}.00Z {w2}"
   if limit !=None:
      where = f" order by LastModifiedDate desc limit {limit}"
   if Id != None:
      where = f" where Id = '{Id}'"

   q0 = f"select Id,vlocity_cmt__GlobalKey__c from  vlocity_cmt__DRBulkData__c {where}"
   bulk_data_records = query.query(q0)

   idl =None
   if limit != None:
      idl = [r['Id'] for r in bulk_data_records['records']]
      q = f"select ID,Body,CreatedById,ParentId,LastModifiedDate from Attachment where ParentId in ($$$IN$$$)"
      #q = f"select ID,Body,ParentId,LastModifiedDate from Attachment where ParentId in ({query.IN_clause(idl)})"

      print(len(q))

   else:
      q = f"select ID,Body,ParentId,LastModifiedDate from Attachment where ParentId in (select Id from  vlocity_cmt__DRBulkData__c {where} )"

   attachments = query.query(q,base64=True,in_list=idl)

   for attachment in attachments['records']:
      attachment['vlocity_cmt__GlobalKey__c'] = [bdr['vlocity_cmt__GlobalKey__c'] for bdr in bulk_data_records['records'] if bdr['Id']==attachment['ParentId']][0]

   return attachments

def process_attachments(attachments,contains=None):
   if attachments == False:
       return False
   ip_definitions = _get_IP_definitions()

   def do_work(attachment):
      attachment['log'] = restClient.requestWithConnection(action=attachment['Body'])
      return attachment
   
   def on_done(attachment,result):
      a=1

   thread.execute_threaded(attachments['records'],None,do_work,on_done,threads=num_threads)

   result = []

   for attachment in attachments['records']:
      if 'log' not in attachment:
          continue
      log = attachment['log']

      if contains != None:
         cont = False
         log_str = simplejson.dumps(log)
         for word in contains.split(','):
              if word in log_str:
                  cont = True
                  break
         if cont == False:
             continue
         
      if 'vlcDebug' in log:
            possible_ips = _findMatch(log,ip_definitions)
            if len(possible_ips) >0:  attachment['possible'] = possible_ips
            else: attachment['best_match'] = _bestMach(log,ip_definitions)
            result.append(attachment)
          #  print("",end='.')


   found = [attachment for attachment in attachments['records'] if 'possible' in attachment]
   best_match = [attachment for attachment in attachments['records'] if 'best_match' in attachment]
   processed_list = sorted(found, key=lambda d: d['LastModifiedDate'])
   processed_list.reverse()
  # processed_list = reversed(sorted(found, key=lambda d: d['LastModifiedDate'])) 
  # newlist = found


   return processed_list

def print_attachments(date1=None,date2=None,limit=None,Id=None,toFile=False,only_not_finished=False,contains=None):
   attachments = get_ip_attachments(date1,date2,limit,Id)
   processed_list = process_attachments(attachments,contains=contains)

   print_list = []
   record = None

   CreatedById = [r['CreatedById'] for r in processed_list]
   q = "select Name,Id from User where Id in ($$$IN$$$)"
   res2 = query.query(q,in_list=CreatedById)
   
   for y,record in enumerate(processed_list):
      for x,pos in enumerate(record['possible']):
            if len(pos['missing']) == 0:
               rec = {'name':"?","type":"?"}
            else:
               rec = pos['missing'][0]
            p = {
               'LastModifiedDate':record['LastModifiedDate'][0:19] if x==0 else "",
         #      'Id':record['Id'],
               'ParentId':record['ParentId'] if x==0 else "",
               'CreatedById':[r['Name'] for r in res2['records'] if r['Id'] == record['CreatedById']][0],
               'vlocity_cmt__GlobalKey__c':record['vlocity_cmt__GlobalKey__c'] if x==0 else "",
               'IP':pos['ip'],
               'debug':pos['executed'],
             #  'missing_num':len(pos['missing']),
              # 'missing' :",".join([f"{rec['name']}-[{rec['type']}]" for rec in pos['missing']])
               'next Step':f"{rec['name']}-[{rec['type']}]" 

            }
            if only_not_finished and len(pos['missing']) <=1 and 'Response Action' in p['next Step']: continue
            if p['debug'].endswith("10") and 'Response Action' in p['next Step']:  p['__color__'] = utils.CGREEN + utils.CFAINT
            if p['debug'].endswith("_0") and 'Response Action' in p['next Step']:  p['__color__'] = utils.CYELLOW + utils.CFAINT

            print_list.append(p)

   utils.printFormated(print_list)

   if Id != None and record!= None:
      print()
      for step in record['possible'][0]['ip_steps']:
         if step in record['possible'][0]['debug_steps']:
            print(f"     {utils.CGREEN}{step}{utils.CEND}")
         else:
            print(f"     {step}")

      filename = Id if toFile == True else None
      utils.print_json(record['log'],filename=filename)

   return print_list

num_threads=15

def _get_IP_definitions():
   q = f"""select 
               Id,
               vlocity_cmt__Content__c,
               vlocity_cmt__OmniScriptId__r.name,
               vlocity_cmt__OmniScriptId__r.vlocity_cmt__ProcedureKey__c 
               from vlocity_cmt__OmniScriptDefinition__c 
               where vlocity_cmt__OmniScriptId__c in (select Id from vlocity_cmt__OmniScript__c where vlocity_cmt__OmniProcessType__c = 'Integration Procedure' and vlocity_cmt__IsActive__c = TRUE) """

   res = query.query(q)

   ip_definitions = []

   for record in res['records']:
      try:
         ip_definition = {
               'vlocity_cmt__ProcedureKey__c': record['vlocity_cmt__OmniScriptId__r']['vlocity_cmt__ProcedureKey__c'],
               'Name':                         record['vlocity_cmt__OmniScriptId__r']['Name'],
               'steps':                        [],
               'steps_names':[]
         }

         ip_definitions.append(ip_definition)
         content = simplejson.loads(record['vlocity_cmt__Content__c'])

         def getChildStep(child,parent_conditional='',parent_loop=False):
               if 'installCoverageEligibility' == child['name']:
                  a=1
               step = {
                  'name':child['name'],
                  'label':child['propSetMap']['label'] if 'label' in child['propSetMap'] else '',
                  'executionConditionalFormula':child['propSetMap']['executionConditionalFormula'] if 'executionConditionalFormula' in child['propSetMap'] else '',
                  'chainOnStep':child['propSetMap']['chainOnStep'] if 'chainOnStep' in child['propSetMap'] else False,
                  'indexInParent':child['indexInParent'],
                  'type':child['type'],
                  'loop_element':parent_loop
               }    
               if parent_conditional != '':
                  step['executionConditionalFormula'] = f"{step['executionConditionalFormula']} - {parent_conditional}"

               if child['type'] == 'Loop Block':
                  step['loop_element'] = True

               return step

         def addChildren(child,parent_conditional='',parent_loop=False):
               step = getChildStep(child,parent_conditional,parent_loop)
               ip_definition['steps'].append(step)
               ip_definition['steps_names'].append(step['name'])

               if 'children' in child and len(child['children'])>0:
                  for child1 in child['children']:
                     if 'eleArray' in child1:
                           for eleChild in child1['eleArray']:
                              parent_loop = True if child['type'] == 'Loop Block' or parent_loop == True  else False
                              addChildren(eleChild,parent_conditional=step['executionConditionalFormula'],parent_loop=parent_loop)
                     else:
                           a=1

         for child in content['children']:
               addChildren(child)
      except Exception as e:
          print(f"IP_Definition Error: {e}")
   return ip_definitions

def _findMatch(log,ip_definitions):
   possible_ips = []

   sequenceExecute = log['vlcDebug']['executionSequence']
   sequence = [key[0:-6] for key in log.keys() if key.endswith('Status') and type(log[key]) is bool]
   if sorted(sequence) == sorted(sequenceExecute):
      a=1
   else:
      a=1

   for ip_definition in ip_definitions:           
      if len(sequence) > len(ip_definition['steps_names']):  continue

      if ip_definition['vlocity_cmt__ProcedureKey__c'] == 'woo_getBundleNBOOffer':
            a=1          
      found = True
      for step in sequence:
            if step not in ip_definition['steps_names']: 
               found = False
               break
      if found: 
            posible = {
               'ip':ip_definition['vlocity_cmt__ProcedureKey__c'],
               'executed':"",
               'ip_steps':ip_definition['steps_names'],
               'debug_steps':sequence,
               'missing':[]
            }
            for ip_step in ip_definition['steps']:
               ex = "1" if ip_step['name'] in sequence or ip_step['name'] in sequenceExecute else "0"
               if '0' not in posible['executed']:
                  if ex == "0" and ip_step['executionConditionalFormula'] != "": 
                        ex = '_'
                  if ex == "0" and ip_step['loop_element'] == True: ex = 'L'
               if ex == '0': posible['missing'].append(ip_step)

               posible['executed'] = f"{posible['executed']}{ex}"
            if '1' not in posible['executed']: continue
            if posible['executed'][0]=='0': 
               continue
            if '01' in posible['executed']:
               continue
            possible_ips.append(posible)

   return possible_ips

def _bestMach(log,ip_definitions):
   possible_ips = []

   sequenceExecute = log['vlcDebug']['executionSequence']
   sequence = [key[0:-6] for key in log.keys() if key.endswith('Status') and type(log[key]) is bool]

   for ip_definition in ip_definitions:
      if ip_definition['vlocity_cmt__ProcedureKey__c'] == 'iUse_submitResumeOrder':
            a=1
      score = 0

      executed = ""
      for ip_step in ip_definition['steps']:
            ex = "1" if ip_step['name'] in sequence else "0"
            if ex == "0" and ip_step['executionConditionalFormula'] != "": ex = '_'
            if ex == "0" and ip_step['loop_element'] == True: ex = 'L' 
            executed = f"{executed}{ex}"

      missed = []
      for seq in sequence:
            if seq not in ip_definition['steps_names']:
               executed = f"{executed}*"
               missed.append(seq)
      score = executed.count('1')

      if score>0:
            ip = {
               'name':ip_definition['vlocity_cmt__ProcedureKey__c'],
               'score':score,
               'ip_steps':len(ip_definition['steps']),
               'size':len(sequence),
               'execured':executed,
               'ip_stesps':ip_definition['steps'],
               'debug_steps':sequence,
               'missed':missed
            }
            possible_ips.append(ip)
   
   possible_ips_sorted = sorted(possible_ips, key=lambda d: d['score'])
   possible_ips_sorted.reverse()

   return possible_ips_sorted

