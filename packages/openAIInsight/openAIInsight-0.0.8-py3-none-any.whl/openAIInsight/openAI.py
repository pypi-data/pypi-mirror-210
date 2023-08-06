import requests, json, traceback, openai
from flask import request
import loggerutility as logger
import commonutility as common
import os

class openAI:
    def getCompletionEndpoint(self):
        try:
            jsonData = request.get_data('jsonData', None)
            jsonData = json.loads(jsonData[9:])
            logger.log(f"\njsonData openAI class::: {jsonData}","0")

            licenseKey      = jsonData['license_key']
            insightInput    = jsonData['insight_input']
            enterpriseName  = jsonData['enterprise']     
            fileName        = enterpriseName + "_insightData.txt"
            openai.api_key  = licenseKey
            
            logger.log(f"\n\njsonData openAI class fileName::: \t{fileName}\n","0")
            
            if os.path.exists(fileName):
                openAI_trainingData = open(fileName,"r").read()
            else:
                openAI_trainingData = open("insightData.txt","r").read()
            
            # response = openai.Completion.create(
            # model="code-davinci-001",
            # prompt= openAI_trainingData + insightInput,
            # temperature=0.25,
            # max_tokens=198,
            # top_p=0.5,
            # frequency_penalty=0,
            # presence_penalty=0,
            # stop=["\n"]
            # )

            # logger.log(f"Response openAI completion endpoint::::: {response}","0")
            # finalResult=str(response["choices"][0]["text"])
            # logger.log(f"OpenAI completion endpoint finalResult ::::: {finalResult}","0")
            # return finalResult
        
            logger.log(f"\n\nopenAI_trainingData before conversion :::::: {type(openAI_trainingData)} \n{openAI_trainingData}\n","0")
            openAI_trainingData = openAI_trainingData.replace("<insight_input>", insightInput)
            logger.log(f"\n\nopenAI_trainingData after replacing <insight_input> :::::: \n{openAI_trainingData} \n{type(openAI_trainingData)}","0")
            messageList = json.loads(openAI_trainingData)
            logger.log(f"\n\nmessageList after conversion :::::: {messageList} \n{type(messageList)}","0")
            
            logger.log(f"\n\nfinal messageList :::::: {messageList}","0")

            response = openai.ChatCompletion.create(
                                                        model="gpt-3.5-turbo",
                                                        messages= messageList,
                                                        temperature=0.25,
                                                        max_tokens=350,
                                                        top_p=0.5,
                                                        frequency_penalty=0,
                                                        presence_penalty=0,
                                                        )
            logger.log(f"\n\nResponse openAI ChatCompletion endpoint::::: {response} \n{type(response)}","0")
            finalResult=str(response["choices"][0]["message"]["content"])
            logger.log(f"\n\nOpenAI ChatCompletion endpoint finalResult ::::: {finalResult} \n{type(finalResult)}","0")
            return finalResult
        
        except Exception as e:
            logger.log(f'\n In getCompletionEndpoint exception stacktrace : ', "1")
            trace = traceback.format_exc()
            descr = str(e)
            returnErr = common.getErrorXml(descr, trace)
            logger.log(f'\n Print exception returnSring inside getCompletionEndpoint : {returnErr}', "0")
            return str(returnErr)
        

