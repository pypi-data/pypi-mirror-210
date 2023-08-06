import unittest,simplejson
from InCli import InCli
from InCli.SFAPI import file,DR_IP,restClient,query,utils,thread,jsonFile,file_csv

class Test_DR_IP(unittest.TestCase):
    options = {
        "isDebug": True,
        "chainable": True,
        "resetCache": False,
        "ignoreCache": True,
        "queueableChainable": False,
        "useQueueableApexRemoting": False
    }     
    def test_IP(self):
        #restClient.init('DTI')
        restClient.init('NOSDEV')

        
        call = DR_IP.ip("custom_GetTrialPromos",input={},options=self.options)
        lc = restClient.lastCall()

        print()

    def test_IP_test(self):
        restClient.init('DTI')

        input = {
            "cartId": "8010Q0000035ec1QAA"
        }
        
        call = DR_IP.ip("unai_chainableIpsTest",input=input,options=self.options)


        print()

    key ='d18120d8-9217-43f9-72b5-9fce1b3cdcd8'
    def test_attachment(self):
        restClient.init('DTI')

        q = f"select fields(all) from vlocity_cmt__DRBulkData__c where vlocity_cmt__GlobalKey__c = '{self.key}' limit 20"
        call0 = query.query(q)
        print(call0)
        
        q2 = f"select fields(all) from Attachment where ParentId ='{call0['records'][0]['Id']}' limit 10"
        call2 = query.query(q2)
        print(call2['records'][0]['Id'])
        attachmentId = call2['records'][0]['Id']
     #   attachmentId = '00P0Q00000JWEzGUAX'
        action = call2['records'][0]['Body']
        call = restClient.requestWithConnection(action=action)

        filepath = restClient.callSave("AttachementX123")

        print()

    def test_finish_call(self):
        restClient.init('DTI')
        input = "{}"

        options1 = self.options.copy()
        options1['vlcIPData'] = self.key

        call = DR_IP.ip("unai_chainableIpsTest",input=input,options=options1)

        print()

    def test_dr_bundle(self):
        restClient.init('DTI')

        q = "SELECT Name, Id, LastModifiedDate, LastModifiedBy.Name, CreatedDate, CreatedBy.Name, vlocity_cmt__Type__c, vlocity_cmt__InputType__c, vlocity_cmt__OutputType__c, vlocity_cmt__Description__c, LastModifiedById FROM vlocity_cmt__DRBundle__c USING SCOPE Everything WHERE vlocity_cmt__Type__c != 'Migration' AND  vlocity_cmt__Type__c != 'Export (Component)' ORDER BY Name"

        q = "SELECT Name, Id, LastModifiedDate, LastModifiedBy.Name, CreatedDate, CreatedBy.Name, vlocity_cmt__Type__c, vlocity_cmt__InputType__c, vlocity_cmt__OutputType__c, vlocity_cmt__Description__c, LastModifiedById FROM vlocity_cmt__DRBundle__c ORDER BY Name"

        res = query.query(q)
        
        out = []
        for record in res['records']:
            o = {
                "Name":record['Name'],
                "type":record['vlocity_cmt__Type__c']

            }
            out.append(o)
        utils.printFormated(out)
        print()

    def bestMach(self,log,ip_definitions):
        possible_ips = []

        sequenceExecute = log['vlcDebug']['executionSequence']
        sequence = [key[0:-6] for key in log.keys() if key.endswith('Status') and type(log[key]) is bool]
     #   for key in sequence:
     #       if key not in log:
     #           sequence.remove(key)

        for ip_definition in ip_definitions:
            if ip_definition['vlocity_cmt__ProcedureKey__c'] == 'iUse_submitResumeOrder':
                a=1
            score = 0

            executed = ""
            for ip_step in ip_definition['steps']:
                ex = "1" if ip_step['name'] in sequence else "0"
                if ex == "0" and ip_step['executionConditionalFormula'] != "": ex = 'C'
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


    def findMatch(self,log,ip_definitions):
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
                            ex = 'C'
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

    def test_find_stooped_VIPs_threaded(self):
        restClient.init('NOSPRD')


        if 1==2:
            q0 = f"select Id,vlocity_cmt__GlobalKey__c from  vlocity_cmt__DRBulkData__c where vlocity_cmt__DRBundleName__c = 'None Specified' and vlocity_cmt__AsyncApexJobId__c = null and vlocity_cmt__GlobalKey__c != null order by Id desc limit 200"
            bulk_data_records = query.query(q0)

            bulk_ids = [record['Id'] for record in bulk_data_records['records']]

            q = f"select ID,Body,ParentId,LastModifiedDate from Attachment where ParentId in ({query.IN_clause(bulk_ids)})"
            q = f"select fields(all) from Attachment where ParentId in ({query.IN_clause(bulk_ids)}) limit 200"

            attachments = query.query(q,base64=True)

            for attachment in attachments['records']:
                attachment['vlocity_cmt__GlobalKey__c'] = [bdr['vlocity_cmt__GlobalKey__c'] for bdr in bulk_data_records['records'] if bdr['Id']==attachment['ParentId']][0]

            jsonFile.write('attachments_123',attachments)
            
        else:
            attachments = jsonFile.read('attachments_123')

        self.process_attachements_threaded(attachments)

    def test_process_one(self):
        restClient.init('DTI')

        bulkDataId = 'a2J0Q000001Qim1UAC'
        q0 = f"select Id,vlocity_cmt__GlobalKey__c from  vlocity_cmt__DRBulkData__c where Id='{bulkDataId}'"
        bulk_data_records = query.query(q0)

        q = f"select fields(all) from Attachment where ParentId = '{bulkDataId}' limit 1"
        attachments = query.query_base64(q)

        for attachment in attachments['records']:
            attachment['vlocity_cmt__GlobalKey__c'] = [bdr['vlocity_cmt__GlobalKey__c'] for bdr in bulk_data_records['records'] if bdr['Id']==attachment['ParentId']][0]

        self.process_attachements_threaded(attachments)


    def test_print_attachments(self):
        restClient.init('NOSQSM')
        date1 = "2023-02-24"


        q0 = f"select Id,vlocity_cmt__GlobalKey__c from  vlocity_cmt__DRBulkData__c where vlocity_cmt__DRBundleName__c = 'None Specified' and vlocity_cmt__AsyncApexJobId__c = null and vlocity_cmt__GlobalKey__c != null and LastModifiedDate>{date1}T00:00:00.00Z "
        bulk_data_records = query.query(q0)

        q = f"select ID,Body,ParentId,LastModifiedDate from Attachment where ParentId in (select Id from  vlocity_cmt__DRBulkData__c where vlocity_cmt__DRBundleName__c = 'None Specified' and vlocity_cmt__AsyncApexJobId__c = null and vlocity_cmt__GlobalKey__c != null and LastModifiedDate>{date1}T00:00:00.00Z)"

        attachments = query.query(q,base64=True)   

        for attachment in attachments['records']:
            attachment['vlocity_cmt__GlobalKey__c'] = [bdr['vlocity_cmt__GlobalKey__c'] for bdr in bulk_data_records['records'] if bdr['Id']==attachment['ParentId']][0]
            attachment['log'] = restClient.requestWithConnection(action=attachment['Body'])
            if 'UpdateOrderStatusToPaid_RA' in attachment['log']:
       #     if 'GetOrderServiceAccount_DEA' in attachment['log']:

                print(attachment['log']['OrderDetailsNode']['OrderNumber'])
                json_formatted_str = simplejson.dumps(attachment['log'], indent=2, ensure_ascii=False)

                print(json_formatted_str)
        print()

    def test_date(self):
        restClient.init('NOSPRD')
        date1 = "2023-01-01"
        date2 = "2023-02-01"


        q0 = f"select Id,vlocity_cmt__GlobalKey__c from  vlocity_cmt__DRBulkData__c where vlocity_cmt__DRBundleName__c = 'None Specified' and vlocity_cmt__AsyncApexJobId__c = null and vlocity_cmt__GlobalKey__c != null and LastModifiedDate>{date1}T00:00:00.00Z and LastModifiedDate<{date2}T00:00:00.00Z"
        bulk_data_records = query.query(q0)

        q = f"select ID,Body,ParentId,LastModifiedDate from Attachment where ParentId in (select Id from  vlocity_cmt__DRBulkData__c where vlocity_cmt__DRBundleName__c = 'None Specified' and vlocity_cmt__AsyncApexJobId__c = null and vlocity_cmt__GlobalKey__c != null and LastModifiedDate>{date1}T00:00:00.00Z and LastModifiedDate<{date2}T00:00:00.00Z)"

        attachments = query.query(q,base64=True)

        for attachment in attachments['records']:
            attachment['vlocity_cmt__GlobalKey__c'] = [bdr['vlocity_cmt__GlobalKey__c'] for bdr in bulk_data_records['records'] if bdr['Id']==attachment['ParentId']][0]

        self.process_attachements_threaded(attachments)


        print()



    num_threads=15
    def process_attachements_threaded(self,attachments):
        ip_definitions = self.get_IP_definitions()

        result = []

        def do_work(attachment):
            attachment['log'] = restClient.requestWithConnection(action=attachment['Body'])
            return attachment

        def on_done(attachment,result):
            log = attachment['log']
            if 'vlcDebug' in log:
                possible_ips =self.findMatch(log,ip_definitions)
                if len(possible_ips) >0:  attachment['possible'] = possible_ips
                else: attachment['best_match'] = self.bestMach(log,ip_definitions)
                result.append(attachment)

        thread.execute_threaded(attachments['records'],result,do_work,on_done,threads=self.num_threads)

        found = [attachment for attachment in attachments['records'] if 'possible' in attachment]
        best_match = [attachment for attachment in attachments['records'] if 'best_match' in attachment]

        newlist = sorted(found, key=lambda d: d['LastModifiedDate']) 

        print_list = []
        for record in newlist:
            for pos in record['possible']:
                p = {
                    'LastModifiedDate':record['LastModifiedDate'][0:19],
                    'Id':record['Id'],
                    'ParentId':record['ParentId'],
                    'vlocity_cmt__GlobalKey__c':record['vlocity_cmt__GlobalKey__c'],
                    'IP':pos['ip'],
                    'debug':pos['executed'],
                    'missing':",".join([f"{rec['name']}-[{rec['type']}]" for rec in pos['missing']])
                }
                print_list.append(p)


        file_csv.write('Attachment_records_Jan',print_list)
        utils.printFormated(print_list)

        print()


    def test_find_stooped_VIPs(self):
        restClient.init('NOSQSM')

        q0 = f"select Id,vlocity_cmt__GlobalKey__c from  vlocity_cmt__DRBulkData__c where vlocity_cmt__DRBundleName__c = 'None Specified' and vlocity_cmt__AsyncApexJobId__c = null and vlocity_cmt__GlobalKey__c != null"
        bulk_data_records = query.query(q0)
        bdrs={}
        for bdr in bulk_data_records['records']: bdrs[bdr['Id']] = bdr['vlocity_cmt__GlobalKey__c']
        print(len(bdrs))

        q = f"select ID,Body,ParentId from Attachment where ParentId in (select Id from  vlocity_cmt__DRBulkData__c where vlocity_cmt__DRBundleName__c = 'None Specified' and vlocity_cmt__AsyncApexJobId__c = null and vlocity_cmt__GlobalKey__c != null)"

        attachments = query.query(q,base64=True)

        for attachment in attachments['records']:
            attachment['vlocity_cmt__GlobalKey__c'] = bdrs[attachment['ParentId']]

        ip_definitions = self.get_IP_definitions()

        ip_definitions_woo = [ip_definition for ip_definition in ip_definitions if ip_definition['vlocity_cmt__ProcedureKey__c'].startswith('woo_')]

        for ip_definition_woo in ip_definitions_woo:
            ip_definition_woo['steps'] = set(ip_definition_woo['steps'])
        for attachment in attachments['records']:
            log = restClient.requestWithConnection(action=attachment['Body'])
            possible_ips = []

            if 'vlcDebug' in log:
                sequence = log['vlcDebug']['executionSequence']
                possible_ips =self.findMatch(sequence,ip_definitions_woo)
                if len(possible_ips) >0:
                    bulk_data_record = [record for record in bulk_data_records['records'] if record['Id']==attachment['ParentId']][0].copy()
                    bulk_data_record['possible'] = possible_ips
                    utils.printFormated(bulk_data_record)
            #    else:
            #        posibles = self.bestMach(sequence,ip_definitions)
           #         utils.printFormated(posibles)

    def get_IP_definitions(self):
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
                'steps':                        [],
                'steps_names':[]
            }
            if ip_definition['vlocity_cmt__ProcedureKey__c'] == 'MACD_ichangeOrderProcessAsynch':
                a=1
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

        return ip_definitions
