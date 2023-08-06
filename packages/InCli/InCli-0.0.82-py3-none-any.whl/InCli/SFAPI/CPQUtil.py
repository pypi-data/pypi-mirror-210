from . import restClient,CPQ,account,timeStats,objectUtil,utils

def create_cart_with_promotion(cartName,accountName,pricelistName,promoName,ts:timeStats=None):
    cartId = CPQ.getCartId(f"name:{cartName}")
    if cartId != None:
        CPQ.deleteCart(cartId)

    accountId = account.createAccount_Id(f'Name:{accountName}',recordTypeName='Consumer')
    cartId = CPQ.createCart(accountF= accountId, pricelistF=f'Name:{pricelistName}',name=cartName,checkExists=True)
    if ts!=None: ts.time('createCart')

    promo = CPQ.getCartPromotions(cartId,query=promoName,onlyOne=True)

    res = CPQ.postCartsPromoItems_api(cartId,promo['Id'])
    print(restClient.getLastCallElapsedTime())

    all = CPQ.getCartItems_api(cartId,fields='vlocity_cmt__ServiceAccountId__c,vlocity_cmt__BillingAccountId__c',price=False,validate=False,includeAttachment=False)
    print(restClient.getLastCallElapsedTime())

def post_cart_item(cartId,items,productCode,itemType='childProduct',path=None,noResponseNeeded=False,price=False,validate=False):
    obj,parents = get_ol(items,productCode)
    if obj == None: utils.raiseException('Item not found',f"{itemType} with product code {productCode} cannot be found")

    item = obj
    position = len(parents) - 2
    parentRecord = parents[position]

    if path == None: path = productCode

    priceBookEntryId = item['Id']['value']
    parentId = parentRecord['parentLineItemId'] if 'parentLineItemId' in parentRecord else parentRecord['Id']['value']
    parentHierarchyPath = parentRecord['productHierarchyPath']

    parentRecord2 = {}
    parentRecord2['Id'] = parentRecord['Id']['value']
    parentRecord2['productId'] = parentRecord['productId']
    parentRecord2['productHierarchyPath'] = parentRecord['productHierarchyPath']
    parentRecord2['itemType'] = parentRecord['itemType']
    parentRecord2['parentLineItemId'] = parentId #parentRecord['parentLineItemId']

    call = CPQ.addItemstoCart_api(cartId,priceBookEntryId,parentRecord=parentRecord,parentId=parentId,parentHierarchyPath=parentHierarchyPath,noResponseNeeded=noResponseNeeded,price=price,validate=validate)

    return call

def update_field(cartId,items,productCode,updateDic=None,attributesDic=None,price=False,validate=False):
    item,parents = get_ol(items,productCode)
    if item == None: utils.raiseException('Item not found',f"With product code {productCode} cannot be found")

    obj = {}
    obj['vlocity_cmt__LineNumber__c'] = item['vlocity_cmt__LineNumber__c']
    obj['vlocity_cmt__RootItemId__c'] = item['vlocity_cmt__RootItemId__c']
    obj['vlocity_cmt__Action__c'] = item['vlocity_cmt__Action__c']
    obj['vlocity_cmt__AssetReferenceId__c'] = item['vlocity_cmt__AssetReferenceId__c']
    obj['Id'] = item['Id']

    if updateDic != None:
        obj.update(updateDic)
        
    if attributesDic != None:
        obj['attributeCategories'] = item['attributeCategories']
        for key in attributesDic.keys():
            att = objectUtil.getSibling(obj,'code',key)
            att['userValues']=attributesDic[key]

    items = {"records":[obj]}
    call = CPQ.updateCartItem_api(cartId,items,price=price,validate=validate)
    return call

def delete_cart_item(cartId,items,productCode,price=False,validate=False):
    obj,parents = get_ol(items,productCode,itemType='lineItem')
    if obj == None: utils.raiseException('Item not found',f" with product code {productCode} cannot be found")

    item = obj
    itemIds = item['Id']['value']

    if len(parents) > 2:
        position = len(parents) - 2
        parentRecord = parents[position]

        parentRecord2 = {}
        parentRecord2['Id'] = parentRecord['Id']['value']
        parentRecord2['productId'] = parentRecord['productId']
        parentRecord2['productHierarchyPath'] = parentRecord['productHierarchyPath']
        parentRecord2['itemType'] = parentRecord['itemType']
        parentRecord2['parentLineItemId'] = parentRecord['parentLineItemId'] if 'parentLineItemId' in parentRecord else parentRecord['Id']['value']

    else:
        parentRecord2 = None # is a root item

    call = CPQ.deleteCartItems_api(cartId,itemIds=[itemIds],parentRecord=parentRecord2,price=price,validate=validate) 

    return call

def create_cart_with_offer(accountname,cartName,offerName,create=False,pricelistF='Name:B2C Price List',price=False,validate=False,timeStats=None):

    cartId = CPQ.getCartId(f"name:{cartName}")
    if cartId != None:
        if create == True:
            CPQ.deleteCart(cartId)

 #   accountF = f'Name:{accountname}'
 #   accountId = account.create_Id(accountname,recordTypeName='Consumer')
    accountId = account.create_Id(accountname)

    inputFields = {
        'NOS_t_CoverageTechnology__c':'FTTH'
    }

    inputFields = None
    cartId = CPQ.createCart(accountF= accountId, pricelistF=pricelistF,name=cartName,checkExists=True,inputFields=inputFields)
    if timeStats != None:  timeStats.time('createCart')

    return add_offer_to_cart(cartId,offerName,pricelistF,price,validate)

def add_offer_to_cart(cartId,offerName,pricelistF='Name:B2C Price List',price=False,validate=False,timeStats=None):
    offer = CPQ.getCartProducts(cartId,query=offerName,onlyOne=True)
    if timeStats != None:  
        timeStats.field('product',offerName)
        timeStats.time('getCartProducts')

    items = CPQ.addItemstoCart(cartId,productCode=offer['ProductCode']['value'],pricelistF=pricelistF,price=price,validate=validate)

    counters = cart_stats(items)
    if timeStats != None:  timeStats.time('addItemstoCart',extend_obj=counters)

    return cartId,items

def create_cart_with_promo(accountname,cartName,promoName,create=False,pricelistF='Name:B2C Price List',price=False,validate=False,timeStats=None,inputFields=None):

    cartId = CPQ.getCartId(f"name:{cartName}")
    if cartId != None:
        if create == True:
            CPQ.deleteCart(cartId)

    accountId = account.create_Id(accountname,recordTypeName='Consumer')
    cartId = CPQ.createCart(accountF= accountId, pricelistF=pricelistF,name=cartName,checkExists=True,inputFields=inputFields)
    if timeStats != None:  timeStats.time('createCart')

    promo = CPQ.getCartPromotions(cartId,query=promoName,onlyOne=True)
    if timeStats != None:  timeStats.time('getCartPromotions')

    if promo == None:
        utils.raiseException('NO_PROMO',f"promo with name {promoName} cannot be found.")

    print(f'Adding promo to cart {promoName}')
    res = CPQ.postCartsPromoItems_api(cartId,promo['Id'],price=price,validate=validate)
    if timeStats != None:  
        timeStats.field('product',promoName)
        timeStats.time('postCartsPromoItems')

    return cartId,res['actions']['rootitemadded']['client']

def _contextLineItemIds(obj,ids=[]):
    if 'lineItems' in obj:
        for li in obj['lineItems']['records']:
            ids.append(li['Id']['value'])
            _contextLineItemIds(li,ids)
    if 'productGroups' in obj:
        for pg in obj['productGroups']['records']:
            _contextLineItemIds(pg,ids)

def post_promo_item(cartId,items,productCode,promotionName,price=True,validate=True):
    obj,parents = get_ol(items,productCode)
    if obj == None: utils.raiseException('Item not found',f" with product code {productCode} cannot be found")

    contextLineItemIds = []
    _contextLineItemIds(obj,contextLineItemIds)

    contextLineItemIds.append(obj['Id']['value'])

    done = False
    position = len(parents) - 2
    while done == False:
        parentRecord = parents[position]
        if 'promotions' not in parentRecord:
            position = position - 2
        else:
            done = True

    promotionId = None
    for promo in parentRecord['promotions']['records']:
        if promo['Name'] == promotionName:
            promotionId = promo['Id']

    call = CPQ.postCartsPromoItems_api(cartId, promotionId,price=price,validate=validate,contextLineItemIds=contextLineItemIds)

    return call

def clone_lineItem(cartId,items,path,price=False,validate=False):
    obj,parents = get_ol(items,path,itemType='lineItem')
    if obj == None: utils.raiseException('Item not found',f"Cannot Clone. Item not found {path} ")

    itemId = obj['Id']['value']

    call = CPQ.clone_item_api(cartId,itemId,price=price,validate=validate)

    return call

def cart_stats(items):
    def _add_to_counter(counters,field,value=1):
        if field not in counters: counters[field] = 0
        counters[field] = counters[field] + value

    def _parse_order_line(ol,counters):
        _add_to_counter(counters,ol['itemType'])
        if 'action' in ol: 
            _add_to_counter(counters,ol['action'])

        if 'attributeCategories' in ol:
            for ar in ol['attributeCategories']['records']:
                _add_to_counter(counters,f"{ol['itemType']}_att",ar['productAttributes']['totalSize'])
            
        ol_types = ['lineItems','childProducts','productGroups']

        for ol_type in ol_types:
            if ol_type in ol:
                for r in ol[ol_type]['records']:
                    _parse_order_line(r,counters)
    
    counters = {} 
    if 'records' not in items: return counters  #cart is empty
    for r in items['records']:
        _parse_order_line(r,counters)

    return counters

def get_ol(items,path,itemType=None):
    """Returns the object and the parents."""

    onlyOne=False

    siblings = objectUtil.getSiblingWhere_path(items,selectKey='ProductCode',selectKeyValuePath=path,whereKey='itemType',whereValue=itemType)

    if siblings == None: return None, None
    return siblings['object'],siblings['objects']
    print()

