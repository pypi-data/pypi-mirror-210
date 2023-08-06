import logging
import threading,time
from queue import Queue
import math
import sys


_counter = 0
#---------------------------------
def getCounter():
  global _counter
  return _counter
#---------------------------------
def count():
  return _counter
  
def printCounter():
  global _counter

  print(_counter)
#---------------------------------
def _testMultiple(func,iterations,processNumber,**funcArg):
  global _counter
  for a in range(iterations):
    func(processNumber=processNumber+a)
    with threadLock:
      _counter += 1
#---------------------------------
threadLock = threading.Lock()
def run(func,iterations,processStartNumber=0,threads=50,onFinished=None):
  global _counter
  _counter = 0

  try:
    for _itera in range(threads):
      processNumber = processStartNumber+ (_itera*threads)
      threading.Thread(target=_testMultiple,args=(func,iterations,processNumber), daemon=True).start()

  except:
    print ("Error: unable to start thread")
  while _counter < iterations * threads :
    logging.info(f'Iteration {_counter}  from {iterations * threads}')
    time.sleep(30)

  if onFinished!=None:
    onFinished()
    
  print("Done")

#---------------------------------
_processed = 0
_totalToProcess = 0

def processList(func,theList,threads):
  global _processed,_totalToProcess

  _processed = 0
  _totalToProcess = len(theList)
  itemsPerTh = math.ceil(_totalToProcess/threads)


  total = 0
  while total < _totalToProcess:
    end = total+itemsPerTh
    if end>_totalToProcess:
      end = _totalToProcess
    data = {
      "list" : theList[total:end]
    }

    threading.Thread(target=_processList,args=(func,theList[total:end],)).start()
    total = total + itemsPerTh

 # print()

  while (_totalToProcess>_processed):
   # print(_processed)
 #   sys.stdout.write("\r%d%%" % int(100*_processed/_totalToProcess))
 #   sys.stdout.flush()
    time.sleep(1)

def progress():
    global _processed,_totalToProcess

    sys.stdout.write("\r%d%%" % int(100*_processed/_totalToProcess))
    sys.stdout.flush() 
    if (_processed==_totalToProcess):
      print()


def _processList(func,ls):
  global _processed
  for l in ls:
    func(l)
   # print('one done')
    with threadLock:
      _processed += 1
      progress()
 # print('X done')
###############
###############
###############

executed_records = 0
total_records = 0
counter_look = threading.Lock()

def increase_counter():
  global executed_records,counter_look,total_records
  with counter_look:
    executed_records = executed_records + 1
    sys.stdout.write("\r%d%%" % int(100*executed_records/total_records))
    sys.stdout.flush() 

def on_work_done(queue,on_done,output_records):
  while True:
    processed_record = queue.get()
    #print(queue.qsize())
    if type(processed_record) is str and processed_record == 'STOP': break
    on_done(processed_record,output_records)
    increase_counter()

def working_thread(queue_in,queue_out,do_work):
  while True:
    record = queue_in.get()
    if type(record) is str and record == 'STOP': break
    processed_record = do_work(record)
    queue_out.put(processed_record)


def execute_threaded(input_records,output_records,do_work,on_done,threads=1):
  """
  - do_work - function that accepts a record and returns a record (record)->processed_record. Gets a record from input and returns a processed record
  - on_done - gets the processed record, does additional processing and must append to output_records. (record,output_records)
  """
  global executed_records,total_records

  q_in = Queue(maxsize=0)
  q_done = Queue(maxsize=0)

  executed_records = 0
  total_records = len(input_records)

  print(f"Executing threaded records->{total_records}")

  thread_work_done = threading.Thread(target=on_work_done,args=(q_done,on_done,output_records), daemon=True)
  thread_work_done.start()

  all_threads = []
  for t in range(0,threads):
    thread = threading.Thread(target=working_thread,args=(q_in,q_done,do_work), daemon=True)
    thread.start()
    all_threads.append(thread)

  for record in input_records:
    q_in.put(record)

  for x in range(0,threads):
    q_in.put('STOP')

  for thread in all_threads:
    thread.join()

  q_done.put('STOP')  
  thread_work_done.join()
  print()
  print(f"Execution finished threaded records->{len(input_records)}")
