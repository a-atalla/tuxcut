#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtCore,QtGui
from TuxCut import *

app = QtGui.QApplication(sys.argv)
settings = QtCore.QSettings("linuxac.org","TuxCut")
translator = QtCore.QTranslator()

lang = settings.value("Language","Arabic")
#lang = "Arabic"   # will be retreived from settings file
print lang
if lang=="Arabic":
    translator.load("i18n/ar.qm")
    app.installTranslator(translator)
    app.setLayoutDirection(QtCore.Qt.RightToLeft)
tux = TuxCut()
sys.exit(app.exec_())