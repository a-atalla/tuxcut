from PyQt4 import QtGui,uic


class AboutDialog(QtGui.QDialog):
	def __init__(self):
		QtGui.QDialog.__init__(self)
		uic.loadUi('ui/AboutDialog.ui',self)

