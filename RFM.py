###############################################################
# Customer Segmentation with RFM
###############################################################
# Data for the year 2010-2011
# InvoiceNo: Invoice number. The unique number of each transaction. Aborted operation if it starts with C.
# StockCode: Product code. Unique number for each product.
# Description: Product name
# Quantity: Number of products. It expresses how many of the products on the invoices have been sold.
# InvoiceDate: Invoice date and time.
# UnitPrice: Product price (sterling)
# CustomerID: Unique customer number
# Country: Country name. Country where the customer lives.


####################
# Business Problem
####################

# An e-commerce company wants to segment its customers and determine marketing strategies according to these segments.
# For this,defining the behaviors of the customers and create groups according to the clusters in these behaviors
# In other words, including those who exhibit common behaviors in the same groups and trying to develop.
# special sales and marketing techniques for these groups.

#Dataset
#https://archive.ics.uci.edu/ml/datasets/Online+Retail+II

# TASK 1

######################
# 1.Understanding Data
######################
import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

df_ = pd.read_excel("Dataset/online_retail_II.xlsx", sheet_name="Year 2010-2011")
df = df_.copy()
df.head()
df.shape
df.describe().T

df.isnull().sum()
df.dropna(inplace=True)
df.head()

# How many unique product(description column)?
df["Description"].nunique()

# How many of each product are there?
df["Description"].value_counts().head()

# Top 5 ordered products
df.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head()

# The 'C' in the invoices shows the canceled transactions.
# Removing the canceled transactions from the dataset.
df = df[~df["Invoice"].str.contains("C", na=False)]
df = df[(df['Quantity'] > 0)]
df = df[(df['Price'] > 0)]
df.head()

# Total Price for each product
df["TotalPrice"] = df["Quantity"] * df["Price"]


# TASK 2
###########################
#Calculation of RFM metrics
###########################

today_date = dt.datetime(2011, 12, 11)
rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                     'Invoice': lambda Invoice: Invoice.nunique(),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})
rfm.head()
rfm.shape
rfm.columns = ['recency', 'frequency', 'monetary']


# TASK 3
#Segmentations
rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])
rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str))
rfm.head()


# TASK 4
seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
rfm.head()

# TASK 5
# Interpret both in terms of action decisions and in terms of the structure of the segments (mean RFM values).


rfm_seg = rfm.groupby(["segment"]).agg({"segment": "count",
                                               "monetary": ["min", "max", "mean"]})


rfm_new= rfm[rfm['segment']=='hibernating']
rfm_new.head() #r:1,2 f:1,2
rfm_new.shape #There is a customer base #1070 that has gone to sleep and has not chosen us again.
rfm_new.describe().T #Each potential sleeper spends an average of £488.


rfm_attention = rfm[rfm['segment']=='need_attention'] #r:3 f:3
rfm_attention.head()
rfm_attention.shape #There are 187 customers that we need to pay attention to and make loyal, the shortest way.
rfm_attention.describe().T

rfm_lotal = rfm[rfm['segment']=='loyal_customers']
rfm_lotal.head()
rfm_lotal.shape
rfm_lotal.describe().T

# Select the customer IDs of the "Loyal Customers" class and get the excel output.

loyal_customers=pd.DataFrame()
loyal_customers['customer_id']=rfm[rfm['segment']=='loyal_customers'].index
loyal_customers.head()
loyal_customers.to_excel("loyal_customers.xlsx")
