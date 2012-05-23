from gi.repository import Gtk
from gui.main_window import *


class TuxCut(Main_Window):
	def __init__(self):
		super(TuxCut,self).__init__()
		self._iface =None
		self._gateway_ip = None
		self._gateway_mac = None
		self._myip = None
		self._mymac = None
		self.fill_ifaces_combo()
		#self.check_protect.hide()
	def get_ifacelist(self):
		ifacelist = []
		f=open('/proc/net/dev','r')
		ifaces = f.read().split('\n')
		f.close()
		ifaces.pop(0)
		ifaces.pop(0)
		for line in ifaces:
			ifacedata = line.replace(' ','').split(':')
			if len(ifacedata) == 2:
				if int(ifacedata[1]) > 0:
					ifacelist.append(ifacedata[0])
		return ifacelist
	
	def fill_ifaces_combo(self):
		ifaces_store = Gtk.ListStore(str)
		for iface in self.get_ifacelist():
			ifaces_store.append([iface])
		self.combo_ifaces.set_model(ifaces_store)