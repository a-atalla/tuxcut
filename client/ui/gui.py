# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Apr 24 2017)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.dataview

###########################################################################
## Class MainFrame
###########################################################################

class MainFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"TuxCut Pro", pos = wx.DefaultPosition, size = wx.Size( 750,400 ), style = wx.CLOSE_BOX|wx.TAB_TRAVERSAL )
		
		self.SetSizeHints( wx.Size( 750,400 ), wx.Size( 750,400 ) )
		
		bSizer7 = wx.BoxSizer( wx.VERTICAL )
		
		self.hosts_view = wx.dataview.DataViewListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), wx.dataview.DV_ROW_LINES )
		self.hosts_view.SetFont( wx.Font( 10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )
		
		bSizer7.Add( self.hosts_view, 1, wx.ALIGN_CENTER|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer7 )
		self.Layout()
		self.toolbar = self.CreateToolBar( wx.TB_HORIZONTAL, wx.ID_ANY ) 
		self.toolbar.Realize() 
		
		self.m_menubar1 = wx.MenuBar( 0 )
		self.file_menu = wx.Menu()
		self.quit_item = wx.MenuItem( self.file_menu, wx.ID_EXIT, u"&Exit", wx.EmptyString, wx.ITEM_NORMAL )
		self.file_menu.Append( self.quit_item )
		
		self.m_menubar1.Append( self.file_menu, u"&File" ) 
		
		self.SetMenuBar( self.m_menubar1 )
		
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

