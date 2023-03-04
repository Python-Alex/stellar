#type: ignore
import time
from authorization import driver

class ActiveUserStack(object):
    
    users : list[tuple[float, driver.UserEntry]] # [ (timeout_timestamp, user_entry) , ]
    
    def __init__(self):
        self.users = []
        
    def new_active(self, user: driver.UserEntry):
        if(user in self.users):
            return
        
        self.users.append((time.time(), user))
        
    def check_timeout(self):
        cursor = driver.MySQLInterface.GetCursor(driver._mysql)
        
        for user in self.users.copy(): # cannot mutate list mid-iteration
            if(time.time() - user[0] > 60):
                cursor.execute("UPDATE users SET session=0 WHERE id=%d" % (user[1].id))
                driver.MySQLInterface.driver.commit()
                
                self.users.remove(user)
                
def reset_data():
    cursor = driver.MySQLInterface.GetCursor(driver._mysql)
    users = driver.MySQLInterface.GetUsers(driver._mysql, lambda entry: entry.session != 0)
    for user in users:
        cursor.execute("UPDATE users SET session=0 WHERE id=%d" % (user.id))
        driver.MySQLInterface.driver.commit()    
    

ActiveStack = ActiveUserStack()