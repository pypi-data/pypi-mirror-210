import pandas as pd
import numpy as np
from . import tru as tru

#just work for year >= 2010
class system: 
    def __init__(self,year,level,unit):
        self.Y = year
        self.L = level
        self.u = unit
        self.D_total_pm()  # Call the D_total_pm method automatically
        self.mDist()
        self.correct_mMG_tra()
        self.correct_mMG_com()
        self.vec_to_matrix()
        self.D_total_pb()
        self.transform_to_quadratic_matrix()
    def D_total_pm(self): #total demand at market price
        import math
        if int(self.Y) >= 2010:
            #matriz de demanda de bens finais
            set1 = ['X_bens_serv', 'C_g', 'C_ong','C_f','FBKF','DE']
            mD_final = np.concatenate([tru.read_var(self.Y,self.L,i,self.u).values for i in set1], axis=1)
        else:
            #matriz de demanda de bens finais
            vX_bens = tru.read_var(self.Y,self.L,'X_bens',self.u).values
            vX_serv = tru.read_var(self.Y,self.L,'X_serv',self.u).values
            vX_bens_serv = vX_bens + vX_serv
            set1 = ['C_g', 'C_ong','C_f','FBKF','DE']
            mD_final_sem_bens_verv = np.concatenate([tru.read_var(self.Y,self.L,i,self.u).values for i in set1], axis=1)
            mD_final = np.concatenate(vX_bens_serv,mD_final_sem_bens_verv)
        #matriz de demanda de bens intermediátios (consumo das firmas)
        mD_int = tru.read_var(self.Y,self.L,'CI_matrix',self.u).values
        #matriz de demanda total (bens finais + bens intermediários)
        self.mD_total = np.concatenate((mD_int,mD_final), axis=1)
    def mDist(self):
        #matriz de distribuição (para distribuir impostos indiretos e margens)
        vD_total = tru.read_var(self.Y,self.L,'D_total',self.u).values
        vDE = tru.read_var(self.Y,self.L,'DE',self.u).values
        mD_total = self.mD_total #D_total_pm(self.Y,self.L,self.u)
        #admita variação nula de estoque
        mD_total[:,int(self.L)+5] = 0
        # Perform row-wise division
        self.mDist1 = mD_total / (vD_total - vDE)[:None] #não deveria funcionar mas está funcionando ok
        #dist = np.nan_to_num(dist, nan=0, posinf=0, neginf=0) #deveria fuincionar mas não fuinciona
        #admita exportacao nula
        mD_total[:,int(self.L)] = 0
        #matriz de distribuição (para distribuir exportação e I_imp)
        vX_bens_serv = tru.read_var(self.Y,self.L,'X_bens_serv',self.u).values
        # Perform row-wise division
        self.mDist2 = mD_total / (vD_total - vDE - vX_bens_serv)[:None]
        #return mDist , mDist_MG
    #usar matriz de transformação para converter vetores em matrizes
    def correct_mMG_tra(self):
        good = 'Transporte'
        mMG_tra_ = self.mDist1 * tru.read_var(self.Y,self.L,'MG_tra',self.u).values[:None]
        ##as linhas referentes aos bens de transportes são
        vMG_tra = tru.read_var(self.Y,self.L,'MG_tra',self.u)
        lines_name = vMG_tra.index[vMG_tra.index.str.contains(good)]
        lines_number = [vMG_tra.index.get_loc(idx) for idx in lines_name]
        ## 'Drop' transport rows 
        mMG_tra_[lines_number] = 0
        ##replace values in transport rows
        ##Eu seu que o total da coluna (1) agora é (X). Então, eu tenho que colocar (-X) nas linhas que foram zeradas, assim o total da coluna serpa zero.
        ##o problema é que eu tenho que distribuir (-X) em (4) linhas referentes à dransporte. Como eu faço a distribuição desses valores?
        ##usando a proporção que existe no vetor 'vMG_tra' 
        prop_trans  = vMG_tra.values[lines_number] / np.sum(vMG_tra.values[lines_number])
        vec_sum_rows = mMG_tra_.sum(axis = 0)
        for i in range(0,len(lines_number)):
            mMG_tra_[lines_number[i]] = - vec_sum_rows * prop_trans[i]
        self.mMG_tra_cor = mMG_tra_.copy()
    #correção da margem de comercio
    def correct_mMG_com(self):
        good='Comércio'
        mMG_com_ = self.mDist1 * tru.read_var(self.Y,self.L,'MG_com',self.u).values[:None]
        vMG_com = tru.read_var(self.Y,self.L,'MG_com',self.u)
        lines_name = vMG_com.index[vMG_com.index.str.contains(good)]
        lines_number = [vMG_com.index.get_loc(idx) for idx in lines_name]
        mMG_com_[lines_number] = 0
        prop_com  = vMG_com.values[lines_number] / np.sum(vMG_com.values[lines_number])
        vec_sum_rows = mMG_com_.sum(axis = 0)
        for i in range(0,len(lines_number)):
            mMG_com_[lines_number[i]] = - vec_sum_rows * prop_com[i]
        self.mMG_com_cor = mMG_com_.copy()
    def vec_to_matrix (self):
        # Perform row-wise product
        self.mIPI = self.mDist1 * tru.read_var(self.Y,self.L,'IPI',self.u).values[:None]
        self.mICMS = self.mDist1 * tru.read_var(self.Y,self.L,'ICMS',self.u).values[:None]
        self.mOI_liq_Sub = self.mDist1 * tru.read_var(self.Y,self.L,'OI_liq_Sub',self.u).values[:None]
        self.mI_imp = self.mDist2 * tru.read_var(self.Y,self.L,'I_imp',self.u).values[:None]
        self.mM_bens_serv = self.mDist2 * tru.read_var(self.Y,self.L,'M_bens_serv',self.u).values[:None]
        #return mIPI, mICMS, mOI_liq_Sub, mMG_tra_, mMG_com_, mI_imp, mM_bens_serv
    #demanda total a preços básicos
    def D_total_pb(self):
        mD_total_pm = self.mD_total #D_total_pm(year,level,unit)
        matrixs = [self.mIPI, self.mICMS, self.mOI_liq_Sub, self.mMG_tra_cor, self.mMG_com_cor, self.mI_imp, self.mM_bens_serv]#vec_to_matrix (year,level,unit)
        mD_total_pb = mD_total_pm.copy()
        for m in matrixs:
            mD_total_pb = mD_total_pb - m
        #separando demanda final e demanda intermediária a preços básicos
        self.mD_int_pb = mD_total_pb[:, 0:int(self.L)] #mU
        self.mD_final_pb = mD_total_pb[:, int(self.L):] #mE
        #return mD_int_pb, mD_final_pb
    def transform_to_quadratic_matrix(self):
        mU = self.mD_int_pb
        mE = self.mD_final_pb
        #Estimar matriz (D)
        mV = tru.read_var(self.Y,self.L,'P_matrix',self.u).values.T
        #Total produzido por produto
        #vQ = np.sum(mV, axis=0)
        vQ = tru.read_var(self.Y,self.L,'PT',self.u).values
        mQChapeu = np.diagflat(1/vQ)
        mD = np.dot(mV, mQChapeu)
        #Estimar matriz (B)
        #Total produzido por setor
        vVBP = np.sum(mV, axis=1)
        vX = np.copy(vVBP)
        mXChapeu = np.diagflat(1/vX)
        mB=np.dot(mU,mXChapeu)
        #converter para matrizes quadradas        
        self.mD_final_pb_qua = np.dot(mD,mE).astype(float) #mY
        self.mD_int_pb_qua = np.dot(mD,mU).astype(float) #mZ
        #encontrar matriz de Leontief
        mA = np.dot(mD,mB).astype(float)
        mI = np.eye(int(self.L))
        self.mLeontief = np.linalg.inv(mI - mA)




  

