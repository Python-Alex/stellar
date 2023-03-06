#type: ignore
import time
from authorization import driver

class ActiveUserStack(object):
    
    users : dict[str, dict]
    
    def __init__(self):
        self.users = []

    def new_connection(self, address: str):
        self.users["address"] = {
            "ip": address, "info": {
                "requests": 0, "rtimes": []
            }}
                
    def request_callback(self, address: str):
        self.users["address"]["info"]["requests"]+=1
        self.users["address"]["info"]["rtimes"].append(time.time())
        
                
def reset_data():
    cursor = driver.MySQLInterface.GetCursor(driver._mysql)
    users = driver.MySQLInterface.GetUsers(driver._mysql, lambda entry: entry.session != 0)
    for user in users:
        cursor.execute("UPDATE users SET session=0 WHERE id=%d" % (user.id))
        driver.MySQLInterface.driver.commit()    
    

ActiveStack = ActiveUserStack()