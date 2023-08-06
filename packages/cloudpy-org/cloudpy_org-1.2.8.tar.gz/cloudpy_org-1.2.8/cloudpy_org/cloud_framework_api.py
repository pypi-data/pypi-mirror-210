"""
███████████████████████████cloud_framework_api of cloudpy_org███████████████████████████
Copyright © 2023 Cloudpy.org

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
Find documentation at https://www.cloudpy.org
"""
import inspect
import tools
import random
import boto3
import json
import os
xpt = tools.processing_tools()
xs3 = boto3.client('s3')
xpt.environment = "s3"

access_key ="AKIAQCBCZZOOKCRB2SWI"
secret = "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"

#session = boto3.Session(
#    aws_access_key_id=settings.AWS_SERVER_PUBLIC_KEY,
#    aws_secret_access_key=settings.AWS_SERVER_SECRET_KEY,
#)
class aws_framework_manager:
    def __init__(self,secret_pair:list=[]):
        self.__cppt_construction(secret_pair)
        self.cppt.environment = "s3"
        self.general_info = {}
        self.service_name = "cloudpy-org-service-beta"
        self.delimiters = ["pZo-9xH9oEO2B2OEo","2nZzN01wtktk10N","VhMxT-9xVVZzN01w","_Shv-4F86Co981h"]
        self.general_separators = {'user_email_sep': '-0-', '@': '-1-', '.': '-2-'}
        self.special_separators = self.general_separators
        self.__service_initialized = False
        self.__not_initialized_message ='Service not initialized yet.\n'\
        'Use initialize_service(service_token="<your service_token>") function to active the service.\n'\
        'Location: cloudpy_org.cloud_framework_api.aws_framework_manager.initialize_service'
    def __cppt_construction(self,secret_pair:list=[]):
        if len(secret_pair) == 2:
            self.cppt = tools.processing_tools(data=xpt.basic_dicstr_to_dict(xpt.decrypt(secret_pair[0],secret_pair[1])))
        else:
            self.cppt = tools.processing_tools()
    def initialize_service(self,service_token:str,version:float=1.28,test:bool=False):
        error_message = 'Could not initialize the service. Please verify you are using the right service token.'
        try:
            for i in range(0,2):
                self.args_by_key,self.dx = {},{}
                self.__api_encrypted_caller = 'gAAAAABkbtchCJzu1TG2Ap2qvSxyTaBx7q1kuEOsVWoo7bcDZQVNhT_'\
                '4lOxMvo3AKpb6sbf9VNIiCLz4NeSglNgWAAtR-FXNDNavSzyxXAKq7342Rphb1NinG9nbBozYY8SAJmGkZlhSF'\
                'dur391PjRe_TKhrD_5doWvyPsYTa5GhazljtuuNu1U4c4hoc-LMrmRYhFmwVZjVZkK-GciCXdFnW-5qcAJrVRvd'\
                '2q5TnyTKThR64WZ0b4QTkPr8-HNHhSr0ZjwwVp_yRDejMleLeCQUhMI6J5O-_4_jzKrbsBSnLnaguXswGSNA-4xR'\
                'OkTEMfappNO_3qSDWnTMT8oqhVUhM_v750vVelIMgSFOrSkM6-5it-cyUK657B9j_rWDy0Scd4mp5p3x1VYHDic8N'\
                '77DtZFn5xJMxCbgdhwf7ApqhIazR9LkiDJcx8Mb48W07yQRmx8Q8bc4izLGJEG-O7_3G-TXiaJUFaOcGyNsLJcxC4x'\
                'PBSpIeIAfv2kAmzZemdPxaNvAsrajIoX5fTxzH7jxk-txATYN9wJpX0Vl3M0hQPTLXxd2NweRSgcoJZM7Spjt9o95mE'\
                'LbCwbXEi3bESeRCGOJz7HBB4La-mimwWJm0dLusl43u6N5qN_7AAw0lV1WCsZhrI-LWG7hw9OyBpgu5dn7YP9tM94nnR'\
                'YaWNan0Fjc59Dci8ZY9s8cLfR6CDiyHxFHiY9KyiPDrTUH_aU1-O5T62C4tWzcaFbzdgW9-3Bq-czaAXg8WHiehHt7GtK'\
                'oATX1O9vfbRK-GtYZbQ8VH9Q93aVUObgXu7zA4mXJhkBN1ZeU0ziCyzLrwRcpIgPAWFThcztOl7r_5ANnHuwF9f1dH2h5O'\
                'GNVSv0M6pmCrHNuLVD6gy3KGIh-lI2W3mY9C_0b4Z2zr-4jGp8fxnO2yES-41iH8pS_Esvr5h7eaEv50kzi3TU='
                self.__get_dynamic_response(service_token=service_token,version=version,test=test)
                self.find_methods_arguments()
                self.set_valid_characters()
                self.version = self.get_version()
            if self.__service_initialized:   
                return 'Service initialized.'
            else:
                return error_message
        except:
            return error_message
    #___________________________________________________________________
    def load_local_code(self):
        with open(os.getcwd() + "/aws_framework_manager_dynamic_code_0128.json", 'r') as f:
            rslt = json.loads(f.read())
        return rslt
    def __get_dynamic_response(self,service_token:str,version:float,test:bool=False):
        try:
            s3FullFolderPath = "s3://" + self.service_name + "/settings/secrets/"
            enc_key = self.cppt.get_s3_file_content(referenceName="service_key",s3FullFolderPath=s3FullFolderPath)
            m = 'gAAAAABkcBT5Pw2_4O4jZe2RJv-9MCa91rfeRHCbDalo2O4E8wqyAn7YVkuyAv6IZgctEDPwpHBoSTNQdqt15BDCzhRmLg8BK9rxBbinlHd0xSIs-2jbHjk='
            dc = self.cppt.decrypt(self.__api_encrypted_caller,enc_key).replace("@version",str(version))\
            .replace(self.cppt.decrypt(m,enc_key),str(self.__gsm(service_token))).replace("pt.","self.cppt.")
            if test:
                replace_this = "x = self.cppt.get_s3_file_content(referenceName=referenceName,s3FullFolderPath=s3FullFolderPath,exceptionCase=True)"
                with_this = "x = self.load_local_code()"
                dc = dc.replace(self.cppt.decrypt(m,enc_key),str(self.__gsm(service_token)))
                dc = dc.replace(replace_this,with_this)
                if with_this in dc:
                    print("testing dynamic respose..")
            exec(dc)
            self.__service_initialized = True
        except:
            self.__service_initialized = False
    def _decorator(decorator_param):
        def inner_func(self,dk):
            k = dk + "_is_function"
            dc = "self.dx['@k'] = self.dynamic_exec(dynamic_key='@dynamic_key'@these_args)"
            dc = dc.replace("@dynamic_key",dk)\
            .replace("@k",k)\
            .replace("@these_args",self.__args_applied[dk])
            exec(dc)
            is_function = self.dx[k]
            self.dx.pop(k, None)
            rslt = None
            if dk in set(self.dx.keys()):
                if is_function:
                    rslt = self.dx[dk]
                self.dx.pop(dk, None)
            self.reset_args_applied(dk)
            if rslt == None:
                rslt = "Encryption expired."
            return rslt
        return inner_func
    #___________________________________________________________________
    @_decorator
    def deco(self,dk:str):
        ...
    #___________________________________________________________________
    def get_methods(self):
        return {method for method in dir(aws_framework_manager) if method.startswith('_') is False}
    #___________________________________________________________________
    def find_methods_arguments(self):
        self.methods_args,self.__args_applied,dc,x = {},{},"","self.methods_args['@i'] = self.arguments_list(self.@i)\n"
        for i in self.get_methods():
            dc += x.replace("@i",i)
        exec(dc)
        self.reset_args_applied()
    #___________________________________________________________________
    def reset_args_applied(self,only_this_case:str=None):
        if only_this_case != None and only_this_case in set(self.methods_args.keys()):
            x = ""
            for i in self.methods_args[only_this_case]:
                x +=  "," + i + " = @" + i
            self.__args_applied[only_this_case] = x
        else:
            for k,v in self.methods_args.items():
                x = ""
                for i in v:
                    x +=  "," + i + " = @" + i
                self.__args_applied[k] = x
    #___________________________________________________________________
    def arguments_list(self,func):
        return [i for i in func.__code__.co_varnames[:func.__code__.co_argcount] if i != "self"]
    #___________________________________________________________________
    def dynamic_exec(self,dynamic_key:str,**kwargs):
        if self.__service_initialized:
            dk=str(inspect.getframeinfo(inspect.currentframe()).function)
            dc_enc = self.dynamic_code_response[dk]["val"]
            dc = self.cppt.decrypt_before_expiration(dc_enc)
            dc = dc.replace("@dynamic_key",dynamic_key)
            self.args_by_key[dynamic_key] = kwargs
            try:
                exec(dc)
            except Exception as e:
                self.dx[dk] = dc
            return self.dx[dk]
        else:
            return self.__not_initialized_message
    #___________________________________________________________________
    def set_valid_characters(self):
        if self.__service_initialized:
            return self.deco(dk=str(inspect.getframeinfo(inspect.currentframe()).function))
        else:
            return self.__not_initialized_message
    #___________________________________________________________________
    def get_version(self):
        if self.__service_initialized:
            dk=str(inspect.getframeinfo(inspect.currentframe()).function)
            self.__args_applied[dk]= self.__args_applied[dk]
            return self.deco(dk=dk)
        else:
            return self.__not_initialized_message
    #___________________________________________________________________
    def format_folder_or_file_name(self,strInput:str,isFile:bool=False):
        if self.__service_initialized:
            dk=str(inspect.getframeinfo(inspect.currentframe()).function)
            self.__args_applied[dk]= self.__args_applied[dk]\
            .replace("@strInput","'" + strInput + "'")\
            .replace("@isFile",str(isFile))
            return self.deco(dk=dk)
        else:
            return self.__not_initialized_message
    #___________________________________________________________________  
    def create_s3_framework(self,bucket_name:str,region:str="us-east-2"):
        if self.__service_initialized:
            dk=str(inspect.getframeinfo(inspect.currentframe()).function)
            self.__args_applied[dk]= self.__args_applied[dk]\
            .replace("@bucket_name","'" + bucket_name + "'")\
            .replace("@region","'" + region + "'")
            return self.deco(dk=dk)
        else:
            return self.__not_initialized_message
    #___________________________________________________________________
    def create_folder(self,bucket_name:str,folder_name:str,format_folder_or_file_name:bool=False):
        if self.__service_initialized:
            dk=str(inspect.getframeinfo(inspect.currentframe()).function)
            self.__args_applied[dk]= self.__args_applied[dk]\
            .replace("@bucket_name","'" + bucket_name + "'")\
            .replace("@folder_name","'" + folder_name + "'")\
            .replace("@format_folder_or_file_name",str(format_folder_or_file_name))
            return self.deco(dk=dk)
        else:
            return self.__not_initialized_message
    #___________________________________________________________________
    def load_s3_framework(self,bucket_name:str):
        if self.__service_initialized:
            dk=str(inspect.getframeinfo(inspect.currentframe()).function)
            self.__args_applied[dk]= self.__args_applied[dk]\
            .replace("@bucket_name","'" + bucket_name + "'")
            return self.deco(dk=dk)
        else:
            return self.__not_initialized_message
    #___________________________________________________________________
    def create_new_user(self,username:str,email:str,pwd:str,bucket_name:str):
        if self.__service_initialized:
            dk=str(inspect.getframeinfo(inspect.currentframe()).function)
            self.__args_applied[dk]= self.__args_applied[dk]\
            .replace("@username","'" + username + "'")\
            .replace("@email","'" + email + "'")\
            .replace("@pwd","'" + pwd + "'")\
            .replace("@bucket_name","'" + bucket_name + "'")
            return self.deco(dk=dk)
        else:
            return self.__not_initialized_message
    #___________________________________________________________________
    def check_if_user_exists_and_was_confirmed(self,username_or_email:list,bucket_name:str):
        if self.__service_initialized:
            dk=str(inspect.getframeinfo(inspect.currentframe()).function)
            self.__args_applied[dk]= self.__args_applied[dk]\
            .replace("@username_or_email",str(username_or_email))\
            .replace("@bucket_name","'" + bucket_name + "'")
            return self.deco(dk=dk)
        else:
            return self.__not_initialized_message
    #___________________________________________________________________
    def framework_loaded(self,bucket_name:str):
        if self.__service_initialized:
            dk=str(inspect.getframeinfo(inspect.currentframe()).function)
            self.__args_applied[dk]= self.__args_applied[dk]\
            .replace("@bucket_name","'" + bucket_name + "'")
            return self.deco(dk=dk)
        else:
            return self.__not_initialized_message
    #___________________________________________________________________
    def load_user_data(self,username:str,bucket_name:str):
        if self.__service_initialized:
            dk=str(inspect.getframeinfo(inspect.currentframe()).function)
            self.__args_applied[dk]= self.__args_applied[dk]\
            .replace("@username","'" + username + "'")\
            .replace("@bucket_name","'" + bucket_name + "'")
            return self.deco(dk=dk)
        else:
            return self.__not_initialized_message
    #___________________________________________________________________
    def create_token_with_expiration(self,username:str,pwd:str,bucket_name:str,minutes_to_expire:int=10):
        if self.__service_initialized:
            dk=str(inspect.getframeinfo(inspect.currentframe()).function)
            self.__args_applied[dk]= self.__args_applied[dk]\
            .replace("@username","'" + username + "'")\
            .replace("@pwd","'" + pwd + "'")\
            .replace("@bucket_name","'" + bucket_name + "'")\
            .replace("@minutes_to_expire",str(minutes_to_expire))
            return self.deco(dk=dk)
        else:
            return self.__not_initialized_message
    #___________________________________________________________________
    def dictstr_to_dict(self,dictstr:str):
        if self.__service_initialized:
            dk=str(inspect.getframeinfo(inspect.currentframe()).function)
            self.__args_applied[dk]= self.__args_applied[dk]\
            .replace("@dictstr","'''" + dictstr + "'''")
            return self.deco(dk=dk)
        else:
            return self.__not_initialized_message
    #___________________________________________________________________
    def validate_token(self,username:str,token:str,bucket_name:str):
        if self.__service_initialized:
            dk=str(inspect.getframeinfo(inspect.currentframe()).function)
            self.__args_applied[dk]= self.__args_applied[dk]\
            .replace("@username","'" + username + "'")\
            .replace("@token","'" + token + "'")\
            .replace("@bucket_name","'" + bucket_name + "'")
            return self.deco(dk=dk)
        else:
            return self.__not_initialized_message
    
    #*******************************************************************
    
    #___________________________________________________________________
    def get_s3_reference_name(self,username:str,email:str):
        referenceName = username + self.general_separators["user_email_sep"] + email
        for i in {x for x in set(self.general_separators.keys()) if x != "user_email_sep"}:
            referenceName = referenceName.replace(i,self.general_separators[i])
        return referenceName
    #___________________________________________________________________
    def gen_service_token(self,username:str,email:str):
        date_id,time_id = self.cppt.date_time_id()
        n = random.randint(1,100) 
        rslt = self.cppt.encrypt(
            inputStr = str(random.randint(0,10000)) + str(time_id)[::-1] + "-3-cloudpy-org-3-" + self.get_s3_reference_name(username=username,email=email) + "-3-cloudpy-org-3-" + str(date_id) + "_" + str(time_id)
            ,keyStr=self.cppt.get_s3_file_content(referenceName="tek",s3FullFolderPath="s3://" + self.service_name + "/settings/secrets/")[str(n)])
        part1 = rslt[0:int(len(rslt)/2)]
        part2 = rslt.replace(part1,"")
        delimiter = self.delimiters[random.randint(0,3)] 
        rslt = part1 + delimiter + str(n) + delimiter + part2
        return rslt
    #___________________________________________________________________
    def reference_from_service_token(self,service_token:str):
        delimiter,u,error_message = "","-3-cloudpy-org-3-","Invalid service token."
        for i in self.delimiters:
            x = service_token.split(i)
            if len(x) == 3:
                delimiter = i
                break
        if delimiter != "":
            service_token = x[0] + x[2]
            rslt = self.cppt.decrypt(inputStr=service_token,keyStr=self.cppt.get_s3_file_content(referenceName="tek",s3FullFolderPath="s3://" + self.service_name + "/settings/secrets/")[x[1]])
            if u in rslt:
                rslt = rslt.split(u)[1]
            else:
                rslt = error_message
        else:
            rslt = error_message
        return rslt
    #___________________________________________________________________
    def get_service_data(self,service_token:str):
        data = self.cppt.get_s3_file_content(
            referenceName = self.reference_from_service_token(service_token=service_token)
            ,s3FullFolderPath="s3://" + self.service_name + "/settings/secrets/users/")
        del data["encrypted_pwd"]
        del data["token"]
        data["service_token"] = service_token
        return data
    #___________________________________________________________________
    def test_data(self,service_token:str):
        print(self.reference_from_service_token(service_token=service_token))
        print("s3://" + self.service_name + "/settings/secrets/users/")
        return self.cppt.get_s3_file_content(
            referenceName = self.reference_from_service_token(service_token=service_token)
            ,s3FullFolderPath="s3://" + self.service_name + "/settings/secrets/users/")
    
    def __gsm(self,service_token:str):
        det = self.cppt.get_s3_file_content(
            referenceName = self.reference_from_service_token(service_token=service_token)
            ,s3FullFolderPath="s3://" + self.service_name + "/settings/secrets/users/")["service_details"]
        date_id0,time_id0 = self.cppt.date_time_id()
        date_id1 =  det["last_payment_date_id"]
        time_id1 = det["last_payment_time_id"]
        date_id2 =  det["payment_due_date_id"]
        time_id2 = det["payment_due_time_id"]
        minutes_limit = 60*24*60
        fecha_actual_menos_fecha_ultimo_pago = self.cppt.minutes_diff(date_id1,time_id1,date_id0,time_id0)
        fecha_corte_menos_fecha_actual = self.cppt.minutes_diff(date_id0,time_id0,date_id2,time_id2)
        if fecha_actual_menos_fecha_ultimo_pago >= minutes_limit:
            return 0
        else:
            if fecha_corte_menos_fecha_actual >= 0:
                return fecha_corte_menos_fecha_actual
            else:
                return 0
        #___________________________________________________________________
    def xgsm(self,service_token:str):
        return self.__gsm(service_token)
