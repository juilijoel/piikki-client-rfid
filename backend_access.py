import json
import requests

class backend_access:
    def __init__(self, backend_address, default_header):
        self.backend_address = backend_address
        self.default_header = default_header

    def authenticate(self, username, password):
        #Authenticate user against backend
        payload = {"username" : username, "password": password}
        r = requests.post(self.backend_address+'/users/authenticate', headers=self.default_header,  json = payload)
        json_data = json.loads(r.text)

        try:
            if json_data["result"]["authenticated"] == True:
                print("User authenticated!")
                return True
            else:
                print("User authentication failed!")
                return False
        except:
            print("User authentication failed!")
            return False
                
    def userInGroup(self, username):
        #Check if user exists in group
        r = requests.get(self.backend_address+'/group/members/'+username, headers=self.default_header)
        json_data = json.loads(r.text)

        try:                
            if json_data["result"]["username"] == username:
                print("User found from group!")
                return True
            else:
                print("User not found from group!")
                return False
        except:
            print("User not found from group!")
            return False

    def doTransaction(self, username, amount):
        payload = {"username":username,"amount":amount}
        r = requests.post(self.backend_address+'/transaction', headers=self.default_header, json=payload)
        json_data = json.loads(r.text)
        return json_data["result"][0]["saldo"]