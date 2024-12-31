import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

day_df = pd.read_csv("main_data.csv")

def create_monthly_sharing_df(df):
    monthly_sharing_df = df.resample(rule='M', on='dteday').agg({
        "cnt": "sum"
    })
    monthly_sharing_df.index = monthly_sharing_df.index.strftime('%Y-%m')
    monthly_sharing_df = monthly_sharing_df.reset_index()
    monthly_sharing_df.rename(columns={
        "dteday": "Bulan",
        "cnt": "Total_Peminjaman"
    }, inplace=True)
    return monthly_sharing_df

datetime_columns = ["dteday"]
 
for column in datetime_columns:
    day_df[column] = pd.to_datetime(day_df[column])

min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()

# Sidebar untuk pengaturan tanggal
with st.sidebar:
    # Mengambil start_date dari date_input
    start_date = st.date_input(
        label='Mulai Tanggal',
        min_value=min_date,
        max_value=max_date,
        value=min_date
    )

    # Mengambil end_date dari date_input
    end_date = st.date_input(
        label='Hingga Tanggal',
        min_value=min_date,
        max_value=max_date,
        value=max_date
    )

    # Membuat validasi agar end_date tidak bisa sebelum start_date
    if start_date > end_date:
        st.error('Tanggal akhir harus setelah tanggal Mulai .')

# Filter data berdasarkan tanggal yang dipilih
main_df = day_df[(day_df["dteday"] >= str(start_date)) & 
                (day_df["dteday"] <= str(end_date))]

monthly_sharing_data_df = create_monthly_sharing_df(main_df)
st.header('Analisis Data Peminjaman Sepeda')

st.subheader('Peminjaman Sepeda perbulan')

monthly_sharing_data_df['Bulan'] = pd.to_datetime(monthly_sharing_data_df['Bulan'])
# Memisahkan data untuk tahun 2011 dan 2012
monthly_sharing_2011 = monthly_sharing_data_df[monthly_sharing_data_df['Bulan'].dt.year == 2011]
monthly_sharing_2012 = monthly_sharing_data_df[monthly_sharing_data_df['Bulan'].dt.year == 2012]

col1, col2 = st.columns(2)
 
with col1:
    total_sharing_2011 = monthly_sharing_2011["Total_Peminjaman"].sum()
    formatted_total_sharing_2011 = "{:,.0f}".format(total_sharing_2011)
    st.metric("Total Peminjaman 2011", value=formatted_total_sharing_2011)

with col2:
    total_sharing_2012 = monthly_sharing_2012["Total_Peminjaman"].sum()
    formatted_total_sharing_2012 = "{:,.0f}".format(total_sharing_2012)
    st.metric("Total Peminjaman 2012", value=formatted_total_sharing_2012)

# Membuat plot menggunakan Matplotlib
fig1, ax1 = plt.subplots(figsize=(10, 6))

# Plot untuk tahun 2011 (Bar Plot)
ax1.bar(monthly_sharing_2011['Bulan'].dt.month - 0.2, monthly_sharing_2011['Total_Peminjaman'], width=0.4, label='2011', color='skyblue')

# Plot untuk tahun 2012 (Bar Plot)
ax1.bar(monthly_sharing_2012['Bulan'].dt.month + 0.2, monthly_sharing_2012['Total_Peminjaman'], width=0.4, label='2012', color='salmon')

# Konfigurasi plot
ax1.set_title('Total Peminjaman Sepeda perbulan', fontsize=20)
ax1.set_xlabel('Bulan', fontsize=15)
ax1.set_ylabel('Total Peminjaman', fontsize=15)
ax1.set_xticks(range(1, 13))
ax1.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
ax1.legend(fontsize=12)

# Menampilkan plot menggunakan Streamlit
st.pyplot(fig1)


with st.expander("Penjelasan"):
    st.write(
        """Berdasarkan grafik yang ditampilkan, terlihat bahwa jumlah peminjaman sepeda pada tahun 2012 jauh lebih tinggi dibandingkan dengan tahun 2011. Di tahun 2012, bulan September menjadi puncak peminjaman, diikuti dengan penurunan yang signifikan pada bulan-bulan berikutnya. Sementara itu, pada tahun 2011, jumlah peminjaman terus meningkat hingga bulan Mei, tetapi setelah itu mengalami penurunan yang lebih stabil hingga akhir tahun. Hal ini menunjukkan bahwa meskipun ada fluktuasi, ada pertumbuhan yang lebih signifikan pada tahun 2012, yang menunjukkan tren peningkatan jumlah penyewaan sepeda dari tahun ke tahun.
        """
    )

# Agregasi data
season_weather_stats = day_df.groupby(["season", "weathersit"]).agg({
    "cnt": ["max", "min", "mean", "std", "sum"]
})

# Ubah multiindex menjadi single index untuk memudahkan visualisasi
season_weather_stats.columns = ['_'.join(col).strip() for col in season_weather_stats.columns.values]
season_weather_stats.reset_index(inplace=True)

st.subheader('Peminjaman Sepeda Berdasarkan Musim dan Kondisi Cuaca')

# Plotting
fig2, ax2 = plt.subplots(figsize=(10, 6))

# Warna untuk kondisi cuaca
weather_colors = {
    1: 'skyblue',  # Clear
    2: 'orange',   # Mist
    3: 'salmon',   # Light Snow
    4: 'lightgreen'  # Heavy Rain + Ice Pallets + Thunderstorm + Mist
}

# Untuk memplot grouped bar plot dengan warna yang konsisten
weather_sits = season_weather_stats['weathersit'].unique()
width = 0.2  # Lebar setiap bar

# Menghitung posisi X untuk setiap bar
for i, weather_sit in enumerate(weather_sits):
    weather_sit_data = season_weather_stats[season_weather_stats['weathersit'] == weather_sit]
    color = weather_colors.get(weather_sit, 'gray')  # Menentukan warna untuk setiap cuaca
    ax2.bar(weather_sit_data['season'] + i * width - 0.2, weather_sit_data['cnt_sum'], width=width, label=f'Cuaca {weather_sit}', color=color)

# Konfigurasi plot
ax2.set_title('Total Peminjaman Sepeda Berdasarkan Musim dan Kondisi Cuaca', fontsize=20)
ax2.set_xlabel('Musim', fontsize=15)
ax2.set_ylabel('Total Peminjaman', fontsize=15)
ax2.legend(title='Kondisi Cuaca', fontsize=12)
ax2.set_xticks(range(1, 5))
ax2.set_xticklabels(['Spring', 'Summer', 'Fall', 'Winter'])

# Menampilkan plot menggunakan Streamlit
st.pyplot(fig2)
with st.expander("Penjelasan"):
    st.write(
        """Berdasarkan grafik di atas, musim gugur (musim 3) menjadi salah satu faktor yang meningkatkan jumlah penyewaan sepeda. Penyewaan sepeda cenderung paling tinggi saat cuaca cerah, yang mendorong lebih banyak orang untuk menggunakan sepeda sewaan. Sebaliknya, di berbagai musim, terlihat bahwa penyewaan sepeda menurun secara signifikan saat cuaca buruk, terutama pada musim 4 (Heavy Rain + Ice Pallets + Thunderstorm + Mist), di mana tidak ada penyewa sepeda sama sekali. Dari sini, dapat disimpulkan bahwa musim dan kondisi cuaca pada hari tertentu sangat memengaruhi tingkat penyewaan sepeda.
        """
    )

st.subheader('Hubungan antara Variabel Cuaca dan Peminjaman Sepeda')

# Memilih kolom yang relevan untuk analisis korelasi
variables = ['temp', 'atemp', 'hum', 'windspeed', 'cnt']

# Membuat pairplot untuk visualisasi hubungan antar variabel
fig3 = sns.pairplot(day_df[variables], kind='scatter', diag_kind='kde', plot_kws={'alpha': 0.6})

# Menambahkan judul
fig3.fig.suptitle('Hubungan antara Variabel Cuaca dan Peminjaman Sepeda', y=1.02, fontsize=20)

# Menampilkan plot menggunakan Streamlit
st.pyplot(fig3)
with st.expander("Penjelasan"):
    st.write(
        """Pada heatmap korelasi di atas, dapat dilihat bahwa suhu (temp) memiliki korelasi positif yang cukup kuat dengan jumlah penyewaan sepeda (0.63), yang menunjukkan bahwa semakin tinggi suhu, semakin banyak sepeda yang disewa. Sebaliknya, kelembaban (humidity) dan kecepatan angin (windspeed) memiliki korelasi negatif, yang berarti bahwa ketika kelembaban dan angin semakin tinggi, penyewaan sepeda cenderung menurun. Visualisasi menggunakan pairplot memperlihatkan hubungan ini lebih jelas, dengan suhu yang menunjukkan hubungan positif terhadap jumlah penyewaan sepeda, sementara kelembaban dan kecepatan angin cenderung menurunkan jumlah penyewaan.
        """
    )