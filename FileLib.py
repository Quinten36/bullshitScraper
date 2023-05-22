from csv import DictWriter, writer
import os
import json
import pyodbc
import sqlite3
from pymongo import MongoClient



def WriteDataToJSON(outfile, data):
    EnsureFileExists(outfile)
    with open(outfile, 'w', encoding="utf8", newline="") as out:
        json.dump(data, out, indent=2, ensure_ascii=False) 
        
def WriteDataToCSV(outfile, data):
    EnsureFileExists(outfile)
    with open(outfile, 'w', encoding="utf8", newline="") as out:
        write = writer(out)
        write.writerows(data)
        
def EnsureFileExists(outfile):
    directory = os.path.dirname(outfile)
    if not os.path.exists(directory):
        os.makedirs(directory)
    if not os.path.exists(outfile):
        open(outfile, 'w').close()
    
def saveDictToJSON(output, data):
    with open(output, 'w', encoding="utf8", newline="") as out:
        json.dump(data, out, ensure_ascii=False)  
    
def saveDictToCSV(output, data):
    with open(output, 'w', encoding="utf8", newline="") as out:
        write = DictWriter(out, fieldnames=data[0].keys())
        write.writeheader()
        for entry in data:
            write.writerow(entry)
    

def saveDictToSQLITE(database, table, data):
    # connect to the database
    conn = sqlite3.connect(database)
    c = conn.cursor()

    # create the table if it doesn't exist
    column_names = ", ".join(data.keys())
    c.execute(f"CREATE TABLE IF NOT EXISTS {table} (id INTEGER PRIMARY KEY AUTOINCREMENT, {column_names})")

    # Check if data already exists
    placeholders = " AND ".join([f"{key} = ?" for key in data.keys()])
    values = tuple(data.values())
    c.execute(f"SELECT * FROM {table} WHERE {placeholders}", values)
    existing_data = c.fetchone()

    # insert the data into the table if it doesn't already exist
    if not existing_data:
        placeholders = ", ".join("?" * len(data))
        c.execute(f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})", values)


    # commit the changes and close the connection
    conn.commit()
    conn.close()
    
    
    
mongoURL = "213.184.119.120:27017"
mongoUser = "Wouter"
mongoPass = "String1!"

    
def saveDictListToMongo(database, collection, dataDict):
    client = MongoClient('mongodb://'+mongoUser+":"+mongoPass+"@"+mongoURL)
    
    db = client[database]
    if collection not in db.list_collection_names():
        db.create_collection(collection)
    collection = db[collection]
    
    #Update records if Id is already present
    for data in dataDict:
        id = data.pop('_id', None)
        if id in collection.distinct('_id'):
            collection.update_one({'_id': id}, {'$set': data})
        else:
            if id is not None:
                data['_id'] = id
            collection.insert_one(data)

    client.close()
    
#Somewhat unrelated usefull functions
def squashDict(nested_dict, parent_key='', sep='_'):
    flattened_dict = {}
    for key, value in nested_dict.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            flattened_dict.update(squashDict(value, new_key, sep))
        else:
            flattened_dict[new_key] = value
    return flattened_dict

def findDiffrenceInStrings(str1, str2):
    min_length = min(len(str1), len(str2))
    for i in range(min_length):
        if str1[i] != str2[i]:
            start = max(0, i - 6)
            end = min(min_length, i + 7)
            differing_chars = str1[start:i] + " <" + str1[i] + "> " + str1[i+1:end]
            print(f"The strings first differ at index {i}.")
            print(f"Surrounding characters: {differing_chars}")
            return i
    return min_length