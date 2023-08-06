"""
███████████████████████████tools of cloudpy_org███████████████████████████
Copyright © 2023 Cloudpy.org

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
Find documentation at https://www.cloudpy.org
"""
import os
import json
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings('ignore')
warnings.simplefilter('ignore')
import pandas as pd
from pandasql import sqldf
import datetime as dt
from datetime import datetime,date
import requests
import boto3
import awswrangler as wr
from tqdm import tqdm
from tqdm import trange

from typing import Union
from botocore.exceptions import ClientError
from cryptography.fernet import Fernet
import numpy as np
import inspect
from os import walk
import s3fs

"""
#pip install PyQt5==5.9.2
plt.scatter(x, y)
plt.plot(myline, mymodel(myline))
plt.show()

"""

class auto_document:
    def __init__(self,processing_tools_instance:object=None):
        if processing_tools_instance == None:
            self.tools = processing_tools()
        else:
            self.tools = processing_tools_instance
        self.load_classes_and_methods()
    #__________________________________________________________________________
    def automatic_documentation(self,module_name_or_invocation:str="", destiny_path:str=None)->None:
        if destiny_path != None:
            if destiny_path[::-1][0:1] == '/' or destiny_path[::-1][0:1] == '\\':
                ...
            elif '\\' in destiny_path:
                destiny_path += '\\'
            elif '/' in destiny_path:
                destiny_path += '/'
            self.tools.documentation_path = destiny_path
        else:
            self.tools.documentation_path = self.tools.local_directory + 'documentation/'
        self.tools.documentation_JSON_path = self.tools.documentation_path + "json/"
        if "from " in module_name_or_invocation or "import " in module_name_or_invocation:
            mod_name = module_name_or_invocation.split("import")[1].replace(' ','')
        else:
            mod_name = module_name_or_invocation
            module_name_or_invocation = "import " + mod_name
        
        dynamic_code = '@module_name_or_invocation\n'\
        'self.pre_gen_automatic_documentation(@mod_name,outputFileName="@mod_name")'
        dynamic_code = dynamic_code.replace("@module_name_or_invocation",module_name_or_invocation).replace("@mod_name",mod_name)
        exec(dynamic_code)
    #__________________________________________________________________________
    def load_classes_and_methods(self)->None:
        '''
        ***
        If classes_and_methods.json already exists in the documentation
        path, it is then being uploaded into the self.classes_and_methods
        instance class as a dict. Otherwhise the self.classes_and_methods dict
        will be by default empty.
        ***
        '''
        self.classes_and_methods = {}
        self.classes_and_methods_path = self.tools.documentation_path + "classes_and_methods.json"
        if os.path.exists(self.classes_and_methods_path):
            with open(self.classes_and_methods_path,'r') as f:
                self.classes_and_methods = json.loads(f.read())
    #__________________________________________________________________________
    def get_methods_and_functions(self,moduleObject:object,className:str)->set:
        '''
        ***
        Given an instance of a class, returns a set of it's availabla methods or functions.
        ***
        '''
        self.temp_methods_and_functions = set()
        dc = 'self.temp_methods_and_functions = '\
        'set([x for x in '\
        'list(dict(inspect.getmembers(moduleObject.' + className + '()'\
        ',predicate=inspect.ismethod)).keys()) '\
        'if len(x.split("__")) == 1])'
        try:
            exec(dc)
        except:
            ...
        return self.temp_methods_and_functions
    #__________________________________________________________________________
    def get_classes_names(self,moduleObject:object,nestLevel:int=0)->set:
        '''
        ***
        Given an instance of a module, returns a set with the names of all the existing classes within it.
        ***
        '''
        objectName = self.tools.retrieve_object_name(moduleObject)
        a = objectName + "."
        raw_set = set([str(x[0]) for x in inspect.getmembers(moduleObject,inspect.isclass) if len(str(x[1]).split('.')) == 2 + nestLevel])
        classes_set = set()
        for cn in raw_set:
            if len(self.get_methods_and_functions(moduleObject,cn)) > 0:
                classes_set.add(cn)
        return classes_set
    #__________________________________________________________________________
    def pre_gen_automatic_documentation(self,moduleOrLibraryInstance:object,onlyThisClassName:str=None,outputFileName:str=None)->None:
        '''
        ***
        Given an instance of a module (moduleOrLibraryInstance parameter), returns a dictionary with relevant information about it in the following format:
         {
             "classA":{
                 "methodOrFunctionA1":{
                     "source_code":"<the source code of the method or function>",
                     "arguments":"<if existing, the arguments of the method or function>"
                     "returns":"<in case is a function, the type of output it returns>"
                     "description":"<any text or description within the method of function source code that is written between acb123*acb123*acb123* and acb123*acb123*acb123*. Example: acb123*acb123*acb123*some description textacb123*acb123*acb123*>"
                     "dependencies": "<the other functions or methods within the same class that depend from this function or method>",
                 "methodOrFunctionA2":{
                     ...
                 }
                 },
            "classB":{
                "methodOrFunctionB1":{
                    ...,
            }
                 }

                }
         }
        Note: If onlyThisClassName argument is different than None, then only that className reference will be in scope as long as it belong to the given module
        ***
        '''

        rslt = {}
        theseClassesSet = set()
        if onlyThisClassName != None:
            theseClassesSet.add(onlyThisClassName)
        else:
            theseClassesSet = self.get_classes_names(moduleOrLibraryInstance)
        for a in theseClassesSet:
            rslt[a] = {}
            for b in self.get_methods_and_functions(moduleOrLibraryInstance,a):
                source_code,arguments,this_returns,description = self.method_or_function_insight(moduleOrLibraryInstance,a,b)
                source_code  = source_code.replace('"','\\"')
                rslt[a][b] = {}
                #rslt[a][b]["source_code"] = source_code
                rslt[a][b]["arguments"] = arguments
                rslt[a][b]["returns"] = this_returns.replace('Union[','').replace(']','')
                rslt[a][b]["description"] = description.replace("acb123*acb123*acb123*","***")
                rslt[a][b]["dependencies"] = self.source_code_dependencies(
                    moduleOrLibraryInstance=moduleOrLibraryInstance
                    ,source_code=source_code)
        if outputFileName == None:
            filename_without_ext = "methods_and_functions"
        else:
            filename_without_ext = outputFileName[::-1].split(".")[0][::-1]
        if not os.path.exists(self.tools.documentation_path):
            os.makedirs(self.tools.documentation_path)
        if not os.path.exists(self.tools.documentation_JSON_path):
            os.makedirs(self.tools.documentation_JSON_path)
        try:
            self.tools.standard_dict_to_json(jsonOrDictionary=rslt
                                             ,fileName=filename_without_ext + ".json"
                                             ,folderPath=self.tools.documentation_JSON_path)
            self.load_classes_and_methods()
            print("Documentation sucessfully created at:\n" + self.tools.documentation_path)
        except Exception as e:
            print(e)
    #__________________________________________________________________________
    def source_code_dependencies(self,moduleOrLibraryInstance:object,source_code:str)->None:
        '''
        ***
        Given a source_code within a module, returns the same module's functions or methods depencies within it.
        ***
        '''
        u = source_code
        classNames = self.get_classes_names(moduleOrLibraryInstance)
        dependencies = {}
        for className in classNames:
            methods_and_functions = self.get_methods_and_functions(moduleOrLibraryInstance,className)
            for x in methods_and_functions:
                y="." + x + "("
                if y in u:
                    if className not in set(dependencies.keys()):
                        dependencies[className] = []
                    if x not in dependencies[className]:
                        dependencies[className].append(x)
        if dependencies == {}:
            return "No dependencies"
        else:
            return dependencies
    #__________________________________________________________________________
    def method_or_function_insight(self,moduleOrLibraryInstance:object,className:str,methodOrFunction:str)->Union[str,dict,str,str]:
        '''
        ***
        Returns source code (st), arguments (dict), type (str) and description (str) of a given method or function name of a given class name.
        ***
        '''
        moduleOrLibraryInstanceName = self.tools.retrieve_object_name(moduleOrLibraryInstance)
        self.theseparams,self.this_source_code,self.this_returns,self.this_description = {},"N/A", "N/A", "N/A"
        dynamic_code='source_code = inspect.getsource('+ moduleOrLibraryInstanceName + '.' + className + "." + methodOrFunction + ')\n'\
        'params = source_code.split("(")[1].split(")")[0].replace("","").replace("self,","").split(",")\n'\
        'if "->" in source_code:\n'\
        '\tself.this_returns = source_code.split("->")[1].split(":")[0].strip()\n'\
        'if "***" in source_code:\n'\
        '\tself.this_description=source_code.split("***")[1].strip()\n'\
        'p={}\n'\
        'for i in range(0,len(params)):\n'\
        '\tj=i+1\n'\
        '\tp[j]={}\n'\
        '\tb=params[i].split(":")\n'\
        '\tp[j]["name"]=b[0].strip()\n'\
        '\tif p[j]["name"]!="self":\n'\
        '\t\tp[j]["datatype"]="N/A"\n'\
        '\t\tif len(b)>1:\n'\
        '\t\t\tif "=" in b[1]:\n'\
        '\t\t\t\tp[j]["datatype"]=b[1].split("=")[0].strip()\n'\
        '\t\t\t\tp[j]["default_value"]=b[1].split("=")[1].strip().replace("\\"","")\n'\
        '\t\t\telse:\n'\
        '\t\t\t\tp[j]["datatype"]=b[1].strip()\n'\
        '\t\t\t\tp[j]["default_value"]="N/A"\n'\
        '\t\t\tif p[j]["default_value"] != "None" and p[j]["datatype"] == "str":\n'\
        '\t\t\t\tp[j]["default_value"]=\"\\"\" + p[j]["default_value\"] + \"\\"\"\n'\
        '\telse:\n'\
        '\t\tp[j]="No parameters."\n'\
        'self.theseparams=p\n'\
        'self.this_source_code=source_code'
        self.this_description = self.this_description.replace("  "," ").replace("#","\n").strip()
        exec(dynamic_code)
        return self.this_source_code, self.theseparams, self.this_returns, self.this_description
    #██████████████████████████████████████████████████████████████████████████          
class processing_tools:
    def __init__(self,data:dict={},bucket_name:str='',region_name:str="us-east-2"):
        self.aux = {}
        self.__tdata = data
        self.environment = 'local'
        self.__set_aws_session(region_name=region_name)
        if self.__session != None:
            self.environment = 's3'
        self.__root_path = os.getcwd()
        self.local_directory = self.__root_path + '/'
        self.s3_bucket = bucket_name.replace('/','') + '/'
        self.main_bucket = ''
        if bucket_name != '':
            self.main_bucket =  's3://' + bucket_name + '/'
            self.environment = bucket_name
        self.documentation_path = self.local_directory + 'documentation/'
        self.documentation_JSON_path = self.documentation_path + "json/"  
        self.settings = self.main_bucket + 'settings/'
        self.secrets = self.settings + 'secrets/'
        self.metadata = self.settings + 'metadata/'
        self.datalake = self.s3_bucket + 'datalake-demo-01/'
        self.hive = self.s3_bucket + 'default_hive/'
        self.dl_crypto = self.datalake + 'crypto/'
        self.dl_crypto_intraday = self.dl_crypto + 'intraday/'
        try:
            self.fs = s3fs.S3FileSystem()
        except:
            self.fs = None
        try:
            self.load_metadata()
        except:
            ...
    #__________________________________________________________________________
    def dataframe_to_parquet(self,df_input:pd.DataFrame,folder_path:str,file_name:str)->str:
        '''
        ***
        If the environment instance class equals "s3", then stores as parquet a given pandas dataframe to a given s3 folder url location under a given file name.
        Otherwise, stores the dataframe locally as a parquet file in the given folder under the given file name.
        ***
        '''
        extension = 'parquet'
        rslt = ""
        file_name = file_name.split(".")[0] + "." + extension
        if "\\" in folder_path:
            if folder_path[::-1][0:1] != "\\":
                folder_path += "\\"  
        elif folder_path[::-1][0:1] != "/":
            folder_path += "/"
        if self.environment == "s3":
            try:
                if self.fs != None:
                    with self.fs.open(folder_path + file_name,'wb') as f:
                        if extension == "parquet":
                            df_input.to_parquet(f)
                            rslt = "Data successfully stored in s3 as: " + folder_path + file_name
                else:
                    rslt = "Could not connect with s3 because AWS CLI credentials have not been set yet."
            except Exception as e:
                rslt = str(e)
                
        else:
            try:
                if extension == "parquet":
                    df_input.to_parquet(folder_path + file_name)
                    rslt = "Data successfully stored locally as: " + folder_path + file_name
            except Exception as e:
                rslt = str(e)
        return rslt
    #__________________________________________________________________________
    def dataframe_to_csv(self,df_input:pd.DataFrame,folder_path:str,file_name:str,sep:str = ',',na_rep:str='',float_format:str = None,index:bool = True,encoding:str = 'utf-8')->str:
        '''
        ***
        If the environment instance class equals "s3", then stores as parquet a given pandas dataframe to a given s3 folder url location under a given file name.
        Otherwise, stores the dataframe locally as a parquet file in the given folder under the given file name.
        ***
        '''
        extension = 'csv'
        rslt = ""
        file_name = file_name.split(".")[0] + "." + extension
        if "\\" in folder_path:
            if folder_path[::-1][0:1] != "\\":
                folder_path += "\\"  
        elif folder_path[::-1][0:1] != "/":
            folder_path += "/"
        if self.environment == "s3":
            try:
                if self.fs != None:
                    with self.fs.open(folder_path + file_name,'wb') as f:
                        if extension == "csv":
                            df_input.to_csv(f,sep=sep,na_rep=na_rep,float_format=float_format,index=index,encoding=encoding)
                            rslt = "Data successfully stored in s3 as: " + folder_path + file_name
                else:
                    rslt = "Could not connect with s3 because AWS CLI credentials have not been set yet."
            except Exception as e:
                rslt = str(e)
                
        else:
            try:
                if extension == "csv":
                    df_input.to_csv(folder_path + file_name,sep=sep,na_rep=na_rep,float_format=float_format,index=index,encoding=encoding)
                    rslt = "Data successfully stored locally as: " + folder_path + file_name
            except Exception as e:
                rslt = str(e)
        return rslt
            
    #__________________________________________________________________________
    def retrieve_object_name(self,objectInput:object)->str:
        '''
        ***
        Retrieves in a str, the name of the object provided.
        ***
        '''
        local_objects = inspect.currentframe().f_back.f_locals.items()
        try:
            return str([x for x, y in local_objects if y is objectInput][0])
        except:
            return ''
    #__________________________________________________________________________
    def gen_enc_key(self)->str:
        '''
        ***
        Generates and returns a random encryption key in str datatype.
        ***
        '''
        return Fernet.generate_key().decode()
    #__________________________________________________________________________
    def encrypt(self,inputStr:str,keyStr:str=None)->str:
        '''
        ***
        Encrypts a given str input and with a given encryption key also in str datatype.
        Returns the encrypted data as str.
        ***
        '''
        return Fernet(keyStr.encode('utf-8')).encrypt(inputStr.encode('utf-8')).decode()
    #__________________________________________________________________________
    def decrypt(self,inputStr:str,keyStr:str=None)->str:
        '''
        ***
        Decrypts a given emctrypted str input and with a given encryption key also in str datatype.
        Return the decrypted data as str.
        ***
        '''
        return Fernet(keyStr.encode('utf-8')).decrypt(inputStr.encode('utf-8')).decode()
    #__________________________________________________________________________
    def __set_aws_session(self,region_name:str="us-east-2")->None:
        '''
        Sets a session with given AWS credentials.
        '''
        self.__session = None
        self.__s3_client = None
        if type(self.__tdata) == dict and self.__tdata != {}:
            spd = self.decrypt_before_expiration(self.__tdata).split("*_xxx_*")
            try:
                self.__session = boto3.Session(aws_access_key_id=spd[0]
                                         ,aws_secret_access_key=spd[1])
                self.__s3_client = boto3.client('s3'
                                                ,aws_access_key_id=spd[0]
                                                ,aws_secret_access_key=spd[1]
                                                ,region_name=region_name)
                print("aws access achieved.")
                spd = []
            except Exception as e:
                print('Error:',str(e))
                self.__session = None
                self.__s3_client = None
            
    #__________________________________________________________________________
    def domain_commands(self,domain_name:str=None)->None:
        '''
        ***
        Prints the terminal commands required to connect to a given domain ubunto instance given the information 
        defined in commands and connection_details json files in metadata folder.
        ***
        '''
        if domain_name != None:
            domain_name = domain_name.lower().strip()
            self.load_metadata()
            strx = ""
            for k,v in self.commands.items():
                for k1,v1 in v.items():
                    if strx != "":
                        strx += "\n"
                    this_command = v1
                    for k2,v2 in self.connection_details[domain_name].items():
                        this_command = this_command.replace("@" + k2, v2)
                    strx += this_command
            output_file = domain_name.replace('.','_') + '.txt'
            with open(output_file,'w') as output_file:
                output_file.write(strx)
                print("output_file:",output_file)
            print(strx)
    #__________________________________________________________________________
    def create_bucket(self,bucket_name:str,region:str="us-east-2")->None:
        '''
        ***
        Creates an s3 bucket with given bucket_name in a given region. If the region is not provided, it's default value "us-east-2" will be choosen.
        ***
        '''
        try:
            if self.__s3_client != None:
                s3_client = self.__s3_client
            else:
                s3_client = boto3.client('s3', region_name=region)
            region_location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name,CreateBucketConfiguration=region_location)
            print("The bucket:",bucket_name, " was succesfully created!")
        except ClientError as e:
            print(e)
    #__________________________________________________________________________
    def store_dict_as_json(self,dictionary_input:dict,writing_path:str)->None:
        '''
        ***
        Locally stores any dict a formatted json file in a giving path.
        ***
        '''
        with open(writing_path,'w') as out_file:
            json.dump(dictionary_input,out_file,sort_keys=False,indent=4)
    #__________________________________________________________________________
    def date_time_id(self)->Union[int,int]:
        '''
        ***
        Returns the current date_id (yyymmdd) and the time_id which is the second of the day (which value is between 0 and 86400). Both outputs are ints.
        ***
        '''
        date_id = int(datetime.now().strftime("%Y%m%d"))
        time_id = int(datetime.now().strftime("%H"))*60*60
        time_id += int(datetime.now().strftime("%M"))*60
        time_id += int(datetime.now().strftime("%S"))
        return date_id,time_id
    #__________________________________________________________________________
    def load_metadata(self,cust_filename:str = None)->None:
        '''
        ***
        Loads all json files within the metadata folder (defined by metadata instance variable) as dict instances variables of the same parent class as
        this function and with the same name, without the extension sufix, than the original files.
        This allows to have metadata dicts directly available.
        If a custom filename is provided (even if we skip to provide the .json extension), then only that file will be loaded as an instance variable as long as 
        it exists and is readable as json.
        ***
        '''
        if self.environment.lower().strip() == 'local':
            #print("self.metadata:",self.metadata)
            all_files_list = self.find_files_in_folder(self.metadata)
            dynamic_code = 'with open(self.metadata + "@json_file.json") as input_file:\n'\
                '\tself.@json_file = json.loads(input_file.read())'
        else:
            all_files_list = self.find_files_in_s3_folder(self.metadata)
            dynamic_code = 'self.@json_file = self.get_s3_file_content("@json_file",self.metadata)'   
        json_files = [f.lower().strip().replace('.json','') for f in all_files_list if f.lower().endswith('.json')]
        if cust_filename != None:
            cust_filename = cust_filename.lower().strip().replace('.json','')
            json_files = [f for f in json_files if f == cust_filename]
        for json_file in json_files:
            this_dynamic_code = dynamic_code.replace('@json_file',json_file)
            exec(this_dynamic_code)
    #__________________________________________________________________________
    def find_files_in_folder(self,path:str=None, extension:str = None)->set:
        '''
        ***
        Returns a set of filenames within a given local folder path. If an extension is specified, only those type of files will be filtered,
        otherwhise all available file names will be considered.
        ***
        '''
        #print("path:",path)
        if path == None:
            path = self.local_directory
        files = [f for f in os.listdir(path)]
        if extension != None:
            files = [f for f in files if f.endswith('.' + extension)]
        return set(files)
    #__________________________________________________________________________ 
    def store_str_as_file_in_s3_folder(self,strInput:str,fileName:str,s3FullFolderPath:str,region_name:str="us-east-2")->None:
        '''
        ***
        Stores a given strInput with a given fileName in a given s3FullFolderPath.
        ***
        '''
        s3FullFolderPath = s3FullFolderPath.replace("s3://","")
        if type(strInput) != str:
            strInput = str(strInput)
        s = s3FullFolderPath
        bucketName=s[0:s.index('/')]
        rp = s.replace(bucketName,'')
        relativePath = rp[1:len(rp)]
        if self.__s3_client != None:
            client = self.__s3_client
        else:
            client = boto3.client('s3', region_name=region_name)
        fileKey = relativePath + fileName
        try:
            client.put_object(Body=strInput,Bucket=bucketName,Key=fileKey)
            print('file successfully stored in:\ns3://' + s3FullFolderPath + fileName)
        except Exception as e:
            print(str(e))
    #__________________________________________________________________________
    def fixed_size_int_to_str(self,intInput:int,size:int)->str:
        '''
        ***
        Transforms a given integer in it's corresponding str of the given size. Example: fixed_size_int_to_str(intInput=95,size=5) will output '00095'. 
        ***
        '''
        rslt = str(intInput)
        while len(rslt) < size:
            rslt = "0" + rslt
        return rslt
    #__________________________________________________________________________
    def standard_dict_to_json(self,jsonOrDictionary:dict,fileName:str,folderPath:str)->None:
        '''
        Stores a given dic as a formatted json file in either an s3 or a local depending on the instance variable self.environment value which can be 'local'
        or 's3'. 
        '''
        fileName = fileName.replace(".json","") + ".json"
        if self.environment.lower().strip() != 'local':
            self.store_str_as_file_in_s3_folder(
                strInput=json.dumps(jsonOrDictionary,sort_keys=False,indent=4)
                ,fileName=fileName
                ,s3FullFolderPath=folderPath)
        else:
            with open(folderPath + fileName, 'w') as f:
                f.write(json.dumps(jsonOrDictionary,sort_keys=False,indent=4))
    #__________________________________________________________________________
    def datetime_id_symbol_path(self,symbol:str,ext:str=None,date_id:int=None)->str:
        '''
        ***
        Returns the relative file path construction that would correspond to given symbol, extension and date_id values.
        ***
        '''
        x,symbol,s3FullPath = '/date_id=',symbol.lower().strip(),self.dl_crypto_intraday
        if date_id == None: 
            date_id,time_id = self.date_time_id()
            s3FullPath += symbol + x + str(date_id) + '/'
            file_name = self.fixed_size_int_to_str(time_id,5) + "." + ext.replace(".","")
            return s3FullPath,file_name
        else:
            s3FullPath += symbol + x + str(date_id) + '/'
            return s3FullPath
    #__________________________________________________________________________
    def seconds_to_timestr(self,time_id:int=0)->str:
        '''
        ***
        Given a time_id (the total of seconds that correspond to a given time of the day), returns the date as a string in the HH:MM:SS format.       
        ***
        '''
        minutes_0 = time_id/(60)
        minutes_1 = int(minutes_0)
        seconds = time_id - minutes_1*60
        hours_0 = minutes_1/60
        hours_1 = int(hours_0)
        minutes_2 = minutes_1 - hours_1*60
        hh = self.fixed_size_int_to_str(hours_1,2)
        mm = self.fixed_size_int_to_str(minutes_2,2)
        ss = self.fixed_size_int_to_str(seconds,2)
        timestr = hh + ':' + mm + ':' + ss
        return timestr
    #__________________________________________________________________________
    def get_s3_file_content(self,referenceName:str,s3FullFolderPath:str,exceptionCase=False)->str:
        '''
        ***
        Returns the content of given s3 file reference name within a given s3 folder location.
        It the file is a json, it´s content is returned as a dict, otherwhise, the content is returned as a str.
        ***
        '''
        rslt_dict,fileContent,ext={},"",""
        if referenceName != "":
            s=s3FullFolderPath.replace('s3://','')
            filesFound=0
            bucketName=s[0:s.index('/')]
            rp=s.replace(bucketName,'')
            relativePath=rp[1:len(rp)]
            if self.__session != None:
                resource = self.__session.resource('s3')
            else:
                resource=boto3.resource('s3')
            my_bucket=resource.Bucket(bucketName)
            objectSumariesList=list(my_bucket.objects.filter(Prefix=relativePath))
            fileKeys=[]
            for obs in objectSumariesList:
                fileKeys.append(obs.key)
            for fileKey in fileKeys:
                a=fileKey[::-1]
                ext='.'+fileKey.lower()[::-1].split('.')[0][::-1]
                thisFile=fileKey.replace(relativePath,'').replace('/','')
                if(thisFile.lower()).replace(ext,'') == referenceName.lower().replace(ext,''):
                    filesFound+=1
                    obj=resource.Object(bucketName,fileKey)
                    fileContent=obj.get()['Body'].read().decode('utf-8')
                    if ext=='.json':
                        if exceptionCase==False:
                            fileContent=fileContent.replace("'",'"')
                        rslt_dict=json.loads(fileContent)
                    break
            if ext=='.json':
                return rslt_dict
            else:
                return fileContent
    #__________________________________________________________________________
    def find_files_in_s3_folder(self,s3FullFolderPath:str)->set:
        '''
        ***
        Return the set of folders and files found inside a given s3 location.
        ***
        '''
        these_files =set()
        s=s3FullFolderPath.replace('s3://','')
        filesFound=0
        bucketName=s[0:s.index('/')]
        rp=s.replace(bucketName,'')
        relativePath=rp[1:len(rp)]
        if self.__session != None:
            resource = self.__session.resource('s3')
        else:
            resource=boto3.resource('s3')
        my_bucket=resource.Bucket(bucketName)
        objectSumariesList=list(my_bucket.objects.filter(Prefix=relativePath))
        fileKeys=[]
        for obs in objectSumariesList:
            fileKeys.append(obs.key)
        for fileKey in fileKeys:
            a=fileKey[::-1]
            ext='.'+fileKey.lower()[::-1].split('.')[0][::-1]
            thisFile=fileKey.replace(relativePath,'').replace('/','')
            these_files.add(thisFile)
        return these_files             

    #__________________________________________________________________________
    def consolidate_staging_data(self,symbol:str,date_id:int)->pd.DataFrame():
        '''
        ***
        Description not available.
        ***
        '''
        symbol = symbol.lower().strip()
        s3FullPath = self.datetime_id_symbol_path(symbol=symbol,date_id=date_id)
        list_of_files = list(self.find_files_in_s3_folder(s3FullPath))
        lx = len(list_of_files)
        if lx > 0:
            rslt = pd.DataFrame()
            print("s3FullPath:\n",s3FullPath)
            message = "Consolidating data for @symbol at @date_id"
            message = message.replace("@symbol",symbol).replace("@date_id",str(date_id))
            
            for i in tqdm(range(lx),desc=message):
                time_id_fileName = list_of_files[i]
                data = self.get_s3_file_content(
                    referenceName = time_id_fileName
                    ,s3FullFolderPath=s3FullPath)
                time_id = int(time_id_fileName.replace(".json",""))
                this_df = self.json_to_df_crypto(symbol,data,date_id,time_id)
                if i > 0:
                    rslt = pd.concat([rslt,this_df])
                else:
                    rslt = this_df
            return rslt
        else:
            print('No files were found in:\n',s3FullPath)
    #__________________________________________________________________________
    def json_to_df_crypto(self,symbol:str,data:dict,date_id:int,time_id:int)->pd.DataFrame():
        '''
        ***
        Description not available.
        ***
        '''
        df = pd.DataFrame(data["Time Series Crypto (5min)"]).transpose()
        df["date"] = df.index
        df['date'] = pd.to_datetime(df['date'])
        df['epoch'] = (df['date'] - dt.datetime(1970,1,1)).dt.total_seconds()
        df['date'] = df['date'].dt.strftime('%d/%m/%Y')
        df['epoch'] = df['epoch'].astype(int)
        df['capture_date_id'] = date_id
        df['capture_date_id'] = df['capture_date_id'].astype(int)
        df['capture_time_id'] = time_id
        df['capture_time_id'] = df['capture_time_id'].astype(int)
        q = """
        select row_number() over(order by a.[epoch] asc) [id],a.* from 
        (select distinct [epoch]
        ,round([1. open],4) [open]
        ,round([2. high],4) [high]
        ,round([3. low],4) [low]
        ,round([4. close],4) [close]
        ,[5. volume] [volume],[date],[capture_date_id],[capture_time_id] from df) a
        order by 1 asc;
        """
        rslt_df = sqldf(q)
        file_name = symbol.lower() + "_" + str(date_id) + "_"+ str(time_id) + ".parquet"
        rslt_df.to_parquet(file_name)
        return rslt_df
    def decrypt_before_expiration(self,data:dict)->str:
        '''
        ***
        Returns the decryption of the "encrypted_content" node of the encrypted_data_with_expiration() output dict as long as it's "keystr_with_expiration" value has not expired.
        ***
        '''
        encrypted_string=data["encrypted_content"]
        exp_seconds,keystr_with_expiration=self.extract_seconds_from_encrypted_input(data["keystr_with_expiration"])
        piece = keystr_with_expiration[0:12]
        spx = keystr_with_expiration.replace(piece,'')[0:14]
        if self.validate_special_phrase(spx,exp_seconds) == True:
            k = piece[::-1] + keystr_with_expiration.replace(spx,'').replace(piece,'')
            a,b = self.date_time_id()
            w = 0
            for i in str(a):
                w+=int(i)
            u = str(w) + '*-*'
            i = -1
            xx = ""
            ol = k.split(u)
            new_keystr = ""
            for o in ol:
                if len(o) > 1:
                    try:
                        intx = int(o[0:2])
                        x = self.alpha_ofuscate(intx)
                        y =  o[2:len(o)]
                        new_piece = x + y
                    except:
                        try:
                            intx = int(o[::-1][0:2][::-1])
                            x = self.alpha_ofuscate(intx)
                            y = o[::-1][2:len(o)][::-1]
                            new_piece = y + x
                        except:
                            new_piece = o
                    new_keystr += new_piece
                else:
                    new_keystr += o 
            return self.decrypt(inputStr=encrypted_string,keyStr=new_keystr)
        else:
            return "encryption expired"
    #__________________________________________________________________________
    def pre_gen_encrypted_data_with_expiration(self,inputStr:str)->dict:
        '''
        ***
        Description not available.
        ***
        '''
        a,b = self.date_time_id()
        timestr = self.seconds_to_timestr(b)
        w = 0
        for i in str(a):
            w+=int(i)
        u = str(w) + '*-*'
        keystr = self.gen_enc_key()
        encryptedStr = self.encrypt(inputStr=inputStr,keyStr=keystr)
        new_keystr = ""
        for k in keystr:
            new_keystr += u + self.alpha_ofuscate(k)
        piece = new_keystr[0:12]
        sp =  self.gen_special_phrase() 
        nkstr = piece[::-1] + sp + new_keystr.replace(piece,'')
        rslt = {}
        rslt["encrypted_content"] = encryptedStr
        rslt["keystr_with_expiration"] = nkstr
        rslt["date_id"] = a
        rslt["timestr"] = timestr
        return rslt
    #__________________________________________________________________________
    def gen_special_phrase(self)->str:
        '''
        ***
        Description not available.
        ***
        '''
        a,b = self.date_time_id()
        c = self.seconds_to_timestr(b)
        special_phrase = str(str(a) + self.fixed_size_int_to_str(b,5))[::-1]
        new_special_phrase = ""
        this_piece = special_phrase[0:8]
        for x in this_piece:
            new_special_phrase += self.alpha_ofuscate(int(x))
        rslt = new_special_phrase + "-" + special_phrase.replace(this_piece,'')
        return rslt
    #__________________________________________________________________________
    def validate_special_phrase(self,phrase:str='',duration_in_secs:int=300)->bool:
        '''
        ***
        Description not available.
        ***
        '''
        rslt_back = ""
        y = phrase.split('-')
        for x in y[0]:
            ix = int(self.alpha_ofuscate(x))
            rslt_back += str(ix)
        rslt_back += y[1]
        a2,b2 = self.date_time_id()
        a1 = int(rslt_back[::-1][0:8])
        b1 = int(rslt_back.replace(str(a1)[::-1],'')[::-1])
        if a1 == a2 and b2-b1 < duration_in_secs:
            return True
        else:
            return False
    #__________________________________________________________________________
    def alpha_ofuscate(self,intOrStrInput:str)->str:
        '''
        ***
        Description not available.
        ***
        '''
        x = ['n','o','p','q','l','b','m','r','s','a','c','d','f','g','h','i','j','t','u','v','w','x','y','e','z','k']
        if type(intOrStrInput) == int:
            return x[intOrStrInput]
        elif type(intOrStrInput) == str:
            rslt = ""
            for i in intOrStrInput:
                if i in x:
                    rslt += self.fixed_size_int_to_str(x.index(i),2)
                else:
                    rslt += i
            return rslt
        else:
            print("Wrong input.")
    #__________________________________________________________________________
    def add_encrypted_seconds(self,strInput:str,seconds:int)->str:
        '''
        ***
        Description not available.
        ***
        '''
        a = strInput[0:7]
        b = strInput[7:len(strInput)]
        keystr =  self.gen_enc_key() 
        encrypted_message = self.encrypt("<*seconds*>" +str(seconds) +"</*seconds*>",keystr) 
        rslt = a+keystr[::-1] + b + "<****>" + encrypted_message
        return rslt
    #__________________________________________________________________________
    def extract_seconds_from_encrypted_input(self,strInput:str)->Union[int,str]:
        '''
        ***
        Description not available.
        ***
        '''
        r = strInput.split("<****>")
        w = r[0]
        m = r[1]
        a = w[0:7]
        b = w[7:len(w)]
        key_reverse = ""
        rslt = -1
        for x in b:
            key_reverse+= x
            try:
                decrypted_seconds = self.decrypt(m,key_reverse[::-1])
                if "<*seconds*>" in decrypted_seconds and "</*seconds*>" in decrypted_seconds:
                    decrypted_seconds = decrypted_seconds.replace("<*seconds*>","").replace("</*seconds*>","")
                    rslt = int(decrypted_seconds)
                    break
            except:
                ...
        return rslt,w.replace(key_reverse,"")
    #__________________________________________________________________________ 
    def gen_encrypted_data_with_expiration(self,original_message:str,minutes_to_expire:int)->dict:
        '''
        ***
        Generates an encrypted dictionary which work as the input of decrypt_before_expiration() function and which
        expires after the minutes_to_expire here provided.
        Once the expiration time has passed, the message won´t be able to be decrypted again.
        The output dict has information about when the encryption took place was created, however the information to validate that is actually encrypted within it, so modifying the "date_id" or "timestr" values has no effect on the expiration time of the "keystr_with_expiration" value. The "date_id" and "timestr" values are only informative and play no effect on the expiration validation. The real time of expiration can't change.
        ***
        '''
        data = {}
        for a in range(100):
            try:
                data = self.pre_gen_encrypted_data_with_expiration(original_message)
                data["keystr_with_expiration"] = self.add_encrypted_seconds(
                    data["keystr_with_expiration"]
                    ,int(minutes_to_expire*60))
                decrypted_message = self.decrypt_before_expiration(data=data)

                break
            except:
                ...
        return data
    #__________________________________________________________________________
    def popsql(self,df_input_name:str,df_output_name:str,column_names:object,action_expression:str,new_column_names:object=None)->pd.DataFrame:
        '''
        ***
        Allows to apply a python expression to a column_name argument. Therefore, the dynamic python code should be provided as string with action over the 
        keyword "@arg". 
        The resultant of the python action can be in the same column(s) or in new ones, defined with the new_columns_name parameter.
        column_names and new_column_names can be str or list depending if the change will apply to a single or multiple columns respectively.
        It simplifies the creation of a user defined function on pandas dataframes.
        ***
        '''
        
        if type(column_names) == str:
            column_names_obj = '"' + column_names + '"'
        else:
            column_names_obj = str(column_names)
        if type(new_column_names) == str:
            new_column_names_obj = '"' + new_column_names + '"'
        else:
            new_column_names_obj = str(new_column_names)   
        dynamyc_code = '@df_output_name = ' + df_input_name + '.copy()\n'\
        'column_names,new_column_names= ' + column_names_obj + ',' + new_column_names_obj + '\n'\
        'if new_column_names == None:\n'\
        '\tnew_column_names = column_names\n'\
        'if type(column_names) == list and type(new_column_names) == list:\n'\
        '\tif len(new_column_names) == len(column_names):\n'\
        '\t\tfor i in range(len(new_column_names)):\n'\
        '\t\t\t@df_output_name[new_column_names[i]] = @df_output_name[column_names[i]].apply(lambda x: pd.Series(@action_expression))\n'\
        'elif type(column_names) == str and type(new_column_names) == str:\n'\
        '\t@df_output_name[new_column_names] = @df_output_name[column_names].apply(lambda x: pd.Series(@action_expression))\n'\
        'else:\n'\
        '\tprint(\'Arguments "column_names" and "new_column_names" can only be str or list and must be of the same type between each other.\')\n'
        dynamyc_code = dynamyc_code.replace('@action_expression',action_expression).replace('@arg','x').replace("@df_output_name",df_output_name)
        return(dynamyc_code)
    #__________________________________________________________________________
    
    def yearmonths_list(self,min_yearmonth:int,max_yearmonth:int=None)->list:
        '''
        ***
        Return a sorted list of all yearmonth between min_yearmonth and max_yearmonth. It max_yearmonth is None or not provided, it will take
        by default the current yearmonth value.
        ***
        '''
        yearmonths = []
        min_good = True
        max_good = True
        try:
            min_month = int(str(min_yearmonth)[::-1][0:2][::-1])
        except:
            min_month = 0
            min_good = False
        try:
            min_year = int(str(min_yearmonth)[0:4])
        except:
            min_year = 1900
            min_good = False
        if  min_good == False:
            min_yearmonth = 0
        if type(min_yearmonth) == int and len(str(min_yearmonth)) == 6 and min_year >= 1900 and min_month > 0 and min_month <= 12:
            yearmonths.append(min_yearmonth)
            if max_yearmonth == None:
                date_id,time_id = self.date_time_id()
                max_yearmonth = int(str(date_id)[0:6])
            try:
                max_month = int(str(max_yearmonth)[::-1][0:2][::-1])
            except:
                max_month = 0
                max_good = False
            try:
                max_year = int(str(max_yearmonth)[0:4])
            except:
                max_year = 1900
                max_good = False
            if max_good == False:
                max_yearmonth = 0
        else:
            print('Invalid min_yearmont input.')
            min_good = False
        if type(max_yearmonth) == int and len(str(max_yearmonth)) == 6 and max_year >= 1900 and max_month > 0 and max_month <= 12:
            this_yearmonth = min_yearmonth
            while this_yearmonth >= min_yearmonth and this_yearmonth < max_yearmonth:
                this_month = int(str(this_yearmonth)[::-1][0:2][::-1])
                this_year = int(str(this_yearmonth)[0:4])
                if this_month < 12:
                    this_yearmonth = int(str(this_year) + self.fixed_size_int_to_str(this_month + 1,2))
                    this_month += 1
                else:
                    this_month = 1
                    this_yearmonth = int(str(this_year + 1) + self.fixed_size_int_to_str(this_month,2))
                if this_yearmonth not in yearmonths:
                    yearmonths.append(this_yearmonth)
            if max_yearmonth not in yearmonths and max_yearmonth > min_yearmonth:
                yearmonths.append(max_yearmonth)
            yearmonths.sort()
            if max_yearmonth < min_yearmonth:
                print('If max_yearmonth is not provided, it will be current yearmonth by default. Otherwise it must be greater or equal than min_yearmonth.')
        elif min_good == True:
            print('Invalid max_yearmonth input.')
        return yearmonths
    #__________________________________________________________________________
    
    def clean_file_name(self,file_name:str,date_id_label:bool=False,time_id_label:bool=False)->str:
        '''
        ***
        Given a file name, returns a clean, lower case, trimmed version of it, with optional date_id and or time_id labels.
        ***
        '''
        ext = file_name[::-1].split('.')[0][::-1].lower().replace(' ','')
        file_name = file_name.lower().strip().replace(' ','_').replace('.' + ext,'')
        if date_id_label or time_id_label:
            date_id,time_id = self.date_time_id()
            if date_id_label:
                file_name += '_' + str(date_id)
            if time_id_label:
                file_name += '_' + self.fixed_size_int_to_str(time_id,5)
        file_name += '.' + ext
        return file_name
    #__________________________________________________________________________
    
    def clean_filepath(self,file_name:str,folder_path:str=None,date_id_label:bool=False,time_id_label:bool=False)->str:
        '''
        ***
        Given a file name, and folder location returns a clean, lower case, trimmed version of it, with optional date_id and or time_id labels.
        If not folder path is specified, then the local path of the location where the cloudpy_org module is called will be displayed along with the clean file name.
        ***
        '''
        if folder_path == None:
            folder_path = self.__root_path
        file_name = self.clean_file_name(
            file_name=file_name
            ,date_id_label=date_id_label
            ,time_id_label=time_id_label)
        x = ''
        if len(folder_path) > 1 and folder_path[::-1][0] not in ['/','\\']:
            x = '/'
            if '\\' in folder_path:
                x = '\\'
        file_path = folder_path + x + file_name
        return file_path
    #__________________________________________________________________________
    def split_date_id(self,date_id:int):
        date_idstr = str(date_id)
        return int(date_idstr[0:4]),int(date_idstr[4:6]),int(date_idstr[6:8])
    #__________________________________________________________________________
    def minutes_diff(self,date_ida,time_ida,date_idb,time_idb)->int:
        ya,ma,da = self.split_date_id(date_ida)
        yb,mb,db = self.split_date_id(date_idb)
        xa = date(ya, ma, da)
        xb = date(yb, mb, db)
        delta_b_a = xb - xa
        days_b_a = delta_b_a.days
        minutes_b_a = days_b_a*24*60 + ((time_idb - time_ida)/60) + 1
        minutes_b_a = int(minutes_b_a)
        return minutes_b_a
    #__________________________________________________________________________
    def save_s3_plain_content_locally(self
                                      ,referenceName:str
                                      ,s3FullFolderPath:str
                                      ,destinyFileName:str = None
                                      ,destinyFolderPath:str = None
                                      ,exceptionCase:bool = False
                                     )->None:
        referenceName = referenceName.split(".")[0]
        if destinyFolderPath == None:
            destinyFolderPath = self.local_directory
        content = self.get_s3_file_content(referenceName,s3FullFolderPath,exceptionCase=exceptionCase)
        ext = "txt"
        if type(content) == dict:
            ext = ".json"
        if destinyFileName == None:
            destinyFileName = referenceName + ext
        if ext == ".json":
            self.store_dict_as_json(dictionary_input=content,writing_path=destinyFolderPath+destinyFileName)
        else:
            with open(destinyFolderPath+destinyFileName,'w') as f:
                f.write(content)
    #__________________________________________________________________________
    def basic_dicstr_to_dict(self,dictstr:str)->dict:
        date_id,time_id = self.date_time_id()
        keyname = str(date_id) + "_" + str(time_id)
        self.aux[keyname] = {}
        dc = "self.aux['@keyname'] = " + dictstr
        dc = dc.replace("@keyname",keyname)
        exec(dc)
        rslt = self.aux[keyname] 
        self.aux.pop(keyname, None)
        return rslt 