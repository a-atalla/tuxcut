from core import TuxCut
from PySide.QtGui import QMainWindow, QTableWidgetItem, QMessageBox, QIcon, QSystemTrayIcon, QMenu, QDesktopWidget
from PySide.QtCore import Qt, SIGNAL, Slot, QTimer
from gui.Ui_MainWindow import Ui_MainWindow
import netinfo
import platform

class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.show_Window()
        self.isQuit = False
        self.fill_active_interfaces()
        self.tuxcut = TuxCut(self.comboIfaces.currentText())
        self.fill_live_hosts()
        self.scanTimer = QTimer()
        self.scanTimer.start(10000)
        self.connect(self.scanTimer, SIGNAL('timeout()'), self.fill_live_hosts)

    @Slot()
    def on_btnRefresh_clicked(self):
        self.fill_live_hosts()

    @Slot()
    def on_cboxProtection_stateChanged(self):
        if self.cboxProtection.isChecked():
            self.tuxcut.enable_protection()
        else:
            self.tuxcut.disable_protection()

    def tray_icon(self):
        self.trayicon=QSystemTrayIcon(QIcon(':/images/images/tuxcut.png'))
        self.trayicon.show()
        self.menu=QMenu()

       # self.menu.addAction(self.action_change_mac)
       # self.menu.addAction(self.action_quit)

        self.trayicon.setContextMenu(self.menu)
       # self.trayicon.activated.connect(self.onTrayIconActivated)

    def show_Window(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)
        self.tblHosts.setColumnWidth(0, 125)
        self.tblHosts.setColumnWidth(1, 150)
        self.tblHosts.setColumnWidth(2, 150)
        self.show()
        self.tray_icon()

    def fill_live_hosts(self):
        hosts_list = self.tuxcut.get_live_hosts().items()
        print hosts_list
        self.tblHosts.setRowCount(len(hosts_list))
        if len(hosts_list) > 0:
            for host in hosts_list:
                self.tblHosts.setItem(hosts_list.index(host), 0, QTableWidgetItem(host[0]))
                self.tblHosts.setItem(hosts_list.index(host), 1, QTableWidgetItem(host[1]))
                self.tblHosts.setItem(hosts_list.index(host), 2, QTableWidgetItem('Not Resolved'))
                self.tblHosts.item(hosts_list.index(host), 0).setIcon(QIcon(':/images/images/online.png'))
                self.tblHosts.item(hosts_list.index(host), 1).setTextAlignment(Qt.AlignCenter)
                self.tblHosts.item(hosts_list.index(host), 2).setTextAlignment(Qt.AlignCenter)
            self.tblHosts.setItem(0, 2, QTableWidgetItem(platform.node()))
            self.tblHosts.item(0, 2).setTextAlignment(Qt.AlignCenter)

    def fill_active_interfaces(self):
        ifaces_list = []
        ifaces_tupel = netinfo.list_active_devs()
        for iface in  ifaces_tupel:
            if not iface == 'lo':
                ifaces_list.append(iface)
                print '### ',iface
                if len(ifaces_list)>0:
                    for iface in ifaces_list:
                        self.comboIfaces.addItem(iface)

    def send_protection_packet(self):
        self.tuxcut.protection_thread()

    def closeEvent(self, event):
        if not self.isQuit:
            event.ignore()
            if self.isVisible():
                self.hide()
        else:
            self.tuxcut.disable_protection()
            self.close()



    def show_message(self, msg):
        msgBox = QMessageBox()
        msgBox.setText(msg)
        msgBox.exec_()

