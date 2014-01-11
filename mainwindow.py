from core import TuxCut
from PySide.QtGui import *
from PySide.QtCore import *
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
        self.tuxcut.enable_protection()
        self.spoofed_hosts = list()
        self.scanTimer = QTimer()
        self.scanTimer.start(10000)
        self.connect(self.scanTimer, SIGNAL('timeout()'), self.fill_live_hosts)

        self.spoofTimer = QTimer()
        self.spoofTimer.start(500)
        self.connect(self.spoofTimer, SIGNAL('timeout()'), self.spoofer)


    @Slot()
    def on_btnRefresh_clicked(self):
        self.fill_live_hosts()

    @Slot()
    def on_cboxProtection_stateChanged(self):
        if self.cboxProtection.isChecked():
            self.tuxcut.enable_protection()
        else:
            self.tuxcut.disable_protection()

    @Slot()
    def on_actionQuit_triggered(self):
        self.isQuit = True
        self.closeEvent(QCloseEvent)

    @Slot()
    def on_btnCut_clicked(self):
        ip = self.tblHosts.item(self.selected_row(), 0).text()
        hw = self.tblHosts.item(self.selected_row(), 1).text()
        victim = (ip, hw)
        if not victim in self.spoofed_hosts:
            self.spoofed_hosts.append(victim)
            self.tblHosts.item(self.selected_row(), 0).setIcon(QIcon(':/images/images/offline.png'))
        self.tuxcut.disable_ip_forward()

    @Slot()
    def on_btnResume_clicked(self):
        ip = self.tblHosts.item(self.selected_row(), 0).text()
        hw = self.tblHosts.item(self.selected_row(), 1).text()
        victim = (ip, hw)
        if victim in self.spoofed_hosts:
            self.spoofed_hosts.remove(victim)
            self.tblHosts.item(self.selected_row(), 0).setIcon(QIcon(':/images/images/online.png'))
        self.tuxcut.enable_ip_forward()

    @Slot()
    def on_btnResumeAll_clicked(self):
        self.spoofed_hosts[:] = []
        for i in range(0, self.tblHosts.rowCount()-1):
            self.tblHosts.item(i, 0).setIcon(QIcon(':/images/images/online.png'))
        self.tuxcut.enable_ip_forward()

    def on_trayicon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show()

    def tray_icon(self):
        self.trayicon=QSystemTrayIcon(QIcon(':/images/images/tuxcut.png'))
        self.trayicon.show()
        self.menu=QMenu()

       # self.menu.addAction(self.action_change_mac)
        self.menu.addAction(self.actionQuit)

        self.trayicon.setContextMenu(self.menu)
        self.trayicon.activated.connect(self.on_trayicon_activated)

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
        ifaces_list = list()
        ifaces_tupel = netinfo.list_active_devs()
        for dev in ifaces_tupel:
            if not dev == 'lo':
                ifaces_list.append(dev)
        if len(ifaces_list) > 0:
            for iface in ifaces_list:
                self.comboIfaces.addItem(iface)

    def spoofer(self):
        print self.spoofed_hosts
        if not len(self.spoofed_hosts) == 0:
            for victim in self.spoofed_hosts:
                self.tuxcut.arp_spoof(victim[0], victim[1])

    def closeEvent(self, event):
        if not self.isQuit:
            event.ignore()
            if self.isVisible():
                self.hide()
        else:
            self.tuxcut.disable_protection()
            self.tuxcut.resume_all()
            self.close()



    def show_message(self, msg):
        msgBox = QMessageBox()
        msgBox.setText(msg)
        msgBox.exec_()

    def selected_row(self):
        selectedRow = self.tblHosts.selectionModel().currentIndex().row()
        return selectedRow
