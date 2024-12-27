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

print(df.loc[df['Yıl'] == 2009])


"""
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

def prepare_gender_literacy_diff_heatmap(df):
    # Kadın ve erkek okuma yazma bilmeyen sayılarını al
    female_illiteracy = df.loc[:, ('Okuma yazma bilmeyen', 'Kadın')]
    male_illiteracy = df.loc[:, ('Okuma yazma bilmeyen', 'Erkek')]
    years = df.loc[:, ('Yıl', '')]
    city_names = df.loc[:, ('İl Adı', '')]

    # Fark hesaplama
    illiteracy_diff = female_illiteracy - male_illiteracy

    # Veri çerçevesi oluşturma
    diff_df = pd.DataFrame({
        'Yıl': years,
        'İl Adı': city_names,
        'Fark': illiteracy_diff
    })

    # Pivot tablo oluşturma
    pivot_data = diff_df.pivot_table(
        index='İl Adı', 
        columns='Yıl', 
        values='Fark', 
        aggfunc='first'
    )

    return pivot_data

def create_gender_literacy_diff_heatmap(data):
    plt.figure(figsize=(20, 15))
    
    # NaN değerleri 0 ile doldur
    data_filled = data.fillna(0)
    
    # Renk sınırlarını hesapla (daha keskin bir görünüm için)
    vabs_max = np.abs(data_filled).max().max()
    
    # Isı haritasını çizme (gelişmiş renklendirme)
    sns.heatmap(
        data_filled, 
        cmap='coolwarm',  # Daha canlı bir renk paleti
        center=0,         # Sıfır merkezli renklendirme
        annot=True,      # Değerleri gösterme
        cbar_kws={
            'label': 'Kadın-Erkek Okuma Yazma Bilmeyen Farkı',
            'format': '%d'
        },
        xticklabels=True,
        yticklabels=True,
        vmin=-vabs_max,   # Minimum değeri simetrik yap
        vmax=vabs_max,    # Maksimum değeri simetrik yap
        robust=True,      # Aykırı değerlerden etkilenmeyi azalt
    )
    
    plt.title('İllere Göre Kadın-Erkek Okuma Yazma Bilmeyen Farkı', fontsize=16)
    plt.xlabel('Yıllar', fontsize=12)
    plt.ylabel('İller', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.show()

# Ek görselleştirme seçenekleri
def create_alternative_visualizations(data):
    # 1. Mutlak fark bar plot
    plt.figure(figsize=(20, 10))
    data.abs().mean().plot(kind='bar')
    plt.title('Yıllara Göre Ortalama Mutlak Okuma Yazma Farkı')
    plt.xlabel('Yıllar')
    plt.ylabel('Mutlak Fark')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

    # 2. Farkın zaman içindeki değişimi
    plt.figure(figsize=(20, 10))
    data.mean().plot(kind='line', marker='o')
    plt.title('Yıllara Göre Ortalama Okuma Yazma Farkı')
    plt.xlabel('Yıllar')
    plt.ylabel('Ortalama Fark')
    plt.axhline(y=0, color='r', linestyle='--')
    plt.tight_layout()
    plt.show()

# Isı haritasını oluştur
try:
    # Veri hazırlama
    gender_literacy_diff = prepare_gender_literacy_diff_heatmap(df)
    
    # Isı haritasını çizme
    create_gender_literacy_diff_heatmap(gender_literacy_diff)
    
    # Alternatif görselleştirmeler
    create_alternative_visualizations(gender_literacy_diff)

except Exception as e:
    print(f"Hata oluştu: {e}")

# Ek bilgilendirme
print("\nFark İstatistikleri:")
print(gender_literacy_diff.describe())

"""



import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class EducationAnalysis:
    def __init__(self, dataframe):
        # Yıl sütununu integer'a çevirme
        dataframe.loc[:, ('Yıl', '')] = pd.to_numeric(dataframe.loc[:, ('Yıl', '')], errors='coerce')
        
        self.df = dataframe
        self.categories = [
            'Genel toplam', 
            'Okuma yazma bilmeyen', 
            'Okuma yazma bilen fakat bir okul bitirmeyen',
            'İlkokul', 
            'İlköğretim', 
            'Ortaokul ve dengi meslek',
            'Lise ve dengi meslek', 
            'Yüksekokul veya fakülte', 
            'Yüksek lisans', 
            'Doktora', 
            'Bilinmeyen'
        ]

    def gender_education_distribution(self):
        """
        Yıllara göre cinsiyet bazında eğitim dağılımını görselleştirir
        """
        plt.figure(figsize=(20, 10))
        
        # Son yılı belirle
        last_year = self.df.loc[:, ('Yıl', '')].max()
        
        # Son yılın verisini al
        last_year_data = self.df[self.df.loc[:, ('Yıl', '')] == last_year]
        
        # Her kategori için erkek ve kadın oranlarını hesapla
        male_percentages = []
        female_percentages = []
        
        for category in self.categories:
            male_total = last_year_data.loc[:, (category, 'Erkek')].sum()
            female_total = last_year_data.loc[:, (category, 'Kadın')].sum()
            
            male_percentages.append(male_total)
            female_percentages.append(female_total)
        
        # Gruplandırılmış bar plot
        x = np.arange(len(self.categories))
        width = 0.35
        
        plt.bar(x - width/2, male_percentages, width, label='Erkek', color='blue', alpha=0.7)
        plt.bar(x + width/2, female_percentages, width, label='Kadın', color='red', alpha=0.7)
        
        plt.title(f'{last_year} Yılı Eğitim Kategorilerinde Cinsiyet Dağılımı', fontsize=16)
        plt.xlabel('Eğitim Kategorileri', fontsize=12)
        plt.ylabel('Toplam Nüfus', fontsize=12)
        plt.xticks(x, self.categories, rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
        plt.show()

    def education_trend_analysis(self):
        """
        Eğitim kategorilerinin yıllara göre trend analizi
        """
        plt.figure(figsize=(20, 10))
        
        for category in self.categories:
            # Her yıl için toplam değeri hesapla
            yearly_totals = self.df.groupby(('Yıl', ''))[[(category, 'Toplam')]].sum().squeeze()
            
            plt.plot(yearly_totals.index, yearly_totals.values, 
                    label=category, marker='o')
        
        plt.title('Eğitim Kategorilerinin Yıllara Göre Değişimi', fontsize=16)
        plt.xlabel('Yıllar', fontsize=12)
        plt.ylabel('Toplam Nüfus', fontsize=12)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.show()

    def illiteracy_gender_gap(self):
        """
        Okuma yazma bilmeyen nüfusun cinsiyet farkını görselleştirir
        """
        # Okuma yazma bilmeyen kadın ve erkek sayıları
        female_illiteracy = self.df.loc[:, ('Okuma yazma bilmeyen', 'Kadın')].astype(float)
        male_illiteracy = self.df.loc[:, ('Okuma yazma bilmeyen', 'Erkek')].astype(float)
        years = self.df.loc[:, ('Yıl', '')].astype(float)
        cities = self.df.loc[:, ('İl Adı', '')]

        # Fark hesaplama
        illiteracy_diff = female_illiteracy - male_illiteracy

        # Isı haritası
        plt.figure(figsize=(20, 15))
        diff_df = pd.DataFrame({
            'Yıl': years,
            'İl': cities,
            'Fark': illiteracy_diff
        })

        # Pivot tablo oluşturma ve NaN değerlerini 0 ile doldurma
        pivot_data = diff_df.pivot_table(
            index='İl', 
            columns='Yıl', 
            values='Fark', 
            aggfunc='first'
        ).fillna(0)

        # Veri türünü float'a çevirme
        pivot_data = pivot_data.astype(float)

        sns.heatmap(
            pivot_data, 
            cmap='RdBu_r', 
            center=0, 
            cbar_kws={'label': 'Kadın-Erkek Okuma Yazma Bilmeyen Farkı'}
        )
        
        plt.title('İllere Göre Okuma Yazma Bilmeyen Nüfus Cinsiyet Farkı', fontsize=16)
        plt.tight_layout()
        plt.show()

    def percentage_analysis(self):
        """
        Eğitim kategorilerinin yüzdesel dağılımını hesaplar
        """
        # Son yılı belirle
        last_year = self.df.loc[:, ('Yıl', '')].max()
        
        # Son yılın verisini al
        last_year_data = self.df[self.df.loc[:, ('Yıl', '')] == last_year]
        
        # Toplam nüfus
        total_population = last_year_data.loc[:, ('Genel toplam', 'Toplam')].sum()
        
        # Her kategori için yüzde hesaplama
        percentages = {}
        for category in self.categories:
            category_total = last_year_data.loc[:, (category, 'Toplam')].sum()
            percentages[category] = (category_total / total_population) * 100
        
        # Pasta grafiği
        plt.figure(figsize=(15, 10))
        plt.pie(
            list(percentages.values()), 
            labels=list(percentages.keys()), 
            autopct='%1.1f%%'
        )
        plt.title(f'{last_year} Yılı Eğitim Kategorileri Yüzdesel Dağılımı', fontsize=16)
        plt.tight_layout()
        plt.show()

"""# Analiz çalıştırma
analysis = EducationAnalysis(df)
analysis.gender_education_distribution()
analysis.education_trend_analysis()
analysis.illiteracy_gender_gap()
analysis.percentage_analysis()

"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import numpy as np

def create_animated_pie_chart(df, output_format='mp4'):
    """
    2008-2023 yılları arasındaki eğitim seviyelerinin dağılımını
    hareketli bir pasta grafiği olarak gösterir ve dosyaya kaydeder.
    
    Parametreler:
    - df: Pandas DataFrame, eğitim verileri içermelidir.
    - output_format: 'mp4' veya 'gif', çıktı dosya formatı.
    """
    # Çok seviyeli sütun başlıklarını düzleştir
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in df.columns]
    
    # 'Yıl' sütununu algıla
    year_column = [col for col in df.columns if 'Yıl' in col]
    if not year_column:
        raise KeyError("Veri setinde 'Yıl' sütunu bulunamadı.")
    year_column = year_column[0]
    
    # Eğitim seviyeleri sütunlarını algıla (_Toplam içeren sütunları seç)
    edu_columns = [col for col in df.columns if col.endswith('_Toplam') and any(level in col for level in [
        'İlkokul', 'İlköğretim', 'Ortaokul', 'Lise', 'Yüksekokul', 'Yüksek lisans', 'Doktora'
    ])]
    
    if not edu_columns:
        raise ValueError("Veri setinde uygun eğitim sütunları bulunamadı.")
    
    # Yıllar ve verileri hazırlama
    years = df[year_column].unique()
    yearly_data = {
        year: df[df[year_column] == year][edu_columns].sum()
        for year in years
    }
    
    # Boş yılları filtrele
    valid_years = {year: data for year, data in yearly_data.items() if data.sum() > 0}
    if not valid_years:
        raise ValueError("Geçerli veri içeren hiçbir yıl bulunamadı.")
    
    # Pasta grafiği için güncelleme fonksiyonu
    fig, ax = plt.subplots(figsize=(10, 7))
    
    def update_pie(frame):
        ax.clear()
        year = list(valid_years.keys())[frame]
        data = valid_years[year]
        data = data[data > 0]  # Sıfır değerleri kaldır
        
        if data.empty:
            return
        
        labels = [label.replace('_Toplam', '') for label in data.index.tolist()]
        explode = [0.05] * len(data)  # Dilimleri ayırmak için
        
        wedges, texts, autotexts = ax.pie(
            data,
            labels=labels,
            autopct='%1.1f%%',
            startangle=140,
            explode=explode
        )
        
        ax.set_title(f"Eğitim Seviyeleri Dağılımı ({year})", fontsize=16)
        for text in autotexts:
            text.set_color('white')
    
    # Animasyonu oluştur
    anim = animation.FuncAnimation(
        fig,
        update_pie,
        frames=len(valid_years),
        interval=750,  # Geçiş süresi (milisaniye)
        repeat=False
    )
    
    # Animasyonu göster
    plt.show()
    
    # Animasyonu bir dosyaya kaydet
    if output_format == 'mp4':
        anim.save('animated_pie_chart.mp4', writer='ffmpeg')
        print("Animasyon MP4 formatında kaydedildi: animated_pie_chart.mp4")
    elif output_format == 'gif':
        anim.save('animated_pie_chart.gif', writer='pillow')
        print("Animasyon GIF formatında kaydedildi: animated_pie_chart.gif")
    else:
        raise ValueError("Geçersiz dosya formatı. 'mp4' veya 'gif' seçin.")


create_animated_pie_chart(df, output_format='mp4')