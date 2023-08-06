from . import Sobjects,utils,restClient,query
import logging

#if the account does not exist, accountX will be used as the account name. 
def getId(accountF):
    """Returns the account Id provided the accountF -> fieldname:fielvalue."""
    Id = Sobjects.IdF('Account',accountF,init='001')
    return Id

def create_Id(accountName,fields=None,recordTypeName=None,checkExists=True):
    """Creates an account
    - accountName - name for the account
    - fields - fields to be set in the account
    - recordType - String with record Type name
    - checkExists - will query if there is an account with the provided accountF - fieldname - The many accounts with the same name, one is returned.
    - returns the accountId
    """
    if checkExists == True:
        accountId = getId(f"Name:{accountName}")

        if accountId != None:
            restClient.glog().info(f'Returning existing Account <{accountId}> ')
            return accountId
            
    acc={
        'Name': accountName,
        'vlocity_cmt__Active__c':'Yes',
        'vlocity_cmt__Status__c':'Active'
    }
    if fields!= None:
        acc.update(fields)

    if recordTypeName!=None:
        acc['RecordTypeId'] = query.queryField(f"select Id from RecordType where SobjectType='Account' and Name = '{recordTypeName}'")

    call = Sobjects.create('Account',acc)

    accountId = call['id']
    restClient.glog().info(f"Account {accountName} Created Account <{accountId}> ")

    return accountId

def create(accountName,fields=None,recordTypeName=None,checkExists=True):
    """Creates an account
    - accountName - name for the account
    - fields - fields to be set in the account
    - recordType - String with record Type name
    - checkExists - will query if there is an account with the provided accountF - fieldname - The many accounts with the same name, one is returned.
    - returns the new account object
    """
    accountId = create_Id(accountName,fields=fields,recordTypeName=recordTypeName,checkExists=checkExists)
    account = Sobjects.get(accountId)

    return account['records'][0]

def get(accountF,multiple=False):
    """
    - multiple - returns an array of accounts (limit 200), else return one account
    - in both cases if no account, returns None
    """
    ef = utils.extendedField(accountF)
    call =  query.query(f" select fields(all) from Account where {ef['field']}='{ef['value']}' limit 200")
    if len(call['records']) == 0:
        return None
    if multiple:
        return call['records']
    return call['records'][0]

def delete(accountF):
    """deletes one account. if multiple match only one is deleted"""
    id = getId(accountF)
    call = Sobjects.delete('Account',id)
    restClient.glog().info(f"Account {accountF} deleted.")
    return call

def getOrdersId(accountF):
    """Returns the orders for the account as a List of Ids
    - if no orders for the account, and empty list is returned."""
    accountId = getId(accountF)
    ids = query.queryFieldList(f" select Id from Order where  AccountId = '{accountId}' ")
    return ids

def deleteOrders(accountF):
    """deletes all the orders for the account. if multiple accounts only the orders for one are deleted"""
    ids = getOrdersId(accountF)
    if ids == [] or ids == None:
        restClient.glog().info(f"Account {accountF} has no orders to delete.")
        return None
    call = Sobjects.delete('Order',ids)
    restClient.glog().info(f"Account {accountF} Orders {ids} deleted.")

    return call
