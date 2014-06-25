# -*- coding: utf-8 -*-
"""
 Copyright (c) 2014 l8orre

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""


 
from PyQt4.QtCore import   QObject , pyqtSignal, pyqtSlot, SIGNAL

from PyQt4 import Qt, QtCore

from nxtPwt.nxtApiSigs import nxtApi
from nxtPwt.nxtApiPrototypes import nxtQs

import time

import sqlite3 as sq

import logging as lg

#import operator as op.m
from operator import mod as opmod


# jsonrpc stuff
from requests import Request as Req
from requests import Response  as Resp
from requests import Session
import requests 


from werkzeug.wrappers import  Response ,Request
from werkzeug.serving import run_simple

from jsonrpc import JSONRPCResponseManager, dispatcher

import sys


import sqlite3 as sq
 
 
    

class nxtUseCaseMeta(QObject):
    """ This is an abstract meta class that has elemtary sigs and methods defined.
    All use case classes inherit from this, so they know all the signals for emission
    The useCaseClass is tho ONLY one that talks to the api.    

     """
    
    apiCalls = nxtQs() # static! dict of prototypes to be filled with vals for apiReq
    blinkerCols = [Qt.Qt.darkYellow, Qt.Qt.magenta]
   
    
    def __init__(self,  sessMan  ): # 
        """ just call the super init here: QObject.
       """        
        super(nxtUseCaseMeta, self).__init__()
        self.nxtApi = sessMan.nxtApi  # there is only ONE apiSigs instance, and that is in the sessMan.

 
 
 
 

class UC_Bridge1(nxtUseCaseMeta):
    """
       
            
            
            
tested examples for the BTC-NXT mappings implemented below, 
using two different curl syntax methods.


 
using bitcoind as jsonrpc relay:
----------------------------------
note: bitcoind does not seem to deliver well formed jsonrpc! 


TESTNET:

./bitcoind -rpcport=7879 getbalance 2865886802744497404 1
50068.83570152


./bitcoind -rpcport=7879 getconnectioncount
46


./bitcoind -rpcport=7879 getinfo
{
    "timeoffset" : 0,
    "keypoolsize" : 290386944,
    "paytxfee" : 0.00000000,
    "balance" : 0.00000000,
    "blocks" : 115901,
    "errors" : "",
    "protocolversion" : "1.1.4",
    "testnet" : false,
    "difficulty" : "2504768413821209",
    "keypoololdest" : 834666496,
    "walletversion" : "1.1.4",
    "connections" : 46,
    "version" : "1.1.4",
    "proxy" : ""
}




./bitcoind -rpcport=7879 getreceivedbyaccount 2865886802744497404
50069.83570152


./bitcoind -rpcport=7879 getreceivedbyaddress 2865886802744497404
50069.83570152



./bitcoind -rpcport=7879 gettransaction 1448848043607985937
{
    "timereceived" : 13323520,
    "txid" : "1448848043607985937",
    "time" : 13323520,
    "details" : [
        {
            "account" : "16159101027034403504",
            "address" : "2865886802744497404",
            "amount" : 3.00000000,
            "category" : "receive"
        }
    ],
    "confirmations" : 34860,
    "amount" : 3.00000000
}



./bitcoind -rpcport=7879 sendfrom xxxxxxxxxx 16159101027034403504 1.98765432 1 comm1 commTo 



./bitcoind -rpcport=7879 gettransaction 13184500470311816723



 ./bitcoind -rpcport=7879 sendfrom 14oreosetc14oreosetc 16159101027034403504 1.2340 1 comm1 commTo 
{
    "txid" : "11564054352935906995"
}

./bitcoind -rpcport=7879 sendfrom XXXXXXXXXXXXXXXX 16159101027034403504 1.2340 1 comm1 commTo 
{
    "txid" : "2732068724802022093"
}



./bitcoind -rpcport=7879 settxfee
{
    "settxfee" : "n/a"
}


./bitcoind -rpcport=7879 validateaddress   xxxxxxxxxxxx
{
    "ismine" : true,
    "address" : "2865886802744497404",
    "isvalid" : true
}


 

            """
  





   #     self.uc_bridge = nxtUC_Bridge.UC_Bridge1(self, self.qPool, host, port, self.bridgeLogger, self.consLogger, DB  )
       
    def __init__(self, sessMan, host = 'localhost', port = '6876',bridgeLogger=None , consLogger=None, DB=None  ):
        super(UC_Bridge1   , self   ).__init__(sessMan)
        self.sessMan = sessMan
        self.qPool = sessMan.qPool
        self.meta = {'caller':'Bridge1'}
        defPass17 = '0'                     #### THIS GOES TO SESSMAN- WALLET!
        acctSecKey = defPass17                      #### THIS GOES TO SESSMAN- WALLET!
        self.bridgeLogger = bridgeLogger
        self.consLogger = consLogger
        
        #        lg.info('nxtBridge listening on host %s : port %s', host, port)
        
        self.mm = BridgeThread( self.qPool, host  , port ,  bridgeLogger,  consLogger ,DB )
         
         
         
 
 
class BridgeThread(QObject):
    """ 2680262203532249785 nxt genesis block """
    # housekeeping of the threads may have to be taken care of
    
    
    def __init__(self, qPool, host, port, bridgeLogger, consLogger, DB ):
        # check : is this the same as calling super(BridgeThread, etc) ???????
        super(QObject, self).__init__( parent = None)
        self.DB=DB
        self.qPool = qPool
        self.host = host
        self.port = port
        self.bridgeLogger = bridgeLogger
        self.consLogger = consLogger
         
    
    
    @pyqtSlot() # 61
    def jsonServ_Slot(self, ):
        
        self.json_Runner = JSON_Runner( self.host, self.port, self.bridgeLogger, self.consLogger , self.qPool, self.DB) # json_Emitter, self to THIS !!!!!!
        self.json_Runner.setAutoDelete(False) 
        self.qPool.start(self.json_Runner)
    

     
        
class JSON_Runner(QtCore.QRunnable):
    """- This is what needs to be put into the QThreadpool """
    nxtApi = nxtApi
    
    def __init__(self,   host = 'localhost', port = '6876', fileLogger = None, consLogger = None , qPool=None, DB=None ): #emitter, 
        super(QtCore.QRunnable, self).__init__()
        global session # this must be global to be accessible from the dispatcher methods
        session = Session()
        headers = {'content-type': 'application/json'}
        sessUrl = 'http://' + host + ':' + port + '/nxt?' 
        global NxtReq
        
        # !!!! use a dedicated DBTrhead later on. Will be no problem! For now, make cursor objects as needed in the QTHreapool runnables
        # self.blockDBConn = DB[0]
        #self.blockDBCur = DB[1]
        
        NxtReq = Req( method='POST', url = sessUrl, params = {}, headers = headers        )
        self.bridgeLogger = fileLogger
        self.consLogger = consLogger
        self.qPool = qPool
        
  
  
############################
 # 2 generic Nxt APIs
    @dispatcher.add_method
    def getState(**kwargs):
        payload = { "requestType" : "getState" } 
        NxtApi = {}
        NxtApi['requestType'] =  payload['requestType'] # here we translate BTC params to NXT params
        NxtReq.params=NxtApi # same obj, only replace params
        preppedReq = NxtReq.prepare()
        response = session.send(preppedReq)
        NxtResp = response.json()
        
        Nxt2Btc = {}
        return NxtResp  

    @dispatcher.add_method
    def getTime( **kwargs):
        payload = { "requestType" : "getTime" } #getTime"   }
        NxtApi = {}
        NxtApi['requestType'] =  payload['requestType'] # here we translate BTC params to NXT params
        NxtReq.params=NxtApi # same obj, only replace params
        preppedReq = NxtReq.prepare()
        response = session.send(preppedReq)
        NxtResp = response.json()
        
        Nxt2Btc = {}
        return NxtResp  

  
#######################
#
# Function Calls implemented below
# Numbers as per appeearance in listing of bitcoind help 
   

# 14 getbalance               <.-.-.-. access wallet: account - addrress mapping
# 21 getconnectioncount
# 25 getinfo 

# 33 getreceivedbyaccount    <.-.-.-. access wallet: iterate over ALL TXs in NXT acct(s) and sum the INCOMING NXT TXs
# 34 getreceivedbyaddress    <.-.-.-. access wallet: iterate over ALL TXs in NXT acct and sum the INCOMING NXT TXs

# 35 gettransaction
# 52 sendfrom                    <.-.-.-. access wallet: simply map acct->addr. ultimatley sendfrom sends from address
# 58 settxfee
# 63 validateaddress

# 15 getbestblockhash 
# 16 getblock          
# 17 getblockcount   
# 18 getblockhash      <------- db: height-blockaddress OK!   


# missing

# getnewaddress              <.-.-.-. access wallet

# sendtoaddress                  <.-.-.-. access wallet

# listunspent             <.-.-.-. access wallet

# listsinceblock

 
  
#######################
#######################
#######################
#######################
#######################
#######################


#######################
# 14 getbalance
  
    @dispatcher.add_method
    def getbalance( **kwargs):
        """ Mapping Commentary. See keys at [Nxt2Btc_Mapping_Comments] in docstring of def application()
        1   getbalance
        
        2   [account] [minconf=1]	
        
        3   If [account] is not specified, returns the server's total available balance.
            If [account] is specified, returns the balance in the account.
        
        4   N	
        
        5   Y	
        
        6   return is a float 0.00000000

        7   http://localhost:7876/nxt?requestType=getBalance&account=ACCOUNT	

        8   {
            "unconfirmedBalanceNQT": UNCONFBALANCENQT,
            "effectiveBalanceNXT": EFFBALANCENXT,
            "balanceNQT": BALANCENQT
            }	

        9   here we use the account to pass in an NXT account number so you can enquire any account and dont need the secret phrase
            run this command for the specified nxt account return the BALANCENQT - <account> is required
        
        EXAMPLE:
                 
        curl -i -X POST -d '{"jsonrpc": "2.0", "method": "getbalance", "params": {"account":"16159101027034403504","minconf":"1"}, "id": 12}' http://localhost:7879/jsonrpc
        
        HTTP/1.0 200 OK
        Content-Type: application/json
        Content-Length: 81
        Server: Werkzeug/0.9.4 Python/3.4.0
        Date: Tue, 27 May 2014 13:10:34 GMT
        
        {"result": {"16159101027034403504": "4061839895698"}, "id": 12, "jsonrpc": "2.0"}azure@boxfish:~/workbench/nxtDev/BRIDGE$ 




        """
        # only gets 'params' - but jsonHandler needs full json
        ACCOUNT = kwargs["account"] #kwargs['account']
        
        # can replace the specific account no. with generic 'account' key
        
        payload = { "requestType" : "getBalance" } #getTime"   }
        NxtApi = {}
        NxtApi['requestType'] =  payload['requestType'] # here we translate BTC params to NXT params
        NxtApi['account'] = ACCOUNT 
        NxtReq.params=NxtApi # same obj, only replace params
        preppedReq = NxtReq.prepare()
        response = session.send(preppedReq)
        NxtResp = response.json()

        #print("NxtResp" + str(NxtResp))

        Nxt2Btc = {}
        try:

         
            Nxt2Btc =  {
                        'ACCOUNT' : float(NxtResp['balanceNQT'] ) * 0.00000001
                        }
         
         
        #            Nxt2Btc =  {
        #                        ACCOUNT: float(NxtResp['balanceNQT'])
        #                        }

        
        except:
            Nxt2Btc =  {
                        ACCOUNT: 0.0
                        }
            
        return Nxt2Btc  
 
 
#########################
# 21 getconnectioncount
   
    @dispatcher.add_method
    def getconnectioncount( **kwargs):
        """ Mapping Commentary. See keys at [Nxt2Btc_Mapping_Comments] in docstring of def application()
        
        
        1    getconnectioncount		
        
        2
        
        3    Returns the number of connections to other nodes.	
        
        4   N	
        
        5   Y	
        
        6       returns int of number of connections	
        
        7       ? requestType=getState	
        
        8       {
        "numberOfPolls": NUMPOLLS,
        "numberOfVotes": NUMVOTES,
        "numberOfTrades": NUMTRADES,
        "lastBlock": "LASTBLOCKID",
        "numberOfAliases": NUMALIASES,
        "lastBlockchainFeeder": "FEEDERPEER",
        "numberOfBlocks": HEIGHT,
        "numberOfPeers": NUMPEERS
        "totalMemory": CURMEMORY,
        "freeMemory": FREEMEMORY,
        "maxMemory": MAXMEMORY,
        "numberOfTransactions": NUMTRANS,
        "numberOfUnlockedAccounts": NUMUSERS,
        "version": "VERSION",
        "numberOfOrders": NUMORDERS,
        "totalEffectiveBalanceNXT": EFFECTIVEBALANCE
        "time": TIME,
        "availableProcessors": NUMPROCESSORS,
        "numberOfAssets": NUMASSETS,
        "cumulativeDifficulty": "CUMEDIFF"
        "numberOfAccounts": NUMACCOUNTS
        }	
        
        9   return numberOfPeers
        
        """
        payload = { "requestType" : "getState" }  
        NxtApi = {}
        NxtApi['requestType'] =  payload['requestType'] # here we translate BTC params to NXT params
        NxtReq.params=NxtApi # same obj, only replace params
        preppedReq = NxtReq.prepare()
        response = session.send(preppedReq)
        NxtResp = response.json()
        Nxt2Btc = {}
         
        Nxt2Btc =  {
                    'numberOfPeers':NxtResp['numberOfPeers']
                    }
        
        return Nxt2Btc  
 
  

#########################
# 25 getinfo 
    @dispatcher.add_method
    def getinfo( **kwargs):
        """ Mapping Commentary. See keys at [Nxt2Btc_Mapping_Comments] in docstring of def application()
        
        1        getinfo
        
        2        None
        
        3        Returns an object containing various state info.
        
        4        N
        
        5        Y
        
        6        Returns JSON as follows
        
        {
        "version" : 80300,
        "protocolversion" : 70001,
        "walletversion" : 60000,
        "balance" : 0.00000000,
        "blocks" : 253584,
        "timeoffset" : -5,
        "connections" : 13,
        "proxy" : "",
        "difficulty" : 50810339.04827648,
        "testnet" : false,
        "keypoololdest" : 1373494595,
        "keypoolsize" : 101,
        "paytxfee" : 0.00000000,
        "errors" : ""
        }	
        
        7        ? requestType=getState	
        
        8        {
        "numberOfPolls": NUMPOLLS,
        "numberOfVotes": NUMVOTES,
        "numberOfTrades": NUMTRADES,
        "lastBlock": "LASTBLOCKID",
        "numberOfAliases": NUMALIASES,
        "lastBlockchainFeeder": "FEEDERPEER",
        "numberOfBlocks": HEIGHT,
        "numberOfPeers": NUMPEERS
        "totalMemory": CURMEMORY,
        "freeMemory": FREEMEMORY,
        "maxMemory": MAXMEMORY,
        "numberOfTransactions": NUMTRANS,
        "numberOfUnlockedAccounts": NUMUSERS,
        "version": "VERSION",
        "numberOfOrders": NUMORDERS,
        "totalEffectiveBalanceNXT": EFFECTIVEBALANCE
        "time": TIME,
        "availableProcessors": NUMPROCESSORS,
        "numberOfAssets": NUMASSETS,
        "cumulativeDifficulty": "CUMEDIFF"
        "numberOfAccounts": NUMACCOUNTS
        }	
        
        9        Returns JSON as follows
        
        {
        "version" : VERSION,
        "protocolversion" : VERSION,
        "walletversion" : VERSION,
        "balance" : 0.00000000,
        "blocks" : HEIGHT,
        "timeoffset" : 0,
        "connections" : NUMPEERS,
        "proxy" : "",
        "difficulty" : CUMEDIFF,
        "testnet" : false,
        "keypoololdest" : CURMEMORY,
        "keypoolsize" : FREEMEMORY,
        "paytxfee" : 0.00000000,
        "errors" : ""
        }
        
        EXAMPLES:
        
        curl --user 'anyName:anyPW' --data-binary '{"jsonrpc":"1.0","id":"curltext","method":"getinfo","params":[]}' -H 'content-type:text/plain;' http://127.0.0.1:7879/jsonrpc

        curl -i -X POST -d '{"jsonrpc": "2.0", "method": "getinfo", "params": { "": "","":""}, "id": 7}' http://localhost:7879/jsonrpc

        """
        # no self. all we know here MUST be supplied in kwargs.

        payload = { "requestType" : "getState" } #getTime"   }
        NxtApi = {}
        NxtApi['requestType'] =  payload['requestType'] # here we translate BTC params to NXT params
        NxtReq.params=NxtApi # same obj, only replace params
        preppedReq = NxtReq.prepare()
        response = session.send(preppedReq)
        NxtResp = response.json()
        VERSION = NxtResp['version']
        HEIGHT = NxtResp['numberOfBlocks']
        NUMPEERS = NxtResp['numberOfPeers']
        CUMEDIFF = NxtResp['cumulativeDifficulty']
        CURMEMORY = NxtResp['totalMemory']
        FREEMEMORY = NxtResp['freeMemory']
        FALSE = False
        Nxt2Btc = {}
        Nxt2Btc =  {
                    "version" : VERSION,
                    "protocolversion" : VERSION,
                    "walletversion" : VERSION,
                    "balance" : 0.00000000,
                    "blocks" : HEIGHT,
                    "timeoffset" : 0,
                    "connections" : NUMPEERS,
                    "proxy" : "",
                    "difficulty" : CUMEDIFF,
                    "testnet" :  FALSE,
                    "keypoololdest" : CURMEMORY,
                    "keypoolsize" : FREEMEMORY,
                    "paytxfee" : 0.00000000,
                    "errors" : ""
                    }
        #print("~~~~~~~~>" + str( self.qPool.activeThreadCount() ))    # this line is  for timing the delay in the # QThread to wait for the proper delay time

        return Nxt2Btc  


 
##################################################
 
# 33 getreceivedbyaccount
         
    @dispatcher.add_method
    def getreceivedbyaccount( **kwargs):
        """ Mapping Commentary. See keys at [Nxt2Btc_Mapping_Comments] in docstring of def application()
                 
        1   getreceivedbyaccount	
        
        2   [account] [minconf=1]	
        
        3   Returns the total amount received by addresses with [account] in transactions with at least [minconf] confirmations. If [account] not provided return will include all transactions to all accounts. (version 0.3.24)
        
        4   N	
        
        5   Y	
        
        6   account=walletaccountnumber, minconf=10, returns float 0.00000000	
        
        7   http://localhost:7876/nxt?
        requestType=getBalance&
        account=ACCOUNT
        
        8	
        
        {
        "guaranteedBalanceNQT": "GUARANTEED_BALANCE",
        "balanceNQT": "BALANCENQT",
        "effectiveBalanceNXT": EFFBALANCENXT,
        "unconfirmedBalanceNQT": "UNCONFBALANCENQT",
        "forgedBalanceNQT": "FORGEDBAL"
        }	
        
        9   Pass in the nxt account number and return GUARANTEED_BALANCE as float


        EXAMPLES:
        
        curl --user 'anyName:anyPW' --data-binary '{"jsonrpc":"1.0","id":"curltext","method":"getreceivedbyaccount","params":  {"account":"16159101027034403504"} }' -H 'content-type:text/plain;' http://127.0.0.1:7879/jsonrpc

        {"result": {"16159101027034403504": 4061839895698.0}, "id": "curltext", "jsonrpc": "2.0"}


        
        curl -i -X POST -d '{"jsonrpc": "2.0", "method": "getreceivedbyaccount", "params": {"account":"16159101027034403504","minconf":"1"}, "id": 12}' http://localhost:7879/jsonrpc
        
        {"result": {"16159101027034403504": 4061839895698.0}, "id": 12, "jsonrpc": "2.0"}



        """
        #print("getreceivedbyaccount" +str(kwargs))   
        ACCOUNT = kwargs["account"] #kwargs['account']
        payload = { "requestType" : "getBalance" } #getTime"   }
        NxtApi = {}
        NxtApi['requestType'] =  payload['requestType'] # here we translate BTC params to NXT params
        NxtApi['account'] = ACCOUNT 
        NxtReq.params=NxtApi # same obj, only replace params
        preppedReq = NxtReq.prepare()
        response = session.send(preppedReq)
        NxtResp = response.json()
        Nxt2Btc = {}


        Nxt2Btc =  {
                    'ACCOUNT' : float(NxtResp['balanceNQT'] ) * 0.00000001
                    }
     
          
        
        return Nxt2Btc  
        
        
        
        
        
        
# 34 getreceivedbyaddress
 
    @dispatcher.add_method
    def getreceivedbyaddress( **kwargs):
        """ Mapping Commentary. See keys at [Nxt2Btc_Mapping_Comments] in docstring of def application()
             
             
                     
        
        1   getreceivedbyaddress	
        
        2   <bitcoinaddress> [minconf=1]	
        
        3   Returns the amount received by <bitcoinaddress> in transactions with at least [minconf] confirmations. It correctly handles the case where someone has sent to the address in multiple transactions. Keep in mind that addresses are only ever used for receiving transactions. Works only for addresses in the local wallet, external addresses will always show 0.
        
        4   N
        
        5   Y	
        
        6   address=bitcoinaddress, minconf=10, returns float 0.00000000	
        
        7   http://localhost:7876/nxt?
        requestType=getAccountId&
        secretPhrase=PASSPHRASE
        Followed by
        http://localhost:7876/nxt?
        requestType=getBalance&
        account=ACCOUNT	
        
        8   Use bitcoinaddress as the secret phrase to return the NXT account ID
        
        {
        "GUARANTEED_BALANCE",
        "GUARANTEED_BALANCE",
        "BALANCENQT",
        "BALANCENQT",
        EFFBALANCENXT,
        EFFBALANCENXT,
        "unconfirmedBalanceNQT": "UNCONFBALANCENQT",
        "FORGEDBAL"
        "FORGEDBAL"
        }	
        
        9   In this model I have mapeed bitcoinaddress as the NXT secretphrase passed to the server return GUARANTEED_BALANCE as float
        
        
        
        EXAMPLES:
        
        
        curl --user 'anyName:anyPW' --data-binary '{"jsonrpc":"1.0","id":"curltext","method":"getreceivedbyaddress","params":  {"account":"16159101027034403504"} }' -H 'content-type:text/plain;' http://127.0.0.1:7879/jsonrpc
        
        {"jsonrpc": "2.0", "id": "curltext", "result": {"16159101027034403504": 4061839895698.0}}


        
        curl -i -X POST -d '{"jsonrpc": "2.0", "method": "getreceivedbyaddress", "params": {"account":"16159101027034403504","minconf":"1"}, "id": 12}' http://localhost:7879/jsonrpc
        
        {"jsonrpc": "2.0", "id": 12, "result": {"16159101027034403504": 4061839895698.0}}




        """
        #print("getreceivedbyaddress" +str(kwargs))   
        ACCOUNT = kwargs["account"] #kwargs['account']
        payload = { "requestType" : "getBalance" } #getTime"   }
        NxtApi = {}
        NxtApi['requestType'] =  payload['requestType'] # here we translate BTC params to NXT params
        NxtApi['account'] = ACCOUNT 
        NxtReq.params=NxtApi # same obj, only replace params
        preppedReq = NxtReq.prepare()
        response = session.send(preppedReq)
        NxtResp = response.json()
        Nxt2Btc = {}
         
        
        Nxt2Btc =  {
                    'ACCOUNT' : float(NxtResp['balanceNQT'] ) * 0.00000001
                    }
     
        return Nxt2Btc  
         
        
      

# 35 gettransaction
  
        
        
    @dispatcher.add_method
    def gettransaction( **kwargs):
        """ Mapping Commentary. See keys at [Nxt2Btc_Mapping_Comments] in docstring of def application()
                 
        1   gettransaction	
        
        2   <txid>	
        
        3   Returns an object about the given transaction containing:
        "amount" : total amount of the transaction
        "confirmations" : number of confirmations of the transaction
        "txid" : the transaction ID
        "time" : time associated with the transaction[1].
        "details" - An array of objects containing:
        "account"
        "address"
        "category"
        "amount"
        "fee"
        
        4   N
        
        5   Y
        
        6	{
        "amount" : 0.05000000,
        "confirmations" : 0,
        "txid" : "9ca8f969bd3ef5ec2a8685660fdbf7a8bd365524c2e1fc66c309acbae2c14ae3",
        "time" : 1392660908,
        "timereceived" : 1392660908,
        "details" : [
        {
        "account" : "",
        "address" : "1hvzSofGwT8cjb8JU7nBsCSfEVQX5u9CL",
        "category" : "receive",
        "amount" : 0.05000000
        }
        ]
        }
        
        7	http://localhost:7876/nxt?
        requestType=getTransaction&
        transaction=TRANSID<txid>	{
        
        8   "sender": "SENDERACCOUNT",
        "senderRS": "SENDERACCOUNTRS",
        "feeNQT": "FEE",
        "amountNQT": "AMOUNT",
        "timestamp": TIME,
        "referencedTransaction": REFTX,
        "confirmations": CONFIRMS,
        "subtype": SUBTYPE,
        "block": "BLOCKID",
        "senderPublicKey": "PUBKEY",
        "type": TYPE,
        "deadline": DEADLINE,
        "signature": "SIGNATURE",
        "recipient": "RECIPACCOUNT",
        "recipientRS": "RECIPACCOUNTRS",
        "fullHash": "FULLHASH", 
        "signatureHash": "SIGHASH", 
        "hash": "HASH", 
        "transaction": "TRANSID", 
        "attachment":
        {
        ATTACHMENT
        }
        }	
        
        9   Pass in a NXT tx id previously obtained and get information on the confirmation status of that.
        {
        "amount" : float(AMOUNT),
        "confirmations" : CONFIRMS,
        "txid" : TRANSID
        "time" : TIME,
        "timereceived" : TIME,
        "details" : [
        {
        "account" : “”,
        "address" : RECIPACCOUNT 
        "category" : "receive",
        "amount" : AMOUNT
        }
        ]
        }
         
        
        ./bitcoin-cli help gettransaction
        gettransaction "txid"
        
        Get detailed information about in-wallet transaction <txid>
        
        Arguments:
        1. "txid"    (string, required) The transaction id
        
        Result:
        {
          "amount" : x.xxx,        (numeric) The transaction amount in btc
          "confirmations" : n,     (numeric) The number of confirmations
          "blockhash" : "hash",  (string) The block hash
          "blockindex" : xx,       (numeric) The block index
          "blocktime" : ttt,       (numeric) The time in seconds since epoch (1 Jan 1970 GMT)
          "txid" : "transactionid",   (string) The transaction id, see also https://blockchain.info/tx/[transactionid]
          "time" : ttt,            (numeric) The transaction time in seconds since epoch (1 Jan 1970 GMT)
          "timereceived" : ttt,    (numeric) The time received in seconds since epoch (1 Jan 1970 GMT)
          "details" : [
            {
              "account" : "accountname",  (string) The account name involved in the transaction, can be "" for the default account.
              "address" : "bitcoinaddress",   (string) The bitcoin address involved in the transaction
              "category" : "send|receive",    (string) The category, either 'send' or 'receive'
              "amount" : x.xxx                  (numeric) The amount in btc
            }
            ,...
          ],
          "hex" : "data"         (string) Raw data for transaction
        }
          
        
        BITCOIN TX REPLY:
        curl --user 'rpcNxtBitcoin:4JLstlAJ6gJyV1DHv2' --data-binary '{"jsonrpc":"1.0","id":"curltext","method":"gettransaction","params":["f0b20213346b14361795a9a387ac28078dc9a8a14fd9ced4f7b32eab9966820f"]}' -H 'content-type:text/plain;' http://127.0.0.1:8332
        {"result":{
        
        "amount":-0.00010000,
        "fee":-0.00010000,
        "confirmations":5521,
        "blockhash":"0000000000000000091ae589c034bc0466e2feca51dc018bb2c3303e8ab8648b",
        "blockindex":156,
        "blocktime":1398350348,
        "txid":"f0b20213346b14361795a9a387ac28078dc9a8a14fd9ced4f7b32eab9966820f",
        "walletconflicts":[],
        "time":1398349976,
        "timereceived":1398349976,
        "details":[
        		{"account":"",
                   "address":"19SCQ8fWR4sChAPwbfNACsv1s6CNspF6Yh",
                   "category":"send",
                   "amount":-0.00010000,
                   "fee":-0.00010000}
        
        ],
        "hex":"0100000001033e27a990fe6f3dba62493dcd59b16405dab0bcf2bdcf9b098b613dfb614790010000006b483045022100f61632e64c9b47a70445166bb5de5bae6d8d099ba96ac0d1219842ac2fdb6c0902204be319107f76dee45e5332a10202c6152da7c0391e91397c273d036b95c4d88d01210272518a71e864d296ca61efd5bd8be6061afa70248462c958b58f52afaff6b688ffffffff0250c30000000000001976a9147fa916934255d62febf440a3fad445e1d743d95a88ac10270000000000001976a9145c84ebab10bdf995178e972e5aac94c6b1c5405688ac00000000"},
        "error":null,
        "id":"curltext"
        }





         Nxt testNet TX: 1448848043607985937
              
        
        
        Nxt full getTransaction reply:
        
        {
            "fullHash": "110fc68c9e571b14bb05bcd7d64aea5ae342a4fa80f32deb85be4bdf285ef8d4",
            "confirmations": 29448,
            "signatureHash": "8169819b0f3f6e950db238ba5dab2c7080b5754c2630eb4d4b3ebdf8639e65d6",
            "transaction": "1448848043607985937",
            "amountNQT": "300000000",
            "block": "9383935361491353106",
            "recipientRS": "NXT-3P9W-VMQ3-9DRR-4EFKH",
            "type": 0,
            "feeNQT": "100000000",
            "recipient": "2865886802744497404",
            "sender": "16159101027034403504",
            "timestamp": 13323520,
            "height": 81053,
            "subtype": 0,
            "senderPublicKey": "f9cecd0a2d38afcb4a799ec7e7c718ce451053bd2a2924c15fbd5922aa915825",
            "deadline": 180,
            "blockTimestamp": 13323576,
            "senderRS": "NXT-L6PJ-SMZ2-5TDB-GA7J2",
            "signature": "b210c5b3e1fa28c9aa5c5fd05d2e6ca64869b191d3d4bc04369f06ffdcffc8044fce36f2825b155ba2be9eeef10a1644306609c965632e638598ee954684c86e"
        }
        
        
                
        EXAMPLES:
        
        curl -i -X POST -d '{"jsonrpc": "2.0", "method": "gettransaction", "params": {"txid":"1448848043607985937"}, "id": 12}' http://localhost:7879/jsonrpc
        
        {"result": {"amount": 300000000.0, "details": [{"amount": 300000000.0, "account": "16159101027034403504", "category": "receive", "address": "2865886802744497404"}], "time": 13323520, "timereceived": 13323520, "confirmations": 29471, "txid": "1448848043607985937"}, "jsonrpc": "2.0", "id": 12} 
        
        
        curl --user 'anyName:anyPW' --data-binary '{"jsonrpc":"1.0","id":"curltext","method":"gettransaction","params":  {"txid":"1448848043607985937"} }' -H 'content-type:text/plain;' http://127.0.0.1:7879/jsonrpc
        
        {"result": {"amount": 300000000.0, "details": [{"amount": 300000000.0, "account": "16159101027034403504", "category": "receive", "address": "2865886802744497404"}], "time": 13323520, "timereceived": 13323520, "confirmations": 29473, "txid": "1448848043607985937"}, "jsonrpc": "2.0", "id": "curltext"}
 


        """
        
        TXid = kwargs["txid"] #kwargs['account']
        try:
            TX_hash = kwargs['hash']
        except:
            TX_hash = ''
        payload = { "requestType" : "getTransaction" }  
        
        NxtApi = {}
        NxtApi['requestType'] =  payload['requestType'] # here we translate BTC params to NXT params
        NxtApi['transaction'] = TXid
        NxtApi['hash'] = TX_hash 
        
        NxtReq.params=NxtApi # same obj, only replace params
        preppedReq = NxtReq.prepare()
        response = session.send(preppedReq)
        NxtResp = response.json()
        

        try:        
            CONFIRMS = NxtResp['confirmations']
        except:
            CONFIRMS = 0
            print(str(NxtResp))
        TRANSID = NxtResp['transaction']
        TIME = NxtResp['timestamp']
        SENDER = NxtResp['sender']
        RECIPIENT = NxtResp['recipient']
        
        AMOUNT = NxtResp['amountNQT']
        AMOUNT =  float(AMOUNT)
        AMOUNT = AMOUNT * 0.00000001
        #print(str(NxtResp))
        Nxt2Btc = {}
        Nxt2Btc =  {
                "amount" : float(AMOUNT),
                "confirmations" : CONFIRMS,
                "txid" : TRANSID,
                "time" : TIME,
                "timereceived" : TIME,
                "details" : [
                            {
                            "account" : SENDER,
                            "address" : RECIPIENT,
                            "category" : "receive",
                            "amount" : float(AMOUNT)
                            }
                            ]
                            }
                    
        return Nxt2Btc  
 


# 52 sendfrom
        
    @dispatcher.add_method
    def sendfrom( **kwargs):
        """ Mapping Commentary. See keys at [Nxt2Btc_Mapping_Comments] in docstring of def application()
 
            
            1   sendfrom	
            
            2   <fromaccount> <tobitcoinaddress> <amount> [minconf=1] [comment] [comment-to]	
            
            3   <amount> is a real and is rounded to 8 decimal places. Will send the given amount to the given address, ensuring the account has a valid balance using [minconf] confirmations. Returns the transaction ID if successful (not in JSON object).	
            
            4   Y	
            
            5   N	
            
            6   { “txid” : “<txid>” }	
            
            7   http://localhost:7876/nxt?
            requestType=sendMoney&
            secretPhrase=<fromaccount>&
            recipient=<tobitcoinaddress>& 
            amountNQT=<amount>& 
            feeNQT=(from set tx fee)& 
            deadline=(default 1440)	
            
            8   { 
            "transaction": "TRANSACTIONID" 
            }	
            
            9   Would have preferred a better bitcond call here as I swap the use of accont and address but I dont see any other option
            use the <fromaccount> to pass the secretphrase for the NXT account, <tobitcoinaddress> becomes the nxt account number, need to convert the float amount into NQT the fee should be defaulted to the minimum or set using set tx fee command, convert the json to pass back the transaction id
            # NOTE: THE AMOUNT IS PASSED IN AS NXT.NQT AND IS CONVERTED TO NQT HERE
            
            EXAMPLES:
            
            curl -i -X POST -d '{"jsonrpc": "2.0", "method": "sendfrom", "params": {"amount":0.00001, "fromaccount":"SECRETPHRASE",  "tobitcoinaddress":"1234567890123456789",  "minconf":1,  "comment":"" , "comment-to":"" }, "id": 12}' http://localhost:7879/jsonrpc
            
            {"jsonrpc": "2.0", "id": 12, "result": {"txid": "948172143107956553"}
            
            
            
            
            curl --user 'anyName:anyPW' --data-binary '{"jsonrpc":"1.0","id":"curltext","method":"sendfrom","params":  {"amount":0.00003, "fromaccount":"SECRETPHRASE",  "tobitcoinaddress":"1234567890123456789",  "minconf":1,  "comment":"" , "comment-to":"" } }' -H 'content-type:text/plain;' http://127.0.0.1:7879/jsonrpc
            {"jsonrpc": "2.0", "id": "curltext", "result": {"txid": "16837301710895534070"}}
            
            
            CORRECT INTERNAL NXT SERVER DICT:
            {'fullHash': 'ce2964c99d93d21688f9755a8bc0b6928f8d01306e5846c0ac9525665e24e42d', 'transaction': '1644539119841585614', 'unsignedTransactionBytes': '00004dfbf3000100f9cecd0a2d38afcb4a799ec7e7c718ce451053bd2a2924c15fbd5922aa915825fcd410ecdcacc527e80300000000000000e1f50500000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000', 'signatureHash': '7e7829a740b5c2286eb698ad6dd3b90ce15d56c70b6343135cd548dbb3177aeb', 'transactionBytes': '00004dfbf3000100f9cecd0a2d38afcb4a799ec7e7c718ce451053bd2a2924c15fbd5922aa915825fcd410ecdcacc527e80300000000000000e1f505000000000000000000000000000000000000000000000000000000000000000000000000054cc9b39f8e5644a06976f92883876451b427890763c6f38746fd8fe27a85022e6bd35254e937fa321083835ed5034e7ca9fb7c3987627066408720077a434b', 'broadcasted': True}
            
            127.0.0.1 - - [28/May/2014 15:33:02] "POST /jsonrpc HTTP/1.1" 200 -

            """


 
        payload = { "requestType" : "sendMoney" }  
        # NOTE: THE AMOUNT IS PASSED IN AS NXT.NQT AND IS CONVERTED TO NQT HERE
        amountNQT = int( float(kwargs['amount'] ) * 100000000 )
        
        NxtApi = {}
        NxtApi['requestType'] =  payload['requestType'] # here we translate BTC params to NXT params
        NxtApi['publicKey'] =  ""
        NxtApi['referencedTransaction'] =  ""
        NxtApi['secretPhrase'] =  kwargs['fromaccount']
        NxtApi['deadline'] =  kwargs['minconf']
        NxtApi['feeNQT'] =  "100000000"
        NxtApi['amountNQT'] = amountNQT
        NxtApi['recipient'] =  kwargs['tobitcoinaddress']
        
        NxtReq.params=NxtApi # same obj, only replace params
        preppedReq = NxtReq.prepare()
        response = session.send(preppedReq)
        NxtResp = response.json()
        
        
        try:
            
            TX_ID = NxtResp['transaction']
        except:
            TX_ID = 'errorDescription'
        Nxt2Btc = {}
        Nxt2Btc =  {
                
                "txid" : TX_ID,
                
                            }
                    
        return Nxt2Btc  
 

 
  

# 58 settxfee
 
    @dispatcher.add_method
    def settxfee( **kwargs):
        """ Mapping Commentary. See keys at [Nxt2Btc_Mapping_Comments] in docstring of def application()
         
                 
                 
        
        1   settxfee	
        
        2   <amount>	<amount> 
        
        3   is a real and is rounded to the nearest 0.00000001	
        
        4   N	
        
        5   Y	
        
        6   returns true	
        
        7   no api	
        
        8   n/a	
        
        9   use to set the default tx fee in nxtcoind


        EXAMPLES:
        
        """
        #print("settxfee"+str(kwargs))   
        payload = { "requestType" : "getState" } #getTime"   }
        NxtApi = {}
        NxtApi['requestType'] =  payload['requestType'] # here we translate BTC params to NXT params
        NxtReq.params=NxtApi # same obj, only replace params
        #preppedReq = NxtReq.prepare()
        #response = session.send(preppedReq)
        #NxtResp = response.json()
        Nxt2Btc = {}
        Nxt2Btc =  {
                    "settxfee" : "n/a"
                    }
        
        return Nxt2Btc  



# 63 validateaddress

    @dispatcher.add_method
    def validateaddress( **kwargs):
        """ Mapping Commentary. See keys at [Nxt2Btc_Mapping_Comments] in docstring of def application()
         
                 
        1   validateaddress	
        
        2   <bitcoinaddress>	
        
        3   Return information about <bitcoinaddress>.	
        
        4   N	
        
        5   Y	
        
        6   {
            "isvalid" : true,
            "address" : "168La15SRLLaJBz6zUrxxyDQXU6cnzoHS2",
            "ismine" : false
            }
            
        7   http://localhost:7876/nxt?
            requestType=getAccountId& secretPhrase=PASSPHRASEhttp://local
            
            Follwed by 
            
            Host:7876/nxt?
            requestType=getAccountPublicKey&
            account=ACCOUNTNUM	
        
        8   {
            "publicKey": "PUBKEY"
            }	
            
        9   Convert as follows – isvalid=true if pubkey exists, ismine=true as secretphrase is known and address is passed back using secretphrease to be consistent
            {
            "isvalid" : IFPUBKEY(true),
            "address" : "PASSPHRASE",
            "ismine" : true
            }

          

        EXAMPLES:
        
        
        curl -i -X POST -d '{"jsonrpc": "2.0", "method": "validateaddress", "params": {"PASSPHRASE":"XXXXXXXXXXXXXXXX"}, "id": 12}' http://localhost:7879/jsonrpc
        
        {"jsonrpc": "2.0", "result": {"ismine": true, "address": "16159101027034403504", "isvalid": true}, "id": 12}azure@boxfish:~/workbench/nxtDev/BRIDGE$ ^C
        
        
        
        curl --user 'anyName:anyPW' --data-binary '{"jsonrpc":"1.0","id":"curltext","method":"validateaddress","params": {"PASSPHRASE":"XXXXXXXXXXXXXXXX"} }' -H 'content-type:text/plain;' http://127.0.0.1:7879/jsonrpc
        
        {"jsonrpc": "2.0", "result": {"ismine": false, "address": "16159101027034403504", "isvalid": true}, "id": "curltext"}azure@boxfish:~/workbench/nxtDev/BRIDGE$  




        """
       
        payload = { "requestType" : "getAccountId" } 
        NxtApi = {}
        NxtApi['requestType'] =  payload['requestType'] # here we translate BTC params to NXT params
        NxtApi['secretPhrase'] =  kwargs['PASSPHRASE'] # here we translate BTC params to NXT params
        NxtReq.params=NxtApi # same obj, only replace params
        preppedReq = NxtReq.prepare()
        response = session.send(preppedReq)
        NxtResp1 = response.json()
        #print(" NxtResp1 "+str(NxtResp1))   

        ACCOUNT = NxtResp1['accountId']

        
        payload = { "requestType" : "getForging" } 
        NxtApi = {}
        NxtApi['requestType'] =  payload['requestType'] # here we translate BTC params to NXT params
        NxtApi['secretPhrase'] =  kwargs['PASSPHRASE'] # here we translate BTC params to NXT params
        NxtReq.params=NxtApi # same obj, only replace params
        preppedReq = NxtReq.prepare()
        response = session.send(preppedReq)
        NxtResp2 = response.json()
 
        if "errorCode" in NxtResp2.keys():
            isForging = False
        elif "remaining" in NxtResp2.keys():
            isForging = True
   

        payload = { "requestType" : "getAccountPublicKey" } #getTime"   }
        NxtApi = {}
        NxtApi['requestType'] =  payload['requestType'] # here we translate BTC params to NXT params
        NxtApi['account'] =  ACCOUNT
        #ACCOUNT = kwargs["account"] #kwargs['account']
        NxtReq.params=NxtApi # same obj, only replace params
        preppedReq = NxtReq.prepare()
        response = session.send(preppedReq)
        NxtResp3 = response.json()
         
        if "errorCode" in NxtResp3.keys():
            isvalid = False
        elif "publicKey" in NxtResp3.keys():
            isvalid = True
            
            
        Nxt2Btc = {}
        Nxt2Btc =  {
                    "isvalid" : isvalid,
                    "address" : ACCOUNT,
                    "ismine" : isForging
                    }
        
        return Nxt2Btc  






####################################
####################################
####################################
####################################
####################################







# 15 getblockcount
 
    @dispatcher.add_method
    def getblockcount( **kwargs):
        """ Mapping Commentary. See keys at [Nxt2Btc_Mapping_Comments] in docstring of def application()
         
         ./bitcoind -rpcport=7879 getblockcount
         163467


        """
        payload = { "requestType" : "getState" }  
        NxtApi = {}
        NxtApi['requestType'] =  payload['requestType'] # here we translate BTC params to NXT params
        
        NxtReq.params=NxtApi # same obj, only replace params
        preppedReq = NxtReq.prepare()
        response = session.send(preppedReq)
        NxtResp = response.json()
        
        # NB: since block height and block count differ by one, the number of blocks is always larger by ONE than the height of the highest block.
        # However, bitcoind returns a correct blockhash to 'getblockhash' when given the blockcount, NOT the height of the highest block.
        # I *SUSPECT* that bitcoind amends this internally. 
        # So when having the numberOfBlocks of NXT, the blockHeight of the highest block is still numberOfBlocks MINUS ONE!
        # This is more consistent with the database and less source of confusion.         
        
        try:
            numberOfBlocks = int(NxtResp['numberOfBlocks']) # CHECK THIS OUT!!! - 1
        except:
            numberOfBlocks = 'errorDescription'
        Nxt2Btc = {}
        Nxt2Btc =  {
                "numberOfBlocks" : numberOfBlocks,
                            }
        return Nxt2Btc  

        #"numberOfBlocks": 127310,

# NB: bitcoin: genesis: Hight

    @dispatcher.add_method
    def getbestblockhash( **kwargs):
        """ Mapping Commentary. See keys at [Nxt2Btc_Mapping_Comments] in docstring of def application()
         
         ./bitcoind -rpcport=7879 getbestblockhash
         1639453107654839557


        """

        # 2 calls: gestate first, then getBlock!!
        payload = { "requestType" : "getState" }  
        NxtApi = {}
        NxtApi['requestType'] =  payload['requestType'] # here we translate BTC params to NXT params
        
        NxtReq.params=NxtApi # same obj, only replace params
        preppedReq = NxtReq.prepare()
        response = session.send(preppedReq)
        NxtResp = response.json()
        
        try:
            lastBlock = NxtResp['lastBlock']
        except:
            numberOfBlocks = 'errorDescription'
            
        # special: double call: now getBlock
        payload = { "requestType" : "getBlock" }  
        NxtApi = {}
        NxtApi['requestType'] =  payload['requestType'] # here we translate BTC params to NXT params
        NxtApi['block'] =  lastBlock # here we translate BTC params to NXT params
        Nxt2Btc = {}
        Nxt2Btc =  {
                "lastBlock" : lastBlock,
                            }
                            
        return Nxt2Btc  



 
    @dispatcher.add_method
    def getblockhash( **kwargs):
        blockAddress = kwargs['blockAddress'] 
        #print("getblockhash ----------" + str(kwargs))
        Nxt2Btc =  {
                    "blockAddress" : blockAddress,
                    }
        
        return Nxt2Btc  


 



    @dispatcher.add_method
    def getblock( **kwargs):
        """ Mapping Commentary. See keys at [Nxt2Btc_Mapping_Comments] in docstring of def application()
            ./bitcoind -rpcport=7879 getblock 8461367503743142254
            {
                "confirmations" : 1,
                "tx" : [
                    "9427743273145010700",
                    "9468719975072532448",
                    "9560907929335947693",
                    "10507706072875875119",
                    "11864667946939877596",
                    "12386165826869904583",
                    "199053848968879261",
                    "1294424573372804181",
                    "1823350660510498915",
                    "2651053493336681749"
                ],
                "chainwork" : "52a6360cc4529b5e07ef1d4b89eee37325a58544f4b9915c934b01fe7d067318",
                "hash" : "8461367503743142254",
                "difficulty" : "791103364",
                "version" : 3,
                "time" : 17715368,
                "bits" : "6785084810899231190",
                "merkleroot" : "91cdadd1f271da60268b11c72cb21fe69806cbbdb22f4f3e6a2021517d04160b1258f45122a15003fbe68eb8f0875fc08770286cc59c3226cb57fe451e73bfd0",
                "nonce" : "4495bad149d538014216d6ed4e05ecb7631036c1ddd80b090542d7ddbefee387",
                "nextblockhash" : "18019781220699116575",
                "height" : 163456,
                "size" : 1857,
                "previousblockhash" : "12614315688190262655"
            }



        """

        # 2 calls: gestate first, then getBlock!!
        payload = { "requestType" : "getBlock" }  
        NxtApi = {}
        #print("kwargs- "+ str(kwargs))
        block = kwargs['block']    
        NxtApi['requestType'] =  payload['requestType'] # here we translate BTC params to NXT params
        NxtApi['block'] = block  # here we translate BTC params to NXT params
        
        #print("NxtApi- "+ str(NxtApi))
        
        NxtReq.params=NxtApi # same obj, only replace params
        preppedReq = NxtReq.prepare()
        response = session.send(preppedReq)
        NxtResp = response.json()
        
        try:
            lastBlock = NxtResp['lastBlock']
        except:
            numberOfBlocks = 'errorDescription'
                            
        # special: double call: now getBlock
        
        #print("NxtResp- "+ str(NxtResp))
           
   
        #        
        #        Nxt2Btc_Mapping = {
        #                    "hash" : "block",
        #                    "confirmations" : 1,
        #                    "size" : "payloadLength",
        #                    "height" : "height",
        #                    "version" : "version",
        #                    "merkleroot" : "blockSignature",
        #                    "tx" : "transactions",
        #                    "time" : "timestamp",
        #                    "nonce" : "generationSignature",
        #                    "bits" : "generator",
        #                    "difficulty" : "baseTarget",
        #                    "chainwork" : "payloadHash",
        #                    "previousblockhash" : "previousBlock",
        #                    "nextblockhash" : "nextBlock",
        #                    "__unavailableInBitcoin1":  "previousBlockHash",
        #                    "__unavailableInBitcoin2":  "generatorRS" 
        #                    "__unavailableInBitcoin3":  "totalAmountNQT" 
        #                    "__unavailableInBitcoin4":  "numberOfTransactions" 
        #                    "__unavailableInBitcoin5":  "totalFeeNQT" 
        #                    }
         
        if 'previousBlock' in NxtResp.keys(): # the genesis block does not have a previousBlock!
            prevBlock = NxtResp['previousBlock']
        else:
            prevBlock = '0'
        if 'nextBlock' in NxtResp.keys(): # the latest block does not have a nextBlock!
            nextBlock = NxtResp['nextBlock']
        else:
            nextBlock = '0'
            
            
            
        Nxt2Btc = {
                    "hash" : block,
                    "confirmations" : 1,
                    "size" : NxtResp['payloadLength'],
                    "height" : NxtResp['height'],
                    "version" : NxtResp['version'],
                    "merkleroot" : NxtResp['blockSignature'],
                    "tx" : NxtResp['transactions'],
                    "time" : NxtResp['timestamp'],
                    "nonce" : NxtResp['generationSignature'],
                    "bits" : NxtResp['generator'],
                    "difficulty" : NxtResp['baseTarget'],
                    "chainwork" : NxtResp['payloadHash'],
                    "previousblockhash" : prevBlock,
                    "nextblockhash" : nextBlock,
                    }
         
        return Nxt2Btc  

  
 
     # this is a method that is NOT routed through dispatcher and it can beused also!!!
    def test(self):
        pass #print("okokkook")
        return "ok3"
 
  
 

    @Request.application
    def application(self, request ):
        """
        
        Nxt2Btc_Mapping_Comments: These are the comment keys as detailed in each dispatcher function docstring 
        
             1 BitcoinD Command/RPC	
             2 Parameters	
             3 Description	
             4 Requires unlocked wallet? (v0.4.0+)	
             5 Supported in nxtcoind v1.0	
             6 BitcoinD return format	
             7 NXT API	
             8 NXT format	
             9 Implementation Rules How to map a NXT API return to a XXXCOIND API return
 
            """
 
        ############################################################
        #
        # bitcoind seems to send NOT well formed jsonrpc calls!       
        #
        #        
        #
        # FOUR steps to implement new BTC2NXT mapping:
        #
        # 1
        #
        # def parse_BTCcall(jsonParms):
        #
        # 2
        # 
        # call parse_BTCcall to get parmsDi
        #
        # 3
        # 
        # call dispatcher with parmsdi
        #
        # 4
        #
        # extract and re-constitute BTC reply object
        #

        # argument extraction from list here in these local functions.


        #print(str(self))
        #ok = self.test() # 
        #print(ok)
        
        #<nxtPwt.nxtUC_Bridge.JSON_Runner object at 0x7fcb351e8048>


        # print threadcountz>!!! keep track of threadpool objects! just to make sure!
        
        def parse_getblockcount(jsonParms):
            parmsDi = {} 
            return parmsDi

        def parse_getbestblockhash(jsonParms):
            parmsDi = {} 
            return parmsDi

        def parse_getblock(jsonParms):
            parmsDi = {} 
            block = str(jsonParms[0])
            parmsDi = {'block':block} 
            return parmsDi
            
        def parse_getblockhash(jsonParms):
            parmsDi = {} 
            blockHeight = str(jsonParms[0])
            self.blockHeightDB = "nxtBlockDB.db"
            self.blockDBConn = sq.connect(self.blockHeightDB)
            self.blockDBCur = self.blockDBConn.cursor()
            self.blockDBCur = self.blockDBConn.cursor()
            self.blockDBCur.execute("SELECT blockAddr from   nxtBlockH_to_Addr WHERE height = ?   ", ( blockHeight, )  )            
            blockAddress_from_blockHeight = self.blockDBCur.fetchone()
            blockAddress = blockAddress_from_blockHeight[0]
            parmsDi = {'blockAddress':blockAddress} 
            return parmsDi
 
        def parse_getbalance(jsonParms):
            account = str(jsonParms[0])
            minconf = str(jsonParms[1])
            #print("account" + str(account))
            parmsDi = {'account':account, 'minconf': minconf}             
            return parmsDi
         
        def parse_getconnectioncount(jsonParms):
            parmsDi = {} 
            return parmsDi
        
        def parse_getinfo(jsonParms):
            parmsDi = {} 
            return parmsDi
              
        def parse_getreceivedbyaccount(jsonParms):
            parmsDi = {} 
            account = str(jsonParms[0])
            parmsDi = {'account':account}             
            return parmsDi
        
        def parse_getreceivedbyaddress(jsonParms):
            parmsDi = {} 
            account = str(jsonParms[0])
            parmsDi = {'account':account}             
            return parmsDi
        
        def parse_gettransaction(jsonParms):
            parmsDi = {} 
            txid = str(jsonParms[0])
            parmsDi = {'txid':txid}             
            return parmsDi
        
        def parse_sendfrom(jsonParms):
        
            parmsDi = {} 
            
            fromaccount = str(jsonParms[0])
            parmsDi['fromaccount']  = fromaccount             

            tobitcoinaddress = str(jsonParms[1])
            parmsDi['tobitcoinaddress']  = tobitcoinaddress
             
            amount = str(jsonParms[2])
            parmsDi['amount']  = amount
            
            try:
                minconf = str(jsonParms[3])
                parmsDi['minconf']  = minconf
            except:
                parmsDi = {'minconf':1}             
            try:
                comment = str(jsonParms[4])
                parmsDi['comment']  = comment
            except:
                parmsDi = {'comment':''}
            try:
                comment_to = str(jsonParms[5])
                parmsDi['comment_to']  = comment_to
            except:
                parmsDi = {'comment_to':''}
            
            return parmsDi
        
        def parse_settxfee(jsonParms):
            parmsDi = {} 
            return parmsDi
        
        def parse_validateaddress(jsonParms):
            parmsDi = {} 
            PASSPHRASE = str(jsonParms[0])
            parmsDi = {'PASSPHRASE':PASSPHRASE}             
            
            return parmsDi
            
             
        ##################################################
        #
        # 1 extract details from the incoming request        
        
        
        jsonRaw = request.get_data()


        #self.bridgeLogger.debug('nxtBridge rcvd raw: %s ', jsonRaw )
        
        #
        # raw str: full json content
        # b'{"jsonrpc": "2.0", "method": "getbalance", "params": {"account":"2865886802744497404","minconf":"1"}, "id": 12}'
        #
        #--------------------------
        # dict: full json content
        #        
        jsonEval = eval(jsonRaw)
        
        self.bridgeLogger.info('nxtBridge rcvd req: %s ', str(jsonEval) )
        
        self.consLogger.info('nxtBridge rcvd req: %s ', str(jsonEval) )
         
        #
        # Now we can access it as a nice dict
        # params payload is handed in as EITHER dict or list 
        # dict:
        # {'jsonrpc': '2.0', 'params': {'minconf': '1', 'account': '2865886802744497404'}, 'method': 'getbalance', 'id': 12}
        #
        # list:
        # {'params': ['2865886802744497404', 1], 'method': 'getbalance', 'id': 1}
        # 
        # using a list w/o key: value pairs seems not correct. But bitcoind does this.
        # esp. it omits the  'jsonrpc': '2.0' designation!! 
        # this must be added before handing it to the JSONhandler
        #
        # We want to maintain BOTH ways of handling the requests, because this is about josn after all,
        # regardless of what unspeakable things bitcoind does.
        #
        jsonParms = jsonEval['params']
        #
        # we have to do an eval to be able to access the details of the request
        # jsonParms is a list, and it is specific to each bitcoind call
        # eg jsonParms--------->    ['1674414626317090683', 1]
        # is from the call  ./bitcoind -rpcport=7879 getbalance 17237348781473815051 1
        # 
        # cmd line args only as either list or dict
        # print( "\njsonParms--------->" + str(jsonParms))
        #
        # dict: THIS IS CORRECT JSON:
        # {'minconf': '1', 'account': '2865886802744497404'}
        # 
        # list: THIS SEEMS TO BE INCORRECT JSON:
        # ['2865886802744497404', 1]
        #
        #   determine which type: bitcoind-like params list or proper json dict
        #   we are preparing for mostly list-type param passing
        #
        #
        if isinstance(jsonParms, list):
                
            # we need this to determine the params extraction method for params in a list.

            bitcoind_method = jsonEval['method']
             
            if bitcoind_method == 'getbalance':
                parmsDi = parse_getbalance(jsonParms)

            ##### new calls 061514
            elif bitcoind_method == 'getblockcount':
                parmsDi = parse_getblockcount(jsonParms)

            elif bitcoind_method == 'getbestblockhash':
                parmsDi = parse_getbestblockhash(jsonParms)
 
            elif bitcoind_method == 'getblock':
                parmsDi = parse_getblock(jsonParms)
                
            elif bitcoind_method == 'getblockhash':
                parmsDi = parse_getblockhash(jsonParms)
                 ############################
             
             
            elif bitcoind_method == 'getconnectioncount':
                parmsDi = parse_getconnectioncount(jsonParms)
                
            elif bitcoind_method == 'getinfo':
                parmsDi = parse_getinfo(jsonParms)
                
            elif bitcoind_method == 'getreceivedbyaccount':
                parmsDi = parse_getreceivedbyaccount(jsonParms)
                
            elif bitcoind_method == 'getreceivedbyaddress':
                parmsDi = parse_getreceivedbyaddress(jsonParms)
                
            elif bitcoind_method == 'gettransaction':
                parmsDi = parse_gettransaction(jsonParms)
                
            elif bitcoind_method == 'sendfrom':
                parmsDi = parse_sendfrom(jsonParms)
                
            elif bitcoind_method == 'settxfee':
                parmsDi = parse_settxfee(jsonParms)
    
            elif bitcoind_method == 'validateaddress':
                parmsDi = parse_validateaddress(jsonParms)
 
            else:
                parmsDi = {'throwException':'here'}
      
        ##################################################
        #
        # 3 here we forcible re-insert our custom made request into the request object
                   
            jsonEval['params'] = parmsDi
            jsonEval['jsonrpc'] = '2.0'
            jsonStr = str(jsonEval)
            jsonStr = jsonStr.replace("'", '"') # this seems to be an irregularity either in python3 str or in JSONRPCResponseManager


            
        elif isinstance(jsonParms, dict):
            #
            # THESE ARE CURRENTLY NOT OPERABLE, BUT THE OPTION SHALL BE MAINTAINED
            # is the json request is well formed, we do not need to do anyting at all,
            # just hand it as a str to the Handler
            jsonEval['params'] = jsonParms
            jsonStr = jsonRaw
            
             
            
        ##################################################
        #
        # 4 send request to the NRS      
            
        responseFromNxt = JSONRPCResponseManager.handle(jsonStr, dispatcher)
        response = Response( responseFromNxt.json, mimetype='application/json') #, mimetype='text/plain') 
        self.consLogger.debug('self.qPool.activeThreadCount()  = %s ', str( self.qPool.activeThreadCount() ) )
        
        # *SOME* of the replies do not seem to be correct JSON format in {key:value} format.
        
        # 5 prepare the details of the response in non-JSON but bitcoind compliant format
        # to be sent back to the original requester
        
        
        self.consLogger.info('response = Response( responseFromNxt.json, ) = %s ', str(jsonEval) )
        
        
        if bitcoind_method == 'getbalance':
            # we MUST forcible violate the response object here because bitcoind does not use proper json
            parseResponse = eval(response.response[0])
            # parseResponse --> {'result': {'ACCOUNT': 2547600000000.0}, 'id': 1, 'jsonrpc': '2.0'}
            resultJson = parseResponse['result']
            amount  = resultJson['ACCOUNT']
            parseResponse['result'] = amount
            parseResponse = str(parseResponse)
            parseResponse = parseResponse.replace( "'",'"') 
            response.response[0] = parseResponse
            self.bridgeLogger.info('nxtBridge returning: %s ', parseResponse )
            return response

        elif bitcoind_method == 'getconnectioncount':
            parseResponse = eval(response.response[0])
            # parseResponse --> {'result': {'ACCOUNT': 2547600000000.0}, 'id': 1, 'jsonrpc': '2.0'}
            resultJson = parseResponse['result']
            numberOfPeers  = resultJson['numberOfPeers']
            parseResponse['result'] = numberOfPeers
            parseResponse = str(parseResponse)
            parseResponse = parseResponse.replace( "'",'"') 
            response.response[0] = parseResponse
            self.bridgeLogger.info('nxtBridge returning: %s ', parseResponse )
            return response

        elif bitcoind_method == 'getinfo':
            self.bridgeLogger.info('nxtBridge returning: %s ', response.response[0] )
            return response

        elif bitcoind_method == 'getreceivedbyaccount':
            parseResponse = eval(response.response[0])
            resultJson = parseResponse['result']
            amount  = resultJson['ACCOUNT']
            parseResponse['result'] = amount
            parseResponse = str(parseResponse)
            parseResponse = parseResponse.replace( "'",'"') 
            response.response[0] = parseResponse

            self.bridgeLogger.info('nxtBridge returning: %s ', parseResponse )
            return response
      
        elif bitcoind_method == 'getreceivedbyaddress':
            parseResponse = eval(response.response[0])
            resultJson = parseResponse['result']
            amount  = resultJson['ACCOUNT']
            parseResponse['result'] = amount
            parseResponse = str(parseResponse)
            parseResponse = parseResponse.replace( "'",'"') 
            response.response[0] = parseResponse

            self.bridgeLogger.info('nxtBridge returning: %s ', parseResponse )
            return response

        elif bitcoind_method == 'gettransaction':

            self.bridgeLogger.info('nxtBridge returning: %s ', response.response[0] )
            return response

        elif bitcoind_method == 'sendfrom':

            self.bridgeLogger.info('nxtBridge returning: %s ', response.response[0] )
            return response

        elif bitcoind_method == 'settxfee':
            
            self.bridgeLogger.info('nxtBridge returning: %s ', response.response[0] )
            return response
            
        elif bitcoind_method == 'validateaddress':

            self.bridgeLogger.info('nxtBridge returning: %s ', response.response[0] )
            return response            
           
        elif bitcoind_method == 'getblockcount':
            parseResponse = eval(response.response[0])
            resultJson = parseResponse['result']
            blockcount  = resultJson['numberOfBlocks']
            parseResponse['result'] = blockcount
            parseResponse = str(parseResponse)
            parseResponse = parseResponse.replace( "'",'"') 
            response.response[0] = parseResponse
            self.bridgeLogger.info('nxtBridge returning: %s ', parseResponse )
            return response
 
        elif bitcoind_method == 'getbestblockhash':
            # this is the ugly stuff where we butcher the dict, and re-configure a synthetic json response object
            parseResponse = eval(response.response[0])
            resultJson = parseResponse['result']
            blockcount  = resultJson['lastBlock']
            parseResponse['result'] = blockcount
            parseResponse = str(parseResponse)
            parseResponse = parseResponse.replace( "'",'"') 
            response.response[0] = parseResponse
            self.bridgeLogger.info('nxtBridge returning: %s ', parseResponse )
            return response
 
        elif bitcoind_method == 'getblock':
            # this format is used when we pass through a nice dict as json reply            
            self.bridgeLogger.info('nxtBridge returning: %s ', response.response[0] )
            # return a dict directly as dict, no need to make a fake list from it
            #self.bridgeLogger.info('nxtBridge returning: %s ', parseResponse )
            return response
 
        elif bitcoind_method == 'getblockhash':
            # this is the ugly stuff where we butcher the dict, and re-configure a synthetic json response object
            parseResponse = eval(response.response[0])
            resultJson = parseResponse['result']
            blockAddress  = resultJson['blockAddress']
            parseResponse['result'] = blockAddress
            parseResponse = str(parseResponse)
            parseResponse = parseResponse.replace( "'",'"') 
            response.response[0] = parseResponse
            self.bridgeLogger.info('nxtBridge returning: %s ', parseResponse )
            return response
             # BITCOIN SLOP: GETBLOCKCOUNT IS ONE TOO SMALL, COZ IT IS THE HEIGHT OF THE LATEST BLOCK THAT IS RETURNED,
             # AND THAT IS ONE LESS THAN THE BLOCKCOUNT, BEAUSE GENESIS IS HEIGHT = ZERO!

        else:
            parmsDi = {'throwException':'here'}
        
          

        return   0 # shoulnd't get here
              
    def run(self,):
        run_simple('localhost', 7879, self.application,  ) # WERKZEUG !!!!
  
 
# 
# getState:
#
#{
#    "lastBlock": "3246422815430149567",
#    "numberOfAliases": 120534,
#    "lastBlockchainFeeder": "89.250.240.60",
#    "numberOfPeers": 1367,
#    "numberOfBlocks": 167392,
#    "totalMemory": 788529152,
#    "isScanning": false,
#    "numberOfUnlockedAccounts": 2,
#    "freeMemory": 257800136,
#    "maxMemory": 954728448,
#    "totalEffectiveBalanceNXT": 973315632,
#    "numberOfTransactions": 270018,
#    "version": "1.1.5",
#    "numberOfOrders": 1150,
#    "numberOfVotes": 0,
#    "numberOfTrades": 6530,
#    "lastBlockchainFeederHeight": 167391,
#    "time": 18149679,
#    "availableProcessors": 4,
#    "numberOfAssets": 142,
#    "numberOfPolls": 0,
#    "cumulativeDifficulty": "5720033783595943",
#    "numberOfAccounts": 39098
#}


#getBlock:
#block:	
#
#{
#    "transactions": [
#        "11347064822191789233",
#        "13022278691169947279",
#        "15344830822878861528",
#        "17027158668263548018",
#        "3928058537964610592",
#        "8126855791819446295"
#    ],
#    "generatorRS": "NXT-HV5P-5WN7-6GHZ-DDY4P",
#    "totalAmountNQT": "996100000000",
#    "blockSignature": "a323bce7e7e6ce4fe9e4922b13db46399d05ab9a9e979f8c42a10fb23f7d5209f5543b1367f3776d73a302e8850b23ac5047a88dd63b594c985b9bf628bad1c1",
#    "payloadLength": 1050,
#    "numberOfTransactions": 6,
#    "version": 3,
#    "timestamp": 18149668,
#    "previousBlock": "12525420578394947162",
#    "payloadHash": "3ce0d462b8860af45331b9ee4fe7d1f8dc6db15de0904217cb55b6e01ad6f954",
#    "height": 167391,
#    "totalFeeNQT": "1500000000",
#    "baseTarget": "1312193556",
#    "generationSignature": "3009d64559091806409276d8c8fe23d61f240c3764433ed792b8c2836a936192",
#    "previousBlockHash": "5a3e994da73bd3ad0cada18e61170bab8292ea0623bba4abc50560654488ea72",
#    "generator": "13442060847498652789"
#}

#getBlock:     2680262203532249785 NXT GENESIS H=0
#block:	
#
#{
#    "transactions": [
#        "9481240856006507060",
#           ... 73 in total
#        "8841312677014468592"
#    ],
#    "generatorRS": "NXT-MRCC-2YLS-8M54-3CMAJ",
#    "nextBlock": "6556228577102711328",
#    "totalAmountNQT": "100000000000000000",
#    "blockSignature": "69d426c498b70ac6d1678180356527c1fee030ad732fbf7672c2266d166a4c08cf8fdeb4524fd1b496bbcaab03fa6e67760f6da452251402249015486c487211",
#    "payloadLength": 9344,
#    "numberOfTransactions": 73,
#    "version": -1,
#    "timestamp": 0,
#    "payloadHash": "72c8a92efffbd8695a866eabb13ca460a2f7cdf3283b82efb163360d6eec9469",
#    "height": 0,
#    "totalFeeNQT": "0",
#    "baseTarget": "153722867",
#    "generationSignature": "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
#    "generator": "1739068987193023818"
#}

#
# output of ./bitcoin-cli help:
#        
#            addmultisigaddress nrequired ["key",...] ( "account" )
#            addnode "node" "add|remove|onetry"
#            backupwallet "destination"
#            createmultisig nrequired ["key",...]
#            createrawtransaction [{"txid":"id","vout":n},...] {"address":amount,...}
#            decoderawtransaction "hexstring"
#            decodescript "hex"
#            dumpprivkey "bitcoinaddress"
#            dumpwallet "filename"
#            getaccount "bitcoinaddress"
#            getaccountaddress "account"
#            getaddednodeinfo dns ( "node" )
#            getaddressesbyaccount "account"
#            getbalance ( "account" minconf )
#            getbestblockhash
#            getblock "hash" ( verbose )
#            getblockcount
#            getblockhash index
#            getblocktemplate ( "jsonrequestobject" )
#            getconnectioncount
#            getdifficulty
#            getgenerate
#            gethashespersec
#            getinfo
#            getmininginfo
#            getnettotals
#            getnetworkhashps ( blocks height )
#            getnewaddress ( "account" )
#            getpeerinfo
#            getrawchangeaddress
#            getrawmempool ( verbose )
#            getrawtransaction "txid" ( verbose )
#            getreceivedbyaccount "account" ( minconf )
#            getreceivedbyaddress "bitcoinaddress" ( minconf )
#            gettransaction "txid"
#            gettxout "txid" n ( includemempool )
#            gettxoutsetinfo
#            getunconfirmedbalance
#            getwork ( "data" )
#            help ( "command" )
#            importprivkey "bitcoinprivkey" ( "label" rescan )
#            importwallet "filename"
#            keypoolrefill ( newsize )
#            listaccounts ( minconf )
#            listaddressgroupings
#            listlockunspent
#            listreceivedbyaccount ( minconf includeempty )
#            listreceivedbyaddress ( minconf includeempty )
#            listsinceblock ( "blockhash" target-confirmations )
#            listtransactions ( "account" count from )
#            listunspent ( minconf maxconf  ["address",...] )
#            lockunspent unlock [{"txid":"txid","vout":n},...]
#            move "fromaccount" "toaccount" amount ( minconf "comment" )
#            ping
#            sendfrom "fromaccount" "tobitcoinaddress" amount ( minconf "comment" "comment-to" )
#            sendmany "fromaccount" {"address":amount,...} ( minconf "comment" )
#            sendrawtransaction "hexstring" ( allowhighfees )
#            sendtoaddress "bitcoinaddress" amount ( "comment" "comment-to" )
#            setaccount "bitcoinaddress" "account"
#            setgenerate generate ( genproclimit )
#            settxfee amount
#            signmessage "bitcoinaddress" "message"
#            signrawtransaction "hexstring" ( [{"txid":"id","vout":n,"scriptPubKey":"hex","redeemScript":"hex"},...] ["privatekey1",...] sighashtype )
#            stop
#            submitblock "hexdata" ( "jsonparametersobject" )
#            validateaddress "bitcoinaddress"
#            verifychain ( checklevel numblocks )
#            verifymessage "bitcoinaddress" "signature" "message"
#            walletlock
#            walletpassphrase "passphrase" timeout
#            walletpassphrasechange "oldpassphrase" "newpassphrase"
#            
#            










       