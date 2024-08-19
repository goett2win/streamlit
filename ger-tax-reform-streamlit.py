import taxgermany as tg
#import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import streamlit as st

st.write("# Eine einfache Einkommenssteuer")

st.write('Für Details schaut euch gerne meinen [ Blogeintrag ]( https://knut-heidemann.net/post/tax-reform/ ) an.')

#st.write("**Formula for computing net income:**")
st.latex(r'''
	n(b) \equiv	\begin{cases}
	b, &\text{für } b<M,\\\
	M \left[1+(k-1)\tanh\left(\frac{b-M}{\alpha M}\right)\right], \alpha \in \mathbb R, &\text{für } b \geq M.
	\end{cases}''')

st.write("$n$: Netto-Einkommen, $b$: Brutto-Einkommen, $M$: Steuerfreibetrag")

#add_vertical_space(10)

g = st.sidebar.slider(r'$\boldsymbol M/12$ (monatlicher Steuerfreibetrag)', value=1500, min_value=400, max_value=2000, step=100)
k = st.sidebar.slider(r'$\boldsymbol k$ (Verhältnis von Maximaleinkommen zu Steuerfreibetrag)', value=5, min_value=1, max_value=15)
alpha = st.sidebar.slider(r'$\boldsymbol\alpha$ (Skalierungsparameter)', min_value=1.0, max_value=50.0, value=5.0, step=0.1)


M = 12*g

B = np.linspace(1,3e5,100)
N = tg.netto_vectorized(B,alpha,k,M)

N_status_quo = tg.netto_ger_vectorized(B)
N_linke = tg.netto_linke_vectorized(B)

data = pd.DataFrame(
        {
            'brutto': B,
            'reform': N,
            'status quo': N_status_quo,
            #'linke': N_linke,
            'brutto=netto': B,
        }
    )

st.line_chart(data, x='brutto', y=['reform','status quo','brutto=netto'], x_label='brutto', y_label='netto')
#st.line_chart(data, x='brutto', y=['reform','status quo','linke','brutto=netto'], x_label='brutto', y_label='netto')
#plt.plot(B/1000, tg.netto_vectorized(B,12.2,10)/1000,label=r"mein Vorschlag", lw=2)


B_frame = pd.read_csv('./data/verteilung-bruttomonatsverdienste-vollzeitbeschaeftigung-cleansed.csv', sep=',')
B_frame.Mittelwert *= 12 # yearly income not monthly
B_frame.Anteil *= 0.01 # not in %

brutto = B_frame['Mittelwert']
mass = B_frame["Anteil"]
netto_now = tg.netto_ger_vectorized(brutto)
netto_dist = tg.netto_vectorized(brutto, alpha, k, M)
delta_tax = netto_now-netto_dist
data_ger = pd.DataFrame(
        {
            'brutto': brutto,
            'dtax': delta_tax
            }
        )

#gini_now = tg.Gini(netto_now, mass)
#gini = tg.Gini(netto_dist, mass)
#
#st.sidebar.write("**Gini index now:**")
#st.sidebar.write(gini_now)
#
#st.sidebar.write("**Gini index reformed:**")
#st.sidebar.write(gini)
#
tax_now = tg.tax_ger_vectorized(brutto)
revenue_now = np.dot(tax_now, mass)
revenue = tg.reformed_tax_revenue(brutto, mass, alpha, k, M)
rel_rev_change = 100*(revenue-revenue_now)/revenue_now
#
st.sidebar.write("**Änderung Steueraufkommen:**")
if (rel_rev_change>0):
    st.sidebar.write("### \+","%0.2f" % rel_rev_change, "%" )
else:
    st.sidebar.write("### %0.2f" % rel_rev_change, "%" )
        #print("delta revenue=","%0.2f" % ((revenue-revenue_now)/revenue_now))

# who has more / less than before?

st.write("### Wer hat mehr / weniger als vorher?")

st.bar_chart(data_ger, x='brutto', y=['dtax'], x_label='brutto', y_label='Änderung der jährlichen Steuerlast')

#st.write("### Zugrundeliegende Brutto-Einkommensverteilung")
