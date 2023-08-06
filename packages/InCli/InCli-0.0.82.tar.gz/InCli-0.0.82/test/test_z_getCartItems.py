import unittest
from InCli import InCli
from InCli.SFAPI import file,restClient,DR_IP,CPQ,digitalCommerce

class Test_CartItems(unittest.TestCase):
    def test_get_cart_items(self):

        restClient.init('NOSDEV')
        inp = {
            'orderId':"8013O000003keqvQAA"
        }
        res=DR_IP.remoteClass('testGetCartItems','method',inp,{})
        print(restClient.getLastCallElapsedTime())
        print(res)

        print()



#Id, ListPrice, OrderId, PricebookEntryId, Product2Id, Quantity, UnitPrice, pricebookentry.pricebook2id, pricebookentry.product2.id, pricebookentry.product2.name, pricebookentry.product2.productcode, pricebookentry.product2.vlocity_cmt__attributedefaultvalues__c, pricebookentry.product2.vlocity_cmt__attributemetadata__c, pricebookentry.product2.vlocity_cmt__globalgroupkey__c, pricebookentry.product2.vlocity_cmt__isconfigurable__c, pricebookentry.product2.vlocity_cmt__type__c, pricebookentry.product2id, vlocity_cmt__Action__c, vlocity_cmt__AssetReferenceId__c, vlocity_cmt__AttributeMetadataChanges__c, vlocity_cmt__AttributeSelectedValues__c, vlocity_cmt__BillingAccountId__c, vlocity_cmt__CatalogItemReferenceDateTime__c, vlocity_cmt__CpqCardinalityMessage__c, vlocity_cmt__CpqMessageData__c, vlocity_cmt__CpqPricingMessage__c, vlocity_cmt__CurrencyPaymentMode__c, vlocity_cmt__EffectiveOneTimeTotal__c, vlocity_cmt__EffectiveRecurringTotal__c, vlocity_cmt__FirstVersionOrderItemId__c, vlocity_cmt__FulfilmentStatus__c, vlocity_cmt__InCartQuantityMap__c, vlocity_cmt__IsChangesAllowed__c, vlocity_cmt__ItemName__c, vlocity_cmt__LineNumber__c, vlocity_cmt__OneTimeCalculatedPrice__c, vlocity_cmt__OneTimeCharge__c, vlocity_cmt__OneTimeManualDiscount__c, vlocity_cmt__OneTimeTotal__c, vlocity_cmt__OrderGroupId__c, vlocity_cmt__ParentItemId__c, vlocity_cmt__PricingLogData__c, vlocity_cmt__Product2Id__c, vlocity_cmt__ProductGroupKey__c, vlocity_cmt__ProductHierarchyGroupKeyPath__c, vlocity_cmt__ProductHierarchyPath__c, vlocity_cmt__ProvisioningStatus__c, vlocity_cmt__ServiceAccountId__c, vlocity_cmt__SubAction__c, vlocity_cmt__SupersededOrderItemId__c, vlocity_cmt__SupplementalAction__c, vlocity_cmt__billingaccountid__r.id, vlocity_cmt__billingaccountid__r.name, vlocity_cmt__recurringcalculatedprice__c, vlocity_cmt__recurringcharge__c, vlocity_cmt__recurringdiscountprice__c, vlocity_cmt__recurringmanualdiscount__c, vlocity_cmt__recurringtotal__c, vlocity_cmt__rootitemid__c, vlocity_cmt__serviceaccountid__r.id, vlocity_cmt__serviceaccountid__r.name

    def test_get_cart_items_real(self):
        restClient.init('NOSDEV')
        res= CPQ.getCartItems_api('8013O000003keqvQAA')       
        print()

    def test_get_cart_items_real(self):
        restClient.init('NOSDEV')
        res = digitalCommerce.getOfferDetails('DC_CAT_MPO_CHILD_007','C_NOS_OFFER_017')
        print()