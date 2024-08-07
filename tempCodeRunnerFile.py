
from flask import Flask, request, render_template, redirect, url_for
import os
import pyodbc
import uuid
import time
from datetime import datetime
from Constants import connString

from AgricultureBoardModel import AgricultureBoardModel
from BuyerModel import BuyerModel
from FarmerModel import FarmerModel
from ProductModel import ProductModel
from RoleModel import RoleModel
from TransactionDetailsModel import TransactionDetailsModel
from UsersModel import UsersModel




app = Flask(__name__)
app.secret_key = "MySecret"
ctx = app.app_context()
ctx.push()

with ctx:
    pass
user_id = ""
emailid = ""
role_object = None
message = ""
msgType = ""
uploaded_file_name = ""

def initialize():
    global message, msgType
    message = ""
    msgType = ""

def process_role(option_id):

    
    if option_id == 0:
        if role_object.canAgricultureBoard == False:
            return False
        
    if option_id == 1:
        if role_object.canBuyer == False:
            return False
        
    if option_id == 2:
        if role_object.canFarmer == False:
            return False
        
    if option_id == 3:
        if role_object.canProduct == False:
            return False
        
    if option_id == 4:
        if role_object.canRole == False:
            return False
        
    if option_id == 5:
        if role_object.canTransactionDetails == False:
            return False
        
    if option_id == 6:
        if role_object.canUsers == False:
            return False
        

    return True



@app.route("/")
def index():
    global user_id, emailid
    return render_template("Login.html")

@app.route("/processLogin", methods=["POST"])
def processLogin():
    global user_id, emailid, role_object
    emailid = request.form["emailid"]
    password = request.form["password"]
    conn1 = pyodbc.connect(connString, autocommit=True)
    cur1 = conn1.cursor()
    sqlcmd1 = "SELECT * FROM Users WHERE emailid = '" + emailid + "' AND password = '" + password + "' AND isActive = 1";
    cur1.execute(sqlcmd1)
    row = cur1.fetchone()

    cur1.commit()
    if not row:
        return render_template("Login.html", processResult="Invalid Credentials")
    user_id = row[0]

    cur2 = conn1.cursor()
    sqlcmd2 = "SELECT * FROM Role WHERE RoleID = '" + str(row[6]) + "'"
    cur2.execute(sqlcmd2)
    row2 = cur2.fetchone()

    if not row2:
        return render_template("Login.html", processResult="Invalid Role")

    role_object = RoleModel(row2[0], row2[1], row2[2], row2[3], row2[4], row2[5], row2[6], row2[7], row2[8])

    return render_template("Dashboard.html")


@app.route("/ChangePassword")
def changePassword():
    global user_id, emailid
    return render_template("ChangePassword.html")


@app.route("/ProcessChangePassword", methods=["POST"])
def processChangePassword():
    global user_id, emailid
    oldPassword = request.form["oldPassword"]
    newPassword = request.form["newPassword"]
    confirmPassword = request.form["confirmPassword"]
    conn1 = pyodbc.connect(connString, autocommit=True)
    cur1 = conn1.cursor()
    sqlcmd1 = "SELECT * FROM Users WHERE emailid = '" + emailid + "' AND password = '" + oldPassword + "'";
    cur1.execute(sqlcmd1)
    row = cur1.fetchone()
    cur1.commit()
    if not row:
        return render_template("ChangePassword.html", msg="Invalid Old Password")

    if newPassword.strip() != confirmPassword.strip():
        return render_template("ChangePassword.html", msg="New Password and Confirm Password are NOT same")

    conn2 = pyodbc.connect(connString, autocommit=True)
    cur2 = conn2.cursor()
    sqlcmd2 = "UPDATE Users SET password = '" + newPassword + "' WHERE emailid = '" + emailid + "'";
    cur1.execute(sqlcmd2)
    cur2.commit()
    return render_template("ChangePassword.html", msg="Password Changed Successfully")


@app.route("/Dashboard")
def Dashboard():
    global user_id, emailid
    return render_template("Dashboard.html")


@app.route("/Information")
def Information():
    global message, msgType
    return render_template("Information.html", msgType=msgType, message=message)


@app.route("/AgricultureBoardListing")
def AgricultureBoard_listing():
    global user_id, emailid

    global message, msgType, role_object
    if role_object == None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("Information"))
    canAgricultureBoard = process_role(0)

    if canAgricultureBoard == False:
        message = "You Don't Have Permission to Access AgricultureBoard"
        msgType = "Error"
        return redirect(url_for("Information"))

    records = AgricultureBoardModel.get_all()

    return render_template("AgricultureBoardListing.html", records=records)

@app.route("/AgricultureBoardOperation")
def AgricultureBoard_operation():
    global user_id, user_name, message, msgType, role_object
    if role_object is None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("Information"))
    canAgricultureBoard = process_role(0)

    if not canAgricultureBoard:
        message = "You Don't Have Permission to Access AgricultureBoard"
        msgType = "Error"
        return redirect(url_for("Information"))
    unique_id = ""
    operation = request.args.get("operation")
    row = AgricultureBoardModel("", "")

    AgricultureBoard = AgricultureBoardModel.get_all()
    
    if operation != "Create":
        unique_id = request.args.get("unique_id").strip()
        row = AgricultureBoardModel.get_by_id(unique_id)

    return render_template("AgricultureBoardOperation.html", row=row, operation=operation, AgricultureBoard=AgricultureBoard, )

@app.route("/ProcessAgricultureBoardOperation", methods=["POST"])
def process_AgricultureBoard_operation():
    global user_id, user_name, message, msgType, role_object

    if role_object is None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("/"))

    canAgricultureBoard = process_role(0)
    if not canAgricultureBoard:
        message = "You Don't Have Permission to Access AgricultureBoard"
        msgType = "Error"
        return redirect(url_for("Information"))

    operation = request.form["operation"]
    obj = AgricultureBoardModel("", "")

    if operation != "Delete":
       obj.agricultureBoardID = request.form['agricultureBoardID']
       obj.agricultureBoardName = request.form['agricultureBoardName']
       obj.contactNbr = request.form['contactNbr']
       obj.emailID = request.form['emailID']
       obj.address = request.form['address']
       obj.city = request.form['city']
       obj.county = request.form['county']
       obj.postcode = request.form['postcode']
       obj.country = request.form['country']
       

    if operation == "Create":
        obj.insert(obj)

    if operation == "Edit":
        obj.agricultureBoardID = request.form["agricultureBoardID"]
        obj.update(obj)

    if operation == "Delete":
        agricultureBoardID = request.form["agricultureBoardID"]
        obj.delete(agricultureBoardID)


    return redirect(url_for("AgricultureBoard_listing"))
                    
@app.route("/BuyerListing")
def Buyer_listing():
    global user_id, emailid

    global message, msgType, role_object
    if role_object == None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("Information"))
    canBuyer = process_role(1)

    if canBuyer == False:
        message = "You Don't Have Permission to Access Buyer"
        msgType = "Error"
        return redirect(url_for("Information"))

    records = BuyerModel.get_all()

    return render_template("BuyerListing.html", records=records)

@app.route("/BuyerOperation")
def Buyer_operation():
    global user_id, user_name, message, msgType, role_object
    if role_object is None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("Information"))
    canBuyer = process_role(1)

    if not canBuyer:
        message = "You Don't Have Permission to Access Buyer"
        msgType = "Error"
        return redirect(url_for("Information"))
    unique_id = ""
    operation = request.args.get("operation")
    row = BuyerModel("", "")

    Buyer = BuyerModel.get_all()
    
    if operation != "Create":
        unique_id = request.args.get("unique_id").strip()
        row = BuyerModel.get_by_id(unique_id)

    return render_template("BuyerOperation.html", row=row, operation=operation, Buyer=Buyer, )

@app.route("/ProcessBuyerOperation", methods=["POST"])
def process_Buyer_operation():
    global user_id, user_name, message, msgType, role_object

    if role_object is None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("/"))

    canBuyer = process_role(1)
    if not canBuyer:
        message = "You Don't Have Permission to Access Buyer"
        msgType = "Error"
        return redirect(url_for("Information"))

    operation = request.form["operation"]
    obj = BuyerModel("", "")

    if operation != "Delete":
       obj.buyerID = request.form['buyerID']
       obj.buyerName = request.form['buyerName']
       obj.contactNbr = request.form['contactNbr']
       obj.emailID = request.form['emailID']
       obj.address = request.form['address']
       obj.city = request.form['city']
       obj.county = request.form['county']
       obj.postcode = request.form['postcode']
       obj.country = request.form['country']
       obj.inbusiness = request.form['inbusiness']
       obj.adharNumber = request.form['adharNumber']
       

    if operation == "Create":
        obj.insert(obj)

    if operation == "Edit":
        obj.buyerID = request.form["buyerID"]
        obj.update(obj)

    if operation == "Delete":
        buyerID = request.form["buyerID"]
        obj.delete(buyerID)


    return redirect(url_for("Buyer_listing"))
                    
@app.route("/FarmerListing")
def Farmer_listing():
    global user_id, emailid

    global message, msgType, role_object
    if role_object == None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("Information"))
    canFarmer = process_role(2)

    if canFarmer == False:
        message = "You Don't Have Permission to Access Farmer"
        msgType = "Error"
        return redirect(url_for("Information"))

    records = FarmerModel.get_all()

    return render_template("FarmerListing.html", records=records)

@app.route("/FarmerOperation")
def Farmer_operation():
    global user_id, user_name, message, msgType, role_object
    if role_object is None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("Information"))
    canFarmer = process_role(2)

    if not canFarmer:
        message = "You Don't Have Permission to Access Farmer"
        msgType = "Error"
        return redirect(url_for("Information"))
    unique_id = ""
    operation = request.args.get("operation")
    row = FarmerModel("", "")

    Farmer = FarmerModel.get_all()
    
    if operation != "Create":
        unique_id = request.args.get("unique_id").strip()
        row = FarmerModel.get_by_id(unique_id)

    return render_template("FarmerOperation.html", row=row, operation=operation, Farmer=Farmer, )

@app.route("/ProcessFarmerOperation", methods=["POST"])
def process_Farmer_operation():
    global user_id, user_name, message, msgType, role_object

    if role_object is None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("/"))

    canFarmer = process_role(2)
    if not canFarmer:
        message = "You Don't Have Permission to Access Farmer"
        msgType = "Error"
        return redirect(url_for("Information"))

    operation = request.form["operation"]
    obj = FarmerModel("", "")

    if operation != "Delete":
       obj.farmerID = request.form['farmerID']
       obj.farmerName = request.form['farmerName']
       obj.contactNbr = request.form['contactNbr']
       obj.emailID = request.form['emailID']
       obj.address = request.form['address']
       obj.city = request.form['city']
       obj.county = request.form['county']
       obj.postcode = request.form['postcode']
       obj.country = request.form['country']
       obj.adharNumber = request.form['adharNumber']
       

    if operation == "Create":
        obj.insert(obj)

    if operation == "Edit":
        obj.farmerID = request.form["farmerID"]
        obj.update(obj)

    if operation == "Delete":
        farmerID = request.form["farmerID"]
        obj.delete(farmerID)


    return redirect(url_for("Farmer_listing"))
                    
@app.route("/ProductListing")
def Product_listing():
    global user_id, emailid

    global message, msgType, role_object
    if role_object == None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("Information"))
    canProduct = process_role(3)

    if canProduct == False:
        message = "You Don't Have Permission to Access Product"
        msgType = "Error"
        return redirect(url_for("Information"))

    records = ProductModel.get_all()

    return render_template("ProductListing.html", records=records)

@app.route("/ProductOperation")
def Product_operation():
    global user_id, user_name, message, msgType, role_object
    if role_object is None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("Information"))
    canProduct = process_role(3)

    if not canProduct:
        message = "You Don't Have Permission to Access Product"
        msgType = "Error"
        return redirect(url_for("Information"))
    unique_id = ""
    operation = request.args.get("operation")
    row = ProductModel("", "")

    Product = ProductModel.get_all()
    
    if operation != "Create":
        unique_id = request.args.get("unique_id").strip()
        row = ProductModel.get_by_id(unique_id)

    return render_template("ProductOperation.html", row=row, operation=operation, Product=Product, )

@app.route("/ProcessProductOperation", methods=["POST"])
def process_Product_operation():
    global user_id, user_name, message, msgType, role_object

    if role_object is None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("/"))

    canProduct = process_role(3)
    if not canProduct:
        message = "You Don't Have Permission to Access Product"
        msgType = "Error"
        return redirect(url_for("Information"))

    operation = request.form["operation"]
    obj = ProductModel("", "")

    if operation != "Delete":
       obj.productID = request.form['productID']
       obj.productName = request.form['productName']
       obj.packageSize = request.form['packageSize']
       obj.price = request.form['price']
       

    if operation == "Create":
        obj.insert(obj)

    if operation == "Edit":
        obj.productID = request.form["productID"]
        obj.update(obj)

    if operation == "Delete":
        productID = request.form["productID"]
        obj.delete(productID)


    return redirect(url_for("Product_listing"))
                    
@app.route("/RoleListing")
def Role_listing():
    global user_id, emailid

    global message, msgType, role_object
    if role_object == None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("Information"))
    canRole = process_role(4)

    if canRole == False:
        message = "You Don't Have Permission to Access Role"
        msgType = "Error"
        return redirect(url_for("Information"))

    records = RoleModel.get_all()

    return render_template("RoleListing.html", records=records)

@app.route("/RoleOperation")
def Role_operation():
    global user_id, user_name, message, msgType, role_object
    if role_object is None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("Information"))
    canRole = process_role(4)

    if not canRole:
        message = "You Don't Have Permission to Access Role"
        msgType = "Error"
        return redirect(url_for("Information"))
    unique_id = ""
    operation = request.args.get("operation")
    row = RoleModel("", "")

    Role = RoleModel.get_all()
    
    if operation != "Create":
        unique_id = request.args.get("unique_id").strip()
        row = RoleModel.get_by_id(unique_id)

    return render_template("RoleOperation.html", row=row, operation=operation, Role=Role, )

@app.route("/ProcessRoleOperation", methods=["POST"])
def process_Role_operation():
    global user_id, user_name, message, msgType, role_object

    if role_object is None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("/"))

    canRole = process_role(4)
    if not canRole:
        message = "You Don't Have Permission to Access Role"
        msgType = "Error"
        return redirect(url_for("Information"))

    operation = request.form["operation"]
    obj = RoleModel("", "")

    if operation != "Delete":
       obj.roleID = request.form['roleID']
       obj.roleName = request.form['roleName']
       obj.canRole = 0 
       if request.form.get("canRole") != None : 
              obj.canRole = 1       
       obj.canUsers = 0 
       if request.form.get("canUsers") != None : 
              obj.canUsers = 1       
       obj.canAgricultureBoard = 0 
       if request.form.get("canAgricultureBoard") != None : 
              obj.canAgricultureBoard = 1       
       obj.canBuyer = 0 
       if request.form.get("canBuyer") != None : 
              obj.canBuyer = 1       
       obj.canFarmer = 0 
       if request.form.get("canFarmer") != None : 
              obj.canFarmer = 1       
       obj.canProduct = 0 
       if request.form.get("canProduct") != None : 
              obj.canProduct = 1       
       obj.canTransactionDetails = 0 
       if request.form.get("canTransactionDetails") != None : 
              obj.canTransactionDetails = 1       
       

    if operation == "Create":
        obj.insert(obj)

    if operation == "Edit":
        obj.roleID = request.form["roleID"]
        obj.update(obj)

    if operation == "Delete":
        roleID = request.form["roleID"]
        obj.delete(roleID)


    return redirect(url_for("Role_listing"))
                    
@app.route("/TransactionDetailsListing")
def TransactionDetails_listing():
    global user_id, emailid

    global message, msgType, role_object
    if role_object == None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("Information"))
    canTransactionDetails = process_role(5)

    if canTransactionDetails == False:
        message = "You Don't Have Permission to Access TransactionDetails"
        msgType = "Error"
        return redirect(url_for("Information"))

    records = TransactionDetailsModel.get_all()

    return render_template("TransactionDetailsListing.html", records=records)

@app.route("/TransactionDetailsOperation")
def TransactionDetails_operation():
    global user_id, user_name, message, msgType, role_object
    if role_object is None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("Information"))
    canTransactionDetails = process_role(5)

    if not canTransactionDetails:
        message = "You Don't Have Permission to Access TransactionDetails"
        msgType = "Error"
        return redirect(url_for("Information"))
    unique_id = ""
    operation = request.args.get("operation")
    row = TransactionDetailsModel("", "")

    TransactionDetails = TransactionDetailsModel.get_all()
    agricultureBoard_list = AgricultureBoardModel.get_name_id()
    buyer_list = BuyerModel.get_name_id()
    farmer_list = FarmerModel.get_name_id()
    product_list = ProductModel.get_name_id()
    if operation != "Create":
        unique_id = request.args.get("unique_id").strip()
        row = TransactionDetailsModel.get_by_id(unique_id)

    return render_template("TransactionDetailsOperation.html", row=row, operation=operation, TransactionDetails=TransactionDetails, agricultureBoard_list = agricultureBoard_list,buyer_list = buyer_list,farmer_list = farmer_list,product_list = product_list)

@app.route("/ProcessTransactionDetailsOperation", methods=["POST"])
def process_TransactionDetails_operation():
    global user_id, user_name, message, msgType, role_object

    if role_object is None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("/"))

    canTransactionDetails = process_role(5)
    if not canTransactionDetails:
        message = "You Don't Have Permission to Access TransactionDetails"
        msgType = "Error"
        return redirect(url_for("Information"))

    operation = request.form["operation"]
    obj = TransactionDetailsModel("", "")

    if operation != "Delete":
       obj.orderID = request.form['orderID']
       obj.agricultureBoardID = request.form['agricultureBoardID']
       obj.gstNbr = request.form['gstNbr']
       obj.buyerID = request.form['buyerID']
       obj.farmerID = request.form['farmerID']
       obj.effDate = request.form['effDate']
       obj.productID = request.form['productID']
       obj.price = request.form['price']
       obj.qty = request.form['qty']
       

    if operation == "Create":
        obj.insert(obj)

    if operation == "Edit":
        obj.orderID = request.form["orderID"]
        obj.update(obj)

    if operation == "Delete":
        orderID = request.form["orderID"]
        obj.delete(orderID)


    return redirect(url_for("TransactionDetails_listing"))
                    
@app.route("/UsersListing")
def Users_listing():
    global user_id, emailid

    global message, msgType, role_object
    if role_object == None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("Information"))
    canUsers = process_role(6)

    if canUsers == False:
        message = "You Don't Have Permission to Access Users"
        msgType = "Error"
        return redirect(url_for("Information"))

    records = UsersModel.get_all()

    return render_template("UsersListing.html", records=records)

@app.route("/UsersOperation")
def Users_operation():
    global user_id, user_name, message, msgType, role_object
    if role_object is None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("Information"))
    canUsers = process_role(6)

    if not canUsers:
        message = "You Don't Have Permission to Access Users"
        msgType = "Error"
        return redirect(url_for("Information"))
    unique_id = ""
    operation = request.args.get("operation")
    row = UsersModel("", "")

    Users = UsersModel.get_all()
    role_list = RoleModel.get_name_id()
    if operation != "Create":
        unique_id = request.args.get("unique_id").strip()
        row = UsersModel.get_by_id(unique_id)

    return render_template("UsersOperation.html", row=row, operation=operation, Users=Users, role_list = role_list)

@app.route("/ProcessUsersOperation", methods=["POST"])
def process_Users_operation():
    global user_id, user_name, message, msgType, role_object

    if role_object is None:
        message = "Application Error Occurred. Logout"
        msgType = "Error"
        return redirect(url_for("/"))

    canUsers = process_role(6)
    if not canUsers:
        message = "You Don't Have Permission to Access Users"
        msgType = "Error"
        return redirect(url_for("Information"))

    operation = request.form["operation"]
    obj = UsersModel("", "")

    if operation != "Delete":
       obj.userID = request.form['userID']
       obj.userName = request.form['userName']
       obj.emailid = request.form['emailid']
       obj.password = request.form['password']
       obj.contactNo = request.form['contactNo']
       obj.isActive = 0 
       if request.form.get("isActive") != None : 
              obj.isActive = 1       
       obj.roleID = request.form['roleID']
       

    if operation == "Create":
        obj.insert(obj)

    if operation == "Edit":
        obj.userID = request.form["userID"]
        obj.update(obj)

    if operation == "Delete":
        userID = request.form["userID"]
        obj.delete(userID)


    return redirect(url_for("Users_listing"))
                    


import hashlib
import json


@app.route("/BlockChainGeneration")
def BlockChainGeneration():

    conn = pyodbc.connect(connString, autocommit=True)
    cursor = conn.cursor()
    sqlcmd = "SELECT COUNT(*) FROM TransactionDetails WHERE isBlockChainGenerated = 1"
    cursor.execute(sqlcmd)
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        blocksCreated = dbrow[0]

    sqlcmd = "SELECT COUNT(*) FROM TransactionDetails WHERE isBlockChainGenerated = 0 or isBlockChainGenerated is null"
    cursor.execute(sqlcmd)
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        blocksNotCreated = dbrow[0]
    return render_template('BlockChainGeneration.html', blocksCreated=blocksCreated, blocksNotCreated=blocksNotCreated)


@app.route("/ProcessBlockchainGeneration", methods=['POST'])
def ProcessBlockchainGeneration():

    conn = pyodbc.connect(connString, autocommit=True)
    cursor = conn.cursor()
    sqlcmd = "SELECT COUNT(*) FROM TransactionDetails WHERE isBlockChainGenerated = 1"
    cursor.execute(sqlcmd)
    blocksCreated = 0
    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        blocksCreated = dbrow[0]

    prevHash = ""
    if blocksCreated != 0:
        connx = pyodbc.connect(connString, autocommit=True)
        cursorx = connx.cursor()
        sqlcmdx = "SELECT * FROM TransactionDetails WHERE isBlockChainGenerated = 0 or isBlockChainGenerated is null ORDER BY sequenceNumber"
        cursorx.execute(sqlcmdx)
        dbrowx = cursorx.fetchone()
        if dbrowx:
            uniqueID = dbrowx[12]
            conny = pyodbc.connect(connString, autocommit=True)
            cursory = conny.cursor()
            sqlcmdy = "SELECT hash FROM TransactionDetails WHERE sequenceNumber < '" + str(uniqueID) + "' ORDER BY sequenceNumber DESC"
            cursory.execute(sqlcmdy)
            dbrowy = cursory.fetchone()
            if dbrowy:
                prevHash = dbrowy[0]
            cursory.close()
            conny.close()
        cursorx.close()
        connx.close()
    conn = pyodbc.connect(connString, autocommit=True)
    cursor = conn.cursor()
    sqlcmd = "SELECT * FROM TransactionDetails WHERE isBlockChainGenerated = 0 or isBlockChainGenerated is null ORDER BY sequenceNumber"
    cursor.execute(sqlcmd)

    while True:
        sqlcmd1 = ""
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        unqid = str(dbrow[12])

        bdata = str(dbrow[1]) + str(dbrow[2]) + str(dbrow[3]) + str(dbrow[4])
        block_serialized = json.dumps(bdata, sort_keys=True).encode('utf-8')
        block_hash = hashlib.sha256(block_serialized).hexdigest()

        conn1 = pyodbc.connect(connString, autocommit=True)
        cursor1 = conn1.cursor()
        sqlcmd1 = "UPDATE TransactionDetails SET isBlockChainGenerated = 1, hash = '" + block_hash + "', prevHash = '" + prevHash + "' WHERE sequenceNumber = '" + unqid + "'"
        cursor1.execute(sqlcmd1)
        cursor1.close()
        conn1.close()
        prevHash = block_hash
    return render_template('BlockchainGenerationResult.html')


@app.route("/BlockChainReport")
def BlockChainReport():

    conn = pyodbc.connect(connString, autocommit=True)
    cursor = conn.cursor()

    sqlcmd1 = "SELECT * FROM TransactionDetails WHERE isBlockChainGenerated = 1"
    cursor.execute(sqlcmd1)
    conn2 = pyodbc.connect(connString, autocommit=True)
    cursor = conn2.cursor()
    sqlcmd1 = "SELECT * FROM TransactionDetails ORDER BY sequenceNumber DESC"
    cursor.execute(sqlcmd1)
    records = []

    while True:
        dbrow = cursor.fetchone()
        if not dbrow:
            break
        row = TransactionDetailsModel(dbrow[0],dbrow[1],dbrow[2],dbrow[3],dbrow[4],dbrow[5],dbrow[6],dbrow[7],dbrow[8],dbrow[9],dbrow[10],dbrow[11],dbrow[12])
        records.append(row)
    return render_template('BlockChainReport.html', records=records)         

            

 
if __name__ == "__main__":
    app.run()

                    
