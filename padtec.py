import requests
import re

class Padtec():
    def __init__(self):
        self.url = 'URL padtec'
        self.username = 'username'
        self.password = 'password'
        self.headers = {"Authorization": self.__getToken()}

    def __getToken(self):
        token = requests.post("http://10.33.14.134/api/auth/login/", json={
            "username": self.username,
            "password": self.password
        })
        return token.json()["token"]

    def __getAllOPS(self):
        boards = []
        for board in requests.get(self.url+'/api/board/inventory?metadata=false&page=1&per_page=100&advanced_filters[]=[%7B%22field_name%22:%22model%22,%22selected_values%22:[%7B%22value%22:%22OPS%22,%22condition%22:%22contains%22%7D]%7D]&alarms=0', headers=self.headers).json()['results']['records']:
            boards.append({'name':board[0],'type':board[1],'part':board[3],'serial':board[4],'description':board[11]})
        return boards
    
    def __getAllOPSInfo(self):
        allOPSInfo = []
        for board in self.__getAllOPS():
            try:
                allOPSInfo.append(requests.get('http://10.33.14.134/card/card/'+str(board['part'])+'-'+str(board['serial']), headers=self.headers).json())
            except:
                pass
        return allOPSInfo
    
    def findErrors(self):
        exceptions = ['OPS-HB#905','OPS-HA#695','OPS-HB#906','OPS-HB#914', 'OPS-HA#718->TF100G STS']
        errors = []
        errors_final = []
        x = 0
        for data in self.__getAllOPSInfo():
            if re.findall('RED',str(data['state']['leds'])):
                states_all = []
                if data['state']['leds']['protection1'] == 'RED':
                    states_all.append('p1')
                if data['state']['leds']['protection2'] == 'RED':
                    states_all.append('p2')
                if data['state']['leds']['working1'] == 'RED':
                    states_all.append('w1')
                if data['state']['leds']['working2'] == 'RED':
                    states_all.append('w2')
                errors.append({"ponta":data['state']['location'],"name":data['state']['name'],"desc":data['state']['desc'],"alarms":states_all})
        
        while x < len(errors):
            state = False
            for exception in exceptions:
                if exception == errors[x]['name']:
                    state = True
                    break
            if state == False:
                    errors_final.append(errors[x])
            x = x+1
            
        return {"ops_errors":errors_final}
    
    def getAlarms(self, endpoint):
        return requests.get(self.url+endpoint, headers=self.headers).json()['results']
