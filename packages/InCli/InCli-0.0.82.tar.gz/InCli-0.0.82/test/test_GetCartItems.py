import unittest
from InCli.SFAPI import restClient,CPQ,account,Sobjects,utils,query,jsonFile,objectUtil,file,timeStats,digitalCommerce,digitalCommerceUtil
import simplejson,threading,time,multiprocessing,traceback,random,uuid,time,calendar
import InCli.InCli as incli

class Test_GetCartItems(unittest.TestCase):
    def get_Order(self,orderId):
        q=f"""SELECT id,
                    pricebook2id,
                    accountid,
                    createddate,
                    vlocity_cmt__defaultcurrencypaymentmode__c,
                    vlocity_cmt__effectiverecurringtotal__c,
                    vlocity_cmt__effectiveonetimetotal__c,
                    vlocity_cmt__numberofcontractedmonths__c,
                    vlocity_cmt__pricelistid__c,
                    recordtypeid,
                    recordtype.developername,
                    status,
                    effectivedate,
                    vlocity_cmt__requestdate__c,
                    vlocity_cmt__orderstatus__c,
                    vlocity_cmt__ischangesallowed__c,
                    vlocity_cmt__ischangesaccepted__c,
                    vlocity_cmt__supplementalaction__c,
                    vlocity_cmt__supersededorderid__c,
                    vlocity_cmt__firstversionorderidentifier__c,
                    vlocity_cmt__requestedstartdate__c,
                    vlocity_cmt__originatingcontractid__c,
                    vlocity_cmt__lastpricedat__c,
                    vlocity_cmt__validationdate__c,
                    vlocity_cmt__ordergroupid__c,
                    vlocity_cmt__ordergroupid__r.vlocity_cmt__groupcartid__c,
                    nos_t_scenariolevel__c,
                    nos_t_coveragetechnology__c,
                    nos_t_businessscenario__c,
                    nos_t_process__c
                    FROM Order WHERE Id IN ('{orderId}')"""
        res = query.query(q)      
        return res

    def get_orderItem(self,orderId):
        q2 =f"""SELECT Id,
                      Quantity,
                      vlocity_cmt__AssetReferenceId__c,
                      vlocity_cmt__ParentItemId__c,
                      vlocity_cmt__RootItemId__c,
                      PriceBookEntry.Product2Id,
                      PriceBookEntry.Name,
                      PriceBookEntry.Product2.vlocity_cmt__GlobalGroupKey__c,
                      vlocity_cmt__LineNumber__c,
                      vlocity_cmt__Product2Id__c,
                      vlocity_cmt__Action__c,
                      PricebookEntryId,
                      vlocity_cmt__ProvisioningStatus__c,
                      vlocity_cmt__ProductHierarchyPath__c,
                      vlocity_cmt__ProductHierarchyGroupKeyPath__c,
                      vlocity_cmt__CatalogItemReferenceDateTime__c,
                      OrderId,
                      vlocity_cmt__SupplementalAction__c,
                      vlocity_cmt__IsChangesAllowed__c 
                      FROM OrderItem WHERE OrderId = '{orderId}'  ORDER BY vlocity_cmt__LineNumber__c """
        res2 = query.query(q2)    

        return res2     
  
    def get_orderAppliedPromoItem(self,idl):
        lineItemIds = query.IN_clause(idl)

        q3 = f"""SELECT vlocity_cmt__OrderAppliedPromotionId__r.vlocity_cmt__PromotionId__c,
                        vlocity_cmt__OrderAppliedPromotionId__r.vlocity_cmt__Action__c,
                        vlocity_cmt__OrderItemId__c 
                        FROM vlocity_cmt__OrderAppliedPromotionItem__c 
                        WHERE vlocity_cmt__OrderItemId__c IN ({lineItemIds})"""
        res3 = query.query(q3)     
        return res3
    
    def get_pricingVariable(self):
        q = f"""SELECT Id, 
                      Name, 
                      vlocity_cmt__IsActive__c, 
                      vlocity_cmt__AdjustmentMethod__c, 
                      vlocity_cmt__Aggregation__c, 
                      vlocity_cmt__AppliesToVariableId__c, 
                      vlocity_cmt__AppliesToVariableId__r.vlocity_cmt__Code__c, 
                      vlocity_cmt__ChargeType__c, 
                      vlocity_cmt__Code__c, 
                      vlocity_cmt__CurrencyType__c, 
                      vlocity_cmt__Description__c, 
                      vlocity_cmt__RecurringFrequency__c, 
                      vlocity_cmt__Scope__c, 
                      vlocity_cmt__SubType__c,
                      vlocity_cmt__Type__c, 
                      vlocity_cmt__ValueType__c, 
                      (SELECT Id, Name, vlocity_cmt__DestinationFieldApiName__c, vlocity_cmt__DestinationSObjectType__c, vlocity_cmt__PricingVariableId__c FROM vlocity_cmt__PricingVariableBindings__r) 
                      FROM vlocity_cmt__PricingVariable__c WHERE vlocity_cmt__IsActive__c = true
        """
        res = query.query(q)     
        return res

    def get_pricebookentry(self,rootItemPriceBookEntrieIds):
        toBeQueriedIds = query.IN_clause(rootItemPriceBookEntrieIds)
        q = f"""SELECT Id, 
                        Pricebook2Id, 
                        Product2Id, 
                        product2.vlocity_cmt__endoflifedate__c, 
                        product2.vlocity_cmt__globalgroupkey__c, 
                        product2.isactive, 
                        product2.vlocity_cmt__isorderable__c, 
                        product2.vlocity_cmt__lifecyclestatus__c, 
                        product2.name, 
                        product2.vlocity_cmt__productspecid__c, 
                        product2.vlocity_cmt__sellingenddate__c, 
                        product2.vlocity_cmt__specificationtype__c 
                        FROM PricebookEntry WHERE  Id IN ({toBeQueriedIds})
        """
        res = query.query(q)     
        return res

    def get_dataStore(self,productIds):
        toBeQueriedIds = query.IN_clause(productIds)
        q0 = """SELECT vlocity_cmt__EffectiveEndDateTime__c, 
                      vlocity_cmt__EffectiveStartDateTime__c, 
                      vlocity_cmt__Key__c, 
                      vlocity_cmt__ProductId__c, 
                      vlocity_cmt__Value__c 
                      FROM vlocity_cmt__Datastore__c 
                      WHERE  ProductId__c IN :toBeQueriedIds AND RecordTypeId = :contextObjectNameOrId AND CachedDataSetId__r.IsActive__c = true
        """
        q = f"""SELECT vlocity_cmt__EffectiveEndDateTime__c, 
                      vlocity_cmt__EffectiveStartDateTime__c, 
                      vlocity_cmt__Key__c, 
                      vlocity_cmt__ProductId__c, 
                      vlocity_cmt__Value__c 
                      FROM vlocity_cmt__Datastore__c 
                      WHERE  vlocity_cmt__ProductId__c IN ({toBeQueriedIds}) AND vlocity_cmt__CachedDataSetId__r.vlocity_cmt__IsActive__c = true
        """
        res = query.query(q)     
        return res
    
    def get_childItems(self,childItemIds,rootItemIds):

        toBeQueriedIds = query.IN_clause(childItemIds)
        rootProdIds = query.IN_clause(rootItemIds)

        q = f"""SELECT Id, 
                      Name, 
                      vlocity_cmt__ChildLineNumber__c, 
                      vlocity_cmt__ChildProductId__c, 
                      vlocity_cmt__CollapseHierarchy__c, 
                      vlocity_cmt__IsOverride__c, 
                      vlocity_cmt__IsRootProductChildItem__c, 
                      vlocity_cmt__IsVirtualItem__c, 
                      vlocity_cmt__MaxQuantity__c, 
                      vlocity_cmt__MaximumChildItemQuantity__c, 
                      vlocity_cmt__MinQuantity__c, 
                      vlocity_cmt__MinimumChildItemQuantity__c, 
                      vlocity_cmt__ParentProductId__c, 
                      vlocity_cmt__Quantity__c, 
                      vlocity_cmt__SeqNumber__c, 
                      vlocity_cmt__childproductid__r.vlocity_cmt__endoflifedate__c, 
                      vlocity_cmt__childproductid__r.vlocity_cmt__globalgroupkey__c, 
                      vlocity_cmt__childproductid__r.name, 
                      vlocity_cmt__childproductid__r.vlocity_cmt__productspecid__c, 
                      vlocity_cmt__childproductid__r.vlocity_cmt__sellingenddate__c, 
                      vlocity_cmt__childproductid__r.vlocity_cmt__sellingstartdate__c, 
                      vlocity_cmt__parentproductid__r.vlocity_cmt__endoflifedate__c, 
                      vlocity_cmt__parentproductid__r.vlocity_cmt__globalgroupkey__c, 
                      vlocity_cmt__parentproductid__r.id, 
                      vlocity_cmt__parentproductid__r.name, 
                      vlocity_cmt__parentproductid__r.vlocity_cmt__productspecid__c, 
                      vlocity_cmt__parentproductid__r.vlocity_cmt__sellingenddate__c, 
                      vlocity_cmt__parentproductid__r.vlocity_cmt__sellingstartdate__c 
                      FROM vlocity_cmt__ProductChildItem__c 
                      WHERE  (ID IN ({toBeQueriedIds}) OR (vlocity_cmt__ParentProductId__c IN ({rootProdIds}) AND vlocity_cmt__IsRootProductChildItem__c = true)) AND vlocity_cmt__IsOverride__c = false  ORDER BY vlocity_cmt__SeqNumber__c ASC NULLS FIRST """
        
        res = query.query(q)     
        return res    
    def get_priceBookEntries(self,pbId,porductIds):
        toBeQueriedIds = query.IN_clause(porductIds)
        q=f"""SELECT Id, 
                    IsActive, 
                    Name, 
                    Pricebook2Id, 
                    Product2Id, 
                    ProductCode, 
                    UnitPrice, 
                    product2.description, 
                    product2.isactive, 
                    product2.name, 
                    product2.productcode, 
                    product2.vlocity_cmt__attributedefaultvalues__c, 
                    product2.vlocity_cmt__attributemetadata__c, 
                    product2.vlocity_cmt__endoflifedate__c, 
                    product2.vlocity_cmt__globalgroupkey__c, 
                    product2.vlocity_cmt__isconfigurable__c, 
                    product2.vlocity_cmt__isorderable__c, 
                    product2.vlocity_cmt__lifecyclestatus__c, 
                    product2.vlocity_cmt__productspecid__c, 
                    product2.vlocity_cmt__productspecid__r.name, 
                    product2.vlocity_cmt__productspecid__r.productcode, 
                    product2.vlocity_cmt__productspecid__r.vlocity_cmt__specificationtype__c, 
                    product2.vlocity_cmt__productspecid__r.vlocity_cmt__versionlabel__c, 
                    product2.vlocity_cmt__sellingenddate__c, 
                    product2.vlocity_cmt__sellingstartdate__c, 
                    product2.vlocity_cmt__specificationtype__c, 
                    product2.vlocity_cmt__subtype__c, 
                    product2.vlocity_cmt__type__c, 
                    product2.vlocity_cmt__versionlabel__c, 
                    vlocity_cmt__recurringprice__c 
                    FROM PricebookEntry 
                    WHERE  PriceBook2Id ='{pbId}' AND Product2Id IN ({toBeQueriedIds})"""

        res = query.query(q)     
        return res 
    def get_overrrideDefinitions(self,groupKeys):
        toBeQueriedGroupkeys=query.IN_clause(groupKeys)
        q = f"""SELECT Id, 
                      vlocity_cmt__IsExclude__c, 
                      vlocity_cmt__OverriddenProductChildItemId__c, 
                      vlocity_cmt__OverrideType__c, 
                      vlocity_cmt__OverridingPriceListEntryId__c, 
                      vlocity_cmt__OverridingProductChildItemId__c, 
                      vlocity_cmt__ProductGroupKey__c, 
                      vlocity_cmt__ProductHierarchyGroupKeyPath__c, 
                      vlocity_cmt__ProductHierarchyPath__c, 
                      vlocity_cmt__ProductId__c, 
                      vlocity_cmt__PromotionItemId__c, 
                      vlocity_cmt__compiledattributeoverrideid__r.vlocity_cmt__attributedefaultvalues__c, 
                      vlocity_cmt__compiledattributeoverrideid__r.vlocity_cmt__attributemetadatachanges__c, 
                      vlocity_cmt__overridingpricelistentryid__r.vlocity_cmt__effectivefromdate__c, 
                      vlocity_cmt__overridingpricelistentryid__r.vlocity_cmt__effectiveuntildate__c, 
                      vlocity_cmt__overridingpricelistentryid__r.vlocity_cmt__pricingelementid__c, 
                      vlocity_cmt__overridingpricelistentryid__r.vlocity_cmt__pricingmatrixbindingdata__c, 
                      vlocity_cmt__overridingpricelistentryid__r.vlocity_cmt__timeplanid__c, 
                      vlocity_cmt__overridingpricelistentryid__r.vlocity_cmt__timepolicyid__c, 
                      vlocity_cmt__overridingproductchilditemid__r.name, 
                      vlocity_cmt__overridingproductchilditemid__r.vlocity_cmt__childproductid__c, 
                      vlocity_cmt__overridingproductchilditemid__r.vlocity_cmt__maximumchilditemquantity__c, 
                      vlocity_cmt__overridingproductchilditemid__r.vlocity_cmt__maxquantity__c, 
                      vlocity_cmt__overridingproductchilditemid__r.vlocity_cmt__minimumchilditemquantity__c, 
                      vlocity_cmt__overridingproductchilditemid__r.vlocity_cmt__minquantity__c, 
                      vlocity_cmt__overridingproductchilditemid__r.vlocity_cmt__quantity__c 
                      FROM vlocity_cmt__OverrideDefinition__c 
                      WHERE  vlocity_cmt__ProductGroupKey__c IN ({toBeQueriedGroupkeys}) AND vlocity_cmt__PromotionId__c = null"""
        res = query.query(q)     
        return res         
      
    def test_getCartItems_x(self):
        restClient.init('DEVNOSCAT4')

        orderId = '8013O0000046OraQAE'

        pv = self.get_pricingVariable()

        order = self.get_Order(orderId)
        print(restClient.getLastCallAllTimes())

        orderItems = self.get_orderItem(orderId)
        print(restClient.getLastCallAllTimes())

        rootProdIds = [oi['vlocity_cmt__Product2Id__c'] for oi in orderItems['records'] if oi['vlocity_cmt__ParentItemId__c']==None]
        rootOiIds = [oi['Id'] for oi in orderItems['records'] if oi['vlocity_cmt__ParentItemId__c']==None]

        oiId_2_child_oiIds = {}
        for oi in orderItems['records']:
            if oi['vlocity_cmt__ParentItemId__c'] == None: continue
            if oi['vlocity_cmt__ParentItemId__c'] in oiId_2_child_oiIds:
                oiId_2_child_oiIds[oi['vlocity_cmt__ParentItemId__c']].append(oi['Id'])
            else:
                oiId_2_child_oiIds[oi['vlocity_cmt__ParentItemId__c']] = [oi['Id']]

        oiIds_2_prodIds = {}
        for oi in orderItems['records']:
          oiIds_2_prodIds[oi['Id']] = oi['vlocity_cmt__Product2Id__c']

        order_prodId_2_child_prodIds = {}

        for key in oiId_2_child_oiIds.keys():
            order_prodId_2_child_prodIds[oiIds_2_prodIds[key]] = []
            for oiId in oiId_2_child_oiIds[key]:
                order_prodId_2_child_prodIds[oiIds_2_prodIds[key]].append(oiIds_2_prodIds[oiId])

        oiProductIds = []
        for oi in orderItems['records']:
            if oi['vlocity_cmt__Product2Id__c'] not in oiProductIds:
              oiProductIds.append(oi['vlocity_cmt__Product2Id__c'])

        idl = [r['Id'] for r in orderItems['records']]

        #appliedPromoItems = self.get_orderAppliedPromoItem(idl)

        rootItemPriceBookEntrieIds = [r['PricebookEntryId'] for r in orderItems['records'] if r['vlocity_cmt__ParentItemId__c'] == None]
        rootItemPriceBookEntries = self.get_pricebookentry(rootItemPriceBookEntrieIds)

        rootItemProductIds = [r['vlocity_cmt__Product2Id__c'] for r in orderItems['records'] if r['vlocity_cmt__ParentItemId__c'] == None]
        ds = self.get_dataStore(rootItemProductIds)

        productChildItemsRelStr = ",".join([r['vlocity_cmt__Value__c'] for r in ds['records']])

        productChildItemRelIds = productChildItemsRelStr.split(',')
        productChildItemRel = self.get_childItems(productChildItemRelIds,rootItemProductIds)

        rel_all_prodIds = []
        for rel in productChildItemRel['records']:
            parentId = rel['vlocity_cmt__ParentProductId__c']
            childId = rel['vlocity_cmt__ChildProductId__c']

            if parentId != None and parentId not in rel_all_prodIds: rel_all_prodIds.append(parentId)
            if childId != None and childId not in rel_all_prodIds: rel_all_prodIds.append(childId)


        productChildItemRelIds_ParentinOrder = [ci for ci in productChildItemRel['records'] if ci['vlocity_cmt__ParentProductId__c'] in oiProductIds and ci['vlocity_cmt__ChildProductId__c']!=None]

        productChildItemRelIds_ParentinOrder_new = [ci for ci in productChildItemRelIds_ParentinOrder if ci['vlocity_cmt__ChildProductId__c'] not in oiProductIds]
        productChildItemRelIds_ParentinOrder_new_virtual = [ci for ci in productChildItemRelIds_ParentinOrder_new if ci['vlocity_cmt__IsVirtualItem__c'] == True]

        def processSiblings(prodId):
            childProdIds = order_prodId_2_child_prodIds[prodId] if prodId in order_prodId_2_child_prodIds else []
            childProdRels = [ci for ci in productChildItemRel['records'] if ci['vlocity_cmt__ParentProductId__c'] == prodId and ci['vlocity_cmt__ChildProductId__c']!=None]     
            for childProdRel in childProdRels:
                childId = childProdRel['vlocity_cmt__ChildProductId__c']
                if childId in childProdIds:
                  print(f"{childProdRel['vlocity_cmt__ParentProductId__r']['Name']} {childId} {childProdRel['vlocity_cmt__ChildProductId__r']['Name']} in order")
                else:
                  print(f"{childProdRel['vlocity_cmt__ParentProductId__r']['Name']} {childId} virtual:{childProdRel['vlocity_cmt__IsVirtualItem__c']} over:{childProdRel['vlocity_cmt__IsOverride__c']} not in order  {childProdRel['vlocity_cmt__ChildProductId__r']['Name']}")
                if childProdRel['vlocity_cmt__IsVirtualItem__c'] == True:
                    processSiblings(childId)

            for childProdId in childProdIds:
                processSiblings(childProdId)
        for rootOiId in rootOiIds:
            prodId = oiIds_2_prodIds[rootOiId]
            processSiblings(prodId)

        pbs = self.get_priceBookEntries(order['records'][0]['Pricebook2Id'],rel_all_prodIds)

        groupKeys = []
        for pb in pbs['records']:
            key = pb['Product2']['vlocity_cmt__GlobalGroupKey__c']
            if key != None:
                groupKeys.append(key)
        overrides = self.get_overrrideDefinitions(groupKeys)
        print()

