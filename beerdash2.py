# %%
import numpy as np
import plotly.graph_objects as go
import seaborn as sns 
import pandas as pd 
import matplotlib.pyplot as plt
import plotly.express as px
import requests
import pandas as pd
import streamlit as st
import json
from streamlit_folium import st_folium

# !pip install folium
# !pip install geopandas
import geopandas as gpd
import folium

st.set_page_config(layout='wide')

# zorgen dat mijn kolommen niet gelimiteerd zijn
pd.set_option('display.max_columns', None)

##################################################################

# Alle biertjes inlezen. Dit moet straks vervangen worden door de code om de API te gebruiken. 
df = pd.read_csv('Allebiertjes.csv')

# FILTEREN OP AMERIKAANSE BIERTJES
amerikaansbier = df[df['country']=='United States']

# Bekijken hoeveel biertjes er per regio zijn. Kan ook weg. 1452 verschillende locaties in de kolom 'region'. Hier willen we staten van maken.
amerikaansbier.value_counts('region')

##################################################################

# ##################################################################
# 
# DATA CLEANEN. NIEUWE KOLOMMEN MAKEN 
# Nieuwe kolom 'state' uit 'region'
# De rating kolom opschonen. Strings er uit
# De ABV kolom opschonen
# De IBU kolom opschonen
# 
# ##################################################################

# Nieuwe kolom 'state' toevoegen die de staat haalt uit de kolom 'region'.

# Functie om de staat te extraheren
def extract_state(region):
    parts = region.split(", ")
    if len(parts) > 1:
        return parts[-1]  # Pak het laatste deel (de staat)
    else:
        return region  # Het is al een staat

# Nieuwe kolom toevoegen met alleen de staat
amerikaansbier["state"] = amerikaansbier["region"].apply(extract_state)

statenlijst = amerikaansbier.value_counts('state')

city_to_state = {
    "Baltimore": "Maryland",
    "Bellingham": "Washington",
    "Boulder": "Colorado",
    "Braintree": "Massachusetts",
    "Brooklyn": "New York",
    "Cambridge": "Massachusetts",
    "Canton": "Ohio",
    "Cape May": "New Jersey",
    "Centennial": "Colorado",
    "Charlotte": "North Carolina",
    "Chester": "Pennsylvania",
    "Cincinnati": "Ohio",
    "Colorado Springs": "Colorado",
    "Columbus": "Ohio",
    "D.C.": "District of Columbia",
    "Des Moines": "Iowa",
    "Detroit": "Michigan",
    "Devon": "Pennsylvania",
    "Denver": "Colorado",
    "Duluth": "Minnesota",
    "Everett": "Washington",
    "Framingham": "Massachusetts",
    "Goliad": "Texas",
    "Hampshire County": "Massachusetts",
    "Hartford": "Connecticut",
    "Honolulu": "Hawaii",
    "Houston": "Texas",
    "Iowa City": "Iowa",
    "Itasca": "Illinois",
    "Jersey City": "New Jersey",
    "Las Vegas": "Nevada",
    "Lexington": "Kentucky",
    "Lincolnshire": "Illinois",
    "Los Angeles": "California",
    "Louisville": "Kentucky",
    "Maryland Heights": "Missouri",
    "Memphis": "Tennessee",
    "Miami": "Florida",
    "Michigan City": "Indiana",
    "Milwaukee": "Wisconsin",
    "Monmouth": "Illinois",
    "Nashville": "Tennessee",
    "New Avalon": "New York",
    "Oakland": "California",
    "Phoenix": "Arizona",
    "Pittsburgh": "Pennsylvania",
    "Plymouth": "Massachusetts",
    "Portland": "Oregon",
    "Rutland": "Vermont",
    "Sacramento": "California",
    "San Francisco": "California",
    "Saint Paul": "Minnesota",
    "Santa Barbara": "California",
    "San Diego": "California",
    'Seattle': "Washington",
    "Scottsdale": "Arizona",
    "Somerville": "Massachusetts",
    "Springfield": "Illinois",
    "St. Charles": "Missouri",
    "St. Louis": "Missouri",
    "St. Paul": "Minnesota",
    "Tacoma": "Washington",
    "Tampa": "Florida",
    "Tulsa": "Oklahoma",
    "Villa Park": "Illinois",
    "Washington D.C.": "District of Columbia",
    "West Kill": "New York",
    "Wichita": "Kansas",
    "Bradley Brew Unicorn Girls American Pale Ale": "California",
    "New Avalon Brewing Company": "New York",
    "New York City": "New York",
    "Dallas": "Texas",
    "Salt Lake City": "Utah",
    "New Orleans": "Louisiana",
    "Virginia Beach": "Virginia",
    "Oklahoma City": "Oklahoma",
    "Kansas City":"Missouri",
    "Boston": "Massachusetts",
    "Minneapolis": "Minnesota",
    "Indianapolis": "Indiana",
    "Philadelphia": "Pennsylvania",
    "Atlanta": "Georgia",
    "Chicago": "Illinois"
}


# Functie om de juiste staat te vinden
def map_to_state(location):
    return city_to_state.get(location, location)  # Vervang stad door staat als die in de mapping staat

# Pas de functie toe
amerikaansbier["state"] = amerikaansbier["state"].apply(map_to_state)

valid_states = {
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut",
    "Delaware", "District of Columbia", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois",
    "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland",
    "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana",
    "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York",
    "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
    "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah",
    "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
}

# Filter de data om alleen rijen te behouden met een geldige staat
amerikaansbier = amerikaansbier[amerikaansbier["state"].isin(valid_states)]

# Nu zijn er nog maar 50 staten (en DC), dus 51 unique values in 'states', over.

# ##################################################################

# Clean up de rating kolom

amerikaansbier["rating"] = amerikaansbier["rating"].astype(str).str.extract(r'(\d+\.?\d*)')[0].astype(float)

# ##################################################################
# Clean up de IBU kolom

amerikaansbier["ibu"] = amerikaansbier["ibu"].astype(str)

# Filter alleen numerieke waarden en zet negatieve getallen om naar positieve integers
amerikaansbier = amerikaansbier[amerikaansbier["ibu"].str.match(r"^-?\d+$")]  # Houd alleen integer getallen (positief of negatief)
amerikaansbier["ibu"] = amerikaansbier["ibu"].astype(int).abs()  # Zet om naar integer en neem absolute waarde

##################################################################
# Clean up de ABV (alcoholpercentage) kolom

# Verwijder alles behalve getallen en de punt, zet om naar float
amerikaansbier["abv"] = (amerikaansbier["abv"].astype(str)                           # Zorg dat alles een string is
    .str.extract(r"(\d+\.\d+)")            # Haal alleen numerieke waarden met een punt
    .astype(float)                         # Zet om naar float
)

# Verwijder rijen waar 'abv' NaN is (die konden niet worden geconverteerd)
amerikaansbier = amerikaansbier.dropna(subset=["abv"])

# Resultaat tonen
# amerikaansbier["abv"].value_counts().to_csv('1234.csv')


##################################################################
# 
# PLOTJES: WORDEN NIET GEBRUIKT IN DE APP...
# 
##################################################################


# %%
# Plotje maken met de rating per staat
# De NaNs moeten gedropt.
usarating = amerikaansbier.dropna(subset=["rating"])

rating_staat = usarating.groupby('state')['rating'].mean().sort_values(ascending=False).index

usarating_sort_rating = usarating.sort_values('rating')

sns.barplot(data=usarating_sort_rating,x='state',y='rating',order=rating_staat)
plt.xticks(rotation=90)

plt.show()

# %%
# Plotje die de gemiddelde IBU waarde per staat laat zien.

iburating = amerikaansbier.dropna(subset = ['ibu'])

ibu_staat = iburating.groupby('state')['ibu'].mean().sort_values(ascending=False).index

usaibu_sort_ibu = iburating.sort_values('ibu')

sns.barplot(data=usaibu_sort_ibu,x='state',y='ibu',order=ibu_staat)
plt.xticks(rotation=90)

plt.show()

##################################################################
# 
# 3 KAARTEN MAKEN: WORDEN WEL GEBRUIKT IN DE APP
# HIERONDER WORDEN EERST DE JUISTE VARIABELEN GEMAAKT OM 
# DE KAARTEN TE KUNNEN MAKEN:
#
#  
##################################################################

# %%
statenkaart = gpd.read_file('us-states.json')
print(statenkaart.head())

# Maak een variabele met de gemiddelde rating per staat
ratingstaat = amerikaansbier.groupby('state')['rating'].agg('mean').round(1)

# Maak een variabele met de gemiddelde IBU per staat
IBUstaat = amerikaansbier.groupby('state')['ibu'].agg('mean').round(0)

# Maak een variabele met de hoeveelheid biertjes met een rating per staat
aantalbiermetrating = amerikaansbier.groupby('state')['rating'].count()

# Maak een variabele met de hoeveelheid biertjes met een IBUscore per staat
aantalbiermetIBU= amerikaansbier.groupby('state')['ibu'].count()

# Maak een variabele met het aantal biertjes per staat in de lijst.
aantalbierperstaat = amerikaansbier.groupby('state').size().reset_index(name='aantal')

# Je wilt de 2 nieuwe variabelen samenvoegen met polygonenkaart. Daarvoor moeten de kolommen hetzelfde heten.
# Het makkelijkst is om de naam van de kolom in de  GeoJson file te veranderen van 'name' naar 'state'
statenkaart = statenkaart.rename(columns={"name": "state"})

# Nu kun je die file samenvoegen met de aangemaakte variabelen. 
# Je krijgt dan 2 kolommen extra met in de ene de rating per staat en in de andere het aantal biertjes met een rating.
# De kolommen moet je nog weer even een logische naam geven, anders heten ze rating_x en rating_y.
ratingkaart = statenkaart.merge(ratingstaat, on='state')
ratingkaart = ratingkaart.merge(aantalbiermetrating, on='state')
ratingkaart = ratingkaart.rename(columns={"rating_x": "rating", "rating_y": 'aantal'})

IBUkaart = statenkaart.merge(IBUstaat, on='state')
IBUkaart = IBUkaart.merge(aantalbiermetIBU, on='state')
IBUkaart = IBUkaart.rename(columns={"ibu_x": "IBU", "ibu_y": 'aantal'})

aantalkaart = statenkaart.merge(aantalbierperstaat, on='state')
print(aantalkaart.columns)

# ratingkaart['rating'] = ratingkaart['rating'].fillna(0) # Sommige staten hebben geen biertjes met een rating. Ik kies er voor om die gewoon niet te tekenen. 
print(ratingkaart.columns)
# print(ratingkaart)
print(IBUkaart.columns)
# print(IBUkaart)

##################################################################
# 
# KAARTJE 1: RATINGPLOT
# 
##################################################################
#
# Center point for USA
USA = [37.0902, -95.7129]

# Create map
RatingPlot = folium.Map(location=USA, zoom_start=5)

# Add Choropleth layer
folium.Choropleth(
    geo_data=ratingkaart,
    name='geometry',
    data=ratingkaart,
    columns=['state', 'rating'],
    key_on='feature.properties.state',
    fill_color='YlOrRd',
    fill_opacity=0.5,
    line_opacity=1,
    legend_name='Average beer rating per state'
).add_to(RatingPlot)

# Function to style polygons (transparent fill, but visible border)
def style_function(feature):
    return {
        "fillColor": "transparent",  # Maakt de polygon transparant
        "color": "black",  # Zwarte randen zodat staten zichtbaar blijven
        "weight": 1,  # Dunne randen
        "fillOpacity": 0,  # Geen kleurvulling
    }

# Voeg interactieve polygonen toe
folium.GeoJson(
    ratingkaart,
    name="States",
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(
        fields=["state", "rating",'aantal'],
        aliases=["State:", "Average Beer Rating:", 'No of Rated Beers:'],
        localize=True,
        sticky=False
    ),
    popup=folium.GeoJsonPopup(
        fields=["state", "rating",'aantal'],
        aliases=["State:", "Average Beer Rating:", 'No of Rated Beers:']
    )
).add_to(RatingPlot)

# Add LayerControl
folium.LayerControl().add_to(RatingPlot)

# Display the map
#display(RatingPlot)

##################################################################
# 
# KAARTJE 2: IBUPLOT
# 
##################################################################
# Create map
IBUplot = folium.Map(location=USA, zoom_start=5)

# Add Choropleth layer
folium.Choropleth(
    geo_data=IBUkaart,
    name='geometry',
    data=IBUkaart,
    columns=['state', 'IBU'],
    key_on='feature.properties.state',
    fill_color='YlOrRd',
    fill_opacity=0.5,
    line_opacity=1,
    legend_name='Average IBU score per state'
).add_to(IBUplot)

# Function to style polygons (transparent fill, but visible border)
def style_function(feature):
    return {
        "fillColor": "transparent",  # Maakt de polygon transparant
        "color": "black",  # Zwarte randen zodat staten zichtbaar blijven
        "weight": 1,  # Dunne randen
        "fillOpacity": 0,  # Geen kleurvulling
    }

# Voeg interactieve polygonen toe
folium.GeoJson(
    IBUkaart,
    name="States",
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(
        fields=["state", "IBU",'aantal'],
        aliases=["State:", "Average IBU Score:", 'No of different beers:'],
        localize=True,
        sticky=False
    ),
    popup=folium.GeoJsonPopup(
        fields=["state", "IBU",'aantal'],
        aliases=["State:", "Average IBU Score:", 'No of different beers:']
    )
).add_to(IBUplot)

# Add LayerControl
folium.LayerControl().add_to(IBUplot)

# Display the map
#display(IBUplot)

##################################################################
# 
# KAARTJE 3: NO OF BEERS KAARTJE
# 
##################################################################

# Create map
Aantalbierplot = folium.Map(location=USA, zoom_start=5)

# Add Choropleth layer
folium.Choropleth(
    geo_data=aantalkaart,
    name='geometry',
    data=aantalkaart,
    columns=['state', 'aantal'],
    key_on='feature.properties.state',
    fill_color='YlOrRd',
    fill_opacity=0.5,
    line_opacity=1,
    legend_name='Number of different beers per state'
).add_to(Aantalbierplot)

# Function to style polygons (transparent fill, but visible border)
def style_function(feature):
    return {
        "fillColor": "transparent",  # Maakt de polygon transparant
        "color": "black",  # Zwarte randen zodat staten zichtbaar blijven
        "weight": 1,  # Dunne randen
        "fillOpacity": 0,  # Geen kleurvulling
    }

# Voeg interactieve polygonen toe
folium.GeoJson(
    aantalkaart,
    name="States",
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(
        fields=["state", 'aantal'],
        aliases=["State:", 'No of different beers:'],
        localize=True,
        sticky=False
    ),
    popup=folium.GeoJsonPopup(
        fields=["state", 'aantal'],
        aliases=["State:", 'No of different beers:']
    )
).add_to(Aantalbierplot)

# Add LayerControl
folium.LayerControl().add_to(Aantalbierplot)

# Display the map
#display(Aantalbierplot)




##################################################################
#
# DASHBOARD BOUWEN 
# 
##################################################################

# 3 TABBLADEN 
# HET EERSTE TAB IS MEER EEN SOORT HOMEPAGE.
# HET TWEEDE TAB LAAT DE KAARTJES ZIEN.
# HET DERDE TAB LAAT DE SCATTERPLOT ZIEN.
tab1, tab2, tab3 = st.tabs(["Home of Beer", "Beer data per US State", "Find your favorite beer"])
with tab1:
    st.title("🍺 Beer List")
    st.write("In dit geweldige dashboard is data te vinden over meerdere soorten bier van over de hele wereld! Het doel is te achterhalen of we met data kunnen bekijken welk land het lekkerste biertje produceert, en wat mensen lekker vinden in een biertje.")

    st.header("Neem een kijkje in de bieren uit onze dataset! Hier bekijken we de lekkerste bieren vanuit heel Amerika. ")

with tab2:

    st.header(" HIER MOET OOK EEN LEUK VERHAALTJE KOMEN EEN TITEL EN/OF EEN KORTE INTRO VAN HET KAARTJE... ")


    # Selectbox voor keuze van de kaart
    keuze = st.selectbox("Selecteer de plot", ("Lokale biertjes per staat", "IBU score per staat", "Rating per staat"))

    # Functie om juiste kaart weer te geven
    if keuze == "Lokale biertjes per staat":
        kaart = Aantalbierplot
    elif keuze == "IBU score per staat":
        kaart = IBUplot
    elif keuze == "Rating per staat":
        kaart = RatingPlot




    # Toon de juiste kaart
    st_folium(kaart, width=1500, height=800)

    #################
    # st.plotly_chart(fig)




###################### SCATTERPLOT ######################
with tab3:

    st.header(" “Jouw Favoriete Bier Onder de Loep: Meer Bitter of Meer Alcohol?” 🔍🍻 ")


    # Unieke kleuren per staat (gesorteerd op alfabetische volgorde)
    unique_states = sorted(amerikaansbier["state"].unique())  
    state_color_map = {state: px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)] for i, state in enumerate(unique_states)}

    # ---- 1. Maak een lege container voor de grafiek ----
    graph_placeholder = st.empty()

    # ---- 2. Plaats de sliders onder de grafiek ----
    values = st.slider(
        "Selecteer een IBU-bereik", 
        int(amerikaansbier["ibu"].min()), 
        int(amerikaansbier["ibu"].max()), 
        (20, 80)
    )

    values2 = st.slider(
        "Selecteer een Alcoholpercentage", 
        float(amerikaansbier["abv"].min()), 
        float(amerikaansbier["abv"].max()), 
        (0.0, 10.0)
    )

    # ---- 3. Filter de data op basis van de slider ----
    filtered_df = amerikaansbier[
        (amerikaansbier["ibu"] >= values[0]) & (amerikaansbier["ibu"] <= values[1]) &
        (amerikaansbier["abv"] >= values2[0]) & (amerikaansbier["abv"] <= values2[1])
    ]

     # ---- 4. Maak de grafiek ----
    fig_filtered = go.Figure()

    for state in unique_states:
        df_state = filtered_df[filtered_df["state"] == state]
        
        fig_filtered.add_trace(go.Scatter(
            x=df_state["ibu"],  
            y=df_state["abv"],
            mode="markers",
            marker=dict(color=state_color_map[state]),
            name=state,  
            text=df_state.apply(lambda row: f"Naam: {row['name']}<br>Brouwer: {row['brewery']}<br>Food Pairing: {row['food_pairing']}<br>Serving Temp: {row['serving_temp_c']}°C / {row['serving_temp_f']}°F<br>IBU: {row['ibu']}<br>ABV: {row['abv']}%", axis=1),
            hoverinfo='text',
            visible="legendonly" if unique_states.index(state) >= 3 else True  # Alleen de eerste 3 staten zichtbaar bij opstarten
        ))

    # ---- 5. Pas de legenda aan ----
    fig_filtered.update_layout(
        title="Alcoholpercentage VS Bitterheid",
        xaxis_title="IBU (Bitterheid)",
        yaxis_title="ABV (Alcoholpercentage)",
        template="plotly_white",
        legend_title="State",
        legend=dict(
            orientation="h",  # Horizontale legenda
            x=0,
            y=-0.2,  # Lager zetten zodat hij niet over de grafiek valt
            xanchor="left",
            yanchor="top",
            traceorder="normal",  # Behoud alfabetische volgorde
            itemsizing="constant",
        ),
        xaxis=dict(range=[0, 100]),  
        yaxis=dict(range=[0, 18]),   
        width=800,  
        height=600  
    )

    # ---- 6. Update de lege container met de grafiek ----
    graph_placeholder.plotly_chart(fig_filtered)
