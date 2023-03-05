#type: ignore

import os
import sys
import time
import json
import pymysql

from flask_login import UserMixin

if(os.name == 'posix'):
    import mariadb

AUTH_PATH = os.path.join(os.getcwd(), 'authorization')
    
class SupportTicket(object):
    
    id : int
    sender_id : int
    sender_name : str
    header : str
    initial_body : str
    responses : str
    priority : int
    timestamp : int
    
    def __init__(self, id: int, sender_id : int, sender_name : str, header : str, initial_body : str, responses : str, priority: int, timestamp : int):
        self.id = id
        self.sender_id = sender_id
        self.sender_name = sender_name  
        self.header = header
        self.initial_body = initial_body
        self.responses = responses
        self.timestamp = timestamp
    
class ChatMessage(object):
    
    id : int
    sender_id : int
    sender_name : str
    content : str
    timestamp : int
    
    def __init__(self, id : int, sender_id : int, sender_name : str, content : str, timestamp : int):
        self.id = id
        self.sender_id = sender_id
        self.sender_name = sender_name
        self.content = content
        self.timestamp = timestamp
    
class Notification(object):
    
    id : int
    recipient_id : int
    recipient_name : str
    
    header_content : str
    body_content : str
    
    sender_id : int
    sender_name : str
    
    marked_read : int
    
    def __init__(self, id : int, recipient_id : int, recipient_name : str, header_content : str, body_content: str, sender_id: int, sender_name: str, marked_read: int):
        self.id = id
        self.recipient_id = int(recipient_id)
        self.recipient_name = recipient_name
        self.header_content = header_content
        self.body_content = body_content
        self.sender_id = int(sender_id)
        self.sender_name = sender_name
        
        self.marked_read = int(marked_read)
    
class Message(object):
    
    id : int
    sender_id : int
    recipient_id : int
    sender_name : int
    recipient_name : int
    content : str
    timestamp : float
    
    marked_read : int
    
    def __init__(self, id: int, sender_id: int, recipient_id: int, sender_name: str, recipient_name: str, content: str, timestamp: float, marked_read: int):
        self.id = id
        self.sender_id = int(sender_id)
        self.recipient_id = int(recipient_id)
        self.sender_name = sender_name
        self.recipient_name = recipient_name
        self.content = content
        self.timestamp = timestamp
        
        self.marked_read = int(marked_read)
    
    
class UserEntry(UserMixin):
    
    id : int
    name : str
    password : str
    email : str
    timestamp : float
    session : int
    permission : int
    salt : bytes
    
    authenticated : bool
    
    sent_messages : list[Message]
    recieved_messages : list[Message]
    
    notifications : list[Notification]
    
    def is_authenticated(self):
        return True if self.authenticated else False
    
    def is_active(self):
        return True if self.is_authenticated() else False
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return self.id    

    def __init__(self, *user_entry):
        self.id = user_entry[0]
        self.name = user_entry[1]
        self.email = user_entry[2]
        self.password = user_entry[3]
        self.timestamp = user_entry[4]
        self.session = user_entry[5]
        self.permission = user_entry[6]
        self.salt = user_entry[7]
        
        self.authenticated = False
        
class MySQLInterface(object):
    
    configuration : dict
    driver = None
       
    def __init__(self, **configuration: dict):
        self.configuration = configuration
        
    def AttemptConnection(self):
        if(os.name == 'nt'):
            self.__class__.driver = pymysql.connect(**self.configuration)
        elif(os.name == 'posix'):
            self.__class__ .driver = mariadb.connect(**self.configuration)
    
    def GetCursor(self)->pymysql.cursors.Cursor:
        if(self.__class__.driver):
            return self.driver.cursor()
        
    def GetUsers(self, expression : None | object)->list[UserEntry]:
        cursor = self.GetCursor()
        
        cursor.execute("select * from users")
        
        users = [
            UserEntry(*result) 
            for result in cursor.fetchall()
        ]
        if(expression):
            users = [
                user
                for user in users
                if(expression(user))
            ]
        
        return users    
    
    def GetMessages(self, expression : None | object)->list[Message]:
        cursor = self.GetCursor()
        
        cursor.execute("select * from messages")

        messages = [
            Message(*result)
            for result in cursor.fetchall()
        ]

        if(expression):
            messages = [
                message
                for message in messages
                if(expression(message))
            ]
            
        return messages
    
    def GetNotifications(self, expression : None | object)->list[Notification]:
        cursor = self.GetCursor()
        
        cursor.execute("select * from notifications")
        
        notifications = [
            Notification(*result)
            for result in cursor.fetchall()
        ]
        
        if(expression):
            notifications = [
                notification
                for notification in notifications
                if(expression(notification))
            ]
            
        return notifications

    def GetChatMessages(self, expression : None | object)->list[ChatMessage]:
        cursor = self.GetCursor()
        
        cursor.execute("select * from chatlounge")
        
        messages = [
            ChatMessage(*result)
            for result in cursor.fetchall()
        ]
        
        if(expression):
            messages = [
                message
                for message in messages
                if(expression(message))
            ]

        return messages

    def GetSupportTickets(self, expression : None | object)->list[SupportTicket]:
        cursor = self.GetCursor()
        
        cursor.execute("select * from tickets")
        
        tickets = [
            SupportTicket(*result)
            for result in cursor.fetchall()
        ]
        
        if(expression):
            tickets = [
                ticket
                for ticket in tickets
                if(expression(ticket))
            ]

        return tickets


def keep_alive():
    """ keeps mysql connection alive """
    while(True):
        cursor = _mysql.GetCursor()
        
        cursor.execute("show tables")
        
        time.sleep(1200)

if(MySQLInterface.driver == None):
    _mysql = MySQLInterface(**json.loads(open(os.path.join(AUTH_PATH, 'configuration.json'), 'r').read()))
    _mysql.AttemptConnection()
