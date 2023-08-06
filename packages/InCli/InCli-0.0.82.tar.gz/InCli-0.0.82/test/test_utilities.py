import unittest,simplejson
from InCli.SFAPI import restClient,query,Sobjects

class Test_Utilities(unittest.TestCase):
    def test_limits(self):
        restClient.init('DEVNOSCAT2')
        action = '/services/data/v51.0/limits'
        res = restClient.callAPI(action)

        print()


    def test_id(self):
        restClient.init('DEVNOSCAT2')
        action = '/services/data/v51.0'
        res = restClient.callAPI(action)

        print()

    def test_id(self):
        restClient.init('DEVNOSCAT2')
        action = '/services/data/v51.0'
        res = restClient.callAPI(action)
        for key in res.keys():
            print()
            action = res[key]
            res1 = restClient.callAPI(action)
            print(action)
            print(res1)

        print()
    
    def test_select(self):
        restClient.init('DEVNOSCAT4')

        q = f"select fields(all) from vlocity_cmt__VlocityTrackingEntry__c order by vlocity_cmt__Timestamp__c desc limit 100"
        res = query.query(q)
        for r in res['records']:
            ll = simplejson.loads(r['vlocity_cmt__Data__c'])
            json_formatted_str = simplejson.dumps(ll, indent=2, ensure_ascii=False)
            print(json_formatted_str)
            print()
    def test_delete_logs(self):
        restClient.init('NOSDEV')

        userId = Sobjects.IdF('User','username:uormaechea_nosdev@nos.pt')

        q = f"select Id from ApexLog where LogUserId='{userId}' "
        res = query.query(q)

        id_list = [record['Id'] for record in res['records']]
        
        Sobjects.deleteMultiple('ApexLog',id_list)
        print()

    def delete(self,q):
        res = query.query(q)

        id_list = [record['Id'] for record in res['records']]
        
        Sobjects.deleteMultiple('ApexLog',id_list)
        print()

    def test_delete_something(self):
        restClient.init('DEVNOSCAT4')

        q = "select Id from vlocity_cmt__CachedAPIResponse__c  "
        self.delete(q)

    def test_delete_fulfil(self):
        restClient.init('DEVNOSCAT4')

        q = "select Id from vlocity_cmt__FulfilmentRequestDecompRelationship__c  "
        self.delete(q)

        q = "select Id from vlocity_cmt__FulfilmentRequestLineDecompRelationship__c  "
        self.delete(q)
        
        q = "select Id from vlocity_cmt__FulfilmentRequest__c  "
        self.delete(q)

        q = "select Id from vlocity_cmt__InventoryItem__c  "
        self.delete(q)

        q = "select Id from vlocity_cmt__InventoryItemDecompositionRelationship__c  "
        self.delete(q)

        q = "select Id from AssetRelationship  "
        self.delete(q)

        q = "select Id from vlocity_cmt__OrderAppliedPromotionItem__c  "
        self.delete(q)

    def test_call_something(self):
        restClient.init('NOSQSM')

       # res = restClient.requestWithConnection(action='resource/1641908190000/vlocity_cmt__OmniscriptLwcCompiler')
        res = restClient.requestRaw('https://nos--nosqms.sandbox.my.salesforce.com/resource/1641908190000/vlocity_cmt__OmniscriptLwcCompiler')

        print(res)
        print()

        

    def test_iJoin_code(self):
        restClient.init('NOSQSM')

        name = 'd9b0fe97-8d5a-b2b6-8293-f5abe8f4b675'

        q = f"select name, Content__c from Dataframe__c where name ='{name}' "

        res = query.query(q)

        print(res['records'][0]['Content__c'])
       # print(res)
        print()