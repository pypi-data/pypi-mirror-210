import unittest
from InCli import InCli
from InCli.SFAPI import file,file_csv,query,Sobjects,restClient


class Test_Splunk(unittest.TestCase):

    users = {}
    def getUser(self,id):
        if id not in self.users:
            user = Sobjects.get(id,'User')
            self.users[id] = user['records'][0]['Username']

        return self.users[id]


    def test_merge_files(self):
        restClient.init('NOSQSM')
        
        J = file_csv.read('/Users/uormaechea/Downloads/Jw.csv',separator=',')
        apars = file_csv.read('/Users/uormaechea/Downloads/aparsw.csv',separator=',')

        lenJ = len(J)
        num = 0
        for ra in apars:
            found = False
            for i,rj in enumerate(J):
                if rj['parentRequestId'] == ra['parentRequestId']:
                    ra['bandwidth'] = rj['bandwidth']
                    J.pop(i)
                    found = True
                   # print('',sep='.')
                    num = num +1
                    break
            if found: 
                print(f"Found:  {ra['userId']}")
                continue
            if found == False:
                print(f"{ra['logName']}  {ra['userId']}  {self.getUser(ra['userId'])}")
                
        print(f"J {len(J)} {lenJ} apars {len(apars)}  found {num}")
        file_csv.write('/Users/uormaechea/Downloads/output_week.csv',apars)
        print()


#(index=CS189) CASE(00D7a0000005DzR) sourcetype=CASE(applog*:J) | stats count by timestamp,bandwidth,runTime,logName,parentRequestId