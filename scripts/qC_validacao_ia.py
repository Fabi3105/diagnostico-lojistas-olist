# -*- coding: utf-8 -*-
"""Validação da classificação com IA dos comentários de nota 1 (sugestão C).
Três classificações independentes de 1.000 comentários (amostra que inclui os 150 da validação humana):
A = classificação original (agentes Claude Sonnet, regras de qC_instrucoes_classificacao_ia.md);
B = agentes Claude Opus, mesmas regras com redação diferente (qC_instrucoes_validador_B.md);
C = agentes Claude Sonnet, mesmas regras com outra redação (qC_instrucoes_validador_C.md).
Mede a concordância por kappa de Cohen (pares) e kappa de Fleiss (os três), por tema e por grupo."""
import pandas as pd, numpy as np
def rd(f): return pd.read_csv(f,sep=';',header=None,names=['cid','tema','sr'])
import os, sys
R=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'resultados')
d=pd.read_csv(os.path.join(R,'qC_validacao_rotulos_3ias.csv'),sep=';')
print('n',len(d))
GR={'nao_recebido':'Logística','atraso':'Logística','falha_entrega':'Logística','incompleto':'Lojista','produto_errado':'Lojista','cancelamento_estoque':'Lojista','defeito_avaria':'Produto','qualidade_anuncio':'Produto','atendimento':'Outros','outro':'Outros'}
def cohen(x,y):
    cats=sorted(set(x)|set(y)); po=(x==y).mean()
    pe=sum((x==c).mean()*(y==c).mean() for c in cats); return (po-pe)/(1-pe), po
def fleiss(M):  # M: n x 3 labels
    cats=sorted(set(M.ravel())); n,r=M.shape
    cnt=np.array([[ (row==c).sum() for c in cats] for row in M])
    P=((cnt*(cnt-1)).sum(1))/(r*(r-1)); Pb=P.mean(); pj=cnt.sum(0)/(n*r); Pe=(pj**2).sum()
    return (Pb-Pe)/(1-Pe)
res=[]
for nivel,f in [('tema',lambda s:s),('grupo',lambda s:s.map(GR))]:
    a,b,c=f(d.tema_A),f(d.tema_B),f(d.tema_C)
    for nm,x,y in [('A x B',a,b),('A x C',a,c),('B x C',b,c)]:
        k,po=cohen(x.values,y.values); res.append([nivel,nm,round(po*100,1),round(k,3)])
    res.append([nivel,'Fleiss (A, B, C)',round(100*((a==b)&(b==c)).mean(),1),round(fleiss(np.column_stack([a,b,c])),3)])
r=pd.DataFrame(res,columns=['nivel','comparacao','concordancia_pct','kappa']); print(r.to_string(index=False))
k,po=cohen(d.sr_A.values,d.sr_B.values); k2,_=cohen(d.sr_A.values,d.sr_C.values); k3,_=cohen(d.sr_B.values,d.sr_C.values)
print('sem_resposta kappas',round(k,3),round(k2,3),round(k3,3))
# maioria
def maj(row):
    v=[row.tema_A,row.tema_B,row.tema_C]; 
    for t in v:
        if v.count(t)>=2: return t
    return 'sem_maioria'
d['maioria']=d.apply(maj,axis=1)
print('sem maioria',(d.maioria=='sem_maioria').sum(),' A igual maioria %',round(100*(d.tema_A==d.maioria).mean(),1))
# por tema: % dos casos rotulados A com tema t em que B e C concordam
d['bA']=d.tema_B==d.tema_A; d['cA']=d.tema_C==d.tema_A; d['tres']=d.bA&d.cA
t=d.groupby('tema_A').agg(n=('cid','size'),B_igual=('bA','mean'),C_igual=('cA','mean'),os_3_iguais=('tres','mean')); t[['B_igual','C_igual','os_3_iguais']]*=100; t=t.round(1).sort_values('n',ascending=False)
print(t)
# distribuição: proporção de cada tema por A vs maioria
print(pd.DataFrame({'A':d.tema_A.value_counts(normalize=True),'B':d.tema_B.value_counts(normalize=True),'C':d.tema_C.value_counts(normalize=True)}).mul(100).round(1))

r.to_csv(os.path.join(R,'qC_validacao_ia_1.csv'),sep=';',decimal=',',index=False,encoding='utf-8-sig'); t.to_csv(os.path.join(R,'qC_validacao_ia_2.csv'),sep=';',decimal=',',encoding='utf-8-sig')
