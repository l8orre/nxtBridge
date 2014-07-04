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
from requests import Session

from werkzeug.wrappers import  Response ,Request
from werkzeug.serving import run_simple

from jsonrpc import JSONRPCResponseManager, dispatcher

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



   #     self.uc_bridge = nxtUC_Bridge.UC_Bridge1(self, self.qPool, host, port, self.bridgeLogger, self.consLogger, DB  )
       
    def __init__(self, sessMan, host = 'localhost', port = '6876',bridgeLogger=None , consLogger=None, DBs=None  ):
        super(UC_Bridge1   , self   ).__init__(sessMan)
        self.sessMan = sessMan
        self.qPool = sessMan.qPool
        self.meta = {'caller':'Bridge1'}
        self.bridgeLogger = bridgeLogger
        self.consLogger = consLogger


        #        lg.info('nxtBridge listening on host %s : port %s', host, port)
        self.mm = BridgeThread( self.qPool, host  , port ,  bridgeLogger,  consLogger ,DBs )

 
class BridgeThread(QObject):
    """ 2680262203532249785 nxt genesis block """
    # housekeeping of the threads may have to be taken care of
    
    
    def __init__(self, qPool, host, port, bridgeLogger, consLogger, DBs ):
        # check : is this the same as calling super(BridgeThread, etc) ???????
        super(QObject, self).__init__( parent = None)
        self.DBs=DBs
        self.qPool = qPool
        self.host = host
        self.port = port
        self.bridgeLogger = bridgeLogger
        self.consLogger = consLogger
        self.walletDB = DBs[0]
        self.blockDB  = DBs[1]

    
    
    @pyqtSlot() # 61
    def jsonServ_Slot(self, ):
        """-"""
        self.json_Runner = JSON_Runner( self.host, self.port, self.bridgeLogger, self.consLogger , self.qPool, self.DBs) # json_Emitter, self to THIS !!!!!!
        self.json_Runner.setAutoDelete(False) 
        self.qPool.start(self.json_Runner)
        self.consLogger.info('  self.qPool.activeThreadCount() = %s ', str(   self.qPool.activeThreadCount()) )
            

     
        
class JSON_Runner(QtCore.QRunnable):
    """- This is what needs to be put into the QThreadpool """
    nxtApi = nxtApi
    
    def __init__(self,   host = 'localhost', port = '6876', fileLogger = None, consLogger = None , qPool=None, DBs=None ): #emitter,
        super(QtCore.QRunnable, self).__init__()
        global session # this must be global to be accessible from the dispatcher methods
        session = Session()
        headers = {'content-type': 'application/json'}
        sessUrl = 'http://' + host + ':' + port + '/nxt?' 
        global NxtReq

        self.walletDB = DBs[0]
        self.blockDB  = DBs[1]


        
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
#
# getbalance	    	# under revision
# getbestblockhash   	# OK
# getblock	        	# OK
# getblockcount	    	# OK
# getblockhash		    # OK
# getconnectioncount	# OK
# getinfo		    	# OK
# getnewaddress	    	# under revision
# getreceivedbyaccount	# under revision
# getreceivedbyaddress	# under revision
# gettransaction		# OK
# listsinceblock		# under revision
# listunspent		   # under revision
# sendfrom		       # under revision
# sendtoaddress	    	# under revision
# settxfee		        # OK (n/a)
# validateaddress		# OK



 
  
#######################
#######################
#######################
#######################
#######################
#######################


#######################

    @dispatcher.add_method
    def getbalance( **kwargs):

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
 
 
 
 
    @dispatcher.add_method
    def getbestblockhash( **kwargs):


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
    def getblock( **kwargs):

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

  
 


 
    @dispatcher.add_method
    def getblockcount( **kwargs):
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
        
        try: # BTC-IDIOM !!!
            numberOfBlocks = int(NxtResp['numberOfBlocks']) - 1  # CHECK THIS OUT!!! # BTC-IDIOM !!!
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
    def getblockhash( **kwargs):
        blockAddress = kwargs['blockAddress'] 
        #print("getblockhash ----------" + str(kwargs))
        Nxt2Btc =  {
                    "blockAddress" : blockAddress,
                    }
        
        return Nxt2Btc  


 
     # NOTE: **kawrags is how we can also pass the 'self' nxtUC_Bridge namespace to the callbacks if we want to!

        #Usage of **kwargs
        #**kwargs allows you to pass keyworded variable length of arguments to a function. You should use **kwargs if you want to handle named arguments in a function. Here is an example to get you going with it:
        #
        #def greet_me(**kwargs):
        #    if kwargs is not None:
        #        for key, value in kwargs.iteritems():
        #            print "%s == %s" %(key,value)
        # 
        #>>> greet_me(name="yasoob")
        #name == yasoob
        #
        #
        #
        # Usage of *args
        #*args and **kwargs are mostly used in function definitions. *args and **kwargs allow you to pass a variable number of arguments to a function. What does variable mean here is that you do not know before hand that how many arguments can be passed to your function by the user so in this case you use these two keywords. *args is used to send a non-keyworded variable length argument list to the function. Here’s an example to help you get a clear idea:
        #
        #def test_var_args(f_arg, *argv):
        #    print "first normal arg:", f_arg
        #    for arg in argv:
        #        print "another arg through *argv :", arg
        #
        #test_var_args('yasoob','python','eggs','test')
        #
        #This produces the following result:
        #
        #first normal arg: yasoob
        #another arg through *argv : python
        #another arg through *argv : eggs
        #another arg through *argv : test
        #



   
    @dispatcher.add_method
    def getconnectioncount( **kwargs):

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
        print("\ngetinfo\n")
        # it is possible to iclude the parent object namespace (runner) in the kwargs to have access!
        #self = kwargs['Runner']
        
        # self.consLogger.info('kwargs = %s ', kwargs )
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


    @dispatcher.add_method
    def getnewaddress( **kwargs):

        # if accName exists in DB, return ERROR
        # generate random pw
        # check if exists -
        # convert RS
        # pad RS to bitcoinRS
        # enter into DB
        # : accName,


        Nxt2Btc = {}
        return Nxt2Btc



# 1Ce1NpJJAH9uLKMR37vzAmnqTjB4Ck8L4g
# NXT-JTA7-B2QR-8BFC-2V222
# NXTxJTA7xB2QRx8BFCx2V222nxtnxtnxtx






    @dispatcher.add_method
    def getreceivedbyaccount( **kwargs):
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



    @dispatcher.add_method
    def getreceivedbyaddress( **kwargs):
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





    @dispatcher.add_method
    def gettransaction( **kwargs):

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




    @dispatcher.add_method
    def listsinceblock( **kwargs):
#        ACCOUNT = kwargs["account"] #kwargs['account']
#        payload = { "requestType" : "getBalance" } #getTime"   }
#        NxtApi = {}
#        NxtApi['requestType'] =  payload['requestType'] # here we translate BTC params to NXT params
#        NxtApi['account'] = ACCOUNT 
#        NxtReq.params=NxtApi # same obj, only replace params
#        preppedReq = NxtReq.prepare()
#        response = session.send(preppedReq)
#        NxtResp = response.json()
#        Nxt2Btc = {}


        Nxt2Btc =  {
                    'A' : "B"
                    }
     
          
        
        return Nxt2Btc  
        
        



    @dispatcher.add_method
    def listunspent( **kwargs):
#        ACCOUNT = kwargs["account"] #kwargs['account']
#        payload = { "requestType" : "getBalance" } #getTime"   }
#        NxtApi = {}
#        NxtApi['requestType'] =  payload['requestType'] # here we translate BTC params to NXT params
#        NxtApi['account'] = ACCOUNT 
#        NxtReq.params=NxtApi # same obj, only replace params
#        preppedReq = NxtReq.prepare()
#        response = session.send(preppedReq)
#        NxtResp = response.json()
#        Nxt2Btc = {}


        Nxt2Btc =  {
                    'A' : "B"
                    }
     
          
        
        return Nxt2Btc  
        





# 52 sendfrom
        
    @dispatcher.add_method
    def sendfrom( **kwargs):

 
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
 

 
    @dispatcher.add_method
    def sendtoaddress( **kwargs):
         
        Nxt2Btc = {}
        Nxt2Btc =  {
                
                "txid" : TX_ID,
                
                            }
                    
        return Nxt2Btc  
 

  

# 58 settxfee
 
    @dispatcher.add_method
    def settxfee( **kwargs):
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




     # this is a method that is NOT routed through dispatcher and it can beused also!!!

    @dispatcher.add_method
    def testC(**kwargs):
        print("-2-------->"  )
        print("kwargs: " + str(kwargs))
        # #{'nxtWalletDB': <nxtPwt.nxtDB.WalletDB_Handler object at 0x7fca49515ca8>, 'bridgeRunner': <nxtPwt.nxtUC_Bridge.JSON_Runner object at 0x7fca46d981f8>}
        #
        # bridgeRunner = kwargs['bridgeRunner'] # <nxtPwt.nxtUC_Bridge.JSON_Runner object
        # nxtWalletDB = kwargs['nxtWalletDB']   #<nxtPwt.nxtDB.WalletDB_Handler object at 0x7fca49515ca8>
        #
        #
        # print("-1-------->"  )
        walletDB_fName  = "nxtWallet.dat" # NAME OF DB HERE ---------- THIS WILL BE HNADED IN AS KWARGS!!!!
        walletDBConn = sq.connect(walletDB_fName)
        print(str(walletDBConn))

        walletDBCur = walletDBConn.cursor()
        print(str(walletDBCur))

        #walletDBCur.execute("SELECT * FROM   nxtWallet WHERE accountName = ?   ", ( "", )) # WHERE height = ?   ", ( blockHeight, )  )
        walletDBCur.execute("SELECT * FROM   nxtWallet") # WHERE height = ?   ", ( blockHeight, )  )

        WALLET = walletDBCur.fetchone()
        #WALLET = WALLET[0]
        print("-3-------->"  )
        print("--str(WALLET)------->" +str(WALLET))

        #
        # self.walletLogger.info('wallet: nxtBridge  : %s ', "in json thread" )
        # self.walletDB = "nxtWalletDB.dat" # NAME OF DB HERE
        # self.walletDBConn = sq.connect(self.walletDB)
        # self.walletDBCur = self.walletDBConn.cursor()
        # self.walletDBCur.execute("SELECT * from   nxtWallet WHERE accountName = ?   ", ( "", )  )
        #
        # wallTemp = self.walletDBCur.fetchone()


        return {"testC":str(WALLET)} # WALLET
 

    def test(self):
        pass
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
        # FIVE steps to implement new BTC2NXT mapping:
        #
        # 1
        #
        #   extract details from the incoming request
        #
        # 2
        # 
        # call the local functions to parse the parameters received in the call
        #
        # 3
        # 
        # re-insert our custom made parameters dict into the 'request' object
        #
        # 4
        #
        # call dispatcher with request object
        #
        #
        # 5
        #
        # return response object using dedicated 'method' label as originally in request object
        #

        # argument extraction from list here in these local functions.


        #print(str(self))
        #ok = self.test() # 
        #print(ok)
        
        #<nxtPwt.nxtUC_Bridge.JSON_Runner object at 0x7fcb351e8048>


        def parse_getbalance(jsonParms):
            account = str(jsonParms[0])
            minconf = str(jsonParms[1])
            #print("account" + str(account))
            parmsDi = {'account':account, 'minconf': minconf}             
            return parmsDi
 
        def parse_getbestblockhash(jsonParms):
            parmsDi = {} 
            return parmsDi

        def parse_getblock(jsonParms):
            parmsDi = {} 
            block = str(jsonParms[0])
            parmsDi = {'block':block} 
            return parmsDi
               
        def parse_getblockcount(jsonParms):
            parmsDi = {} 
            return parmsDi
            
        def parse_getblockhash(jsonParms):
            parmsDi = {} 
            blockHeight = str(jsonParms[0])
            #print("test")

            # maybe later this can be done ONCE for the object instance...
            #self.blockHeightDB = "nxtBlockDB.db"
            #self.blockDBConn = sq.connect(self.blockHeightDB)

            #self.blockDBCur = self.blockDBConn.cursor()





            self.blockHeightDB = "nxtBlockDB.db" # NAME OF DB HERE
            self.blockDBConn = sq.connect(self.blockHeightDB)
            self.blockDBCur = self.blockDBConn.cursor()

            self.blockDBCur.execute("SELECT blockAddr from   nxtBlockH_to_Addr WHERE height = ?   ", ( blockHeight, )  )

            blockAddress_from_blockHeight = self.blockDBCur.fetchone()
            blockAddress = blockAddress_from_blockHeight[0]
            parmsDi = {'blockAddress':blockAddress} 
            return parmsDi



        def parse_getconnectioncount(jsonParms):
            parmsDi = {} 
            return parmsDi
        
        def parse_getinfo(jsonParms):
            parmsDi = {} 
            return parmsDi
            
        def parse_getnewaddress(jsonParms):
            account = str(jsonParms[0])
            parmsDi = {'account':account}             
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


        def parse_listsinceblock(jsonParms):
            parmsDi = {}
            blockAddress = str(jsonParms[0])
            parmsDi = {'blockAddress':blockAddress}
            minimumConfs = str(jsonParms[0])
            parmsDi = {'minimumConfs':minimumConfs}
            return parmsDi

        def parse_listunspent(jsonParms):
            parmsDi = {}
            minimumConfs = str(jsonParms[0])
            parmsDi = {'minimumConfs':minimumConfs}
            maximumConfs = str(jsonParms[0])
            parmsDi = {'maximumConfs':maximumConfs}
            addresses = str(jsonParms[0])
            parmsDi = {'addresses':addresses}
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
        
        
        def parse_sendtoaddress(jsonParms):
            """ - """
            parmsDi = {} 
            tobitcoinaddress = str(jsonParms[0])
            parmsDi['tobitcoinaddress']  = tobitcoinaddress
            amount = str(jsonParms[1])
            parmsDi['amount']  = amount
            comment = str(jsonParms[2])
            parmsDi['comment']  = comment
            commentTo = str(jsonParms[3])
            parmsDi['commentTo']  = commentTo
            return parmsDi
        
        
        def parse_settxfee(jsonParms):
            parmsDi = {} 
            return parmsDi
            
            
        
        def parse_validateaddress(jsonParms):
            parmsDi = {} 
            PASSPHRASE = str(jsonParms[0])
            parmsDi = {'PASSPHRASE':PASSPHRASE}             
            
            return parmsDi
        





        
        def parse_testC(jsonParms):
            #print(str(jsonParms))
            parmsDi = {}
            parmsDi['bridgeRunner'] = self # here we add the walletDB to the parms to hand it into the callback

            parmsDi['nxtWalletDB'] = self.walletDB # here we add the walletDB to the parms to hand it into the callback
            return parmsDi
            #./bitcoind -rpcport=7879 test "" --------------  ['']
            #./bitcoind -rpcport=7879 test "*" ---------      ['*']






        ##################################################
        #
        # 1 extract details from the incoming request        
        #
        #
        #
        #
        #
        #
        ####################################################
        
        jsonRaw = request.get_data()

        #
        #
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
        ##################################################
        #
        # 2 call the local functions to parse the parameters received in the call
        #
        #
        #
        #
        #
        ####################################################

        if isinstance(jsonParms, list):  # THIS IS NOT WELL FORMED JSON !!!!!!!!!!!!!
                
            # we need this to determine the params extraction method for params in a list.

            bitcoind_method = jsonEval['method']
             
            if bitcoind_method == 'getbalance':
                parmsDi = parse_getbalance(jsonParms)

            elif bitcoind_method == 'getbestblockhash':
                parmsDi = parse_getbestblockhash(jsonParms)

            elif bitcoind_method == 'getblock':
                parmsDi = parse_getblock(jsonParms)

            elif bitcoind_method == 'getblockcount':
                parmsDi = parse_getblockcount(jsonParms)

            elif bitcoind_method == 'getblockhash':
                parmsDi = parse_getblockhash(jsonParms)
                 
            elif bitcoind_method == 'getconnectioncount':
                parmsDi = parse_getconnectioncount(jsonParms)
                
            elif bitcoind_method == 'getinfo':
                parmsDi = parse_getinfo(jsonParms)

            elif bitcoind_method == 'getnewaddress':
                parmsDi = parse_getinfo(jsonParms)

            elif bitcoind_method == 'getreceivedbyaccount':
                parmsDi = parse_getreceivedbyaccount(jsonParms)
                
            elif bitcoind_method == 'getreceivedbyaddress':
                parmsDi = parse_getreceivedbyaddress(jsonParms)

            elif bitcoind_method == 'gettransaction':
                parmsDi = parse_gettransaction(jsonParms)

            elif bitcoind_method == 'listsinceblock':
                parmsDi = parse_getreceivedbyaccount(jsonParms)
                
            elif bitcoind_method == 'listunspent':
                parmsDi = parse_getreceivedbyaddress(jsonParms)

            elif bitcoind_method == 'sendfrom':
                parmsDi = parse_sendfrom(jsonParms)

            elif bitcoind_method == 'sendtoaddress':
                parmsDi = parse_sendfrom(jsonParms)
                
            elif bitcoind_method == 'settxfee':
                parmsDi = parse_settxfee(jsonParms)
    
            elif bitcoind_method == 'validateaddress':
                parmsDi = parse_validateaddress(jsonParms)





            elif bitcoind_method == 'testC':

                parmsDi = parse_testC(jsonParms)
                parmsDi = {'testC':'testc_PARMSDI'}
                print("\nparse json: elif bitcoind_method == 'testC': str(parmsDi) " + str(parmsDi) )

                
            else:
                parmsDi = {'throwException':'here'}
      
        ##################################################
        #
        # 3 here we forcible re-insert our custom made request into the request object
        #
        #
        #
        #
        ###################################################

            #parmsDi['Runner'] = self # this is to include the 'self  namespace in the CB functions!
            
            jsonEval['params'] = parmsDi
            jsonEval['jsonrpc'] = '2.0'
            jsonStr = str(jsonEval)
            jsonStr = jsonStr.replace("'", '"') # this seems to be an irregularity either in python3 str or in JSONRPCResponseManager
            #self.consLogger.info('jsonStr= %s ', jsonStr )
         
            
        elif isinstance(jsonParms, dict): # THIS WOULD BE WELL FORMED JSON !!!!!!!!!!!!!
            self.consLogger.debug('jsonParms= %s ', str( jsonParms ) )
            # THESE ARE CURRENTLY NOT OPERABLE, BUT THE OPTION SHALL BE MAINTAINED
            # is the json request is well formed, we do not need to do anyting at all,
            # just hand it as a str to the Handler
            jsonEval['params'] = jsonParms
            jsonStr = jsonRaw
            
              
        ##################################################
        #
        # 4 send request to the NRS using the dispatcher functions registered with Werkzeug
        #
        #
        #
        #
        #
        #

        responseFromNxt = JSONRPCResponseManager.handle(jsonStr, dispatcher)
        response = Response( responseFromNxt.json, mimetype='application/json') #, mimetype='text/plain') 
        
        self.consLogger.info('self.qPool.activeThreadCount()  = %s ', str( self.qPool.activeThreadCount() ) )
        
        # *SOME* of the replies do not seem to be correct JSON format in {key:value} format.
        
        # 5 prepare the details of the response in non-JSON but bitcoind compliant format
        # to be sent back to the original requester
        
        
        self.consLogger.info('response = Response( responseFromNxt.json, ) = %s ', str(jsonEval) )
        
        ########################################################
        #
        # 5 return response object using dedicated 'method' label as originally in request object
        #
        #
        #
        #
        #
        #######################################################
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
 
        elif bitcoind_method == 'getnewaddress':
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

        elif bitcoind_method == 'listsinceblock':
            self.bridgeLogger.info('nxtBridge returning: %s ', response.response[0] )
            return response

        elif bitcoind_method == 'listunspent':
            self.bridgeLogger.info('nxtBridge returning: %s ', response.response[0] )
            return response

        elif bitcoind_method == 'sendfrom':

            self.bridgeLogger.info('nxtBridge returning: %s ', response.response[0] )
            return response

        elif bitcoind_method == 'sendtoaddress':

            self.bridgeLogger.info('nxtBridge returning: %s ', response.response[0] )
            return response

        elif bitcoind_method == 'settxfee':
            
            self.bridgeLogger.info('nxtBridge returning: %s ', response.response[0] )
            return response
            
        elif bitcoind_method == 'validateaddress':

            self.bridgeLogger.info('nxtBridge returning: %s ', response.response[0] )
            return response            
           


        elif bitcoind_method == 'testC':
            print("\nelif bitcoind_method == 'testC':" + str(response))
            #print("elif bitcoind_method == 'testC':" + str(response.__dir__()))

            #   parseResponse = eval(response.response[0])
            # parseResponse --> {'result': {'ACCOUNT': 2547600000000.0}, 'id': 1, 'jsonrpc': '2.0'}
            #resultJson = parseResponse['result']
            #amount  = resultJson['ACCOUNT']
            #parseResponse['result'] = amount
            #parseResponse = str(parseResponse)
            #parseResponse = parseResponse.replace( "'",'"')
            #response.response[0] = parseResponse
            #print(str(wallTemp))
            return response

        else:
            parmsDi = {'throwException':'here'}
        
          

        return   0 # shoulnd't get here
              
    def run(self,):
        run_simple('localhost', 7879, self.application,  ) # WERKZEUG !!!!
  
  
#
#    
 
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










       