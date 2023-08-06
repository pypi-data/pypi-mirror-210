import unittest
from InCli import InCli
from InCli.SFAPI import file,restClient,tooling,Sobjects,utils,traceFlag,query

class Test_TraceFlag(unittest.TestCase):
    def test_set_InCli_for_user(self):
        restClient.init('NOSDEV')

     #   userId = Sobjects.IdF('User','username:uormaechea_nosdev@nos.pt')
        userF='username:pvg@optimus.force.com.nosdev'
        InCli_trace_flags = traceFlag.get_InCli_traceflags_for_user(userF)

        if InCli_trace_flags == None:
            InCli_trace_flags = traceFlag.create_trace_flag_incli_f(userF)

        InCli_trace_flags = traceFlag.get_InCli_traceflags_for_user(userF)

        InCli_trace_flags = traceFlag.update_trace_flag_incli(InCli_trace_flags['Id'])

        traceFlag.delete_trace_Flag(InCli_trace_flags['Id'])

        print()

    def test_create_debug_level(self):
        restClient.init('DTI')
        traceFlag.create_debug_level_incli()

    def test_set_incli_traceFlag_for_user(self):
        restClient.init('DTI')

        userF = "username:onboarding@nosdti-parceiros.cs109.force.com"
        traceFlag.set_incli_traceFlag_for_user(userF)

    def test_debuglevel_get(self):
        restClient.init('NOSDEV')

        call = tooling.tooling_IdF('DebugLevel',"DeveloperName:XXXX")   
        self.assertTrue(call==None)

        id = tooling.tooling_IdF('DebugLevel',"DeveloperName:InCli")   
        if id != None:
            tooling.tooling_delete('DebugLevel',id)
            id = tooling.tooling_IdF('DebugLevel',"DeveloperName:InCli")   

            print()
        if id == None:
            tooling.create_debug_level_incli()
            print()


    def test_query_using_incli(self):
        restClient.init('NOSDEV')
        debuglevel_ids = traceFlag.get_InCli_debuglevelIds()
        user_ids = traceFlag.get_InCli_usersIds(debuglevel_ids)

        
        q1 = f"select username from User where Id in ({query.IN_clause(user_ids)})"
        res1 = query.query(q1)
        print()

    def test_query_who(self):

        envs = ['DTI',"NOSDEV","NOSQSM","NOSPRD"]
        for env in envs:
            try:
                restClient.init(env)

                DebugLevelId = tooling.IdF('DebugLevel',"DeveloperName:InCli")   
                q = f"select TracedEntityId,StartDate,ExpirationDate from TraceFlag where DebugLevelId='{DebugLevelId}' limit 100"

                res =tooling.query(q)
                q1 = f"select username from User where Id='{res['records'][0]['TracedEntityId']}'"
                res1 = query.query(q1)
                print()
                print(f'Environment: {env}')
                utils.printFormated(res1['records'])
            except Exception as e:
                utils.printException(e)

        print()

    def test_completions(self):
        restClient.init('NOSDEV')
        tooling.completions()

    def test_aync(self):
        restClient.init('DEVNOSCAT4')
        tooling.executeAnonymous()

    def test_aync_EPCProductAttribJSONBatchJob(self):
        restClient.init('DEVNOSCAT2')
        code = """
        List<Id> productIds = new List<Id>();
        for (Product2 prod : [ Select Id from Product2 where vlocity_cmt__ObjectTypeId__c!= null ]) {
            productIds.add(prod.Id);}
        Database.executeBatch(new vlocity_cmt.EPCProductAttribJSONBatchJob(productIds), 1);
        """
        tooling.executeAnonymous(code)

    def test_aync_EPCFixCompiledAttributeOverrideBatchJob(self):
        restClient.init('DEVNOSCAT2')
        code = """
        Database.executeBatch(new vlocity_cmt.EPCFixCompiledAttributeOverrideBatchJob (), 1);
        """
        tooling.executeAnonymous(code)

    def test_limitUsageHistory(self):
        restClient.init('NOSDEV')

        q = "select fields(all) from NetworkPublicUsageDailyMetrics limit 10 "

        res = tooling.query(q)

        print()
