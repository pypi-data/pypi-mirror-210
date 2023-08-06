import unittest,simplejson
from InCli.SFAPI import restClient,query,Sobjects,utils,tooling


class Test_z_compareOrgs(unittest.TestCase):
    definitions = []
    def test_limits(self):
        restClient.init('NOSQSM')

        sObjectName = 'product2'
      #  sObjectName = 'Family__c'
      #  sObjectName = 'Spectrum__c'
      #  sObjectName = 'Level__c'
      #  sObjectName =  'Product__c'
        sObjectName = 'ProductCorporate__c'
        sObjectName = 'Order'
        sObjectName = 'Account'

        prod_qsm = Sobjects.describe(sObjectName)

        self.definitions = self.get_custom_fields(sObjectName)

        restClient.init('demo240')
        prod_demo240 = Sobjects.describe(sObjectName)

        prod_qsm_field_names = [p['name'] for p in prod_qsm['fields']]
        prod_demo240_field_names = [p['name'] for p in prod_demo240['fields']]

        diff_list = list (set(prod_qsm_field_names).difference(prod_demo240_field_names))
        for field in prod_qsm['fields']:
            name = field['name']
            if name not in prod_demo240_field_names:
                print('-------------------------------------------------------')
                print(name)
                print(field['type'])
                try:
                    data = self.calc_customField(sObjectName,field)
                    #data = self.customField(sObjectName,field)
                    call = self.create_custom_field(data)
                    self.set_field_permission(sObjectName,data=data)
                    print('DONE!!!!!!')
                except Exception as e:
                    if 'errorCode' in e.args[0] and e.args[0]['errorCode'] == 'DUPLICATE_DEVELOPER_NAME':
                        continue
                    utils.printException(e)


        print()

    def create_custom_field(self,data):
        action ='/services/data/v54.0/tooling/sobjects/CustomField'
        method = 'post'

        call= restClient.callAPI(action=action,method=method,data=data)
        restClient.checkError()
        print(call)
        return call

    def get_custom_field(self,sobject,field):
        data = { "FullName": f"{sobject}.{field}"}
        action ='/services/data/v54.0/tooling/sobjects/CustomField'
        method = 'get'

        call= restClient.callAPI(action=action,method=method,data=data)
        restClient.checkError()
        print(call)

    def get_field_definition(self):

        res = tooling.query(f"select fields(all) from FieldDefinition WHERE EntityDefinition.QualifiedApiName IN ('Product2') limit 100")

        res2 = tooling.query(f"SELECT NamespacePrefix, DeveloperName, TableEnumOrId,ManageableState FROM CustomField ")
        for r in res2['records']:
            print(f"{r['TableEnumOrId']}  {r['NamespacePrefix']} {r['DeveloperName']}")
            if 'Availability_SLA_Formula' == r['DeveloperName']:
                res3 = tooling.query(f"SELECT NamespacePrefix, DeveloperName, TableEnumOrId,ManageableState,Metadata FROM CustomField where DeveloperName='{r['DeveloperName']}' limit 1")

        print()

    def get_custom_fields(self,sobject,namespace=None):
        
        tableEnumOrId = sobject
        is_custom_object = False

        if '__c' in sobject:
            is_custom_object == True
            obj = sobject.split('__')[0]
            res2 = tooling.query(f"Select Id, DeveloperName, NamespacePrefix From CustomObject where DeveloperName = '{obj}' limit 10")
            if len(res2['records']) == 0:
                utils.raiseException("RECORDS_NOT_FOUND",f"No records found for {sobject} {namespace}")
            tableEnumOrId = res2['records'][0]['Id']
        
        ns = f" and NamespacePrefix = {namespace}" if namespace != None else f" and NamespacePrefix = null "

        res2 = tooling.query(f"SELECT NamespacePrefix, DeveloperName, TableEnumOrId,ManageableState FROM CustomField where TableEnumOrId = '{tableEnumOrId}'  {ns}")

        devNames = [r['DeveloperName'] for r in res2['records']]

        q = f"SELECT NamespacePrefix, DeveloperName, TableEnumOrId,ManageableState,Metadata FROM CustomField where DeveloperName='$$$' and TableEnumOrId='{tableEnumOrId}' {ns} limit 1"
        res4 = tooling.query_threaded(q,devNames)

        for r in res2['records']:
            r['Metadata'] = [m for m in res4 if m['DeveloperName']==r['DeveloperName']][0]
            r['type'] = r['Metadata']['Metadata']['type']
            r['formula'] = True if 'formula' in r['Metadata']['Metadata'] and r['Metadata']['Metadata']['formula']!=None else False


        formulas = [r for r in res2['records'] if r['formula']==True]
        rest = [r for r in res2['records'] if r['formula']==False]

        rest.extend(formulas)
        utils.printFormated(rest,"NamespacePrefix:DeveloperName:TableEnumOrId:type:formula")

        return rest
        for r in res2['records']:
            print(f"{r['TableEnumOrId']}  {r['NamespacePrefix']} {r['DeveloperName']}")
            res3 = tooling.query(f"SELECT NamespacePrefix, DeveloperName, TableEnumOrId,ManageableState,Metadata FROM CustomField where DeveloperName='{r['DeveloperName']}' limit 1")
            r['Metadata'] = res3['records'][0]

        return res2

    def get_field_definition2(self,sobject,fieldName,namespace=None):

        ns = f" and NamespacePrefix = {namespace}" if namespace != None else f" and NamespacePrefix = null "
        res3 = tooling.query(f"SELECT NamespacePrefix, DeveloperName, TableEnumOrId,ManageableState,Metadata FROM CustomField where DeveloperName='{fieldName}' and TableEnumOrId='{sobject}' {ns} limit 1")

        print() 
        
    def no_nulls(self,obj):
        obj2 = {}
        for key in obj.keys():
            if obj[key] != None:
                if type(obj[key]) == dict:
                    obj2[key]= self.no_nulls(obj[key])
                else:
                    obj2[key] = obj[key]
        return obj2

    def calc_customField(self,sobject,field):
        name = field['name'].split('__c')[0]
        metadata = [d for d in self.definitions if d['DeveloperName'] == name][0]['Metadata']['Metadata']

        metadata2 = self.no_nulls(metadata)

        if field['name'] == 'Data_da_ultima_oportunidade__c':
            a=1
            metadata2['summaryOperation'] = metadata2['summaryOperation'].title()
            metadata2.pop('summaryFilterItems')
        data = { "FullName": f"{sobject}.{field['name']}", 
                "Metadata": metadata2
                } 

        data_str = simplejson.dumps(data, indent=2, ensure_ascii=False)

        print(data_str)
      #  print(data)
        return data

    def customField(self,sobject,field):
        if field['dependentPicklist']:
            a=1
        if field['relationshipName'] != None:
            a=1
        if field['relationshipOrder']!=None:
            a=1
        if len(field['referenceTo'])>0:
            a=1
        data = { "FullName": f"{sobject}.{field['name']}", 
                "Metadata": { "label": field['label'], 
                              "description": "my new test field", 
                              "required": False, 
                              "externalId": field['externalId'], 
                              "type": field['type'], 
                              "length": field['length'] if 'length' in field else None,
                              "unique":field['unique']
                            } 
                }
        if data['Metadata']['type'] == 'string' : 
            data['Metadata']['type'] = 'Text'

        if data['Metadata']['type'] == 'boolean' : 
            data['Metadata']['type'] = 'Checkbox'
            data['Metadata'].pop("length")
            data['Metadata']['defaultValue'] = field['defaultValue']

        if data['Metadata']['type'] == 'double' : 
            data['Metadata']['type'] = 'Number'
            data['Metadata']['precision'] = field['precision']
        #    data['Metadata']['digits'] = field['digits']
            data['Metadata']['scale'] = field['scale']
        #    data['Metadata']['length'] = field['precision']
            data['Metadata'].pop("length")

        if data['Metadata']['type'] == 'percent' : 
            data['Metadata']['type'] = 'Percent'
            data['Metadata']['precision'] = field['precision']
         #   data['Metadata']['digits'] = field['digits']
            data['Metadata']['scale'] = field['scale']

        if data['Metadata']['type'] == 'url' : 
            data['Metadata']['type'] = 'Url'
            data['Metadata'].pop("length")

        if data['Metadata']['type'] == 'textarea' : 
            data['Metadata']['type'] = 'TextArea'
            data['Metadata'].pop("length")


        if field['calculatedFormula'] != None:
      #      data['Metadata']['type'] = 'FORMULA'
         #   data['Metadata']['scale']=field['scale']
         #   data['Metadata']['calculatedFormula'] = field['calculatedFormula'] 
         #   data['Metadata']['calculated']=field['calculated']
         #   data['Metadata']['formulaTreatNullNumberAsZero']=field['formulaTreatNullNumberAsZero']
            data['Metadata']['formula']=field['calculatedFormula']
            if "length" in data['Metadata']: data['Metadata'].pop("length")

        #    if data['Metadata']['type'] == 'Text':
        #        data['Metadata']['type'] = 'Formula(Text)'
            a=1

        
        if data['Metadata']['type'] == 'reference':
            data['Metadata']['type'] = 'Lookup'
            data['Metadata']['relationshipName'] = field['relationshipName']
            data['Metadata']['referenceTo'] = field['referenceTo'][0]
            data['Metadata']['referenceTargetField'] = field['referenceTargetField'] 
            data['Metadata']['relationshipOrder'] = field['relationshipOrder'] 
            data['Metadata'].pop("length")

        if data['Metadata']['type'] == 'picklist':
            data['Metadata']['type'] = 'Picklist'
            data['Metadata'].pop("length")
            data['Metadata']['valueSet'] = {
                'restricted': field['restrictedPicklist'],
                'valueSetDefinition': {
                    'sorted': False,
                    'value': []
                }
            }
            for value in field['picklistValues']:
                value = {
                    'fullName': value['value'],
                    'default': value['defaultValue'],
                    'label': value['label']
                }
                data['Metadata']['valueSet']['valueSetDefinition']['value'].append(value)

        if data['Metadata']['type'] == 'multipicklist' : 
            data['Metadata']['type'] = 'MultiselectPicklist'
            data['Metadata'].pop("length")

            data['Metadata']['valueSet'] = {
                'restricted': field['restrictedPicklist'],
                'valueSetDefinition': {
                    'visibleLines':10,
                    'sorted': False,
                    'value': []
                }
            }
            for value in field['picklistValues']:
                value = {
                    'fullName': value['value'],
                    'default': value['defaultValue'],
                    'label': value['label']
                }
                data['Metadata']['valueSet']['valueSetDefinition']['value'].append(value)      

        print(data)
        return data

    def set_field_permission(self,sobject,data):
        action='/services/data/v54.0/composite/'
        method =  'post'        
        data={
            "allOrNone": True,
            "compositeRequest": [
                {
                    "referenceId": "Profile",
                    "url": "/services/data/v54.0/query/?q=SELECT+Id+FROM+Profile+Where+Name='System Administrator'",
                    "method": "GET"
                },
                {
                    "referenceId": "PermissionSet",
                    "url": "/services/data/v54.0/query/?q=SELECT+Id+FROM+PermissionSet+WHERE+ProfileId='@{Profile.records[0].Id}'",
                    "method": "GET"
                },
                {
                    "referenceId": "NewFieldPermission",
                    "body": {
                        "ParentId": "@{PermissionSet.records[0].Id}",
                        "SobjectType": sobject,
                        "Field": data["FullName"],
                        "PermissionsEdit": "true",
                        "PermissionsRead": "true"
                    },
                    "url": "/services/data/v54.0/sobjects/FieldPermissions/",
                    "method": "POST"
                }
            ]
        }
        call = restClient.callAPI(action=action,method=method,data=data)
        return call



