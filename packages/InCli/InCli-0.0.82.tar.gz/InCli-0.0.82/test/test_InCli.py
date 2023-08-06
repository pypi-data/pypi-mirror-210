from InCli.SFAPI import utils,query,restClient,file
import sys, os
#python3 -m unittest

import unittest
from InCli import InCli
#from InCli.SFAPI import restClient
import traceback,time

#/Users/uormaechea/Documents/Dev/python/InCliLib/InCLipkg
# python3 -m build
#python3 -m twine upload --repository pypi dist/InCli-0.0.29*

class Test_Main(unittest.TestCase):

    def test_q(self):
        try:
            InCli._main(["-u","NOSDEV","-q", "select fields(all) from Order limit 1"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_q_System(self):
        try:
            InCli._main(["-u","NOSDEV","-q", "select fields(all) from Order limit 1","-system"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)
    def test_q_nulls(self):
        try:
            InCli._main(["-u","NOSDEV","-q", "select fields(all) from Order limit 1","-null"])       
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2) 
    def test_q_all(self):
        try:
            InCli._main(["-u","NOSDEV","-q", "select fields(all) from Order limit 1","-all"])   
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)
    def test_q_fields_all(self):
        try:
            InCli._main(["-u","NOSDEV","-q", "select fields(all) from Order limit 10","-fields","AccountId"])  
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)
    def test_q_fields_all(self):
        try:
            InCli._main(["-u","NOSDEV","-q", "select AccountId,Pricebook2Id,OrderNumber,TotalContractCost__c,State__c from Order limit 50","-fields","all"])  
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)
  
    def test_q_complexfields_all(self):
        try:
            InCli._main(["-u","NOSDEV","-q", "select Id,vlocity_cmt__BillingAccountId__c,vlocity_cmt__LineNumber__c,vlocity_cmt__ServiceAccountId__c,vlocity_cmt__Product2Id__r.productCode from orderitem where OrderId='8013O000003ivMKQAY' order by vlocity_cmt__LineNumber__c","-fields","all"])  
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

  
    def test_o(self):
        try:
            InCli._main(["-u","uormaechea.devnoscat2@nos.pt","-o"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_o_name(self):
        try:
            InCli._main(["-u","uormaechea.devnoscat4@nos.pt","-o","-name","order"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)
    def test_o_name_limit(self):
        try:
            InCli._main(["-u","uormaechea.devnoscat4@nos.pt","-o","-name","order","-limit","10"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)
    def test_o_like(self):
        try:
            InCli._main(["-u","uormaechea.devnoscat2@nos.pt","-o","-like","XOM"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_h(self):
        try:
            InCli._main(["-h"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_hu(self):
        try:
            InCli._main(["-hu"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_cc(self):
        try:
            InCli._main(["-u","DEVNOSCAT4","-cc"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_cc_no_u(self):
        try:
            InCli._main(["-cc"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)


    def test_cc_basket(self):
        try:
            InCli._main(["-u","NOSQSM","-cc","-basket"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_cc_list(self):
        try:
            InCli._main(["-u","NOSDEV","-cc","-list"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_cc_code(self):
        try:
            InCli._main(["-u","NOSDEV","-cc","-code","DC_CAT_DEEPLINK"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_cc_account(self):
        try:
            InCli._main(["-u","NOSDEV","-cc","-account","name:unaiTest4","-code","DC_CAT_MPO_CHILD_003"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_logs(self):
        try:
            InCli._main(["-u","NOSDEV","-logs"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_logs_where(self):
        try:
            InCli._main(["-u","NOSDEV","-logs","-where","adaasdasd='asasd'"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_logs_store(self):
        try:
            InCli._main(["-logs","-store"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_logs_store_id(self):
        try:
            InCli._main(["-logs","-store","07L0Q00000N7AHsUAN"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_logs_store_error(self):
        try:
            InCli._main(["-u","NOSDEV","-logs","-store","-error"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_logs_user_ELK(self):
        try:
            res = InCli._main(["-u","NOSDEV","-logs","-tail","-loguser","InCli","-deletelogs"])
            print()
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_logs_user(self):
        try:
            res = InCli._main(["-u","NOSDEV","-logs","-loguser","Alias:ana.r"])
            print()
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_logs_query(self):
        try:
            res = InCli._main(["-u","NOSDEV","-logs","-where","Operation='Batch Apex'","-last","10"])
            print()
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_logs_userDefault_loguser(self):
        try:
            InCli._main(["-default:set","loguser","Alias:ana.r"])
            InCli._main(["-u","NOSDEV","-logs"])
            InCli._main(["-default:del","loguser"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_logs_userWrong(self):
        try:
            res = InCli._main(["-u","NOSDEV","-logs","-loguser","username:uormaechea_nosdev@nos.pt"])
        except Exception as e:
            print(e.args[0]['error'])
            self.assertTrue(e.args[0]['error']=='User with field Alias:xxxx does not exist in the User Object.')
            utils.printException(e)

    def test_logs_limit(self):
        try:
            res = InCli._main(["-u","NOSDEV","-logs","-limit","2"])
            self.assertTrue(len(res)==2)
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_logs(self):
        try:
            res = InCli._main(["-u","DTI","-logs"])
            if len(res)>0:
                self.assertTrue(res[0]['Id']!=None)
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)
   
    def test_logs_level(self):
        try:
            res = InCli._main(["-u","NOSDEV","-logs","07L3O00000DjhX1UAJ","-level","1"])
            print()
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_log_ID_2(self):
        try:
            id = '07L3O00000Dic7oUAB'
           # id = '07L7a00000TOMLDEA5'
            env = 'NOSDEV'
            #id = None

            if id == None:
                restClient.init(env)
                id = query.queryField("Select Id FROM ApexLog order by StartTime desc limit 1")
            InCli._main(["-u",env,"-logs",id])

        except Exception as e:
            print(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_log_limitinfo(self):
        try:
           # id = '07L3O00000Dh69HUAR'
            id = None

            if id == None:
                restClient.init('NOSDEV')
                id = query.queryField("Select Id FROM ApexLog order by StartTime desc limit 1")
            InCli._main(["-u","NOSDEV","-logs",id])
            InCli._main(["-u","NOSDEV","-logs",id,"-limitinfo"])

        except Exception as e:
            print(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)
    def test_log_IDflow(self): #flow
        try:
            InCli._main(["-u","NOSDEV","-logs","-inputfile","/Users/uormaechea/Documents/Dev/python/InCliLib/InCLipkg/test/files/flowAndWF.log"])
        except Exception as e:
            print(e)
            print(traceback.format_exc())

#07L3O00000Dy7SAUAZ
    def test_log_ID(self):
        try:
            InCli._main(["-u","DEVNOSCAT4","-logs","07L3O00000E7b0YUAR"])
        except Exception as e:
            print(e)
            print(traceback.format_exc())

    def test_log_ID_wrong(self):
        try:
            InCli._main(["-u","DEVNOSCAT4","-logs","xxx"])
        except Exception as e:
            print(e)
            print(traceback.format_exc())

    def test_log_ID_limitsInfo(self):
        try:
            InCli._main(["-u","NOSDEV","-logs","07L3O00000DxlaLUAR","-limitinfo"])
        except Exception as e:
            print(e)
            print(traceback.format_exc())
    def test_log_ID_to_file(self):
        try:
            InCli._main(["-u","DTI","-logs","07L0Q00000N5yVKUAZ","-file"])
        except Exception as e:
            print(e)
            print(traceback.format_exc())

    def test_log_folder(self):
        try:
            res = InCli._main(["-logs","-folder",f"/Users/uormaechea/Documents/Dev/python/InCliLib/InCLipkg/InCli/logs1"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_log_folder_Id(self):
        try:
            res = InCli._main(["-logs","-folder",f"/Users/uormaechea/Downloads/logs_SF"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    
    def test_log_file(self):
        try:
            res = InCli._main(["-logs","-inputfile",f"/Users/uormaechea/Documents/Dev/python/InCliLib/InCLipkg/incli/logs/07L3O00000EmvvzUAB.log"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_log_file_allLimits(self):
        try:
            res = InCli._main(["-logs","-inputfile",f"/Users/uormaechea/Documents/Dev/python/InCliLib/InCLipkg/incli/logs/07L3O00000EmvvzUAB.log","-allLimits"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_log_file_to_file(self):
        try:
            res = InCli._main(["-logs","-inputfile",f"/Users/uormaechea/Documents/Dev/python/InCliLib/InCLipkg/incli/logs/07L3O00000EmvvzUAB.log","-file"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_log_file_id(self):
        try:
            id = '07L0Q00000N5yVKUAZ'
            res = InCli._main(["-logs","-inputfile",f"/Users/uormaechea/Documents/Dev/python/InCliLib/InCLipkg/.InCli/logs/{id}.log"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_log_file_set_id(self):
        try:
            id = '07L3O00000DwvxvUAB'
            res = InCli._main(["-u","NOSDEV","-logs","-inputfile",f"/Users/uormaechea/Documents/Dev/python/InCliLib/InCLipkg/.InCli/logs/{id}.log"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_log_file_test_folder(self):
        try:
            id = '07L3O00000EBQ6MUAX'
            res = InCli._main(["-u","NOSDEV","-logs","-inputfile",f"/Users/uormaechea/Documents/Dev/python/InCliLib/InCLipkg/InCli/logs/{id}.log"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_log_file_to_file(self):
        try:
            if 1==2:
                restClient.init('DTI')
                html_name = f"{restClient.logFolder()}07L3O00000Dgt4sUAB.html"
                txt_name = f"{restClient.logFolder()}07L3O00000Dgt4sUAB.html"

                if file.exists(html_name):
                    file.delete(html_name)
                if file.exists(txt_name):
                    file.delete(txt_name)
                self.assertTrue(file.exists(html_name)==False)
            res = InCli._main(["-u","NOSDEV","-logs","-inputfile",f"/Users/uormaechea/Documents/Dev/python/InCliLib/InCLipkg/InCli/logs/07L3O00000ETNTKUA5.log","-file"])
            self.assertTrue(file.exists(html_name)==True)
            self.assertTrue(file.exists(txt_name)==True)

            html = file.read(f"{restClient.logFolder()}07L3O00000Dgt4sUAB.html")
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_log_file_2(self):
        try:
            InCli._main(["-u","NOSDEV","-logs","-inputfile",f"/Users/uormaechea/Documents/Dev/python/InCliLib/InCLipkg/test/files/07L3O00000DgwlbUAB.log"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_log_file_exception_wf(self):
        try:
            res = InCli._main(["-u","NOSDEV","-logs","-inputfile",f"/Users/uormaechea/Documents/Dev/python/InCliLib/InCLipkg/test/files/ExceptionThrown.log"])
            self.assertTrue(res['exception']==True)
            last = res['debugList'][-1]
            self.assertTrue(last['cmtSOQLQueries'][0] == '43')
            self.assertTrue(last['CPUTime'][0] == '13363')
            self.assertTrue(res['file_exception']==True)
            
            print()
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_log_last(self):
        try:
            InCli._main(["-u","NOSDEV","-logs","-last","100"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_log_tail_loguser_guest_auto_delete(self):
        try:
            InCli._main(["-u","demo240","-logs","-tail","-auto","-deletelogs"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_log_last_loguser(self):
        try:
            InCli._main(["-u","NOSQSM","-logs","-last","2","-loguser","username:uormaechea@nos.pt"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_log_tail_auto_loguser_new(self):
        try:
            InCli._main(["-u","NOSDEV","-logs","-tail","-auto","-loguser","username:pvg@optimus.force.com.nosdev"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_log_tail_auto(self):
        try:
            #return
            InCli._main(["-u","devupg2","-logs","-tail","-auto"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)  

    def test_log_tail_auto_delete(self):
        try:
            #return
            InCli._main(["-u","NOSDEV","-logs","-tail","-auto","-deletelogs","-debuglevel","M"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)  

    def test_log_tail(self):
        try:
            #return
            InCli._main(["-u","DEVNOSCAT4","-logs","-tail"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)   
    def test_log_tail_delete_guest(self):
        try:
            #return
            InCli._main(["-u","NOSQSM","-logs","-tail","-deletelogs"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)     

    def test_log_tail_delete(self):
        try:
            #return
            InCli._main(["-u","DEVNOSCAT4","-logs","-tail","-deletelogs"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)     

    def test_log_tail_delete_noScreen(self):
        try:
            #return
            InCli._main(["-u","DEVNOSCAT4","-logs","-tail","-deletelogs","-noScreen"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)    

    def test_log_tail_where(self):
        try:
            return

            InCli._main(["-u","NOSDEV","-logs","-tail","-where","LogLength>3000"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)    
    def test_log_tailx(self):
        try:
            restClient.init('NOSDEV')
            logRecords = query.queryRecords("Select fields(all) FROM ApexLog order by StartTime desc limit 1")
            time = logRecords[0]['StartTime']
            timez = time.split('.')[0] + "Z"
            while (True):
                logRecords = query.queryRecords(f"Select Id,LogUserId,LogLength,LastModifiedDate,Request,Operation,Application,Status,DurationMilliseconds,StartTime,Location,RequestIdentifier FROM ApexLog where StartTime > {timez} order by StartTime asc ")

                if len(logRecords) > 0:
                    print()
                    for record in logRecords:
                        print(f"{record['StartTime']}  {record['Operation']}")
                        time = record['StartTime']
                        timez = time.split('.')[0] + "Z"
                        
                time.sleep(5)
            print()

          #  InCli._main(["-u","NOSDEV","-logs","-last","10"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_default(self):
        try:
            InCli._main(["-default:set","u"])
            InCli._main(["-default:set","u","NOSDEV"])
            InCli._main(["-default:get","u"])        
            res = InCli._main(["-logs","-last","1"])
            InCli._main(["-default:del","u"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_default_get(self):
        try:
            InCli._main(["-default:get"])        
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_default_weird(self):
        try:
            InCli._main(["-h:","InCli","-default:set","u","NOSDEV"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_d(self):
        try:
            InCli._main(["-u","NOSDEV","-d"])
            InCli._main(["-u","NOSDEV","-d","Order"])
            InCli._main(["-u","NOSDEV","-d","Order:Status"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_l(self):
        try:
            InCli._main(["-u","NOSPRD","-l"])
            InCli._main(["-u","DEVNOSCAT2","-l"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_l_no_U(self):
        try:
            InCli._main(["-l"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_checkVersion(self):
        InCli.checkVersion()
        print()

    def test_ipe(self):
        try:
            InCli._main(["-u","NOSPRD","-ipe"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_ipe_id(self):
        try:
            InCli._main(["-u","NOSPRD","-ipe","a6K7T000001dk4PUAQ"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_ipe_id_tofile(self):
        try:
            InCli._main(["-u","NOSDEV","-ipe","a6K3O000000FJ5WUAW","-file"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)
    def test_ipe_last(self):
        try:
            InCli._main(["-u","NOSPRD","-ipe","-last","100"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_ipa(self):
        try:
            InCli._main(["-u","NOSPRD","-ipa"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_ipa_dates(self):
        try:
            InCli._main(["-u","NOSPRD","-ipa","-from","2023-03-09T09:19:31","-to","2023-03-11T13:55:00"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_ipa_around(self):
        try:
            InCli._main(["-u","NOSPRD","-ipa","-around","2023-03-28T16:25:00"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_ipa_contains(self):
        try:
            InCli._main(["-u","NOSPRD","-ipa","-around","2023-03-14T11:24:07","-contains","a3l7T000001RbofQAC,Marco"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)          

    def test_ipa_limit(self):
        try:
            InCli._main(["-u","NOSPRD","-ipa","-limit","25"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_ipa_orderNumber(self):
        try:
            InCli._main(["-u","NOSPRD","-ipa","-orderNumber","00300083"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_ipa_id(self):
        try:
            InCli._main(["-u","NOSPRD","-ipa","a6a7T000002RNtlQAG"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_ipa_id_toFile(self):
        try:
            InCli._main(["-u","NOSQSM","-ipa","a2J7a000002UakuEAC","-file"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_vte(self):
        try:
            InCli._main(["-u","NOSDEV","-vte"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_vte_id(self):
        try:
            InCli._main(["-u","NOSDEV","-vte","a6a3O000000FFkYQAW"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_vte_id_file(self):
        try:
            InCli._main(["-u","NOSDEV","-vte","a6a3O000000FFkYQAW","-file"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_vte_wrong_command(self):
        try:
            InCli._main(["-u","NOSDEV","-xxx","a6a3O000000FFkYQAW","-file"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)

    def test_vte_wrong_modifier(self):
        try:
            InCli._main(["-u","NOSDEV","-logs","a6a3O000000FFkYQAW","-dellogs"])
        except Exception as e:
            utils.printException(e)
            print(traceback.format_exc())
            self.assertTrue(1==2)