from gi.repository import Gtk


class Main_Window(Gtk.Window):
	def __init__(self):
		super(Main_Window,self).__init__()
		self.resize(600,350)
		self.set_position(Gtk.WindowPosition.CENTER)
		self.main_box = Gtk.VBox(spacing=5)
		self.top_box  = Gtk.Box(spacing=5) 
		self.bot_box  = Gtk.Box(spacing=5)
		
		### Top Box
		self.check_protect = Gtk.CheckButton('Protect Me!')
		self.label_ifaces = Gtk.Label('Network Interfaces : ')
		
		self.combo_ifaces = Gtk.ComboBox()
		self.render_iface = Gtk.CellRendererText()
		self.combo_ifaces.pack_start(self.render_iface,True)
		self.combo_ifaces.add_attribute(self.render_iface,'text',0)
		
		self.top_box.pack_start(self.check_protect,False,False,0)
		self.top_box.pack_start(self.label_ifaces,False,False,0)
		self.top_box.pack_start(self.combo_ifaces,False,False,0)
		
		### Middle Area
		self.hosts_list = Gtk.ListStore(str,str,str)
		self.scr_win   = Gtk.ScrolledWindow()
		self.tree_view = Gtk.TreeView(self.hosts_list)
		self.scr_win.add(self.tree_view)
		
		### Bottom Box
		self.btn_about = Gtk.Button(Gtk.STOCK_ABOUT)
		self.bot_box.pack_end(self.btn_about,False,False,0)
		self.btn_quit = Gtk.Button(Gtk.STOCK_CLOSE)
		self.bot_box.pack_end(self.btn_quit,False,False,0)
		
		### Fill the main box
		self.main_box.pack_start(self.top_box,False,False,0)
		self.main_box.pack_start(self.scr_win,True,True,0)
		self.main_box.pack_start(self.bot_box,False,False,0)
		self.add(self.main_box)
		self.show_all()
		self.conns()
	def conns(self):
		self.connect('destroy',Gtk.main_quit)
		self.btn_quit.connect('clicked',Gtk.main_quit)
		self.btn_about.connect('clicked',self.about_dialog)
		
	def about_dialog(self,btn):
		self.about_dialog = Gtk.AboutDialog()
		self.about_dialog.set_program_name('TuxCut')
		###
		self.about_dialog.set_license("""
    Released under terms of Waqf Public License.
    This program is free software; you can redistribute it and/or modify
    it under the terms of the latest version Waqf Public License as
    published by Ojuba.org.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

    The Latest version of the license can be found on
    "http://waqf.ojuba.org/"
	""")
		self.about_dialog.set_default_response(Gtk.ResponseType.CLOSE)
		self.about_dialog.connect('response',self.hide_about_dialog)
		self.about_dialog.run()
		
	def hide_about_dialog(self, dlg, *args):
		dlg.hide()
		
	
