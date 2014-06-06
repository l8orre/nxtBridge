#!/usr/bin/python3
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

import sys
import os
from PyQt4 import QtGui
 
import nxtPwt
from nxtPwt.nxtSessionManager import nxtSessionManager

import logging as lg

#import argparse
#import configparser



from nxtPwt import nxtBridgeCtrl
# 

class MainApplication:
    """  Nxt """
    
    def __init__(self, app, argv): # = None):
        self.app = app
        self.argv = argv
        #runAs = self.args['runAs']
        #here we can reboot other sessions
        self.sessMan = nxtSessionManager(app, argv ) # self = app        
 
# 
#        mainLg = lg.getLogger('mainL')
#        mainLg.setLevel(lg.INFO)        
#        fh=lg.FileHandler('mainL.log')
#        
        
#        logFile = 'nxtBridge.log'
#        lg.basicConfig( filename=logFile, level=lg.INFO, format='%(asctime)s %(message)s')
#        lg.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
#        lg.debug('This message should appear on the console')
#        lg.info('So should this')
#        lg.warning('And this, too')
#        lg.basicConfig(format='%(asctime)s %(message)s')
#        lg.warning('is when this event was logged.')
#        lg.info('%i int %f float START test', 12, 3.12)
#        lg.info('start')
        




    # these are controllers
    def startBridge(self):
        """ This means that PowerTools can also be run WITHOUT windows!   """
        self.nxtBridge1Ctrl = nxtBridgeCtrl.Bridge1Ctrl(self) # bridge is what the WinCtrl would be
        self.nxtBridge1Ctrl.activate()
 

def main(argv):
    
    sys.path += [ os.path.dirname(os.path.dirname(os.path.realpath(__file__))) ]
    argv = sys.argv
    print('nxtBridge starting with cmd line:' + str(argv))

#
#    if len(argv) < 2:
#        argv.append('testNet')
#
#    runAs = argv[1]
#    
#    args={}
#    args['runAs'] = runAs

    app = QtGui.QApplication(sys.argv) # creation of the app object
    main = MainApplication(app, argv )
    
    main.startBridge( )
    done = app.exec_()
    print(done )
    sys.exit(done)
    
   


        
if __name__ == "__main__":

    main(sys.argv)
    


