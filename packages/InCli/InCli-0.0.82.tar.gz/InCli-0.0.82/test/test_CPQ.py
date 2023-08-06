import unittest
from InCli.SFAPI import restClient,CPQ,account,Sobjects,utils,query,jsonFile,objectUtil,file,timeStats,digitalCommerce,digitalCommerceUtil,CPQUtil
import simplejson,threading,time,multiprocessing,traceback,random,uuid,time,calendar
import InCli.InCli as incli

procNum = 10
threadNum = 20
reps = 30
guest_url = 'https://nosdti-parceiros.cs109.force.com/onboarding'
def do_work(details):
  restClient.initWithToken('GUEST',url=guest_url)

  def getOffers(details):

    errors = 0
    ts = timeStats.TimeStats()

    for x in range(0,reps):
      try:
        # cartId = '8017a000002ad21AAA'
        # items2 = CPQ.getCartItems_api(cartId,price=False,validate=False)

        #
        # call = digitalCommerce.getOfferByCatalogue('DC_CAT_WOO_MOBILE')
        # digitalCommerce.createBasket('DC_CAT_WOO_MOBILE','C_WOO_MOBILE')
      #  val = f"{uuid.uuid4()}"
      #  print(val)
        ts.new(["Basket","Error"])
        current_GMT = time.gmtime()

        val = calendar.timegm(current_GMT)
        offerDetails = digitalCommerceUtil.updateOfferField(details,'ATT_NOS_OTT_SUBSCRIPTION_ID','userValues',val,'code')
        print("creating basket")        
        basket2 = digitalCommerce.createBasketAfterConfig('DC_CAT_WOO_MOBILE',offerDetails)
        print("got basket")
        ts.time("Basket")

        call1 = restClient.lastCall()
        if call1['totalCalls'] >1:
          calls = restClient.thread_get_calls()
          times = restClient._get_call_times(call1)
          times2 = restClient._get_call_times(calls[-2])
          ts.time_no("Basket1",times2['delta'])
          ts.time_no("Basket2",times['delta'])

       #   print(f"{times2} {times}",flush=True)

     #   print(restClient.getLastCallAllTimes(),flush=True)
      except Exception as e:
        utils.printException(e)
        errors = errors + 1
        ts.time_no("Error","True")

    ts.print()
      
    print(f"Processed {reps} with errors{errors}")  
     #   print(traceback.format_exc())
     #   print(restClient.lastCall())

  threads =  []
  for x in range(0,threadNum):
      thread = threading.Thread(target=getOffers,args=(details,))
      thread.start()
      threads.append(thread)
  for x,t in enumerate(threads):
    t.join()
    print(f'Thread Done {x}')


class Test_Query(unittest.TestCase):
    def test_guestUser(self):
        def do_process():
          restClient.initWithToken('GUEST',url=guest_url)

          print("getting offer details")
          details = digitalCommerce.getOfferDetails('DC_CAT_WOO_MOBILE','C_WOO_MOBILE')
          print("got offer details")

          processes = []
          for x in range(0,procNum):
            process = multiprocessing.Process(target=do_work,args=(details,))
            process.start()  
            processes.append(process)
          for p in processes:
            p.join()
            print('Process Done')

        do_process()

    def test_query_apexlog(self):
      restClient.init('DTI')

      q = "select Operation,StartTime,DurationMilliseconds from Apexlog order by StartTime desc limit 200"
      res = query.query(q)
      for r in res['records']:
        r.pop('attributes')

      utils.printFormated(res['records'])
      print()
    
    def test_createCart(self):
        restClient.init('NOSDEV')

        acc = account.createAccount('Name:unaiTest2',recordTypeName='Consumer')

        self.assertTrue(Sobjects.checkId(acc['Id']))

        cartId = CPQ.createCart(accountF= acc['Id'], pricelistF='Name:B2C Price List',name="testa5",checkExists=True)

        print(cartId)

    def test_delCartItems(self):
        restClient.init('NOSDEV')
        cartId = CPQ.getCartId('name:testa5')

        items = CPQ.getCartItems_api(cartId)

        if items['totalSize'] > 0:
          itemIds = [item['Id']['value'] for item in items['records']]

          dele = CPQ.deleteCartItems_api(cartId,itemIds)

          self.assertEqual(dele['messages'][0]['message'],'Successfully deleted.')
          print()

    def test_delete_applied_promotions(self):
        restClient.init('NOSDEV')

        cartId = CPQ.getCartId('name:testa5')
        applied = CPQ.getCartPromotions_api(cartId,getPromotionsAppliedToCart=True)
        dele = CPQ.deleteCartPromotion_api(cartId,applied[0]['Id']['value'])

    def test_postPromo(self):
        restClient.init('NOSDEV')

        promoName = 'NOS4u 100Mb + Móvel'
        promo = CPQ.getCartPromotions('name:testa5',query=promoName,onlyOne=True)

        cartId = CPQ.getCartId('name:testa5')

        res = CPQ.postCartsPromoItems_api(cartId,promo['Id'])

        applied = CPQ.getCartPromotions_api(cartId,getPromotionsAppliedToCart=True)

       # dele = CPQ.deleteCartPromotion_api(cartId,applied[0]['Id']['value'])

        print()

    def test_getErrors(self):
        cartId = CPQ.getCartId('name:testa5')

        all = CPQ.getCartItems_api(cartId,fields='vlocity_cmt__ServiceAccountId__c,vlocity_cmt__BillingAccountId__c')

        sim = all['records'][0]['lineItems']['records'][3]['productGroups']['records'][1]['productGroups']['records'][0]['lineItems']['records'][0]
        for key in sim.keys():
          sim2= sim.copy()
          sim2.pop(key)
          items = {"records":[sim2]}
          res = CPQ.updateCartItem_api(cartId,items)
          if res['messages'][0]['message'] == 'Successfully updated.':
            print(f"{key} {res['messages'][0]['message']}")
          else:
            print(f"******************************************************   {key} {res['messages'][0]['message']}")

    def test_updateCartItem(self):
        restClient.init('NOSDEV')
        cartId = CPQ.getCartId('name:testa5')

        all = CPQ.getCartItems_api(cartId,fields='vlocity_cmt__ServiceAccountId__c,vlocity_cmt__BillingAccountId__c')

        sim = all['records'][0]['lineItems']['records'][3]['productGroups']['records'][1]['productGroups']['records'][0]['lineItems']['records'][0]

        print(sim['Quantity'])
        sim_m = {}
        sim_m['vlocity_cmt__LineNumber__c'] = sim['vlocity_cmt__LineNumber__c']
        sim_m['vlocity_cmt__RootItemId__c'] = sim['vlocity_cmt__RootItemId__c']
        sim_m['vlocity_cmt__Action__c'] = sim['vlocity_cmt__Action__c']
        sim_m['Id'] = sim['Id']
      #  sim_m['Quantity'] = sim['Quantity']
      #  sim_m['Quantity']['value'] = 2.0
        items = {"records":[sim_m]}

        sim_m['vlocity_cmt__ServiceAccountId__c'] = '0013O000016sKfwQAE'
        sim_m['vlocity_cmt__BillingAccountId__c'] = '0013O000016sKfwQAE'

        res = CPQ.updateCartItem_api(cartId,items)
        time = restClient.getLastCallElapsedTime()
        print(time)
        print(res['messages'][0]['message'])

        all_2 = CPQ.getCartItems_api(cartId,fields='vlocity_cmt__ServiceAccountId__c,vlocity_cmt__BillingAccountId__c')
        sim_2 = all_2['records'][0]['lineItems']['records'][3]['productGroups']['records'][1]['productGroups']['records'][0]['lineItems']['records'][0]
        print(sim_2['Quantity']['value'])
        print()

    def test_updateCartItem(self):
        restClient.init('DEVNOSCAT4')

        promoName = 'NOS4u 100Mb + Móvel'

        cartId,items =  CPQUtil.create_cart_with_promo('account_2','cart_2',promoName,create=True)

        if 1==2:
          postPromo =True

          acc = account.create('Name:unaiTest21',recordTypeName='Consumer')
          cartId = CPQ.createCart(accountF= acc['Id'], pricelistF='Name:B2C Price List',name="testa_7",checkExists=True)
          print(cartId)

          if postPromo==True:
            promoName = 'NOS4u 100Mb + Móvel'
            promo = CPQ.getCartPromotions(cartId,query=promoName,onlyOne=True)

            res = CPQ.postCartsPromoItems_api(cartId,promo['Id'])

          all = CPQ.getCartItems_api(cartId,fields='vlocity_cmt__ServiceAccountId__c,vlocity_cmt__BillingAccountId__c')

          codes = ['C_NOS_OFFER_001','C_NOS_AGG_SERVICE_TV_UMA','C_NOS_SERVICE_TV_003','C_NOS_EQUIP_TV_009']
          codes = ['C_NOS_OFFER_001']

          account1Id = acc['Id']
          account2Id = account.getId('name:account_6')

        objs = []
        codes = ['C_NOS_OFFER_001']
        account2Id = account.getId('name:account_6')

        for code in codes:
          lineItem = objectUtil.getSiblingWhere(items,selectKey='ProductCode',selectKeyValue=code,whereKey='itemType',whereValue='lineItem')['object']
          if lineItem == None:
            print(f"None for code {code}")
            continue

        #  assert(lineItem['vlocity_cmt__ServiceAccountId__c']['value'] == account1Id)
        #  assert(lineItem['vlocity_cmt__BillingAccountId__c']['value'] == account1Id)

          obj = {}
          obj['vlocity_cmt__LineNumber__c'] = lineItem['vlocity_cmt__LineNumber__c']
          obj['vlocity_cmt__RootItemId__c'] = lineItem['vlocity_cmt__RootItemId__c']
          obj['vlocity_cmt__Action__c'] = lineItem['vlocity_cmt__Action__c']
          obj['vlocity_cmt__AssetReferenceId__c'] = lineItem['vlocity_cmt__AssetReferenceId__c']
          obj['Id'] = lineItem['Id']
          obj['vlocity_cmt__ServiceAccountId__c'] = account2Id
          obj['vlocity_cmt__BillingAccountId__c'] = account2Id

          objs.append(obj)
       #   objs.append({"records":[obj]})

        items = {"records":objs}
        res = CPQ.updateCartItem_api(cartId,items)
        time = restClient.getLastCallElapsedTime()
        restClient.callSave('minimum',logRequest=True)
        print(time)
        print(res['messages'][0]['message'])

#        all2 = CPQ.getCartItems_api(cartId,fields='vlocity_cmt__ServiceAccountId__c,vlocity_cmt__BillingAccountId__c')
#
#        for code in codes:
#          lineItem = objectUtil.getSiblingWhere(all2,selectKey='ProductCode',selectKeyValue=code,whereKey='itemType',whereValue='lineItem')['object']
#          print(f"{code}  {lineItem['vlocity_cmt__ServiceAccountId__c']['value']}  {lineItem['vlocity_cmt__BillingAccountId__c']['value']}   {account2Id}")

        incli._main(["-u","DEVNOSCAT4","-q", f"select Id,vlocity_cmt__BillingAccountId__c,vlocity_cmt__LineNumber__c,vlocity_cmt__ServiceAccountId__c,vlocity_cmt__Product2Id__r.productCode from orderitem where OrderId='{cartId}' order by vlocity_cmt__LineNumber__c","-fields","all"])  

        CPQ.deleteCart(cartId)

        print()
    def test_updateCartItem_CPQUtil(self):
        restClient.init('DEVNOSCAT4')

        promoName = 'NOS4u 100Mb + Móvel'

        cartId,items =  CPQUtil.create_cart_with_promo('account_2','cart_2',promoName,create=True)

        objs = []
        code = 'C_NOS_OFFER_001'
        account2Id = account.getId('name:account_6')

        obj = {
           'vlocity_cmt__ServiceAccountId__c' : account2Id,
           'vlocity_cmt__BillingAccountId__c' : account2Id
        }

        attr = {
           'ATT_NOS_MATRIX_ID':1111,
           'ATT_SERVICE_ACCOUNT_TYPE':'Móvel'
        }

        call = CPQUtil.update_field(cartId,items,code,obj,attributesDic=attr)

        time = restClient.getLastCallElapsedTime()
        restClient.callSave('minimum',logRequest=True)
        print(time)

#        all2 = CPQ.getCartItems_api(cartId,fields='vlocity_cmt__ServiceAccountId__c,vlocity_cmt__BillingAccountId__c')
#
#        for code in codes:
#          lineItem = objectUtil.getSiblingWhere(all2,selectKey='ProductCode',selectKeyValue=code,whereKey='itemType',whereValue='lineItem')['object']
#          print(f"{code}  {lineItem['vlocity_cmt__ServiceAccountId__c']['value']}  {lineItem['vlocity_cmt__BillingAccountId__c']['value']}   {account2Id}")

        incli._main(["-u","DEVNOSCAT4","-q", f"select Id,vlocity_cmt__BillingAccountId__c,vlocity_cmt__LineNumber__c,vlocity_cmt__ServiceAccountId__c,vlocity_cmt__Product2Id__r.productCode from orderitem where OrderId='{cartId}' order by vlocity_cmt__LineNumber__c","-fields","all"])  

        CPQ.deleteCart(cartId)

        print()
    def test_write_to_file(self):
        restClient.init('NOSDEV')

        cartId = CPQ.getCartId('name:testa_1')
        CPQ.deleteCart(cartId)

        acc = account.createAccount('Name:unaiTest2',recordTypeName='Consumer')
        cartId = CPQ.createCart(accountF= acc['Id'], pricelistF='Name:B2C Price List',name="testa_1",checkExists=True)
        print(cartId)

        promoName = 'NOS4u 100Mb + Móvel'
        promo = CPQ.getCartPromotions(cartId,query=promoName,onlyOne=True)

        res = CPQ.postCartsPromoItems_api(cartId,promo['Id'])

        all = CPQ.getCartItems_api(cartId,fields='vlocity_cmt__ServiceAccountId__c,vlocity_cmt__BillingAccountId__c')
        filename = restClient.callSave('getItemsqwe')
        print(filename)

    def test_read_from_file(self):
        restClient.init('NOSDEV')
        account1Id = account.getAccountId('name:unaiTest2')
        account2Id = account.getAccountId('name:unai2')

        print(account2Id)

        stItems = file.read('/Users/uormaechea/Documents/Dev/python/InCliLib/.incli/output/getItemsqwe_res.json')
        stItems2 = stItems.replace(account1Id,account2Id)
        items = simplejson.loads(stItems2)
        cartId = CPQ.getCartId('name:testa_1')
        print(cartId)
     #   res = CPQ.updateCartItem_api(cartId,items)

        C_NOS_OFFER_001 = objectUtil.getSiblingWhere(items,selectKey='ProductCode',selectKeyValue='C_NOS_OFFER_001',whereKey='itemType',whereValue='lineItem')['object']
        C_NOS_EQUIP_TV_006 = objectUtil.getSiblingWhere(items,selectKey='ProductCode',selectKeyValue='C_NOS_EQUIP_TV_006',whereKey='itemType',whereValue='lineItem')['object']
        C_NOS_EQUIP_TV_009 = objectUtil.getSiblingWhere(items,selectKey='ProductCode',selectKeyValue='C_NOS_EQUIP_TV_009',whereKey='itemType',whereValue='lineItem')['object']
        C_NOS_SERVICE_TV_003 = objectUtil.getSiblingWhere(items,selectKey='ProductCode',selectKeyValue='C_NOS_SERVICE_TV_003',whereKey='itemType',whereValue='lineItem')['object']

        C_NOS_SERVICE_IF_001 = objectUtil.getSiblingWhere(items,selectKey='ProductCode',selectKeyValue='C_NOS_SERVICE_IF_001',whereKey='itemType',whereValue='lineItem')['object']
        C_NOS_EQUIP_GIGA_ROUTER = objectUtil.getSiblingWhere(items,selectKey='ProductCode',selectKeyValue='C_NOS_EQUIP_GIGA_ROUTER',whereKey='itemType',whereValue='lineItem')['object']

        C_NOS_DN = objectUtil.getSiblingWhere(items,selectKey='ProductCode',selectKeyValue='C_NOS_DN',whereKey='itemType',whereValue='lineItem')['object']
        C_NOS_SERVICE_VF_001 = objectUtil.getSiblingWhere(items,selectKey='ProductCode',selectKeyValue='C_NOS_SERVICE_VF_001',whereKey='itemType',whereValue='lineItem')['object']


        C_NOS_OFFER_001['lineItems']['records'].append(C_NOS_EQUIP_TV_006)
        C_NOS_OFFER_001['lineItems']['records'].append(C_NOS_EQUIP_TV_009)
        C_NOS_OFFER_001['lineItems']['records'].append(C_NOS_SERVICE_TV_003)

        C_NOS_OFFER_001['lineItems']['records'].append(C_NOS_SERVICE_IF_001)
        C_NOS_OFFER_001['lineItems']['records'].append(C_NOS_EQUIP_GIGA_ROUTER)

        C_NOS_OFFER_001['lineItems']['records'].append(C_NOS_DN)
        C_NOS_OFFER_001['lineItems']['records'].append(C_NOS_SERVICE_VF_001)
    #    C_NOS_OFFER_001['lineItems']['records'].append(C_NOS_AGG_SERVICE_VF_HFC)

        items = {"records":[C_NOS_OFFER_001]}
        res = CPQ.updateCartItem_api(cartId,items)
        print(restClient.getLastCallElapsedTime())
        print(res['messages'][0]['message'])

        incli._main(["-u","NOSDEV","-q", f"select Id,vlocity_cmt__BillingAccountId__c,vlocity_cmt__LineNumber__c,vlocity_cmt__ServiceAccountId__c,vlocity_cmt__Product2Id__r.productCode from orderitem where OrderId='{cartId}' order by vlocity_cmt__LineNumber__c","-fields","all"])  

        print()

    def lineItem_for_update(self,lineItem):
          obj = {}
          obj['vlocity_cmt__LineNumber__c'] = lineItem['vlocity_cmt__LineNumber__c']
          obj['vlocity_cmt__RootItemId__c'] = lineItem['vlocity_cmt__RootItemId__c']
          obj['vlocity_cmt__Action__c'] = lineItem['vlocity_cmt__Action__c']          
          obj['vlocity_cmt__AssetReferenceId__c'] = lineItem['vlocity_cmt__AssetReferenceId__c']
          obj['Id'] = lineItem['Id']

   #       obj['vlocity_cmt__ServiceAccountId__c'] = account2Id
   #       obj['vlocity_cmt__BillingAccountId__c'] = account2Id

          if 'lineItems2' in lineItem:
            obj['lineItems'] = lineItem['lineItems']
            for li in obj['lineItems']['records']:
              li.pop('productChildItemDefinition')
              li.pop('lineItems',None)
              li.pop('childProducts',None)
              li.pop('productGroups',None)

              li.pop('messages',None)
              li.pop('actions',None)
              li.pop('displaySequence',None)
              li.pop('UnitPrice',None)
              li.pop('Product2',None)

              li.pop('Name',None)
              li.pop('Product2Id',None)
              li.pop('IsActive',None)
              li.pop('ProductCode',None)
              li.pop('vlocity_cmt__RecurringPrice__c',None)

              li.pop('Pricebook2Id',None)
              li.pop('PricebookEntry',None)
              li.pop('productId',None)
              li.pop('defaultQuantity',None)
              li.pop('minQuantity',None)

              li.pop('maxQuantity',None)
              li.pop('groupMinQuantity',None)
              li.pop('groupMaxQuantity',None)
              li.pop('sequenceNumber',None)
              li.pop('productChildItemId',None)
              li.pop('productChildItemDefinition',None)

              li.pop('name',None)
              li.pop('isVirtualItem',None)
              li.pop('hasChildren',None)
              li.pop('orderActive',None)
              li.pop('parentRecordTypeDevName',None)
              li.pop('itemType',None)

              li.pop('action',None)
              li.pop('SellingPeriod',None)
              li.pop('ListPrice',None)
              li.pop('OrderId',None)
              li.pop('PricebookEntryId',None)
              li.pop('Quantity',None)

         #     li.pop('vlocity_cmt__AssetReferenceId__c',None)
              li.pop('vlocity_cmt__CatalogItemReferenceDateTime__c',None)
              li.pop('vlocity_cmt__CurrencyPaymentMode__c',None)
              li.pop('vlocity_cmt__EffectiveOneTimeTotal__c',None)
              li.pop('vlocity_cmt__EffectiveRecurringTotal__c',None)
              li.pop('vlocity_cmt__InCartQuantityMap__c',None)
              li.pop('vlocity_cmt__IsChangesAllowed__c',None)

          if 'lineItems' in lineItem:
            obj['lineItems'] = {}
            obj['lineItems']['records'] = []
            for record in lineItem['lineItems']['records']:
              li = self.lineItem_for_update(record)
              obj['lineItems']['records'].append(li)
          return obj
    
    def test_do_all_puts(self):
        def getObj(lineItem,account2Id):
          obj = {}
          obj['vlocity_cmt__LineNumber__c'] = lineItem['vlocity_cmt__LineNumber__c']
          obj['vlocity_cmt__RootItemId__c'] = lineItem['vlocity_cmt__RootItemId__c']
          obj['vlocity_cmt__Action__c'] = lineItem['vlocity_cmt__Action__c']          
          obj['vlocity_cmt__AssetReferenceId__c'] = lineItem['vlocity_cmt__AssetReferenceId__c']
          obj['Id'] = lineItem['Id']

          obj['vlocity_cmt__ServiceAccountId__c'] = account2Id
          obj['vlocity_cmt__BillingAccountId__c'] = account2Id

          obj['attributeCategories'] = lineItem['attributeCategories']

          if 'lineItems2' in lineItem:
            obj['lineItems'] = lineItem['lineItems']
            for li in obj['lineItems']['records']:
              li.pop('productChildItemDefinition')
              li.pop('lineItems',None)
              li.pop('childProducts',None)
              li.pop('productGroups',None)

              li.pop('messages',None)
              li.pop('actions',None)
              li.pop('displaySequence',None)
              li.pop('UnitPrice',None)
              li.pop('Product2',None)

              li.pop('Name',None)
              li.pop('Product2Id',None)
              li.pop('IsActive',None)
              li.pop('ProductCode',None)
              li.pop('vlocity_cmt__RecurringPrice__c',None)

              li.pop('Pricebook2Id',None)
              li.pop('PricebookEntry',None)
              li.pop('productId',None)
              li.pop('defaultQuantity',None)
              li.pop('minQuantity',None)

              li.pop('maxQuantity',None)
              li.pop('groupMinQuantity',None)
              li.pop('groupMaxQuantity',None)
              li.pop('sequenceNumber',None)
              li.pop('productChildItemId',None)
              li.pop('productChildItemDefinition',None)

              li.pop('name',None)
              li.pop('isVirtualItem',None)
              li.pop('hasChildren',None)
              li.pop('orderActive',None)
              li.pop('parentRecordTypeDevName',None)
              li.pop('itemType',None)

              li.pop('action',None)
              li.pop('SellingPeriod',None)
              li.pop('ListPrice',None)
              li.pop('OrderId',None)
              li.pop('PricebookEntryId',None)
              li.pop('Quantity',None)

         #     li.pop('vlocity_cmt__AssetReferenceId__c',None)
              li.pop('vlocity_cmt__CatalogItemReferenceDateTime__c',None)
              li.pop('vlocity_cmt__CurrencyPaymentMode__c',None)
              li.pop('vlocity_cmt__EffectiveOneTimeTotal__c',None)
              li.pop('vlocity_cmt__EffectiveRecurringTotal__c',None)
              li.pop('vlocity_cmt__InCartQuantityMap__c',None)
              li.pop('vlocity_cmt__IsChangesAllowed__c',None)

          if 'lineItems' in lineItem:
            obj['lineItems'] = {}
            obj['lineItems']['records'] = []
            for record in lineItem['lineItems']['records']:
              li = getObj(record,account2Id)
              obj['lineItems']['records'].append(li)
          return obj

        restClient.init('NOSDEV')

        accountname='unaiTest_1'

        cartId = CPQUtil.create_cart_with_promo(accountname=accountname,cartName='testa_18',promoName='NOS4u 100Mb + Móvel',create=True,pricelistF='Name:B2C Price List')

        all = CPQ.getCartItems_api(cartId,fields='vlocity_cmt__ServiceAccountId__c,vlocity_cmt__BillingAccountId__c',price=False,validate=False,includeAttachment=False)
        print(restClient.getLastCallElapsedTime())

        account1Id = account.getId(f'name:{accountname}')
        account2Id = account.getId('name:unai2')

     #   strAll = simplejson.dumps(all)
     #   stItems2 = strAll.replace(account1Id,account2Id)
        items = objectUtil.replace_everywhere_in_obj(all,account1Id,account2Id)

        print(cartId)

        codes = ['C_NOS_SERVICE_TV_003','C_NOS_EQUIP_TV_006','C_NOS_EQUIP_TV_009','C_NOS_SERVICE_IF_001','C_NOS_EQUIP_GIGA_ROUTER','C_NOS_DN','C_NOS_SERVICE_VF_001','C_NOS_MSISDN','C_NOS_SERVICE_VM_001','C_NOS_EQUIP_SIM_CARD','C_NOS_OFFER_001','C_NOS_OFFER_006','C_NOS_AGG_SERVICE_TV_UMA','C_NOS_AGG_SERVICE_IF_HFC','C_NOS_AGG_SERVICE_VF_HFC','C_NOS_AGG_SERVICES_MAND_VM']
    #    codes = ['C_NOS_OFFER_006']
      #  codes = []
        lineItem = objectUtil.getSiblingWhere(items,selectKey='ProductCode',selectKeyValue='C_NOS_OFFER_001',whereKey='itemType',whereValue='lineItem')['object']
   #     for key in lineItem.keys():
   #       print(key)
        C_NOS_OFFER_001 = getObj(lineItem,account2Id)
        C_NOS_OFFER_001['lineItems']['records'] = []
    #    C_NOS_OFFER_001_copy = C_NOS_OFFER_001.copy()
    #    C_NOS_OFFER_001_copy.pop('lineItems')
        if 1==1:
            C_NOS_OFFER_001.pop('vlocity_cmt__LineNumber__c')
            C_NOS_OFFER_001.pop('vlocity_cmt__RootItemId__c')
            C_NOS_OFFER_001.pop('vlocity_cmt__Action__c')
            C_NOS_OFFER_001.pop('Id')
            C_NOS_OFFER_001.pop('vlocity_cmt__ServiceAccountId__c')
            C_NOS_OFFER_001.pop('vlocity_cmt__BillingAccountId__c')
            C_NOS_OFFER_001.pop('vlocity_cmt__AssetReferenceId__c')

    #    C_NOS_OFFER_001['lineItems'] = {}
    #    C_NOS_OFFER_001['lineItems']['records']=[]

    #    C_NOS_OFFER_001['lineItems']['records'].append(C_NOS_OFFER_001_copy)
        for code in codes:
          lineItem = objectUtil.getSiblingWhere(items,selectKey='ProductCode',selectKeyValue=code,whereKey='itemType',whereValue='lineItem')['object']
          li = getObj(lineItem,account2Id)
          C_NOS_OFFER_001['lineItems']['records'].append(li)

        items = {"records":[C_NOS_OFFER_001]}
        res = CPQ.updateCartItem_api(cartId,items)  
        filename = restClient.callSave('records0001',logRequest=True,logReply=False)   

        print(restClient.getLastCallElapsedTime())
        print(res['messages'][0]['message'])

        incli._main(["-u","NOSDEV","-q", f"select Id,vlocity_cmt__BillingAccountId__c,vlocity_cmt__LineNumber__c,vlocity_cmt__ServiceAccountId__c,vlocity_cmt__Product2Id__r.productCode from orderitem where OrderId='{cartId}' order by vlocity_cmt__LineNumber__c","-fields","all"])  

        items = CPQ.getCartItems_api(cartId=cartId)
        print()

    def test_get_order_lines_for_CartId(self):
        cartId = '8013O000003j97nQAA'
        incli._main(["-u","NOSDEV","-q", f"select Id,vlocity_cmt__LineNumber__c,vlocity_cmt__Product2Id__r.productCode,vlocity_cmt__Product2Id__r.name from orderitem where OrderId='{cartId}' order by vlocity_cmt__LineNumber__c","-fields","all"])  

    def test_deleteOrder(self):
      orderId = '8013O000003a9CoQAI'
      restClient.init('NOSDEV')
      try:
        delete = CPQ.deleteCart(orderId)
      except Exception as e:
        utils.printException(e)

    def test_delete_discount(self):

      restClient.init('NOSDEV')

   # def create_cart_with_offer(self,accountname,cartName,offerName,create=False,pricelistF='Name:B2C Price List',timeStats=None):

    #    cartId = CPQ.getCartId(f"name:{cartName}")
    #    if cartId != None:
     #     if create == False:
       #     return cartId
     #     CPQ.deleteCart(cartId)

     #   accountF = f'Name:{accountname}'
     #   accountId = account.create_Id(accountname,recordTypeName='Consumer')

     #   inputFields = {
#'NOS_t_CoverageTechnology__c':'FTTH'
 #       }
     #   cartId = CPQ.createCart(accountF= accountId, pricelistF=pricelistF,name=cartName,checkExists=True,inputFields=inputFields)

     #   offer = CPQ.getCartProducts(cartId,query=offerName,onlyOne=True)
     #   res = CPQ.addItemstoCart(cartId,productCode=offer['ProductCode']['value'],pricelistF=pricelistF)

      #  return cartId  
    
    #def create_cart_with_promo(self,accountname,cartName,promoName,create=False,pricelistF='Name:B2C Price List'):

     #   cartId = CPQ.getCartId(f"name:{cartName}")
     #   if cartId != None:
     #     if create == False:
     #       return cartId
     #     CPQ.deleteCart(cartId)

     #   accountF = f'Name:{accountname}'
     #   accountId = account.create_Id(accountname,recordTypeName='Consumer')
     #   cartId = CPQ.createCart(accountF= accountId, pricelistF=pricelistF,name=cartName,checkExists=True)

     #   promo = CPQ.getCartPromotions(cartId,query=promoName,onlyOne=True)

     #   res = CPQ.postCartsPromoItems_api(cartId,promo['Id'],price=False,validate=False)

      #  return cartId

    def test_post_cart_item(self):
        restClient.init('NOSDEV')
        restClient.setLoggingLevel()
        cartName = 'testa_4c'

        cartId = CPQ.getCartId(f"name:{cartName}")
        if cartId != None:
          CPQ.deleteCart(cartId)

        accountId = account.create_Id('unaiTest1c',recordTypeName='Consumer')
        cartId = CPQ.createCart(accountF= accountId, pricelistF='Name:B2C Price List',name=cartName,checkExists=True)
        print(restClient.getLastCallElapsedTime())

        promoName = 'NOS4u 100Mb + Móvel - Desc. Mensal'
        promo = CPQ.getCartPromotions(cartId,query=promoName,onlyOne=True)

        res = CPQ.postCartsPromoItems_api(cartId,promo['Id'])
        print(restClient.getLastCallElapsedTime())

        all = CPQ.getCartItems_api(cartId,fields='vlocity_cmt__ServiceAccountId__c,vlocity_cmt__BillingAccountId__c',price=False,validate=False,includeAttachment=False)
        print(restClient.getLastCallElapsedTime())

    def test_create_cart_from_asset(self):
        restClient.init('DEVNOSCAT2')

        restClient.setLoggingLevel()
        cartName = 'testa_4'

        cartId = CPQ.createCartFromAsset(assetId='02i3O00000KQ489QAD',accountId='0013O0000186LXLQA2',date='2023-02-22',inputFields={"Name":cartName})

        print()

    def test_update_attribute2(self):
        restClient.init('DEVNOSCAT4')
        restClient.setLoggingLevel()
        cartName = 'testa_4'

        promoName = 'NOS4u 100Mb + Móvel'

        cartId,items =  CPQUtil.create_cart_with_promo('account_2','cart_2',promoName,create=True)
        print(cartId)
        items = CPQ.getCartItems_api(cartId,price=False,validate=False)
        lineItem = objectUtil.getSiblingWhere(items,selectKey='ProductCode',selectKeyValue='C_NOS_SERVICE_TV_003',whereKey='itemType',whereValue='lineItem')['object']
        line2 = self.lineItem_for_update(lineItem)

        def onlyValue(line):
          obj = {}
          obj['value'] = line['value']
          return obj

        line2['vlocity_cmt__LineNumber__c'] = onlyValue(line2['vlocity_cmt__LineNumber__c'])
        line2['vlocity_cmt__RootItemId__c'] = onlyValue(line2['vlocity_cmt__RootItemId__c'])
        line2['vlocity_cmt__AssetReferenceId__c'] = onlyValue(line2['vlocity_cmt__AssetReferenceId__c'])
        line2['Id'] = onlyValue(line2['Id'])
      #  line2['vlocity_cmt__Action__c'] = onlyValue(line2['vlocity_cmt__Action__c'])
        line2['vlocity_cmt__Action__c'].pop('previousValue')
        line2['vlocity_cmt__Action__c'].pop('originalValue')
        line2['vlocity_cmt__Action__c'].pop('messages')
        line2['vlocity_cmt__Action__c'].pop('actions')
        line2['vlocity_cmt__Action__c'].pop('hidden')
      #  line2['vlocity_cmt__Action__c'].pop('editable')  #REQ
      #  line2['vlocity_cmt__Action__c'].pop('dataType')  #REQ
        line2['vlocity_cmt__Action__c'].pop('alternateValues')
      #  line2['vlocity_cmt__Action__c'].pop('label')
       # line2['vlocity_cmt__Action__c'].pop('fieldName')  #REQ

        if 1==1:
          line2['attributeCategories'] = lineItem['attributeCategories']
          line2['attributeCategories']['records'][0]['productAttributes']['records'][2]['userValues'] = 'yyyy5'
          line2['attributeCategories']['records'].pop()
          line2['attributeCategories']['records'].pop()
          line2['attributeCategories']['records'][0]['productAttributes']['records'].pop(0)
          line2['attributeCategories']['records'][0]['productAttributes']['records'].pop(0)

          line2['attributeCategories']['records'][0]['productAttributes'].pop('totalSize')
          line2['attributeCategories']['records'][0]['productAttributes'].pop('messages')

          line2['attributeCategories']['records'][0].pop('displaySequence')
          line2['attributeCategories']['records'][0].pop('Name')
          line2['attributeCategories']['records'][0].pop('id')
          line2['attributeCategories']['records'][0].pop('messages')

        # line2['attributeCategories']['records'][0].pop('Code__c')  REQ

          line2['attributeCategories']['records'][0]['productAttributes']['records'][0].pop('messages')
          line2['attributeCategories']['records'][0]['productAttributes']['records'][0].pop('dataType')
      #   line2['attributeCategories']['records'][0]['productAttributes']['records'][0].pop('inputType',None)   REQ
          line2['attributeCategories']['records'][0]['productAttributes']['records'][0].pop('hasRules')
          line2['attributeCategories']['records'][0]['productAttributes']['records'][0].pop('cloneable')
          line2['attributeCategories']['records'][0]['productAttributes']['records'][0].pop('multiselect')
          line2['attributeCategories']['records'][0]['productAttributes']['records'][0].pop('isNotTranslatable')


      #   line2['attributeCategories']['records'][0]['productAttributes']['records'][0].pop('required')     REQ
          line2['attributeCategories']['records'][0]['productAttributes']['records'][0].pop('attributeId')

          line2['attributeCategories']['records'][0]['productAttributes']['records'][0].pop('filterable')
          line2['attributeCategories']['records'][0]['productAttributes']['records'][0].pop('label')
          line2['attributeCategories']['records'][0]['productAttributes']['records'][0].pop('displaySequence')

          line2['attributeCategories']['records'][0]['productAttributes']['records'][0].pop('disabled',None)
          line2['attributeCategories']['records'][0]['productAttributes']['records'][0].pop('readonly',None)
          line2['attributeCategories'].pop('totalSize')
          line2['attributeCategories'].pop('messages')

          line2['attributeCategories']['records'][0]['productAttributes']['records'][0].pop('values')
          line2['attributeCategories']['records'][0]['productAttributes']['records'][0].pop('hidden',None)
          line2['attributeCategories']['records'][0]['productAttributes']['records'][0].pop('disabled',None)
          line2['attributeCategories']['records'][0]['productAttributes']['records'][0].pop('readonly',None)

        items = {"records":[line2]}
        res = CPQ.updateCartItem_api(cartId,items)  
        filepath = restClient.callSave("update1111",logRequest=True,logReply=False)
        print(res['messages'][0]['message'])
        print(restClient.getLastCallElapsedTime())

        itemsAfter = CPQ.getCartItems_api(cartId,price=False,validate=False)

        line3 = objectUtil.getSiblingWhere(itemsAfter,selectKey='ProductCode',selectKeyValue='C_NOS_SERVICE_TV_003',whereKey='itemType',whereValue='lineItem')['object']
        print(line3['attributeCategories']['records'][0]['productAttributes']['records'][2]['userValues'])
        print()

    def test_update_attribute(self):
        restClient.init('NOSQSM')
        restClient.setLoggingLevel()

        cartId = CPQUtil.create_cart_with_promo('account_2','cart_2','NOS4u 100Mb + Móvel',create=False)

        items = CPQ.getCartItems_api(cartId)

        item = items['records'][1]['lineItems']['records'][0]
        item2 = {}
        item2['attributeCategories'] = item['attributeCategories']
        item2['attributeCategories']['records'].pop()
        item2['attributeCategories']['totalSize'] = 1

        item2['Id'] = item['Id']
        item2['Product2'] = item['Product2']

        item2['PricebookEntry'] = {}
        item2['PricebookEntry']['attributes'] = item['PricebookEntry']['attributes']
        item2['PricebookEntry']['Product2Id'] = item['PricebookEntry']['Product2Id']
        item2['PricebookEntry']['Pricebook2Id'] = item['PricebookEntry']['Pricebook2Id']
        item2['PricebookEntry']['Product2'] = item['PricebookEntry']['Product2']
        item2['PricebookEntry']['Id'] = item['PricebookEntryId']['value']
     #   item2['PricebookEntry']['value'] = item['PricebookEntry']['value']

        item2['PricebookEntry']['Product2'].pop('vlocity_cmt__AttributeDefaultValues__c')
        item2['PricebookEntry']['Product2'].pop('vlocity_cmt__AttributeMetadata__c')

        item2['PricebookEntryId'] = item['PricebookEntryId']

        attributes = CPQ.update_item_attribute_api(cartId,item2)


        print()

    def test_get_cart_items2(seld):
        #restClient.init('NOSDEV')
        #cartId = "8013O000003lX6DQAU"
        restClient.init('DEVNOSCAT4')
        cartId = "8013O0000046OraQAE"
        ts = timeStats.TimeStats()

        ts.new()

        items = CPQ.getCartItems_api(cartId,price=True,validate=False)

     #   filename = restClient.callSave('getItems')
        ts.time('getCartItems_api')

        ts.print()
        print()
    def test_get_cart_items(seld):
        restClient.init('NOSDEV')
        cartId = "8013O000003lX6DQAU"
        #restClient.init('NOSDEV')
        #cartId = "8013O000003lX6DQAU"
        ts = timeStats.TimeStats()

        ts.new()

        items = CPQ.getCartItems_api(cartId,price=True,validate=False)

     #   filename = restClient.callSave('getItems')
        ts.time('getCartItems_api')

        ts.print()
        print()

    def test_get_cart_items_bt(seld):
        restClient.init('DEVNOSCAT4')
        restClient.setLoggingLevel()
        cartId = "8013O0000046OraQAE"

        items = CPQ.getCartItems_api_bt(cartId,price=True,validate=True)
        filename = restClient.callSave('getItems_bt')

        print()


    def test_submit_order(seld):
        restClient.init('DEVNOSCAT2')
        restClient.setLoggingLevel()
        cartId = "8013O000003izGtQAI"

        items = CPQ.checkOut_api(cartId)

        print()

    def test_post_cart_items_Movel(self):
        restClient.init('NOSDEV')
        pricelistF = "Name:Woo Price List"

        self.create_cart_with_offer('account_2','cart_a4','Móvel',pricelistF=pricelistF,create=False)

        print()


    def test_post_cart_items(self):
        restClient.init('DEVNOSCAT4')
        restClient.setLoggingLevel()
        pricelistF = "Name:B2C Price List"

        ts = timeStats.TimeStats()

        #cartId = CPQ.getCartId(f"name:cart_7a3")
        cartId = CPQ.getCartId(f"8013O0000046OraQAE")

        
       # cartId = self.create_cart_with_promo('account_2','cart_7a4','NOS4u 100Mb + Móvel',pricelistF=pricelistF,create=True)
        print(cartId)
        #items = CPQ.getCartItems_api(cartId,price=False,validate=False)
     #   while 1==1:
        items = CPQ.getCartItems_api(cartId,price=False,validate=False)

      #  return

        siblings = objectUtil.getSiblingWhere(items,selectKey='ProductCode',selectKeyValue='C_NOS_SERVICE_OTT_PWR_WIFI_L',whereKey='itemType',whereValue='childProduct')
        C_NOS_SERVICE_OTT_PWR_WIFI_L = siblings['object']
        parentRecord = siblings['objects'][5]

        powerWifi = CPQ._getItemAtPathEx(items,'C_NOS_SERVICE_OTT_PWR_WIFI_L')

        req1,res1 = restClient.callSave('getITems123')
      #  parentRecord = items['records'][0]['productGroups']['records'][0]

        priceBookEntryId = C_NOS_SERVICE_OTT_PWR_WIFI_L['Id']['value']
        parentId = parentRecord['parentLineItemId']
        parentHierarchyPath = parentRecord['productHierarchyPath']

        parentRecord2 = {}
        parentRecord2['Id'] = parentRecord['Id']['value']
        parentRecord2['productId'] = parentRecord['productId']
        parentRecord2['productHierarchyPath'] = parentRecord['productHierarchyPath']
        parentRecord2['itemType'] = parentRecord['itemType']
        parentRecord2['parentLineItemId'] = parentRecord['parentLineItemId']
     #   parentRecord = items['records'][0]['productGroups']['records'][0]

   #     priceBookEntryId = parentRecord['childProducts']['records'][0]['Pricebook2Id']['value']
   #     parentId = items['records'][0]['Id']['value']
   #     parentHierarchyPath = parentRecord['productHierarchyPath']

   #     parentRecord2 = {}
   #     parentRecord2['Id'] = parentRecord['Id']['value']
   #     parentRecord2['productId'] = parentRecord['productId']
   #     parentRecord2['productHierarchyPath'] = parentRecord['productHierarchyPath']
   #     parentRecord2['itemType'] = parentRecord['itemType']
  #      parentRecord2['parentLineItemId'] = parentRecord['parentLineItemId']

        for x in range(0,10):
          ts.new()

          call = CPQ.addItemstoCart_api(cartId,priceBookEntryId,parentRecord=parentRecord,parentId=parentId,parentHierarchyPath=parentHierarchyPath,noResponseNeeded=False,price=False,validate=False)
          ts.time('postCartItem')

          req2,res2 = restClient.callSave("addItemstoCart_api123",logReply=True,logRequest=True)
          
          items2 = CPQ.getCartItems_api(cartId,price=False,validate=False)
          ts.time('getCartItems')

          C_NOS_SERVICE_OTT_PWR_WIFI_L = objectUtil.getSiblingWhere(items2,selectKey='ProductCode',selectKeyValue='C_NOS_SERVICE_OTT_PWR_WIFI_L',whereKey='itemType',whereValue='lineItem')['object']

          itemIds = C_NOS_SERVICE_OTT_PWR_WIFI_L['Id']['value']

          call2 = CPQ.deleteCartItems_api(cartId,itemIds=[itemIds],parentRecord=parentRecord2,price=False,validate=False)
          ts.time('deleteCartItem')

        ts.print()
        print()

    def test_post_cart_items_util(self):
        restClient.init('DEVNOSCAT4')
        pricelistF = "Name:B2C Price List"

        time_series = True
        if time_series:
           timestamp = False
           time_series_dic = {
              'env':'CAT4',
              'offer':'NOS4u 100Meg Movel'
           }
           filename = 'test_stats_ts'
        else:
          timestamp = True
          time_series_dic=None
          filename = 'test_stats'

        ts = timeStats.TimeStats(filename=f'/Users/uormaechea/Documents/Dev/tableau/summer23/{filename}',timestamp=timestamp,append=True,timeseries_dic=time_series_dic)

        for x in range(0,1000):
          try:
            ts.new()

            cartId = CPQ.getCartId(f"8013O0000046OraQAE")

            print(cartId)
            items = CPQ.getCartItems_api(cartId,price=False,validate=False)
            ts.time('getCartItems')

            productCodes = ['C_NOS_SERVICE_OTT_PWR_WIFI_L','C_NOS_SERVICE_COMP_VM_008','C_NOS_SERVICE_COMP_VM_005','C_NOS_SERVICE_COMP_VM_004','C_NOS_EQUIP_SMART_NUMBER_001']
            productCodes = ['C_NOS_SERVICE_OTT_PWR_WIFI_L']

            def pc_name(pc):
              if 'C_NOS_SERVICE_' in pc:
                pname = pc.split('C_NOS_SERVICE_')[1]
              if 'C_NOS_EQUIP_SMART_' in pc:
                pname = pc.split('C_NOS_EQUIP_SMART_')[1]

              return pname
            
            for pc in productCodes:
              pname = pc_name(pc)

              call = CPQUtil.post_cart_item(cartId,items,pc)
              ts.time(f'post_{pname}')
              items2 = CPQ.getCartItems_api(cartId,price=False,validate=False)
              ts.time(f'get_{pname}')

            for pc in productCodes:
              pname = pc_name(pc)
              call = CPQUtil.delete_cart_item(cartId,items2,pc)
              ts.time(f'del_{pname}')

            ts.print()
          except Exception as e:
             print('Exception')

    def test_post_cart_items_util_new(self):
        restClient.init('DEVNOSCAT4')
        pricelistF = "Name:B2C Price List"

        time_series_dic = {
          'env':'CAT4',
          'offer':'NOS4u 100Meg Movel',
          'product':'',
          'create_cart':True,
          'price':False,
          'validate':False,
          'filename':'/Users/uormaechea/Documents/Dev/tableau/summer23/test_stats_ts_xx.csv',
        }
        filename = 'test_stats_ts'

        ts = timeStats.TimeStats(append=True,timeseries_dic=time_series_dic)

        for x in range(0,1000):
          try:
            ts.new()

            if time_series_dic['create_cart']:
              cartId = CPQUtil.create_cart_with_offer(accountname='account_5',cartName='test12',offerName='NOS4u 100Megas Móvel',create=True,timeStats=ts)
            else:
              cartId = CPQ.getCartId(f"8013O0000046OraQAE")

            print(cartId)
            items = CPQ.getCartItems_api(cartId,price=time_series_dic['price'],validate=time_series_dic['validate'])
            ts.time('getCartItems')

            productCodes = ['C_NOS_SERVICE_OTT_PWR_WIFI_L','C_NOS_SERVICE_COMP_VM_008','C_NOS_SERVICE_COMP_VM_005','C_NOS_SERVICE_COMP_VM_004','C_NOS_EQUIP_SMART_NUMBER_001']
            productCodes = ['C_NOS_SERVICE_OTT_PWR_WIFI_L']
            
            for pc in productCodes:
              call = CPQUtil.post_cart_item(cartId,items,pc,price=False,validate=False)
              ts.field('product',pc)
              ts.time(f'post')
              items2 = CPQ.getCartItems_api(cartId,price=False,validate=False)

            for pc in productCodes:
              call = CPQUtil.delete_cart_item(cartId,items2,pc,price=False,validate=False)
              ts.field('product',pc)
              ts.time(f'del')

            if time_series_dic['create_cart']:
              CPQ.deleteCart(cartId)
              ts.time(f'delCart')


            ts.print()
          except Exception as e:
             print('Exception')

    def test_promo_times(self):
        time_series_dic = {
          'init':'DEVNOSCAT4',
          'env':'CAT4',
          'offer':'NOS4u 100Mb + Móvel',
          'promo':True,
          'product':'',
          'create_cart':True,
          'price':False,
          'validate':False,
          'filename':'/Users/uormaechea/Documents/Dev/tableau/summer23/test_stats_ts_xx.csv',
          'productCodes' : ['C_NOS_AGG_SERVICES_OPT_VM']
        }

        restClient.init(time_series_dic['init'])
        pricelistF = "Name:B2C Price List"   

        ts = timeStats.TimeStats(append=True,timeseries_dic=time_series_dic)

        productCodes = time_series_dic['productCodes']
        time_series_dic.pop('init',None)
        time_series_dic.pop('promo',None)
        time_series_dic.pop('filename',None)
        time_series_dic.pop('productCodes',None)


        for x in range(0,10000):
          ts.new()

          cartId,items = CPQUtil.create_cart_with_promo(accountname='account_6',cartName='testPromo1',promoName=time_series_dic["offer"],create=True,timeStats=ts,price=time_series_dic['price'],validate=time_series_dic['validate'])

          print(cartId)
        #  items = CPQ.getCartItems_api(cartId,price=time_series_dic['price'],validate=time_series_dic['validate'])
        #  filename = restClient.callSave('xxxxxx')
        #  ts.time('getCartItems')

          for pc in productCodes:
              call = CPQUtil.post_cart_item(cartId,items,pc,price=False,validate=False)
              ts.field('product',pc)
              ts.time(f'post')

          items2 = CPQ.getCartItems_api(cartId,price=False,validate=False)
          ts.time('getCartItems')

          for pc in productCodes:
              call = CPQUtil.post_promo_item(cartId,items2,pc,time_series_dic['offer'],price=True,validate=True)
              ts.time(f'promoItem')

          for pc in productCodes:
              call = CPQUtil.delete_cart_item(cartId,items2,pc,price=False,validate=False)
              ts.field('product',pc)
              ts.time(f'del')

          if time_series_dic['create_cart']:
              CPQ.deleteCart(cartId)
              ts.time(f'delCart')


    def test_promo_from_file(self):
       jstr= jsonFile.read('/Users/uormaechea/Documents/Dev/python/InCliLib/incli/output/xxxxx2_res.json')

       CPQUtil.post_promo_item(jstr,'C_NOS_SERVICE_OTT_PWR_WIFI_L','NOS4u 100Mb + Móvel') 
       print()

    def test_getCartItems_x(self):
        restClient.init('NOSDEV')
        q="""SELECT id,
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
                    nos_t_channel__c,
                    nos_t_process__c,
                    nos_b_isbsimulation__c 
                    FROM Order WHERE Id IN ('8013O000003keqvQAA')"""
        res = query.query(q)

        print(restClient.getLastCallAllTimes())

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
                      FROM OrderItem WHERE OrderId = '{res['records'][0]['Id']}'  ORDER BY vlocity_cmt__LineNumber__c """
        res2 = query.query(q2)
        print(restClient.getLastCallAllTimes())

        idl = [r['Id'] for r in res2['records']]
        lineItemIds = query.IN_clause(idl)

        q3 = f"""SELECT vlocity_cmt__OrderAppliedPromotionId__r.vlocity_cmt__PromotionId__c,
                        vlocity_cmt__OrderAppliedPromotionId__r.vlocity_cmt__Action__c,
                        vlocity_cmt__OrderItemId__c 
                        FROM vlocity_cmt__OrderAppliedPromotionItem__c 
                        WHERE vlocity_cmt__OrderItemId__c IN ({lineItemIds})"""
        res3 = query.query(q3)

        print(restClient.getLastCallAllTimes())
        print()
    def test_clone_item(self):
        restClient.init('DEVNOSCAT4')

        CPQ.clone_item_api("8013O000004AoXHQA0","8023O0000060FZJQA2",None)

    def test_save_order(self):
        restClient.init('DEVNOSCAT4')
        cartId = '8013O000004AoXHQA0'

        items = CPQ.getCartItems_api(cartId,price=False,validate=False)

        filename = restClient.callSave(f'cartItems{cartId}')

        print()

    def test_order_stats(self):
      file = '/Users/uormaechea/Documents/Dev/python/InCliLib/InCLipkg/test/files/cartItems8013O000004AoXHQA0_res.json'
      
      items = jsonFile.read(file)

      counters = CPQUtil.cart_stats(items)

      print(counters)

    def test_getting_siblings(self):
      file = '/Users/uormaechea/Documents/Dev/python/InCliLib/InCLipkg/test/files/cartItems8013O000004AoXHQA0_res.json'
      
      items = jsonFile.read(file)

      CPQUtil.get_ol(items,'C_NOS_OFFER_017:C_NOS_AGG_SERVICES_OPT_VM|2:C_NOS_SERVICE_VM_001')      
      
      CPQUtil.get_ol(items,'C_NOS_OFFER_017XXX:C_NOS_AGG_SERVICES_OPT_VM|2:C_NOS_SERVICE_VM_001')

      CPQUtil.get_ol(items,'C_NOS_OFFER_017:C_NOS_AGG_SERVICES_OPT_VM|9:C_NOS_SERVICE_VM_001')      

      ##siblings = objectUtil.getSiblingWhere(items,selectKey='ProductCode',selectKeyValue='C_NOS_AGG_SERVICES_OPT_VM',whereKey='itemType',onlyOne=False)
      print()

