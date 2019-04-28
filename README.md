Payments MicroService for stock application: http://esd-ezstock.herokuapp.com/ (type in orange and orange123 for test user access)

### Functionality of Microservice
Microservice helps a client on our application withdraw money from his e-Wallet to his bank account or deposit money from his Bank account to his E-wallet.

### Microservice Process Diagram
Diagram of how Payments Microservice Works: (diagram credits to https://github.com/elihuansen)
![](https://i.imgur.com/9jyXlDz.jpg?raw=true)

#### Explanation of Process Diagram
1) Client will make an bank transfer request via the Trading Portal UI.
2) Trading Portal NodeJS Server makes a POST request to Payments service.
3) Payment service query DBS Sandpox API to get access token to make transfer.
4) Payments service will then query Clients Service for the PayeeID (bank account ID).
5) Payment Service will issue a command to DBS Bank Sandbox API to make the transfer.
6) Upon success, Payments service will issue a command to clients service to update the balance.
7) When balance is updated, Clients service will send an asynchronus notification to RabbitMQ which      will then notify client the balance has been updated through our Telegram Service.
8) Traidng Portal UI will display cash transfer success/failure to client. 

### Sample Input
Consumes a JSON input via HTTP POST method. Sample input for body below:
 ``` 
  {
    "username": "username",
    "transfer_amt": 1000,
    "transfer_type": "toBankAccount",
    "assertion": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJEQlMiLCJpYXQiOjE1NTYzNzEyODAsImV4cCI6MTU1NjQ1NzY4MCwic3ViIjoiSnd0IFNpZ25lZCBUb2tlbiBmb3IgRGVtZSBBcHAgUGFydG5lciBUb2tlbiBmbG93IiwiUEFSVFlfVFlQRSI6MywiQ0xJRU5UX0lEIjoiY2xpZW50SWQzIiwiQ0xJRU5UX1RZUEUiOiJQYXJ0bmVyIiwiQUNDRVNTIjoiQ29tbXVuaXR5IiwiU0NPUEUiOiJSRUFEIiwiYXVkIjoiUGFydG5lcnMiLCJqdGkiOiJTdGFuZGVyZEpXVFRva2VuMSJ9.A7cDZFWCdm9OUpCJ6A-i-NkEc0lkIfrsTSnLMo0x4yqJnT2F8BGPR40MbYkVWBH_4WHp2E3rw4JmCJ-_oLL3ypzgYBLzzmRU_Ukf9N5c6HFbPcAOTeRDIodKWkQcpoepAG3AN0eyR39aIPRoVu8OVZvuI_DO-7INNjSyInF1hX8q0Q47213wEACRLzKk7koQp4XaG9IFUV9sy7sXgSScZ5iOVT9JGATTykyKIdxSZubBjzH2D3_gLyENmhS8eFCEPbZy3rDwYD1fqY3OfdcgGUuFmQOrIhCFgZ89qi9fG2jzZ8caQ5JBiTMSMgFEd73v8-lEllRoEJTFyxupuZjuUQ"
  }
 ```

Transfer type is either "toBankAccount" or "FromBankAccount".

### Sample Output

Outputs a JSON Object containing transfer status and transfer amount.

```
 {
   "status": "success",
   "amount" : 1000
 }
 ```
