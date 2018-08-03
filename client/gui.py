# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Nov  7 2017)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.dataview

###########################################################################
## Class MainFrame
###########################################################################

class MainFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"TuxCut", pos = wx.DefaultPosition, size = wx.Size( 750,400 ), style = wx.CAPTION|wx.CLOSE_BOX|wx.MINIMIZE_BOX )
		
		self.SetSizeHints( wx.Size( 750,400 ), wx.Size( 750,400 ) )
		
		bSizer7 = wx.BoxSizer( wx.VERTICAL )
		
		bSizer2 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.cb_protection = wx.CheckBox( self, wx.ID_ANY, u"Protect My Computer", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2.Add( self.cb_protection, 0, wx.ALL, 5 )
		
		
		bSizer7.Add( bSizer2, 0, 0, 5 )
		
		self.hosts_view = wx.dataview.DataViewListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), wx.dataview.DV_ROW_LINES|wx.DOUBLE_BORDER )
		self.hosts_view.SetFont( wx.Font( 10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )
		
		bSizer7.Add( self.hosts_view, 1, wx.ALIGN_CENTER|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer7 )
		self.Layout()
		self.toolbar = self.CreateToolBar( 0, wx.ID_ANY ) 
		self.toolbar.Realize() 
		
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.cb_protection.Bind( wx.EVT_CHECKBOX, self.toggle_protection )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def toggle_protection( self, event ):
		event.Skip()
	

