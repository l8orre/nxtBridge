# -*- coding: utf-8 -*-
"""
Created on Wed Jun 25 10:17:16 2014

@author: azure
"""
 

from PyQt4 import  QtCore #Qt,
from PyQt4.Qt import QTimer
from PyQt4.QtCore import   QObject , pyqtSignal, pyqtSlot,  SIGNAL
import sqlite3 as sq
from nxtPwt.nxtApiPrototypes import nxtQs

import os
from requests import Request as Req
from requests import Session

from string import ascii_letters as letters
from string import digits
from numpy.random import randint as ri

from operator import mod as opmod



class nxtUseCaseMeta(QObject):
    """ This is an abstract meta class that has elemtary sigs and methods defined.
    All use case classes inherit from this, so they know all the signals for emission
    The useCaseClass is tho ONLY one that talks to the api.    

     """
    apiCalls = nxtQs() # static! dict of prototypes to be filled with vals for apiReq
    def __init__(self,  sessMan  ): # 
        super(nxtUseCaseMeta, self).__init__()
        self.nxtApi = sessMan.nxtApi  # there is only ONE apiSigs instance, and that is in the sessMan.



# **kwargs as dict ?!?! 

class WalletDB_Handler(nxtUseCaseMeta): # need to talk to NRS, hence UC derived
    """ 
    This is a container and manager object for the QThrerasd that checks the blockchain for new blocks."""
   
    def __init__(self, sessMan, walletDB_fName =  "nxtWallet.dat", walletLogger = None ,   consLogger =None, host='localhost' , port='6876'    ):
        super(nxtUseCaseMeta, self).__init__( parent = None)
        self.sessMan = sessMan
        self.qPool = sessMan.qPool # qPool is already in sessMan!
        self.consLogger = consLogger
        self.walletLogger = walletLogger
        self.walletDB_fName = walletDB_fName
        self.sessUrl = 'http://' + host + ':' + port + '/nxt?'
        self.init_WalletDB() # the init of the sqlite DB is not supposed to be threaded!
        self.walletPass = None
        DB = ( self.walletDBConn, self.walletDBCur)
        # the QTHread dual bundle: Emitter+Runner
        self.walletDB_Emitter = WalletDB_Emitter(   self.consLogger, self.walletLogger )
        self.walletDBb_Runner = WalletDB_Runner( self.walletDB_Emitter, self.sessMan, DB,  self.consLogger , self.walletLogger  ) #self.DBLogger, )
        self.walletDBb_Runner.setAutoDelete(False) 
        self.qPool.start(self.walletDBb_Runner)
        self.consLogger.info(' WalletDB_Handler -  self.qPool.activeThreadCount() = %s ', str(   self.qPool.activeThreadCount()) )

    def genRanSec(self):
        allchars = letters+digits
        numChars = len(allchars) # 62 no special chars, just caps, digs, mins
        ranSec = ''
        charList = ri(0,numChars, 96 )
        for char in charList:
            ranSec += allchars[char]
        return ranSec

    def init_WalletDB(self, ):

        # CREATE TABLE customer(
	     #           id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        #             firstname VARCHAR(50),
        #             lastname VARCHAR(50),
        #             age INTEGER
        #             )
        #


        #
        # 1Ce1NpJJAH9uLKMR37vzAmnqTjB4Ck8L4g l=34
        # NXT-JTA7-B2QR-8BFC-2V222 l =24
        # NXTxJTA7xB2QRx8BFCx2V222nxtnxtnxtx l =34
        #
        # NFD-AQQA-MREZ-U45Z-FWSZG     l=24
        # 15528161504488872648         l=20

#Longer answer: If you declare a column of a table to be INTEGER PRIMARY KEY, then whenever you insert a NULL into that column of the table, the NULL is automatically converted into an integer which is one greater than the largest value of that column over all other rows in the table, or 1 if the table is empty.

        #id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        wallet_is_new = not os.path.exists(self.walletDB_fName)
        try:
            nxtWallet_sqlite3_schema =  """create table nxtWallet (
                                            accountName text unique,
                                            NxtNumeric VARCHAR(20) unique primary key,
                                            NxtRS VARCHAR(24)  unique,
                                            NxtRS_BTC VARCHAR(34),
                                            NxtSecret VARCHAR(96) unique,
                                            Nxt_hasPubkey VARCHAR(5)
                                            );
                                        """
            # nxtWallet_sqlite3_schema =  """create table nxtWallet (
            #                                 accountName text unique,
            #                                 NxtNumeric text primary key,
            #                                 NxtRS text  unique,
            #                                 NxtRS_BTC text,
            #                                 NxtSecret text unique,
            #                                 Nxt_hasPubkey text
            #                                 );
            #                             """
            #

        #if wallet_is_new:
        #try:
            self.consLogger.info('creating wallet.db with filename: %s ', self.walletDB_fName )
            self.walletDBConn = sq.connect(self.walletDB_fName)
            self.walletDBCur = self.walletDBConn.cursor()
            self.walletDBCur.execute(nxtWallet_sqlite3_schema)
            sessionTemp = Session()

            nxtSecret = self.genRanSec()
            headers = {'content-type': 'application/json'}
            getAccountId = {
                                            "requestType" : "getAccountId" ,  \
                                            "secretPhrase" : nxtSecret ,  \
                                            "pubKey" : ""
                                            }
            NxtReqT = Req( method='POST', url = self.sessUrl, params = {}, headers = headers        )

            NxtReqT.params=getAccountId # same obj, only replace params
            preppedReq = NxtReqT.prepare()
            response = sessionTemp.send(preppedReq)
            NxtResp = response.json()
            #  print("\n\n ------>" + str(NxtResp))
            nxtNumAcc = NxtResp['account']
            nxtRSAcc = NxtResp['accountRS']
            NxtRS_BTC = NxtResp['accountRS']
            NxtRS_BTC =NxtRS_BTC.replace("-","x")
            NxtRS_BTC+='nxtnxtnxt'

# make sure it has no pubKey here!!!
#  and if it has raise a huge alarm!
            accName = ""
            has_pubKey = "N"
            newNxtAccount = (  accName,nxtNumAcc ,nxtRSAcc ,NxtRS_BTC ,nxtSecret , has_pubKey)
            insertNewNxtAccount = """insert into nxtWallet values (  ?,?,?,?,?,?)"""
            self.walletDBCur.execute(insertNewNxtAccount, newNxtAccount )
            self.walletDBConn.commit()
            #http://stackoverflow.com/questions/11490100/no-autoincrement-for-integer-primary-key-in-sqlite3 shit.
        except:
            self.consLogger.info('could not create wallet db with filename %s Assuming it exists already.', self.walletDB_fName )
            self.walletDBConn = sq.connect(self.walletDB_fName)
            self.walletDBCur = self.walletDBConn.cursor()
            self.walletDBCur.execute('SELECT SQLITE_VERSION()')
            sqlVers = self.walletDBCur.fetchone()
            self.consLogger.info('use existing db with SQLite version: %s ', sqlVers )


        self.walletDBConn = sq.connect(self.walletDB_fName)
        self.walletDBCur = self.walletDBConn.cursor()
        #########################################################
        self.walletDBConn.commit()
        self.consLogger.info('walletDB - some info here!')
           

class WalletDB_Emitter(QObject):

    walletDBSig = pyqtSignal(object  ,object)
    
    def __init__(self,     consLogger = None  , walletLogger = None  ): #emitter,
        super(WalletDB_Emitter, self).__init__()
        self.conLogger = consLogger
        self.walletLogger = walletLogger
         
        
class WalletDB_Runner(QtCore.QRunnable):
    """- This is what needs to be put into the QThreadpool """
    #nxtApi = nxtApi
    
    def __init__(self, emitter , sessMan,   DB,   consLogger = None , walletLogger = None, ): #emitter,
        super(QtCore.QRunnable, self).__init__()
        self.consLogger = consLogger
        self.walletLogger = walletLogger

        self.walletDBConn = DB[0]
        self.walletDBCur = DB[1]
        self.emitter = emitter

        self.walletDB_pollTime = 25000
        self.walletDBTimer = QTimer()
        QObject.connect(self.walletDBTimer, SIGNAL("timeout()"),  self.walletDBTimer_CB)


    def run(self,):
        self.blockDBTimer.start(self.blockDB_pollTime)

    def run(self,):
        self.walletDBTimer.start(self.walletDB_pollTime)
        
    def walletDBTimer_CB(self,):
        pass
        # this is  a heartbeat for now!
        self.consLogger.info('walletDB heartbeat')
        #########################################################
         
        # do the activities here         
           
           
     

#  INSERT INTO addresses (accN, addr,secret) VALUES (NULL, "1X123", "sec13");

#  SELECT * FROM addresses WHERE accN is NULL;

#  SELECT * FROM addresses WHERE addr="1X123";

#  DELETE from addresses where addr="1X123";

#  CREATE TABLE addresses (accountName TEXT, address TEXT UNIQUE, secret TEXT);

#  INSERT INTO addresses (accountName, address, secret) VALUES (NULL, "1X123", "sec13");

#  SELECT * FROM addresses WHERE accountName is NULL;

#  
#self.blockDBCur.execute("CREATE TABLE nxtBlockH_to_Addr(height INT, blockAddr TEXT)")
#self.blockDBCur.execute("INSERT INTO nxtBlockH_to_Addr(height, blockAddr) VALUES(?,?)",(  0 , "2680262203532249785")) # genesis b
            
         
#
#
#

#
#
#    CREATE TABLE t1(a, b UNIQUE);
#
#    CREATE TABLE t1(a, b PRIMARY KEY);
#
#    CREATE TABLE t1(a, b);
#    CREATE UNIQUE INDEX t1b ON t1(b); 
#       
            

#accN|addr|secret
#|1K123|sadf
#|1K456|sterst
#sqlite> 
