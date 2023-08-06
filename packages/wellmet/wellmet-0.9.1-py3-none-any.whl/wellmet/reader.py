
import csv
import numpy as np
from .samplebox import SampleBox
from .f_models import Ingot


class ExportError(BaseException):
    pass


class Store(list):
    """
    stateful object to keep consistency of using append()
    # reader bude pokažde otevirat/zavirat soubor, což není úplně ideální,
    # ale zás,
    # předpokladá se, že každej vzorek musí být schvalen vědeckou radou
    # csv umožňuje dozápis
    """
    
    #č pro formu. Když už dědíme až od seznamu!
    __slots__ = ('filename', 'namedtuple')
    
    def __new__(cls):
        raise Exception("Please, use Store.create() constructor")
    
    @classmethod
    def create(cls, filename, namedtuple):
        # piece of black magic
        self = super().__new__(cls)
        
        try:
            with open(filename + '.csv', 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
                #č první řadek - jmeno n-tice
                first_row = next(reader)
                if namedtuple.__name__ != first_row[0]:
                    raise ExportError("%s of target csv is different from %s passed"%\
                                     (namedtuple.__name__, first_row[0]))
                if namedtuple._fields != tuple(next(reader)):
                    raise ExportError("Target csv have inconsictent data")
                
                #č aby pandas nám vytvořil pěkné krasné hlavičky
                #č a seznam seznamů sežral, 
                #č první položka musí být namedtuple.
                list.append(self, namedtuple(*next(reader)))
                
                list.extend(self, reader)
                    
        except FileNotFoundError:
            pass
            
        self.filename = filename
        self.namedtuple = namedtuple
            
        return self
            
            
    def append(self, estimation):
        if not isinstance(estimation, self.namedtuple):
            raise ExportError("Data are of incorrect type")
        with open(self.filename + '.csv', 'a', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
            if csvfile.tell() == 0:
                csv_writer.writerow([estimation.__class__.__name__])
                csv_writer.writerow(estimation._fields)
            csv_writer.writerow(estimation)
        
        super().append(estimation)



#č Mám hrozné vzpomínky z ladění csv-čka.
#č Pamatuji si, jak po opakované opravě chyby exportu
#č jsem vztekl a posunul celou tu funkcionalitu do tohoto modulu.
#č Teď jsem analyzoval, co to vlastně bylo, na jaké problémy jsem tehdy narazil.
#č No, vlastně, vidím, že export v BlackBox jíž byl doladěný před tím, 
#č než vznikl samostatný SampleBox. BlackBox tehdy inicializoval prazdný,
#č s prazdnými g_values, z f-ka bral pouze rozdělení. Hned pridaval hodnoty z
#č csv souboru, když se nic nepřidalo - exportoval hlavičky, při přidaní vzorku appendoval.
#č Po vzníku SampleBox se to stalo neudržitelným:
#č bylo třeba hlídat gm_signatures, aby byly stejné.
#č Rozhodující tehdy stal chybící export hlaviček pri inicializacii (jásná regrese),
#č ale i tak zajištění, třeba neprazdné gm_signature v BlackBoxu už by bylo otravné.
#č Každopadně, tahle spousta problemu tykala SampleBoxu kvůli tomu,  
#č že bylo třeba data i načítat, bylo třeba zajištovat správné rozdělení,
#č bylo třeba hlídat gm_signature v hlavičce.
#č Když ale zaměstnáme csv pro export odhadů, tak nás veškeré tyhle
#č pytloviny se nebudou tykat: krabička tyhle data nebude potřebovat,
#č hlavičku jednoduše vytvoříme jen když soubor ještě neexistuje
#č a je nám vlastně šuma, co se do souboru bude psat: 
#č nechaj krabička tam píše co chce.
#č Zkratka, csv zůstavá výbornou volbou pro uložiště dat i v roce 2021, doporučujem!
#č (strukturování odhadů a valka s pandas byly chybou)

def export_estimation(filename, stm_dict):
    with open(filename + '.csv', 'a', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
        if csvfile.tell() == 0:
            csv_writer.writerow(stm_dict.keys())
        csv_writer.writerow(stm_dict.values())
        
        

class Reader:
    """
    stateful object to keep consistency of using append()
    First rule of writing API - write example of use
    # musel tedy tady bejt...
    
    zkusím takovehle delegování
    
    # reader bude pokažde otevirat/zavirat soubor, což není úplně ideální,
    # ale zás,
    # předpokladá se, že každej vzorek musí být schvalen vědeckou radou
    # csv umožňuje dozápis
    """
    
    # piece of black magic
    def __new__(cls, filename, f_model=None):
        """
        Здесь отталкиваемся от файла
        """
        sb = super().__new__(cls)
        sb.filename = filename
        try: # sample box nemá vůbec smysl schovavat
            sb.sample_box = reader(filename, f_model)
            sb.append_allowed = True
        except FileNotFoundError:
            # Штош...
            sb.append_allowed = False
            if f_model is not None:
                sb.sample_box = SampleBox(f_model)
            print("Reader:", filename + '.csv', "ӧвӧл")
        return sb
            
    @classmethod
    def FromSampleBox(cls, filename, sample_box):
        """
        Здесь отталкиваемся от сэмплбоксу
        """
        sb = super().__new__(cls)
        # nepotrebujeme žádné rozdělení, nic
        sb.sample_box = sample_box
        sb.filename = filename
        sb.append_allowed = False
        return sb
            
    def __len__(self):
        return self.sample_box.nsim
    
    def __call__(self):
        #č ne že bych chtěl sahat na kód readeru
        #č kvůli blbostem (kdo to, kruci, potřebuje?),
        #č ale formálně Reader
        #č musí být SampleBox compliant
        #č a musí být callable
        return self.sample_box()
                
    def __getitem__(sb, slice):
        # stačí vratit sample_box
        return sb.sample_box[slice]
    
    def __getattr__(sb, attr):
        if attr == 'reader':
            return sb
        # По всем (почти) вопросам обращайтесь 
        # на нашу горячую линию 
        elif attr == 'sample_box':
            return None
        else:
            return getattr(sb.sample_box, attr)        
            
#    def read(self):
#        return self.__sbox        
        
    def force_read(self):
        try:
            self.sample_box = reader(self.filename, self.sample_box.sampled_plan)
            self.append_allowed = True
            return self.sample_box
        except AttributeError:
            self.sample_box = reader(self.filename)
            self.append_allowed = True
            return self.sample_box
        except FileNotFoundError:
            # Штош...
            print("Reader:", self.filename + '.csv', "opravdu ӧвӧл")
            
    def write(self):
        export(self.filename, self.sample_box)
        self.append_allowed = True
    
    # что бы эта бурда могла делать?
#    def force_write(self):
#        self.__sbox = sample_box
#        export(self.__filename, sample_box)
        
    def add_sample(self, sample_box):
        if self.append_allowed and (self.sample_box.gm_signature == sample_box.gm_signature):
            self.sample_box.add_sample(sample_box)
            append(self.filename, sample_box)
        elif 'sample_box' in dir(self):
            self.sample_box.add_sample(sample_box)
            if self.sample_box.nsim > 0:
                export(self.filename, self.sample_box)
                self.append_allowed = True
        else:
            self.sample_box = sample_box
            if self.sample_box.nsim > 0:
                export(self.filename, self.sample_box)
                self.append_allowed = True
                
      
      # průbežný export
#        if bx.filename:
#            if gm_signature == input_sample.gm_signature:
#                reader.append(bx.filename + '.csv', input_sample)
#            else:
#                bx.export(bx.filename)
      
        
            

#
# import simulations
#
def reader(filename, f_model=None):
    rows = []
    with open(filename + '.csv', 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
        for row in reader:
            rows.append(row)
            
    # předpokladam, že na prvních dvou řadcích jsou gm_signature a popísek
    data = np.atleast_2d(rows[2:])
    
    if f_model is None:
        # veškeré datové řadky, sloupy -  od (včetně) do (nezahrnuje)
        return SampleBox(Ingot(data[:,:-2]), data[:,-2:-1].reshape(-1), rows[0][0])
    else:
        sample = f_model()
        sample.add_sample(data[:,:-2])
        return SampleBox(sample, data[:,-2:-1].reshape(-1), rows[0][0])



def append(filename, sample_box):
    """
    Святые угодники, объясните мне кто-нибудь, почему я здесь не использ..овал
    context manager?
    """
    if sample_box.nsim == 0:
        return False
        
    with open(filename + '.csv', 'a', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
        
        # bacha! není tu žádná kontrola, co se kam zapisuje!
        for i in range(sample_box.nsim):
            row = [sample_box.R[i, j] for j in range(sample_box.nvar)]
            row.append(sample_box.g_values[i])
            row.append(int(sample_box.failsi[i]))
            csv_writer.writerow(row)
        #csvfile.close()

def Export(filename, sample_box):
    """
    vratíme nový Reader objekt
    """
    export(filename, sample_box)
    return Reader.FromSampleBox(filename, sample_box)

def export(filename, sample_box):
    if sample_box.nsim == 0:
        return False
        
    with open(filename + '.csv', 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
        
        # gm_signature
        csv_writer.writerow([sample_box.gm_signature])
        
        # popísky 
        row = ['var ' + str(j+1) for j in range(sample_box.nvar)]
        row.append('value')
        row.append('failure')
        csv_writer.writerow(row)        
        
        for i in range(sample_box.nsim):
            row = [sample_box.R[i, j] for j in range(sample_box.nvar)]
            row.append(sample_box.g_values[i])
            row.append(int(sample_box.failsi[i]))
            csv_writer.writerow(row)
        # csvfile.close()
    
    
