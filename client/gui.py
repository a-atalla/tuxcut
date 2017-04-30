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
		
		bSizer2 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.cb_protection = wx.CheckBox( self, wx.ID_ANY, u"Protect My Computer", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer2.Add( self.cb_protection, 0, wx.ALL, 5 )
		
		
		bSizer7.Add( bSizer2, 0, 0, 5 )
		
		self.hosts_view = wx.dataview.DataViewListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), wx.dataview.DV_ROW_LINES )
		self.hosts_view.SetFont( wx.Font( 10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, wx.EmptyString ) )
		
		bSizer7.Add( self.hosts_view, 1, wx.ALIGN_CENTER|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer7 )
		self.Layout()
		self.toolbar = self.CreateToolBar( wx.TB_HORIZONTAL, wx.ID_ANY ) 
		self.m_tool1 = self.toolbar.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u"icons/refresh.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Refresh", u"Refresh", None ) 
		
		self.toolbar.AddSeparator()
		
		self.m_tool3 = self.toolbar.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u"icons/register.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None ) 
		
		self.m_tool2 = self.toolbar.AddLabelTool( wx.ID_ANY, u"tool", wx.Bitmap( u"icons/exit.png", wx.BITMAP_TYPE_ANY ), wx.NullBitmap, wx.ITEM_NORMAL, u"Exit", u"Exit", None ) 
		
		self.toolbar.Realize() 
		
		self.m_menubar1 = wx.MenuBar( 0 )
		self.file_menu = wx.Menu()
		self.quit_item = wx.MenuItem( self.file_menu, wx.ID_EXIT, u"&Exit", wx.EmptyString, wx.ITEM_NORMAL )
		self.file_menu.Append( self.quit_item )
		
		self.m_menubar1.Append( self.file_menu, u"&File" ) 
		
		self.SetMenuBar( self.m_menubar1 )
		
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.cb_protection.Bind( wx.EVT_CHECKBOX, self.toggle_protection )
		self.Bind( wx.EVT_TOOL, self.on_refresh, id = self.m_tool1.GetId() )
		self.Bind( wx.EVT_TOOL, self.on_exit, id = self.m_tool2.GetId() )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def toggle_protection( self, event ):
		event.Skip()
	
	def on_refresh( self, event ):
		event.Skip()
	
	def on_exit( self, event ):
		event.Skip()
	

