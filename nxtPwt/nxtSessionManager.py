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
  
from PyQt4.QtCore import   QObject , pyqtSignal, pyqtSlot
 
from PyQt4 import Qt, QtCore
import nxtPwt.nxtUC_Bridge as nxtUC_Bridge
 
import nxtPwt.nxtModels as nxtMods
from nxtPwt.nxtApiSigs import nxtApi

from requests import Request as Req
from requests import Response  as Resp
from requests import Session
import requests 

from operator import mod as opmod

import sqlite3 as sq
import logging as lg

import nxtPwt.nxtDB as nxtDB


# Here we can do some control on whether or not to do testing 
#import nxtPwt.nxtTestCases as nxtTestCases
 
  
    
class nxtSessionManager(QObject):
    """ 
    
session management. 

container and brokering services for the useCases. 

connection management.

  
  """


    def __init__(self, app, argv ):# app, self.lastSess
        """
        sessMan can do things himself.
        But most of the things are done in the UC instances which are clollected here.
        So this is a container object for useCases and models

       """
        super(nxtSessionManager, self).__init__()
        self.app = app
        self.app.sessMan = self #
        
        self.nxtApi = nxtApi(self) # make the apiSigs instance here!
        self.activeNRS = nxtMods.NRSconn(self)
        self.nxtApi.initSignals() # leapFrog init: account and NRSconn must be made before connecting their Sigs on nxtApi
        self.qPool=QtCore.QThreadPool.globalInstance()
        self.qPool.setMaxThreadCount(2500) # robustness

        if len(argv) < 2:
            argv.append('testNet')
    
        runAs = argv[1]
        
        args={}
        args['runAs'] = runAs
        
        if runAs == 'testNet':
            host = 'localhost'
            port = '6876'
        elif runAs == 'mainNet':
            host = 'localhost'
            port = '7876'

        args['host'] = host
        args['port'] = port
        
        # build the loggers:        
        self.bridgeLogger = lg.getLogger('bridgeLogger')
        self.bridgeLogger.setLevel(lg.INFO)        
        fh=lg.FileHandler('bridge.log')
        fh.setLevel(lg.INFO)
        fter = lg.Formatter('%(asctime)s - %(message)s')
        fh.setFormatter(fter)
        self.bridgeLogger.addHandler(fh)
        self.bridgeLogger.info('nxtBridge listening on %s:%s', host, port)
        #        
        self.consLogger = lg.getLogger('consoleDebugger')
        self.consLogger.setLevel(lg.INFO)        
        ch = lg.StreamHandler()
        ch.setLevel(lg.DEBUG)
        ch.setFormatter(fh)
        self.consLogger.addHandler(ch)
         
        self.blockDB = nxtDB.BlockDB_Handler(self, host, port, self.consLogger )
        
        DB_blockHeights = (0,0)
                                                # self is sessMan!!
        self.uc_bridge = nxtUC_Bridge.UC_Bridge1(self,  host, port, self.bridgeLogger, self.consLogger, DB_blockHeights  )
       



  
   