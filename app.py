from flask import Flask, jsonify, request, abort
import requests, json
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode
from datetime import datetime
import sys


app = Flask(__name__)

@app.route("/")
def index():
    return "heroku deployment for payment"

@app.route("/api/makeTransfer/", methods=["GET"])

# def get_details():
#     return jsonify({'payload': user_details})

def sendPayment():

    failureStatus = {
        "status": "failure"
    }
    
    return jsonify(request.get_json)
    # if not request.json or 'username' not in request.json or 'transfer_amt' not in request.json or 'transfer_type' not in request.json or 'assertion' not in request.json:
    #     abort(400)

    amount = request.json['transfer_amt']

    if request.json["transfer_type"] == "toBankAccount":
        amount = - amount #set amount to negative as client's balance will get deducted instead if client transfers from eWallet to his/her bankAccount
    
    username = request.json['username']
    assertion = request.json['assertion'] #key to access access bank account authentication key

    bankCredentials = { 
    "client_id":"demo", 
    "client_assertion": assertion
    }

    
    bankHeaders = {
        "Content-Type": "application/json",
        "clientId": "clientId3"
    }

    # makes requests to dbs auth endpoint, bankCredentials are default set to demo because of interaction with bankApi
    accessToken = requests.post("https://www.dbs.com/sandbox/api/sg/v1/oauth/authorize", data = json.dumps(bankCredentials), headers = bankHeaders).json()["access_token"]

    
    #request client service to get payeeId details
    r = requests.get("http://huansenlim2017-eval-prod.apigee.net/esdbroker/api/v1/clients/info/" + username).json()

    payeeId = r["payeeId"]
    currentBalance = r["balance"]


    #make Transfer of money
    transferDetails = {
        "fundTransferDetl":
        {
            "debitAccountId":"05560007040018",
            "payeeId": payeeId,
            "amount": amount,
            "sourceCurrency":"SGD",
            "destinationCurrency":"SGD",
            "transferCurrency":"SGD",
            "comments": request.json["transfer_type"],
            "purpose":"BEXP",
            "valueDate":"2017-05-29", #value_date set to static date for testing purposes
            "transferType":"INSTANT",
            "partyId":"2076251808",
            "referenceId":"93292733C649266803099"
        }
    }

    transferHeaders = {
        "Content-Type": "application/json",
        "clientId": "clientId3",
        "accessToken": accessToken
    }

    print('hello, its come to this')

    r = requests.post("https://www.dbs.com/sandbox/api/sg/v1/transfers/creditPayeeAccount",
    data = json.dumps(transferDetails), headers = transferHeaders)

    #update client balance on success status for both payments and clients database
    if str(r.status_code) == "200" or str(r.status_code) == "201":
        #updateBalannce on ClientSide
        newBalance = currentBalance + amount
        updateBalanceStatus = requests.get("http://huansenlim2017-eval-prod.apigee.net/esdbroker/api/v1/clients/" + username + "/updateBalance/" + str(newBalance)).json()["status"]

        if updateBalanceStatus == "success": 

            #update payments Transactional Database
            try:
                connection = mysql.connector.connect(host='us-cdbr-iron-east-02.cleardb.net',
                                            database='heroku_bda8ea0c956826f',
                                            user='b26c9e886c4967',
                                            password='4698d536')

                cursor = connection.cursor(prepared=True)

                #insert single record now
                sql_insert_query = """ INSERT INTO `payment_info`
                                (`username`,`debitAccountId`, `payeeId`, `Amount`, `sourceCurrency`, `destinationCurrency`, `transferCurrency`, `Comments`, `transferType`, `referenceId`, `Status`, `Timestamp`)
                                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

                # current date and time
                now = datetime.now()

                insert_tuple = (username,transferDetails["fundTransferDetl"]["debitAccountId"], payeeId, amount, transferDetails["fundTransferDetl"]["sourceCurrency"],
                                transferDetails["fundTransferDetl"]["destinationCurrency"], transferDetails["fundTransferDetl"]["transferCurrency"], request.json["transfer_type"], request.json["transfer_type"], transferDetails["fundTransferDetl"]["referenceId"], str(r.status_code), now)
                
                result  = cursor.execute(sql_insert_query, insert_tuple)
                connection.commit()
                print ("Record inserted successfully into payment_info table")
            
            except mysql.connector.Error as error :
                connection.rollback()
                print("Failed to insert into MySQL table {}".format(error))
            
            finally:
                #closing database connection.
                if(connection.is_connected()):
                    cursor.close()
                    connection.close()
                    print("MySQL connection is closed")

            responseStatus = {
                "status" : "success",
                "transferAmount" : amount
            }

            return jsonify(responseStatus)
    print("fail!!!!")
    return failureStatus

    

if __name__ == '__main__':
    app.run(debug=True)