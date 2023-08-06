#!/usr/bin/env python
# coding: utf-8

import numpy as np

from scipy.spatial import KDTree
from scipy.spatial.distance import cdist

import collections # for defaultdict, namedtuple

from . import IS_stat
from .candynodes import CandyNodes
from . import sball 


        
        

#č vlastní slovník se dycky hodí
class WardrobeDict(dict):
    def __init__(self):
        super().__init__()
        self.index = 0
        
    def add(self, item):
        #č nulový index se nesmí vratit
        #č CV ho použivá jako False
        self.index += 1
        #оӵ мар ке вал отын - туж жаль
        self[self.index] = item
        return self.index



TData = collections.namedtuple('TData', ('X', 'imask', 'dd'))
#VorSTM = collections.namedtuple('VorSTM', \
#       ('nsim', 'failure', 'mixed', 'pfv', 'pfw'))

## TRI-compatible estimation
#TriSTM = collections.namedtuple('TriSTM', \
#       ('outside', 'success', 'failure', 'mixed', 'pfv', 'pfw'))

        

# HalfspaceVoronoi
# TwoFaces :)
# TwoHalvesVoronoi
# TwoHalves
class TwoHorses:
    """
    č Motivace třídy:
    č Bylo mi lito vyhazovaných informací, které normálně
    č získávám z KDTree (dd, ii) a tak hledal jsem cestu 
    č jak ty informace, ta data vůbec nevytvařit.
    č Já je skutečně nepotřebuji ve fázi vzorkování.
    č Všechno co potřebujeme - 
    č vědět zda i,j jsou nejblížší, nebo ne.
    
    č Úvod:
    č Ve výsokých dimenzích (od 15, možná až od 20) 
    č věda nezná žádný způsob najít nejblížší vzorek
    č rychlejc jak brutforsem. 
    č To je jako najit vzdálenosti do všech vzorků
    č a pak si zvolit s tou (těmi) nejmenšími.
    č KDTree ve scipy uvnitř zřejmě přechází na brutforce,
    č neboť má stejný výkon jako cdist 
    č Složitost úlohy tedy uměrna npoints*nnodes
    
    č Hlavní myšlenka třídy:
    č Využit (zase) geometrických informací.
    č Kontaktní hyperrovina mezí "i" a "j" dělí
    č prostor na dva poloprostory.
    č Stejně jako dělí vzorky i bodíky do dvou skupin.
    č Skalarním součínem jednoduše zjistíme
    č do jaké poloviny patří.
    č Bodíky patří do oblasti (i,j) jen pokud mají 
    č vzorek "i" jako nejblížší v jednom z poloprostoru
    č a "j" - v druhém.
    č Bodíky, třeba, z poloprostoru "i" nejdřív 
    č proženeme KDTree přes vzorky na straně "i" 
    č a jenom ty, které mají "i" jako nejblížší
    č pustíme dál přes KD strom na straně "j".
    č Můžeme očekávát zrychlení díky tomu, 
    č že většína vzorků mimo kontaktní oblast
    č bude vyfiltrována jíž na prvním stromě.
    č Stromy ale nejsou balancovány, jeden může být 
    č představen jedním vzorkem, druhý - zbytkem.
    č
    č Musíme být opatrní, protože kontakt nemusí
    č vůbec existovat a je třeba ujistit se, že
    č nejblížší vzorek z druhého poloprostoru
    č je globálně nejblížší. (v tom prvním musíme
    č dělat dotáz na dva nějblížších)
    
    č Neplatí:
    č Neplatí, že by stačílo v každem ze stromu 
    č zkontolovat, že příslušný vzorek (i, nebo j)
    č je nejblížší
    
    č Už chapu, že hyperroviny, normály, meze atd.
    č nehrajou až takovou roli. Stačilo by 
    č i náhodně rozdělit vzorky na dvě sady tak,
    č aby v jedné sadě bylo i-čko, v druhé - j-čko.
    
    č Za úkol máme jednodušší úkol: vyhodit bodíky, 
    č které nejsou nejblížší
    č Možné variánty strategie (od blbého k chytejšímu):
    č 1. Smyčka. Když někdo jinej je blížší, tak s bodíkem
    č    se loučíme. Cečkovej kód knihoven ale nedoženeme...
    #for vzorečíček in vzorky: if dist(vzočíček) < l_i: ...
    č 2. Nasekat vzorky na 100500 skupin (nsim >> 100500)
    č    V každé skupině bereme dva nejblížších a vyhazujeme
    č    bodíky, pokud "i", nebo "j" nejsou nejblížší. 
    č    Na konci výber globálních sousedů ze všech skupin.
    č 3. Libovolně dělíme vzorky na dvě skupiny,
    č    do jedné patří i, do druhé j.
    č    a. Prohnat bodíky i-tou skupinou,
    č       vyhodit co není k "i" nejblížší,
    č       vzít vzdálenosti do dvou nejblížších.
    č    b. Opakovat pro j-tou, zas dva nejblížších
    č    c. Hledáme globální min ze čtyrž vzorků
    č 4. Dělíme vzorky na dvě skupíny libovolně
    č    proloženou hyperrovinou mezí nima.
    č    Můžeme na dvě skupiny dělit i bodíky.
    č    Moc to nepřínáší, jenom že budou blíž
    č    k svým globálním sousedům a efektivnějc maskovány.
    č             | vzorky "j" : efektivně jedna z ndim
    č    bodíky i |            : dimenzí ztracena,
    č                            rozhodování je podle 
    č                             zbývajících ndim-1
    č             | vzorky "j" : provedena klasterizace
    č             | bodíky j   : podel jedné dimenze
    č                            ekvivalentní jednomu kroku KDTree
    č 5. Dělíme vzorky na dvě skupíny kontaktní (kolmou)
    č    hyperrovinou přesně v půlce mezí "i" a "j":
    č    hyperrovinou je garantovano, že patří-li bodík 
    č    z "i" do kontaktu (i,j), tak je nejblížší. 
    č    Zbyde zkontrolovat ten druhý.
    č    a. Prohnat bodíky i-tou skupinou,
    č       vyhodit co není k "i" nejblížší,
    č       vzít vzdálenosti do dvou nejblížších.
    č    b. Opakovat pro j-tou, stačí jeden nejblížší
    č    c. Zkontrolujeme jenom, že d2_i > d1_j
    
    
    """
    def __init__(self, points, couple_indices):
        i, j = couple_indices
        #č vektor zadáme přímkou mezí vzorky
        #č od "i" k "j", normalizovat nebudeme
        self.normal_vector = points[j] - points[i]
        
        #č jako indice zkusme použit bod na usečce uprostřed mezí vzorky
        half_point = np.mean(points[[i, j]], axis=0) 
        
        self.delimit = np.inner(half_point, self.normal_vector)
        
        #č pokud skalarní součin je menší jak delimit
        #č (protože směr normály od "i" k "j"),
        #č tak patří hledané do poloprostoru "i"
        mask = (points @ self.normal_vector) < self.delimit 
        
        self.tree_i = KDTree(points[mask])
        self.tree_j = KDTree(points[~mask])
        
        #č neznám convinient cestu pro získaní
        #č tamtamtoho indexu na maskovaném poli
        #č np.ma mně příjde zbytečným
        # ha! monkey patching
        self.tree_i.idx = len(mask[:i][mask[:i]])
        self.tree_j.idx = len(mask[:j][~mask[:j]])
        
        
    def query(self, nodes, p_norm=2):
        #č pokud skalarní součin je menší jak delimit
        #č (protože směr normály od "i" k "j"),
        #č tak patří hledané do poloprostoru "i"
        halfmask = (nodes @ self.normal_vector) < self.delimit 
        
        nodes_i = nodes[halfmask]
        nodes_j = nodes[~halfmask]
        
        #č globální maska
        gmask = np.ones(len(nodes), dtype=bool)
        
        mask_i, dd_i = self._run(nodes_i, self.tree_i, self.tree_j, p_norm)
        mask_j, dd_j = self._run(nodes_j, self.tree_j, self.tree_i, p_norm)
        
        gmask[halfmask] = mask_i
        gmask[~halfmask] = mask_j
        
        
        dd_mask = halfmask[gmask]
        dd = np.empty((len(dd_i)+len(dd_j), 2))
        dd[dd_mask] = dd_i
        dd[~dd_mask] = dd_j
        
        return gmask, TData(X=nodes[gmask], imask=dd_mask, dd=dd)
        
        
        
    @staticmethod
    def _run(nodes, tree_1, tree_2, p_norm):
        dd, ii = tree_1.query(nodes, k=2, p=p_norm)
        mask = (ii[:, 0] == tree_1.idx)
        
        d, j = tree_2.query(nodes[mask], k=1, p=p_norm)
        mask_2 = (j == tree_2.idx)
        mask[mask] = mask_2
        
        mask_3 = dd[mask][:,1] > d[mask_2]
        mask[mask] = mask_3
        
        #č smí to být jen takto: nejdřív osa, pak maska
        #č opačné pořadí nefunguje
        dd[:,1][mask] = d[mask_2][mask_3]
        return mask, dd[mask]
        
        
        


class TwoPoints:
    def __init__(self, points, couple_indices, workers=1):
        self.couple_indices = couple_indices
        self.workers = workers
        i, j = couple_indices
        
        self.point_i = point_i = points[i]
        self.point_j = point_j = points[j]
        #č vektor zadáme přímkou mezí vzorky
        #č od "i" k "j", normalizovat nebudeme
        self.normal_vector = point_j - point_i
        
        #č jako indice zkusme použit bod na usečce uprostřed mezí vzorky
        self.half_point = np.mean(points[[i, j]], axis=0) 
        
        self.delimit = np.inner(self.half_point, self.normal_vector)
        
        #č pokud skalarní součin je menší jak delimit
        #č (protože směr normály od "i" k "j"),
        #č tak patří hledané do poloprostoru "i"
        mask = (points @ self.normal_vector) < self.delimit 
        
        #č vypnu optimizace KD stromu. 
        #č Netestoval však, zda je to skutečně rychlejší.
        self.tree_i = KDTree(points[mask], compact_nodes=False, balanced_tree=False)
        self.tree_j = KDTree(points[~mask], compact_nodes=False, balanced_tree=False)
        #č neznám convinient cestu pro získaní
        #č tamtamtoho indexu na maskovaném poli
        #č np.ma mně příjde zbytečným
        # ha! monkey patching
        self.tree_i.idx = len(mask[:i][mask[:i]])
        self.tree_j.idx = len(mask[:j][~mask[:j]])
        
        #č bacha na indexy. Musíme vyhodit i-tý a j-tý vzorky
        mask[i] = False
        self.points_i = points[mask]
        #č teď ale jedeme se stejnou, ale invertovanou maskou 
        mask[i] = True
        mask[j] = True
        self.points_j = points[~mask]
        
        
    def query(self, nodes, order='F'):
        #č uživatel získával hodně nekonzistentní výstup
        #č když posílal pouze jeden bodík.
        nodes = np.atleast_2d(nodes)
        #č pokud skalarní součin je menší jak delimit
        #č (protože směr normály od "i" k "j"),
        #č tak patří hledané do poloprostoru "i"
        halfmask = (nodes @ self.normal_vector) < self.delimit 
        
        nodes_i = nodes[halfmask]
        nodes_j = nodes[~halfmask]
        
        
        status_i = status_j = False
        if nodes_i.size:
            status_i, mask_i, dd_i = self._run(self.point_j, self.points_i, 
                                                self.tree_j, nodes_i, order)
        
        if nodes_j.size:
            status_j, mask_j, dd_j = self._run(self.point_i, self.points_j, 
                                                self.tree_i, nodes_j, order)
        
        if not (status_i or status_j):
            return False, None, None
        
        #č globální maska
        gmask = np.empty(len(nodes), dtype=bool)
        
        if status_i and not status_j:
            gmask[halfmask] = mask_i
            gmask[~halfmask] = False
            return True, gmask, TData(X=nodes[gmask], imask=mask_i[mask_i], dd=dd_i)
            
        if status_j and not status_i:
            gmask[halfmask] = False
            gmask[~halfmask] = mask_j
            return True, gmask, TData(X=nodes[gmask], imask=~mask_j[mask_j], dd=dd_j)
            
        
        gmask[halfmask] = mask_i
        gmask[~halfmask] = mask_j
        
        dd_mask = halfmask[gmask]
        dd = np.empty(len(dd_i) + len(dd_j))
        dd[dd_mask] = dd_i
        dd[~dd_mask] = dd_j
        
        return True, gmask, TData(X=nodes[gmask], imask=dd_mask, dd=dd)
    
    
    @staticmethod
    def _run(center_2, points_1, tree_2, nodes_1, order):
        """
        č Úkolem první fáze je vyhodit co nejvíc bodíků
        č Bodíky bereme z i-tého poloprostoru a kontrolní vzdálenosti - 
        č vůči vzorku "j" z protílehlé strany.
        č Předpokládáme, že na konci první fázi získame už
        č dobře vyfiltrované tečičky, které přece pro formu
        č musíme zkontrolovat i vůči vzorkům na opačné straně.
        č Předpokladáme, že zůstaly jíž vícemené dobré bodíky
        č a že smyčka druhé fáze už by musela běžet přes skoro všechno.
        č Proto se nebudeme snažit dohnat Cečkovej kód v Pythonu
        č a poslední část pokorně svěříme KDTree - 
        č nejrychlejší implementaci the nearest search na dívokém západě.
        """
        #č cdist vysloveně chce 2D pola, viděl jsem to i v kódě.
        #č Vrací sloupcovou matici. Co kdyby s F pořadí by to jelo rychlejc?
        #d1 = np.empty((len(nodes), 1), dtype=float, order=order)
        #cdist(nodes, [center_1], 'sqeuclidean', out=d1)
        d2 = np.empty((len(nodes_1), 1), dtype=float, order=order)
        cdist(nodes_1, [center_2], 'sqeuclidean', out=d2)
        
        mask = np.isfinite(d2)
        
#       #č udělám to takhle i když neumím si představit, 
#       #č jak se můžou objevit NaNs a nekonečna ve d2, když nejsou v d1
#       mask = np.isfinite(d1) & np.isfinite(d2)
        
        n = len(mask[mask])
        d_i = np.empty((n, 1), dtype=float, order=order)
        
        #č pro nás spíše budou kritické  poslední přídané vzorky
        for point in reversed(points_1):
            cdist(nodes_1[mask[:,0]], np.atleast_2d(point), 'sqeuclidean', out=d_i)
            
            mask[mask[:,0]] &= d2[mask[:,0]] <= d_i
            
            n = len(mask[mask])
            if n == 0:
                return False, None, None #mask[:,0], d_2[mask_2]
            d_i.resize((n, 1), refcheck=False)
        
        #č ty špinavé 2D matice zhora jíž nepotřebujem
        #č převedeme (co nejlevnějc) masku na 1D
        mask = mask[:,0]
        d_2, j = tree_2.query(nodes_1[mask], k=1, p=2, workers=self.workers)
        mask_2 = (j == tree_2.idx)
        
        if np.any(mask_2):
            #č hotovo. Vzdálenosti jíž nemusíme kontrolovat.
            #č ve smyčce d2 jsme jíž prohnali.
            mask[mask] = mask_2
            return True, mask, d_2[mask_2]
        else:
            return False, None, None
    
            
            
            
    
        


#оӵ кык точкаен Вороной
# KickTouchCayenneVoronoi

class ContactVoronoi:
    """
    č hlavní myšlenka-pointa třídy je, 
    č že místo integrování buňka po buňce 
    č a pofiderního rozhodování 
    č kdy a jak odhady aktualizovat
    č integrujeme zde všechny možné pary vzorků,
    č kontakt po kontaktu,
    č tj. oblastí ve kterých nejblížšimi jsou pár určitých vzorků.
    č Vyhody:
    č + Získáváme strukturální informace o problému.
    č + Nemusíme integrovat všechno. Na zelený-zelený kontakty kašleme.
    č + V rámci kontaktu entropie je neměnná, potenciál taky.
    č + Důraz integrace je právě na oblastéch zájmu, ne bůhví na čem u buňek.
    č + Nejsou-li body příslyšné kontaktu, tak řekneme, že kontakt neexistuje
    č   a vyhodíme ho z dalšího usuzování. U buňek člověk nikdy neví...
    č 
    č Nevyhody: 
    č - Kvadrát. Kontaktů je nsim-krát víc jak buňek. 
    č Ale i tak počet je konečný. Zvladnutelný. A nezavisí na dimenzi prostoru.
    
    č Další předpoklady, na kterých tuhle třídu stavíme (nevím, zda opravdu platí):
    č 1. existuje-li kontakt mezí vzorky "a" a "b", 
    č    tak aspoň nějaká část musí být obsažena v kouli mezi "a" a "b"
    č 1a. Nepatří-li střed usečky mezí vzorky "a" a "b" do kontaktu, 
    č     tak už nikdy ani nebude
    č 1b. I když nepatří střed usečky mezí vzorky "a" a "b" do kontaktu, 
    č     kontakt pořad může existovat.
    č 1c. Jde-li kontakt do nekonečna, pořad může (i když nemusí) 
    č     existovat část, která patří do (QHull) konvexní obálky.
    č 2. Při přidani vzorku "d" musíme aktualizovat všechny vazby všech 
    č    sousedících s tím d-čkem vzorků. To je právě proto, že oblast kontaktu
    č    jsou DVA sousedících vzorků. I když vzorek "d" nemá kontakt s "c",
    č    pouze s "a" a "b", pořád můžou existovat bodíky "ac" a "bc", pro které
    č    "c" a "d" stanou nejbližší.
    č 3. Už jsme opustili svět napočítaných stěn, 
    č    kde i konvexní obálku jsme vždycky sestavovali v prostoru triangulace.
    č    Konvexní obálka se může sestavovat v jiném prostoru a tak úplně
    č    každý bodík (i na usečce mezi dvěma vzorky) se může objevit venku.
    č 4a. Aktualizace. Jsou-li změny v kontaktní oblasti, tak jsou vyvolany
    č     přídáním nových vzorků (jasný) a vyfiltrováné vzorky je budou mít v ii.
    č 4b. Je-li oblast kontaktu ovlivněna přídanými vzorky, tak u vyfiltrovaných
    č     bodíků se nutné změní ii2: z předchozího ii2 na ii1, 
    č     nebo rovnou na index nového vzorku. Tj. stačí kontrolovat jenom ii2.
    č 4c. Aktualizaci lze provadět na redukovaném stromu 2 + nové vzorky 
    č
    č Neplatí:
    č 2. (Při přidani vzorku "c"). Jakože neexistují-li kontakty mezi vzorky "c" a "a",
    č    a mezi "c" a "b", tak přídaní "c" nemůže kontakt mezi "a" a "b" ovlivnit.
    
    
    č Poznámky k adaptivnímu vzorkování:
    č Pro vzorkování alike potřebujeme CoV, 
    č kde važení hustotámi je relativné,
    č násobení dvakrát aweights nezmění výslednou kovarianční matici.
    č Pro rozhodování, která sada nejlepé zachytila "buňku" - 
    č něco jako matici setrvačnosti, u které by násobění "hmotností"
    č konstantou zvětšovalo by celkovou setrvačnost systému.
    č Tušíme, že (obecně) dobře zachycená "buňka" by měla výkazovat
    č největší setrvačnost, ale i taky prostě hmotnost (pravděpodobnostní obsah).
    č Mohli bychom zůstat u CoV pro účely adaptivního vzorkování
    č a volít nejlepší sadu podle podílu pravděpodobnostního obsahu 
    č k rozptylu estimatoru 
    
    
    
    č co máme zadavat jako aweight u np.cov?
    č pdf bodíku? Nebo jejich vahy?
    č Vahy.
    č Rozepíšu zde dětailněji, protože to není na první pohled zřejmný 
    č a myslím si, že i kontrintuitivní
    č 1. Uvaha číslo jedna: když se snažíme odhadnout rozptyl vzorků,
    č    výbraných z normálního rozdělení, tak jich hustotami nepřevažíme
    č 2. Uvaha číslo dva: máme sadu IS a chceme odhadnout rozptyl skutečného
         rozdělení. Chce se tu použit váhy, že ano?
    č 3. Uvaha číslo tří: Jak bychom počítali těžiště a momenty setrvačnosti
    č    rovinného obrazce s odlíšnou tloušťkou t? 
    č    (označme "m" jako mass, v naši "fyzice" nechť bude y*t=m)
         
                sum[y_i * A_i * t_i]     Int y*t dA
         y_c = ---------------------- =  ----------
                    sum(A_i*t_i)          Int t dA

                sum[y_i * m_i]     Int y dm
         y_c = ---------------- =  ----------
                    sum(m_i)        Int  dm
         
         I = sum[(y_i - y_c)**2 * A_i * t_i] = Int (y-y_c)**2 * t dA
         
         I = sum[(y_i - y_c)**2 * m_i] = Int (y-y_c)**2 dm
         
         f_i je jako tloušťka t
         1/h_i je jako integrovační ploška dA
         w = f_i / h_i vahy jsou jako hmotnosti
         Monte Carlo - integrovaní dělením na kusy stejné hmotnosti
         IS - kusy mají odlíšnou hmotnost
         
                  
    č base_r dává poloměr, do kterého/za který spadá jistý podíl bodíků
    '
    r_ball/r_base = sigma
    '
    č Když máme nějakou oblast s poloměrem alespoň r
    č můžeme nastavit směrodatnou odchylku normálního rozdělení tak,
    č aby jisté procento bodíků dopadalo dovnitř
    č (integrujeme-li obyčejnou Voroneho buňku, tak r = mindist / 2)
    č Co ale máme dělat, když máme výběrovou směrodatnou odchylku 
    č bodíků z cenzurovanného rozdělení? Survival bias.
    č Můžu spočítat r_ball, ten nebude korrettní, protože vzorky
    č nebyly z normálního rozdělení, ale z cenzurovanného
    č A ani ten r_ball nepotřebuji. Chcu nastavit vzorkovací sigmu.
    č Co jako? Mám dělat výzkum? Počítat třetí a čtverté výběrové momenty?
    č Před tím se dělalo tohle: sigmas = sigmy / base_r
    č Což, pokud rozumím, ve 2D ještě víc změnšovalo směrodatné odchylky
    '
    č Mám výberovou "sigmu" (std) z cenzurovanného rozdělení, 
    č podle mé osy má odříznuté chvosty. 
    č Odříznuté chvosty podel jinejch os mě nezajimají
    č std * r_base(ndim) = r_ball(ndim)
    č sigma * r_base(ndim-1) = r_ball(ndim-1)
    č Nabízím opravu: sigma = std * r_base(ndim) / r_base(ndim-1)
    č Ve výsokých dimenzích rozdíl je minimální
    č Ale kdo tuší, co a jak tam funguje a má fungovat?
          
      
    č Score počítáme jako pravděpodobnostní obsah buňky dělený
    č směrodatnou odchylkou odhadu (3.) Není to ale jediná možnost
    č 1. sum((w_i - w_mean)**2) / n         To je rozptyl w
    č 2. sum((w_i - w_mean)**2) / n**2      To je rozptyl odhadu w_mean
    č 3. sqrt(sum((w_i - w_mean)**2)) / n   Směrodatná odchylka odhadu w_mean
    """
    def __init__(self, sample_box, hull, model_space='G', \
                ns=1000, p_base=0.5, auto_update=True, workers=1,\
                on_add_mixed=None, on_update_mixed=None, on_delete_mixed=None):
        self.sample_box = sample_box
        self.hull = hull
        self.model_space = model_space
        self.ns = ns
        
        self.auto_update = auto_update
        self.workers = workers
        
        if on_add_mixed is not None:
            self.on_add_mixed = on_add_mixed
        if on_update_mixed is not None:
            self.on_update_mixed = on_update_mixed
        if on_delete_mixed is not None:
            self.on_delete_mixed = on_delete_mixed
        
        #č chcu, aby behem dalších iterací pulka (p_base) tečiček dopadala do buňky
        self.base_r = sball.get_Radius_ps(sample_box.nvar, p_base)
        #č pro funkci IS_stat.sample_like(), víz. diskuse v poznamkách
        self.d = (sball.get_Radius_ps(sample_box.nvar - 1, p_base) / self.base_r)**2
        self.ndim = sample_box.nvar
        
        self._nsim = 0
        self._enabled = False # if nsim < 2 and not failsi
        self.nodes = WardrobeDict()
        # checklist
        #č defaultdict zajistí, že na nás dycky čeka seznam, 
        #č do kterého můžeme přidávat indexy bodíků
        self.couples = collections.defaultdict(list)
        self.mixed_couples = {}
        self.red_couples = {}
        #č uvnitř třídy ještě můžeme ordnung dodržovat
        self._indices_to_update = set() # set of couples to update
        self._valid_outsides = set() # node indexes
        
        
        #č já chcu, aby třída byla blbuvzdorná
        #č aby šlo ji vytvořit na prazdné skřiňce 
        #č aby neotravovala chybáma
        #self._update()
        
    
    # dump methods
    # callbacks are set up at __init__ if provided
    # otherwise do nothing
    @staticmethod
    def on_add_mixed(nodes): pass
    
    @staticmethod
    def on_update_mixed(idx): pass
    
    @staticmethod
    def on_delete_mixed(idx): pass
    
    
    """
    ## checklist
    self.couples # dict of active contacts {couple_indices: list of node idxs}
    self.mixed_couples = {}  ##č pár slovníků reprezentativních sad vzorků 
    self.red_couples = {}    ## {couple_indices: nodes}
    self._add_indices_to_update(j) 
    self._valid_outsides = set() #č zabyvá se tím bezprostředně integrovačka
    
    
#    Nodes pipeline:
#    0. Sampling: generate coordinates
#    1. _store_masked(): Filter out, create CandyNodes 
#       with d2 and (optionally) imask assigned
#    2. assign weights (w) such as sum(w)=1 over entire domain
#    3. score(): assign so called "score"
    """
        
    
    #č funkce se nemá dělat toho víc,
    #č pokud by ji někdo opakovaně volal pořad dokola
    def _update(self):
        if self.auto_update:
            if self.basic_checks():
                ##č můžeme udělat obraceně - 
                ##č je-li to nutné, nechť si uživatel třídy 
                ##č zajístí správnost autsajdů
                ##č a teprvé poté volá update()
                #č Ale nebudeme. Po aktualizaci něco i zmízí,
                #č tak si ušetříme kus práce
                self.update_contacts()
                self.invalidate_outside()
        
    
    def basic_checks(self):
        if self._enabled:
            return True
        elif self.sample_box.nsim < 2:
            return False
        elif not np.any(self.sample_box.failsi):
            return False
        else:
            self._enabled = True
            return True
            
    def invalidate_outside(self):
        self._valid_outsides.clear()
        
    #č funkce se nemá dělat toho víc,
    #č pokud by ji někdo opakovaně volal pořad dokola
    def update_contacts(self):
        #č já vím, že sample box pokážde failsi přepočítavá
        self.failsi = failsi = self.sample_box.failsi 
        self.points = points = getattr(self.sample_box, self.model_space)
        self.PDF = self.sample_box.pdf(self.model_space)
        
        assert len(self._indices_to_update) == 0
        
        nis = self.ns
        workers = self.workers
        
        #č zde postupně v cyklu prochazíme všemi (novými) páry kontaktů
        #č a omezujeme se pouse nejbližšími vzorky
        #č disjunktnost je pořad zajištěna
        #č a môžeme všechny nasbírané pravděpodobnosti jednoduše sčítat
        # good old event ids...
        # -1 = 'outside', 0=success, 1=failure, 2=mix
        for i in range(self._nsim, self.sample_box.nsim): 
            if failsi[i]: #č první je červený
                for j in range(i):
                    tp = TwoPoints(points, (i, j), workers=workers)
                    if failsi[j]:
                        #č červený kontakt
                        # -1 = 'outside', 0=success, 1=failure, 2=mix
                        self.onboard_couple(tp, event_id=1, nis=nis)
                    else:
                        #č žlutý kontakt
                        # -1 = 'outside', 0=success, 1=failure, 2=mix
                        self.onboard_couple(tp, event_id=2, nis=nis)
            
            else: #č první je zelený
                for j in range(i):
                    if failsi[j]:
                        #č žlutý kontakt
                        # -1 = 'outside', 0=success, 1=failure, 2=mix
                        tp = TwoPoints(points, (i, j), workers=workers)
                        self.onboard_couple(tp, event_id=2, nis=nis)
                    
                    #else: #č jinak nič
                        #оӵ Вож. Кулэ ӧвӧл
        
        
        #č project páry na update
        for couple_indices in self._indices_to_update:
            #č nepodporuje slovník množinové operace
            self.update_couple(couple_indices)
#            if couple_indices in self.couples:
#                #č i kdyby někdo (nelegálně!) přímo volal update_couple()
#                #č žádná katastrofa se dít nebude
#                #č defaultdict vytvoří prazdný seznam,
#                #č ale bez bodíků se aktualizace brzy skončí :)
#                self.update_couple(couple_indices)
        self._indices_to_update.clear()
        self._nsim = nsim
    
    
    def _add_indices_to_update(self, j):
        #č i-té indexy jsou ty čerstvé, přes ně iterujeme
        #č j-té - ty bežné, protí ním rozhodujeme
        if j < self._nsim:
            for k in range(j):
                self._indices_to_update.add((j, k))
            for k in range(j+1, self._nsim):
                self._indices_to_update.add((k, j))
    
    
    def _recommend_to_integration(self, nodes):
        # -1 = 'outside', 0=success, 1=failure, 2=mix
        if nodes.event_id == 2:
            self.mixed_couples[nodes.couple] = nodes
        else:
            self.red_couples[nodes.couple] = nodes
    
        
                
                
                
        
    
    def update_couple(self, couple_indices):
        #č při aktualizaci páry kontrolujeme, 
        #č zda nejsou změny u sady, doporučenou k integraci
        
        #č co všechno se tu může dít?
        #č -1. pár není, neboť smyčka tam přídavá všechny možné kombinace.
        if couple_indices not in self.couples:
            assert couple_indices not in self.mixed_couples
            assert couple_indices not in self.red_couples
            return -1
        idx_list = self.couples[couple_indices]
        
        #č -2. seznam může být prazdný i když by neměl
        if not idx_list:
            self.couples.pop(couple_indices)
            print("ContactVoronoi: empty list found for ", couple_indices)
            print(self.mixed_couples.pop(couple_indices, None))
            print(self.red_couples.pop(couple_indices, None))
            return -2
        
        #č 3. Pokud je pár červený, stačí zkontrolovat jen reprezentativní sadu
        if couple_indices in self.red_couples:
            idx = self.red_couples[couple_indices].idx
            status, nodes = self._check_nodes(idx)
            if status == 1: #č nic se nezměnilo
                return 3
            #č idx už jsme zkontrolovali. 
            idx_list.remove(idx)
            #č Dále seznam proženeme smyčkou _walk_through_couple_nodes()
            #č (i kdyby se tam poslal prazdný idx_list - nic se neděje)
            #č pokud bodíky se jen maliňko změnily (status 2 z _check_nodes), 
            #č tak budou použity jako best_nodes a dostanou se zpatky do seznamu.
            #č Propadla-li sada kompletně (status 3), tak nodes budou None
        else:
            nodes = None
        
        #č 4. (u smíšených) může být potřeba zkontorlovat všechy sady bodíků
        #č kvůli garancim skříňce
        new_idxs, best_nodes = self._walk_through_couple_nodes(idx_list, nodes)
        if not new_idxs:
            self._invalidate_couple(couple_indices)
            return -5
        else:
            self.couples[couple_indices] = new_idxs
            self._recommend_to_integration(best_nodes)
            return 4
        
        
        
    def _walk_through_couple_nodes(self, idx_list, best_nodes=None):
        new_idxs = []
        #č i kdyby se poslal prazdný idx_list - nic se neděje
        if best_nodes is not None:
            new_idxs.append(best_nodes.idx)
            best_score = best_nodes.score
        else:
            best_score = -np.inf
            
        
        sampling_needed = False
        
        for idx in idx_list:
            status, nodes = self._check_nodes(idx)
            if status != 1: #č 1 == nic se nezměnilo
                sampling_needed = True
            if status == 3: #č Padla celá sada bodů.
                continue
                
            new_idxs.append(idx)
            if nodes.score > best_score:
                best_nodes = nodes
                best_score = nodes.score
                
        if (best_nodes is not None) and sampling_needed:
            #č tp-čko se musí znovu vygenerovat na aktuálních vzorcích
            #č nepůjde je ukladat
            tp = TwoPoints(self.points, best_nodes.couple, workers=self.workers)
            nodes = self.sample_alike(tp, best_nodes, self.ns)
            if nodes is not None:
                new_idxs.append(nodes.idx)
                if nodes.score > best_score:
                    best_nodes = nodes
        
        return new_idxs, best_nodes
        
        
    def _check_nodes(self, idx):
        "returns status, masked_nodes"
        #č co všechno se tu může dít?
        #č 1. nic se nezměnilo, všechny bodíky pořad patří k páru
        #č 2. Pozor, změna! Některé bodíky odpadly
        #č 3. Padla celá sada bodů.
        
        #č bodíky musí mít konečné souřadnice - ony prošly KD stromem
        #č vzorky - tím více
        nodes = self.nodes[idx]
        nodes_model = getattr(nodes, self.model_space)
        d3 = np.min(cdist(nodes_model, self.points[self._nsim:]), axis=1)
        mask = nodes.d2 <= d3
        
        if not np.any(mask):
            # -1 = 'outside', 0=success, 1=failure, 2=mix
            if nodes.event_id == 2:
                #č dáme zákazníkovi vědět před tím, než bodíky vyhodíme
                self.on_delete_mixed(idx)
            #č invalidace sady
            self.nodes.pop(idx)
            return 3, None
        elif np.all(mask):
            return 1, nodes
        else:
            del nodes.p_inside
            del nodes.p_fv
            del nodes.p_fw
            masked_nodes = nodes[mask]
            # update score
            self.score(masked_nodes)
            self.nodes[idx] = masked_nodes
            #č nejdřív update, teprve poté informujeme kontrahenta
            if nodes.event_id == 2:
                self.on_update_mixed(idx)
            return 2, masked_nodes
        
        ## checklist
        #self.couples[tp.couple_indices].append(nodes.idx)
        
        
    def _invalidate_couple(self, couple_indices):
        self.couples.pop(couple_indices)
        self.mixed_couples.pop(couple_indices, None)
        self.red_couples.pop(couple_indices, None)
        
    def explore_couple(self, couple_indices, nis):
        """
        Method is dedicated for the external usage.
        If someone thinks CV missed out some pair,
        it could say about and try to fix the thing.
        """
        i, j = max(couple_indices), min(couple_indices)
        couple_indices = (i, j)
        failsi = self.sample_box.failsi 
        if failsi[i]: #č první je červený
            if failsi[j]:
                #č červený kontakt
                # -1 = 'outside', 0=success, 1=failure, 2=mix
                event_id = 1
            else:
                #č žlutý kontakt
                # -1 = 'outside', 0=success, 1=failure, 2=mix
                event_id = 2
        
        else: #č první je zelený
            if failsi[j]:
                #č žlutý kontakt
                # -1 = 'outside', 0=success, 1=failure, 2=mix
                event_id = 2
            else:
                return 
                #оӵ Вож. Кулэ ӧвӧл
        
        tp = TwoPoints(self.points, couple_indices, workers=self.workers)
        #č pokud pár známe, jen přídáme další sadu bodů
        if couple_indices in self.couples:
            if event_id == 2:
                best_nodes = self.mixed_couples[couple_indices]
            else:
                best_nodes = self.red_couples[couple_indices]
            nodes = self.sample_alike(tp, best_nodes, nis)
            if nodes is not None:
                self.couples[couple_indices].append(nodes.idx)
                if nodes.score > best_nodes.score:
                    self._recommend_to_integration(nodes)
            
            return nodes
            
        #č pár nám není znám. Ještě jednou pokusíme nasypat body
        nodes = self.onboard_couple(tp, event_id=event_id, nis=nis)
        
        #č project páry na update
        for couple_indices in self._indices_to_update:
            #č nepodporuje slovník množinové operace
            self.update_couple(couple_indices)
        self._indices_to_update.clear()
        
        return nodes
        
        
        
        
        
    def onboard_couple(self, tp, event_id, nis):
        #č (i, j)? poprvé ta čísla vidíme
        i, j = couple_indices = tp.couple_indices
        
        midpoint = tp.half_point
        #č Nejdřív - zda je přímy kontakt, prostě na usečce
        #TData(X=nodes[gmask], imask, dd)
        nodes = self._store_masked(tp, midpoint, np.atleast_1d(np.inf), event_id)
        if nodes is not None:
            #č kontakt existuje, dáme vědět aktualizovačce 
            ##č (snad jediné místo kde tuhle funkci voláme)
            self._add_indices_to_update(i) #č může nás volat i explore_couple()
            self._add_indices_to_update(j) 
            self.couples[couple_indices].append(nodes.idx)
            
            
            ##nodes.w = 0
            ##nodes.p_couple = 0
            #č nsim score
            #č 0   -inf    #č myšleno hypoteticky
            #č 1   0       #č jednomu bodíku bych nedůveroval a nebral bych největší p
            #č 2   ~p_couple
            #č chcu, aby score byl měnší jak u připadného skutečného bodíku.
            nodes.score = -1 #č není špatný score
            
            #č chcu zjednodušit logiku. 
            #č Pokud máme pouze jeden bodík, tak snad i bude nejlepším?
            #č Nechť veškeré couples v třídě budou konzistentní.
            #č dočasně nejlepší tenhlensten, tak ho doporučíme k integraci
            self._recommend_to_integration(nodes)
        
        
        #č a teď deme vzorkovat
        #vec = couple_nodes[0] - couple_nodes[1]
        vec = tp.normal_vector
        r = np.sqrt(np.inner(vec, vec)) / 2
        
        # initially we'll perform IS from multivariate Gaussian distribution 
        # with center at mid node (i. e. in beetween of two points)
        # and single standard deviation (let's say "ball" sampling)
        #č r-ko dělíme base_r'kem k získání sigmy.
        sampling_plan_N, h_pdf = IS_stat.get_norm_plan(nis, self.ndim, \
                                mean=midpoint, 
                                std=r/self.base_r, design=None)
        
        nodes = self._store_masked(tp, sampling_plan_N, h_pdf, event_id)
        if nodes is None:
            return None
        
        #č kontakt existuje, dáme vědět aktualizovačce 
        ##č (druhé místo kde tuhle funkci voláme)
        self._add_indices_to_update(i) #č může nás volat i explore_couple()
        self._add_indices_to_update(j) 
        self.couples[couple_indices].append(nodes.idx)
            
        #č jdeme do adaptivního IS vzorkování
        #č zde jenom vzorkujeme; 
        #č integrování, vyhodnocování je jinde a později!
        best_score = -np.inf
        while nodes.score > best_score:
            best_nodes = nodes
            best_score = nodes.score
            nodes = self.sample_alike(tp, nodes, nis)
            self.couples[couple_indices].append(nodes.idx)
            
        
        #č doporučíme k integraci
        #č Má cenu integrovat pouze nejreprezentativnější sadu bodů.
        #č Špatné sady je velmi obtižné správně započítavat
        #č aby nezhoršovaly výsledek.
        #č Možná TrueIS by si mohl s tím poradit, ale 
        #č zde je to totálná zbytečnost
        # -1 = 'outside', 0=success, 1=failure, 2=mix
        self._recommend_to_integration(best_nodes)
        return best_nodes
            
        
        
    def score(self, nodes):
        #č p_couple není finální pravděpodobnost
        #č bodíky ještě musejí projít konvexní obálkou
        nodes.p_couple = np.sum(nodes.w)
        #č nsim score
        #č 0   -inf    #č myšleno hypoteticky
        #č 1   0       #č jednomu bodíku bych nedůveroval a nebral bych největší p
        #č 2   ~p_couple
        nodes.score = nodes.p_couple * np.log(len(nodes))
        
        
    def sample_alike(self, tp, nodes, nis):
        """
        č zde jenom vzorkujeme; 
        č integrování, vyhodnocování je jinde a později!
        returns: node_idx, score
        """
        assert len(nodes) > 0
        
        nodes_model = getattr(nodes, self.model_space)
        
        
        if len(nodes) > 1:
            #č potřebujeme vahy, pokud bodíků víc jak jeden. Takže v cajku.
            sampling_plan, h_pdf = IS_stat.sample_alike(nodes_model, \
                                            weights=nodes.w, nis=nis, d=self.d)
            
        else:
            #č máme jeden bodík. To znaméná, že kontakt existuje
            #č a zákazník hodla provést vzorkování.
            #č Pro tento vzácný případ naše společnost nabízí řešení - 
            #č zapojít informace o těch dvou vzorkách, ke kterým patří.
            #č Na ty dva vzorky se nemůžeme spoléhat z hlediska směrových 
            #č preferencí, použijme je jen jako zdroj jakési 
            #č charakteristické délky. Těžiště necháme v tamtamtom bodíku.
            
            #č d2 je vždy přítomný. Zajistěno v _store_masked()
            #č Specifikem CandyNodes je, že d2 pro jeden bodík může vrátit
            #č jak skalarní hodnotu, tak i pole s jediným prvkem
            #č numpy si poradí s obojí
            r = nodes.d2
            
            # we'll perform IS from multivariate Gaussian distribution 
            # centered at the isolated node 
            # and some standard deviation
            #č r-ko dělíme base_r'kem k získání sigmy.
            sampling_plan, h_pdf = IS_stat.get_norm_plan(nis, self.ndim,
                                    mean=nodes_model[0], 
                                    std=r/self.base_r, design=None)
                                
                                
        return self._store_masked(tp, sampling_plan, h_pdf, nodes.event_id)
        
        
        
    def _store_masked(self, tp, nodes_model, h_pdf, event_id):
        """ returns nodes, mask, tdata
        
        č logika celé třídy je, že máme-li příslušné kontaktu bodíky,
        č tak stojí za to je uložit. 
        č Proto metod maskuje a je-li co ukladat tak i rovnou uloži 
        č a vratí jejich index (jinak vratí nulu).
        č To ale vyžaduje trochu větší pozornost - 
        č bodíky pak někdo má odebrat a invalidovat.
        č Proto i podtržitko v názvu
        """
        #TData(X=nodes[gmask], imask, dd)
        status, mask, tdata = tp.query(nodes_model)
        
        if not status:
            return None
            
            
        #č přídat, zavolat kólbek
        f = self.sample_box.f_model
        #č tady je to super, ťažké datové struktury f-modelu
        #č vytvaříme na jíž vyfiltrovaných datéch.
        nodes = f.new_sample(tdata.X, self.model_space)
        couple_stats = {'event_id': event_id, 'couple': tp.couple_indices}
        nodes = CandyNodes(nodes, couple_stats, d2=tdata.dd)
        idx = self.nodes.add(nodes)
        nodes.idx = idx
        
        w = nodes.pdf(self.model_space) / h_pdf[mask] / len(mask)
        #č Filtrace stromem (která pořad je) zaručuje, 
        #č že bodíky (přenejmenším na vstupu f_modelu) 
        #č mají konečné souřadnice bez nan a nekonečno.
        #č To ale nic neříká o hustotách 
        nodes.w = w * np.isfinite(w)
        #č beztak skorem v této třídě projde každá sada vzorků 
        self.score(nodes)
        
        #č červené kontakty prostě rovnou integrujeme
        #č takže netřeba pro ně ukladat zbytečná data
        # -1 = 'outside', 0=success, 1=failure, 2=mix
        if event_id == 2:
            nodes.imask = tdata.imask
            self.on_add_mixed(nodes)
        
        
        ## checklist
        #č _store_masked dělá na urovní nodes
        #č zbytek nechť dělá kód vejš
        #č michá se to u kontrol párů z minule
        #self.couples[tp.couple_indices].append(nodes.idx) 
        #self.mixed_couples #č v této fázi nevíme,
        #self.red_couples   #č zda je sada ta nejlepší
        #self._add_indices_to_update(j) #č vždyť já nevím, jestli se jedná o aktualizaci
        
        return nodes
        
        
        
    #č tahle funkce může být volána i skřiňkou
    def estimate_mixed(self, nodes):
        "assigns d1, fv, fw"
        nodes_model = getattr(nodes, self.model_space)
        i, j = nodes.couple
        imask = nodes.imask
        d2 = nodes.d2
        
        di1 = cdist(nodes_model[imask], np.atleast_2d(self.points[i])).reshape(-1)
        dj1 = cdist(nodes_model[~imask], np.atleast_2d(self.points[j])).reshape(-1)
        
        d1 = np.empty(len(imask))
        d1[imask] = di1
        d1[~imask] = dj1
        #č skříňka bude chtit d1
        nodes.d1 = d1
        
        Pdf_i = self.PDF[i]
        Pdf_j = self.PDF[j]
        
        if self.failsi[i]:
            df[imask] = di1
            df[~imask] = d2[~imask]
            dpdf = df * Pdf_i
        else:
            df[imask] = d2[imask]
            df[~imask] = dj1
            dpdf = df * Pdf_j
        
        sumpdf = np.empty(len(imask))
        sumpdf[imask] = di1 * Pdf_i + d2[imask] * Pdf_j
        sumpdf[~imask] = dj1 * Pdf_j + d2[~imask] * Pdf_i
        
        w = nodes.w
        
        nodes.fv = w * df / (d1 + d2)
        nodes.fw = w * dpdf / sumpdf
        
        
        
        
        
    def get_pf_estimation(self):
        #č zkusme představit, 
        #č že někdo bude volat tuhle funkci pořad dokola,
        #č aniž by se přídaly nové vzorky.
        self._update()
        failure, mixed, pfv, pfw = 0
        
        valid_insides = self._valid_outsides
        is_inside = self.hull.is_inside
        
        for nodes in self.red_couples.values():
            if nodes.idx not in valid_insides:
                nodes.inside = mask = is_inside(nodes)
                valid_insides.add(nodes.idx)
                nodes.p_inside = p_inside = np.sum(nodes.w[mask])
            else:    #č kód třídy musí zajistit konzistentnost p_inside, 
                try: #č mazajic ji kdyby něco 
                    p_inside = nodes.p_inside
                except AttributeError:
                    nodes.p_inside = p_inside = np.sum(nodes.w[nodes.inside])
                    
            failure += p_inside
            pfv += p_inside
            pfw += p_inside
        
        
        for nodes in self.mixed_couples.values():
            if not hasattr(nodes, 'fw'):
                self.estimate_mixed(nodes)
                
            if nodes.idx not in valid_insides:
                nodes.inside = mask = is_inside(nodes)
                valid_insides.add(nodes.idx)
                nodes.p_inside = p_inside = np.sum(nodes.w[mask])
                nodes.p_fv = p_fv = np.sum(nodes.fv[mask])
                nodes.p_fw = p_fw = np.sum(nodes.fw[mask])
            else:    #č kód třídy musí zajistit konzistentnost peček, 
                try: #č mazajic je kdyby něco 
                    p_inside = nodes.p_inside
                    p_fv = nodes.p_fv
                    p_fw = nodes.p_fw
                except AttributeError:
                    mask = nodes.inside
                    nodes.p_inside = p_inside = np.sum(nodes.w[mask])
                    nodes.p_fv = p_fv = np.sum(nodes.fv[mask])
                    nodes.p_fw = p_fw = np.sum(nodes.fw[mask])
            
            mixed += p_inside
            pfv += p_fv
            pfw += p_fw
        
        return failure, mixed, pfv, pfw
        
        
