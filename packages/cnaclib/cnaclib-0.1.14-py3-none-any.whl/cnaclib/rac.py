# Importer les modules

from datetime import datetime
from dateutil import relativedelta
import pandas as pd

##########################################################################################################################################
#                                                       REGIME ASSURANCE CHOMAGE : SIMULATEUR
##########################################################################################################################################

class RAC:
    '''
    REGIME ASSURANCE CHOMAGE : SIMULATEUR

    Cette Class en python permet de réaliser des simulations pour le calculs des différents éléments liés au régime d'assurance chômage.
    Elle permet de :
    - Vérifier la condition d'admission relative à l'experience professionnelle;
    - Calculer la durée de prise en charge (DPC);
    - Calculer le montant de la Contribution d'Ouverture de Droits;
    - Récupérer le montant du SNMG en fonction de la date;
    - Calculer les montants d'indemnités en fonction des 04 périodes;
    - Calculer les montants de cotisations de sécurité sociale (part patronale & part salariale );

    Parameters
    ----------

    DateRecrutement : date, 
        C'est de la date de recrutement du salarié chez le dernier employeur.
        Elle doit être exprimé selon le format : dd/mm/yyyy.


    DateCompression : date,
        C'est la de compression du salarié chez le dernier employeur.
        Elle doit être exprimé selon le format : dd/mm/yyyy.

    
    SMM : float,
        C'est le Salaire Mensuel Moyen des 12 derniers mois.
        Il doit être exprimé en DA et concerne la moyenne des salaires soumis à cotisation de sécurité sociale des 12 derniers mois.

    
    Attributes
    ----------

    annee : int,
        C'est la durée d'experience en année;

    mois : int,
        C'est la durée d'experience en mois lorsque la période est inferieure à une année;
    
    jours : int,
        C'est la durée d'experience en jours lorsque la période est inferieure à un mois;

    message : string,
        C'est le message affiché aprés vérification de la condition d'admission relative à la durée d'experience professionnelle.
        Il y a 03 types de messages selon les paramétres annee, mois & jours.
    
    DateAdmission : date,
        C'est une date calculée pour les besoins de la simulation.
        Elle représente la date d'admission (thérique) au régime d'assurance chomage. 
        Elle permet de confectionner le tableau des indemnités selon les 04 période;
        Elle permet aussi de vérifier la condition d'âge pour le versement au régime de la retraite anticipée.
    
    DPC : int,
        C'est la durée (calculée) de prise en charge. 
        Elle est exprimée en mois et représente le nombre de mois qui seront payés par la CNAC en termes d'indemnités.
        Elle est comprise entre 12 et 36 mois.
    
    CODMensuel : float,
        C'est le montant calculée de la contribution forfétaire d'ouverture de droits mensuelle.

    CODTotale : float,
        C'est le montant calculée de la contribution forfétaire d'ouverture de droits totale.
        C'est le montant à la charge de l'employeur pour l'ouverture des droits de son ou ses salariés.
    
    MoisPeriode : int,
        C'est le nombre de mois pour chaque période sachant qu'il y a 04 périodes.

    DateMois : date,
        C'est la date relative à chaque indemnité figurant sur le tableau des indemnités.
        Donc pour chaque MoisPeriode il y a une DateMois.

    IndemniteBrut : float,
        C'est le montant de l'indemnité brute pour chaque DateMois igurant sur le tableau des indemnités.
        
    IndemniteNet : float,
        C'est le montant de l'indemnité nette pour chaque DateMois igurant sur le tableau des indemnités.
        Il est égal à IndemniteBrut - PartSalariale.

    PartPatronale : float,
        C'est le montant de la cotisation de sécurié sociale à la charge de la CNAC.

    SalRef : float,
        C'est la salaire de référence. Il est égal au (SMM + SNMG) /2.
        Il permet de calculer les montants des indemnités. 
    
    FDD : date;
        C'est la date (calculée) de fin de droits.
        Elle représente le dernier mois de paiement de l'indemnité.
    
    '''

    def __init__(self, DateRecrutement, DateCompression, SMM):
        self.DateRecrutement = DateRecrutement
        self.DateCompression = DateCompression
        self.SMM = SMM

    def durexp(self):
        d1 = datetime.strptime(self.DateCompression, "%d/%m/%Y")
        d2 = datetime.strptime(self.DateRecrutement, "%d/%m/%Y")
        delta = relativedelta.relativedelta(d1, d2)
        self.annee = delta.years
        self.mois = delta.months
        self.jours = delta.days
        return self.annee, self.mois, self.jours
    
    def admission(self):
        RAC.durexp(self)
               
        if self.annee >= 3:
            self.message = "Si vous remplisez les conditions préalablement citées et selon votre expérience professionnelle calculée, vous pouvez bénéficier du Régime d'Assurance Chômage. Pour les besoins de la sumulation nous allons proposer une date d'admission en fonction des dates que vous avez fournies."
        elif self.annee > 0 and self.annee < 3 :  
            self.message = "Selon votre expérience calculée, nous devons vérifier si vous avcez cumulé 03 ans de cotisation à la SS"
        elif self.annee < 1 and self.mois >=6:
            self.message = "Selon votre expérience calculée, nous devons vérifier si vous avcez cumulé 03 ans de cotisation à la SS"
        else:
            self.message = "Selon votre expérience calculée, vous ne pouvez pas bénéficier du RAC "
        self.DateAdmission = datetime.strptime(self.DateCompression, "%d/%m/%Y") + relativedelta.relativedelta(months=1)
        return self.message, self.DateAdmission

    
    def DPC(self):
        RAC.admission(self)
        
        if self.message == "Selon votre expérience calculée, vous ne pouvez pas bénéficier du RAC ":
            self.message2 = "Selon votre expérience calculée, vous ne pouvez pas bénéficier du RAC"
                    
        else:
            if self.annee < 3 :
                self.DPC= 12
            elif  self.annee >= 3 :
                self.DPC= self.annee * 2
                if self.mois == 0 and self.jours == 0:
                    self.DPC += 0
                elif self.mois == 0 and self.jours > 0:
                    self.DPC  += 1
                elif self.mois == 6 and self.jours == 0:
                    self.DPC += 1
                elif self.mois == 6 and self.jours > 0:
                    self.DPC += 2
                elif self.mois > 6:
                    self.DPC += 2
                elif self.mois < 6:
                    self.DPC += 1
                        
            if self.DPC < 12:
                self.DPC = 12
            elif self.DPC > 36:
                self.DPC = 36
        
            return self.DPC
    
    def COD(self):
        RAC.DPC(self)
        
        if self.message == "Selon votre expérience calculée, vous ne pouvez pas bénéficier du RAC ":
            print("Selon votre expérience calculée, vous ne pouvez pas bénéficier du RAC")
            exit()    
        
        else:
            if self.annee < 3 :
                self.CODMensuel = 0
                self.CODTotale = 0
                
            elif  self.annee >= 3 :
                self.CODMensuel =  0.8 * self.SMM
                self.CODTotale = (self.annee - 3) * self.CODMensuel
                if self.mois == 0 and self.jours == 0:
                    self.CODTotale += 0
                elif self.mois == 0 and self.jours > 0:
                    self.CODTotale +=  0.4 * self.SMM
                elif self.mois == 6 and self.jours == 0:
                    self.CODTotale += 0.4 * self.SMM
                elif self.mois == 6 and self.jours > 0:
                    self.CODTotale += 0.8 * self.SMM
                elif self.mois > 6:
                    self.CODTotale +=  0.8 * self.SMM
                elif self.mois < 6:
                    self.CODTotale += 0.4 * self.SMM            
            return self.CODMensuel, self.CODTotale

    def SNMG(self, Date):
        global SNMG
        if Date >= datetime.strptime('01/01/1990', "%d/%m/%Y") and  Date <= datetime.strptime('31/12/1990', "%d/%m/%Y") :
            SNMG = 1000
        elif  Date >= datetime.strptime('01/01/1991', "%d/%m/%Y") and Date <= datetime.strptime('30/06/1991', "%d/%m/%Y"):
            SNMG = 1800
        elif  Date >= datetime.strptime('01/07/1991', "%d/%m/%Y") and Date <= datetime.strptime('31/03/1992', "%d/%m/%Y"):
            SNMG = 2000
        elif  Date >= datetime.strptime('01/04/1992', "%d/%m/%Y") and Date <= datetime.strptime('30/04/1997', "%d/%m/%Y"):
            SNMG = 2500
        elif  Date >= datetime.strptime('01/05/1997', "%d/%m/%Y") and Date <= datetime.strptime('31/12/1997', "%d/%m/%Y"):
            SNMG = 4800
        elif  Date >= datetime.strptime('01/01/1998', "%d/%m/%Y") and Date <= datetime.strptime('31/08/1998', "%d/%m/%Y"):
            SNMG = 5400
        elif  Date >= datetime.strptime('01/09/1998', "%d/%m/%Y") and Date <= datetime.strptime('31/12/2000', "%d/%m/%Y"):
            SNMG = 6000
        elif  Date >= datetime.strptime('01/01/2001', "%d/%m/%Y") and Date <= datetime.strptime('31/12/2003', "%d/%m/%Y"):
            SNMG = 8000
        elif  Date >= datetime.strptime('01/01/2004', "%d/%m/%Y") and Date <= datetime.strptime('31/12/2006', "%d/%m/%Y"):
            SNMG = 10000
        elif  Date >= datetime.strptime('01/01/2007', "%d/%m/%Y") and Date <= datetime.strptime('31/12/2009', "%d/%m/%Y"):
            SNMG = 12000
        elif  Date >= datetime.strptime('01/01/2010', "%d/%m/%Y") and Date <= datetime.strptime('31/12/2011', "%d/%m/%Y"):
            SNMG = 15000
        elif  Date >= datetime.strptime('01/01/2012', "%d/%m/%Y") and Date <= datetime.strptime('31/05/2020', "%d/%m/%Y"):
            SNMG = 18000
        elif  Date >= datetime.strptime('01/06/2020', "%d/%m/%Y"):
            SNMG = 20000
        return SNMG

    def NumPeriode(self):
        RAC.DPC(self)
        NumMois = [x for x in range(1, (self.DPC) + 1)]
        NumPeriode = []
        z = round((self.DPC)/4)
        for m in NumMois:
            if m <= z : 
                NumPeriode.append("P1")
            elif (m > z and m <= z * 2):
                NumPeriode.append("P2")
            elif (m > z * 2 and m <= z * 3):
                NumPeriode.append("P3")
            else:
                NumPeriode.append("P4")
        self.MoisPeriode = {NumMois[x]: NumPeriode[x] for x in range(len (NumMois))}
        return self.MoisPeriode

    def Indemnite(self): 

        self.SalRef = (RAC.SNMG(self, self.DateAdmission) + float(self.SMM)) / 2
        RAC.NumPeriode(self)
        RAC.SNMG(self, self.DateAdmission)
        
        self.IndemniteBrut = []
        self.IndemniteNet = []
        self.PartPatronale = []
        self.DateMois = []
        
        for m in self.MoisPeriode:
            mois = self.DateAdmission 
            nextmois = mois + relativedelta.relativedelta(months=m)
            self.DateMois.append(nextmois)
        
        for m in self.MoisPeriode:
            if self.MoisPeriode[m] == "P1":
                if 1 * self.SalRef < 0.75 * SNMG:
                    self.IndemniteBrut.append(0.75 * SNMG)
                elif 1 * self.SalRef > 3 * SNMG :
                    self.IndemniteBrut.append(3 * SNMG)
                else : 
                    self.IndemniteBrut.append(1 * self.SalRef)
            
            if self.MoisPeriode[m] == "P2":
                if 0.8 * self.SalRef < 0.75 * SNMG:
                    self.IndemniteBrut.append(0.75 * SNMG)
                elif 0.8 * self.SalRef > 3 * SNMG :
                    self.IndemniteBrut.append(3 * SNMG)
                else : 
                    self.IndemniteBrut.append(0.8 * self.SalRef)

            if self.MoisPeriode[m] == "P3":
                if 0.6 * self.SalRef < 0.75 * SNMG:
                    self.IndemniteBrut.append(0.75 * SNMG)
                elif 0.6 * self.SalRef > 3 * SNMG :
                    self.IndemniteBrut.append(3 * SNMG)
                else : 
                    self.IndemniteBrut.append(0.6 * self.SalRef)
            
            if self.MoisPeriode[m] == "P4":
                if 0.5 * self.SalRef < 0.75 * SNMG:
                    self.IndemniteBrut.append(0.75 * SNMG)
                elif 0.5 * self.SalRef > 3 * SNMG :
                    self.IndemniteBrut.append(3 * SNMG)
                else : 
                    self.IndemniteBrut.append(0.5 * self.SalRef)
        
        for ind in self.IndemniteBrut:
            self.PartPatronale.append(SNMG * 0.15)
            if ind <= SNMG :
                self.IndemniteNet.append(ind)
            else:
                self.IndemniteNet.append(ind - (ind*0.085))
        
        return self.DateMois, self.IndemniteBrut, self.IndemniteNet, self.PartPatronale, self.SalRef

    def tableaux_Indemnites(self):
        RAC.NumPeriode(self)
        RAC.Indemnite(self)
        Periodes=[RAC.NumPeriode(self)[p] for p in RAC.NumPeriode(self)]
        Mois = [p for p in RAC.NumPeriode(self)]
        DateMois=[p for p in RAC.Indemnite(self)[0]]
        IndemniteBrut=[p for p in RAC.Indemnite(self)[1]]
        IndemniteNet = [p for p in RAC.Indemnite(self)[2]]
        PartSalariale = [Brut - Net for Brut, Net in zip(IndemniteBrut, IndemniteNet) ]
        PartPatronale=[p for p in RAC.Indemnite(self)[3]]

        TableauRAC={"Periode":Periodes,
        "Mois":Mois,
        "Date":DateMois,
        "Montant Indemnité Brut":["{:,.2f}".format(p).replace(',', ' ').replace('.', ',') for p in IndemniteBrut],
        "Cotisation SS (PS)":["{:,.2f}".format(p).replace(',', ' ').replace('.', ',') for p in PartSalariale],
        "Montant Indemnité Net":["{:,.2f}".format(p).replace(',', ' ').replace('.', ',') for p in IndemniteNet],
        "Cotisation SS (PP)":["{:,.2f}".format(p).replace(',', ' ').replace('.', ',') for p in PartPatronale]}
        
        df = pd.DataFrame(TableauRAC)
        
        return df

    
    
    
    def Date_FDD(self):
        d = datetime.strptime(self.DateCompression,"%d/%m/%Y") 
        nextd = d + relativedelta.relativedelta(months=1)
        RAC.Indemnite(self) # nextd.strftime("%d/%m/%Y")
        self.FDD  = self.DateMois[-1]
        return self.FDD



class RAC_RRA(RAC):

    '''
    REGIME ASSURANCE CHOMAGE : SIMULATEUR

    Cette Class en python permet de réaliser des simulations pour le calculs des différents éléments liés au régime d'assurance chômage.
    Elle permet de :
    - Vérifier la condition d'admission relative à l'experience professionnelle;
    - Calculer la durée de prise en charge (DPC);
    - Calculer le montant de la Contribution d'Ouverture de Droits;
    - Récupérer le montant du SNMG en fonction de la date;
    - Calculer les montants d'indemnités en fonction des 04 périodes;
    - Calculer les montants de cotisations de sécurité sociale (part patronale & part salariale );

    Parameters
    ----------

    DateRecrutement : date, 
        C'est de la date de recrutement du salarié chez le dernier employeur.
        Elle doit être exprimé selon le format : dd/mm/yyyy.


    DateCompression : date,
        C'est la de compression du salarié chez le dernier employeur.
        Elle doit être exprimé selon le format : dd/mm/yyyy.

    
    SMM : float,
        C'est le Salaire Mensuel Moyen des 12 derniers mois.
        Il doit être exprimé en DA et concerne la moyenne des salaires soumis à cotisation de sécurité sociale des 12 derniers mois.

    genre : string,
        C'est le genre de l'allocataire.
        Il prend deux valeurs : Un Homme / Une Femme
    

    Attributes
    ----------

    annee : int,
        C'est la durée d'experience en année;

    mois : int,
        C'est la durée d'experience en mois lorsque la période est inferieure à une année;
    
    jours : int,
        C'est la durée d'experience en jours lorsque la période est inferieure à un mois;

    message : string,
        C'est le message affiché aprés vérification de la condition d'admission relative à la durée d'experience professionnelle.
        Il y a 03 types de messages selon les paramétres annee, mois & jours.
    
    DateAdmission : date,
        C'est une date calculée pour les besoins de la simulation.
        Elle représente la date d'admission (thérique) au régime d'assurance chomage. 
        Elle permet de confectionner le tableau des indemnités selon les 04 période;
        Elle permet aussi de vérifier la condition d'âge pour le versement au régime de la retraite anticipée.
    
    DPC : int,
        C'est la durée (calculée) de prise en charge. 
        Elle est exprimée en mois et représente le nombre de mois qui seront payés par la CNAC en termes d'indemnités.
        Elle est comprise entre 12 et 36 mois.
    
    CODMensuel : float,
        C'est le montant calculée de la contribution forfétaire d'ouverture de droits mensuelle.

    CODTotale : float,
        C'est le montant calculée de la contribution forfétaire d'ouverture de droits totale.
        C'est le montant à la charge de l'employeur pour l'ouverture des droits de son ou ses salariés.
    
    MoisPeriode : int,
        C'est le nombre de mois pour chaque période sachant qu'il y a 04 périodes.

    DateMois : date,
        C'est la date relative à chaque indemnité figurant sur le tableau des indemnités.
        Donc pour chaque MoisPeriode il y a une DateMois.

    IndemniteBrut : float,
        C'est le montant de l'indemnité brute pour chaque DateMois igurant sur le tableau des indemnités.
        
    IndemniteNet : float,
        C'est le montant de l'indemnité nette pour chaque DateMois igurant sur le tableau des indemnités.
        Il est égal à IndemniteBrut - PartSalariale.

    PartPatronale : float,
        C'est le montant de la cotisation de sécurié sociale à la charge de la CNAC.

    SalRef : float,
        C'est la salaire de référence. Il est égal au (SMM + SNMG) /2.
        Il permet de calculer les montants des indemnités. 
    
    FDD : date;
        C'est la date (calculée) de fin de droits.
        Elle représente le dernier mois de paiement de l'indemnité.
    
    age : int,
        C'est l'age (calculé) de l'allocataire aprés  épuisement de ses droits.
        il permet de vérifier la condition d'age pour le bénéfice de la retraite anticipée.
    
    
    Adm_RRA : date,
        C'est une date (théorique) d'admission au régime de la retraite anticipée.
    
    AnneeAnt : int,
        C'est le nombre d'année d'anticipation.
        il est égal à l'age légal de la retraite anticipée - l'age de l'allocataire aprés  épuisement de ses droits et admis au 
        régime de la retraite anticipée.
    
    CFOD : float,
        C'est le montant de la contribution forfétaire d'ouverture de droits que la CNAC doit verser à la CNR.
    
    AnneeCNR : int,
        C'est le nombre d'année de prise en charge par la CNR dans le cadre du régime de la retraite anticipée.

    MoisCNR : int,
        C'est le nombre de mois par année de prise en charge par la CNR dans le cadre du régime de la retraite anticipée.
    
    PartPatronaleCNR: float,
        C'est le montant de la cotisation de sécurité sociale à verser par la CNAC au profit des allocataires admis au régime 
        de la retraite anticpée  au niveau de la CNR.
    '''


    
    def __init__(self, DateRecrutement, DateCompression, SMM, DateNaissance):
        self.Datenaissance = DateNaissance
        super().__init__(DateRecrutement, DateCompression, SMM)        
    
    def Age_Date_RRA(self):
        
        RAC.Date_FDD(self)
        self.Adm_RRA = self.FDD + relativedelta.relativedelta(months=1)

        d1 = self.Adm_RRA
        d2 = datetime.strptime(self.Datenaissance, "%d/%m/%Y")
        
        delta = relativedelta.relativedelta(d1, d2)
        
        self.age = delta.years
        return  self.age, self.Adm_RRA
    
    def Nombre_Annee_Ant(self, genre):
        RAC_RRA.Age_Date_RRA(self)
        if genre == 'Un Homme':
            self.AnneeAnt = 60 - int(self.age)
        elif genre == 'Une Femme':
            self.AnneeAnt = 55 - int(self.age)
        return self.AnneeAnt

    def CFOD(self):
        RAC.COD(self)
        self.CFOD = (self.CODTotale * 0.3) + (self.AnneeAnt * 0.04 * self.CODTotale)
        return self.CFOD

    def Cotis_CNR(self):
        self.AnneeCNR =[]
        self.MoisCNR = []
        self.PartPatronaleCNR =[]
        for a in range(1, self.AnneeAnt+1):
            for b in range(1,13):
                self.MoisCNR.append(b)
                self.AnneeCNR.append(a)
                self.PartPatronaleCNR.append(round((0.14 * SNMG),2))          
        return self.AnneeCNR, self.MoisCNR, self.PartPatronaleCNR









