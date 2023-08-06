import json
import openai
import pinecone
import datetime
import traceback
import pandas as pd
from flask import request
import loggerutility as logger
import commonutility as common
from openai.embeddings_utils import get_embedding, get_embeddings, cosine_similarity


class OpenAI_PineConeVector:
    
    index_name      =   "" 
    openAI_apiKey   =   "" 
    pineCone_apiKey =   "" 
    queryList       =   "" 
    dfJson          =   ""
    engineName      =   "text-embedding-ada-002" # Model that we want to use 
    dimensions      =   1536
    my_index        =   ""
    enterpriseName  =   ""

    def trainData(self, pineCone_json):
        # When calling from process definition, we need to pass hard-coded openAI_apiKey & pineCone_apiKey.
        try:
            
            logger.log("inside PineConeVector class trainData()","0")
            
            if "openAI_apiKey" in pineCone_json and pineCone_json["openAI_apiKey"] != None:
                self.openAI_apiKey = pineCone_json["openAI_apiKey"]           
                logger.log(f"\ntrain_PineConeVector openAI_apiKey:::\t{self.openAI_apiKey} \t{type(self.openAI_apiKey)}","0")
            
            if "pineCone_apiKey" in pineCone_json and pineCone_json["pineCone_apiKey"] != None:
                self.pineCone_apiKey = pineCone_json["pineCone_apiKey"]           
                logger.log(f"\ntrain_PineConeVector pineCone_apiKey:::\t{self.pineCone_apiKey} \t{type(self.pineCone_apiKey)}","0")

            if "index_name" in pineCone_json and pineCone_json["index_name"] != None:
                self.index_name = pineCone_json["index_name"]
                logger.log(f"\ntrain_PineConeVector index_name:::\t{self.index_name} \t{type(self.index_name)}","0")
            
            if "dfJson" in pineCone_json and pineCone_json["dfJson"] != None:
                self.dfJson = pineCone_json["dfJson"]
                logger.log(f"\ntrain_PineConeVector dfJson:::\t{self.dfJson} \t{type(self.dfJson)}","0")
            
            if "trainData" in pineCone_json and pineCone_json["trainData"] != None:
                self.dfJson = pineCone_json["trainData"]
                logger.log(f"\ntrain_PineConeVector trainData:::\t{self.trainData} \t{type(self.trainData)}","0")

            if "enterprise" in pineCone_json and pineCone_json["enterprise"] != None:
                self.enterpriseName = pineCone_json["enterprise"]
                logger.log(f"\nPineConeVector class LookUpData() enterprise:::\t{self.enterpriseName} \t{type(self.enterpriseName)}","0")

            logger.log(f"\nPineConeVector class trainData() all Parameters:::  \n{locals()}\n","0")
            
            parsed_json = (json.loads( self.dfJson))
            df = pd.DataFrame(parsed_json[1:])
            
            pinecone.init(api_key=self.pineCone_apiKey, environment='us-west4-gcp')
            openai.api_key = self.openAI_apiKey                 

            logger.log(f"Pinecone Available indexes List  :: \t {pinecone.list_indexes()}", "0")    
            # Creating index
            if self.index_name not in pinecone.list_indexes():
                logger.log(f" '{self.index_name}' index not present. Creating New!!!", "0")
                pinecone.create_index(name = self.index_name, dimension=self.dimensions, metric='cosine')
            else:
                logger.log(f" '{self.index_name}' index is present. Loading now!!!", "0")
                self.my_index = pinecone.Index(index_name=self.index_name)
                
            logger.log(f"Pinecone Available indexes List  :: \t {pinecone.list_indexes()}", "0")    

            df.columns = ['_'.join(column.lower().split(' ')) for column in df.columns]
            df.fillna("N/A",inplace=True)
            #Changing column names to lowercase and replacing nan values with a string placeholder
            df.columns = ['_'.join(column.lower().split(' ')) for column in df.columns]
            df.fillna("N/A",inplace=True)
            
            df['enterprise'] = self.enterpriseName
            
            if self.index_name == "item":
                logger.log(f"\ntrain_PineConeVector df.head() line 84:: {df.head()},\n {df.head()}", "0")    
                df.columns = ['id', 'material_description', 'product', 'delivery_method', 'strength', 'size', 'enterprise']
                logger.log(f"\ntrain_PineConeVector df.head() line 86:: {df.head()},\n {df.head()}", "0")    
                df['embedding'] = get_embeddings(df['material_description'].to_list(), engine=self.engineName)
                metadata = df[['material_description', 'product', 'delivery_method', 'strength', 'size', 'enterprise']].to_dict(orient='records')
            
            elif self.index_name == "document":
                df['embedding'] = get_embeddings(df['description'].to_list(), engine=self.engineName)
                metadata = df[['description','enterprise']].to_dict(orient='records')

            else:
                logger.log(f"\n\n INVALID INDEX NAME ::: \t{self.index_name}\n", "0")    
            
            logger.log(f"\ntrain_PineConeVector df.head() line 96 :: {df.head()},\n {df.head()}", "0")    
            upsert = list(zip(df['id'], df['embedding'], metadata))
            _ = self.my_index.upsert(vectors=upsert)
            logger.log(f"{self.my_index.describe_index_stats()}","0")

            logger.log(f"\nOpenAI_PineConeVector class trainData:::\t{self.my_index}","0")

            if self.my_index != "":
                return f" '{self.index_name}' Index Creation successful. "
            else:
                return f" '{self.index_name}' Index Creation failed. "
            
            
        except Exception as e:
            logger.log(f"OpenAI_PineConeVector class trainData() Issue::: \n{e}","0")
            trace = traceback.format_exc()
            descr = str(e)
            errorXml = common.getErrorXml(descr, trace)
            logger.log(f'\n OpenAI_PineConeVector class trainData() errorXml::: \n{errorXml}', "0")
            raise str(errorXml)

    def getLookupData(self):               
        try:
            
            logger.log("inside PineConeVector class LookUpData()","0")
            logger.log(f"\nPineConeVector class LookUpData() all Parameters:::  \n{locals()}\n","0")
            result      = []
            id_list     = []
            finalResult = ""
            pineCone_json =  request.get_data('jsonData', None)
            logger.log(f"\nPineConeVector class LookUpData() pineCone_json raw:::\t{pineCone_json} \t{type(pineCone_json)}","0")
            pineCone_json = json.loads(pineCone_json[9:])
            logger.log(f"\nPineConeVector class trainData() pineCone_json:::\t{pineCone_json} \t{type(pineCone_json)}","0")

            if "openAI_apiKey" in pineCone_json and pineCone_json["openAI_apiKey"] != None:
                self.openAI_apiKey = pineCone_json["openAI_apiKey"]          
                logger.log(f"\nPineConeVector class LookUpData() openAI_apiKey:::\t{self.openAI_apiKey} \t{type(self.openAI_apiKey)}","0")
                openai.api_key = self.openAI_apiKey                 

            if "pineCone_apiKey" in pineCone_json and pineCone_json["pineCone_apiKey"] != None:
                self.pineCone_apiKey = pineCone_json["pineCone_apiKey"]           
                logger.log(f"\nPineConeVector class LookUpData() pineCone_apiKey:::\t{self.pineCone_apiKey} \t{type(self.pineCone_apiKey)}","0")

            if "index_name" in pineCone_json and pineCone_json["index_name"] != None:
                self.index_name = pineCone_json["index_name"]
                logger.log(f"\nPineConeVector class LookUpData() index_name:::\t{self.index_name} \t{type(self.index_name)}","0")
            
            if "queryList" in pineCone_json and pineCone_json["queryList"] != None:
                self.queryList = pineCone_json["queryList"]
                logger.log(f"\nPineConeVector class LookUpData() queryList:::\t{self.queryList} \t{type(self.queryList)}","0")
            
            if "enterprise" in pineCone_json and pineCone_json["enterprise"] != None:
                self.enterpriseName = pineCone_json["enterprise"]
                logger.log(f"\nPineConeVector class LookUpData() enterprise:::\t{self.enterpriseName} \t{type(self.enterpriseName)}","0")

            openai.api_key  =  self.openAI_apiKey         
            pinecone.init(api_key=self.pineCone_apiKey, environment='us-west4-gcp')
            
            pinecone_IndexList = pinecone.list_indexes()
            
            if self.index_name in pinecone_IndexList:
                self.my_index = pinecone.Index(index_name=self.index_name)
                logger.log(f"self.my_index::: {self.my_index}","0")
                logger.log(f"Pinecone execution START Time::: {datetime.datetime.now().strftime('%H:%M:%S')}","0")
                for query in self.queryList:
                    if query != "" and query != None:
                        if self.index_name == 'item':
                            result.append(self.my_index.query(vector=get_embedding(query, engine=self.engineName),filter={"enterprise": self.enterpriseName},top_k=1, include_metadata=True))
                        else:
                            pineConeResponse = self.my_index.query(vector=get_embedding(query, engine=self.engineName),filter={"enterprise": self.enterpriseName},top_k=10, include_metadata=True)
                            result.append(pineConeResponse)

                logger.log(f"Pinecone execution END Time::: {datetime.datetime.now().strftime('%H:%M:%S')}","0")
                logger.log(f"OpenAI_PineConeVector class getLookUP() Response::: \n{result}\tlen::: {len(result)}\t{type(result)}", "0")
                
                # filtering response 
                if len(result[0]['matches']) > 0:
                    if self.index_name == 'item':
                        id_list = [element["matches"][0]["id"] for element in result]
                        IdDescription_dict = dict(zip(self.queryList, id_list))
                        finalResult = IdDescription_dict
                        logger.log(f"\n\nOpenAI_PineConeVector class getLookUP() 'ITEM' Index IdDescription_dict::: \n{finalResult}\tlen::: {len(finalResult)}\t{type(finalResult)}", "0")
                    else :
                        logger.log(f"\n\nOpenAI_PineConeVector class getLookUP() 'DOCUMENT' Index result::: \n{result}\tlen::: {len(result)}\t{type(result)}", "0")
                        for query in self.queryList:
                            for matchJson in result:
                                # logger.log(f"\n\nOpenAI_PineConeVector class getLookUP() 'DOCUMENT' Index matchJson::: \n{matchJson}\t{type(matchJson)}", "0")
                                for j in matchJson['matches']:
                                    # logger.log(f"\n\nOpenAI_PineConeVector class getLookUP() 'DOCUMENT' Index j::: \n{j}\t{type(j)}", "0")
                                    if j['score']  >= 0.75 and query in j['metadata']['description']:
                                        id_list = [k['id'] for k in matchJson['matches']]
                        logger.log(f"\n\nOpenAI_PineConeVector class getLookUP() 'DOCUMENT' Index id_list::: \n{id_list}\t\t{type(id_list)}", "0")
                        finalResult = id_list
                    return str(finalResult)
            
            else:
                logger.log(f"OpenAI_PineConeVector class getLookUP()::: \nIndex_Name: {self.index_name} not found in pinecone_IndexList: {pinecone_IndexList}","0")
                message = f"Index_Name: '{self.index_name}' not found in pinecone_IndexList: {pinecone_IndexList}"
                errorXml = common.getErrorXml(message, "")
                raise Exception(errorXml)
            
        except Exception as e:
            logger.log(f"OpenAI_PineConeVector class getLookUP() Issue::: \n{e}","0")
            trace = traceback.format_exc()
            descr = str(e)
            errorXml = common.getErrorXml(descr, trace)
            logger.log(f'\n OpenAI_PineConeVector class getLookUP() errorXml::: \n{errorXml}', "0")
            raise str(errorXml)
