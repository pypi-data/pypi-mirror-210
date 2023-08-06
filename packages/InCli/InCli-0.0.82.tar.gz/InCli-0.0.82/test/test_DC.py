import unittest
from InCli import InCli
from InCli.SFAPI import account,restClient,digitalCommerce,digitalCommerceUtil,utils,CPQ,timeStats

class Test_DC(unittest.TestCase):
    def test_catalogs(self):
        restClient.init('DEVNOSCAT4')

        catalogs = digitalCommerce.getCatalogs()

        print()

    def test_getOffers(self):
        restClient.init('DEVNOSCAT4')

    #    catalogs = digitalCommerce.getCatalogs()
        catalogs =['DCTEST','MPOTEST']
        for catalog in catalogs:
            try:
                offers = digitalCommerce.getOfferByCatalogue(catalog)
                print(f"offers: {len(offers)}")
            except Exception as e:
                print(f"{catalog}  {e.args[0]['error']}")

        print()

    def test_create_Basket_config(self):
        restClient.init('DEVNOSCAT4')

        catalog ='DCTEST'
        offer ='C_WOO_MOBILE'
        try:
            details = digitalCommerce.getOfferDetails(catalog,offer)
            digitalCommerce.createBasketAfterConfig(catalog,details)
            print(f"offers: {len(details)}")
        except Exception as e:
            print(f"{catalog}  {e.args[0]['error']}")

        print()

    def test_getOffer_details(self):
        restClient.init('DEVNOSCAT4')

        catalog ='DCTEST'
        offer ='C_WOO_MOBILE'
        try:
            offers = digitalCommerce.getOfferDetails(catalog,offer)
            print(f"offers: {len(offers)}")
        except Exception as e:
            print(f"{catalog}  {e.args[0]['error']}")

        print()

    def test_create_Basket(self):
        restClient.init('DEVNOSCAT4')

        catalog ='DCTEST'
        offer ='C_WOO_MOBILE'
        try:
            basket = digitalCommerce.createBasket(catalog,offer)

            print(f"offers: {len(basket)}")
        except Exception as e:
            print(f"{catalog}  {e.args[0]['error']}")

        print()

    def test_create_Basket_cart(self):
        restClient.init('DEVNOSCAT4')

        catalog ='DCTEST'
        offer ='C_WOO_MOBILE'
        try:
            basket = digitalCommerce.createBasket(catalog,offer)
            accountId ='0013O000017xZ2UQAU'
            digitalCommerce.createCart(accountId,catalog,cartContextKey=basket['cartContextKey'])

            print(f"offers: {len(basket)}")
        except Exception as e:
            print(f"{catalog}  {e.args[0]['error']}")

        print()

        #getItemAttributes {ATT_MOBILE_NUMBER=null, ATT_ORDER_TYPE=null, ATT_PORT_ACTIVE_ICCID=null, ATT_PORT_ACTIVE_MOBILE_TARIFF=null, ATT_PORT_CVP_NUMBER=null, ATT_PORT_DATE=null, ATT_PORT_DOC_UPLOAD_DATE=null, ATT_PORT_MOBILE_NUMBER=null, ATT_PORT_ORIGIN_ISP=null, ATT_PORT_ORIGIN_OWNER_NAME=null, ...}
    
        
    def test_DEVNOSCAT4_C_WOO_MOBILE(self):
        restClient.init('DEVNOSCAT4')
        self.test_WOO_Mobile('DCTEST',userValue=21,iterations=1)

    def test_NOSDEV_C_WOO_MOBILE(self):
        restClient.init('NOSDEV')
        self.test_WOO_Mobile('DC_CAT_WOO_MOBILE')

    def test_WOO_Mobile(self,catalog,userValue=200,iterations=3):
        offer ='C_WOO_MOBILE'

        for i in range(0,iterations):
            try:
                restClient.new_time_record()

                details = digitalCommerce.getOfferDetails(catalog,offer,ts_name='getOfferDetails')

                updated = digitalCommerceUtil.updateOfferField(details,'ATT_NOS_OTT_SUBSCRIPTION_ID','userValues',userValue+i,'code')

                basket = digitalCommerce.createBasketAfterConfig(catalog,updated,ts_name='createBasketAfterConfig')
              #  basket = digitalCommerce.createBasket(catalog,basketAction='AddWithNoConfig',offer=offer)

                bd = digitalCommerce.getBasketDetails(catalog,basket['cartContextKey'])

                filename = restClient.callSave('getBasketDetails_111')

                res = digitalCommerce.addChildBasket(bd,"C_VOICE_MOBILE_TARIFFS:C_VOICE_MOBILE_SERVICE_001",ts_name='add_SERVICE_001')

                res = digitalCommerce.addChildBasket(bd,"C_SIM_E-SIM_CARD:C_SIM_CARD",ts_name='add_C_CIM_CARD')

                res = digitalCommerce.addChildBasket(bd,"C_COMPLEMENT_SERVICE:C_EXTRAS_DATA_3GB",ts_name='add_DATA_3GB')

                accountId ='0013O000017xZ2UQAU'
                res = digitalCommerce.createCart(accountId,catalog,cartContextKey=basket['cartContextKey'],ts_name='createCart')

                orderId = res['orderId']

                res1 = CPQ.deleteCart(orderId,ts_name='deleteCart')


            except Exception as e:
                filename = restClient.callSave('request_DC_111',logRequest=True,logReply=False)
                utils.printException(e)
                #ts.time_no("Error",e.args[0]['errorCode'])
               # ts.print()

        restClient.time_print()

        print()

    def test_DCTEST_C_MPO_Mobile100(self):
        restClient.init('DEVNOSCAT4')

        catalog ='MPOTEST'
        offer ='C_NOS_OFFER_001'
        ts = timeStats.TimeStats()
        ts.new()

        try:
            details = digitalCommerce.getOfferDetails(catalog,offer)

            ts.time('getOfferDetails')

            filename = restClient.callSave('mpodetails111')

            updated = digitalCommerceUtil.updateOfferField(details,'ATT_SERIAL_NUMBER','userValues',1113,'code')

            basket = digitalCommerce.createBasketAfterConfig(catalog,details)
            #basket = digitalCommerce.createBasket(catalog,basketAction='AddWithNoConfig',offer=offer)



            print(f"createBasketAfterConfig: {restClient.getLastCallAllTimes()}")

            bd = digitalCommerce.getBasketDetails(catalog,basket['cartContextKey'])
            ts.time('getBasketDetails')

            filename = restClient.callSave('getBasketDetails_111')

            res = digitalCommerce.addChildBasket(bd,"C_NOS_AGG_EQUIPS_TV_OPT_UMA:C_NOS_EQUIP_TV_005")
            ts.time('add_TV_005')

            res = digitalCommerce.addChildBasket(bd,"C_NOS_AGG_MOBILE_DATA:C_NOS_SERVICE_VM_004")
            ts.time('add_VM_004')

            res = digitalCommerce.addChildBasket(bd,"C_NOS_OFFER_001:C_NOS_AGG_SERVICES_OPT_VM")
            ts.time('add_OPT_VM')

            accountId ='0013O000017xZ2UQAU'
            res = digitalCommerce.createCart(accountId,catalog,cartContextKey=basket['cartContextKey'])
            ts.time('createCart')

            orderId = res['orderId']

            res1 = CPQ.deleteCart(orderId)
            ts.time('deleteCart')

            ts.print()
            print()

        except Exception as e:
            filename = restClient.callSave('request_DC_111',logRequest=True,logReply=False)
            utils.printException(e)
            ts.time_no("Error",e.args[0]['errorCode'])
            ts.print()


        print()

    def test_DCTEST_MOBILE_TRIAL(self):
        restClient.init('DEVNOSCAT4')

        catalog ='DCTEST'
        offer ='PROMO_WOO_MOBILE_TRIAL'
        try:
            details = digitalCommerce.getOfferDetails(catalog,offer)
            print(f"getOfferDetails: {restClient.getLastCallAllTimes()}")

            updated = digitalCommerceUtil.updateOfferField(details,'ATT_NOS_OTT_SUBSCRIPTION_ID','userValues',1113,'code')

           # basket = digitalCommerce.createBasketAfterConfig(catalog,updated)AddAfterConfig
        #    basket = digitalCommerce.createBasket(catalog,basketAction='AddWithNoConfig',offer=offer)
            basket = digitalCommerce.createBasket(catalog,basketAction='AddAfterConfig',offer=offer)

            #basket = digitalCommerce.createBasket(catalog,'',basketAction='AddAfterConfig',productConfig=updated)

            print(f"createBasketAfterConfig: {restClient.getLastCallAllTimes()}")

            bd = digitalCommerce.getBasketDetails(catalog,basket['cartContextKey'])
            print(f"getBasketDetails: {restClient.getLastCallAllTimes()}")

            filename = restClient.callSave('getBasketDetails_111')

            res = digitalCommerce.addChildBasket(bd,"C_VOICE_MOBILE_TARIFFS:C_VOICE_MOBILE_SERVICE_001")
            print(f"addChildBasket: {restClient.getLastCallAllTimes()}")

            res = digitalCommerce.addChildBasket(bd,"C_SIM_E-SIM_CARD:C_SIM_CARD")
            print(f"addChildBasket: {restClient.getLastCallAllTimes()}")

            res = digitalCommerce.addChildBasket(bd,"C_COMPLEMENT_SERVICE:C_EXTRAS_DATA_3GB")
            print(f"addChildBasket: {restClient.getLastCallAllTimes()}")

            accountId ='0013O000017xZ2UQAU'
            res = digitalCommerce.createCart(accountId,catalog,cartContextKey=basket['cartContextKey'])
            print(f"createCart: {restClient.getLastCallAllTimes()}")

            orderId = res['orderId']

            res1 = CPQ.deleteCart(orderId)
            print(f"deleteCart: {restClient.getLastCallAllTimes()}")

            print()

        except Exception as e:
            filename = restClient.callSave('request_DC_111',logRequest=True,logReply=False)
            utils.printException(e)

        print()