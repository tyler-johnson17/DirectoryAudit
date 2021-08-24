import sys,json
#import sources.ldap as ldapSource
import jsondiff as jd
from jsondiff import diff
from multiprocessing import Lock, Process, Queue, current_process, cpu_count
import time
import queue # imported for using queue.Empty exception

## Classes ##
## END Classes ##
## Functions ##
def compareJSONObjects(old, new):
    return (diff(old, new, syntax='explicit'))

def compareJSONObjectsFormatted(old, new, index, value):
    result = compareJSONObjects(old, new)
    # if result != {}:
    #     print(result)
    result_json = [{
        "index" : index,
        "value" : value,
        "results" : result
        }]
    return result_json

def worker(outstanding_tasks, completed_tasks):
    while True:
        try:
            task = outstanding_tasks.get_nowait()
        except queue.Empty:
            break
        else:
            list1 = task[0]
            list2 = task[1]
            index = task[2]
            value = task[3]
            #print("Working on object " + str(value) + " | #: " + str(index))
            completed_tasks.put(compareJSONObjectsFormatted(list1, list2, index, value))
    return True


def loadJSON(path: str):
    try:
        with open(path) as f:
            data = json.load(f)
        return data
    except:
        print("Error loading " + path)
        return None

def writeJSON(data, path: str):
    try:
        with open(path, "w") as f:
            f.write(data)
    except:
        print("Error writing " + path)
        return None

def getSubListofElements(jsonObject, field):
    new_list = []
    for element in jsonObject:
        new_list.append({field : element[field]})
    return new_list

def createConfig():
    return 1

def sortJSON(jsonObject, element):
    return jsonObject.sort(key=lambda x: x[element])

def compareJSON(old, new, element):
    try:
        multicompareListResults = multiprocessCompareJSON(old, new, element)
        result = multiprocessComparisonResults(old, new, multicompareListResults)
        return result
    except Exception as ex:
        return ex

def multiprocessCompareJSON(old, new, task_value):
    totalDiff = []
    try:
        number_of_tasks = len(old)
        number_of_processes = (4*cpu_count())
        outstanding_tasks = Queue()
        completed_tasks = Queue()
        processes = []
        for i in range(number_of_tasks):
            outstanding_tasks.put([old[i], new[i], i, task_value])
        # creating processes
        for w in range(number_of_processes):
            p = Process(target=worker, args=(outstanding_tasks, completed_tasks))
            processes.append(p)
            p.start()
        # completing process
        for p in processes:
            p.join()
        # print the output
        while not completed_tasks.empty():
            for complete in completed_tasks.get():
                try:
                    totalDiff.append(complete)
                except:
                    None
        return totalDiff
    except Exception as ex:
        print(ex)
        return ex

def multiprocessComparisonResults(old, new, results):
    processed_results = []
    for result in results:
        if result['results'] != {}:
            index = result['index']
            index_value = result['value']
            #print("Detected change in object (index: " + str(index) + "): " + str(index_value))
            #print(result['results'])
            old_value = ''
            new_value = ''
            field_index = 0
            for k, v in result['results'].items():
                try:
                    for k2, v2 in v.items():
                        try:
                            for k3, v3 in v2.items():
                                try:
                                    if 'insert' in str(k3):
                                        try:
                                            for field in v3:
                                                field_index = int(field[0])
                                                #old_value = str(old_fields[index][field_index])
                                                new_value = new[index][index_value][field_index]
                                                processed_results.append([index, index_value, field_index, old_value, new_value, 'insert'])
                                        except Exception as ex:
                                            print("Got insert")
                                            print(str(index) + " " + str(index_value) + " " + str(k3)+ " " + str(v3))
                                            print(ex)
                                    elif 'delete' in str(k3):
                                        try:
                                            for field in v3:
                                                field_index = int(field)
                                                old_value = old[index][index_value][field_index]
                                                #new_value = str(new_fields[index][field_index])
                                                processed_results.append([index, index_value, field_index, old_value, new_value, 'delete'])
                                        except Exception as ex:
                                            print("Got delete")
                                            print(str(index) + " " + str(index_value) + " " + str(k3)+ " " + str(v3))
                                            print(ex)
                                    else:
                                        try:
                                            field_index = int(k3)
                                            old_value = old[index][index_value][field_index]
                                            new_value = new[index][index_value][field_index]
                                            processed_results.append([index, index_value, field_index, old_value, new_value, 'update'])
                                        except Exception as ex:
                                            print("Got update")
                                            print(str(index) + " " + str(index_value) + " " + str(k3)+ " " + str(v3))
                                            print(ex)
                                except Exception as ex1:
                                    try:
                                        for field in v2.items():
                                            field_index = field['field']
                                            #old_value = old[index][index_value][field_index]
                                            new_value = field['value']
                                            processed_results.append([index, index_value, field_index, old_value, new_value, 'strange_update'])
                                    except Exception as ex2:
                                        print("Got strange update")
                                        print(str(index) + " " + str(index_value) + " " + str(k3)+ " " + str(v3))
                                        print(ex2)
                                    print(ex1)
                        except Exception as ex3:
                            try:
                                for field in v2:
                                    field_index = field['field']
                                    #old_value = old[index][index_value][field_index]
                                    new_value = field['value']
                                    processed_results.append([index, index_value, field_index, old_value, new_value, 'dupdate'])
                            except:
                                print(str(index) + " " + str(index_value) + " " + str(k2)+ " " + str(v2))
                                print("Not good")
                            print(ex3)
                except Exception as ex4:
                    try:
                        for field in v:
                            field_index = field
                            new_value = new[index][field_index]
                            processed_results.append([index, index_value, field_index, old_value, new_value, (str(k))])
                    except:
                        print(str(index) + " " + str(index_value) + " " + str(k)+ " " + str(v))
                        print("Really bad")
                    print(ex4)
    return processed_results

## END Functions ##
## Global Vars ##
config = loadJSON("../config.json")
first_run = False
## END Global Vars ##
## Main Routine ##
if config == None: # Check if first run.
    createConfig
    print("Please modify the default configuration.")
    exit
else:
    sources = config['sources']
    for source in sources:
        if source['type'] == 'LDAP':
            ## Detect Inserted/Deleted Objects
            #print(compareJSONFiles("../last_members_1.json", "../last_members_2.json", "dn"))
            json1 = loadJSON("../last_members_1.json")
            json2 = loadJSON("../last_members_2.json")
            json1.sort(key=lambda x: x[source['key']])
            json2.sort(key=lambda x: x[source['key']])
            #key_list1 = getSubListofElements(json1, source['key'])
            #key_list2 = getSubListofElements(json2, source['key'])
            #fields_list1 = getSubListofElements(json1, "fields")
            #fields_list2 = getSubListofElements(json2, "fields")
            compare = {}
            compare_index = 0
            compare_results_1 = []
            compare_results_2 = []
            for item in json2:
                found = False
                for item2 in json1:
                    if item[source['key']] == item2[source['key']]:
                        found = True
                        compare_results_1.append({'fields':item['fields']})
                        compare_results_2.append({'fields':item2['fields']})
                if found == False:
                    print("New object (" + str(item[source['key']]) + ") is found!")
                compare[compare_index] = found
                compare_index += 1
            for item2 in json1:
                found = False
                for item in json2:
                    if item[source['key']] == item2[source['key']]:
                        found = True
                if found == False:
                    print("Deleted object (" + str(item2[source['key']]) + ")!")
            fieldsResult = compareJSON(compare_results_2, compare_results_1, "fields")
            print(fieldsResult)