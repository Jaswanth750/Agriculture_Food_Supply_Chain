from Constants import connString
import pyodbc
import datetime
import uuid
import time
import Constants    

class ProductModel:
    def __init__(self, productID = '',productName = '',packageSize = '',price = 0):
        self.productID = productID
        self.productName = productName
        self.packageSize = packageSize
        self.price = price
       
        

    @staticmethod
    def get_all():
        conn = pyodbc.connect(connString, autocommit=True)
        cursor = conn.cursor()
        sqlcmd1 = "SELECT * FROM Product ORDER BY productName"
        cursor.execute(sqlcmd1)
        records = []
        for dbrow in cursor.fetchall():
            row = ProductModel(dbrow[0],dbrow[1],dbrow[2],dbrow[3])
            records.append(row)
        cursor.close()
        conn.close()
        return records

    @staticmethod
    def get_name_id():
        conn = pyodbc.connect(connString, autocommit=True)
        cursor = conn.cursor()
        sqlcmd1 = "SELECT productID, productName FROM Product  ORDER BY productName"
        cursor.execute(sqlcmd1)
        records = []
        for dbrow in cursor.fetchall():
            row = ProductModel(dbrow[0],dbrow[1])
            records.append(row)
        cursor.close()
        conn.close()
        return records
        
    @staticmethod
    def get_by_id(unique_id):
        conn = pyodbc.connect(connString, autocommit=True)
        cursor = conn.cursor()
        sqlcmd1 = "SELECT * FROM Product WHERE productID = ?"
        cursor.execute(sqlcmd1, unique_id)
        record = None
        for dbrow in cursor.fetchall():
            record = ProductModel(dbrow[0],dbrow[1],dbrow[2],dbrow[3])
        cursor.close()
        conn.close()
        return record
    
    @staticmethod
    def insert(obj):
        obj.productID = str(uuid.uuid4())
        conn = pyodbc.connect(connString, autocommit=True)
        cursor = conn.cursor()
        sqlcmd1 = "INSERT INTO Product (productID,productName,packageSize,price) VALUES(?,?,?,?)"
        cursor.execute(sqlcmd1, (obj.productID,obj.productName,obj.packageSize,obj.price))
        cursor.close()
        conn.close()
        
    
    @staticmethod
    def update(obj):
        conn = pyodbc.connect(connString, autocommit=True)
        cursor = conn.cursor()
        sqlcmd1 = "UPDATE Product SET productName = ?,packageSize = ?,price = ? WHERE productID = ?"
        cursor.execute(sqlcmd1,  (obj.productName,obj.packageSize,obj.price,obj.productID))
        cursor.close()
        conn.close()
    
    @staticmethod
    def delete(unique_id):
        conn = pyodbc.connect(connString, autocommit=True)
        cursor = conn.cursor()
        sqlcmd1 = "DELETE FROM Product WHERE productID = ?"
        cursor.execute(sqlcmd1, (unique_id))
        cursor.close()
        conn.close()

