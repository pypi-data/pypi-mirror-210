import unittest,simplejson
from InCli import InCli
from InCli.SFAPI import file,ip_attachments,restClient,utils,file_csv,thread

class Test_Attachement(unittest.TestCase):
    def test_Attachmenst_saveforlater(self):
        #restClient.init('NOSQSM')
        restClient.init('NOSPRD')
        rl = 2002
        res = ip_attachments.get_attachments(limit=rl)

        stats = []
        resp_out=[]

        stats_columns=[]

        def do_work(record):
            try:
                attachment = restClient.requestWithConnection(action=record['Body'])  
                attachment['BodyLength'] = record['BodyLength']
                return attachment
            except Exception as e:
                print(e)
                return None   

        def on_done(attachment,stats):
            if attachment == None: return
            att_str = simplejson.dumps(attachment)

            out = self.obj_sizes(attachment)
            self.obj_size_percentage(out)

            resp = self.obj_sizes(attachment['response'])
            self.obj_size_percentage(resp)

            children = self.obj_sizes(attachment['children'])
            self.obj_size_percentage(children)

            stat = {
                'BodyLength':attachment['BodyLength'],
                'JSONLenght':len(att_str),
                'name':attachment['lwcName'],
                'saveURL':attachment['saveURL'],
       #         'children%': int([ o['percentage'] for o in out if o['key']=='children'][0]),
       #         'childrenS': [ o['size'] for o in out if o['key']=='children'][0],
       #         'labelMap%': int([ o['percentage'] for o in out if o['key']=='labelMap'][0]),
       #         'labelMapS': [ o['size'] for o in out if o['key']=='labelMap'][0],
       #         'response%': int([ o['percentage'] for o in out if o['key']=='response'][0]),
       #         'responseS': [ o['size'] for o in out if o['key']=='response'][0]
            } 

            for o in out:
                if o['percentage'] > 3:
                    stat[f"main_p_{o['key']} %"] = o['percentage']
                    stat[f"main_s_{o['key']}"] = o['size']

            for re in resp:
                if re['percentage'] > 3:
                    stat[f"resp_p_{re['key']} %"] = re['percentage']
                    stat[f"resp_s_{re['key']}"] = re['size']

            for ch in children:
                if ch['percentage'] > 3:
                    stat[f"children_p_{ch['key']} %"] = ch['percentage']
                    stat[f"children_s_{ch['key']}"] = ch['size']

            stats.append(stat)

        thread.execute_threaded(res['records'],stats,do_work,on_done,threads=20)

        for stat in stats:
            for key in stat.keys():
                if key not in stats_columns: stats_columns.append(key)
        
        utils.printFormated(stats,fieldsString=":".join(stats_columns))

        file_csv.write(f'attachment_stats_size_{rl}',stats,header_columns_list=stats_columns)

        print()

    def obj_size_percentage(self,obj):
        sum = 0
        for o in obj:
            sum = sum + o['size']

        for o in obj:
            o['percentage'] = 100*o['size']/sum

    def obj_sizes(self,obj):
        out =[] 
        if type(obj) is list:
            for x,r in enumerate(obj):
                o = {'key':x,'size':self.getsize(r)}
                out.append(o)
            return out
                
        for key in obj.keys():
            val = obj[key]
            o = {'key':key,'size':self.getsize(val)}
            out.append(o)
        return out

    def getsize(self,value):
        if value == None: return 0
        if type(value) is int: return 1
        if type(value) is float: return 4

        if type(value) is str: return len(value)
        if type(value) is bool: return 1

        if type(value) is dict:
            val_str = simplejson.dumps(value)
            return len(val_str)
        
        if type(value) is list:
            val_str = simplejson.dumps(value)
            return len(val_str)          

        print(type(value))

        a=1
        
