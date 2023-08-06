from . import  file
import os

def read_as_lists(filepath):
    filepath = file.addExtension(filepath,".csv")

    lineslist = []
    f = open(f'{filepath}', 'r',encoding='utf-8-sig')
    lines = f.readlines()

    for line in lines:
        linelist = line.split(";")
        i = 0
        while i < len(linelist):
            linelist[i] = linelist[i].rstrip("\n")
            if linelist[i] == '':   #$$$$ Should there be a NULL?
                linelist[i] = None
            i = i +1

        lineslist.append(linelist)

    return lineslist

def read(filepath,separator=';'):
    filepath = file.addExtension(filepath,".csv")

    f = open(f'{filepath}', 'r',encoding='utf-8-sig')

    #f = open(f'{filepath}', 'r')
    lines = f.readlines()

    firstline = True    
    fieldsMap = []
    headers = None

    for line in lines:
        field = {}
        if firstline == True:
            headers = line.split(separator)
            firstline = False
            continue

        items = line.split(separator)

        i = 0
        for he in headers:
            value = items[i].rstrip("\n")
            if value == '':
                value = None
            field[he.rstrip("\n")] = value
            i = i +1

        fieldsMap.append(field)

    return fieldsMap

def write(filepath,obj,header_columns_list=None):
    filepath = file.addExtension(filepath,".csv")
    f = write_open(filepath,obj,mode='w',header=True,header_columns_list=header_columns_list)
    write_close(f)
    return file.abspath(filepath)

def write_open(filepath,objects,mode="w",header=False,header_columns_list=None):
    filepath = file.addExtension(filepath,".csv")
    f = open(filepath,mode)     
    emptyfile = os.stat(filepath).st_size == 0
    write_objects(f,objects,header,header_columns_list=header_columns_list,emptyfile=emptyfile)
     
    return f

def write_objects(f,objects,header=False,header_columns_list=None,emptyfile=True):
    def write_obj(obj,column_list=None):
        values = []
        if column_list == None: column_list = obj.keys()
        for key in column_list:
            if key not in obj: values.append("")
            else: values.append(str(obj[key]))
        line = ";".join(values)
        print(line,file=f, flush=True)       

    if header == True and emptyfile==True:
        if header_columns_list == None:
            if type(objects) is dict:
                keys = list(objects.keys())
            if type(objects) is list:
                keys = list(objects[0].keys())
            line = ";".join(keys)
        else:
            line = ";".join(header_columns_list)

        print(line,file=f, flush=True)   

    if type(objects) is list:
        for obj in objects:
            write_obj(obj,column_list=header_columns_list)   
    if type(objects) is dict:
        write_obj(objects)   

def write_close(f):
    f.close()