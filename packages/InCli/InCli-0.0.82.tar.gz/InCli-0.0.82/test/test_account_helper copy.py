import unittest,simplejson
from InCli import InCli
from InCli.SFAPI import account,restClient,CPQ,query,file_csv,jsonFile

class Test_Account(unittest.TestCase):
    def test_main(self):
        name = 'User_a2'
        accountF = f"Name:{name}"

        restClient.init('DTI')
        restClient.setLoggingLevel()
        accountId = account.create_Id(name,recordTypeName='Consumer',checkExists=True)

        dele = account.deleteOrders(accountF)

        cartId = CPQ.createCart(accountF,'Name:B2C Price List','name')
        orders = account.getOrdersId(accountF)
        self.assertTrue(orders!=None)

        dele = account.deleteOrders(accountF)
        orders = account.getOrdersId(accountF)
        self.assertTrue(orders==[])

        accountId2 = account.getId(accountF)
        self.assertTrue(accountId==accountId2)

        acc = account.get(accountId)
        self.assertTrue(accountId==acc['Id'])

        account.delete(accountId)
        acc2 = account.get(accountId)
        self.assertTrue(acc2==None)
        accountId3 = account.getId(f"Name:{name}")
        self.assertTrue(accountId3==None)

        acc3 = account.create(name,recordTypeName='Consumer',checkExists=True)
        accountId4 = account.getId(accountF=f"Name:{name}")
        self.assertTrue(accountId4==acc3['Id'])

        acc4 = account.create(name,recordTypeName='Consumer',checkExists=True)
        self.assertTrue(accountId4==acc4['Id'])
        account.delete(accountId4)

        account.delete(accountId4)


        print()

    def test_get_errors(self):
        restClient.init('NOSPRD')

        q = f"select Id,vlocity_cmt__InputData__c from vlocity_cmt__VlocityErrorLogEntry__c"

        res = query.query(q)


        out=[]
        for record in res['records']:
            data = record['vlocity_cmt__InputData__c']
            datas = simplejson.loads(data)
            out.append(datas)
            print(datas['ErrorMessage__c'])


        file_csv.write('VlocityErrorLogEntry_1',out)

        print()

    def test_get_error_ip(self):
        restClient.init('NOSDEV')

        Id = 'a6K3O000000FHuqUAG'

        q = f"select fields(all) from vlocity_cmt__VlocityErrorLogEntry__c where Id='{Id}' limit 10"

        res = query.query(q)


        out=[]
        for record in res['records']:
            data = record['vlocity_cmt__InputData__c']
            datas = simplejson.loads(data)

            theFile =jsonFile.write('TheIPError_1',datas)
            
            out.append(datas)
            print(datas['ErrorMessage__c'])


      #  file_csv.write('VlocityErrorLogEntry_1',out)

        print()

        
