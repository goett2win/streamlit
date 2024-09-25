import taxgermany as tg
#import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import streamlit as st

st.write("# Eine einfache Einkommenssteuer")
st.write("Version 0.0.5")

st.write('Für Details schaut euch gerne meinen [ Blogeintrag ]( https://knut-heidemann.net/post/tax-reform/ ) an.')

st.write("*Reform a:*")
st.latex(r'''
	n(b) \equiv	\begin{cases}
	b\,, &\text{für } b<M,\\\
	M \left[1+(k-1)\tanh\left(\frac{b-M}{\alpha M}\right)\right], \alpha \in \mathbb R, &\text{für } b \geq M.
	\end{cases}''')

st.write("$n$: Netto-Einkommen, $b$: Brutto-Einkommen, $M$: Steuerfreibetrag")

st.write("*Reform b:*")
st.latex(r'''
        n(b) \equiv \begin{cases}
        b\,, &\text{für } b<M,\\\ 
        a\,\log(1+b/c)\,, \quad a = \frac{M}{\log(1+M/c)}\,, &\text{für } b\geq M.
        \end{cases}
        ''')
#add_vertical_space(10)

st.sidebar.write("**Parameter:**")
g = st.sidebar.slider(r'$\boldsymbol M/12$ (monatlicher Steuerfreibetrag)', value=1500, min_value=400, max_value=2000, step=100)

st.sidebar.write("*Reform a:*")

k = st.sidebar.slider(r'$\boldsymbol k$ (Verhältnis von Maximaleinkommen zu Steuerfreibetrag)', value=5.0, min_value=1.0, max_value=30.0, step=1.0)
alpha = st.sidebar.slider(r'$\boldsymbol\alpha$ (Skalierungsparameter)', min_value=k-1, max_value=3*k, value=1.5*(k-1), step=0.1)

M = 12*g

st.sidebar.write("*Reform b:*")
c = st.sidebar.slider(r'$\boldsymbol c$ (Skalierungsparameter)', min_value=1e4, max_value=20e4, value=2.5*M, step=1e3)


B = np.linspace(1,3e5,300)
N = tg.netto_vectorized(B,alpha,k,M)

N_status_quo = tg.netto_ger_vectorized(B)
N_max = tg.netto_max_vectorized(B, c, M)
N_linke = tg.netto_linke_vectorized(B)

data = pd.DataFrame(
        {
            'brutto': B,
            'Reform a': N,
            'status quo': N_status_quo,
            'Reform b': N_max,
            #'linke': N_linke,
            'brutto=netto': B,
        }
    )

data_tax = pd.DataFrame(
        {
            'brutto': B,
            'Reform a': (B-N)/B,
            'status quo': (B-N_status_quo)/B,
            'Reform b': (B-N_max)/B,
        }
    )
st.write("### Netto vom Brutto")
switch = st.radio(
      "Was soll gezeigt werden?",
      ["Netto", "Steuersatz"],
      horizontal = True
      )
#on = st.toggle("Durchschnittssteuersatz")


if switch == "Steuersatz":
    #st.write("### Durchschnittssteuersatz")
    st.line_chart(data_tax, x='brutto', y=['Reform a', 'Reform b', 'status quo'], y_label='Durchschnittssteuersatz', x_label='brutto')
else:
    st.line_chart(data, x='brutto', y=['Reform a', 'Reform b', 'status quo','brutto=netto'], x_label='brutto', y_label='netto')


B_frame = pd.read_csv('./data/verteilung-bruttomonatsverdienste-vollzeitbeschaeftigung-cleansed.csv', sep=',')
B_frame.Mittelwert *= 12 # yearly income not monthly
B_frame.Anteil *= 0.01 # not in %

brutto = B_frame['Mittelwert']
mass = B_frame["Anteil"]

netto_now = tg.netto_ger_vectorized(brutto)
netto_dist = tg.netto_vectorized(brutto, alpha, k, M)
netto_dist_max = tg.netto_max_vectorized(brutto, c, M)

tax_now = tg.tax_ger_vectorized(brutto)
tax_reformed = tg.tax_vectorized(brutto, alpha, k, M)
tax_reformed_b = tg.tax_max_vectorized(brutto, c, M)

revenue_now = np.dot(tax_now, mass)
revenue = tg.reformed_tax_revenue(brutto, mass, alpha, k, M)
revenue_max = tg.reformed_tax_revenue_max(brutto, mass, c, M)
rel_rev_change = 100*(revenue-revenue_now)/revenue_now
rel_rev_change_max = 100*(revenue_max-revenue_now)/revenue_now

delta_tax = (netto_now-netto_dist)
delta_tax_b = (netto_now-netto_dist_max)
#delta_tax = (netto_now-netto_dist)/tax_now # in %
data_ger = pd.DataFrame(
        {
            'brutto': brutto,
            'Reform a': delta_tax,
            'Reform b': delta_tax_b
            }
        )

#
st.sidebar.write("**Änderung Steueraufkommen:**")
if (rel_rev_change>0):
    st.sidebar.write("### \+","%0.2f" % rel_rev_change, "%", "(Reform A)")
else:
    st.sidebar.write("### %0.2f" % rel_rev_change, "%", "(Reform A)" )
        #print("delta revenue=","%0.2f" % ((revenue-revenue_now)/revenue_now))
if (rel_rev_change_max>0):
    st.sidebar.write("### \+","%0.2f" % rel_rev_change_max, "%", "(Reform B)")
else:
    st.sidebar.write("### %0.2f" % rel_rev_change_max, "%", "(Reform B)")


st.write("### Wer hat mehr / weniger als vorher?")

st.bar_chart(data_ger, x='brutto', y=['Reform a', 'Reform b'], x_label='brutto', y_label='Änderung des jährlichen Steuerlast', stack=False)

### Contributions to tax revenue by quintiles
quantiles = [0.2, 0.4, 0.6, 0.8, 1.0]
xlabel = ['0-20%','20-40%','40-60%','60-80%','80-100%']
contributions = 100*np.array(tg.quantile_contributions(mass, tax_reformed, quantiles))
contributions_max = 100*np.array(tg.quantile_contributions(mass, tax_reformed_b, quantiles))
contributions_sq = 100*np.array(tg.quantile_contributions(mass, tax_now, quantiles))

contributions_str = [("%0.2f" % c) + "%" for c in contributions]
contributions_sq_str = [("%0.2f" % c) + "%" for c in contributions_sq]
contributions_max_str = [("%0.2f" % c) + "%" for c in contributions_max]
quantile_df = pd.DataFrame(
        {
            'Einkommens-Quintil': xlabel,
            #'Quantil': quantiles,
            'Beitrag (Status Quo)':  contributions_sq_str,
            'Beitrag (Reform a)':  contributions_str,
            'Beitrag (Reform b)':  contributions_max_str
            }
        )
st.write("### Beiträge zum Steueraufkommen")
#st.write("Das Quintil 0-20% umfasst die Beiträge der 20% Vollzeitbeschäftigten mit den geringsten Einkommen, 20-40% entsprechend die nächsten 20% höhere Einkommen etc., bis schließlich die 20% mit den höchsten Einkommen (80-100%).")

st.write(quantile_df)
#st.bar_chart(quantile_df, x='Quantil', y='Beitrag')


st.write('### Zugrundeliegende Brutto-Einkommensverteilung')

st.markdown("![Foo](https://knut-heidemann.net/img/income-distribution-germany-2023.png)")
#st.write("### Zugrundeliegende Brutto-Einkommensverteilung")
