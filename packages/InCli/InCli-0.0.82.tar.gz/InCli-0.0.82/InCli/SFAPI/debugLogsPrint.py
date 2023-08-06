from . import restClient,file,utils,elementParser

import colorama
import sys
import ansi2html,re
import simplejson

def delta(obj,field):
    return obj[field][1] - obj[field][0] if len(obj[field]) > 1 else 0

def print_parsed_lines_to_output(pc):
    def escape_ansi(line):
        ansi_escape =re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
        return ansi_escape.sub('', line)

    if 1==1:
        pc['context']['parsedLines'] = processRepetition(pc['context']['parsedLines'])

    logId = pc['logId']
    toFile= pc['writeToFile'] if 'writeToFile' in pc else False

    if toFile == True:
        filename = f"{restClient.logFolder()}{logId}_ansi.txt"

        original_stdout = sys.stdout
        with open(filename, 'w') as f:
            sys.stdout = f 
            print_parsed_lines(pc)
            sys.stdout = original_stdout 

        data = file.read(filename)
        converter = ansi2html.Ansi2HTMLConverter()
     #   converter.
        html = converter.convert(data)
        html1 = html[:html.index("<style type")]
        html2 = html.split('</style>')[1]

        style = """
        <style type="text/css">
        * {font-family:monospace}
        * {font-size: small;}
        .ansi2html-content { display: inline; white-space: pre-wrap; word-wrap: break-word; }
        .body_foreground { color: #FFFFFF; }
        .body_background { background-color: #020934; }
        .inv_foreground { color: #000000; }
        .inv_background { background-color: #FFFFFF; }
        .ansi1 { font-weight:normal; }
        .ansi2 { font-weight: lighter; }
        .ansi31 { color: #f98e7e; }
        .ansi32 { color: #05de05; }
        .ansi33 { color: #d0d011; }
        .ansi36 { color: #04e2e2; }
        .ansi37 { color: #b2acac; }
        </style>"""

        if 1==2:
            style = """
            <style type="text/css">
            * {font-family:monospace}
            * {font-size: small;}
            .ansi2html-content { display: inline; white-space: pre-wrap; word-wrap: break-word; }
            .body_foreground { color: #020934; }
            .body_background { background-color: #FFFFFF; }
            .inv_foreground { color: #000000; }
            .inv_background { background-color: #FFFFFF; }
            .ansi1 { font-weight:normal; }
            .ansi2 { font-weight: lighter; }
            .ansi31 { color: #c13f1e; }
            .ansi32 { color: #0a870a; }
            .ansi33 { color: #ddbe22; }
            .ansi36 { color: #2585de; }
            .ansi37 { color: #8e8b8b; }
            </style>"""
       # html = html.replace('background-color: #000000;','background-color: #020b3b;')
       # html = html.replace('aa5500','ecec16')
       # html = html.replace('F5F1DE','8e8383')
       # html = html.replace('AAAAAA','FFFFFF')
       # html = html.replace('000316','3c3e48')
       # html = html.replace('aa0000','e41717')
        html = html1 + style + html2
        filename = f"{restClient.logFolder()}{logId}.html"
        file.write(filename,html)
        print(f"Html file: {filename}")
        clean = escape_ansi(data)
        filename = f"{restClient.logFolder()}{logId}.txt"
        file.write(filename,clean)  
        print(f"Txt file: {filename}")
 
    else:
        colorama.just_fix_windows_console()
        print_parsed_lines(pc)

def is_print_to_json(pc):
    return 'print_output' in pc['context'] and pc['context']['print_output'] == 'JSON'

def print_parsed_lines(pc):
    context = pc['context']

    if pc['output_format']=='JSON':
        if 'logRecord' in pc and pc['logRecord'] != None:
       #     lr = simplejson.dumps(pc['logRecord'])
            parsed_lines = []
            for num,parsedLine in enumerate(context['parsedLines']):
                if parsedLine['type'] == 'LOGDATA': continue
                parsed_lines.append(print_parsed_line(pc,parsedLine,num))
            output_dict = {
                'logRecord':pc['logRecord'],
                'parsed_lines':parsed_lines
            }
            output_json = simplejson.dumps(output_dict,indent=2)

           # filename = f"{restClient.logFolder()}{pc['logId']}.json"
           # file.write(filename,output_json)
            print(output_json)
            a=1
    else:
        logId = pc['logId'] if 'logId' in pc else None
        print_only_errors = pc['print_only_errors'] if 'print_only_errors' in pc else False
        if context['exception'] == False and print_only_errors == True: return 
        print('___________________________________________________________________________________________________________________________________________________________________')
        if logId != None:  print(logId)
        print()
        if logId != None:  print(f"{utils.CFAINT}Parsing log Id {logId}    file: {restClient.logFolder()}{logId}.log{utils.CEND}")
        elif pc['filepath'] != None:
                print(f"file: {pc['filepath']}")

        firstLines = True

        pc['new_print'] = True
        for num,parsedLine in enumerate(context['parsedLines']):
            if parsedLine['type'] == 'LOGDATA':
                print(parsedLine['output'])
                continue
            else:
                if firstLines == True:
                    firstLines = False
                    print()
                    print()
            printLimits = pc['printLimits'] if 'printLimits' in pc else False

            if printLimits == False:
                if '*** getCpuTime() ***' in parsedLine['output']:   continue
                if '*** getQueries() ***' in parsedLine['output']:   continue
                if 'LoggingOpenInterface.' in parsedLine['output']:   continue
                if parsedLine['type'] == 'LIMIT':                    continue

            print_parsed_line(pc,parsedLine,num)    
        print()

def isRep(all_loops,parsed_line_index,parsed_line,parsed_lines):
      if parsed_line['type'] not in ['METHOD','WF_CRITERIA','CONSTRUCTOR','DEBUG']:  return False,None

      for loop in all_loops:
        links = len(loop)
        loop_start_position = loop[0]
        link_lenght = loop[1] - loop[0]
        loop_lenght = links * link_lenght

        if loop_start_position <= parsed_line_index <= loop_start_position + loop_lenght - 1:
            if loop_start_position <= parsed_line_index <= loop_start_position + link_lenght-1:

                parsed_line['loop'] = links
                parsed_line['is_loop'] = True
                parsed_line['loop_links'] = links
                parsed_line['loop_link_lenght'] = link_lenght
                parsed_line['loop_position'] = parsed_line_index - loop_start_position + 1

                if len(parsed_line['timeStamp']) > 1 and (loop_start_position <= parsed_line_index < loop_start_position + link_lenght):
                    total_method_time = 0
                    total_wait_time = 0
                    for link_index in range(0,links):
                        brother_index = parsed_line_index + link_index * link_lenght
                        brother = parsed_lines[brother_index]
                        brother_method_time = brother['timeStamp'][1] - brother['timeStamp'][0]
                        total_method_time = total_method_time + brother_method_time

                        if link_index !=0:
                            brother_previous_line = parsed_lines[brother_index - 1]

                            if brother_previous_line['ident'] < brother['ident']:
                                wait_time =  brother['timeStamp'][0] - brother_previous_line['timeStamp'][0]
                            else:
                                ts = brother_previous_line['timeStamp'][1] if len(brother_previous_line['timeStamp'])>1 else  brother_previous_line['timeStamp'][0]
                                wait_time =  brother['timeStamp'][0] - ts

                            total_wait_time = total_wait_time + wait_time
                        #    print(f"{brother_previous_line['ident']} {brother_previous_line['output']}  {brother_previous_line['timeStamp'][0]}  {brother_previous_line['timeStamp'][1]} {brother['ident']}  {brother['output']}   {brother['timeStamp'][0]} {brother['timeStamp'][1]}   {wait_time}  {total_wait_time}")
                    parsed_line['totalLoopTime'] = total_method_time
                    parsed_line['totalLoopWait'] = total_wait_time
    
                #for the last line in the chain, set time_exit to the very last in the loop
                if len(parsed_line['timeStamp']) > 1 : 
                    parsed_line['timeStamp'][1] = parsed_lines[ parsed_line_index + (links-1) * link_lenght ]['timeStamp'][1]
                return True,True

            else: return True,False

      return False,False

def processRepetition(parsed_lines):

    for parsed_line in parsed_lines:
        if 'output' not in parsed_line:  
            print()

    all_loops = utils.get_all_loops(parsed_lines,"output")

    new_parsed_lines = []
    for parsedLineNum,parsedLine in enumerate(parsed_lines):
        if 'timeStamp' in parsedLine and parsedLine['timeStamp'][0] == 10188648957:
            a=1
            
        is_loop, is_first_chain = isRep(all_loops,parsedLineNum,parsedLine,parsed_lines)
        if is_loop == True and is_first_chain == False:   continue
        new_parsed_lines.append(parsedLine)

    return new_parsed_lines   

def emptyString(context,size,char=' ',ident=None):
 #   str = ''
    if ident is None:   
        ident = context['ident']
    length = ident * size
    str = " "*length
 #   for x in range(length):   str = str + char  
    return str       

def get_parent_if_last_for_level(parsed_lines,parsed_line_index):
    current = parsed_lines[parsed_line_index]
    for index in range(parsed_line_index+1,len(parsed_lines)):
        if parsed_lines[index]['ident'] == current['ident']:
            return None
        if parsed_lines[index]['ident'] < current['ident']:
            i = 1
            while True:
                parent = parsed_lines[parsed_line_index-i]
                if parent['ident'] < current['ident']:
                    return parent
                i = i + 1

def get_all_limits_as_lists(pc,d,entry=True):
    packages = get_packages_in_LU(pc)

    pack = []
    keys = []
    vals = []

    for package in packages:
        limits = get_limits(pc,d,package,entry)
        if limits == None:
            limits = elementParser.create_LU_limits()
        key_str = list(limits.keys())
        vs = [l['v'] if int(l['v'])>0 else '' for l in list(limits.values())]

        s = utils.CLIGHT_GRAY +utils.CFAINT+  "|" + utils.CEND

        pack.append(f"{package:^62}")
        keys.append(f"{'SOQ':^3}{s}{'SOQr':^5}{s}{'SOS':^3}{s}{'DML':^3}{s}{'PID':^3}{s}{'DMr':^5}{s}{'CPU':^6}{s}{'Heap':^7}{s}{'CO':^3}{s}{'@':^3}{s}{'Fut':^3}{s}{'Que':^3}{s}{'Mob':^3}")
        vals.append(f"{vs[0]:>3}{s}{vs[1]:>5}{s}{vs[2]:>3}{s}{vs[3]:>3}{s}{vs[4]:>3}{s}{vs[5]:>5}{s}{vs[6]:>6}{s}{vs[7]:>7}{s}{vs[8]:>3}{s}{vs[9]:>3}{s}{vs[10]:>3}{s}{vs[11]:>3}{s}{vs[12]:>3}")

    return f"{s}".join(pack),f"{s}".join(keys),f"{s}".join(vals)

def get_limits(pc,d,package='(default)',entry=True):
    lu = d['LU']
    pos=lu[0]
    if entry == False and len(lu)>1: pos = lu[1]

    if package in pos:
        index = pos[package]
        return pc['context']['LU'][package][index]

    return None

def get_limit(pc,d,package='(default)',limit='DML rows',entry=True,):

    limits = get_limits(pc,d,package,entry)
    if limits != None and limit in limits: return limits[limit]['v']

    return 0

def get_packages_in_LU(pc):
    packages = ['(default)']
    for key in pc['context']['LU'].keys():
        if key != '(default)': packages.append(key)
    return packages

def soql_total_queries(pc,d):
    soql_total_queries_entry = d['totalQueries'][0]
    soql_total_queries_exit = d['totalQueries'][1] if len(d['totalQueries']) >1 else soql_total_queries_entry
    soql_total_queries_delta = soql_total_queries_exit-soql_total_queries_entry

    return soql_total_queries_entry,soql_total_queries_delta

def times(pc,d,parsed_line_index):
    level = d['ident']
    context = pc['context']

    if 'prevTimes' not in context:
        context['prevTimes'] = {
            0:[0,0]
        }
    if 'prevLevel' not in context:
        context['prevLevel'] = 0

    time_stamp_entry = d['timeStamp'][0]
    time_stamp_exit = d['timeStamp'][1] if len(d['timeStamp'])>1 else time_stamp_entry

    if level == context['prevLevel']:  wait_time = time_stamp_entry - context['prevTimes'][level][1]
    if level >  context['prevLevel']:  wait_time = time_stamp_entry - context['prevTimes'][context['prevLevel']][0]
    if level <  context['prevLevel']:  wait_time = time_stamp_entry - context['prevTimes'][level][1]

    context['prevTimes'][level] = [time_stamp_entry,time_stamp_exit]

    if wait_time <0 and 'is_loop' in d:   
        wait_time = time_stamp_entry - context['prevTimes'][level][0]

    if 'totalLoopWait' in d:
        wait_time = d['totalLoopWait'] + wait_time

    wait_time = f"{wait_time/1000000:.0f}"

    wait_time_exit = "0"
    parent = get_parent_if_last_for_level( context['parsedLines'],parsed_line_index)
    if parent != None:
        if len(parent['timeStamp']) > 1:
            wait_time_exit = parent['timeStamp'][1] - time_stamp_exit
            wait_time_exit = f"{wait_time_exit/1000000:.0f}"

    context['prevLevel'] = level

    time_ms = f"{d['elapsedTime']/1000000:.0f}"
    time_ms = f'{int(time_ms):,}'

    element_time = f"{delta(d,'timeStamp')/1000000:.0f}"
    if 'totalLoopTime' in d:  element_time = f"{ d['totalLoopTime']/1000000:.0f}"

    return time_stamp_entry,time_stamp_exit,time_ms,wait_time,wait_time_exit,element_time

def cpu_times(pc,d):
    context = pc['context']

    if 'previousElapsedTime' not in context:
        context['previousElapsedTime'] = 0
    if 'previousCPUTime' not in context:
        context['previousCPUTime'] = 0

    if d['elapsedTime'] == 7929058566:
        a=1
   #cpu_time_entry = int(d['CPUTime'][0])
    cpu_time_entry = get_limit(pc,d,limit='CPU time')


    if int(context['previousCPUTime']) == 0:
        a=1
    if cpu_time_entry == 0:
        a=1

    cpu_time_elapsed = int(cpu_time_entry) - int(context['previousCPUTime'])

    context['previousCPUTime'] = cpu_time_entry
    context['previousElapsedTime']  = d['elapsedTime']

    return cpu_time_entry,cpu_time_elapsed

def queries(pc,d):
    
    soql_queries = {
        '(default)':get_limit(pc,d,limit='SOQL queries')
    }
    for package in get_packages_in_LU(pc):
        if package == '(default)':continue
        soql_queries[package] = get_limit(pc,d,package=package,limit='SOQL queries')

    soql_total_queries_entry = d['totalQueries'][0]

    unaccounted = soql_total_queries_entry #- int(soql_queries['(default)'])
    for value in soql_queries.values():
        unaccounted = unaccounted - int(value)

    return soql_queries,unaccounted

def s_queries_columns(soql_queries):
    ko = []
    ko.append('Q')
    for key in soql_queries.keys():
        if key == '(default)': continue
        else: ko.append(f"Q{key[0:2]}")

    s = utils.CLIGHT_GRAY +utils.CFAINT+  "|" + utils.CEND

    kos = [f"{k:^3}" for k in ko]
    str = s.join(kos)

    return str

def s_queries_values(soql_queries):
    vals = []
    val = soql_queries['(default)']
    if val == 0: val =''

    vals.append(soql_queries['(default)'])

    for key in soql_queries.keys():
        if key == '(default)': continue
        else: 
            val = soql_queries[key]
            if val == 0: val =''
            vals.append(val)

    s = utils.CLIGHT_GRAY +utils.CFAINT+  "|" + utils.CEND

    kos = [f"{k:^3}" for k in vals]
    str = s.join(kos)

    return str

def print_parsed_line(pc,d,parsed_line_index):
    context = pc['context']
    Cinit = utils.CEND

    if d['type'] == 'LIMITS':
        context['previousIsLimit'] = True
        return

    if 'output' not in d:
        print()
    output_string = d['output']
    
    apex_line_number = d['apexline'] if 'apexline' in d else ''

    soql_total_queries_entry,soql_total_queries_delta = soql_total_queries(pc,d)

    cpu_time_entry,cpu_time_elapsed = cpu_times(pc,d)

    soql_queries,Qmct_estimate = queries(pc,d)

   # s_queries(soql_queries)
    time_stamp_entry,time_stamp_exit,time_ms,wait_time,wait_time_exit,element_time = times(pc,d,parsed_line_index)

    element_type = d['type']
    level = d['ident']

    compact = True

    if pc['output_format']=='STDOUT':
        if pc['new_print']:
            pc['new_print'] = False
            print( f"Log time: {pc['context']['parsedLines'][3]['lines'][0].split(' ')[0]} to {pc['context']['parsedLines'][-1]['lines'][0].split(' ')[0]}")

        pcLevel = pc['level'] if 'level' in pc else None
        if pcLevel != None:
            if level > int(pc['level']):
                return

        if element_type == 'DEBUG':
            element_type = f"{d['type']}-{d['subType']}"
            Cinit = utils.CRED if d['subType'] == 'ERROR' else utils.CGREEN
        elif element_type == 'VAR_ASSIGN' and d['subType'] == 'EXCEPTION':  Cinit = utils.CRED
        elif element_type == 'VAR_ASSIGN' and d['subType'] != 'EXCEPTION':  return
        elif d['type'] == 'EXCEPTION':  Cinit = utils.CRED
        elif d['type'] == 'SOQL':   Cinit = utils.CCYAN
        elif d['type'] == 'DML':    Cinit =  utils.CYELLOW
        elif d['type'] == 'CODE_UNIT':  Cinit =  utils.CYELLOW

        element_type_color =utils. CYELLOW  if d['type'] in ['SOQL','DML','VAR_ASSIGN'] and level == 0 else ''

        if cpu_time_elapsed == 0 and element_type != 'END':
            cpu_time_elapsed = ''
            cpu_time_entry = ''

        if 'is_loop' in d:
            ls = f"    x{d['loop_links']}-{d['loop_position']}"# if d['loop_position'] == 1 else f"             "
            output_string = f"{output_string}   {utils.CYELLOW}{ls}{utils.CEND}"

        if element_time == "0":  element_time =''
        if soql_total_queries_delta ==0: soql_total_queries_delta = ''
        if Qmct_estimate == 0: Qmct_estimate = ''
        if soql_total_queries_entry == 0: soql_total_queries_entry = ''
        if wait_time == "0":  wait_time =''
        if wait_time_exit == "0":  wait_time_exit ='' 
        else: wait_time_exit=f"{wait_time_exit}"
 #       if soql_queries_cmt_entry == 0 : soql_queries_cmt_entry = ''
 #       if soql_queries_entry == 0 : soql_queries_entry = ''

        time_stamp_entry = utils.CLIGHT_GRAY +utils.CFAINT+ f"{time_stamp_entry:12}" + utils.CEND
        time_stamp_exit = utils.CLIGHT_GRAY +utils.CFAINT+ f"{time_stamp_exit:12}" + utils.CEND

        s = utils.CLIGHT_GRAY +utils.CFAINT+  "|" + utils.CEND

        times_lenght = 12

        if pc['allLimits'] == True:
            packages_str,limits_str,values_str = get_all_limits_as_lists(pc,d)

        if context['firstLineOut'] == True:
            valname = f"time         query  Call Stack"

            if pc['allLimits']==False:
                sql_cols = s_queries_columns(soql_queries)
             #   limits_str = f"{'CPU':^6}{s}{'cpuD':^6}{s}{'Qt':^3}{s}{'Q':^3}{s}{'Qmp':^3}{s}{'Qe':^3}"
                limits_str = f"{'CPU':^6}{s}{'cpuD':^6}{s}{'Qt':^3}{s}{sql_cols}{s}{'Qe':^3}"

            else:
                print(f"{' ':34}{s}{packages_str}{s}")

            print(f"{utils.CFAINT}{'time entry':^12}{s}{utils.CFAINT}{'time exit':^12}{s}{'ts':^8}{s}{limits_str}{s}{'type':^21}{s}{'line':^4}{s}{valname:50}")
            context['firstLineOut'] = False

        a=f"{wait_time}·{element_time}·{wait_time_exit}"
        aa = times_lenght-len(a)
        if aa<0: aa=0
        element_time = utils.CGREEN + f"{wait_time}·{utils.CWHITE}{element_time}{utils.CLIGHT_GREEN}·{wait_time_exit}{'':<{aa}}"

        output_string = utils.CYELLOW+utils.CFAINT+ f"{'':<{level}}"+f"{element_time:<{times_lenght}}"+utils.CYELLOW+utils.CFAINT+f"{soql_total_queries_delta:>4}" +utils.CEND + Cinit +f"    {utils.CYELLOW}{utils.CFAINT}{level} {utils.CEND}{Cinit}{output_string}"

        if pc['allLimits'] == False:
            sql_vals = s_queries_values(soql_queries)
            limits_string = f"{cpu_time_entry:>6}{s}{cpu_time_elapsed:6}{s}{soql_total_queries_entry:>3}{s}{utils.CGREEN}{sql_vals}{s}{utils.CYELLOW}{(Qmct_estimate):>3}"
        else:
            limits_string = values_str

        print(f"{time_stamp_entry:12}{s}{time_stamp_exit:12}{s}{time_ms:>8}{s}{limits_string}{utils.CEND}{s}{element_type_color}{element_type:21}{utils.CEND}{s}{apex_line_number:>4}{s}{output_string:50}"+utils.CEND)

    else:
        
        output = {
            'line num':parsed_line_index-2,
            'level':level,
            'TS entry':cpu_time_entry,
            'TS exit':time_stamp_exit,
            'TS ms':time_ms,
            'CPU (default)':cpu_time_entry,
            'CPU_elapsed':cpu_time_elapsed,
            'SOQL Total':soql_total_queries_entry,
            'SOQL (default)':soql_queries['(default)'] if '(default)' in soql_queries else 0,
            'SOQL vlocity_cmt':soql_queries['vlocity_cmt'] if 'vlocity_cmt' in soql_queries else 0,
            'SOQL unaccounted':Qmct_estimate,
            'type':element_type,
            'apex line':apex_line_number,
            'event time prev':wait_time,
            'event time':element_time,
            'event time post':wait_time_exit,
            'event SOQL':soql_total_queries_delta,
            'output':output_string,
            'exception':context['exception'] if 'exception' in context else False
        }

        return output

