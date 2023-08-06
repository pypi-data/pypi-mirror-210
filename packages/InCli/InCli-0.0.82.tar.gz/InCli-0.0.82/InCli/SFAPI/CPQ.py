import logging, copy
from . import Sobjects, objectUtil, priceBook, query as queryM, utils,restClient
from datetime import date
import simplejson 


_carts = []
def _get(Id):
    for cart in _carts:
        if cart['Id'] == Id:
            return cart
def _set(Id,name,pricelistId,accountId):
    global _carts
    _carts.append({
        'Id':Id,
        'name':name,
        'plId':pricelistId,
        'accId':accountId
    })
#------------------------------------------------------------------------

def stringify(parameters,exclude,initSeparator='?'):
  isFirst = True

  ret = ''
  for name in parameters:
    if name in exclude:
      continue
    if(parameters[name] == None):
      continue
    separator = initSeparator if isFirst == True else '&'
    value = parameters[name]
    if isinstance(value, str) == False:
      value = simplejson.dumps(value)
    paramStr = f'{separator}{name}={value}'
    ret = ret + paramStr
    isFirst = False

  return ret


#------------------------------------------------------------------------
def checkError():
    lc = restClient.lastCall()
    if lc['error'] is not None:
      utils.raiseException(lc['errorCode'],lc['error'],lc['action'])
    response = lc['response']
    if 'messages' in response:
        if len(response['messages']) > 0:
            msg = response['messages'][0]
            if 'code' in msg:
                if msg['code'] == '208': return False
                if msg['code'] == '101': return False
                if msg['code'] == '204': return False  #missing attribute

                if msg['severity'] == 'ERROR':  utils.raiseException(msg['code'],msg['message'])

    return False

#------------------------------------------------------------------------
def getCartId(orderF):
    cartId = Sobjects.IdF('Order',orderF)
    return cartId

def createQuote(opportunityid,pricelistName,name, recordTypeId,expirationDate = "2023-01-17" ,inputFields = None,fields='Id,Name,EffectiveDate'):
    global _carts

    Body = {
    "methodName": "createCart",
    "objectType": 'Quote',
    "inputFields": [
        {"opportunityid": opportunityid},
        {"Name": name},
        {"ExpirationDate": expirationDate},
        {"RecordTypeId": recordTypeId},
        {"pricelistName": pricelistName}
        ],
    "subaction":'createQuote',
    "fields": fields
    }     

    if inputFields != None:
        Body['inputFields'] = Body['inputFields'] + inputFields

    call = restClient.callAPI('/services/apexrest/vlocity_cmt/v2/carts',
                                method="post",
                                data=Body)
    logging.info(f"Quote {name} created with code {restClient.lastCall()['status_code']}")

  #  _set(call['records'][0]['Id'],name,pricelistId,accountId)
    checkError()
    return  call

def createCart_api(accountId,pricelistId,name='', subaction='createOrder',effectivedate =  date.today().strftime("%Y-%m-%d"),channel='python',inputFields = None,fields='Id,Name,EffectiveDate'):
    """
    - subaction: createOrder or createQuote
    RETURNS: ['records'][0]['Id']"""
    global _carts

    objectType = "Order"
    if subaction == 'createQuote':
        objectType = "Quote"

    if subaction == 'createOrder':
        Body = {
            "methodName": "createCart",
            "objectType": objectType,
            "inputFields": [
                {"effectivedate": effectivedate },
                {"status": "Draft"},
                {"Name": name},
                {"AccountId": accountId},
                {"vlocity_cmt__PriceListId__c": pricelistId}#, 
      #          {"vlocity_cmt__OriginatingChannel__c": channel}
                ],
            "subaction":subaction,
            "fields": fields
            }

    if inputFields != None:
        list_inputFields = [{k: v} for k, v in inputFields.items()]
        for inF in list_inputFields: 
            Body['inputFields'].append(inF)

    call = restClient.callAPI('/services/apexrest/vlocity_cmt/v2/carts',
                                method="post",
                                data=Body)

    checkError()
    restClient.glog().info(f"Cart {name} created with Id {call['records'][0]['Id']} for {accountId}")

   # _set(call['records'][0]['Id'],name,pricelistId,accountId)

    return call

def createCart(accountF,pricelistF,name,checkExists=False,subaction='createOrder',effectivedate =  date.today().strftime("%Y-%m-%d"),channel='python',inputFields=None,fields='Id,Name,EffectiveDate'):
    """
    As per create cart API.
    - accountF as extended field
    - pricelistF as extended field
    - name: the name for the cart
    - checkExists: will query for a cart with that name. if exist will return it and not create another one. 
    - RETURNS: the cart Id
    """
    if type(accountF) is dict:
        accountId = utils.Id(accountF)
    else:
        accountId = queryM.queryIdF('Account',accountF)
    
    pricelistId = queryM.queryIdF('vlocity_cmt__PriceList__c',pricelistF)

    if checkExists:
        cartId = queryM.queryField(f" select Id from Order where Name ='{name}' and AccountId='{accountId}' ")
        if cartId != None:
            restClient.glog().info(f"Cart with Name {name} exists. Returning existing")
            _set(cartId,name,pricelistId,accountId)
            return cartId

    cartCall= createCart_api(accountId,pricelistId,name,subaction,effectivedate,channel,inputFields,fields)
    cartId = cartCall['records'][0]['Id']
    return cartId

def createCartFromAsset(assetId, accountId, date, inputFields=None):
    """As per assetToOder API
    - inputFields: sets the fields in the Cart. Json of the form {"Name":"value"}
    - return value is the cart Id, or an exception is thrown
    """
    call = createCartFromAsset_api(assetId,accountId,date)

    id = call['records'][0]['cartId']

    if inputFields != None:
        data = inputFields
        Sobjects.update(id, data)
        restClient.glog().info(f"Cart updated with inputFields {inputFields}.")

    return id

def createCartFromAsset_api(assetId, accountId, date):
    """As per the API
    - return ['records'][0]['cartId']"""
    if type(assetId) == list:
        assetId = ",".join(assetId)

    data = {
        "subaction": "assetToOrder",
        "id": assetId,
        "accountId": accountId,
        "requestDate": date
    }

    call = restClient.callAPI('/services/apexrest/vlocity_cmt/v2/carts',method="post",data=data)
    checkError()
    restClient.glog().info(f"Created Cart {call['records'][0]['cartId']} from asset {assetId} for account {accountId}")

    return call

def getCartSummary_api(cartid,validate=None,price=None,headerFieldSet=None,translation=None):

    paramStr = stringify(locals(),exclude=['cartid'])
    action = f'/services/apexrest/vlocity_cmt/v2/cpq/carts/{cartid}{paramStr}'

    call = restClient.callAPI(action)
    checkError()
    return call

def deleteCart(cartId,cartType='Order',ts_name=None):
    delete = Sobjects.delete('Order',cartId,ts_name=ts_name)
    checkError()
    restClient.glog().info(f"Cart {cartId} deleted.")
    return delete

def get_item_attributes_NO(cart_ID,item_ID):
    action = f'/services/apexrest/vlocity_cmt/v2/cpq/carts/{cart_ID}/items/{item_ID}/itemAttributes'

    call = restClient.callAPI(action)
    checkError()
    return call

def update_item_attribute_api(cartId,item):
    itemId = Sobjects.Id(cartId)
   # itemId = item['Id']['value']
    action = f'/services/apexrest/vlocity_cmt/v2/cpq/carts/{cartId}/items/{itemId}/itemAttributes'
    method ='Put'
    params= {
        "methodName": "putItemAttributes",
        "items": {
            "records": [
                item
            ]
        },
        "filters": None,
        "itemId": itemId,
        "id": itemId,
        "cartId": cartId,
        "price":False,
        "validate":False
    }
    call = restClient.callAPI(action,method=method,data=params)
    filepath = restClient.callSave('attributes123',logRequest=True,logReply=False)

    checkError()
    return call

def runCartValidation_api(cartid,validate=None,price=None):

    paramStr = stringify(locals(),exclude=['cartid'])
    action = f'/services/apexrest/vlocity_cmt/v2/cpq/carts/{cartid}{paramStr}'

    body=    {
        "cartId":cartid,
        "methodName":"runCartValidation"#,
      #  "price":true,
      #  "validate":true
        }
    call = restClient.callAPI(action,method='post',data=body)
    checkError()
    return call

def getCartItems_api_bt(cartId, query=None,id=None,lastRecordId=None,pagesize=None,hierarchy=None,includeAttachment=None,headerFieldSet=None,filter=None,price=None,validate=None,fields=None):
    paramStr = stringify(locals(),exclude=['cartId'])

    action = f'/services/apexrest/v1/getcartitems/{cartId}/items'

    print(action)

    call = restClient.callAPI(action)
    checkError()
    return call

def getCartItems_api(cartId, query=None,id=None,lastRecordId=None,pagesize=None,hierarchy=None,includeAttachment=None,headerFieldSet=None,filter=None,price=None,validate=None,fields=None):
    paramStr = stringify(locals(),exclude=['cartId'])

    action = f'/services/apexrest/vlocity_cmt/v2/cpq/carts/{cartId}/items{paramStr}'    

    call = restClient.callAPI(action)
    checkError()
    return call

def addItemstoCart(cartId,productCode,pricelistF,parentId=None,parentHierarchyPath=None,parentRecord=None,price=True,validate=True,hierarchy=None,pagesize=None,includeAttachment=None,expandAll=None,fields=None,noResponseNeeded=False):
    plEF = utils.extendedField(pricelistF)
    pb2Id = queryM.queryField(f" select vlocity_cmt__Pricebook2Id__c from vlocity_cmt__PriceList__c where {plEF['field']} = '{plEF['value']}' ")
    pricebookEntryId = queryM.queryField(f" select Id from PricebookEntry where ProductCode='{productCode}' and Pricebook2Id = '{pb2Id}' ")

    #priceBookEntryId = priceBook.pricebookEntryId_pl(_get(cartId)['plId'],productCode,pricelistField='Id')
    return addItemstoCart_api(cartId,pricebookEntryId,parentId,parentHierarchyPath,parentRecord,price,validate,hierarchy,pagesize,includeAttachment,expandAll,fields,noResponseNeeded)

def addItemstoCart_api_bt(cartId,priceBookEntryId,parentId=None,parentHierarchyPath=None,parentRecord=None,price=True,validate=True,hierarchy=None,pagesize=None,includeAttachment=None,expandAll=None,fields=None,noResponseNeeded=False):
    paramStr = stringify(locals(),exclude=['cartId','itemIds','parentRecord','priceBookEntryId'])

    action = f'/services/apexrest/v2/postcartitems/{cartId}/items?noResponseNeeded=true'

    data = {
        "items": [{
            "itemId": priceBookEntryId,  
        }]
    }

    if parentRecord != None:
        data = {
            "methodName": "postCartsItems",
            "items": [{
                "parentId": parentId,
                "parentHierarchyPath": parentHierarchyPath,
                "itemId": priceBookEntryId,  
                "parentRecord": {
                    "records": [
                        parentRecord
                    ]
                }

            }],
            "cartId": cartId,
            "price": price,
            "validate": validate,
            "includeAttachment": False,
            "pagesize": 10,
            "lastRecordId": None,
            "hierarchy": -1,
            "query": None
        }
    if noResponseNeeded == True:
        data['noResponseNeeded'] = True

    call = restClient.callAPI(action,method='post',data=data)

    restClient.glog().info(f"added {priceBookEntryId} to cart {cartId}")
    checkError()
    return call

def addItemstoCart_api(cartId,priceBookEntryId,parentId=None,parentHierarchyPath=None,parentRecord=None,price=True,validate=True,hierarchy=None,pagesize=None,includeAttachment=None,expandAll=None,fields=None,noResponseNeeded=False):
    paramStr = stringify(locals(),exclude=['cartId','itemIds','parentRecord','priceBookEntryId'])

    action = f'/services/apexrest/vlocity_cmt/v2/cpq/carts/{cartId}/items{paramStr}'

    data = {
        "items": [{
            "itemId": priceBookEntryId,  
        }]
    }

    if parentRecord != None:
        data = {
            "methodName": "postCartsItems",
            "items": [{
                "parentId": parentId,
                "parentHierarchyPath": parentHierarchyPath,
                "itemId": priceBookEntryId,  
                "parentRecord": {
                    "records": [
                        parentRecord
                    ]
                }

            }],
            "cartId": cartId,
            "price": price,
            "validate": validate,
            "includeAttachment": False,
            "pagesize": 10,
            "lastRecordId": None,
            "hierarchy": -1,
            "query": None
        }
    if noResponseNeeded == True:
        data['noResponseNeeded'] = True

    call = restClient.callAPI(action,method='post',data=data)

    restClient.glog().info(f"added {priceBookEntryId} to cart {cartId}")
    checkError()
    return call

def clone_item_api(cartId,itemId,price=False,validate=False):
    """return all items as per getCartItems"""

    action = f'/services/apexrest/vlocity_cmt/v2/cpq/carts/{cartId}/items/clone'

    data = {
        "methodName": "cloneItems",
        "items": [
            {
            "itemId": itemId#,
            #"parentRecord": parentRecord
            }
        ],
        "id": itemId,
        "cartId": cartId,
        "price": price,
        "validate": validate
    }
    call = restClient.callAPI(action,method='post',data=data)
    checkError()
    return call

def updateCartItem_api(cartId, items,price=False,validate=False):

    action = f'/services/apexrest/vlocity_cmt/v2/cpq/carts/{cartId}/items'
    data = {
        "methodName": "putCartsItems",
        "items": items,
        "price": price,
        "validate": validate,
        "includeAttachment": False ,
      #  "pagesize": 10,
      #  "lastRecordId": None,
        "hierarchy": 5#,
      #  "query": None,
      #  "filters": None,
       # "fields": "vlocity_cmt__BillingAccountId__c,vlocity_cmt__ServiceAccountId__c,Quantity,vlocity_cmt__RecurringTotal__c,vlocity_cmt__OneTimeTotal__c,vlocity_cmt__OneTimeManualDiscount__c,vlocity_cmt__RecurringManualDiscount__c,vlocity_cmt__ProvisioningStatus__c,vlocity_cmt__RecurringCharge__c,vlocity_cmt__OneTimeCharge__c,ListPrice,vlocity_cmt__ParentItemId__c,vlocity_cmt__BillingAccountId__r.Name,vlocity_cmt__ServiceAccountId__r.Name,vlocity_cmt__PremisesId__r.Name,vlocity_cmt__InCartQuantityMap__c,vlocity_cmt__EffectiveQuantity__c"
        }
    call = restClient.callAPI( action, method="put",data=data)
    checkError()
    return call

def _getItemAtPath(obj,path,field='ProductCode'):
    for p in path.split(':'):
        obj = objectUtil.getSibling(obj,field,p)  
    return obj
def _getItemAtPathEx(obj,path,field='ProductCode'):
    obj = objectUtil.getSiblingEx(obj,field,path)  
    return obj

def addToCart_action(parentItem,product,field='ProductCode'):
    sibbling = objectUtil.getSiblingWhere(parentItem,field,product,'itemType','childProduct')['object']
    if sibbling == None:
        logging.warn("The expand does not have a reference to the product. {field}:{product}")
        return None

    actions = objectUtil.getSiblingWhere(sibbling,selectKey='actions')['object']

    if 'records' in parentItem:
        parentItem = parentItem['records'][0]
    parentItem = copy.deepcopy(parentItem)
    parentItem['childProducts'] = ""   

    call = executeActions(actions,'addtocart',parentItem=parentItem)

    logging.info(f"Adding to cart with expansion. Product {product}")

    return call

def addToCart(cartId,parentProductName,productName,field='name',cartItems=None):

    restClient.logCall('getCartItems12')
    if cartItems == None:
        cartItems = getCartItems_api(cartId)

    parentItem = _getItemAtPath(cartItems,parentProductName,field)
    #parentItem = jsonUtil.getSibling(cartItems,'name',parentProductName,logValues=True)
    item = objectUtil.getSibling(parentItem,'name',productName)
   # if item == '':
   #     expanditems = 

    parentItem = copy.deepcopy(parentItem)
    parentItem['childProducts'] = ""

    execute = executeActions(item,parentItem=parentItem)
    return execute

def expand_action(cartItems,sibling,field='ProductCode'):    
    sibblingItem = objectUtil.getSiblingWhere(cartItems,field,sibling,'itemType','lineItem')
    if sibblingItem['object'] == None:
        sibblingItem = objectUtil.getSiblingWhere(cartItems,field,sibling,'itemType','productGroup')

    call = executeActions(sibblingItem['object']['actions'],'expanditems')
    logging.info(f"Expanding {sibling}")
    return call

def expand_api(cartId,itemId,productHierarchyPath):
    paramStr = stringify(locals(),exclude=[], initSeparator='?')

    action = f'/services/apexrest/vlocity_cmt/v2/cpq/carts/{cartId}/items/{itemId}/expand{paramStr}'

    call = restClient.callAPI( action, method="get")
    checkError()
    return call

def executeRestAction_api(rest):
    link = rest['link']
    params = rest['params']
    method = f"{rest['method']}".lower()

    call = restClient.callAPI(link, method=method, data=params)
    return call

def executeActions(actionsObject, actionName='addtocart', parentItem=None):
    if 'actions' in actionsObject:
        actions = actionsObject['actions']

    rest = actionsObject[actionName]['rest']
    if actionName == 'addtocart':
        rest['params']['items'][0]['parentRecord'] = {"records": [parentItem]}

    call = executeRestAction_api(rest)
    return call

def deleteCartItems_api(cartId, itemIds,parentRecord=None,hierarchy=None,lastRecordId=None,pagesize=None,includeAttachment=None,fields=None,query=None,filters=None,price=True,validate=True):
    paramStr = stringify(locals(),exclude=['cartid','itemIds'],initSeparator='&')
    paramStr = ''
    action =  f'/services/apexrest/vlocity_cmt/v2/cpq/carts/{cartId}/items?id={",".join(itemIds)}{paramStr}'
    if parentRecord == None:
        requestBody = {
            "items": [{
                "itemId": ",".join(itemIds)
            }]#,
        # "price": True,
        # "validate": True
        }
    if parentRecord != None:
        requestBody = {
            "methodName": "deleteCartsItems",
            "id": itemIds,
            "filters": filters,
            "fields": fields,
            "cartId": cartId,
            "price": price,
            "validate": validate,
            "includeAttachment": False,
            "pagesize": 10,
            "lastRecordId": None,
            "hierarchy": -1,
            "query": None,
            "items": [
                {
                    "parentRecord": {
                        "records": [
                            parentRecord
                        ]
                    }
                }
            ]
        }
   # parentRecord['noResponseNeeded'] = True  #This does not work

    call = restClient.callAPI(action,method="delete",data=requestBody)
    checkError()
    restClient.glog().info(f"Deleted cart Item {itemIds} for cart {cartId}")

    return call
#{"methodName":"deleteCartsItems","id":"802Dn000000dnsgIAA","filters":null,"fields":"vlocity_cmt__BillingAccountId__c,vlocity_cmt__ServiceAccountId__c,Quantity,vlocity_cmt__RecurringTotal__c,vlocity_cmt__OneTimeTotal__c,vlocity_cmt__OneTimeManualDiscount__c,vlocity_cmt__RecurringManualDiscount__c,vlocity_cmt__ProvisioningStatus__c,vlocity_cmt__RecurringCharge__c,vlocity_cmt__OneTimeCharge__c,ListPrice,vlocity_cmt__ParentItemId__c,vlocity_cmt__BillingAccountId__r.Name,vlocity_cmt__ServiceAccountId__r.Name,vlocity_cmt__PremisesId__r.Name,vlocity_cmt__InCartQuantityMap__c,vlocity_cmt__EffectiveQuantity__c","cartId":"801Dn000000cv2EIAQ","price":true,"validate":true,"includeAttachment":true,"pagesize":10,"lastRecordId":null,"hierarchy":-1,"query":null}

#was retrieved via SOQL without querying the requested field: OrderItem.vlocity_cmt__AssetReferenceId__c
def getCartPromotions(cartF,getPromotionsAppliedToCart=False,query=None,include=None,includePenalties=None,ruleType=None,ruleEvaluationInput=None,filters=None,category=None,fields=None,pagesize=None,commitmentDateFilter=None,appliedPromoStatusFilter=None,onlyOne=False):
    cartId = queryM.queryIdF('Order',cartF)
    promos = getCartPromotions_api(cartId=cartId,
                            getPromotionsAppliedToCart=getPromotionsAppliedToCart,
                            query=query,
                            include=include,
                            includePenalties=includePenalties,
                            ruleType=ruleType,
                            ruleEvaluationInput=ruleEvaluationInput,
                            filters=filters,
                            category=category,
                            fields=fields,
                            pagesize=pagesize,
                            commitmentDateFilter=commitmentDateFilter,
                            appliedPromoStatusFilter=appliedPromoStatusFilter
                            )
    if promos == None:
        return None
    if onlyOne:
        promo = [promo  for promo in promos if promo['Name'] == query]
        if len(promo) == 0:
            return None
        return promo[0]
    return promos

def getCartPromotions_api(cartId,getPromotionsAppliedToCart=False,query=None,include=None,includePenalties=None,ruleType=None,ruleEvaluationInput=None,filters=None,category=None,fields=None,pagesize=None,commitmentDateFilter=None,appliedPromoStatusFilter=None):
    subaction =  "getPromotionsAppliedToCart" if getPromotionsAppliedToCart == True else None

    paramStr = stringify(locals(),exclude=['cartId','getPromotionsAppliedToCart'])
    action = f'/services/apexrest/vlocity_cmt/v2/cpq/carts/{cartId}/promotions{paramStr}'

    call = restClient.callAPI(action)
    checkError()
    if call['totalSize'] == 0:
        return None
    return call['records']

def postCartsPromoItems_api(cartId, promotionId,price=True,validate=True,contextLineItemIds=None):
    action = f'/services/apexrest/vlocity_cmt/v2/cpq/carts/{cartId}/promotions?cartId={cartId}&id={promotionId}'

    data = {
        "methodName": "postCartsPromoItems",
        "items": [{
            "itemId": promotionId
        }],
        "promotionId": promotionId,
        "cartId": cartId,
        "price":price,
        "validate":validate
    }
    if contextLineItemIds != None:
        data['items'][0]['contextLineItemIds'] = contextLineItemIds
        data['items'][0]['isPartialPromo'] = True

    call = restClient.callAPI(action, method='post', data=data)
    checkError()
    restClient.glog().info(f"Promo {promotionId} added to cart {cartId}")
    return call


def deleteCartPromotion(cartF, promotion,price=True,validate=True):
    cartId = queryM.queryIdF('Order',cartF)

    if 'Id' in promotion:
        promotion = promotion['Id']
    if 'value' in promotion:
        promotion = promotion['value']
    return deleteCartPromotion_api(cartId=cartId, promotionId=promotion,price=price,validate=validate)

def deleteCartPromotion_api(cartId, promotionId,price=True,validate=True):
    action = f'/services/apexrest/vlocity_cmt/v2/cpq/carts/{cartId}/promotions?cartId={cartId}&id={promotionId}'
    data = {
        "id": promotionId,
        "cartId": cartId,
        "methodName": "deleteAppliedPromoItems",
        "price": price,
        "validate": validate
    }
    call = restClient.callAPI(action, method='delete', data=data)
    checkError()
    return call

def getCartProducts(cartF, maxProdListHierarchy=None, query=None, filters=None,getCartProducts=None,lastRecordId=None,includeAttachment=None,offsetSize=None,fields=None,pagesize=None,attributes=None,includeAttributes=None,includeIneligible=True,onlyOne=False):
    cartId = utils.Id(cartF)

    products = getCartProducts_api(cartId=cartId, 
                        maxProdListHierarchy=maxProdListHierarchy, 
                        query=query, 
                        filters=filters,
                        getCartProducts=getCartProducts,
                        lastRecordId=lastRecordId,
                        includeAttachment=includeAttachment,
                        offsetSize=offsetSize,
                        fields=fields,
                        pagesize=pagesize,
                        attributes=attributes,
                        includeAttributes=includeAttributes,
                        includeIneligible=includeIneligible)
    if products == None:
        return None
    if onlyOne:
        _products = [product  for product in products if product['Name']['value'] == query]
        if len(_products) == 0:
            return None
        return _products[0]
    return _products

def getCartProducts_api(cartId, maxProdListHierarchy=None, query=None, filters=None,getCartProducts=None,lastRecordId=None,includeAttachment=None,offsetSize=None,fields=None,pagesize=None,attributes=None,includeAttributes=None,includeIneligible=True):
    """
    - cartId:  Cart Id (Salesforce Id).Opportunity, Quote or Order Id. - Required. String
    - maxProdListHierarchy: hierarchy depth returned for list of products. Integer. 
    - lastRecordId: The last record ID from the previous search result, if available. string.
    - query: search string. 
    - includeAttachment: Whether product attachments are returned. boolean
    - filters: Filter field values. string
    - offsetSize: Offset from which to start reading products, for pagination. Integet.
    - fields: List of fields to return in the response, separated by commas. 
    - pagesize: Number of records to be returned. integer.
    - attributes: Attribute filters. 
    - includeAttributes: Specifies whether to return a list of attributes and their values for the product. boolean
    """
    paramStr = stringify(locals(),exclude=['cartId'])

    cartId = utils.Id(cartId)
    action = f'/services/apexrest/vlocity_cmt/v2/cpq/carts/{cartId}/products{paramStr}'

    call = restClient.callAPI(action)

    checkError()
   # if call['messages'][0]['message'] == 'No Results Found.':
   #     return None
    return call['records']

def checkOut_api(cartId,validateSubmittedXLI=True,assetizeFullBundlePerRoot=True,checkOrderStatus=True, provisioningStatus='Active',skipCheckoutValidation=True,waitActivation=False,asyncCall = False):
    cartId = utils.Id(cartId)

    data = {
        "methodName": "checkout",
        "cartId": cartId,
        "ContextId": cartId,
        #     "objectTypeToIdsToClone":"OrderItem:8021N000008NG5t_8021N000008NG5s",
        "validateSubmittedXLI": validateSubmittedXLI,
        "assetizeFullBundlePerRoot": assetizeFullBundlePerRoot,
        "checkOrderStatus": checkOrderStatus,
        "provisioningStatus": provisioningStatus,
        "skipCheckoutValidation": skipCheckoutValidation
    }

    action = f'/services/apexrest/vlocity_cmt/v2/cpq/carts/{cartId}/items/checkout'
    if asyncCall == True:
        action = f'/services/apexrest/AsyncCPQAppHandler/v1/checkout'
    call = restClient.callAPI(
        action,
        method="post",
        data=data)
    checkError()
    logging.info(f'Cart Check-out {cartId}')

    assert(False)
   # if waitActivation == True:
   #   orderUtils.waitforOrderActivation(cartId)
    
    return call

def postCartDiscount():
    print()
