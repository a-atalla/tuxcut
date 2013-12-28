
#!/usr/bin/env python2

import sys
import setproctitle
from PySide.QtGui import QApplication
from mainwindow import MainWindow

setproctitle.setproctitle('tuxcut')
app = QApplication(sys.argv)
win = MainWindow()
win.show()

sys.exit(app.exec_())
