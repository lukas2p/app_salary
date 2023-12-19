import streamlit as st
import pandas as pd
import datetime
import numpy as np
import graphviz

st.set_page_config(layout="wide")

def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)
    return next_month - datetime.timedelta(days=next_month.day)
st.sidebar.subheader("Základné parametre")

d_sviatky = pd.read_excel("./sviatky.xlsx", index_col = None)
d_sviatky['DATUM1'] = d_sviatky['DATUM'].dt.date

v_pn_prvy_den = datetime.date(2099, 12, 31)
v_pn_posl_den = datetime.date(2099, 12, 31)
v_prisp_zl=0
v_prisp_zc=0

# SIDEPANEL
sb1c1, sb1c2 = st.sidebar.columns(2)
v_rok = sb1c1.selectbox('Rok: ', [2023, 2024])
v_mesiac = sb1c2.selectbox('Mesiac: ', [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
v_zmluvna_mzda = st.sidebar.number_input("Zmluvná mzda", min_value = 0, value = 1500, key="zmluvna_mzda")
v_priemerka = st.sidebar.number_input("Priemerná hodinová mzda", min_value = 0.0000, value = v_zmluvna_mzda/168, key="priemerna_hodinova_mzda")
v_denny_fond_hodin = st.sidebar.number_input("Denný fond hodín", min_value = 0.00, value = 8.00, key="denny_fond_hodin")
v_ostatne = st.sidebar.number_input("Ostatné príjmy", min_value = 0, value = 0)
with st.sidebar.expander("Prispievam na DDS"):
    v_dds = st.sidebar.toggle("Prispievam na DDS", False, key = "3dss")
    if v_dds == True:
        v_prisp_zl = st.sidebar.number_input("Príspevok zamestnávateľa na DDS", min_value = 0, value = 0, key="dss_zamestnavatel", placeholder="Vyplňte koeficient")
        v_prisp_zc = st.sidebar.number_input("Príspevok zamestnanca na DDS", min_value = 0, value = 0, key="dss_zamestnanec", placeholder="Vyplňte koeficient")

with st.sidebar.expander("PNka"):
    v_pn = st.sidebar.toggle("Bol som práceneschopný", False, key="1pn")
    if v_pn == True:
        sb2c1, sb2c2 = st.sidebar.columns(2)
        v_pn_prvy_den = sb2c1.date_input("Prvý deň PN", value=datetime.date(v_rok, 1, 1))
        v_pn_posl_den = sb2c2.date_input("Posledný deň PN", value=datetime.date(v_rok, 1, 1))
        v_vz_minuly_rok = st.sidebar.number_input("Vymeriavací základ za predch. rok", min_value = 0.00, value = float(v_zmluvna_mzda*12))
        st.sidebar.write("Koeficienty náhrady príjmu od zamestnávateľa")
        sb3c1, sb3c2, sb3c3 = st.sidebar.columns(3)
        v_pn_prisp3 = (sb3c2.number_input("Dni 1-3", min_value = 25, value = 25))/100
        v_pn_prisp10 = (sb3c3.number_input("Dni 4-10", min_value = 55, value = 55))/100

v_min_rok_pocet_dni = (datetime.date(v_rok-1, 12, 31) - datetime.date(v_rok-2, 12, 31)).days

d_dictionaries = []
v_datum_min = datetime.date(v_rok, v_mesiac, 1)
v_datum_max = last_day_of_month(v_datum_min)
v_pocet_dni = v_datum_max.day
v_pocet_dni_pn = (v_pn_posl_den - v_pn_prvy_den).days+1
v_dni_pn = dict()
v_fond = 0
sb4c = ["sb4c1", "sb4c2", "sb4c3", "sb4c4"]
sb4 = []

with st.sidebar.expander("Dovolenka"):
    v_dov = st.sidebar.toggle("Čerpal som dovolenku", False, key="2dov")
    if v_dov == True:
        st.sidebar.caption("Vyberte dni čerpanej dovolenky. Ak je zaškrtávacie pole neaktívne ide o sviatok alebo víkend.")
        sb4c[0], sb4c[1], sb4c[2], sb4c[3] = st.sidebar.columns(4)
        for j in range(v_pocet_dni):
            v_day = datetime.date(v_rok, v_mesiac, j+1)
            if v_day in d_sviatky["DATUM1"].tolist():
                sb4 = sb4 + [sb4c[j%4].checkbox(str(j+1), disabled=True, key="dov"+str(j))]
            elif v_day.weekday() in [5,6]:
                sb4 = sb4 + [sb4c[j%4].checkbox(str(j+1), disabled=True, key="dov"+str(j))]
            else:
                sb4 = sb4 + [sb4c[j%4].checkbox(str(j+1), disabled=False, key="dov"+str(j))]
                


for i in range(v_pocet_dni_pn):
    v_dni_pn[v_pn_prvy_den + datetime.timedelta(days=i)] = i+1
for i in range(v_pocet_dni): 
    v_day = datetime.date(v_rok, v_mesiac, i+1)
    if v_day.weekday() in [5,6]:
        v_fond = v_fond + 0
    elif v_day in d_sviatky["DATUM1"].tolist():
        v_fond = v_fond + 1
    else:
        v_fond = v_fond + 1



for i in range(v_pocet_dni):
    v_day = datetime.date(v_rok, v_mesiac, i+1)
    v_working_day = "N/A"
    v_hruby_prijem_denny = 0
    v_hruby_prijem_denny_typ = "Neplatený deň"
    if v_day.weekday() in [5,6]:
        v_working_day = "Víkend"
    elif v_day in d_sviatky["DATUM1"].tolist():
        v_working_day = "Sviatok - "+list(d_sviatky.loc[d_sviatky['DATUM1'] == v_day, "SVIATOK"])[0]
        v_hruby_prijem_denny = v_zmluvna_mzda/v_fond
        v_hruby_prijem_denny_typ = "Hrubý príjem - sviatok"
    else:
        v_working_day = "Pracovný deň"
        v_hruby_prijem_denny = v_zmluvna_mzda/v_fond
        v_hruby_prijem_denny_typ = "Hrubý príjem - mzda"

        
    d_dictionaries.append({"Dátum": v_day, 
                           "Deň":v_working_day, 
                           "Hrubý príjem": v_hruby_prijem_denny,
                           "Typ": v_hruby_prijem_denny_typ})


d_df = pd.DataFrame.from_dict(d_dictionaries)
for i in range(v_pocet_dni):
    v_day = datetime.date(v_rok, v_mesiac, i+1)
    if v_day >= v_pn_prvy_den and v_day <= v_pn_posl_den:
        if v_dni_pn[v_day] <= 3:
            d_dictionaries[i]["Hrubý príjem"] = round(v_pn_prisp3*v_vz_minuly_rok/v_min_rok_pocet_dni,4)
            d_dictionaries[i]["Typ"] = "Náhrada za 1. až 3. deň PN"
        elif v_dni_pn[v_day] >= 4 and v_dni_pn[v_day] <= 10:
            d_dictionaries[i]["Hrubý príjem"] = round(v_pn_prisp10*v_vz_minuly_rok/v_min_rok_pocet_dni,4)
            d_dictionaries[i]["Typ"] = "Náhrada za 4. až 10. deň PN"
        elif v_dni_pn[v_day] >= 11:
            d_dictionaries[i]["Hrubý príjem"] = round(0.55*v_vz_minuly_rok/v_min_rok_pocet_dni,4)
            d_dictionaries[i]["Typ"] = "Nemocenská dávka"
    if v_dov == True:
        if sb4[i] == True:
            d_dictionaries[i]["Hrubý príjem"] = round(v_priemerka*v_denny_fond_hodin,4)
            d_dictionaries[i]["Typ"] = "Náhrada mzdy za dovolenku"


# VYPOCTY
v_sum_sviatky = 0
v_sum_mzda = 0
v_sum_pn = 0
v_sum_pn_nem = 0
v_sum_dov = 0
v_vz_zp = 0
v_vz_sp = 0
for i in range(v_pocet_dni):
    if d_dictionaries[i]["Typ"] == "Hrubý príjem - mzda":
        v_sum_mzda = v_sum_mzda + d_dictionaries[i]["Hrubý príjem"]
    elif d_dictionaries[i]["Typ"] == "Hrubý príjem - sviatok":
        v_sum_sviatky = v_sum_sviatky + d_dictionaries[i]["Hrubý príjem"]
    elif d_dictionaries[i]["Typ"] in ("Náhrada za 1. až 3. deň PN", "Náhrada za 4. až 10. deň PN"):
        v_sum_pn = v_sum_pn + d_dictionaries[i]["Hrubý príjem"]
    elif d_dictionaries[i]["Typ"] in ("Nemocenská dávka"):
        v_sum_pn_nem = v_sum_pn_nem + d_dictionaries[i]["Hrubý príjem"]
    elif d_dictionaries[i]["Typ"] in ("Náhrada mzdy za dovolenku"):
        v_sum_dov = v_sum_dov + d_dictionaries[i]["Hrubý príjem"]
v_vz_zp = v_sum_mzda+v_sum_sviatky+v_ostatne+v_sum_dov+v_prisp_zl
v_vz_sp = v_sum_mzda+v_sum_sviatky+v_ostatne+v_sum_dov
print(v_sum_dov)


# PREZENTÁCIA
m1c1, m1c2 = st.columns([7,9])
m1c1.subheader("Súhrn")
m1c2.subheader("Odvody")

m1c1, m1c2, mc, m1c3, m1c4 = st.columns([4,2,1,7,2])
v_hruby_prijem = v_sum_mzda+v_sum_sviatky+v_ostatne+v_sum_dov
m1c1.caption("Hrubý príjem")
m1c2.markdown('<div style="text-align: right;">'+str(format(round(v_hruby_prijem,2),".2f"))+' €</div>', unsafe_allow_html=True)
m1c3.caption("Vymeriavací základ - zdr. poistenie")
m1c4.markdown('<div style="text-align: right; color: rgb(131,133,139); font-size:11pt">'+str(format(round(v_vz_zp,2),".2f"))+' €</div>', unsafe_allow_html=True)

m1c1, m1c2, mc, m1c3, m1c4 = st.columns([4,2,1,7,2])
m1c1.caption("Náhrady za PN (1. - 10 deň)", help="Platí zamestnávateľ.")
m1c2.markdown('<div style="text-align: right;">'+str(format(round(v_sum_pn,2),".2f"))+' €</div>', unsafe_allow_html=True)
m1c3.caption("Vymeriavací základ - soc. poistenie:")
m1c4.markdown('<div style="text-align: right; color: rgb(131,133,139); font-size:11pt">'+str(format(round(v_vz_sp,2),".2f"))+' €</div>', unsafe_allow_html=True)

m1c1, m1c2, mc, m1c3, m1c4 = st.columns([4,2,1,7,2])
m1c3.caption("Zdravotné poistenie:")
m1c4.markdown('<div style="text-align: right; color: rgb(131,133,139); font-size:11pt">'+str(format(round(v_vz_zp*0.04,2),".2f"))+' €</div>', unsafe_allow_html=True)

v_zaklad_dane = round(v_sum_mzda+v_sum_sviatky+v_ostatne+v_sum_dov+v_prisp_zl-v_vz_zp*0.04-v_vz_sp*0.094,2)
m1c1, m1c2, mc, m1c3, m1c4 = st.columns([4,2,1,7,2])
m1c1.caption("Základ dane")
m1c2.markdown('<div style="text-align: right; color: rgb(131,133,139); font-size:11pt">'+str(format(v_zaklad_dane,".2f"))+' €</div>', unsafe_allow_html=True)
m1c3.caption("Sociálne poistenie:")
m1c4.markdown('<div style="text-align: right; color: rgb(131,133,139); font-size:11pt">'+str(format(round(v_vz_sp*0.094,2),".2f"))+' €</div>', unsafe_allow_html=True)

v_dan_19 = 0
v_dan_25 = 0
m1c1, m1c2, mc, m1c3, m1c4 = st.columns([4,2,1,7,2])
v_dan_19 = v_zaklad_dane*0.19
m1c1.caption("Daň 19%")
m1c2.markdown('<div style="text-align: right;">'+str(format(round(v_dan_19,2),".2f"))+' €</div>', unsafe_allow_html=True)
m1c3.caption("Sociálne poistenie:")
m1c4.markdown('<div style="text-align: right; color: rgb(131,133,139); font-size:11pt">'+str(format(round(v_vz_sp*0.094,2),".2f"))+' €</div>', unsafe_allow_html=True)

if v_zaklad_dane > 3499.19:
    m1c1, m1c2, mc, m1c3, m1c4 = st.columns([4,2,1,7,2])
    v_dan_25 = (v_zaklad_dane - 3499.19)*0.25
    m1c1.caption("Daň 25%")
    m1c2.markdown('<div style="text-align: right;">'+str(format(round(v_dan_25,2),".2f"))+' €</div>', unsafe_allow_html=True)

m1c1, m1c2, mc, m1c3, m1c4 = st.columns([4,2,1,7,2])
v_cista_mzda = v_sum_mzda+v_sum_sviatky+v_ostatne+v_sum_dov+v_sum_pn-v_dan_19-v_dan_25-v_vz_sp*0.094-v_vz_zp*0.04
m1c1.markdown('<div style="text-align: left; font-weight:bold;">Čistá mzda</div>', unsafe_allow_html=True)
m1c2.markdown('<div style="text-align: right; font-weight:bold;">'+str(format(round(v_cista_mzda,2),".2f"))+' €</div>', unsafe_allow_html=True)

m1c1, m1c2, mc, m1c3, m1c4 = st.columns([4,2,1,7,2])
m1c1.caption('Zrážky - Príspevky DDS')
m1c2.markdown('<div style="text-align: right; color: rgb(131,133,139); font-size:11pt">'+str(format(round(v_prisp_zc,2),".2f"))+' €</div>', unsafe_allow_html=True)

m1c1, m1c2, mc, m1c3, m1c4 = st.columns([4,2,1,7,2])
m1c1.markdown('<div style="text-align: left; font-weight:bold;">K výplate</div>', unsafe_allow_html=True)
m1c2.markdown('<div style="text-align: right; font-weight:bold;">'+str(format(round(v_cista_mzda-v_prisp_zc,2),".2f"))+' €</div>', unsafe_allow_html=True)

m1c1, m1c2, mc, m1c3, m1c4 = st.columns([4,2,1,7,2])
m1c1.markdown('<div style="text-align: left; font-weight:bold;">Náhrady za PN - nemocenské</div>', unsafe_allow_html=True)
m1c2.markdown('<div style="text-align: right; font-weight:bold;">'+str(format(round(v_sum_pn_nem,2),".2f"))+' €</div>', unsafe_allow_html=True)

m1c1, m1c2, mc, m1c3, m1c4 = st.columns([4,2,1,7,2])

st.subheader("Podrobný rozpis")

#for i in range(v_pocet_dni):
#    v_day = datetime.date(v_rok, v_mesiac, i+1)
#    m1c1, m1c2, m1c3, m1c4 = st.columns([1,3,1,3])
#    m1c1.caption(d_dictionaries[i]["Dátum"]) 
#    m1c2.caption(d_dictionaries[i]["Deň"]) 
#    if v_day.weekday() in [5,6] or v_day in d_sviatky["DATUM1"].tolist():
#        m1c3.markdown('<div style="text-align: right; color: rgb(131,133,139); font-size:11pt">' + str(format(d_dictionaries[i]["Hrubý príjem"],".4f")) + '</div>', unsafe_allow_html=True)
#    else:
#        m1c3.markdown('<div style="text-align: right;">' + str(format(d_dictionaries[i]["Hrubý príjem"],".4f")) + '</div>', unsafe_allow_html=True)
#    m1c4.caption(d_dictionaries[i]["Typ"]) 

#####################
# GRAF
#####################
graph = graphviz.Digraph()
graph.node('Hrubý príjem za\n odpracované dni\n'+str(format(round(v_sum_mzda,2),".2f"))+' €', shape="box", style="filled", color="lightblue")
graph.node('Náhrada za sviatok\n'+str(format(round(v_sum_sviatky,2),".2f"))+' €', shape="box", style="filled", color="lightblue")
graph.node('Hrubý príjem\n'+str(format(round(v_hruby_prijem,2),".2f"))+' €', shape="box", style="filled", color="steelblue")
graph.node('Daň z príjmu\n'+str(format(round(v_dan_19,2),".2f"))+' €', shape="box", style="filled", color="salmon")
graph.node('Sociálne poistenie\n'+str(format(round(v_vz_sp*0.094,2),".2f"))+' €', shape="box", style="filled", color="salmon")
graph.node('Zdravotné poistenie\n'+str(format(round(v_vz_zp*0.04,2),".2f"))+' €', shape="box", style="filled", color="salmon")
graph.node('Čistý príjem\n'+str(format(round(v_cista_mzda,2),".2f"))+' €', shape="box", style="filled", color="mediumseagreen")

graph.edge('Hrubý príjem za\n odpracované dni\n'+str(format(round(v_sum_mzda,2),".2f"))+' €', 'Hrubý príjem\n'+str(format(round(v_hruby_prijem,2),".2f"))+' €', label="+")
graph.edge('Hrubý príjem za\n odpracované dni\n'+str(format(round(v_sum_mzda,2),".2f"))+' €', 'Základ dane\n'+str(format(round(v_zaklad_dane,2),".2f"))+' €', label="+")

graph.edge('Náhrada za sviatok\n'+str(format(round(v_sum_sviatky,2),".2f"))+' €', 'Hrubý príjem\n'+str(format(round(v_hruby_prijem,2),".2f"))+' €', label="+")
graph.edge('Náhrada za sviatok\n'+str(format(round(v_sum_sviatky,2),".2f"))+' €', 'Základ dane\n'+str(format(round(v_zaklad_dane,2),".2f"))+' €', label="+")

if v_dov == True:
    graph.node('Náhrada za dovolenku\n'+str(format(round(v_sum_dov,2),".2f"))+' €', shape="box", style="filled", color="lightblue")
    graph.edge('Náhrada za dovolenku\n'+str(format(round(v_sum_dov,2),".2f"))+' €', 'Hrubý príjem\n'+str(format(round(v_hruby_prijem,2),".2f"))+' €', label="+")
    graph.edge('Náhrada za dovolenku\n'+str(format(round(v_sum_dov,2),".2f"))+' €', 'Základ dane\n'+str(format(round(v_zaklad_dane,2),".2f"))+' €', label="+")
if v_ostatne > 0:
    graph.node('Ostatné príjmy\n'+str(format(round(v_ostatne,2),".2f"))+' €', shape="box", style="filled", color="lightblue")
    graph.edge('Ostatné príjmy\n'+str(format(round(v_ostatne,2),".2f"))+' €', 'Hrubý príjem\n'+str(format(round(v_hruby_prijem,2),".2f"))+' €', label="+")
    graph.edge('Ostatné príjmy\n'+str(format(round(v_ostatne,2),".2f"))+' €', 'Základ dane\n'+str(format(round(v_zaklad_dane,2),".2f"))+' €', label="+")

graph.edge('Hrubý príjem\n'+str(format(round(v_hruby_prijem,2),".2f"))+' €', 'Vymeriavací základ - SP\n'+str(format(round(v_vz_sp,2),".2f"))+' €', label="+")
if v_dds == True:
    graph.edge('Príspevok na DDS\n'+str(format(round(v_prisp_zl,2),".2f"))+' €', 'Vymeriavací základ - ZP\n'+str(format(round(v_vz_zp,2),".2f"))+' €', label="+")
    graph.edge('Príspevok na DDS\n'+str(format(round(v_prisp_zl,2),".2f"))+' €', 'Základ dane\n'+str(format(round(v_zaklad_dane,2),".2f"))+' €', label="+")

graph.edge('Hrubý príjem\n'+str(format(round(v_hruby_prijem,2),".2f"))+' €', 'Vymeriavací základ - ZP\n'+str(format(round(v_vz_zp,2),".2f"))+' €', label="+")

graph.edge('Vymeriavací základ - SP\n'+str(format(round(v_vz_sp,2),".2f"))+' €', 'Sociálne poistenie\n'+str(format(round(v_vz_sp*0.094,2),".2f"))+' €', label="9.4%")
graph.edge('Sociálne poistenie\n'+str(format(round(v_vz_sp*0.094,2),".2f"))+' €', 'Základ dane\n'+str(format(round(v_zaklad_dane,2),".2f"))+' €', label="-")

graph.edge('Vymeriavací základ - ZP\n'+str(format(round(v_vz_zp,2),".2f"))+' €', 'Zdravotné poistenie\n'+str(format(round(v_vz_zp*0.04,2),".2f"))+' €', label="4%")
graph.edge('Zdravotné poistenie\n'+str(format(round(v_vz_zp*0.04,2),".2f"))+' €', 'Základ dane\n'+str(format(round(v_zaklad_dane,2),".2f"))+' €', label="-")

graph.edge('Základ dane\n'+str(format(round(v_zaklad_dane,2),".2f"))+' €', 'Daň z príjmu\n'+str(format(round(v_dan_19,2),".2f"))+' €', label="19%")
graph.edge('Daň z príjmu\n'+str(format(round(v_dan_19,2),".2f"))+' €', 'Čistý príjem\n'+str(format(round(v_cista_mzda,2),".2f"))+' €', label="-")

if v_zaklad_dane > 3499.19:
    graph.edge('Základ dane\n'+str(format(round(v_zaklad_dane,2),".2f"))+' €', 'Progresívna daň\n'+str(format(round(v_dan_25,2),".2f"))+' €', label="25%")
    graph.node('Progresívna daň\n'+str(format(round(v_dan_25,2),".2f"))+' €', shape="box", style="filled", color="salmon")
    graph.edge('Progresívna daň\n'+str(format(round(v_dan_25,2),".2f"))+' €', 'Čistý príjem\n'+str(format(round(v_cista_mzda,2),".2f"))+' €', label="-")

graph.edge('Hrubý príjem\n'+str(format(round(v_hruby_prijem,2),".2f"))+' €', 'Čistý príjem\n'+str(format(round(v_cista_mzda,2),".2f"))+' €')
graph.edge('Zdravotné poistenie\n'+str(format(round(v_vz_zp*0.04,2),".2f"))+' €', 'Čistý príjem\n'+str(format(round(v_cista_mzda,2),".2f"))+' €')
graph.edge('Sociálne poistenie\n'+str(format(round(v_vz_sp*0.094,2),".2f"))+' €', 'Čistý príjem\n'+str(format(round(v_cista_mzda,2),".2f"))+' €')
if v_pn == True:
    graph.node('Náhrada príjmu za\n práceneschopnosť\n'+str(format(round(v_sum_pn,2),".2f"))+' €', shape="box", style="filled", color="steelblue")
    graph.edge('Náhrada príjmu za\n práceneschopnosť\n'+str(format(round(v_sum_pn,2),".2f"))+' €', 'Čistý príjem\n'+str(format(round(v_cista_mzda,2),".2f"))+' €')

st.graphviz_chart(graph)

