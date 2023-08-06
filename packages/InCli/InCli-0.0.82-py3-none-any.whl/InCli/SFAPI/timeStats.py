from . import restClient,utils,file_csv


class TimeStats:
    time_records = []
    time_record = {}
    file = None
    filename = None
    timestamp = False
    timeseries_dic = None
    time_series = False
    #ts_object = None
    callback = None

    def __init__(self,filename=None,timestamp=False,append=False,timeseries_dic=None):
        self.filename = filename
        self.timestamp = timestamp
        self.append = append
        self.timeseries_dic = timeseries_dic
        if timeseries_dic!=None:
            timeseries_dic['TS']=''
            timeseries_dic['op']=''
            timeseries_dic['time']=''
            self.time_series = True
            self.filename = timeseries_dic['filename']

    def new(self,fields=None):
        if self.time_series:
            self.time_record = self.timeseries_dic.copy()

        else:
            self.time_record = {}
            self.time_records.append(self.time_record)
            if fields == None: return
            for field in fields:
                self.time_record[field] = ''
    
    def field(self,name,value):  
        self.time_record[name]=value   

    def __time_series(self,field,value):
        self.time_record['TS'] = utils.datetime_now_string('%Y/%m/%d %H:%M:%S')
        self.time_record['op'] = field
        self.time_record['time'] = value

        self.__print_to_file(self.time_record)

    def time(self,field,extend_obj=None,index=-1):
        if extend_obj != None:
            self.time_record.update(extend_obj)
        elapsedTime = restClient.getLastCallElapsedTime(index=index)
        if self.time_series:
            self.__time_series(field,elapsedTime)
            self.time_record = self.timeseries_dic.copy()
        else:
            self.time_record[field] = elapsedTime

    def time_inner(self,field,time):
        self.time_record[field] = time

    def time_no(self,field,value):
        self.time_record[field] = value
    
    def __print_to_file(self,obj):
        if self.callback != None:
            self.callback(obj)
            return
        if self.file == None:
            mode = 'w' if self.append == False else 'a'
            self.file = file_csv.write_open(self.filename,objects= obj,mode=mode,header=True)
        else:
            file_csv.write_objects(self.file,obj)   

    def print(self):
        if self.timeseries_dic != None:
            return
        
        if self.timestamp == True:
            self.time_record['TS'] = utils.datetime_now_string('%Y/%m/%d %H:%M:%S')

        if self.filename!=None:
            self.__print_to_file(self.time_records[-1])

        else:
            utils.printFormated(self.time_records)

    def end(self):
        if self.file!=None:
            file_csv.write_close(self.file)
