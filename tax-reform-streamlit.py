import taxgermany as tg
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import streamlit as st

st.write("# A simple income tax")

st.write('For detailed discussion see my [ blog post ]( https://knut-heidemann.net/post/tax-reform/ )(German).')

#st.write("**Formula for computing net income:**")
st.latex(r'''
	n(b) \equiv	\begin{cases}
	M, &\text{for } b<M,\\\
	M \left[1+(k-1)\tanh\left(\frac{b-M}{\alpha M}\right)\right], \alpha \in \mathbb R, &\text{for } b \geq M.
	\end{cases}''')

st.write("$n$: net income, $b$: gross income, $M$: basic net income")

k = st.slider(r'$\boldsymbol k$ (max/min net income)', value=5, min_value=1, max_value=30)
alpha = st.slider(r'$\boldsymbol\alpha$ (scaling of transition)', min_value=1.0, max_value=50.0, value=5.0, step=0.1)

#st.sidebar.write(r'$\boldsymbol M = 12.000$')

M = 12000

B = np.linspace(1,3e5,100)
N = tg.netto_vectorized(B,alpha,k)/M

N_status_quo = tg.netto_ger_vectorized(B)/M
N_linke = tg.netto_linke_vectorized(B)/M

data = pd.DataFrame(
        {
            'gross income': B/M,
            'net income (Eq. above)': N,
            'net income (status quo)': N_status_quo,
            'net income (die Linke)': N_linke,
            'gross = net income': B/M
        }
    )

st.line_chart(data, x='gross income', y=['net income (Eq. above)','net income (status quo)','net income (die Linke)', 'gross = net income'], x_label='gross income / M', y_label='net income / M')
#plt.plot(B/1000, tg.netto_vectorized(B,12.2,10)/1000,label=r"mein Vorschlag", lw=2)


#B_frame = pd.read_csv('/home/kheidemann/ownCloud/projects/tax-reform/data/verteilung-bruttomonatsverdienste-vollzeitbeschaeftigung-cleansed.csv', sep=',')
#B_frame.Mittelwert *= 12 # yearly income not monthly
#B_frame.Anteil *= 0.01 # not in %
#
#brutto = B_frame['Mittelwert']
#mass = B_frame["Anteil"]
#netto_now = tg.netto_ger_vectorized(brutto)
#netto_dist = tg.netto_vectorized(brutto, alpha, k)
#gini_now = tg.Gini(netto_now, mass)
#gini = tg.Gini(netto_dist, mass)
#
#st.sidebar.write("**Gini index now:**")
#st.sidebar.write(gini_now)
#
#st.sidebar.write("**Gini index reformed:**")
#st.sidebar.write(gini)
#
#tax_now = tg.tax_ger_vectorized(brutto)
#revenue_now = np.dot(tax_now, mass)
#revenue = tg.reformed_tax_revenue(brutto, mass, alpha, k)
#
#st.sidebar.write("**Change in tax revenue:**")
#st.sidebar.write(((revenue-revenue_now)/revenue_now))


