import psycopg2
import datetime
#import paho.mqtt.client as mqtt
import sam_mqtt

def bestimmeZeitwerte():
    try:
        conn = psycopg2.connect("dbname='getraenke' user='postgres' host='172.16.0.1' password='hackathon'")
        cur=conn.cursor()
        anzahl = [0, 0, 0] #Kaffee, Wasser, Cola
        zeitenMitWerten = [[],[],[]]
        query = "SELECT * FROM public.protokoll ORDER BY tstamp ASC"
        cur.execute(query)
        rows = cur.fetchall()
        #query = "SELECT EXTRACT(EPOCH FROM TSTAMP) FROM public.protokoll WHERE typ <= 3"
        #cur.execute(query)
        #times = cur.fetchall()
        for i,row in enumerate(rows):
            type, tstamp, number = row
            anzahl[type - 1] += number
            zeitenMitWerten[type - 1].append((tstamp, anzahl[type - 1]))
        print(anzahl)
        return zeitenMitWerten
    except Exception as e:
        print ("Database Error: ", e)

def bestandZuZeit(zeitListe, zeitpunkt):
    for i in range(len(zeitListe)):
        if zeitListe[i][0] > zeitpunkt:
            if i==0:
                return 0
            return zeitListe[i-1][1]
    return zeitListe[len(zeitListe)-1][1]

def bestandZuZeit2(zeitListe, zeitpunkt, getraenk):
    liste = zeitListe[getraenk]
    value = 0
    for tstamp, amount in liste:
        if(tstamp > zeitpunkt):
            return value
        value = amount
    return value

def setzeHinzufuegenAnAnfang(zeitListe):
    rueckgabe = []
    for liste in zeitListe:
        i = 1
        while i < len(liste):
            if (liste[i][1] > liste[i - 1][1]):
                for intern in range(i):
                   liste[intern] = (liste[intern][0], liste[intern][1] + liste[i][1] - liste[i - 1][1])
                del liste[i]
            i += 1
        rueckgabe.append(liste)
    return rueckgabe

def listeNachMinuten(zeitListeSortiert, messstartzeit, messendzeit):
    rueckgabe = [[], [], []]
    getraenk = 0
    for liste in zeitListeSortiert:
        zeit = messstartzeit.timestamp() // 60
        i = 0
        while i < len(liste):
            while liste[i][0].timestamp() // 60  - zeit > 1:
                if len(rueckgabe[getraenk]) == 0:
                    rueckgabe[getraenk].append(0)
                else:
                    rueckgabe[getraenk].append(liste[i][1])
                    #rueckgabe[getraenk].append(rueckgabe[getraenk][len(rueckgabe[getraenk]) - 1])
                zeit += 1
            if liste[i][0].timestamp() // 60 == liste[i - 1][0].timestamp() // 60:
                if len(rueckgabe[getraenk]) == 0:
                    rueckgabe[getraenk].append(0)
                    zeit += 1
                rueckgabe[getraenk][len(rueckgabe[getraenk]) - 1] = liste[i][1]
            else:
                #print(rueckgabe[getraenk],i)
                #if len(rueckgabe[getraenk]) == 0:
                    rueckgabe[getraenk].append(liste[i][1])
                    zeit += 1
                #else:
                #    rueckgabe[getraenk].append(rueckgabe[getraenk][len(rueckgabe[getraenk]) - 1] + liste[i][1])
                #zeit += 1
            i += 1
        getraenk += 1
    return rueckgabe

def funktionswertBerechnen(funktion, punkt):
    funktionswert = 0
    exponent = 1
    for wert in funktion:
        funktionswert += wert * punkt ** exponent
        exponent -= 1
    return funktionswert


def funktionsAbweichung(funktion, liste):
    gesamtwert = 0
    for i in range(0, len(liste)):
        #print(funktionswertBerechnen(funktion, i),liste[i],liste[0])
        gesamtwert += (funktionswertBerechnen(funktion, i) - (liste[i] - liste[0]))**2
    return gesamtwert

def gesamtAbweichung(funktion, liste):
    gesamtwert = 0
    for i in range(0, len(liste)):
        #print(funktionswertBerechnen(funktion, i),liste[i],liste[0])
        gesamtwert += ((funktionswertBerechnen(funktion, i) - (liste[i] - liste[0]))**2)**0.5
    return gesamtwert

def effizientesteFunktion(liste):
    endwert = liste[len(liste) - 1]
    startwert = liste[0]
    funktion = []
    for i in range(1):
        funktion.append((endwert - startwert) / (len(liste) ** (1 - i)))
    print(funktion)
    for iOut in range(15):
        for exponent in range(1):
            for i in range(3):
                abwStart = funktionsAbweichung(funktion, liste)
                funktion[exponent] *= 1.1
                abwMalZwei = funktionsAbweichung(funktion, liste)
                funktion[exponent] /= 1.1 ** 2
                abwDurchZwei = funktionsAbweichung(funktion, liste)
                if abwMalZwei <= abwDurchZwei:
                    funktion[exponent] *= 1.1 ** 0.5
                else:
                    funktion[exponent] *= 1.1 ** 1.5
                abwZwischenStartUndBesser = funktionsAbweichung(funktion, liste)
                if abwMalZwei <= abwDurchZwei:
                    funktion[exponent] *= 1.1 ** 0.5
                else:
                    funktion[exponent] /= 1.1 ** 0.5
                #print(funktionsAbweichung(funktion,liste),abwStart)
                if (abwStart <= abwMalZwei) & (abwStart <= abwDurchZwei) & (abwStart <= abwZwischenStartUndBesser):
                    print("o")
                    break    #1
                elif (abwMalZwei <= abwStart) & (abwMalZwei <= abwDurchZwei) & (abwMalZwei <= abwZwischenStartUndBesser):
                    funktion[exponent] *= 1.1
                    print("x")
                elif (abwDurchZwei <= abwStart) & (abwDurchZwei <= abwMalZwei) & (abwDurchZwei <= abwZwischenStartUndBesser):
                    funktion[exponent] /= 1.1
                    print("y")
                else:
                    print("z")
                    if abwMalZwei <= abwDurchZwei:
                        funktion[exponent] *= 1.1 ** 1.5
                    else:
                        funktion[exponent] /= 1.1 ** 1.5
    print(funktion)
    print(gesamtAbweichung(funktion, liste))
    return funktion

def funktionUnterNull(funktion, startpunkt, startwert):
    i = startpunkt
    while 0 == 0:
        i += 1
        if startwert - funktionswertBerechnen(funktion, i) <= 0:
            return i
        if i - startpunkt >= 60 * 24 * 7 * 6:
            return "extrem vielen"

def lineareFunktionsbestimmung(liste):
    return (liste[0]-liste[len(liste) - 1]) / len(liste)

def lineareNullstelle(steigung, startwert):
    return startwert/steigung
            
if __name__ == "__main__":
    messstartzeit, messendzeit = datetime.datetime(2017, 9, 30, 10, 20), datetime.datetime.utcnow()
    zeit = setzeHinzufuegenAnAnfang(bestimmeZeitwerte())
    liste = listeNachMinuten(zeit, messstartzeit, messendzeit)
    #print(liste)
    ausgegangen = []
    for i in range(3):
        ausgegangen.append(lineareNullstelle (lineareFunktionsbestimmung(liste[i]), liste[i][0])) 
    print(ausgegangen)
    publisher = sam_mqtt.Publisher()
    publisher.push_estimate(int(ausgegangen[0]),int(ausgegangen[1]),int(ausgegangen[2]))