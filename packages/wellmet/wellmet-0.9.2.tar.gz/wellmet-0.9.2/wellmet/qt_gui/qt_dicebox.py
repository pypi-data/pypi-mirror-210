import sys
import numpy as np
from .. import schemes
from ..candybox import CandyBox
#from ..dicebox.goal import Goal, Razitko, DiceBox
from ..dicebox.circumtri import CirQTri, CircumTri, QTri
from ..dicebox._exploration import DumbExploration
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets

spaces = ['R', 'aR', 'Rn', 'aRn', 'P', 'GK', 'G', 'aG', 'U', 'aU']
potentials = ['q_psee', 'psee', 'fee', 'fee2', 'ksee', 'chee', 'chee2', 'dd']



class DumbExplorationWidget(pg.parametertree.ParameterTree):
    def __init__(self, wt, parent=None):
        self.box = wt
        super().__init__(parent=parent, showHeader=False)
        self._set_param()
        self.setParameters(self.param, showTop=False)
    
    def _set_param(self):
        params = list()
        params.append({'name': 'q', 'type': 'float', \
                    'limits': (1, float('inf')), 'value': 10, 'default': 10})
        
        
        ### Create tree of Parameter objects
        # I don't know why that signals do not work for me
        # Only sigTreeStateChanged works, but I don't want to struggle with it
        # May be I'll report the issue 
        #self.param.sigValueChanged.connect(self.param_changed)
        #self.param.sigValueChanging.connect(self.param_changing)
        self.param = pg.parametertree.Parameter.create(name='params', type='group', children=params)
        
        #č branima sa rekurzii
        #оӵ рекурзилы пезьдэт!
        self.param_values = self.param.getValues()
        
    def __getattr__(self, attr):
        #č na teoreticky možnou rěkurziju vykašleme
        #оӵ рекурзия уз луы
        return self.param_values[attr][0]
        
    def setup_box(self):
        #č to je důležité! __getatr__ odsaď bere hodnoty
        self.param_values = self.param.getValues()
        
        self.box.sample_box = DumbExploration(
                self.box.sample_box, #č rekurze)
                q=self.q)



class QTriWidget(pg.parametertree.ParameterTree):
    def __init__(self, wt, parent=None):
        self.box = wt
        super().__init__(parent=parent, showHeader=False)
        self._set_param()
        self.setParameters(self.param, showTop=False)
    
    def _set_param(self):
        params = list()
        params.append({'name': 'convex_hull_degree', 'type': 'int', \
                    'title': "facet degree",\
                    'limits': (0, float('inf')), 'value': 5, 'default': 5,\
                    'tip': "Degree of Grundmann-Möller cubature"})
        params.append({'name': 'tri_degree', 'type': 'int', \
                    'title': "simplex degree",\
                    'limits': (0, float('inf')), 'value': 5, 'default': 5,\
                    'tip': "Degree of Grundmann-Möller cubature"})
        
#        params.append({'name': 'potential_mode', 'type': 'int', 'value': 2, 
#                    'title': "potential mode", 
#                    'limits': (0, float('inf')),
#                    'tip': "0: use rating, \n1: use pure potential, \nn: use pure ponetial for every n-th node"})
                    
        params.append({'name': 'circumcenters_only', 'title': "circumcenters only", 
                    'type': 'bool', 'value': False, 
                    'tip': "Do not treat integration nodes as candidates"})   
                    
        params.append({'name': 'store_candidates_metainformation', 'title': "store candidates metainformation", 
                    'type': 'bool', 'value': False, 
                    'tip': "True allows introspection"})   
                    
#        params.append({'name': 'weighted_entropy', 'title': "weighted entropy", 
#                    'type': 'bool', 'value': True, 
#                    'tip': "Choose to calculate agressive (weighted) or simple (vertex) entropy"})   
                    
        params.append({'name': 'q', 'type': 'float', 
                    'limits': (0, float('inf')), 'value': 1, 'default': self.box.nvar,
                    'tip': '"Agressiveness" of exploration'})
                    
        q = np.log(self.box.nvar) / self.box.nvar**2
        params.append({'name': 'psi_q', 'type': 'float', \
                    'title': "psi_q", \
                    'limits': (0, 1), 'value': 0.5, 'default': q,\
                    'tip': "Used for psi potential calculation"})   
        
        
        params.append({'name': 'holydays', 'type': 'int', \
                    'title': "holydays",  \
                    'limits': (0, float('inf')), 'value': 0, 'default': 10,\
                    'tip': "Every n-th point is an screening point. 0 to switch off"})
        
        
        ### Create tree of Parameter objects
        # I don't know why that signals do not work for me
        # Only sigTreeStateChanged works, but I don't want to struggle with it
        # May be I'll report the issue 
        #self.param.sigValueChanged.connect(self.param_changed)
        #self.param.sigValueChanging.connect(self.param_changing)
        self.param = pg.parametertree.Parameter.create(name='params', type='group', children=params)
        
        
        #č branima sa rekurzii
        #оӵ рекурзилы пезьдэт!
        self.param_values = self.param.getValues()
        
        
    def __getattr__(self, attr):
        #č na teoreticky možnou rěkurziju vykašleme
        #оӵ рекурзия уз луы
        return self.param_values[attr][0]
        
    def setup_box(self):
        #č to je důležité! __getatr__ odsaď bere hodnoty
        self.param_values = self.param.getValues()
        
        self.box.sample_box = QTri(
                self.box.sample_box, #č rekurze)
                self.convex_hull_degree,
                self.tri_degree,
                #potential_mode=self.potential_mode,
                store_candidates_metainformation=self.store_candidates_metainformation,
                q=self.q,
                psi_q=self.psi_q,
                circumcenters_only=self.circumcenters_only,
                holydays=self.holydays
                )



class CircumTriWidget(pg.parametertree.ParameterTree):
    def __init__(self, wt, parent=None):
        self.box = wt
        super().__init__(parent=parent, showHeader=False)
        self._set_param()
        self.setParameters(self.param, showTop=False)
    
    def _set_param(self):
        params = list()
        tschemes = schemes.get_tn_keys(self.box.nvar)
        params.append({'name': 'scheme', 'type': 'list', \
                    'title': "cubature scheme", \
                     'values': tschemes, 'value': 'stroud_tn_2_1b'})
        params.append({'name': 'degree', 'type': 'int', \
                    'title': "degree",\
                    'limits': (0, float('inf')), 'value': 5, 'default': 5,\
                    'tip': "Used only with Grundmann-Möller and Silvester cubaturas"})
        
#        params.append({'name': 'potential_mode', 'type': 'int', 'value': 2, 
#                    'title': "potential mode", 
#                    'limits': (0, float('inf')),
#                    'tip': "0: use rating, \n1: use pure potential, \nn: use pure ponetial for every n-th node"})
                    
        params.append({'name': 'circumcenters_only', 'title': "circumcenters only", 
                    'type': 'bool', 'value': False, 
                    'tip': "Do not treat integration nodes as candidates"})   
                    
        params.append({'name': 'store_candidates_metainformation', 'title': "store candidates metainformation", 
                    'type': 'bool', 'value': False, 
                    'tip': "True allows introspection"})   
                    
#        params.append({'name': 'weighted_entropy', 'title': "weighted entropy", 
#                    'type': 'bool', 'value': True, 
#                    'tip': "Choose to calculate agressive (weighted) or simple (vertex) entropy"})   
                    
        params.append({'name': 'q', 'type': 'float', 
                    'limits': (0, float('inf')), 'value': 1, 'default': self.box.nvar,
                    'tip': '"Agressiveness" of exploration'})
                    
        q = np.log(self.box.nvar) / self.box.nvar**2
        params.append({'name': 'psi_q', 'type': 'float', \
                    'title': "psi_q", \
                    'limits': (0, 1), 'value': 0.5, 'default': q,\
                    'tip': "Used for psi potential calculation"})   
        
        params.append({'name': 'shell_budget', 'type': 'int', \
                    'title': "shell budget",  \
                    'limits': (1, float('inf')), 'value': 1000, 'default': 1000,\
                    'tip': "Number of annulus candidates"})
        
        params.append({'name': 'holydays', 'type': 'int', \
                    'title': "holydays",  \
                    'limits': (0, float('inf')), 'value': 10, 'default': 10,\
                    'tip': "Every n-th point is sacrificed to the greatest safe simplex. 0 to switch off"})
        
        
        ### Create tree of Parameter objects
        # I don't know why that signals do not work for me
        # Only sigTreeStateChanged works, but I don't want to struggle with it
        # May be I'll report the issue 
        #self.param.sigValueChanged.connect(self.param_changed)
        #self.param.sigValueChanging.connect(self.param_changing)
        self.param = pg.parametertree.Parameter.create(name='params', type='group', children=params)
        
        p = self.param.child('scheme')
        p.sigValueChanged.connect(self.scheme_changed)
        
        #č podle implicitně nastavené scheme
        self.param.child('degree').hide()
        
        #č branima sa rekurzii
        #оӵ рекурзилы пезьдэт!
        self.param_values = self.param.getValues()
        
    def scheme_changed(self, parameter):
        scheme = parameter.value()
        if scheme in ('Grundmann-Möller', 'Silvester open', 'Silvester closed'):
            self.param.child('degree').show()
        else:
            self.param.child('degree').hide()
        
    def __getattr__(self, attr):
        #č na teoreticky možnou rěkurziju vykašleme
        #оӵ рекурзия уз луы
        return self.param_values[attr][0]
        
    def setup_box(self):
        #č to je důležité! __getatr__ odsaď bere hodnoty
        self.param_values = self.param.getValues()
        
        scheme = schemes.get_tn_scheme(self.scheme, self.box.nvar, self.degree)
        
        
        self.box.sample_box = CircumTri(
                self.box.sample_box, #č rekurze)
                scheme,
                #potential_mode=self.potential_mode,
                store_candidates_metainformation=self.store_candidates_metainformation,
                q=self.q,
                psi_q=self.psi_q,
                shell_budget=self.shell_budget,
                circumcenters_only=self.circumcenters_only,
                holydays=self.holydays
                )



class CirQTriWidget(pg.parametertree.ParameterTree):
    def __init__(self, wt, parent=None):
        self.box = wt
        super().__init__(parent=parent, showHeader=False)
        self._set_param()
        self.setParameters(self.param, showTop=False)
    
    def _set_param(self):
        params = list()
        tschemes = schemes.get_tn_keys(self.box.nvar)
        params.append({'name': 'scheme', 'type': 'list', \
                    'title': "cubature scheme", \
                     'values': tschemes, 'value': 'stroud_tn_3_6b'})
        params.append({'name': 'degree', 'type': 'int', \
                    'title': "degree",\
                    'limits': (0, float('inf')), 'value': 5, 'default': 5,\
                    'tip': "Used only with Grundmann-Möller and Silvester cubaturas"})
        
        params.append({'name': 'convex_hull_degree', 'type': 'int', \
                    'title': "facet degree",\
                    'limits': (0, float('inf')), 'value': 5, 'default': 5,\
                    'tip': "Degree of Grundmann-Möller cubature"})
                    
        params.append({'name': 'q', 'type': 'float', 
                    'limits': (0, float('inf')), 'value': 1, 'default': self.box.nvar,
                    'tip': '"Agressiveness" of exploration'})
        
        params.append({'name': 'holydays', 'type': 'int', \
                    'title': "holydays",  \
                    'limits': (0, float('inf')), 'value': 0, 'default': 10,\
                    'tip': "Every n-th point is an screening point. 0 to switch off"})
        
        
        ### Create tree of Parameter objects
        # I don't know why that signals do not work for me
        # Only sigTreeStateChanged works, but I don't want to struggle with it
        # May be I'll report the issue 
        #self.param.sigValueChanged.connect(self.param_changed)
        #self.param.sigValueChanging.connect(self.param_changing)
        self.param = pg.parametertree.Parameter.create(name='params', type='group', children=params)
        
        p = self.param.child('scheme')
        p.sigValueChanged.connect(self.scheme_changed)
        
        #č podle implicitně nastavené scheme
        self.param.child('degree').hide()
        
        #č branima sa rekurzii
        #оӵ рекурзилы пезьдэт!
        self.param_values = self.param.getValues()
        
    def scheme_changed(self, parameter):
        scheme = parameter.value()
        if scheme in ('Grundmann-Möller', 'Silvester open', 'Silvester closed'):
            self.param.child('degree').show()
        else:
            self.param.child('degree').hide()
        
    def __getattr__(self, attr):
        #č na teoreticky možnou rěkurziju vykašleme
        #оӵ рекурзия уз луы
        return self.param_values[attr][0]
        
    def setup_box(self):
        #č to je důležité! __getatr__ odsaď bere hodnoty
        self.param_values = self.param.getValues()
        
        scheme = schemes.get_tn_scheme(self.scheme, self.box.nvar, self.degree)
        
        self.box.sample_box = CirQTri(
                self.box.sample_box, #č rekurze)
                scheme,
                convex_hull_degree=self.convex_hull_degree,
                q=self.q,
                holydays=self.holydays
                )




class DumbDiceBoxWidget(QtWidgets.QWidget):
    def __init__(self, wt, parent=None):
        self.box = wt
        super().__init__(parent=parent)
        
    def setup_box(self):
        # do the thing
        self.box.sample_box = DiceBox(self.box.sample_box)


class RazitkoWidget(pg.parametertree.ParameterTree):
    def __init__(self, wt, parent=None):
        self.box = wt
        super().__init__(parent=parent, showHeader=False)
        self._set_param()
        self.setParameters(self.param, showTop=False)
    
    def _set_param(self):
        params = list()
        tschemes = schemes.get_tn_keys(self.box.nvar)
        params.append({'name': 'scheme', 'type': 'list', \
                    'title': "cubature scheme", \
                     'values': tschemes, 'value': tschemes[0]})
        params.append({'name': 'degree', 'type': 'int', \
                    'title': "degree",\
                    'limits': (0, float('inf')), 'value': 5, 'default': 5,\
                    'tip': "Used only with Grundmann-Möller and Silvester cubaturas"})
        
        params.append({'name': 'tri_space', 'type': 'list', 'value': 'G', \
                    'title': "triangulation space", 'values': spaces})
        params.append({'name': 'tree_space', 'type': 'list', 'value': 'None', \
                    'title': "tree (potential) space", 'values': spaces+['None'], \
                    'tip': """Space where distances (and densities) are 
                    calculated. 'None' means triangulation space will be used"""})
        params.append({'name': 'sampling_space', 'type': 'list', 'value': 'None', \
                    'title': "sampling space", 'values': spaces+['None'], \
                    'tip': """Space where convex hull is being integrated. 
                    'None' means triangulation space will be used"""})
        params.append({'name': 'kechato_space', 'type': 'list', 'value': 'U', \
                    'title': "kechato space", 'values': spaces, \
                    'tip': "Only used with ksee potential"})
        params.append({'name': 'potential', 'type': 'list', 'value': 'q_psee', \
                    'title': "potential", \
                    'values': potentials})
        q = np.log(self.box.nvar) / self.box.nvar**2
        params.append({'name': 'q', 'type': 'float', \
                    'title': "q", \
                    'limits': (0, 1), 'value': q, 'default': q,\
                    'tip': "Only used with q_psee potential"})   
        params.append({'name': 'p_norm', 'type': 'float', \
                    'title': "p norm", \
                    'limits': (1, float('inf')), 'value': 2, 'default': np.inf,
                    'tip': "Space metric - used for distance calculations"})   
        params.append({'name': 'budget', 'type': 'int', \
                    'title': "Shull budget",  \
                    'limits': (1, float('inf')), 'value': 1000, 'default': 1000,\
                    'tip': "Number of nodes for outside integration"})
        params.append({'name': 'LHS_correction', \
                    'title': "LHS-like nodes placement",\
                    'type': 'bool', 'value': False })
        
        ### Create tree of Parameter objects
        # I don't know why that signals do not work for me
        # Only sigTreeStateChanged works, but I don't want to struggle with it
        # May be I'll report the issue 
        #self.param.sigValueChanged.connect(self.param_changed)
        #self.param.sigValueChanging.connect(self.param_changing)
        self.param = pg.parametertree.Parameter.create(name='params', type='group', children=params)
        
        #č branima sa rekurzii
        #оӵ рекурзилы пезьдэт!
        self.param_values = self.param.getValues()
        
    def __getattr__(self, attr):
        #č na teoreticky možnou rěkurziju vykašleme
        #оӵ рекурзия уз луы
        return self.param_values[attr][0]
        
    def setup_box(self):
        #č to je důležité! __getatr__ odsaď bere hodnoty
        self.param_values = self.param.getValues()
        
        scheme = schemes.get_tn_scheme(self.scheme, self.box.nvar, self.degree)
        
        if self.tree_space == 'None':
            tree_space = None
        else:
            tree_space = self.tree_space
            
        if self.sampling_space == 'None':
            sampling_space = None
        else:
            sampling_space = self.sampling_space
            
#        try:
#            stm_filename = self.box.filename + '_stm'
#        except AttributeError:
#            stm_filename = None
        
        
        #č implicitně vložime bombonjeru
        self.box.samplebox.sampled_plan = CandyBox(self.box.f_model())
        # do the thing
        self.box.sample_box = Razitko(
                self.box.sample_box, #č rekurze)
                scheme,
                tri_space=self.tri_space,
                tree_space=tree_space,
                sampling_space=sampling_space,
                kechato_space=self.kechato_space, 
                potential=self.potential, 
                q=self.q,
                p_norm=self.p_norm,
                budget=self.budget,
                LHS_correction=self.LHS_correction,
                #stm_filename=stm_filename,
                design=None
                )




class GoalWidget(pg.parametertree.ParameterTree):
    def __init__(self, wt, parent=None):
        self.box = wt
        super().__init__(parent=parent, showHeader=False)
        self._set_param()
        self.setParameters(self.param, showTop=False)
    
    def _set_param(self):
        params = list()
        tschemes = schemes.get_tn_keys(self.box.nvar)
        params.append({'name': 'scheme', 'type': 'list', \
                    'title': "cubature scheme", \
                     'values': tschemes, 'value': tschemes[0]})
        params.append({'name': 'degree', 'type': 'int', \
                    'title': "degree",\
                    'limits': (0, float('inf')), 'value': 5, 'default': 5,\
                    'tip': "Used only with Grundmann-Möller and Silvester cubaturas"})
        
        params.append({'name': 'tri_space', 'type': 'list', 'value': 'G', \
                    'title': "triangulation space", 'values': spaces})
        params.append({'name': 'tree_space', 'type': 'list', 'value': 'None', \
                    'title': "tree (potential) space", 'values': spaces+['None'], \
                    'tip': """Space where distances (and densities) are 
                    calculated. 'None' means triangulation space will be used"""})
        params.append({'name': 'kechato_space', 'type': 'list', 'value': 'U', \
                    'title': "kechato space", 'values': spaces, \
                    'tip': "Only used with ksee potential"})
        params.append({'name': 'potential', 'type': 'list', 'value': 'q_psee', \
                    'title': "potential", \
                    'values': potentials})
        q = np.log(self.box.nvar) / self.box.nvar**2
        params.append({'name': 'q', 'type': 'float', \
                    'title': "q", \
                    'limits': (0, 1), 'value': q, 'default': q,\
                    'tip': "Only used with q_psee potential"})   
        params.append({'name': 'p_norm', 'type': 'float', \
                    'title': "p norm", \
                    'limits': (1, float('inf')), 'value': 2, 'default': np.inf,
                    'tip': "Space metric - used for distance calculations"})   
        params.append({'name': 'shell_budget', 'type': 'int', \
                    'title': "shell budget",  \
                    'limits': (1, float('inf')), 'value': 1000, 'default': 1000,\
                    'tip': "Number of annulus candidates"})
        
        params.append({'name': 'outer_budget', 'type': 'int', \
                    'title': "Outer budget",  \
                    'limits': (1, float('inf')), 'value': 100, 'default': 100,\
                    'tip': "Number of candidates nodes outside of circumscribed d-ball"})
        
        params.append({'name': 'LHS_correction', \
                    'title': "LHS-like nodes placement",\
                    'type': 'bool', 'value': False })
        
        ### Create tree of Parameter objects
        # I don't know why that signals do not work for me
        # Only sigTreeStateChanged works, but I don't want to struggle with it
        # May be I'll report the issue 
        #self.param.sigValueChanged.connect(self.param_changed)
        #self.param.sigValueChanging.connect(self.param_changing)
        self.param = pg.parametertree.Parameter.create(name='params', type='group', children=params)
        
        #č branima sa rekurzii
        #оӵ рекурзилы пезьдэт!
        self.param_values = self.param.getValues()
        
    def __getattr__(self, attr):
        #č na teoreticky možnou rěkurziju vykašleme
        #оӵ рекурзия уз луы
        return self.param_values[attr][0]
        
    def setup_box(self):
        #č to je důležité! __getatr__ odsaď bere hodnoty
        self.param_values = self.param.getValues()
        
        scheme = schemes.get_tn_scheme(self.scheme, self.box.nvar, self.degree)
        
        if self.tree_space == 'None':
            tree_space = None
        else:
            tree_space = self.tree_space
            
        try:
            stm_filename = self.box.filename + '_stm'
        except AttributeError:
            stm_filename = None
        
        #č implicitně vložime bombonjeru
        self.box.samplebox.sampled_plan = CandyBox(self.box.f_model())
        self.box.sample_box = Goal(
                self.box.sample_box, #č rekurze)
                scheme,
                tri_space=self.tri_space,
                tree_space=tree_space,
                kechato_space=self.kechato_space, 
                potential=self.potential, 
                q=self.q,
                p_norm=self.p_norm,
                shell_budget=self.shell_budget,
                outer_budget=self.outer_budget,
                LHS_correction=self.LHS_correction,
                stm_filename=stm_filename,
                )
        

class SetupDiceBoxWidget(pg.LayoutWidget):
    def __init__(self, wt, parent=None):
        self.box = wt
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
        self.setWindowTitle("Set up sequential algorithm")
        
        self.setup_tabs()
        self.addWidget(self.tab_widget, row=0, col=0, rowspan=1, colspan=2)
        
        self.btn_skip = QtWidgets.QPushButton('Skip')
        self.addWidget(self.btn_skip, row=1, col=0)
        self.btn_skip.clicked.connect(self.skip)
        
        self.btn_choose = QtWidgets.QPushButton('Create')
        self.addWidget(self.btn_choose, row=1, col=1)
        self.btn_choose.clicked.connect(self.create)
        
    def skip(self):
        self.app.quit()
        
    def create(self):
        tab_index = self.tab_widget.currentIndex()
        self.tabs[tab_index].setup_box()
        self.app.quit()
        
    def setup_tabs(self):
        # Initialize tab screen
        self.tab_widget = QtWidgets.QTabWidget(self)
        #č šlo by to, samozřejmně, i přes Qt
        #č ale stejně musíme reference explicitně ukladat 
        #č aby je nám Python nehodil
        self.tabs = []


        box_widget = CirQTriWidget(self.box, self)
        self.tab_widget.addTab(box_widget, "CirQTri")
        self.tabs.append(box_widget)        
        

