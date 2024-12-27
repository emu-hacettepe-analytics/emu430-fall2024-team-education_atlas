import pandas as pd
import matplotlib.pyplot as plt

# Veri setini yükle ve tamamen boş sütunları kaldır
df = pd.read_excel('/home/mami/emu430/emu430-fall2024-team-education_atlas/data/yıllara_göre_egitim.xlsx')
df = df.dropna(axis=1, how='all')

# İlk iki satırı başlık olarak kullan ve eksik değerleri doldur
header1 = df.iloc[0].bfill()
header2 = df.iloc[1].bfill()

# Çok seviyeli (MultiIndex) başlıklar oluştur
df.columns = pd.MultiIndex.from_tuples(zip(header1, header2))
df = df.iloc[2:].reset_index(drop=True)

# İlk 3 sütunu tek seviyeli başlık yap
first_three_headers = ['Yıl', 'İl Kodu', 'İl Adı']

# Ana başlıklar ve alt başlıkları tanımla
main_headers = [
    'Genel toplam', 'Okuma yazma bilmeyen', 'Okuma yazma bilen fakat bir okul bitirmeyen',
    'İlkokul', 'İlköğretim', 'Ortaokul ve dengi meslek', 'Lise ve dengi meslek',
    'Yüksekokul veya fakülte', 'Yüksek lisans', 'Doktora', 'Bilinmeyen'
]
sub_headers = ['Toplam', 'Erkek', 'Kadın']

# Sütunları 3'erli gruplar hâlinde düzenle
education_columns = []
for main in main_headers:
    for sub in sub_headers:
        education_columns.append(f"{main}_{sub}")

# Tüm başlıkları birleştir
final_headers = first_three_headers + education_columns[:df.shape[1] - len(first_three_headers)]
df.columns = final_headers

# Yıl sütununu kontrol et
df['Yıl'] = pd.to_numeric(df['Yıl'], errors='coerce')
df = df.dropna(subset=['Yıl'])
df['Yıl'] = df['Yıl'].astype(int)

# 2023 yılı verilerini çek
df_2023 = df[df['Yıl'] == 2023].copy()

# Eğitim düzeylerine karşılık gelen yıl süreleri
education_years = {
    'Okuma yazma bilmeyen': 0,
    'İlkokul': 5,
    'İlköğretim': 8,
    'Ortaokul ve dengi meslek': 8,
    'Lise ve dengi meslek': 12,
    'Yüksekokul veya fakülte': 16,
    'Yüksek lisans': 18,
    'Doktora': 22
}

# Eğitim süresi hesaplaması
def calculate_avg_education_duration(row):
    total_years = 0
    total_students = 0
    
    for level, years in education_years.items():
        col_name = f"{level}_Toplam"
        if col_name in row.index and pd.notnull(row[col_name]):
            total_years += row[col_name] * years
            total_students += row[col_name]
    
    if total_students == 0:
        return 0
    return total_years / total_students

# Ortalama eğitim süresi hesapla
df_2023['Education_Avg'] = df_2023.apply(calculate_avg_education_duration, axis=1)

# 'Türkiye' satırını çıkar
df_2023 = df_2023[~df_2023['İl Adı'].str.contains('Türkiye', case=False, na=False)]

# En yüksek ve en düşük ortalamaya sahip illeri bul
top5_provinces = df_2023.nlargest(5, 'Education_Avg')[['İl Adı', 'Education_Avg']]
bottom5_provinces = df_2023.nsmallest(5, 'Education_Avg')[['İl Adı', 'Education_Avg']]

# Sonuçları yazdır
print("✅ En Yüksek Ortalama Eğitim Süresi Olan İller:")
print(top5_provinces)

print("\n✅ En Düşük Ortalama Eğitim Süresi Olan İller:")
print(bottom5_provinces)

# Grafik oluşturma
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(top5_provinces['İl Adı'], top5_provinces['Education_Avg'], color='skyblue', label='Highest Average')
ax.bar(bottom5_provinces['İl Adı'], bottom5_provinces['Education_Avg'], color='orange', label='Lowest Average')

ax.set_xlabel('Provinces')
ax.set_ylabel('Average Education Duration (Years)')
ax.set_title('Highest and Lowest Average Education Duration by Province (2023)')
ax.legend()
plt.xticks(rotation=30, ha='right')
plt.tight_layout()
plt.show()
