#--------------------------------------------------------#
#                     Spas Kaloferov                     #
#                   www.kaloferov.com                    #
# bit.ly/The-Twitter      Social     bit.ly/The-LinkedIn #
# bit.ly/The-Gitlab        Git         bit.ly/The-Github #
# bit.ly/The-BSD         License          bit.ly/The-GNU #
#--------------------------------------------------------#

  #
  #       VMware Cloud Assembly ABX Code Sample          
  #
  # [Info] 
  #   - Action posts Cloud Assembly deployment info in a Slack channel via Oauth or Webhook.
  #   - It posts IP Address and Resource Name. 
  #   - Can be tested from within the ABC Action without deployment payload
  # [Inputs]
  #   - actionOptionAcceptPayloadInputIn (Boolean): Can be used to turn off payload inputs and use action inputs to speed up ABX action testing. 
  #      - True: Accept payload inputs. 
  #      - False: Accept only action inputs. Mainly for ABX testing only 
  #         - runOnBlueprintOptionMatchABXIn: see below
  #         - runOnPorpertyMatchABXIn: see below
  #         - slackMsgABXIn: Slack message to be posted
  #   - actionOptionRunOnPropertyIn (Boolean): RunOn custom property condition
  #      - True: Check for runOn condition
  #         - runOnPropertyIn (String): Custom property key/value to match for when actionOptionRunOnPropertyIn=True ( e.g. cloudZoneProp: cas.cloud.zone.type:aws )
  #         - runOnPorpertyMatchABXIn (String): Custom property key/value to match actionOptionRunOnPropertyIn=True and actionOptionAcceptPayloadInputIn=False. For ABX testing. ( e.g. cloudZoneProp: cas.cloud.zone.type:aws )
  #      - False: Do not check for runOn condition
  #   - actionOptionRunOnBlueprintOptionIn (Boolean): RunOn blueprint option condition
  #      - True: Check for runOn condition
  #         - runOnBlueprintOptionIn (String): Blueprint property key/value to match for when actionOptionRunOnBlueprintOptionIn=True (e.g. gitlabSyncEnable: true)
  #         - runOnBlueprintOptionMatchABXIn (String): Blueprint property key/value to match for when actionOptionRunOnBlueprintOptionIn=True and actionOptionAcceptPayloadInputIn=False. For ABX testing. (e.g. gitlabSyncEnable: true)
  #      - False: Do not check for runOn condition
  #   - actionOptionUseAwsSecretsManagerIn (Boolean): Allows use of AWS Secrets Manager for secrets retrieval 
  #      - True: Use AWS Secrets Manager for secrets
  #         - awsSmRegionNameIn (String): AWS Secrets Manager Region Name e.g. us-west-2
  #         - awsSmCspTokenSecretIdIn (String): AWS Secrets Manager CSP Token Secret ID
  #         - awsSmSlackTokenSecretIdIn (String): AWS Secrets Manager Slack Bot Token Secret ID
  #      - False: Use action inputs for secrets
  #         - cspRefreshTokenIn (String): CSP Token
  #   - actionOptionSlackUseOauthIn (Boolean): Select Auth Method. 
  #      - True: Use Oauth. 
  #         - slackTokenIn (String): Slack Bot Token
  #         - slackThreadIn (String): Slack thread
  #         - slackChannelIn (String): Slack channel
  #         - slackParentMessageIn (String): Parent Message value
  #      - False: Use Webhook.
  #         - slackHookIn (String): Slack Hook Url
  #   - slackAttColorIn (String): color value
  #   - slackAttFallbackIn (String): fallback value
  #   - slackAttAuthorIconIn (String): Author icon value (e.g http://gitlab.elasticskyholdings.com/class-delivery/lab-files/raw/master/images/tito-v2-app-icon.png)
  #   - slackAttAuthorLinkIn (String): Author link value (e.g http://gitlab.elasticskyholdings.com/class-delivery/tito)
  #   - slackAttAuthorNameIn (String): Author name value 
  # [Outputs]
  # [Dependency]
  #   - pyyaml, boto3, requests,datetime
  # [Subscription]
  #   - Event Topics: compute.provision.post 
  # [Blueprint Options]
  #   - Supported options: 
  #      - slackPostEnale (Boolean): Enable Slack notification
  #   - For more on blueprint options , visit: Using Blueprint Options in Cloud Assembly (http://kaloferov.com/blog/skkb1051/)
  # [Thanks]
  #

import requests
import json
import yaml 
import urllib3
import datetime
import boto3

# ----- Global ----- # 

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)   # Warned when making an unverified HTTPS request.
urllib3.disable_warnings(urllib3.exceptions.DependencyWarning)   # Warned when an attempt is made to import a module with missing optional dependencies. 
cspBaseApiUrl = "https://api.mgmt.cloud.vmware.com"    # CSP portal base url


# ----- Functions  ----- # 

def handler(context, inputs):   # Function posts to Slack

    fn = "handler -"    # Holds the funciton name. 
    print("[ABX] "+fn+" Action started.")
    print("[ABX] "+fn+" Function started.")
   
    # ----- Action Options ----- #
    
    # General action options
    actionOptionAcceptPayloadInput = inputs['actionOptionAcceptPayloadInputIn'].lower()     
    actionOptionRunOnProperty = inputs['actionOptionRunOnPropertyIn'].lower()   
    actionOptionRunOnBlueprintOption = inputs['actionOptionRunOnBlueprintOptionIn'].lower()
    actionOptionUseAwsSecretsManager = inputs['actionOptionUseAwsSecretsManagerIn'].lower() 
    awsSmCspTokenSecretId = inputs['awsSmCspTokenSecretIdIn']   # TODO: Set in actin inputs if actionOptionUseAwsSecretsManagerIn=True  
    awsSmSlackTokenSecretId = inputs['awsSmSlackTokenSecretIdIn']   # TODO: Set in actin inputs if actionOptionUseAwsSecretsManagerIn=True  
    
    awsSmRegionName = inputs['awsSmRegionNameIn']   # TODO: Set in actin inputs if actionOptionUseAwsSecretsManagerIn=True    
    runOnProperty = inputs['runOnPropertyIn'].replace('"','').lower()   # TODO: Set in actin inputs if actionOptionRunOnPropertyIn=True  
    runOnPorpertyMatch = inputs['runOnPorpertyMatchABXIn'].replace('"','').lower()    # TODO: Set in actin inputs if actionOptionAcceptPayloadInput=False  
    runOnBlueprintOption = inputs['runOnBlueprintOptionIn'].replace('"','').lower()    # TODO: Set in actin inputs if actionOptionRunOnBlueprintOptionIn=True  
    runOnBlueprintOptionMatch = inputs['runOnBlueprintOptionMatchABXIn'].replace('"','').lower()    # TODO: Set in actin inputs if actionOptionAcceptPayloadInput=False  
    cspRefreshToken = inputs['cspRefreshTokenIn']    # TODO: Set in actin inputs if actionOptionUseAwsSecretsManagerIn=False
    blueprintId = ""    # TODO: Used to get the blueprint options   
    eventTopicId = ""   # Event Topic for which the aciton is running
    
    # Integration action options
    actionOptionSlackUseOauth = inputs["actionOptionSlackUseOauthIn"].lower()

    # ----- Inputs ----- #

    # Slack Hook Required inputs:
    slackHook = inputs["slackHookIn"]

    # Slack Oauth Required inputs:
    slackToken = inputs["slackTokenIn"]   
    slackChannel = inputs["slackChannelIn"]   
    slackThread = inputs["slackThreadIn"]   
    slackParentMessage = inputs["slackParentMessageIn"]   
    slackHost = "https://slack.com/api/chat.postMessage"
    
    # Slack general Inputs
    slackUrl = ""   # Slack Post Url
    slackMsg = inputs["slackMsgABXIn"]   
    slackBody = ""   # Slack message body
    slackAttFallback = inputs["slackAttFallbackIn"]   
    slackAttColor = inputs["slackAttColorIn"]   
    slackAttAuthorName = inputs["slackAttAuthorNameIn"]   
    slackAttAuthorLink = inputs["slackAttAuthorLinkIn"]  
    slackAttAuthorIcon = inputs["slackAttAuthorIconIn"]  
    
    # Other Inputs 
    now = datetime.datetime.now()   # Gets Date & time 

    # eventTopicId 
    if (str(inputs).count('compute.provision.post') == 1):
        eventTopicId = "compute.provision.post"
    elif (str(inputs).count("eventTopicId") == 0):
        eventTopicId = "TEST"
    else:
        eventTopicId = "UNSUPPORTED"
    # End Loop
    
    actionInputs = {}  #  build json with the action inputs
    actionInputs['actionOptionAcceptPayloadInput'] = actionOptionAcceptPayloadInput
    actionInputs['actionOptionRunOnProperty'] = actionOptionRunOnProperty
    actionInputs['actionOptionRunOnBlueprintOption'] = actionOptionRunOnBlueprintOption
    actionInputs['actionOptionUseAwsSecretsManager'] = actionOptionUseAwsSecretsManager
    actionInputs['awsSmCspTokenSecretId'] = awsSmCspTokenSecretId 
    actionInputs['awsSmRegionName'] = awsSmRegionName 
    actionInputs['runOnProperty'] = runOnProperty 
    actionInputs['runOnBlueprintOption'] = runOnBlueprintOption
    actionInputs['cspRefreshToken'] = cspRefreshToken
    actionInputs['eventTopicId'] = eventTopicId
    actionInputs['actionOptionSlackUseOauth'] = actionOptionSlackUseOauth
    actionInputs['slackHook'] = slackHook
    actionInputs['slackToken'] = slackToken
    actionInputs['slackChannel'] = slackChannel
    actionInputs['slackThread'] = slackThread
    actionInputs['slackParentMessage'] = slackParentMessage
    actionInputs['slackHost'] = slackHost
    actionInputs['slackUrl'] = slackUrl
    actionInputs['slackBody'] = slackBody
    actionInputs['slackAttFallback'] = slackAttFallback
    actionInputs['slackAttColor'] = slackAttColor
    actionInputs['slackAttAuthorName'] = slackAttAuthorName
    actionInputs['slackAttAuthorLink'] = slackAttAuthorLink
    actionInputs['slackAttAuthorIcon'] = slackAttAuthorIcon
    
    # replace any emptry , optional, "" or '' inputs with empty value 
    for key, value in actionInputs.items(): 
        if (("Optional".lower() in str(value).lower()) or ("empty".lower() in str(value).lower()) or ('""' in str(value).lower())  or ("''" in str(value).lower())):
            actionInputs[key] = ""
        else:
            print('')
    # End Loop
    

    # ----- AWS Secrets Manager  ----- #     
    
    # Get AWS Secrets Manager Secrets
    if (actionInputs['actionOptionUseAwsSecretsManager'] == "true"):
        print("[ABX] "+fn+" Auth/Secrets source: AWS Secrets Manager")
        awsRegionName = awsSmRegionName
        awsSecretId_csp = awsSmCspTokenSecretId
        awsSecretId_slack = awsSmSlackTokenSecretId
        awsSecrets = awsSessionManagerGetSecret (context, inputs, awsSecretId_csp, awsSecretId_slack, awsRegionName)  # Call function
        cspRefreshToken = awsSecrets['awsSecret_csp']
        actionInputs['cspRefreshToken'] = cspRefreshToken
        slackTokenIn = awsSecrets['awsSecret_slack']
        actionInputs['slackTokenIn'] = slackTokenIn
    else:
        # use action inputs
        print("[ABX] "+fn+" Auth/Secrets source: Action Inputs")

    # ----- CSP Token  ----- #     
    
    # Get Token
    getRefreshToken_apiUrl = cspBaseApiUrl + "/iaas/api/login"  # Set API URL
    body = {    # Set call body
        "refreshToken": actionInputs['cspRefreshToken']
    }
    
    print("[ABX] "+fn+" Getting CSP Bearer Token.")
    getRefreshToken_postCall = requests.post(url = getRefreshToken_apiUrl, data=json.dumps(body))   # Call 
    getRefreshToken_responseJson = json.loads(getRefreshToken_postCall.text)    # Get call response
    bearerToken = getRefreshToken_responseJson["token"]   # Set response
    requestsHeaders= {
        'Accept':'application/json',
        'Content-Type':'application/json',
        'Authorization': 'Bearer {}'.format(bearerToken),
        # 'encoding': 'utf-8'
    }
    
    actionInputs['cspBearerToken'] = bearerToken
    actionInputs['cspRequestsHeaders'] = requestsHeaders
    


    if (actionInputs['actionOptionAcceptPayloadInput'] == 'true'):  # Loop. If Payload exists and Accept Payload input action option is set to True , accept payload inputs . Else except action inputs.
        print("[ABX] "+fn+" Using PAYLOAD inputs based on actionOptionAcceptPayloadInputIn action option")

        # blueprintId 
        blueprintId = inputs['blueprintId'] 

        # slackMsg 
        slackMsg = '*Name:* {0} \n *IP Address:* {1} \n *Date:* {2}'.format(inputs["resourceNames"][0], inputs["addresses"][0], now.strftime("%Y-%m-%d %H:%M"))    # Sets the Slack message
        
        # runOn Condition Inputs
        if (actionInputs['eventTopicId'] != "TEST"):
            
            # runOnPorpertyMatch
            if (actionInputs['actionOptionRunOnProperty'] == "true"):    # Loop. Get property to match against. 
                runOnPorpertyMatch = (json.dumps(inputs)).replace('"','').lower()
            else:
                print('')
                # Get value from action inputs
            # End Loop
    
            # runOnBlueprintOptionMatch
            if (actionInputs['actionOptionRunOnBlueprintOption'] == "true"):    # Loop. Get property to match against. 
                print("[ABX] "+fn+" Using BLUEPRINT for blueprintOptions based on actionOptionRunOnBlueprintOptionIn action option")
                print("[ABX] "+fn+" Getting blueprintOptions...")
                body = {}
                resp_blueprintOptions_callUrl = cspBaseApiUrl + '/blueprint/api/blueprints/'+blueprintId+'?$select=*&apiVersion=2019-09-12'
                resp_blueprintOptions_call = requests.get(resp_blueprintOptions_callUrl, data=json.dumps(body), verify=False, headers=(actionInputs['cspRequestsHeaders']))
                #runOnBlueprintOptionMatch = str(json.loads(resp_blueprintOptions_call.text)).lower()
                runOnBlueprintOptionMatch = json.loads(resp_blueprintOptions_call.text)
                runOnBlueprintOptionMatch = yaml.safe_load(runOnBlueprintOptionMatch['content'])   # Get the BP Yaml from the Content
                runOnBlueprintOptionMatch = str(runOnBlueprintOptionMatch['options']).replace("'","").lower()    # Get the options from the BP Yaml
            else:
                print('')
                # Get value from action inputs
            # End Loop
            
        else:
            print('')
            # Get value from action inputs
        # End Loop

    elif (actionInputs['actionOptionAcceptPayloadInput'] == 'false'):
        print("[ABX] "+fn+" Using ACTION inputs for ABX action based on actionOptionAcceptPayloadInputIn action option")
        print("[ABX] "+fn+" Using ACTION inputs for blueprintOptions based on actionOptionRunOnBlueprintOptionIn action option")
        # Get values from action inputs
    else: 
        print("[ABX] "+fn+" INVALID action inputs based on actionOptionAcceptPayloadInputIn action option")
    # End Loop

    actionInputs['blueprintId'] = blueprintId     
    actionInputs['slackMsg'] = slackMsg
    
    actionInputs['runOnPorpertyMatch'] = runOnPorpertyMatch    
    actionInputs['runOnBlueprintOptionMatch'] = runOnBlueprintOptionMatch    


    # Print actionInputs
    for key, value in actionInputs.items(): 
        if (("cspRefreshToken".lower() in str(key).lower()) or ("cspBearerToken".lower() in str(key).lower()) or ("cspRequestsHeaders".lower() in str(key).lower()) or ("runOnPorpertyMatch".lower() in str(key).lower()) or ("runOnBlueprintOptionMatch".lower() in str(key).lower()) or ("slackToken".lower() in str(key).lower())   ):
            print("[ABX] "+fn+" actionInputs[] - "+key+": OMITED")
        else:
            print("[ABX] "+fn+" actionInputs[] - "+key+": "+str(actionInputs[key]))
    # End Loop
    
    # ----- Evals ----- # 
    
    evals = {}  # Holds evals values
    
    # runOnProperty eval
    if ((actionInputs['actionOptionRunOnProperty'] == "true") and (actionInputs['runOnProperty'] in actionInputs['runOnPorpertyMatch'])):   # Loop. RunOn eval.
        runOnProperty_eval = "true"
    elif ((actionInputs['actionOptionRunOnProperty'] == "true") and (actionInputs['runOnProperty'] not in actionInputs['runOnPorpertyMatch'])):
        runOnProperty_eval = "false"
    else:
        runOnProperty_eval = "Not Evaluated"
    # End Loop

    # runOnBlueprintOption  eval
    if ((actionInputs['actionOptionRunOnBlueprintOption'] == 'true') and (actionInputs['runOnBlueprintOption'] in actionInputs['runOnBlueprintOptionMatch'])):     # Loop. RunOn eval.
        runOnBlueprintOption_eval = "true"
    elif ((actionInputs['actionOptionRunOnBlueprintOption'] == 'true') and (actionInputs['runOnBlueprintOption'] not in actionInputs['runOnBlueprintOptionMatch'])):  
        runOnBlueprintOption_eval = "false"
    else:  
        runOnBlueprintOption_eval = "Not Evaluated"
    # End Loop

    evals['runOnProperty_eval'] = runOnProperty_eval.lower()
    print("[ABX] "+fn+" runOnProperty_eval: " + runOnProperty_eval)        
    evals['runOnBlueprintOption_eval'] = runOnBlueprintOption_eval.lower()
    print("[ABX] "+fn+" runOnBlueprintOption_eval: " + runOnBlueprintOption_eval)


    # ----- Function Calls  ----- # 

    if (evals['runOnProperty_eval'] != 'false' and evals['runOnBlueprintOption_eval'] != 'false'): 
        print("[ABX] "+fn+" runOnProperty matched or actionOptionRunOnPropertyIn action option disabled.")
        print("[ABX] "+fn+" runOnBlueprintOption matched or actionOptionRunOnBlueprintOptionIn action option disabled.")
        print("[ABX] "+fn+" Running myActionFunction...")
        resp_myActionFunction = myActionFunction (context, inputs, actionInputs, evals )     # Call function
    else:
        print("[ABX] "+fn+" runOn condition(s) NOT matched. Skipping action run.")
        resp_myActionFunction = ""
     
        
    # ----- Outputs ----- #

    resp_handler = {}   # Set function response 
    resp_handler = evals
    outputs = {   # Set action outputs
       #"actionInputs": actionInputs,
       "resp_handler": resp_handler,
       "resp_myActionFunction": resp_myActionFunction,
    }
    print("[ABX] "+fn+" Function return: \n" + json.dumps(resp_handler))    # Write function responce to console  
    print("[ABX] "+fn+" Function completed.")     
    print("[ABX] "+fn+" Action return: \n" +  json.dumps(outputs))    # Write action output to console     
    print("[ABX] "+fn+" Action completed.")     
    print("[ABX] "+fn+" P.S. Spas Is Awesome !!!")

    return outputs    # Return outputs 


    
    
def myActionFunction (context, inputs, actionInputs, evals):   # Main Function. 
    fn = "myActionFunction -"    # Holds the funciton name. 
    print("[ABX] "+fn+" Action started.")
    print("[ABX] "+fn+" Function started.")
    
    # ----- Script ----- #

    
    # Set URL and Request Headres
    if (actionInputs['actionOptionSlackUseOauth'] == "true".lower()):    # Set Oauth url and headers
        print("[ABX] "+fn+" Using OAuth as per actionOptionSlackUseOauth action input.")
        
        # Set Headers
        requestsHeaders= {  
            'Accept':'application/json',
            'Content-Type':'application/json',
            'Authorization': 'Bearer {}'.format(actionInputs['slackToken']),
            # 'encoding': 'utf-8'
        }
        
        # Set Call body attachments
        bodyOauth = {   
         "channel": actionInputs['slackChannel'], 
         "text": actionInputs['slackParentMessage'],
         "thread_ts": actionInputs['slackThread'],
         "attachments": [
             {
                 "fallback": actionInputs['slackAttFallback'],
                 "color": actionInputs['slackAttColor'],
                 "text" : actionInputs['slackMsg'] ,
                 "author_name": actionInputs['slackAttAuthorName'],
                 "author_link": actionInputs['slackAttAuthorLink'],
                 "author_icon": actionInputs['slackAttAuthorIcon']
             }
         ]
        }
        
        actionInputs['slackRequestsHeaders'] = requestsHeaders   # Request Header to use with Oath
        actionInputs['slackBody'] = bodyOauth   
        actionInputs['slackUrl'] = actionInputs['slackHost']    
    elif (actionInputs['actionOptionSlackUseOauth'] == "false".lower()):    # Set Webhook url and headers
        print("[ABX] "+fn+" Using Webhook as per actionOptionSlackUseOauth action input.")
        
        # Set Call body attachments
        bodyWebhook = {   
         "attachments": [
             {
                 "fallback": actionInputs['slackAttFallback'],
                 "color": actionInputs['slackAttColor'],
                 "text" : actionInputs['slackMsg'] ,
                 "author_name": actionInputs['slackAttAuthorName'],
                 "author_link": actionInputs['slackAttAuthorLink'],
                 "author_icon": actionInputs['slackAttAuthorIcon']
             }
         ]
        }
        
        actionInputs['slackBody'] = bodyWebhook   
        actionInputs['slackRequestsHeaders'] = ""    
        actionInputs['slackUrl'] = actionInputs['slackHook']
    else:
        print("[ABX] "+fn+" Please choose correct value for actionOptionSlackUseOauthIn.")
    # End Loop


    # Call
    print("[ABX] "+fn+" Sending message...")   
    slackPost_resp = requests.post(actionInputs['slackUrl'], data=json.dumps(actionInputs['slackBody']), verify=False, headers=actionInputs['slackRequestsHeaders'])    
    
    
    # ----- Outputs ----- #

    resp_myActionFunction = {}
    resp_myActionFunction = actionInputs['slackMsg']
    
    response = {    # Set action outputs
         "response": resp_myActionFunction,
    }
    print("[ABX] "+fn+" Function return: \n" + json.dumps(response))    # Write function responce to console  
    print("[ABX] "+fn+" Function completed.")   
    
    return response    # Return response 
    # End Function  

def awsSessionManagerGetSecret (context, inputs, awsSecretId_csp, awsSecretId_slack, awsRegionName):  # Retrieves AWS Secrets Manager Secrets
    # Ref: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/secretsmanager.html
    fn = "awsSessionManagerGetSecret -"    # Holds the funciton name. 
    print("[ABX] "+fn+" Function started.")
    
    
    # ----- Script ----- #

    # Create a Secrets Manager client
    print("[ABX] "+fn+" AWS Secrets Manager - Creating session...")
    session = boto3.session.Session()
    sm_client = session.client(
        service_name='secretsmanager',
        region_name=awsRegionName
    )

    # Get Secrets
    print("[ABX] "+fn+" AWS Secrets Manager - Getting secret(s)...")
    resp_awsSecret_csp = sm_client.get_secret_value(
            SecretId=awsSecretId_csp
        )
    resp_awsSecret_slack = sm_client.get_secret_value(
            SecretId=awsSecretId_slack
        )
    
    # Cleanup the response to get just the secret
    awsSecret_csp = json.dumps(resp_awsSecret_csp['SecretString']).replace(awsSecretId_csp,'').replace("\\",'').replace('"{"','').replace('"}"','').replace('":"','')   
    awsSecret_slack = json.dumps(resp_awsSecret_slack['SecretString']).replace(awsSecretId_slack,'').replace("\\",'').replace('"{"','').replace('"}"','').replace('":"','')   

    # ----- Outputs ----- #
    
    response = {   # Set action outputs
        "awsSecret_csp" : str(awsSecret_csp),
        "awsSecret_slack" : str(awsSecret_slack),
        }
    print("[ABX] "+fn+" Function completed.")  
    
    return response    # Return response 
    # End Function  
