#pip install bs4
import requests
import requests

#ne pas afficher les erreur
from requests.packages import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def cal_dju_costic(Tmin,Tmax):
    if Tmax<=18:
        dju=18-(Tmin+Tmax)/2
    if Tmin>=18:
        dju=0
    if Tmin<18 and Tmax>18:
        a=Tmax-Tmin
        b=(18-Tmin)/(Tmax-Tmin)
        dju=a*b*(0.08+0.42*b)
    
    return dju

def MeteoCiel_dayScraping(code2,annee2,mois2,jour2):

    url='https://www.meteociel.fr/temps-reel/obs_villes.php?jour2='+str(jour2)+'&mois2='+str(mois2-1)+'&annee2='+str(annee2)+'&code2='+str(code2)
    #print('url',url)

##########récupérer les données en format HTML
    response = requests.get(url,verify=False)
    soup = BeautifulSoup ( response.content , "html.parser" )
    soup.prettify()
    #print(soup.findAll('table', attrs={'bgcolor': "#EBFAF7"}))
    if soup.findAll('table', attrs={'bgcolor': "#EBFAF7"})==[]:
        print("pas de tableau de données")
        df=pd.DataFrame([])
    else:
        for table in soup.findAll('table', attrs={'bgcolor': "#EBFAF7"}):
            #print("TABLE",table)
            col=-1
            col_array = []
            columns=[]
            
            #print(table.text)
            for tr in table.findAll('tr'):
                #print(tr.text)
                col=col+1
                #print("col",col)
                
                row=-1
                row_array = []
                
                for td in tr.findAll('td'):
                    row=row+1
                    #print("row",row)
                    #print(td.text)

                    if row!=8 and col!=0 :
                        row_array.append(td.text)
                    if col==0:
                        columns.append(td.text)
                
                #print(row_array)

                if col!=0:
                    col_array.append(row_array)
                    
                
                #ligne_tr=td.text
                #print(ligne_tr)

                
        #print("col_array",col_array)
        #print("entête",columns)

    ###############récupérer le tableau sous forme d'un DataFrame
        df=pd.DataFrame(col_array,columns=columns)
        #print("df_brut:",df)
    ############### Transformer le tableau en colonnes de valeurs et unités
        df[['Visi','Unité Visi']] = df['Visi'].str.split(' ',expand=True)
        df[['Heurelocale','Unité Heurelocale']] = df['Heurelocale'].str.split(' ',expand=True)

        #ajouter un 0 devant les heures
        df['Heurelocale']=df.apply(lambda row: ('0'+row.Heurelocale) if int(row.Heurelocale) <= 9 else row.Heurelocale, axis = 1)
        


        try:
            df[['Température','Unité Température']] = df['Température'].str.split(' ',expand=True)
        except:
            df[['Température','Unité Température']] = df['Température'].str.split(' ',expand=True).drop(columns=[2])
        df['Température'] = df['Température'].str.strip()
    

        try:
            df[['Pression','Unité Pression']] = df['Pression'].str.split(' ',expand=True)
        except:
            df[['Pression','Unité Pression']] = df['Pression'].str.split(' ',expand=True).drop(columns=[2])

        df[['Vent','rafales']] = df['Vent (rafales)'].str.split('(',expand=True)
        
        df[['Vent','Unité Vent']] = df['Vent'].str.split(' ',expand=True).drop(columns=[2,3])
        df[['rafales','Unité rafales']] = df['rafales'].str.split(' ',expand=True)
        df[['Unité rafales']] = df['Unité rafales'].str.split(')',expand=True).drop(columns=[1])
        df=df.drop(columns=['Vent (rafales)'])


        df["Timestamp"]=df.apply(lambda row: datetime(annee2,mois2, jour2, hour=int(row.Heurelocale), minute=0, second=0, microsecond=0)  , axis = 1)
        df.set_index('Timestamp', inplace=True)
        df=df.sort_index(ascending=True)

        #df.to_excel("output_meteociel.fr.xlsx")
        #print(df)


    return df

#############"aller chercher toutes les données historique########################
def MeteoCiel_histoScraping(code2,date_debut,date_fin):
    from tqdm import tqdm
    from datetime import datetime

    df_histo=pd.DataFrame([])
    date_reference=datetime(1970,1,1,1,0,0,0)
    Timestamp_debut=round((date_debut-date_reference).total_seconds())
    Timestamp_fin=round((date_fin-date_reference).total_seconds())

    #for annee2 in range(date_debut.year, date_fin.year+1):
    for current_Timestamp in tqdm(range(Timestamp_debut, Timestamp_fin,3600*24),desc='Evolution du temps de scraping'):
        current_date=datetime.fromtimestamp(current_Timestamp)
        try:
            df=MeteoCiel_dayScraping(code2,current_date.year,current_date.month,current_date.day)
            #print("df=====================",df)
            df_histo=df_histo.append(df)       
        except:
            print("erreur dans le scraping de la journée :"+str(current_date))
                
        #print("df_histo=====",df_histo)
        
    print("fin du scrapping...........")


    date='Timestamp'
    # Convert the column to numeric with errors='coerce'
    df_histo['Température'] = pd.to_numeric(df_histo['Température'], errors='coerce')
    df_histo = df_histo.dropna(subset=['Température'])
    # Identify the rows containing NaN values
    #problematic_rows = df[df['Température'].isna()]
    # Print the problematic rows
    #print(problematic_rows)

    #créer un index pour l'agregation
    #df_histo['date_only'] = df_histo[date].dt.strftime('%Y-%m-%d')
    df_histo['date_only']=df_histo.index
    df_histo['month_only']=df_histo.index
    df_histo['year_only']=df_histo.index

    df_histo['date_only'] =df_histo['date_only'].apply(lambda x: x.replace(hour=0, minute=0, second=0))
    #df_histo['month_only'] = df_histo[date].dt.strftime('%Y-%m')
    df_histo['month_only'] =df_histo['date_only'].apply(lambda x: x.replace(day=1,hour=0, minute=0, second=0))
    #df_histo['year_only'] = df_histo[date].dt.strftime('%Y')
    df_histo['year_only'] =df_histo['date_only'].apply(lambda x: x.replace(month=1,day=1,hour=0, minute=0, second=0))

    print(df_histo.head())
    #calcul de la table jour
    df_day = df_histo.groupby('date_only').agg({'Température': ['mean','min', 'max']})
    df_day['DJU'] = df_day.apply(lambda row: cal_dju_costic(row[('Température',  'min')], row[('Température',  'max')]), axis=1)
    df_day['month_only']=df_histo.groupby('date_only').agg({'month_only': ['first']})
    df_day['year_only']=df_histo.groupby('date_only').agg({'year_only': ['first']})
    
    print(df_day.columns)

    #calcul de la table mois
    df_month= df_day.groupby('month_only').agg({('DJU',''): ['sum']})
    df_month['Température']=df_histo.groupby('month_only').agg({'Température': ['mean']})

    print(df_month)

    #calcul de la table année
    df_year= df_day.groupby('year_only').agg({('DJU',''): ['sum']})
    df_year['Température']=df_histo.groupby('year_only').agg({'Température': ['mean']})

    print(df_year)
   

 
    return df_histo,df_day, df_month, df_year
    






####################### utiliser la fonction############################

# jour2=7
# mois2=3
# annee2=2023
# code2=7471 #station météo

# df3=MeteoCiel_dayScraping(code2,annee2,mois2,jour2)
# # imprimer le dataFrame
# df3.to_excel("Meteociel.fr_station_"+str(code2)+"_"+str(annee2)+str(('0'+str(mois2)) if int(mois2) <= 9 else mois2)+str(('0'+str(jour2)) if int(jour2) <= 9 else jour2)+".xlsx")
# print("df3=",df3)

##################################################################################
