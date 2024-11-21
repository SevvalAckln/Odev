#Importing necessary libraries

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
matplotlib.use('Agg')

# TODO: In this assignment students will develop skills in complex data manipulation, data cleaning and analysis.
#       They will go through a data analysis process with subtasks of various difficulty levels.

""" 

Sales Data: A data set with different products sold in each row.
            Sample columns: date, product_code, product_name, category, price, quantity, total_sales
            
            
Customer Data: Contains data about customers.
               Sample columns: customer_id, name, gender, age, city, expenditure_amount

"""

pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)

#EXPLORATORY DATA ANALYSIS (TASK 1: DATA CLEANING AND MANIPULATION

sales_data = pd.read_csv('C:/Users/ackln/Downloads/satis_verisi_5000.csv')
customer_data = pd.read_csv('C:/Users/ackln/Downloads/musteri_verisi_5000_utf8.csv')

print(sales_data.head())
print(customer_data.head())


sales_data.info() #"tarih","fiyat","toplam_satis"
customer_data.info()

print(sales_data.isnull().sum())#No Null data
print(customer_data.isnull().sum())#No null data

print(sales_data.duplicated().sum())
print(customer_data.duplicated().sum())

sales_data = sales_data.drop('Unnamed: 0', axis=1)

# Change 'fiyat' column to numeric and if there is a mistake make it "NaN"
sales_data['fiyat'] = pd.to_numeric(sales_data['fiyat'], errors='coerce')

#fill the empty values in the "fiyat" column with mean
price_mean = sales_data['fiyat'].mean()
sales_data['fiyat'] = sales_data['fiyat'].fillna(price_mean)

# Change 'toplam_satis' column to numeric and if there is a mistake make it "NaN"
sales_data['toplam_satis'] = pd.to_numeric(sales_data['toplam_satis'], errors='coerce')

# Threshold for extremely large numbers
max_normal_value = 100000  # Choose this value according to our very own dataset
sales_data['toplam_satis'] = sales_data['toplam_satis'].apply(
    lambda x: np.nan if x > max_normal_value else x
)

# fill the empty values in the "toplam_satis" column with mean
sum_sale_mean = sales_data['toplam_satis'].mean()
sales_data['toplam_satis'] = sales_data['toplam_satis'].fillna(sum_sale_mean)

print(sales_data.head(30))

# Detecting more outliers by using Quartiles
def cap_outliers(data, column):
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1

    #Sales cant be negative!
    lower_bound = max(0, Q1 - 1.5 * IQR)
    upper_bound = Q3 + 1.5 * IQR

    data[column] = data[column].clip(lower=lower_bound, upper=upper_bound)

    return lower_bound, upper_bound

# Controlling the numerical datas if there is an outlier or not
Price_outlier = cap_outliers(sales_data, 'fiyat')
Count_outlier = cap_outliers(sales_data, 'adet')
Sales_outlier = cap_outliers(sales_data, 'toplam_satis')

Age_outlier = cap_outliers(customer_data, 'yas')
Spend_outlier = cap_outliers(customer_data, 'harcama_miktari')

print("Outliers in the Price column:", Price_outlier)
print("Outliers in the Quantity column:", Count_outlier)
print("Outliers in the Total Sales column:", Sales_outlier)

print("Outliers in the Age column:", Age_outlier)
print("Outliers in the Expenditure column:", Spend_outlier)

# Also using visualization to detect outliers
plt.figure(figsize=(10, 6))
sns.boxplot(data=sales_data[['fiyat', 'toplam_satis', 'adet']])
plt.title('sales_data Veri Seti için Kutu Grafiği')
plt.savefig('sales_data_boxplot.png')

plt.figure(figsize=(10, 6))
sns.boxplot(data=customer_data[['yas', 'harcama_miktari']])
plt.title('customer_data Veri Seti için Kutu Grafiği')
plt.savefig('customer_data_boxplot.png')

# Since there is outliers in the "toplam_satis" column
sale_bounds = cap_outliers(sales_data, 'toplam_satis')

print("Toplam satış sütunu sınırları:", sale_bounds)

plt.figure(figsize=(10, 6))
sns.boxplot(data=sales_data[['fiyat', 'adet', 'toplam_satis']])
plt.title('Düzenlenmiş sales_data Veri Seti için Kutu Grafiği')
plt.savefig('adjusted_sales_data_boxplot.png')

#Merging both datasets into 1

merged_data = pd.merge(sales_data, customer_data, on="musteri_id", how="inner")

print(merged_data.head())
print(merged_data.describe())
print(merged_data.info())


#TIME SERIES ANALYSIS

# Change 'tarih' dtype to date
sales_data['tarih'] = pd.to_datetime(sales_data['tarih'], errors='coerce')
sales_data = sales_data.dropna(subset=['tarih'])

# Weekly Total sales
weekly_sales = sales_data.resample('W', on='tarih')['toplam_satis'].sum()

# Monthly total sales
monthly_sales = sales_data.resample('ME', on='tarih')['toplam_satis'].sum()

print(weekly_sales.head())
print("****************************************************************************************")
print(monthly_sales.head())

# First day of sales of each month
first_sale_each_month = sales_data.groupby(sales_data['tarih'].dt.to_period('M'))['tarih'].min()
# last day of sales of each month
last_sale_each_month = sales_data.groupby(sales_data['tarih'].dt.to_period('M'))['tarih'].max()

print(first_sale_each_month)
print("****************************************************************************************")
print(last_sale_each_month)

# Weekly Total sold product count
weekly_product_sales = sales_data.resample('W', on='tarih')['adet'].sum()
print(weekly_product_sales.head())

# Time Series Trend: Weekly total sales
plt.figure(figsize=(12, 6))
plt.plot(weekly_sales.index, weekly_sales, marker='o', color='orange', label='Haftalık Toplam Satış')
plt.title('Haftalık Toplam Satış Trendleri')
plt.xlabel('Tarih')
plt.ylabel('Toplam Satış')
plt.legend()
plt.grid()
plt.savefig('weekly_sales_trends.png')

# Time Series Trend: Monthly total sales
plt.figure(figsize=(12, 6))
plt.plot(monthly_sales.index, monthly_sales, marker='o', label='Aylık Toplam Satış')
plt.title('Aylık Toplam Satış Trendleri')
plt.xlabel('Tarih')
plt.ylabel('Toplam Satış')
plt.legend()
plt.grid()
plt.savefig('monthly_sales_trends.png')

# Monthly sales groupby product
monthly_product_sales = sales_data.groupby([sales_data['tarih'].dt.to_period('M'), 'ürün_adi'])['adet'].sum()

# weekly sales groupby product
weekly_product_sales = sales_data.groupby([sales_data['tarih'].dt.to_period('W'), 'ürün_adi'])['toplam_satis'].sum()
print(weekly_product_sales.head())

unique_products = sales_data['ürün_adi'].unique()

for product in unique_products:
    product_weekly_sales = weekly_product_sales.xs(product, level='ürün_adi')

    plt.figure(figsize=(12, 6))
    product_weekly_sales.plot(marker='o', label=f'Haftalık Satış - {product}')
    plt.title(f'{product} Haftalık Satış Trendleri')
    plt.xlabel('Hafta')
    plt.ylabel('Toplam Satış')
    plt.legend()
    plt.grid()
    plt.savefig(f'{product}_trends.png')
    plt.close()

for product in unique_products:
    product_monthly_sales = monthly_product_sales.xs(product, level='ürün_adi')

    plt.figure(figsize=(12, 6))
    product_monthly_sales.plot(marker='o', label=f'Aylık Satış - {product}')
    plt.title(f'{product} Aylık Satış Trendleri')
    plt.xlabel('Ay')
    plt.ylabel('Toplam Satış')
    plt.legend()
    plt.savefig(f'{product}_trends.png')
    plt.close()

#CATEGORICAL AND QUANTITATIVE ANALAYSIS

# Total sales by categories
category_sales = sales_data.groupby('kategori')['toplam_satis'].sum()
print(category_sales)

total_sales = category_sales.sum()
category_percentage = (category_sales / total_sales) * 100

print("Percentage of Total Sales by Product Categories: ")
print(category_percentage)

pd.options.display.float_format = '{:,.2f}'.format

category_analysis = pd.DataFrame({
    'Toplam Satış': category_sales,
    'Oran (%)': category_percentage
})

print(category_analysis)

plt.figure(figsize=(8, 8))
plt.pie(category_percentage, labels=category_percentage.index, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
plt.title('Ürün Kategorilerinin Toplam Satışlar İçindeki Oranı')
plt.savefig('category_analysis.png')

# Analysis by age
bins = [18, 25, 35, 50, np.inf]  # Example age groups
labels = ['18-25', '26-35', '36-50', '50+']

merged_data['yas_grubu'] = pd.cut(merged_data['yas'], bins=bins, labels=labels, right=True)
print(merged_data[['yas', 'yas_grubu']].head())

# Total sales by age groups
age_group_sales = merged_data.groupby('yas_grubu', observed=False)['toplam_satis'].sum()
print(age_group_sales)

age_group_percentage = (age_group_sales / age_group_sales.sum()) * 100
print("Yaş Gruplarının Toplam Satışlardaki Oranı (%):")
print(age_group_percentage)

plt.figure(figsize=(8, 8))
plt.pie(age_group_percentage, labels=age_group_percentage.index, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
plt.title('Yaş Gruplarının Toplam Satışlar İçindeki Oranı')
plt.savefig('Age_Groups_By_Total_Sales.png')

# Expenditure By Sex
gender_spend = merged_data.groupby('cinsiyet')['harcama_miktari'].mean()
print(gender_spend)

plt.figure(figsize=(10, 6))
sns.boxplot(data=merged_data, x='cinsiyet', y='harcama_miktari')
plt.title('Kadın ve Erkek Müşterilerin Harcama Dağılımı')
plt.xlabel('Cinsiyet')
plt.ylabel('Harcama Miktarı')
plt.savefig('ExpenditureBySex.png')

gender_total_spend = merged_data.groupby('cinsiyet')['harcama_miktari'].sum()
print(gender_total_spend)

gender_diff = gender_spend['Kadın'] - gender_spend['Erkek']
print("Kadın ve Erkek Müşteriler Arasındaki Ortalama Harcama Farkı:", gender_diff)


# ADVANCED DATA MANIPULATION

# Expenditure by city
city_spend = merged_data.groupby('sehir')['harcama_miktari'].sum()
print(city_spend)

city_spend_sorted = city_spend.sort_values(ascending=False)
print(city_spend_sorted)

plt.figure(figsize=(12, 6))
sns.barplot(x=city_spend_sorted.index, y=city_spend_sorted.values, hue=city_spend_sorted.index, palette='viridis', legend=False)
plt.title('Şehir Bazında Toplam Harcama Miktarları')
plt.xlabel('Şehir')
plt.ylabel('Toplam Harcama Miktarı')
plt.xticks(rotation=45)
plt.savefig('cityAnalysis.png')

# By Product
monthly_sales = sales_data.groupby([sales_data['tarih'].dt.to_period('M'), 'ürün_adi'])['toplam_satis'].sum().unstack()
print(monthly_sales.head())

monthly_sales_pct_change = monthly_sales.pct_change() * 100  # Yüzde olarak hesapla
print(monthly_sales_pct_change.head())

average_sales_growth = monthly_sales_pct_change.mean()
print(average_sales_growth)


plt.figure(figsize=(12, 6))
monthly_sales_pct_change.plot(kind='bar', figsize=(12, 6), colormap='viridis')
plt.title('Aylık Satış Artış Oranları (Yüzde Değişim)')
plt.xlabel('Ürünler ve Aylık Dönemler')
plt.ylabel('Yüzde Değişim')
plt.xticks(rotation=45)
plt.legend(title='Ürün Adı')
plt.savefig('ProductByMonth.png')


monthly_category_sales = sales_data.groupby([sales_data['tarih'].dt.to_period('M'), 'kategori'])['toplam_satis'].sum().unstack()
print(monthly_category_sales.head())

monthly_category_pct_change = monthly_category_sales.pct_change() * 100
print(monthly_category_pct_change.head())

plt.figure(figsize=(12, 6))
monthly_category_pct_change.plot(kind='bar', figsize=(12, 6), colormap='viridis')
plt.title('Kategori Bazında Aylık Satış Artış Oranları (Yüzde Değişim)')
plt.xlabel('Kategori ve Aylık Dönemler')
plt.ylabel('Yüzde Değişim')
plt.xticks(rotation=45)
plt.legend(title='Kategori')
plt.grid(True)
plt.savefig('CategoryAndMonth.png')


average_sales_growth_by_category = monthly_category_pct_change.mean()
print(average_sales_growth_by_category)