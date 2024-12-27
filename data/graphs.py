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

import matplotlib.pyplot as plt
import pandas as pd

def calculate_gender_inequality(df, year):
    """
    Belirli bir yıl için eğitim seviyelerinde kadın ve erkek arasındaki eşitsizliği hesaplar
    ve pasta grafiğiyle görselleştirir.
    
    Parametreler:
    - df: Pandas DataFrame, eğitim verileri içermelidir.
    - year: Analiz edilecek yıl.
    """
    # Çok seviyeli sütun başlıklarını düzleştir
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in df.columns]
    
    # 'Yıl' sütununu algıla
    year_column = [col for col in df.columns if 'Yıl' in col]
    if not year_column:
        raise KeyError("Veri setinde 'Yıl' sütunu bulunamadı.")
    year_column = year_column[0]
    
    # Yılı filtrele
    df_year = df[df[year_column] == year]
    
    # Kadın ve Erkek sütunlarını belirle
    gender_columns = {
        'Kadın': [col for col in df.columns if col.endswith('_Kadın')],
        'Erkek': [col for col in df.columns if col.endswith('_Erkek')]
    }
    
    if not gender_columns['Kadın'] or not gender_columns['Erkek']:
        raise ValueError("Kadın veya Erkek sütunları bulunamadı.")
    
    # Toplam kadın ve erkek sayısını hesapla
    total_female = df_year[gender_columns['Kadın']].sum().sum()
    total_male = df_year[gender_columns['Erkek']].sum().sum()
    
    # Toplam nüfusu hesapla
    total_population = total_female + total_male
    
    # Oranları hesapla
    female_ratio = (total_female / total_population) * 100
    male_ratio = (total_male / total_population) * 100
    
    # Pasta Grafiği
    labels = ['Kadın', 'Erkek']
    sizes = [female_ratio, male_ratio]
    colors = ['#FF69B4', '#1E90FF']
    explode = [0.05, 0.05]  # Dilimleri ayırmak için
    
    plt.figure(figsize=(10, 7))
    plt.pie(
        sizes,
        labels=labels,
        autopct='%1.1f%%',
        startangle=140,
        colors=colors,
        explode=explode
    )
    plt.title(f"{year} Yılı Eğitim Düzeyleri Kadın-Erkek Dağılımı")
    plt.show()
    
    # Sonuçları döndür
    return {
        'Kadın Toplam': total_female,
        'Erkek Toplam': total_male,
        'Kadın Oranı': female_ratio,
        'Erkek Oranı': male_ratio
    }


import matplotlib.animation as animation

import matplotlib.pyplot as plt
import matplotlib.animation as animation

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import numpy as np

def animated_gender_pie_chart(df):
    """
    2008-2023 yılları arasındaki kadın-erkek dağılımını hareketli pasta grafiğiyle gösterir.
    """
    # Çok seviyeli sütun başlıklarını düzleştir
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(map(str, col)).strip() if isinstance(col, tuple) else col for col in df.columns]
    
    # Yıl sütununu algıla
    year_column = [col for col in df.columns if 'Yıl' in col][0]
    years = df[year_column].dropna().unique()
    
    # Eksik değerleri doldur
    df = df.fillna(0)
    
    # Geçerli yılları filtrele
    valid_years = []
    for year in years:
        df_year = df[df[year_column] == year]
        female = df_year[[col for col in df.columns if col.endswith('_Kadın')]].sum().sum()
        male = df_year[[col for col in df.columns if col.endswith('_Erkek')]].sum().sum()
        if female > 0 and male > 0:
            valid_years.append(year)
    
    if not valid_years:
        raise ValueError("Geçerli veri içeren hiçbir yıl bulunamadı.")
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    def update(frame):
        ax.clear()
        year = valid_years[frame]
        df_year = df[df[year_column] == year]
        
        # Kadın ve Erkek verilerini al
        female = df_year[[col for col in df.columns if col.endswith('_Kadın')]].sum().sum()
        male = df_year[[col for col in df.columns if col.endswith('_Erkek')]].sum().sum()
        
        # NaN ve negatif değerleri önle
        female = max(female, 0)
        male = max(male, 0)
        total_population = female + male
        if total_population == 0:
            female_ratio, male_ratio = 0, 0
        else:
            female_ratio = (female / total_population) * 100
            male_ratio = (male / total_population) * 100
        
        sizes = [female_ratio, male_ratio]
        labels = ['Kadın', 'Erkek']
        colors = ['#FF69B4', '#1E90FF']
        explode = [0.05, 0.05]
        
        ax.pie(
            sizes,
            labels=labels,
            autopct='%1.1f%%',
            startangle=140,
            explode=explode,
            colors=colors
        )
        ax.set_title(f"{year} Yılı Eğitim Düzeyleri Kadın-Erkek Dağılımı")
    
    # Animasyonu oluştur
    anim = animation.FuncAnimation(
        fig,
        update,
        frames=len(valid_years),
        repeat=False
    )
    
    plt.show()
    anim.save('gender_inequality_pie_chart.mp4', writer='ffmpeg')
    print("Animasyon başarıyla kaydedildi: gender_inequality_pie_chart.mp4")

# Örnek kullanım
# animated_gender_pie_chart(df)

#animated_gender_pie_chart(df)

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
import numpy as np

def animated_gender_pie_chart(df):
    """
    2008-2023 yılları arasındaki kadın-erkek dağılımını her eğitim düzeyi için
    ayrı ayrı hareketli pasta grafikleriyle gösterir.
    """
    # Çok seviyeli sütun başlıklarını düzleştir
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(map(str, col)).strip() if isinstance(col, tuple) else col for col in df.columns]
    
    # Yıl sütununu algıla
    year_column = [col for col in df.columns if 'Yıl' in col][0]
    years = df[year_column].dropna().unique()
    
    # Eğitim seviyelerini belirle
    education_levels = [
        'Genel toplam', 'Okuma yazma bilmeyen', 'Okuma yazma bilen fakat bir okul bitirmeyen',
        'İlkokul', 'İlköğretim', 'Ortaokul ve dengi meslek', 'Lise ve dengi meslek',
        'Yüksekokul veya fakülte', 'Yüksek lisans', 'Doktora'
    ]
    
    # Eksik değerleri doldur
    df = df.fillna(0)
    
    # Geçerli yılları filtrele
    valid_years = []
    for year in years:
        df_year = df[df[year_column] == year]
        female = df_year[[col for col in df.columns if col.endswith('_Kadın')]].sum().sum()
        male = df_year[[col for col in df.columns if col.endswith('_Erkek')]].sum().sum()
        if female > 0 and male > 0:
            valid_years.append(year)
    
    if not valid_years:
        raise ValueError("Geçerli veri içeren hiçbir yıl bulunamadı.")
    
    fig, axs = plt.subplots(2, 5, figsize=(18, 12))
    axs = axs.flatten()[:10]  # Fazla eksenleri kaldır
    print(len(axs))
    def update(frame):
        year = valid_years[frame]
        df_year = df[df[year_column] == year]
        
        for i, level in enumerate(education_levels):
            if i >= len(axs):
                break
            ax = axs[i]
            ax.clear()
            
            female = df_year[[col for col in df.columns if col.startswith(level) and col.endswith('_Kadın')]].sum().sum()
            male = df_year[[col for col in df.columns if col.startswith(level) and col.endswith('_Erkek')]].sum().sum()
            
            # NaN ve negatif değerleri önle
            female = max(female, 0)
            male = max(male, 0)
            total_population = female + male
            if total_population == 0:
                female_ratio, male_ratio = 0, 0
            else:
                female_ratio = (female / total_population) * 100
                male_ratio = (male / total_population) * 100
            
            sizes = [female_ratio, male_ratio]
            labels = ['Kadın', 'Erkek']
            colors = ['#FF69B4', '#1E90FF']
            explode = [0.05, 0.05]
            
            ax.pie(
                sizes,
                labels=labels,
                autopct='%1.1f%%',
                startangle=140,
                explode=explode,
                colors=colors
            )
            ax.set_title(f" {level}")
            fig.suptitle(f"{year} Yılı Eğitim Düzeyleri Kadın-Erkek Dağılımı", fontsize=16)
    # Animasyonu oluştur
    anim = animation.FuncAnimation(
        fig,
        update,
        frames=len(valid_years),
        interval=600,
        repeat=False
    )
    
    plt.tight_layout()
    plt.show()
    anim.save('gender_inequality_pie_chart_by_level.gif', writer='pillow')

    anim.save('gender_inequality_pie_chart_by_level.mp4', writer='ffmpeg')
    print("Animasyon başarıyla kaydedildi: gender_inequality_pie_chart_by_level.mp4")



# Örnek kullanım
#animated_gender_pie_chart(df)


#######ISI grafiği
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from PIL import Image
import os

def gender_difference_heatmap(df):
    """
    Şehirlere göre kadın ve erkek arasındaki farkı yıl yıl ısı dağılım grafiğiyle gösterir ve her yılı ayrı bir görüntü dosyası olarak kaydeder.
    Isı haritasındaki renkler:
    - Kırmızı tonları: Erkeklerin sayısının kadınlardan daha fazla olduğunu gösterir.
    - Mavi tonları: Kadınların sayısının erkeklerden daha fazla olduğunu gösterir.
    - Beyaz: Kadın ve erkek sayısının birbirine yakın olduğunu gösterir.
    """
    # Çok seviyeli sütun başlıklarını düzleştir
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(map(str, col)).strip() if isinstance(col, tuple) else col for col in df.columns]
    
    # Yıl ve şehir sütunlarını algıla
    year_column = [col for col in df.columns if 'Yıl' in col][0]
    city_column = [col for col in df.columns if 'İl Adı' in col][0]
    years = df[year_column].dropna().unique()
    
    # Eğitim seviyelerini belirle
    education_levels = [
        'Genel toplam', 'Okuma yazma bilmeyen', 'Okuma yazma bilen fakat bir okul bitirmeyen',
        'İlkokul', 'İlköğretim', 'Ortaokul ve dengi meslek', 'Lise ve dengi meslek',
        'Yüksekokul veya fakülte', 'Yüksek lisans', 'Doktora', 'Bilinmeyen'
    ]
    
    # Eksik değerleri doldur
    df = df.fillna(0)
    
    output_folder = 'heatmap_frames'
    os.makedirs(output_folder, exist_ok=True)
    
    for year in years:
        fig, ax = plt.subplots(figsize=(16, 12))
        df_year = df.loc[df[year_column] == year].copy()
        
        heatmap_data = pd.DataFrame(index=df_year[city_column].unique())
        for level in education_levels:
            female_col = f'{level}_Kadın'
            male_col = f'{level}_Erkek'
            if female_col in df.columns and male_col in df.columns:
                df_year['Difference'] = df_year[female_col] - df_year[male_col]
                city_diff = df_year.groupby(city_column)['Difference'].sum()
                heatmap_data[level] = city_diff
        
        heatmap_data = heatmap_data.fillna(0)
        
        # Farkı daha görünür hale getirmek için norm aralığı ayarla
        vmin = -np.percentile(np.abs(heatmap_data.values), 95)
        vmax = np.percentile(np.abs(heatmap_data.values), 95)
        
        sns.heatmap(
            heatmap_data,
            cmap='coolwarm',
            annot=False,
            fmt='.0f',
            linewidths=0.5,
            ax=ax,
            vmin=vmin,
            vmax=vmax,
            cbar_kws={'label': 'Kadın-Erkek Farkı'}
        )
        ax.set_title(f'Kadın-Erkek Farkı Isı Dağılım Grafiği - {year}', fontsize=16)
        ax.set_xlabel('Eğitim Seviyeleri', fontsize=12)
        ax.set_ylabel('Şehirler', fontsize=12)
        
        # Yazıların okunabilirliğini artır
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        
        # Açıklama kutusu ekle
        plt.figtext(0.5, -0.05,
                    'Kırmızı: Erkeklerin kadınlardan fazla olduğu bölgeler | Mavi: Kadınların erkeklerden fazla olduğu bölgeler',
                    wrap=True, horizontalalignment='center', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(f'{output_folder}/heatmap_{year}.png')
        print(f"{year} yılı için ısı haritası kaydedildi: {output_folder}/heatmap_{year}.png")
        plt.close(fig)

def create_heatmap_gif():
    """
    Kaydedilen ısı haritası görüntülerini kullanarak bir GIF oluşturur.
    """
    output_folder = 'heatmap_frames'
    images = []
    for file in sorted(os.listdir(output_folder)):
        if file.endswith('.png'):
            images.append(Image.open(os.path.join(output_folder, file)))
    if images:
        images[0].save(
            'gender_difference_heatmap.gif',
            save_all=True,
            append_images=images[1:],
            duration=500,
            loop=0
        )
        print("Isı dağılım grafiği animasyonu başarıyla kaydedildi: gender_difference_heatmap.gif")

# Örnek kullanım
# gender_difference_heatmap(df)

#gender_difference_heatmap(df)

create_heatmap_gif()

