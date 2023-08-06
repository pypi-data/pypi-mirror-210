from . import query,utils
import simplejson,sys

def get_errors(where=None,limit=None):
    l = f" limit {limit} " if limit!= None else " limit 50 "
    if where == None: where=''
    q = f"""select Id,
                    OwnerId,
                    IsDeleted,
                    Name,
                    CreatedDate,
                    CreatedById,
                    LastModifiedDate,
                    SystemModstamp,
                    vlocity_cmt__ActionContainerComponent__c,
                    vlocity_cmt__TrackingService__c,
                    vlocity_cmt__VlocityInteractionToken__c,
                    vlocity_cmt__ErrorMessage__c,
                    vlocity_cmt__Timestamp__c,
                    vlocity_cmt__RequestPayload__c,
                    vlocity_cmt__ResponsePayload__c,
                    vlocity_cmt__Data__c,
                    ElementName__c,
                    ElementLabel__c,
                    vlocity_cmt__InstanceIdentifier__c
                    from vlocity_cmt__VlocityTrackingEntry__c {where} {l}"""#order by LastModifiedDate desc  {l}"""

    return query.query(q)

#0057T000000XEEyQAO
#    where = " where LastModifiedDate>2023-03-14T13:30:00.00Z and LastModifiedDate<2023-03-14T13:50:00.00Z order by LastModifiedDate desc"#and vlocity_cmt__ErrorOccurred__c=true "

def print_error_list(limit=None,orderNumber=None):
   # orderNumber = '00303477'
    if orderNumber != None:
        order = query.query(f"select fields(all) from order where OrderNumber='{orderNumber}' limit 1")
        maround = order['records'][0]['CreatedDate'].split('.')[0]
        mfrom,mto = utils.datetimestr_around(maround,minutes=10) 
        userId = order['records'][0]['OwnerId']
        print(f"OrderNum {orderNumber} time {maround}   userId  {userId}")

        where = f" where LastModifiedDate>{mfrom}.00Z and LastModifiedDate<{mto}.00Z order by LastModifiedDate desc"#and vlocity_cmt__ErrorOccurred__c=true "
        limit = 2000
    else:
        where = " order by LastModifiedDate desc"
    res = get_errors(limit=limit,where=where)

    if len(res['records'])==0: return print(f"There are no records to pring.")
    
    onwerIds = [r['CreatedById'] for r in res['records']]
    q = "select Name,Id from User where Id in ($$$IN$$$)"
    res2 = query.query(q,in_list=onwerIds)

    if orderNumber!=None:
        rec2 = {
            'records':[]
        }
        for record in res['records']:
            if userId in record['vlocity_cmt__Data__c']:
        #      print("=====?")
                rec2['records'].append(record)
        res = rec2

    for record in res['records']:
        record['LastModifiedDate'] = record['LastModifiedDate'][0:19]
        if 'vlocity_cmt__ErrorMessage__c' in record and record['vlocity_cmt__ErrorMessage__c'] != None:
            record['Error'] = "Exception"
        record['LastModifiedDate'] = record['LastModifiedDate'][0:19]
        if record['Name'] == 'Integration Procedure': record['Name']="IP"
        if 'vlocity_cmt__Data__c' in record and record['vlocity_cmt__Data__c']!=None:
            try:
                vlocity_cmt__Data__c = simplejson.loads(record['vlocity_cmt__Data__c'])
            except Exception as e:
                a=1
            if 'OmniScriptSubType' in vlocity_cmt__Data__c:
                record['OS'] = vlocity_cmt__Data__c['OmniScriptSubType']
        record['Owner'] = [r['Name'] for r in res2['records'] if r['Id'] == record['OwnerId']][0]


    print(f"Printing {len(res['records'])} records from vlocity_cmt__VlocityTrackingEntry__c.")
    utils.printFormated(res['records'],"Id:Owner:LastModifiedDate:vlocity_cmt__TrackingService__c:vlocity_cmt__InstanceIdentifier__c:OS:ElementName__c:Name:ElementLabel__c:Error",rename="LastModifiedDate%Time:vlocity_cmt__TrackingService__c%Service:vlocity_cmt__InstanceIdentifier__c%Identifier")

def _get_record_error_message(record):
    input_data = simplejson.loads(record['vlocity_cmt__InputData__c'])

    error_message = 'Other'

    if record['vlocity_cmt__SourceType__c'] == 'Odin':
        error_message = input_data['ErrorMessage__c'][0:70]

    elif record['vlocity_cmt__SourceType__c'] == 'Integration Procedure':
        if  'ErrorMessage'  in input_data:
            if 'ErrorCode' in input_data:
                error_message  = f"{input_data['ErrorCode']} {input_data['ErrorMessage']} "
            else:
                error_message  = f"{input_data['ErrorMessage']} "

        elif 'GenericLogMessage' in input_data:
            error_message = input_data['GenericLogMessage'][0:70]
        else: 
            if 'StepResult' in input_data:
                if 'result' in input_data['StepResult']:
                    if 'HTTPStatusCode' in input_data['StepResult']['result']:
                        error_message  = f"HttpCode {input_data['StepResult']['result']['HTTPStatusCode']} "
                    if 'errors' in input_data['StepResult']['result']:
                        error_message  = str(input_data['StepResult']['result']['errors'])

                if 'info' in input_data['StepResult']:
                    if 'status' in input_data['StepResult']['info']:
                        error_message  = f"{input_data['StepResult']['info']['status']} {input_data['StepResult']['info']['statusCode']}"
                if 'error' in input_data['StepResult']:
                        error_message  = f"{input_data['StepResult']['error']}"
    return error_message

def print_error_records(last=None):
    limit = last if last!=None else 50
    res = get_errors(limit=limit)

    for record in res['records']:
        record['vlocity_cmt__ErrorTime__c'] = record['vlocity_cmt__ErrorTime__c'][0:19]
        record['ErrorMessage__c'] = _get_record_error_message(record)

        _print_error_record(record,print_renames=False)
        print()
        print()

def query_and_print_error_record(id,tofile=False):
    q = f"select fields(all) from vlocity_cmt__VlocityTrackingEntry__c where Id='{id}'"
    records = query.queryRecords(q)

    if len(records)>0:
        record = records[0]
        _print_error_record(record,tofile=tofile)
    else:
        print(f"Record Id {id} not found.")

def _print_error_record(record,print_renames=True,tofile=False):
  #  record['ErrorMessage__c'] = _get_record_error_message(record)
    record['LastModifiedDate'] = record['LastModifiedDate'][0:19]

    utils.printFormated(record,"Id:vlocity_cmt__ErrorTime__c:vlocity_cmt__SourceType__c:vlocity_cmt__SourceName__c:vlocity_cmt__Action__c:ErrorMessage__c",rename="vlocity_cmt__SourceType__c%sourceType:vlocity_cmt__ObjectName__c%ObjectName:vlocity_cmt__ErrorTime__c%time",print_renames=print_renames)

    for key in list(record.keys()):
        if record[key] == None:
            record.pop(key)

    if 'vlocity_cmt__ErrorMessage__c' in record:
        record['vlocity_cmt__ErrorMessage__c'] = simplejson.loads(str(record['vlocity_cmt__ErrorMessage__c']))
        exception = record['vlocity_cmt__ErrorMessage__c']['Exception']
        if 'Description' in exception:
            exception['Description'] = simplejson.loads(exception['Description'])
   
    if 'vlocity_cmt__RequestPayload__c' in record:
        record['vlocity_cmt__RequestPayload__c'] = simplejson.loads(record['vlocity_cmt__RequestPayload__c'])

    if 'vlocity_cmt__ResponsePayload__c' in record:
        record['vlocity_cmt__ResponsePayload__c'] = simplejson.loads(record['vlocity_cmt__ResponsePayload__c'])

    if 'vlocity_cmt__Data__c' in record:
        record['vlocity_cmt__Data__c'] = simplejson.loads(record['vlocity_cmt__Data__c'])

    filename = record['Id'] if tofile == True else None
    utils.print_json(record,filename=filename)

    return

