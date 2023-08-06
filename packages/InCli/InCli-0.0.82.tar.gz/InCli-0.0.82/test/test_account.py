import unittest
from InCli import InCli
from InCli.SFAPI import account,restClient,CPQ

class Test_Account(unittest.TestCase):
    def test_main(self):
        name = 'test1234'
        accountF = f"Name:{name}"

        restClient.init('NOSDEV')
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


        
