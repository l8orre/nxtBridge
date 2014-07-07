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

from copy import copy
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

from string import ascii_letters as letters
from string import digits
from numpy.random import randint as ri
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

    def __init__(self, sessMan, host = 'localhost', port = '6876',bridgeLogger=None , consLogger=None, wallDB=None  ):
        super(UC_Bridge1   , self   ).__init__(sessMan)
        self.sessMan = sessMan
        self.qPool = sessMan.qPool
        self.meta = {'caller':'Bridge1'}
        self.bridgeLogger = bridgeLogger
        self.consLogger = consLogger
        self.walletDB = wallDB['walletDB']
        self.walletDB_fName = wallDB['walletDB_fName']
        self.mm = BridgeThread( self.qPool, host  , port ,  bridgeLogger,  consLogger ,wallDB )

 
class BridgeThread(QObject):
    """ 2680262203532249785 nxt genesis block """
    def __init__(self, qPool, host, port, bridgeLogger, consLogger, wallDB ):
        # check : is this the same as calling super(BridgeThread, etc) ???????
        super(QObject, self).__init__( parent = None)
        self.qPool = qPool
        self.host = host
        self.port = port
        self.bridgeLogger = bridgeLogger
        self.consLogger = consLogger
        self.wallDB = wallDB
        #self.walletDB = wallDB['walletDB']
        #self.walletDB_fName = wallDB['walletDB_fName']

    @pyqtSlot() # 61
    def jsonServ_Slot(self, ):
        """-"""
        self.json_Runner = JSON_Runner( self.host, self.port, self.bridgeLogger, self.consLogger , self.qPool, self.wallDB) # json_Emitter, self to THIS !!!!!!
        self.json_Runner.setAutoDelete(False) 
        self.qPool.start(self.json_Runner)
        self.consLogger.info('  self.qPool.activeThreadCount() = %s ', str(   self.qPool.activeThreadCount()) )

        
class JSON_Runner(QtCore.QRunnable):
    """- This is what needs to be put into the QThreadpool """
    nxtApi = nxtApi
    
    def __init__(self,   host = 'localhost', port = '6876', fileLogger = None, consLogger = None , qPool=None, wallDB=None ): #emitter,
        super(QtCore.QRunnable, self).__init__()
        global session # this must be global to be accessible from the dispatcher methods
        session = Session()
        headers = {'content-type': 'application/json'}
        sessUrl = 'http://' + host + ':' + port + '/nxt?' 
        global NxtReq

        self.walletDB = wallDB['walletDB']
        self.walletDB_fName = wallDB['walletDB_fName']
        NxtReq = Req( method='POST', url = sessUrl, params = {}, headers = headers        )

        # ToDo here we can also include a walletLogger to snd encrypted emails to a safe location as backup!
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
        return NxtResp

  
#######################
#
# Function Calls implemented below
# Numbers as per appeearance in listing of bitcoind help 
#
# getbalance	    	# OK -uses wallet.dat DB
# getbestblockhash   	# OK
# getblock	        	# OK
# getblockcount	    	# OK
# getblockhash		    # OK
# getconnectioncount	# OK
# getinfo		    	# OK
# getnewaddress	    	# OK    -uses wallet.dat DB
# getreceivedbyaccount	# under revision  -uses wallet.dat DB
# getreceivedbyaddress	# OK    -uses wallet.dat DB  WOKRING ON !!!! ALMOST READY
# gettransaction		# OK
# listsinceblock		# under revision  -uses wallet.dat DB
# listunspent		    #  OK   -uses wallet.dat DB
# sendfrom		        # under revision  -uses wallet.dat DB
# sendtoaddress	    	# under revision  -uses wallet.dat DB
# settxfee		        # OK (n/a)
# validateaddress		# OK



 
  
#######################
#######################
#######################
#######################
#######################
#######################


#######################

# ./bitcoind help getbalance
# getbalance ( "account" minconf )
#
# If account is not specified, returns the server's total available balance.
# If account is specified, returns the balance in the account.
# Note that the account "" is not the same as leaving the parameter out.
# The server total may be different to the balance in the default "" account.
#
#
        #listunspent ( minconf maxconf  ["address",...] )

        # getBalance
        # {
        #     "guaranteedBalanceNQT": "4979307947821",
        #     "balanceNQT": "4979307947821",
        #     "effectiveBalanceNXT": 49793,
        #     "unconfirmedBalanceNQT": "4979307947821",
        #     "forgedBalanceNQT": "100000000"
        # }

    @dispatcher.add_method # note: NEGATIVE account balances are unaccessible in this implementation.
    def getbalance( **kwargs):
        #kwargs: {'account': 'popo', 'walletDB_fName': 'nxtWallet.dat', 'minconf': '13'}
        # fetch guaranteed balance #
        #ignore minconf
        # fecth ONE or loop over all in wallet

        #print("getbalance----> " + str(kwargs))
        walletDB_fName = kwargs['walletDB_fName']
        walletDBConn = sq.connect(walletDB_fName)
        walletDBCur = walletDBConn.cursor()

        payload = { "requestType" : "getBalance" } #getTime"   }
        NxtApi = {}
        NxtApi['requestType'] =  payload['requestType'] # here we translate BTC params to NXT params
        accountName = kwargs['accountName'] #kwargs['account']
        balance_local = 0.0

        #print("---->        accountName "+ str(accountName ))
        if accountName == 'None':
            get_all_accs_from_wallet = """select  NxtNumeric from nxtWallet"""
            walletDBCur.execute(get_all_accs_from_wallet  )
            accts_in_wallet = walletDBCur.fetchall()#[0]
            for accountNum in accts_in_wallet:
                #print("accountNum[0]: " + accountNum[0])
                NxtApi['account'] = accountNum[0]
                NxtReq.params=NxtApi # same obj, only replace params
                preppedReq = NxtReq.prepare()
                response = session.send(preppedReq)
                NxtResp = response.json()
                #print("----------->"+str(NxtResp))
                if 'guaranteedBalanceNQT' in NxtResp.keys():
                    guaranteedBalanceNQT = NxtResp['guaranteedBalanceNQT']
                    guaranteedBalanceNXT = float(guaranteedBalanceNQT) * 0.00000001
                    balance_local += guaranteedBalanceNXT
        else:
            #                print("--------------->4" + str(accountName))
            get_accNum_from_wallet = """select  NxtNumeric from nxtWallet where accountName = ?  """
            accountNameTuple = (accountName,)
            walletDBCur.execute(get_accNum_from_wallet, accountNameTuple  )
            acct_in_wallet = walletDBCur.fetchall()#[0]
            #print("fetcing aaconuit from NRS:" + str(acct_in_wallet))
            try:
                #print("fetcing aaconuit from NRS:" + str(acct_in_wallet[0]))
                NxtApi['account'] = acct_in_wallet[0]
                NxtReq.params=NxtApi # same obj, only replace params
                preppedReq = NxtReq.prepare()
                response = session.send(preppedReq)
                NxtResp = response.json()
                guaranteedBalanceNQT = NxtResp['guaranteedBalanceNQT']
                guaranteedBalanceNXT = float(guaranteedBalanceNQT) * 0.00000001
                balance_local += guaranteedBalanceNXT
            except Exception as inst:
                print('account does not exist: %s ', str(inst) )
        try:
            Nxt2Btc =  {
                        'amount' : balance_local
                        }
        except:
            Nxt2Btc =  {
                        'amount': 0.0
                        }
        #print(str(Nxt2Btc))
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
            Nxt2Btc =  {
                    "lastBlock" : 'NRS_getState_error',
                                }
            return Nxt2Btc
        payload = { "requestType" : "getBlock" }
        NxtApi = {}
        NxtApi['requestType'] =  payload['requestType'] # here we translate BTC params to NXT params
        NxtApi['block'] =  lastBlock # here we translate BTC params to NXT params
        Nxt2Btc =  {
                "lastBlock" : lastBlock,
                            }
        return Nxt2Btc



    @dispatcher.add_method
    def getblock( **kwargs):

        # 2 calls: gestate first, then getBlock!!
        payload = { "requestType" : "getBlock" }  
        NxtApi = {}

        block = kwargs['block']    
        NxtApi['requestType'] =  payload['requestType'] # here we translate BTC params to NXT params
        NxtApi['block'] = block  # here we translate BTC params to NXT params

        NxtReq.params=NxtApi # same obj, only replace params
        preppedReq = NxtReq.prepare()
        response = session.send(preppedReq)
        NxtResp = response.json()
        
        try:
            lastBlock = NxtResp['lastBlock']
        except:
            numberOfBlocks = 'errorDescription'

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
            numberOfBlocks = int(NxtResp['numberOfBlocks']) - 1  # CHECK THIS OUT!!! # BTC-IDIOM !!! NB: since block height and block count differ by one,
        except:
            numberOfBlocks = 'errorDescription'
        Nxt2Btc =  {
                "numberOfBlocks" : numberOfBlocks,
                            }
        return Nxt2Btc  

 
    @dispatcher.add_method
    def getblockhash( **kwargs):
        payload = { "requestType" : "getBlockId" }
        NxtApi = {}
        NxtApi['requestType'] =  payload['requestType'] # here we translate BTC params to NXT params
        NxtApi['height'] =  kwargs['height'] # here we translate BTC params to NXT params
        NxtReq.params=NxtApi # same obj, only replace params
        preppedReq = NxtReq.prepare()
        response = session.send(preppedReq)
        NxtResp = response.json()
        blockAddress = NxtResp['block']
        #print("blockAddress - " + str(blockAddress))
        Nxt2Btc =  {
                    "blockAddress" : blockAddress,
                    }
        return Nxt2Btc



   
    @dispatcher.add_method
    def getconnectioncount( **kwargs):
        payload = { "requestType" : "getState" }
        NxtApi = {}
        NxtApi['requestType'] =  payload['requestType'] # here we translate BTC params to NXT params
        NxtReq.params=NxtApi # same obj, only replace params
        preppedReq = NxtReq.prepare()
        response = session.send(preppedReq)
        NxtResp = response.json()

        Nxt2Btc =  {
                    'numberOfPeers':NxtResp['numberOfPeers']
                    }
        
        return Nxt2Btc  
 
  

#########################
# 25 getinfo 
    @dispatcher.add_method
    def getinfo( **kwargs):
        #print("\ngetinfo\n")

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

        return Nxt2Btc  

    @dispatcher.add_method
    def getnewaddress(**kwargs):
        #print("\n\n-2--getnewaddress------>"  )

        def genRanSec():
            allchars = letters+digits
            numChars = len(allchars) # 62 no special chars, just caps, digs, mins
            ranSec = ''
            charList = ri(0,numChars, 96 )
            for char in charList:
                ranSec += allchars[char]
            return ranSec

        walletDB_fName = kwargs['walletDB_fName']
        walletDBConn = sq.connect(walletDB_fName)
        walletDBCur = walletDBConn.cursor()

        nxtSecret = genRanSec()

        getAccountId = {
                                        "requestType" : "getAccountId" ,  \
                                        "secretPhrase" : nxtSecret ,  \
                                        "pubKey" : ""
                                        }


# make sure it has no pubKey here!!! # ToDo !!!!!!!!!!!!!!!!!!
 #  and if it has raise a huge alarm!

        accName = kwargs['account']
        has_pubKey = "N"
        check_accName_exists= """select exists(select accountName from nxtWallet where accountName= ?)"""
        check_accName = (accName,)
        walletDBCur.execute(check_accName_exists,check_accName)

        accName_already_exists = walletDBCur.fetchall()[0]
        accName_already_exists = accName_already_exists[0] # <class 'int'>
        if accName_already_exists == 1:
            return {'account':'accountAlreadyExistsError'}
        elif accName_already_exists == 0:

            NxtReq.params=getAccountId # same obj, only replace params
            preppedReq = NxtReq.prepare() # NxtReq is global!
            response = session.send(preppedReq)
            NxtResp = response.json()
            nxtNumAcc = NxtResp['account']
            nxtRSAcc = NxtResp['accountRS']
            NxtRS_BTC = NxtResp['accountRS']
            NxtRS_BTC =NxtRS_BTC.replace("-","x")
            NxtRS_BTC += 'nxtnxtnxt'

            newNxtAccount = (accName,nxtNumAcc ,nxtRSAcc ,NxtRS_BTC ,nxtSecret , has_pubKey)
            insertNewNxtAccount = """insert into nxtWallet values (?,?,?,?,?,?)"""
            walletDBCur.execute(insertNewNxtAccount, newNxtAccount )
            walletDBConn.commit()
            return {'account': NxtRS_BTC} # THIS IS THE RETURN STRING

        # 1Ce1NpJJAH9uLKMR37vzAmnqTjB4Ck8L4g
        # NXT-JTA7-B2QR-8BFC-2V222
        # NXTxJTA7xB2QRx8BFCx2V222nxtnxtnxtx


        Nxt2Btc = {}
        return Nxt2Btc



    @dispatcher.add_method
    def getreceivedbyaddress( **kwargs):
        #print("getreceivedbyaccount" +str(kwargs))
        NXTaccount = kwargs["NXTaccount"] #kwargs['account']

        # get ALL account TXs
        # loop and select the 'IN' TXs
        # sum over these
        print("NXTaccount" +NXTaccount)

        payload1 = { "requestType" : "getAccountTransactionIds" } #getTime"   }
        NxtApi = {}
        NxtApi['requestType'] =  payload1['requestType'] # here we translate BTC params to NXT params
        NxtApi['account'] = NXTaccount
        NxtReq.params=NxtApi # same obj, only replace params
        preppedReq = NxtReq.prepare()
        response = session.send(preppedReq)
        NxtResp = response.json()
        payload2 = { "requestType" : "getTransaction" } #getTime"   }
        TXs = NxtResp['transactionIds']
        #print(str(TXs))
        NQT_received = 0.0
        for TX in TXs:
            #print("1"+str(TX))

            NxtApi = {}
            NxtApi['requestType'] =  payload2['requestType'] # here we translate BTC params to NXT params
            NxtApi['transaction'] = TX
            NxtReq.params=NxtApi # same obj, only replace params
            preppedReq = NxtReq.prepare()
            response = session.send(preppedReq)
            NxtResp = response.json()
            #print("2"+str(NxtResp))
            #print(str(NxtResp['recipient']))

            if NxtResp['recipient'] == str(NXTaccount):
                #print(str( NQT_received )) # pass
                NQT_received += float(NxtResp['amountNQT'])

        #Nxt2Btc = {}

        NXT_received =  NQT_received * 0.00000001
        #print(str(NXT_received))
        Nxt2Btc =  {
                    'NXT_received' : NXT_received
                    }

        return Nxt2Btc



    @dispatcher.add_method
    def getreceivedbyaccount( **kwargs):



        # we need to loop over all address/account pairs int the wallet.dat db here
        walletDB_fName = kwargs['walletDB_fName']
        walletDBConn = sq.connect(walletDB_fName)
        walletDBCur = walletDBConn.cursor()

        print("-----------__>1: " + str(kwargs))

        accountName = kwargs['accountName']

        accountName = (accountName,) # wrap inot tuple


        #get_accNum_from_wallet = """select  NxtNumeric from nxtWallet where accountName = ?  """
        #accountNameTuple = (accountName,)
        #walletDBCur.execute(get_accNum_from_wallet, accountNameTuple  )
        #acct_in_wallet = walletDBCur.fetchall()#[0]



        get_address_from_wallet = """select  NxtNumeric from nxtWallet where accountName = ? """

        walletDBCur.execute(get_address_from_wallet, accountName  )

        NXTaccount = walletDBCur.fetchall()[0]
        print(str(NXTaccount))
        NXTaccount = NXTaccount[0]
        print(str(NXTaccount))

        # get ALL account TXs
        # loop and select the 'IN' TXs
        # sum over these
        print("NXTaccount" +NXTaccount)

        payload1 = { "requestType" : "getAccountTransactionIds" } #getTime"   }
        NxtApi = {}
        NxtApi['requestType'] =  payload1['requestType'] # here we translate BTC params to NXT params
        NxtApi['account'] = NXTaccount
        NxtReq.params=NxtApi # same obj, only replace params
        preppedReq = NxtReq.prepare()
        response = session.send(preppedReq)
        NxtResp = response.json()
        payload2 = { "requestType" : "getTransaction" } #getTime"   }
        TXs = NxtResp['transactionIds']
        #print(str(TXs))
        NQT_received = 0.0
        for TX in TXs:
            #print("1"+str(TX))

            NxtApi = {}
            NxtApi['requestType'] =  payload2['requestType'] # here we translate BTC params to NXT params
            NxtApi['transaction'] = TX
            NxtReq.params=NxtApi # same obj, only replace params
            preppedReq = NxtReq.prepare()
            response = session.send(preppedReq)
            NxtResp = response.json()
            #print("2"+str(NxtResp))
            #print(str(NxtResp['recipient']))

            if NxtResp['recipient'] == str(NXTaccount):
                #print(str( NQT_received )) # pass
                NQT_received += float(NxtResp['amountNQT'])

        #Nxt2Btc = {}

        NXT_received =  NQT_received * 0.00000001
        #print(str(NXT_received))
        Nxt2Btc =  {
                    'NXT_received' : NXT_received
                    }

        return Nxt2Btc






    @dispatcher.add_method
    def gettransaction( **kwargs):# 3515074356657480623 testNet 070614

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
     
#
#   azure@boxfish:~/workbench/Altcoins/bitcoin-0.9.1-linux/bin/64$ ./bitcoind help listsinceblock
# listsinceblock ( "blockhash" target-confirmations )
#
# Get all transactions in blocks since block [blockhash], or all transactions if omitted
#
# Arguments:
# 1. "blockhash"   (string, optional) The block hash to list transactions since
# 2. target-confirmations:    (numeric, optional) The confirmations required, must be 1 or more
#
# Result:
# {
#   "transactions": [
#     "account":"accountname",       (string) The account name associated with the transaction. Will be "" for the default account.
#     "address":"bitcoinaddress",    (string) The bitcoin address of the transaction. Not present for move transactions (category = move).
#     "category":"send|receive",     (string) The transaction category. 'send' has negative amounts, 'receive' has positive amounts.
#     "amount": x.xxx,          (numeric) The amount in btc. This is negative for the 'send' category, and for the 'move' category for moves
#                                           outbound. It is positive for the 'receive' category, and for the 'move' category for inbound funds.
#     "fee": x.xxx,             (numeric) The amount of the fee in btc. This is negative and only available for the 'send' category of transactions.
#     "confirmations": n,       (numeric) The number of confirmations for the transaction. Available for 'send' and 'receive' category of transactions.
#     "blockhash": "hashvalue",     (string) The block hash containing the transaction. Available for 'send' and 'receive' category of transactions.
#     "blockindex": n,          (numeric) The block index containing the transaction. Available for 'send' and 'receive' category of transactions.
#     "blocktime": xxx,         (numeric) The block time in seconds since epoch (1 Jan 1970 GMT).
#     "txid": "transactionid",  (string) The transaction id (see https://blockchain.info/tx/[transactionid]. Available for 'send' and 'receive' category of transactions.
#     "time": xxx,              (numeric) The transaction time in seconds since epoch (Jan 1 1970 GMT).
#     "timereceived": xxx,      (numeric) The time received in seconds since epoch (Jan 1 1970 GMT). Available for 'send' and 'receive' category of transactions.
#     "comment": "...",       (string) If a comment is associated with the transaction.
#     "to": "...",            (string) If a comment to is associated with the transaction.
#   ],
#   "lastblock": "lastblockhash"     (string) The hash of the last block
# }
#
# Examples:
# > bitcoin-cli listsinceblock
# > bitcoin-cli listsinceblock "000000000000000bacf66f7497b7dc45ef753ee9a7d38571037cdb1a57f663ad" 6
# > curl --user myusername --data-binary '{"jsonrpc": "1.0", "id":"curltest", "method": "listsinceblock", "params": ["000000000000000bacf66f7497b7dc45ef753ee9a7d38571037cdb1a57f663ad", 6] }' -H 'content-type: text/plain;' http://127.0.0.1:8332/
#
# azure@boxfish:~/workbench/Altcoins/bitcoin-0.9.1-linux/bin/64$
#
        return Nxt2Btc  
        



    @dispatcher.add_method
    def listunspent( **kwargs):

        #./bitcoind -rpcport=7879 listunspent 0 1111111  "[\"2865886802744497404\",\"16159101027034403504\"]"

        #print("-3-----> listunspent" + str(kwargs))
        #listunspent ( minconf maxconf  ["address",...] )

        # getBalance
        # {
        #     "guaranteedBalanceNQT": "4979307947821",
        #     "balanceNQT": "4979307947821",
        #     "effectiveBalanceNXT": 49793,
        #     "unconfirmedBalanceNQT": "4979307947821",
        #     "forgedBalanceNQT": "100000000"
        # }

        acctTemplate = {
                            "txid" : "0",\
                            "vout" : 0,\
                            "address" : "NXT-ABCD-EFGH-IJKL-MNOP",\
                            "account" : "Portster1",\
                            "scriptPubKey" : "notAvailable",\
                            "amount" : 0.00000000,\
                            "confirmations" : 0,\
                            }

        #        ACCOUNT = kwargs["account"] #kwargs['account']

        # we need to loop over all address/account pairs int the wallet.dat db here
        walletDB_fName = kwargs['walletDB_fName']
        walletDBConn = sq.connect(walletDB_fName)
        walletDBCur = walletDBConn.cursor()

        # print("4: " + str(accts_in_wallet))
        payload = { "requestType" : "getBalance" } #getTime"   }
        NxtApi = {}
        NxtApi['requestType'] =  payload['requestType'] # here we translate BTC params to NXT params
        accounts_queried = []

        #testNetAcc = ('2865886802744497404','') # <------testNet------------- FOR TESTING with  non-existing accounts in wallet!!!
        #accts_in_wallet.append(testNetAcc)

        if kwargs['addresses'] == []:
            get_all_accs_from_wallet = """select  NxtNumeric,accountName from nxtWallet"""
            walletDBCur.execute(get_all_accs_from_wallet  )
            accts_in_wallet = walletDBCur.fetchall()#[0]
            for ACCOUNT in accts_in_wallet:  # a list of tuples of len 1
                NxtApi['account'] = ACCOUNT[0] # a list of tuples
                try:
                    NxtNumeric = ACCOUNT[0] # a list of tuples
                    accountName = ACCOUNT[1] # a list of tuples
                except:
                    print("oops: " +str(ACCOUNT))
                NxtReq.params=NxtApi # same obj, only replace params
                preppedReq = NxtReq.prepare()
                response = session.send(preppedReq)
                NxtResp = response.json()
                # getBalance
                try:
                    guaranteedBalanceNQT = NxtResp['guaranteedBalanceNQT']# "": "4979307947821",
                    guaranteedBalanceNXT = int(guaranteedBalanceNQT) * 0.00000001
                    balanceNQT = NxtResp['balanceNQT'] #"": "4979307947821",
                    balanceNXT = int(balanceNQT) * 0.00000001
                    #effectiveBalanceNXT =NxtResp['effectiveBalanceNXT']# "": 49793,
                    unconfirmedBalanceNQT = NxtResp['unconfirmedBalanceNQT'] #"": "4979307947821",
                    unconfirmedBalanceNXT = int(unconfirmedBalanceNQT) * 0.00000001
                except:
                    guaranteedBalanceNXT = 0
                    balanceNXT = 0
                    unconfirmedBalanceNXT = 0

                #forgedBalanceNQT = NxtResp['forgedBalanceNQT'] #"": "100000000"
                retAcct = copy(acctTemplate)
                retAcct['amount'] = guaranteedBalanceNXT
                retAcct['account']=accountName
                retAcct['address']=NxtNumeric
                retAcct['vout']=balanceNXT
                retAcct['txid']=unconfirmedBalanceNXT
                accounts_queried.append(retAcct)

        else:
            get_all_accs_from_wallet = """select  NxtNumeric,accountName from nxtWallet"""
            walletDBCur.execute(get_all_accs_from_wallet  )
            accts_in_wallet = walletDBCur.fetchall()#[0]
            #print("kwargs['addresses']------->" + str(kwargs['addresses']))
            for ACCOUNT in accts_in_wallet:
                #print("ACCOUNT[0]: " + ACCOUNT[0])
                if not ACCOUNT[0] in kwargs['addresses']:
                    continue

                NxtApi['account'] = ACCOUNT[0] # a list of tuples
                try:
                    NxtNumeric = ACCOUNT[0] # a list of tuples
                    accountName = ACCOUNT[1] # a list of tuples
                except:
                    print("oops: " +str(ACCOUNT))
                NxtReq.params=NxtApi # same obj, only replace params
                preppedReq = NxtReq.prepare()
                response = session.send(preppedReq)
                NxtResp = response.json()
                # getBalance
                try:
                    guaranteedBalanceNQT = NxtResp['guaranteedBalanceNQT']# "": "4979307947821",
                    guaranteedBalanceNXT = int(guaranteedBalanceNQT) * 0.00000001
                    balanceNQT = NxtResp['balanceNQT'] #"": "4979307947821",
                    balanceNXT = int(balanceNQT) * 0.00000001
                    #effectiveBalanceNXT =NxtResp['effectiveBalanceNXT']# "": 49793,
                    unconfirmedBalanceNQT = NxtResp['unconfirmedBalanceNQT'] #"": "4979307947821",
                    unconfirmedBalanceNXT = int(unconfirmedBalanceNQT) * 0.00000001
                except:
                    guaranteedBalanceNXT = 0
                    balanceNXT = 0
                    unconfirmedBalanceNXT = 0

                #forgedBalanceNQT = NxtResp['forgedBalanceNQT'] #"": "100000000"
                retAcct = copy(acctTemplate)
                retAcct['amount'] = guaranteedBalanceNXT
                retAcct['account']=accountName
                retAcct['address']=NxtNumeric
                retAcct['vout']=balanceNXT
                retAcct['txid']=unconfirmedBalanceNXT
                accounts_queried.append(retAcct)




        #
        # acctTemplate = {
        #                     "txid" : "0",\
        #                     "vout" : 0,\
        #                     "address" : "NXT-ABCD-EFGH-IJKL-MNOP",\
        #                     "account" : "Portster1",\
        #                     "scriptPubKey" : "notAvailable",\
        #                     "amount" : 0.00000000,\
        #                     "confirmations" : 0,\
        #                     }
        #

        Nxt2Btc = accounts_queried # IT IS EASY TO JUST RETURN A LIST! SAME AS BITCOIN DOES!
        #Nxt2Btc =  {
        #            'accountsListunspent' : accounts_queried
        #            }
# [
#     {
#         "vout" : 0,
#         "confirmations" : 0,
#         "txid" : 0,
#         "account" : "a1a6",
#         "address" : "13229287245520819191",
#         "scriptPubKey" : "notAvailable",
#         "amount" : 0
#     },
#     {
#         "vout" : 49793.07947821,
#         "confirmations" : 0,
#         "txid" : 49793.07947821,
#         "account" : "",
#         "address" : "2865886802744497404",
#         "scriptPubKey" : "notAvailable",
#         "amount" : 49793.07947821
#     }
# ]


#
#       azure@boxfish:~/workbench/Altcoins/bitcoin-0.9.1-linux/bin/64$ ./bitcoind -rpcport=7879 listunspent 0 1111111  "[\"1PGFqEzfmQch1gKD3ra4k18PNj3tTUUSqg\"]"[
#     {
#         "errorDescription" : "Unknown account",
#         "errorCode" : 5
#     },
#     {
#         "errorDescription" : "Unknown account",
#         "errorCode" : 5
#     },
#     {
#         "errorDescription" : "Unknown account",
#         "errorCode" : 5
#     },
#     {
#         "errorDescription" : "Unknown account",
#         "errorCode" : 5
#     },
#     {
#         "errorDescription" : "Unknown account",
#         "errorCode" : 5
#     },
#     {
#         "errorDescription" : "Unknown account",
#         "errorCode" : 5
#     },
#     {
#         "errorDescription" : "Unknown account",
#         "errorCode" : 5
#     },
#     {
#         "effectiveBalanceNXT" : 49793,
#         "unconfirmedBalanceNQT" : "4979307947821",
#         "balanceNQT" : "4979307947821",
#         "forgedBalanceNQT" : "100000000",
#         "guaranteedBalanceNQT" : "4979307947821"
#     }
# ]
# azure@boxfish:~/workbench/Altcoins/bitcoin-0.9.1-linux/bin/64$
#
        #
#           azure@boxfish:~/workbench/Altcoins/bitcoin-0.9.1-linux/bin/64$ ./bitcoind listunspent
# [
#     {
#         "txid" : "790388dd2037863a302e738d24beb92fc4821fd6542b964009e12b8f6ef40e00",
#         "vout" : 0,
#         "address" : "1E5bdoMrBFkffc7hjXnNxFcm2Dh32SDRUH",
#         "account" : "Portster1",
#         "scriptPubKey" : "76a9148f7835df29a1b08958e59ff68caf572547a1eae188ac",
#         "amount" : 0.00007000,
#         "confirmations" : 31675
#     },
#     {
#         "txid" : "f0b20213346b14361795a9a387ac28078dc9a8a14fd9ced4f7b32eab9966820f",
#         "vout" : 0,
#         "address" : "1Ce1NpJJAH9uLKMR37vzAmnqTjB4Ck8L4g",
#         "account" : "",
#         "scriptPubKey" : "76a9147fa916934255d62febf440a3fad445e1d743d95a88ac",
#         "amount" : 0.00050000,
#         "confirmations" : 11987
#     }
# ]
# azure@boxfish:~/workbench/Altcoins/bitcoin-0.9.1-linux/bin/64$


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
        TX_ID='temp'
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

    #  ./bitcoind validateaddress 1Ce1NpJJAH9uLKMR37vzAmnqTjB4Ck8L4g
    # {
    #     "isvalid" : true,
    #     "address" : "1Ce1NpJJAH9uLKMR37vzAmnqTjB4Ck8L4g",
    #     "ismine" : true,
    #     "isscript" : false,
    #     "pubkey" : "0207d0373b78dafd79e4caad7abaa9b77e685c2af6ae125c0c0378c0b44b48789c",
    #     "iscompressed" : true,
    #     "account" : ""
    # }
    # azure@boxfish:~/workbench/Altcoins/bitcoin-0.9.1-linux/bin/64$
    #

    @dispatcher.add_method
    def validateaddress( **kwargs):

        # ToDo: maybe parse BTC-congruent padded RS acct to real ACCT!
        #payload = { "requestType" : "getAccountId" }
        #NxtApi = {}
        #NxtApi['requestType'] =  payload['requestType'] # here we translate BTC params to NXT params
        #NxtApi['secretPhrase'] =  kwargs['PASSPHRASE'] # here we translate BTC params to NXT params
        #NxtReq.params=NxtApi # same obj, only replace params
        #preppedReq = NxtReq.prepare()
        #response = session.send(preppedReq)
        #NxtResp1 = response.json()
        #print(" NxtResp1 "+str(NxtResp1))   
        # getAccountId
        #         secretPhrase:
        # publicKey:
        #
        # {
        #     "accountRS": "NXT-3P9W-VMQ3-9DRR-4EFKH",
        #     "account": "2865886802744497404"
        # }

        #ACCOUNT = NxtResp1['accountId']
        #
        # {
        #     "errorCode": 5,
        #     "errorDescription": "Account is not forging"
        # }
        # #
        #         {
        #     "errorCode": 5,
        #     "errorDescription": "Unknown account"
        # }
        #
        #   {
        #     "remaining": 36518,
        #     "deadline": 36546
        # }
        #

        #print(str(kwargs))
        account = kwargs['account']
        # this needs knowledge of the secret- but with BTC call 'validateaddress', you can also ask for ALL accounts w/o secret!
        #payload = { "requestType" : "getForging" }
        #NxtApi = {}
        #NxtApi['requestType'] =  payload['requestType'] # here we translate BTC params to NXT params
        #NxtApi['secretPhrase'] =  kwargs['PASSPHRASE'] # here we translate BTC params to NXT params
        #NxtReq.params=NxtApi # same obj, only replace params
        #preppedReq = NxtReq.prepare()
        #response = session.send(preppedReq)
        #NxtResp2 = response.json()

        #if "remaining" in NxtResp2.keys():
        #    ismine = 'true'
        #else:
        #    ismine = 'false'
        ismine = 'false'


        payload = { "requestType" : "getAccountPublicKey" } #getTime"   }
        NxtApi = {}
        NxtApi['requestType'] =  payload['requestType'] # here we translate BTC params to NXT params
        NxtApi['account'] =  account
        #ACCOUNT = kwargs["account"] #kwargs['account']
        NxtReq.params=NxtApi # same obj, only replace params
        preppedReq = NxtReq.prepare()
        response = session.send(preppedReq)
        NxtResp3 = response.json()
         
        if "errorCode" in NxtResp3.keys():
            isvalid = 'false'
            publicKey = ''
        elif "publicKey" in NxtResp3.keys():
            isvalid = 'true'

        Nxt2Btc =  {
                    "isvalid" : isvalid,
                    "address" : account,
                    "ismine" : ismine
                    }



#       getAccount
#         {
#     "publicKey": "10eb3c8cb67b4898e2993b1b463448f4f018939022c13892d682073a511ffa4a",
#     "assetBalances": [
#         {
#             "asset": "13294423783048908944",
#             "balanceQNT": "55"
#         },
#         {
#             "asset": "13309267173964952697",
#             "balanceQNT": "1200"
#         },
#         {
#             "asset": "13388701969217905199",
#             "balanceQNT": "39"
#         }
#     ],
#     "description": "description1",
#     "guaranteedBalanceNQT": "4979307947821",
#     "balanceNQT": "4979307947821",
#     "name": "name1",
#     "accountRS": "NXT-3P9W-VMQ3-9DRR-4EFKH",
#     "unconfirmedAssetBalances": [
#         {
#             "unconfirmedBalanceQNT": "55",
#             "asset": "13294423783048908944"
#         },
#         {
#             "unconfirmedBalanceQNT": "1200",
#             "asset": "13309267173964952697"
#         },
#         {
#             "unconfirmedBalanceQNT": "39",
#             "asset": "13388701969217905199"
#         }
#     ],
#     "account": "2865886802744497404",
#     "effectiveBalanceNXT": 49793,
#     "unconfirmedBalanceNQT": "4979307947821",
#     "forgedBalanceNQT": "100000000"
# }
#
        return Nxt2Btc  






####################################
####################################
####################################
####################################
####################################
    # customizations:
    @dispatcher.add_method
    def test_return_arbitrary_JSON_DICT(**kwargs):
        return {"test_return_arbitrary_JSON_DICT": "test_return_arbitrary_JSON_DICT"} # WALLET

    @dispatcher.add_method
    def test_return_arbitrary_NON_JSON(**kwargs):
        return {'ripThisIntoAList': 1387}

    def _any_method(self):
        self.consLogger.info('_any_method')
        return {"ripThisIntoAList": 5387}






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

        #<nxtPwt.nxtUC_Bridge.JSON_Runner object at 0x7fcb351e8048>

        self.consLogger.info('self.walletDB_fName  : %s ', self.walletDB_fName )

        def parse_getbalance(jsonParms): # getbalance ( "account" minconf )

            parmsDi = {'walletDB_fName' : self.walletDB_fName}
            parmsDi['accountName'] = 'None'
            parmsDi['minconf'] = '0'
            numargs=len(jsonParms)
            if numargs == 1:
                parmsDi['accountName'] =str(jsonParms[0])
            elif numargs == 2:
                parmsDi['accountName'] =str(jsonParms[0])
                parmsDi['minconf'] =str(jsonParms[1])
            #print("------->2" + str(parmsDi))
            return parmsDi
 
        def parse_getbestblockhash(jsonParms):
            parmsDi = {} 
            return parmsDi

        def parse_getblock(jsonParms):
            block = str(jsonParms[0])
            parmsDi = {'block':block} 
            return parmsDi
               
        def parse_getblockcount(jsonParms):
            parmsDi = {} 
            return parmsDi
            
        def parse_getblockhash(jsonParms):
            height = str(jsonParms[0])
            #print(height)
            parmsDi = {'height':height}
            return parmsDi

        def parse_getconnectioncount(jsonParms ):
            parmsDi = {}
            return parmsDi
        
        def parse_getinfo(jsonParms):
            parmsDi = {}
            return parmsDi
            
        def parse_getnewaddress(jsonParms): # 'self' is the bridgeRunner namespace
            account = str(jsonParms[0])
            parmsDi = {'walletDB_fName' : self.walletDB_fName}
            parmsDi['account'] = account
            #print("parse_getnewaddress" + str(parmsDi))
            return parmsDi
          
        def parse_getreceivedbyaccount(jsonParms):
            accountName = str(jsonParms[0])
            parmsDi = {'walletDB_fName' : self.walletDB_fName}
            parmsDi['accountName'] = accountName
            return parmsDi
        
        def parse_getreceivedbyaddress(jsonParms):
            account = str(jsonParms[0])
            parmsDi = {'NXTaccount':account}
            #print(str(parmsDi))
            return parmsDi
        
        def parse_gettransaction(jsonParms):
            txid = str(jsonParms[0])
            parmsDi = {'txid':txid}             
            return parmsDi


        def parse_listsinceblock(jsonParms):
            blockAddress = str(jsonParms[0])
            parmsDi = {'blockAddress':blockAddress}
            minimumConfs = str(jsonParms[0])
            parmsDi['minimumConfs'] = minimumConfs
            return parmsDi

        def parse_listunspent(jsonParms):
            # can be 0,1,2,3 args
            # 0 : parse_listunspent as list[]
            # 1 args : parse_listunspent as list[1]
            # 2 args : parse_listunspent as list[0, 1111111]
            # 3 args : parse_listunspent as list[0, 1111111, ['1PGFqEzfmQch1gKD3ra4k18PNj3tTUUSqg', '1LtvqCaApEdUGFkpKMM4MstjcaL4dKg8SP']]
            numargs=len(jsonParms)
            parmsDi = {
                        'minimumConfs': 0,\
                        'maximumConfs': 0,\
                        'addresses' :   [],
                        } # for len(numargs)==0
            if numargs == 1:
                parmsDi['minimumConfs'] =str(jsonParms[0])
            elif numargs == 2:
                parmsDi['minimumConfs'] =str(jsonParms[0])
                parmsDi['maximumConfs'] =str(jsonParms[1])

            elif numargs == 3:
                parmsDi['minimumConfs'] =str(jsonParms[0])
                parmsDi['maximumConfs'] =str(jsonParms[1])
                addresses = str(jsonParms[2])
                addresses = eval(addresses)
                parmsDi['addresses'] = addresses

            parmsDi['walletDB_fName'] = self.walletDB_fName

            return parmsDi

            #./bitcoind -rpcport=7879 listunspent 0 1111111  "[\"1PGFqEzfmQch1gKD3ra4k18PNj3tTUUSqg\",\"1LtvqCaApEdUGFkpKMM4MstjcaL4dKg8SP\"]"
            #./bitcoind -rpcport=7879 listunspent 0 1111111  "[\"2865886802744497404\",\"16159101027034403504\"]"




            # azure@boxfish:~/workbench/Altcoins/bitcoin-0.9.1-linux/bin/64$ ./bitcoind  listunspent 0 1111111
            # [
            #     {
            #         "txid" : "790388dd2037863a302e738d24beb92fc4821fd6542b964009e12b8f6ef40e00",
            #         "vout" : 0,
            #         "address" : "1E5bdoMrBFkffc7hjXnNxFcm2Dh32SDRUH",
            #         "account" : "Portster1",
            #         "scriptPubKey" : "76a9148f7835df29a1b08958e59ff68caf572547a1eae188ac",
            #         "amount" : 0.00007000,
            #         "confirmations" : 31652
            #     },
            #     {
            #         "txid" : "f0b20213346b14361795a9a387ac28078dc9a8a14fd9ced4f7b32eab9966820f",
            #         "vout" : 0,
            #         "address" : "1Ce1NpJJAH9uLKMR37vzAmnqTjB4Ck8L4g",
            #         "account" : "",
            #         "scriptPubKey" : "76a9147fa916934255d62febf440a3fad445e1d743d95a88ac",
            #         "amount" : 0.00050000,
            #         "confirmations" : 11964
            #     }
            # ]
            # azure@boxfish:~/workbench/Altcoins/bitcoin-0.9.1-linux/bin/64$
            #
            #             azure@boxfish:~/workbench/Altcoins/bitcoin-0.9.1-linux/bin/64$ ./bitcoind  listunspent 0 1111111  "[\"1E5bdoMrBFkffc7hjXnNxFcm2Dh32SDRUH\",\"1Ce1NpJJAH9uLKMR37vzAmnqTjB4Ck8L4g\"]"
            # [
            #     {
            #         "txid" : "790388dd2037863a302e738d24beb92fc4821fd6542b964009e12b8f6ef40e00",
            #         "vout" : 0,
            #         "address" : "1E5bdoMrBFkffc7hjXnNxFcm2Dh32SDRUH",
            #         "account" : "Portster1",
            #         "scriptPubKey" : "76a9148f7835df29a1b08958e59ff68caf572547a1eae188ac",
            #         "amount" : 0.00007000,
            #         "confirmations" : 31652
            #     },
            #     {
            #         "txid" : "f0b20213346b14361795a9a387ac28078dc9a8a14fd9ced4f7b32eab9966820f",
            #         "vout" : 0,
            #         "address" : "1Ce1NpJJAH9uLKMR37vzAmnqTjB4Ck8L4g",
            #         "account" : "",
            #         "scriptPubKey" : "76a9147fa916934255d62febf440a3fad445e1d743d95a88ac",
            #         "amount" : 0.00050000,
            #         "confirmations" : 11964
            #     }
            # ]
            # azure@boxfish:~/workbench/Altcoins/bitcoin-0.9.1-linux/bin/64$

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
            account = str(jsonParms[0])
            parmsDi = {'account':account}
            return parmsDi

        # DEMO FUNCS
        def parse_test_return_arbitrary_NON_JSON(jsonPArms):
            parmsDi = {}
            return parmsDi

        def parse_test_return_arbitrary_JSON_DICT(jsonParms):
            parmsDi = {}
            parmsDi['bridgeRunner'] = self # here we add the walletDB to the parms to hand it into the callback

            parmsDi['nxtWalletDB'] = self.walletDB # here we add the walletDB to the parms to hand it into the callback
            return parmsDi

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
        
        #self.bridgeLogger.info('nxtBridge rcvd req: %s ', str(jsonEval) )
        
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
                parmsDi = parse_getnewaddress(jsonParms)

            elif bitcoind_method == 'getreceivedbyaccount':
                parmsDi = parse_getreceivedbyaccount(jsonParms)
                
            elif bitcoind_method == 'getreceivedbyaddress':
                parmsDi = parse_getreceivedbyaddress(jsonParms)

            elif bitcoind_method == 'gettransaction':
                parmsDi = parse_gettransaction(jsonParms)

            elif bitcoind_method == 'listsinceblock':
                parmsDi = parse_listsinceblock(jsonParms)
                
            elif bitcoind_method == 'listunspent':
                parmsDi = parse_listunspent(jsonParms) #{'TTT':'GGG'} #
                #print("parmsDi    -- > "  +str(parmsDi))
#
            elif bitcoind_method == 'sendfrom':
                parmsDi = parse_sendfrom(jsonParms)

            elif bitcoind_method == 'sendtoaddress':
                parmsDi = parse_sendfrom(jsonParms)
                
            elif bitcoind_method == 'settxfee':
                parmsDi = parse_settxfee(jsonParms)
    
            elif bitcoind_method == 'validateaddress':
                parmsDi = parse_validateaddress(jsonParms)

            elif bitcoind_method == 'test_return_arbitrary_NON_JSON':
                #parmsDi = parse_test_return_arbitrary_NON_JSON(jsonParms)
                parmsDi = {'test_return_arbitrary_NON_JSON':'test_return_arbitrary_NON_JSON'}

            elif bitcoind_method == 'test_return_arbitrary_JSON_DICT':
                #parmsDi = parse_test_return_arbitrary_JSON_DICT(jsonParms)
                parmsDi = {'test_return_arbitrary_JSON_DICT':'test_return_arbitrary_JSON_DICT_PARMSDI'}
                #print("\nparse json: elif bitcoind_method == 'test_return_arbitrary_JSON_DICT': str(parmsDi) " + str(parmsDi) )

                
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
        # TWO ways of handling this!!
        # can't hand the 'self' namespace in here, because it uses a string!
        #
        # we CAN use a non-dispatcher method here, but the we have to MANUALLY construct the RESPONSE object!
        # should work also!
        #

        responseFromNxt = JSONRPCResponseManager.handle(jsonStr, dispatcher)

        #
        # this construction allows to introduce ANY dict as result into the response object.
        # the local dispatcher functions that are wrapped as decorators are not really needed here!
        # dispatcher_override = True
        # if dispatcher_override:
        #     result = self._any_method()
        #     responseFromNxt._data['result'] = result

        response = Response( responseFromNxt.json, mimetype='application/json') #, mimetype='text/plain')

        #self.consLogger.info('self.qPool.activeThreadCount()  = %s ', str( self.qPool.activeThreadCount() ) )
        #
        # *SOME* of the replies do not seem to be correct JSON format in {key:value} format.
        #
        # 5 prepare the details of the response in non-JSON but bitcoind compliant format
        # to be sent back to the original requester
        #
        # ########################################################
        #
        # 5 return response object using dedicated 'method' label as originally in request object
        #
        #
        #
        #
        #
        #######################################################
        if bitcoind_method == 'getbalance': #
            """  RETURN NON - JSON  """
            # we MUST forcible violate the response object here because bitcoind does not use proper json
            #print(str(response.response))
            parseResponse = eval(response.response[0])
            # parseResponse --> {'result': {'ACCOUNT': 2547600000000.0}, 'id': 1, 'jsonrpc': '2.0'}
            #print(str(parseResponse))
            resultJson = parseResponse['result'] # result OUT

            amount  = resultJson['amount'] # do s.t. with it

            #print(str(amount))
            #amount=str(amount)
            parseResponse['result'] = amount # result back IN : force in a string or int instead of a dict!
            parseResponse = str(parseResponse) # re-package
            parseResponse = parseResponse.replace( "'",'"') 
            response.response[0] = parseResponse
            self.bridgeLogger.info('nxtBridge returning: %s ', parseResponse )
            return response

        elif bitcoind_method == 'getbestblockhash':
            """  RETURN NON - JSON  """
            # this is the ugly stuff where we butcher the dict, and re-configure a synthetic json response object
            parseResponse = eval(response.response[0])
            resultJson = parseResponse['result']
            blockcount  = resultJson['lastBlock']
            parseResponse['result'] = blockcount    # force in a string or int instead of a dict!
            parseResponse = str(parseResponse)
            parseResponse = parseResponse.replace( "'",'"') 
            response.response[0] = parseResponse
            self.bridgeLogger.info('nxtBridge returning: %s ', parseResponse )
            return response
 
        elif bitcoind_method == 'getblock':
            """  RETURN NON - JSON  """
            # this format is used when we pass through a nice dict as json reply            
            # return a dict directly as dict, no need to make a fake list from it
            # self.bridgeLogger.info('nxtBridge returning: %s ', parseResponse )
            return response
       
        elif bitcoind_method == 'getblockcount':
            """  RETURN NON - JSON  """
            parseResponse = eval(response.response[0])
            resultJson = parseResponse['result']
            blockcount  = resultJson['numberOfBlocks']
            parseResponse['result'] = blockcount         # force in a string or int instead of a dict!
            parseResponse = str(parseResponse)
            parseResponse = parseResponse.replace( "'",'"') 
            response.response[0] = parseResponse
            self.bridgeLogger.info('nxtBridge returning: %s ', parseResponse )
            return response
 
        elif bitcoind_method == 'getblockhash':
            """  RETURN NON - JSON  """
            # this is the ugly stuff where we butcher the dict, and re-configure a synthetic json response object
            parseResponse = eval(response.response[0])
            resultJson = parseResponse['result']
            blockAddress  = resultJson['blockAddress']
            parseResponse['result'] = blockAddress        # force in a string or int instead of a dict!
            parseResponse = str(parseResponse)
            parseResponse = parseResponse.replace( "'",'"') 
            response.response[0] = parseResponse
            self.bridgeLogger.info('nxtBridge returning: %s ', parseResponse )
            return response
             # BITCOIN SLOP: GETBLOCKCOUNT IS ONE TOO SMALL, COZ IT IS THE HEIGHT OF THE LATEST BLOCK THAT IS RETURNED,
             # AND THAT IS ONE LESS THAN THE BLOCKCOUNT, BEAUSE GENESIS IS HEIGHT = ZERO!
 
        elif bitcoind_method == 'getconnectioncount':
            """  RETURN NON - JSON  """
            parseResponse = eval(response.response[0])
            # parseResponse --> {'result': {'ACCOUNT': 2547600000000.0}, 'id': 1, 'jsonrpc': '2.0'}
            #print(str(parseResponse))
            resultJson = parseResponse['result']
            numberOfPeers  = resultJson['numberOfPeers']
            parseResponse['result'] = numberOfPeers         # force in a string or int instead of a dict!
            parseResponse = str(parseResponse)
            parseResponse = parseResponse.replace( "'",'"') 
            response.response[0] = parseResponse
            self.bridgeLogger.info('nxtBridge returning: %s ', parseResponse )
            return response
 
        elif bitcoind_method == 'getinfo':
            """  RETURN   JSON  """
            self.bridgeLogger.info('nxtBridge returning: %s ', parseResponse )
            return response
 
        elif bitcoind_method == 'getnewaddress':
            """  RETURN   JSON  """
            parseResponse = eval(response.response[0])
            resultJson = parseResponse['result']
            account  = resultJson['account']
            parseResponse['result'] = account           # force in a string or int instead of a dict!
            parseResponse = str(parseResponse)
            parseResponse = parseResponse.replace( "'",'"')
            response.response[0] = parseResponse
            self.bridgeLogger.info('nxtBridge returning: %s ', parseResponse )
            return response



        elif bitcoind_method == 'getreceivedbyaccount':
            """  RETURN NON - JSON  """
            parseResponse = eval(response.response[0])
            resultJson = parseResponse['result']
            amount  = resultJson['NXT_received']
            parseResponse['result'] = amount           # force in a string or int instead of a dict!
            parseResponse = str(parseResponse)
            parseResponse = parseResponse.replace( "'",'"') 
            response.response[0] = parseResponse
            self.bridgeLogger.info('nxtBridge returning: %s ', parseResponse )
            return response
      
        elif bitcoind_method == 'getreceivedbyaddress':
            """  RETURN NON - JSON  """
            parseResponse = eval(response.response[0])
            resultJson = parseResponse['result']
            amount  = resultJson['NXT_received']
            parseResponse['result'] = amount        # force in a string or int instead of a dict!
            parseResponse = str(parseResponse)
            parseResponse = parseResponse.replace( "'",'"') 
            response.response[0] = parseResponse
            self.bridgeLogger.info('nxtBridge returning: %s ', parseResponse )
            return response

        elif bitcoind_method == 'gettransaction':
            """  RETURN   JSON  """
            self.bridgeLogger.info('nxtBridge returning: %s ', response.response[0] )
            return response

        elif bitcoind_method == 'listsinceblock':
            """  RETURN   JSON  """
            self.bridgeLogger.info('nxtBridge returning: %s ', response.response[0] )
            return response

        elif bitcoind_method == 'listunspent':
            """  RETURN   JSON  """
            self.bridgeLogger.info('nxtBridge returning: %s ', response.response[0] )
            return response

        elif bitcoind_method == 'sendfrom':
            """  RETURN   JSON  """
            self.bridgeLogger.info('nxtBridge returning: %s ', response.response[0] )
            return response

        elif bitcoind_method == 'sendtoaddress':
            """  RETURN   JSON  """
            self.bridgeLogger.info('nxtBridge returning: %s ', response.response[0] )
            return response

        elif bitcoind_method == 'settxfee':
            """  RETURN   JSON  """
            self.bridgeLogger.info('nxtBridge returning: %s ', response.response[0] )
            return response
            
        elif bitcoind_method == 'validateaddress':
            """  RETURN   JSON  """
            self.bridgeLogger.info('nxtBridge returning: %s ', response.response[0] )
            return response            
        #
        #
        # example methods:
        elif bitcoind_method == 'test_return_arbitrary_JSON_DICT':
            """  RETURN  JSON  """
            self.bridgeLogger.info(' test_return_arbitrary_JSON_DICT nxtBridge returning: %s ', response.response[0] )
            return response

        elif bitcoind_method == 'test_return_arbitrary_NON_JSON':
            """  RETURN NON - JSON  """
            parseResponse = eval(response.response[0])
            resultJson = parseResponse['result']
            parseResponse['result'] = resultJson['ripThisIntoAList']    # force in a string or int instead of a dict!
            parseResponse['result'] = [1,2,3,4,'1599']   # force in a string or int instead of a dict!
            parseResponse['result'] = 1599   # force in a string or int instead of a dict!
            parseResponse = str(parseResponse)
            parseResponse = parseResponse.replace( "'",'"')
            response.response[0] = parseResponse
            return response



        else:
            parmsDi = {'throwException':'here'}
        
          

        return   0 # shouldn't get here
              
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










       