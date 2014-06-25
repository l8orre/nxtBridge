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

from requests import Request as Req
from requests import Response  as Resp
from requests import Session
import requests 


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

 
 
class BlockDB_Handler(nxtUseCaseMeta): # need to talk to NRS, hence UC derived
    """ 2680262203532249785 nxt genesis block
    This is a container and manager object for the QThrerasd that checks the blockchain for new blocks."""
   
    
    def __init__(self, sessMan,  host, port,    consLogger,   ):
        # check : is this the same as calling super(BridgeThread, etc) ???????
        super(nxtUseCaseMeta, self).__init__( parent = None)
        self.sessMan = sessMan
        self.qPool = sessMan.qPool # qPool is already in sessMan!
        #self.DBLogger = DBLogger
        self.consLogger = consLogger


        self.sessionBlockDB = Session()
        headers = {'content-type': 'application/json'}
        sessUrl = 'http://' + host + ':' + port + '/nxt?' 

        #    expiryTimeout ()     const

        self.init_BlockDB(host, port,) # the init of the sqlite DB is not supposed to be threaded!
        
        
        DB = ( self.blockDBConn, self.blockDBCur)
        # the QTHread dual bundle: Emitter+Runner
        self.blockDB_Emitter = BlockDB_Emitter(   self.consLogger )
        
        self.blockDBb_Runner = BlockDB_Runner( self.blockDB_Emitter, self.sessionBlockDB, self.sessMan, DB, self.NxtReq, self.consLogger ,  ) #self.DBLogger, ) 
        self.blockDBb_Runner.setAutoDelete(False) 
        
        # NB: this can be done WITHOUT QTHREADPOOL ALSO!!!

        # self.blockDBb_Runner.run()

#    expiryTimeout () const

        self.qPool.start(self.blockDBb_Runner)
        
        
        
        #  # housekeeping of the threads may have to be taken care of
    
        # SET QTHREAD PARMS HERE ! autodeleta false etc
        #self.qPool.start(self.db_Runner)



    def init_BlockDB(self, host, port):
        
        self.sessionBlockDB = Session()
        self.getBlock= {"requestType" : "getBlock" , "block" : "BLOCKADDRESS" }
        self.getState= {"requestType" : "getState"}
        self.blockHeightDB = "nxtBlockDB.db"
        self.blockDBConn = sq.connect(self.blockHeightDB)
        self.blockDBCur = self.blockDBConn.cursor()
        try:
            self.blockDBCur.execute("CREATE TABLE nxtBlockH_to_Addr(height INT, blockAddr TEXT)")
            self.blockDBCur.execute("INSERT INTO nxtBlockH_to_Addr(height, blockAddr) VALUES(?,?)",(  0 , "2680262203532249785")) # genesis block
            self.blockDBConn.commit()            
            # genesis Block at height 0
        except:
            self.consLogger.info("block DB table already exists")
        headers = {'content-type': 'application/json'}
        sessUrl = 'http://' + host + ':' + port + '/nxt?' 
        self.NxtReq = Req( method='POST', url = sessUrl, params = {}, headers = headers        )
        
        #########################################################
        self.NxtReq.params = self.getState         # 1 - getState 
        preppedReq = self.NxtReq.prepare()
        response = self.sessionBlockDB.send(preppedReq)
        NxtResp = response.json()
        #########################################################
        highBlockAddrBC = NxtResp['lastBlock']
        highBlockBC = NxtResp['numberOfBlocks'] - 1 # GENESIS H=0 
        self.blockDBCur.execute("SELECT MAX(height)  from  nxtBlockH_to_Addr ")
        highBlockDB = self.blockDBCur.fetchone()[0]  #all()  

        self.consLogger.info('init blockHeightDB. DBhigh, BChigh : %s, %s ', str(highBlockDB) , str(highBlockBC) )
 
        if highBlockDB >= highBlockBC :
            self.consLogger.info('blockHeightDB is complete!')
            return 0
        # the highest block is already in the DB, and we fecth it from NRS again to get 'nextBlock'!
        self.blockDBCur.execute("SELECT blockAddr from   nxtBlockH_to_Addr WHERE height = ?   ", (highBlockDB,))
        highestBlockAddrDB = self.blockDBCur.fetchone() #all()  
        highBlockAddrDB = str(highestBlockAddrDB[0]) # ok
        self.getBlock['block'] = highBlockAddrDB
        
        # this is the highest block currently in blockDB            
        #########################################################
        self.NxtReq.params = self.getBlock               # 2 - getBlock
        preppedReq = self.NxtReq.prepare()
        response = self.sessionBlockDB.send(preppedReq)
        NxtResp = response.json()
        #########################################################        
        
        nextBlock = str(NxtResp['nextBlock'])
        self.consLogger.info('fetching new blocks, starting with: %s ', str(nextBlock)   )
         
        logIncr = 1000
        # numberOfBlocks = height+1 genesis height =0
        while highBlockDB < highBlockBC:
            self.getBlock['block'] = nextBlock
            #########################################################
            self.NxtReq.params = self.getBlock                  # 2 - getBlock
            preppedReq = self.NxtReq.prepare()
            response = self.sessionBlockDB.send(preppedReq)
            NxtResp = response.json()
            #########################################################
            highBlockDB = int(NxtResp['height'])
            blockAddrIntoDB=str(nextBlock) 
            self.blockDBCur.execute("INSERT INTO nxtBlockH_to_Addr(height, blockAddr) VALUES(?,?)",( highBlockDB, blockAddrIntoDB))
            if opmod( highBlockDB , logIncr) == 0:
                self.consLogger.info('fetching new blocks: DBhigh, BChigh : %s, %s ', str(highBlockDB) , blockAddrIntoDB )
            if 'nextBlock' in NxtResp.keys():
                nextBlock = str(NxtResp['nextBlock'])
            else:
                break
        self.blockDBConn.commit()
        self.consLogger.info('blockHeightDB is complete!')
           

class BlockDB_Emitter(QObject):

    blockDBSig =  NRSREPLY = pyqtSignal(object  ,object) 
    
    def __init__(self,     consLogger = None  ,  ): #emitter, 
        super(BlockDB_Emitter, self).__init__()
        
        self.conLogger = consLogger
         
         
         
        
class BlockDB_Runner(QtCore.QRunnable):
    """- This is what needs to be put into the QThreadpool """
    #nxtApi = nxtApi
    
    def __init__(self, emitter,session , sessMan,   DB, NxtReq ,  consLogger = None , DBLogger = None, ): #emitter, 
        super(QtCore.QRunnable, self).__init__()
        self.NxtReq = NxtReq
        self.consLogger = consLogger
        self.getBlock= {"requestType" : "getBlock" , "block" : "BLOCKADDRESS" }
        self.getState= {"requestType" : "getState"}
        
        self.sessionBlockDB = session
        self.blockDBConn = DB[0]
        self.blockDBCur = DB[1]
        self.emitter = emitter
        self.blockDB_pollTime = 25000
        self.blockDBTimer = QTimer()
        QObject.connect(self.blockDBTimer, SIGNAL("timeout()"),  self.blockDBTimer_CB)
        #
        # also prep the two requests here: getState and getBlock
        #

        
    def run(self,):
        self.blockDBTimer.start(self.blockDB_pollTime)
        
    def blockDBTimer_CB(self,):
        
        self.consLogger.info('fetching new blocks: DBhigh, BChigh')# : %s, %s ', str(highBlockDB) , blockAddrIntoDB )
        
        
        #########################################################
        self.NxtReq.params = self.getState         # 1 - getState 
        preppedReq = self.NxtReq.prepare()
        response = self.sessionBlockDB.send(preppedReq)
        NxtResp = response.json()
        #########################################################
        highBlockAddrBC = NxtResp['lastBlock']
        highBlockBC = NxtResp['numberOfBlocks'] - 1 # GENESIS H=0 
        self.blockDBCur.execute("SELECT MAX(height)  from  nxtBlockH_to_Addr ")
        highBlockDB = self.blockDBCur.fetchone()[0]  #all()  

        self.consLogger.info('init blockHeightDB. DBhigh, BChigh : %s, %s ', str(highBlockDB) , str(highBlockBC) )
 
        if highBlockDB >= highBlockBC :
            self.consLogger.info('blockHeightDB is complete!')
            return 0

        self.consLogger.info('getState : %s  ', str(NxtResp) ,   )
            
        # the highest block is already in the DB, and we fecth it from NRS again to get 'nextBlock'!
        self.blockDBCur.execute("SELECT blockAddr from   nxtBlockH_to_Addr WHERE height = ?   ", (highBlockDB,))
        highestBlockAddrDB = self.blockDBCur.fetchone() #all()  
        highBlockAddrDB = str(highestBlockAddrDB[0]) # ok
        self.getBlock['block'] = highBlockAddrDB
        
        # this is the highest block currently in blockDB            
        #########################################################
        self.NxtReq.params = self.getBlock               # 2 - getBlock
        preppedReq = self.NxtReq.prepare()
        response = self.sessionBlockDB.send(preppedReq)
        NxtResp = response.json()
        #########################################################        
        
        nextBlock = str(NxtResp['nextBlock'])
        self.consLogger.info('fetching new blocks, starting with: %s ', str(nextBlock)   )
         
        logIncr = 10
        # numberOfBlocks = height+1 genesis height =0
        while highBlockDB < highBlockBC:
            self.getBlock['block'] = nextBlock
            #########################################################
            self.NxtReq.params = self.getBlock                  # 2 - getBlock
            preppedReq = self.NxtReq.prepare()
            response = self.sessionBlockDB.send(preppedReq)
            NxtResp = response.json()
            #########################################################
            highBlockDB = int(NxtResp['height'])
            blockAddrIntoDB=str(nextBlock) 
            self.blockDBCur.execute("INSERT INTO nxtBlockH_to_Addr(height, blockAddr) VALUES(?,?)",( highBlockDB, blockAddrIntoDB))
            if opmod( highBlockDB , logIncr) == 0:
                self.consLogger.info('fetching new blocks: DBhigh, BChigh : %s, %s ', str(highBlockDB) , blockAddrIntoDB )
            if 'nextBlock' in NxtResp.keys():
                nextBlock = str(NxtResp['nextBlock'])
            else:
                break
            
        self.blockDBConn.commit()
        self.consLogger.info('blockHeightDB is complete!')
           
            
         
     



     
     