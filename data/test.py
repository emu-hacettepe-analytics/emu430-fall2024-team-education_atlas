import pandas as pd

# Veri setini yükle ve tamamen boş sütunları kaldır
df = pd.read_excel('/home/mami/emu430/emu430-fall2024-team-education_atlas/data/yıllara_göre_egitim.xlsx')
df = df.dropna(axis=1, how='all')

# Yılları ve indeks aralıklarını tanımla
years = list(range(2008, 2024))  # 2008'den 2023'e kadar
index_ranges = [(1 + i * 82, 1 + (i + 1) * 82) for i in range(len(years))]

# Her yıl için alt veri çerçevelerini oluştur
yearly_data = {}
for year, (start, end) in zip(years, index_ranges):
    yearly_data[year] = df.iloc[start:end]

# İlk birkaç yılın veri çerçevelerini kontrol et
sample_years = {year: data.head(1) for year, data in list(yearly_data.items())[:3]}

# İlk iki satırı başlık olarak kullan ve eksik değerleri doldur
header1 = df.iloc[0].bfill()
header2 = df.iloc[1].bfill()

# Çok seviyeli (MultiIndex) başlıklar oluştur
df.columns = pd.MultiIndex.from_tuples(zip(header1, header2))

# İlk iki satırı kaldır ve veri setini sıfırla
df = df.iloc[2:].reset_index(drop=True)

# İlk 3 sütun için tek seviyeli başlıklar oluştur
first_three_headers = ['Yıl', 'İl Kodu', 'İl Adı']

# Ana başlıklar ve alt başlıkları tanımla
main_headers = [
    'Genel toplam', 'Okuma yazma bilmeyen', 'Okuma yazma bilen fakat bir okul bitirmeyen',
    'İlkokul', 'İlköğretim', 'Ortaokul ve dengi meslek', 'Lise ve dengi meslek',
    'Yüksekokul veya fakülte', 'Yüksek lisans', 'Doktora', 'Bilinmeyen'
]
sub_headers = ['Toplam', 'Erkek', 'Kadın']

# Çok seviyeli başlıkları oluştur
remaining_headers = [(main, sub) for main in main_headers for sub in sub_headers]

# Tüm başlıkları birleştir
final_headers = first_three_headers + remaining_headers[:df.shape[1] - len(first_three_headers)]

df.columns = pd.MultiIndex.from_tuples(
    [(header, '') if isinstance(header, str) else header for header in final_headers]
)

if isinstance(df.columns, pd.MultiIndex):
    df.columns = ['_'.join(map(str, col)).strip() if isinstance(col, tuple) else col for col in df.columns]

# Yıl sütununu bul
year_column = [col for col in df.columns if 'Yıl' in col]
if not year_column:
    raise KeyError("Veri setinde 'Yıl' sütunu bulunamadı.")
year_column = year_column[0]

print(df.columns)
print(df.head())
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from PIL import Image
import os
import plotly.express as px
import plotly.graph_objects as go
import json
print(df.columns)



def create_turkey_interactive_map(df):
    """
    Türkiye haritası üzerinde şehir bazında kadın-erkek farkını ve belirli başlıklardaki cinsiyet eşitsizlik indekslerini gösteren etkileşimli bir harita oluşturur.
    """
    city_column = [col for col in df.columns if 'İl Adı' in col][0]
    year_column = [col for col in df.columns if 'Yıl' in col][0]
    years = df[year_column].dropna().unique()
    
    # JSON dosyasını doğrula
    geojson_path = 'data/tr-cities.json'
    if not os.path.exists(geojson_path):
        raise FileNotFoundError("GeoJSON dosyası bulunamadı: data/tr-cities.json")
    
    with open(geojson_path) as f:
        geojson = json.load(f)
    
    # Veri temizliği ve eşleştirme
    df = clean_turkey_city_names(df)
    df = map_city_numbers(df, geojson)
    df = calculate_gender_inequality_indices(df)
    
    dropdown_options = [
        {'label': str(year), 'method': 'update', 'args': [{'visible': [year == y for y in years]}, {'title': f'Cinsiyet Eşitsizlik İndeksi - {year}'}]}
        for year in years
    ]
    
    fig = go.Figure()
    for year in years:
        df_year = df.loc[df[year_column] == year].copy()
        
        # Hover metni için gerekli bilgiler
        df_year['hover_text'] = (
            'Şehir: ' + df_year[city_column] + '<br>' +
            'Genel Toplam Eşitsizlik: ' + df_year['Genel toplam_Eşitsizlik'].astype(str) + '<br>' +
            'Okuma Yazma Bilmeyen: ' + df_year['Okuma yazma bilmeyen_Eşitsizlik'].astype(str) + '<br>' +
            'Yüksekokul veya Fakülte: ' + df_year['Yüksekokul veya fakülte_Eşitsizlik'].astype(str)
        )
        
        # Harita katmanı oluştur
        fig.add_trace(
            go.Choropleth(
                geojson=geojson,
                locations=df_year['CityNumber'],
                z=df_year['Genel toplam_Eşitsizlik'],
                text=df_year['hover_text'],
                hoverinfo='text',
                featureidkey='properties.number',
                colorscale='YlGnBu',  # Düşük eşitsizlik: Yeşil | Yüksek eşitsizlik: Kırmızı
                zmin=0,
                zmax=df_year['Genel toplam_Eşitsizlik'].max(),
                colorbar_title='Eşitsizlik İndeksi',
                visible=(year == years[0])
            )
        )
    
    fig.update_layout(
        title_text='Yıla Göre Cinsiyet Eşitsizlik İndeksi Haritası',
        geo=dict(
            fitbounds="locations",
            visible=True
        ),
        updatemenus=[{'buttons': dropdown_options, 'direction': 'down', 'showactive': True}]
    )
    
    fig.show()

def clean_turkey_city_names(df):
    """
    Excel veri çerçevesindeki şehir adlarını temizler ve gerekli düzeltmeleri yapar.
    """
    # 'Türkiye' ve NaN satırlarını kaldır
    df = df[~df['İl Adı_'].isin(['türkiye'])]
    df = df.dropna(subset=['İl Adı_'])
    
    # Özel şehir adı düzeltmeleri
    city_replacements = {
        'Afyonkarahisar': 'Afyon',
    }
    df['İl Adı_'] = df['İl Adı_'].replace(city_replacements)
    
    return df


def map_city_numbers(df, geojson):
    """
    Şehir adlarını şehir numaralarıyla eşleştirir.
    """
    city_mapping = {feature['properties']['name'].strip().lower(): str(feature['properties']['number']) for feature in geojson['features']}
    df['İl Adı_'] = df['İl Adı_'].str.strip().str.lower()
    df['CityNumber'] = df['İl Adı_'].map(city_mapping)
    
    # Eşleşmeyen şehirleri kontrol et
    unmatched_cities = df.loc[df['CityNumber'].isnull(), 'İl Adı_']
    if not unmatched_cities.empty:
        print("⚠️ Hâlâ eşleşmeyen şehirler var:")
        print(unmatched_cities.unique())
    
    return df


def calculate_gender_inequality_indices(df):
    """
    Her ana başlık için cinsiyet eşitsizlik indekslerini hesaplar ve veri çerçevesine ekler.
    """
    main_headers = [
        'Genel toplam', 'Okuma yazma bilmeyen', 'Okuma yazma bilen fakat bir okul bitirmeyen',
        'İlkokul', 'İlköğretim', 'Ortaokul ve dengi meslek', 'Lise ve dengi meslek',
        'Yüksekokul veya fakülte', 'Yüksek lisans', 'Doktora', 'Bilinmeyen'
    ]
    
    for header in main_headers:
        female_col = f"{header}_Kadın"
        male_col = f"{header}_Erkek"
        total_col = f"{header}_Toplam"
        
        if female_col in df.columns and male_col in df.columns and total_col in df.columns:
            df[f"{header}_Eşitsizlik"] = (df[female_col] - df[male_col]).abs() / df[total_col]
    
    return df



# Veri temizliği ve harita oluşturma
df = clean_turkey_city_names(df)
create_turkey_interactive_map(df)
