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
  #   - requests,datetime
  # [Subscription]
  #   - Event Topics:
  #      - compute.provision.post  
  # [Thanks]
  #

import requests
import json
import datetime

# ----- Global ----- # 
# ----- Functions  ----- # 

def handler(context, inputs):   # Function posts to Slack

    fn = "handler -"    # Holds the funciton name. 
    print("[ABX] "+fn+" Action started.")
    print("[ABX] "+fn+" Function started.")
   
    # ----- Actin Options ----- #

    actionOptionSlackUseOauth = inputs["actionOptionSlackUseOauthIn"].lower()
    
    # ----- Inputs ----- #
    
    # Hook Required inputs:
    slackHook = inputs["slackHookIn"]

    # Oauth Required inputs:
    slackToken = inputs["slackTokenIn"]   
    slackChannel = inputs["slackChannelIn"]   
    slackThread = inputs["slackThreadIn"]   
    slackParentMessage = inputs["slackParentMessageIn"]   
    slackHost = "https://slack.com/api/chat.postMessage"
    
    # General Inputs
    now = datetime.datetime.now()   # Gets Date & time 
    slackUrl = ""   # Slack Post Url
    slackBody = ""   # Slack message body
    slackAttFallback = inputs["slackAttFallbackIn"]   
    slackAttColor = inputs["slackAttColorIn"]   
    slackAttAuthorName = inputs["slackAttAuthorNameIn"]   
    slackAttAuthorLink = inputs["slackAttAuthorLinkIn"]  
    slackAttAuthorIcon = inputs["slackAttAuthorIconIn"]  
    
    actionInputs = {}
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
        if (("Optional".lower() in value.lower()) or ("empty".lower() in value.lower()) or ('""'.lower() in value.lower())  or ("''".lower() in value.lower())):
            actionInputs[key] = ""
        else:
            print('')
    # End Loop


    # Set Slack message
    if ( (str(inputs).count("resourceNames") != 0) and (str(inputs).count("addresses") != 0) ):
        slackMsg = '*Name:* {0} \n *IP Address:* {1} \n *Date:* {2}'.format(inputs["resourceNames"][0], inputs["addresses"][0], now.strftime("%Y-%m-%d %H:%M"))    # Sets the Slack message
    else:
        slackMsg = "No Deployment Payload, but <http://www.kaloferov.com/|Spas Is Awsome>"

    actionInputs['slackMsg'] = slackMsg     # Slack message


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
        
        actionInputs['requestsHeaders'] = requestsHeaders   # Request Header to use with Oath
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
        actionInputs['requestsHeaders'] = ""    
        actionInputs['slackUrl'] = actionInputs['slackHook']
    else:
        print("[ABX] "+fn+" Please choose correct value for actionOptionSlackUseOauthIn.")
    # End Loop


    # ----- Script ----- #

    # Call
    print("[ABX] "+fn+" Sending message...")   
    requests.post(actionInputs['slackUrl'], data=json.dumps(actionInputs['slackBody']), verify=False,headers=actionInputs['requestsHeaders'])    
    
    
    # ----- Outputs ----- #
    
    response = {   # Set action outputs
         "slackMsg" : actionInputs['slackMsg']
         }
         
    print("[ABX] "+fn+" Function completed.")   
    print("[ABX] "+fn+" Action completed.")     
    print("[ABX] "+fn+" P.S. Spas Is Awesome !!!")
   
    return response    # Return response 
    # End Function    

