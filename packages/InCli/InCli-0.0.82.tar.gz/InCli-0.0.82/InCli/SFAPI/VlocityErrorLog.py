from . import query,utils
import simplejson,sys 

def get_errors(where=None,limit=None):
    l = f" limit {limit} " if limit!= None else " limit 50 "
    q = f"""select Id,
                    OwnerId,
                    IsDeleted,
                    Name,
                    CreatedDate,
                    CreatedById,
                    LastModifiedDate,
                    SystemModstamp,
                    vlocity_cmt__Action__c,
                    vlocity_cmt__ErrorTime__c,
                    vlocity_cmt__InputData__c,
                    vlocity_cmt__ObjectName__c,
                    vlocity_cmt__SourceName__c,
                    vlocity_cmt__SourceType__c 
                    from vlocity_cmt__VlocityErrorLogEntry__c order by vlocity_cmt__ErrorTime__c desc  {l}"""

    return query.query(q)

def print_error_list(limit=None):
    res = get_errors(limit=limit)
    if len(res['records'])==0: return print(f"There are no records to pring.")

    onwerIds = [r['OwnerId'] for r in res['records']]
    q = "select Name,Id from User where Id in ($$$IN$$$)"
    res2 = query.query(q,in_list=onwerIds)

    for record in res['records']:
        record['ErrorMessage__c'] = _get_record_error_message(record)
        record['vlocity_cmt__ErrorTime__c'] = record['vlocity_cmt__ErrorTime__c'][0:19]
        record['Owner'] = [r['Name'] for r in res2['records'] if r['Id'] == record['OwnerId']][0]

    print(f"Printing {len(res['records'])} records from vlocity_cmt__VlocityErrorLogEntry__c.")
    utils.printFormated(res['records'],"Id:Owner:vlocity_cmt__SourceType__c:vlocity_cmt__SourceName__c:vlocity_cmt__ErrorTime__c:vlocity_cmt__Action__c:ErrorMessage__c",rename="vlocity_cmt__SourceType__c%sourceType:vlocity_cmt__ErrorTime__c%ErrorTime")

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
                if  'result' in input_data['StepResult']:
                    if type(input_data['StepResult']['result']) is dict and 'Error' in input_data['StepResult']['result']:
                        if 'errorCode' in input_data['StepResult']['result']['Error']:
                            error = input_data['StepResult']['result']['Error']
                            return f"ERROR: {error['errorMessage']} - {error['errorCode']} "
                    if 'ActivisErr' in input_data['StepResult']['result']:
                        if input_data['StepResult']['result']['ActivisErr'] != None:
                            try:
                                return f"HttpCode {input_data['StepResult']['result']['ActivisErr']['eDescription']} "
                            except Exception as e:
                                print(e)
                        else:
                            if 'Verbose' in input_data['StepResult']['result']:
                                if 'System' in input_data['StepResult']['result']['Verbose']:
                                    if 'Tibco' in input_data['StepResult']['result']['Verbose']['System']:
                                        if 'eCodes' in input_data['StepResult']['result']['Verbose']['System']['Tibco']:
                                            eCodes = input_data['StepResult']['result']['Verbose']['System']['Tibco']['eCodes']
                                            return f"TIBCO: {eCodes['eDescription']} - {eCodes['eCode']} "
                    if 'HTTPStatusCode' in input_data['StepResult']['result']:
                        error_message  = f"HttpCode {input_data['StepResult']['result']['HTTPStatusCode']} "
                    if 'errors' in input_data['StepResult']['result']:
                        error_message  = str(input_data['StepResult']['result']['errors'])
                    if 'message' in input_data['StepResult']['result']:
                        return input_data['StepResult']['result']['message']
                    if 'eNative' in input_data['StepResult']['result']:
                        if 'eDescription' in input_data['StepResult']['result']['eNative']:
                            return input_data['StepResult']['result']['eNative']['eDescription']
                        else:
                            if type(input_data['StepResult']['result']['eNative']) is list:
                                enative = input_data['StepResult']['result']['eNative'][0]
                                return enative['eDescription']
                    
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

   # utils.printFormated(res['records'],"Id:vlocity_cmt__ErrorTime__c:vlocity_cmt__SourceType__c:vlocity_cmt__SourceName__c:vlocity_cmt__Action__c:ErrorMessage__c",rename="vlocity_cmt__SourceType__c%sourceType:vlocity_cmt__ObjectName__c%ObjectName:vlocity_cmt__ErrorTime__c%time")

def query_and_print_error_record(id,tofile=False):
    q = f"select fields(all) from vlocity_cmt__VlocityErrorLogEntry__c where Id='{id}'"
    records = query.queryRecords(q)

    if len(records)>0:
        record = records[0]
        _print_error_record(record,tofile=tofile)
    else:
        print(f"Record Id {id} not found.")


def _print_error_record(record,print_renames=True,tofile=False):
    record['ErrorMessage__c'] = _get_record_error_message(record)
    record['vlocity_cmt__ErrorTime__c'] = record['vlocity_cmt__ErrorTime__c'][0:19]


    utils.printFormated(record,"Id:vlocity_cmt__ErrorTime__c:vlocity_cmt__SourceType__c:vlocity_cmt__SourceName__c:vlocity_cmt__Action__c:ErrorMessage__c",rename="vlocity_cmt__SourceType__c%sourceType:vlocity_cmt__ObjectName__c%ObjectName:vlocity_cmt__ErrorTime__c%time",print_renames=print_renames)

    filename = record['Id'] if tofile == True else None

    input_data = simplejson.loads(record['vlocity_cmt__InputData__c'])
  #  if 'Request' in input_data:
  #      input_data['Request'] = simplejson.loads(input_data['Request'])

    utils.print_json(input_data,filename=filename)

    return
    input_data = simplejson.loads(record['vlocity_cmt__InputData__c'])
    json_formatted_str = simplejson.dumps(input_data, indent=2, ensure_ascii=False)


def _extract_error(record):
    inputdata_str = record['vlocity_cmt__InputData__c']
    inputdata = simplejson.loads(inputdata_str)

    if 'StepResult' in inputdata:
        if 'ActivisErr' in inputdata['StepResult']:
            return inputdata['StepResult']['result']['ActivisErr']
        
    return ''