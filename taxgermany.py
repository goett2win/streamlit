import numpy as np

# tax revenue

def reformed_tax_revenue(brutto_values, mass, alpha=5, k=5):

    #tax_current = tg.tax_ger_vectorized(brutto_values)
    #revenue_current = np.dot(tax_current, mass)

    tax_reformed = tax_vectorized(brutto_values, alpha, k)
    revenue_reformed = np.dot(tax_reformed, mass)

    return revenue_reformed

# gini index

def Gini(values, mass_function): # based on section "discrete probability distribution" on wikipedia
    N = len(mass_function)
    mu = np.dot(values, mass_function)
    sum = 0
    for i in range(N):
        for j in range(N):
            delta = mass_function[i]*mass_function[j]*abs(values[i]-values[j])
            sum += delta
            #print(delta)
    G = 1.0/(2*mu)*sum
    return G
#print(N)

#new income tax introducing a maximum and minimum net income

M=12*1000. # jährlicher Mindestlohn 

def tax(x, alpha=5, k=5):
    if x<=M:
        return x-M
    else:
        return x-netto(x, alpha, k)

tax_vectorized = np.vectorize(tax)

def netto(x, alpha=5, k=5):
    if x<=M:
        return M
    else:
        return M*(1+(k-1)*np.tanh((x-M)/(alpha*M)))

netto_vectorized = np.vectorize(netto)

def tax_rate(x, alpha=5, k=5): # Durchschnittssteuersatz
    if x<=M:
        return 0.0
    else:
        return (x-netto(x, alpha, k))/x # tax(x) / x

tax_rate_vectorized = np.vectorize(tax_rate)

def grenzsteuersatz(x, alpha=5, k=5):
    z = (x-M)/(alpha*M)
    if x<=M:
        return 0.0
    else:
        #return 1-2*M/x*(1+4*np.tanh(z))+4*M/alpha*(1-np.tanh(z)*np.tanh(z))
        #return 1+(1+4*np.tanh(z))*(M/(x*x)-M/x)+4/(alpha*x)*(1-np.tanh(z)*np.tanh(z))
        return 1-4.0/alpha*(1-np.tanh(z)*np.tanh(z))

grenzsteuersatz_vectorized = np.vectorize(grenzsteuersatz)

## Function that returns the income tax currently implemented by German law (§32a Einkommensstuertarif)
#
# see: https://esth.bundesfinanzministerium.de/esth/2022/A-Einkommensteuergesetz/IV-Tarif/Paragraf-32a/inhalt.html
# b: brutto income
# returns netto income n
###

def tax_ger(b):
    M = 11604 # "Grundfreibetrag"
    Q = 17005
    P = 66760
    V = 277825
    if b <= M:
        return 0.0
    elif (M < b) & (b <= Q):
        return (922.98*(b-M)/1e4 + 1400)*(b-M)/1e4
    elif (Q < b) & (b <= P):
        return (181.19*(b-Q)/1e4 + 2397)*(b-Q)/1e4 + 1025.38
    elif (P < b) & (b <= V):
        return 0.42 * b - 10602.13
    elif V < b:
        return 0.45 * b - 18936.88

tax_ger_vectorized = np.vectorize(tax_ger)

def tax_ger_2022(b):
    M = 10347 # "Grundfreibetrag"
    Q = 14926
    if b <= M:
        return 0.0
    elif (M < b) & (b <= Q):
        return (1088.67*(b-M)/1e4 + 1400)*(b-M)/1e4
    elif (Q < b) & (b <= 58596):
        return (206.43*(b-Q)/1e4 + 2397)*(b-Q)/1e4 + 869.32
    elif (58596 < b) & (b <= 277825):
        return 0.42 * b - 9336.45
    elif 277825 < b:
        return 0.45 * b - 17671.20

def tax_ger_2019(b):
    M = 9168 # "Grundfreibetrag"
    Q = 14254
    P = 55960
    V = 265327
    if b <= M:
        return 0.0
    elif (M < b) & (b <= Q):
        return (980.14*(b-M)/1e4 + 1400)*(b-M)/1e4
    elif (Q < b) & (b <= P):
        return (216.16*(b-Q)/1e4 + 2397)*(b-Q)/1e4 + 965.58
    elif (P < b) & (b <= V):
        return 0.42 * b - 8780.9
    elif V < b:
        return 0.45 * b - 16740.68


def netto_ger(b):
    return b-tax_ger(b)

netto_ger_vectorized = np.vectorize(netto_ger)

def grenz_ger(b):
    M = 10347 # "Grundfreibetrag"
    Q = 14926
    if b <= M:
        return 0.0
    elif (M < b) & (b <= Q):
        return 2*1088.67*(b-M)/1e8 + 0.14
    elif (Q < b) & (b <= 58596):
        return 2*206.43*(b-Q)/1e8 + 0.2397
    elif (58596 < b) & (b <= 277825):
        return 0.42
    elif 277825 < b:
        return 0.45

grenz_ger_vectorized = np.vectorize(grenz_ger)
    

def grenz_linke(b):
    M = 14400 # "Grundfreibetrag"
    Q = 14926
    S = 70000 # ab hier Spitzensteuersatz
    R = 278000 # ab hier Reichensteuer
    t1 = 0.14; t2 = 0.2397; t3 = 0.53; t4 = 0.6;
    x = (t2-t1)/(Q-M); y = (t3-t2)/(S-Q);
    if b <= M:
        return 0.0
    elif (M < b) & (b <= Q):
        return t1+(b-M)*x
    elif (Q < b) & (b <= S):
        return t2+(b-Q)*y
    elif (S < b) & (b <= R):
        return 0.53
    elif R < b:
        return 0.60

grenz_linke_vectorized = np.vectorize(grenz_linke)

def tax_linke(b):
    M = 14400 # "Grundfreibetrag"
    Q = 14926
    S = 70000 # ab hier Spitzensteuersatz
    R = 278000 # ab hier Reichensteuer
    t1 = 0.14; t2 = 0.2397; t3 = 0.53; t4 = 0.6;
    x = (t2-t1)/(Q-M); y = (t3-t2)/(S-Q);
    t2Q = t1*(Q-M)+0.5*(Q-M)*(Q-M)*x # needed for continuity
    delta = t3*S-(t2*(S-Q)+0.5*(S-Q)*(S-Q)*y+t2Q)
    gamma = t4*R-(t3*R-delta)
    if b <= M:
        return -M+b
    elif (M < b) & (b <= Q):
        return t1*(b-M)+0.5*(b-M)*(b-M)*x
    elif (Q < b) & (b <= S):
        return t2*(b-Q)+0.5*(b-Q)*(b-Q)*y+t2Q
    elif (S < b) & (b <= R):
        return t3*b-delta 
 
    elif R < b:
        return t4*b-gamma

tax_linke_vectorized = np.vectorize(tax_linke)

def netto_linke(b):
    #if b <= 14400:
    #    return 14400
    #else:
    return b-tax_linke(b)

netto_linke_vectorized = np.vectorize(netto_linke)
