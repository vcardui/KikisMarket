# +----------------------------------------------------------------------------+
# | CARDUI WORKS v1.0.0
# +----------------------------------------------------------------------------+
# | Copyright (c) 2024 - 2024, CARDUI.COM (www.cardui.com)
# | Vanessa Reteguín <vanessa@reteguin.com>
# | Released under the MIT license
# | www.cardui.com/carduiframework/license/license.txt
# +----------------------------------------------------------------------------+
# | Author.......: Vanessa Reteguín <vanessa@reteguin.com>
# | First release: November 24th, 2024
# | Last update..: November 24th, 2024
# | WhatIs.......: KikisMarketDataset.py - Main
# +----------------------------------------------------------------------------+

# ------------ Resources / Documentation involved -------------
# Original Kaggle Dataset URL: 
#     https://www.kaggle.com/datasets/bhavikjikadara/grocery-store-dataset
#
# Downloading Kaggle Datasets:
#     https://stackoverflow.com/questions/55934733/documentation-for-kaggle-api-within-python

# ------------------------- Libraries -------------------------
from kaggle.api.kaggle_api_extended import KaggleApi
import os  # os.path.exists(path)
import pandas as pd
import re # re.split() (Regular expression operations)
import random

# ------------------------- Variables -------------------------
datasetFolder = "groceriesDataset"

# --------------------------- Code ----------------------------

api = KaggleApi()
api.authenticate()

#download single file: dataset_download_file(dataset, file_name, path=None, force=False, quiet=True)
# api.dataset_download_files("bhavikjikadara/grocery-store-dataset", path = datasetFolder, unzip=True)

# datasetPath = 'groceriesDataset/GroceryDataset.csv'
datasetPath = f"{datasetFolder}/{os.listdir(datasetFolder)[0]}"

if (os.path.exists(datasetPath)):
	print('File found')
	storeStock = pd.read_csv(datasetPath)
	print(storeStock.head())
else:
	print("File not found. Please check route")

# Show column names
print(storeStock.all())

# 1 is the axis number (0 for rows and 1 for columns)
storeStock = storeStock.drop(['Discount', 'Rating', 'Currency', 'Product Description'], axis=1)
storeStock.rename(columns={'Sub Category': 'Category'}, errors="raise") # No sé por qué no funciona pero bueno

# Show column names
print(storeStock.all())

inventory = []
remChar1 = '"'
remChar2 = '”'
for i in range(0, len(storeStock)):
	# Trim prices for strings such as '$32.99through-$83.99'
	price = str(storeStock.iloc[i,1])
	trimmedPrice = re.split(r"\$([\d,]+\.\d{2})", price, 1)
	trimmedPrice = next(s for s in trimmedPrice if s)

	storeStock.iloc[i,1] = trimmedPrice

	# Delete all " in string for avoiding parsing problems
	title = str(storeStock.iloc[i,2])
	storeStock.iloc[i,2] = title.replace(remChar1, "").replace(remChar2, "")

	feature = str(storeStock.iloc[i,3])
	storeStock.iloc[i,3] = feature.replace(remChar1, "").replace(remChar2, "")

	# Create random amount of products in stock within the inventory
	inventory.append(random.randrange(0, 300))

# Add inventory to dataframe
storeStock.insert(1, 'Stock', inventory)

print(storeStock.head())

# Save as a CSV
storeStock.to_csv('kkmktstock.csv', index=False) 

# Create MariaDB table delcaration
with open("KikisMarket.mariadb.txt", mode="a") as txt_file:
	header = """--
-- +----------------------------------------------------------------------------+
-- | CARDUI WORKS v1.0.0
-- +----------------------------------------------------------------------------+
-- | Copyright (c) 2024 - 2024, CARDUI.COM (www.cardui.com)
-- | Vanessa Reteguín <vanessa@reteguin.com>
-- | Released under the MIT license
-- | www.cardui.com/carduiframework/license/license.txt
-- +----------------------------------------------------------------------------+
-- | Author.......: Vanessa Reteguín <vanessa@reteguin.com>
-- | First release: November 24th, 2024
-- | Last update..: November 24th, 2024
-- | WhatIs.......: Kiki's Market - Scheme
-- | DBMS.........: MariaDB
-- +----------------------------------------------------------------------------+
--
"""
	tableDeclaration = """
-- DROP TABLE IF EXISTS kkmktstock;
CREATE TABLE kkmktstock (
	idkkmktstock    INT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE,
	
	category        VARCHAR(128) NOT NULL,
	stock           SMALLINT,
	price           DECIMAL(19, 4) DEFAULT 0,
	title           VARCHAR(256) NOT NULL,
	feature         VARCHAR(512) NOT NULL

) ENGINE = InnoDB DEFAULT CHARACTER SET = utf8;
"""
	insertsDeclaration = """
-- Inventario de la tienda
INSERT INTO kkmktstock (category, stock, price, title, feature) VALUES
"""
	txt_file.write(f"{header}")
	txt_file.write(f"{tableDeclaration}")
	txt_file.write(f"{insertsDeclaration}")

with open("KikisMarket.mariadb.txt", mode="a") as txt_file:
	for index, row in storeStock.iterrows():
		category = row['Sub Category']
		stock = row['Stock']
		price = row['Price']
		title = row['Title']
		feature = row['Feature']

		newInsert = f'("{category}", {stock}, {price}, "{title}", "{feature}"),\n'
		# print(newInsert)
		txt_file.write(f"{newInsert}")
	txt_file.write(f";")