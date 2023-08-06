import sys

from ..testcases import testcases_nD
from ..testcases import gaussian_2D, testcases_2D, testcases_2D_papers, testcases_nD_papers
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets

 

unparametrized_testcases = [
                            (gaussian_2D, "Gaussian 2D testcases"),
                            (testcases_2D_papers, "Well-known 2D testcases"),
                            (testcases_nD_papers, "Well-known nD testcases"),
                            (testcases_2D, "2D testcases"),
                            ]



class TestCasesListWidget(QtWidgets.QListWidget):
    def __init__(self, module, parent=None):
        self.module = module
        super().__init__(parent)
        self.addItems(module.__all__)
        
    def extract_selected_item(self):
        item = self.currentItem()
        if item is None:
            return getattr(self.module, self.module.__all__[0])
        else:
            item_str = self.currentItem().text()
            return getattr(self.module, item_str)


class SelectTestCaseWidget(pg.LayoutWidget):
    def __init__(self, parent=None):
        #č nejdřív vytvořiť apku
        self.app = pg.mkQApp("WellMet")
        # 
        super().__init__(parent)
        
        self.setup()
        
        #č zobraziť
        self.show()
        #č a spustit smyčku
        self.app.exec_()
        
    def setup(self):
        self.setWindowTitle("Select testcase")
        self.box = None
        
        self.setup_tabs()
        self.addWidget(self.tabs, row=0, col=0, rowspan=1, colspan=2)
        
        self.btn_exit = QtWidgets.QPushButton('Exit')
        self.addWidget(self.btn_exit, row=1, col=0)
        self.btn_exit.clicked.connect(self.exit)
        
        self.btn_choose = QtWidgets.QPushButton('Next')
        self.addWidget(self.btn_choose, row=1, col=1)
        self.btn_choose.clicked.connect(self.choose)
        
    def exit(self):
        self.app.quit()
        sys.exit()
        
    def choose(self):
        tab_index = self.tabs.currentIndex()
        if tab_index == 0:
            ndim, ok = QtWidgets.QInputDialog.getInt(self,\
                    "Enter dimension of the problem","ndim", value=2, min=2)
            if not ok:
                ndim = 2 
            testcase_helper = self.tab_nd.extract_selected_item()
            self.box = testcase_helper(ndim)
        else:
            tab_widget = self.tab_widgets[tab_index-1]
            testcase_helper = tab_widget.extract_selected_item()
            self.box = testcase_helper()
        self.app.quit()
        
    def setup_tabs(self):
        # Initialize tab screen
        self.tabs = QtWidgets.QTabWidget(self)
        
        ## Add tabs
        # nD - parametrized
        self.tab_nd = TestCasesListWidget(testcases_nD, self)
        self.tabs.addTab(self.tab_nd, "nD testcases")
        
        # the rest - unparametrized
        self.tab_widgets = []
        for testcases, description in unparametrized_testcases:
            tab_widget = TestCasesListWidget(testcases, self)
            self.tabs.addTab(tab_widget, description)
            #č ať nám pythonovej GC nekrešne appku
            self.tab_widgets.append(tab_widget)
        

