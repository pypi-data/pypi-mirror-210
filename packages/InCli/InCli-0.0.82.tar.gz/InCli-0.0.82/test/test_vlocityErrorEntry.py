import unittest,simplejson,sys
from InCli import InCli
from InCli.SFAPI import VlocityErrorLog,restClient,VlocityTrackingEntry

class Test_VlocityErrorEntry(unittest.TestCase):

    def test_get_errors(self):
        restClient.init('NOSPRD')

        VlocityErrorLog.get_errors()

        print()

    def test_get_errors(self):
        restClient.init('NOSPRD')

        VlocityErrorLog.get_errors()

        print()
    def test_print_errors_orderNum(self):
        restClient.init('NOSPRD')

        orderNums = [
            '00300871',
            '00300083',
            '00300052',
            '00298441',
            '00303789',
            '00303731',
            '00303549',
            '00303520',
            '00303458',
            '00303477',
            '00302987',
            '00303406',
            '00303322',
            '00302681',
            '00302623'
        ]

        original_stdout = sys.stdout
        _filename = f"vte_output.txt"
        with open(_filename, 'w') as f:
            sys.stdout = f 
            for orderNumber in orderNums:
                VlocityTrackingEntry.print_error_list(orderNumber=orderNumber)
                print()
            sys.stdout = original_stdout 
            print()
            print(f"   File {_filename} created.")

        print()
    def test_get_error_ip(self):
        restClient.init('NOSDEV')

        Id = 'a6K3O000000FHuqUAG'

        q = f"select fields(all) from vlocity_cmt__VlocityErrorLogEntry__c where Id='{Id}' limit 10"

        res = query.query(q)


        out=[]
        for record in res['records']:
            data = record['vlocity_cmt__InputData__c']
            datas = simplejson.loads(data)

            theFile =jsonFile.write('TheIPError_1',datas)
            
            out.append(datas)
            print(datas['ErrorMessage__c'])


      #  file_csv.write('VlocityErrorLogEntry_1',out)

        print()

        
