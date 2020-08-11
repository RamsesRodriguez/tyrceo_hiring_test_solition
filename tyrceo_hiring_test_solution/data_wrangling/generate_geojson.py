import pymysql.cursors
import pandas as pd
import numpy as np
import difflib
from osgeo import gdal, ogr, osr
from fiona.ogrext import Iterator, ItemsIterator, KeysIterator
import fiona
import geopandas as gpd
#import matplotlib.pyplot as plt

connection = pymysql.connect(host='35.187.55.190',
							 user='candidate',
							 password='Fbps9Y7MhKQa4XPxjYo8',
							 db='test',
							 charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

try:
	with connection.cursor() as cursor:
		
		#Query with desired values
		sql = """
			SELECT data.id, 
				   pokemon, 
				   score, 
				   coordinates.longitude, 
				   coordinates.latitude 
			  FROM data 
			 INNER JOIN coordinates 
			    ON data.id=coordinates.id 
			 WHERE score >= 0.5 
			   AND pokemon IN ('Charmander', 'Bulbasur', 'Squirtle')
			 ORDER BY data.id 
			"""
		#Array with starter names
		fixed_poke = ["Charmander", "Bulbasur", "Squirtle"]

		#Creation of the originalDF
		cursor.execute(sql)
		result = cursor.fetchall()
		originaldf = pd.DataFrame(result)
		df = originaldf

		#Dictionary for pokemon names
		dict_POKEMON = dict()

		#Correction of misspellings and typos
		def Spelling(ask):
			a = difflib.get_close_matches(ask, fixed_poke, n=3, cutoff=0.5)
			#list comprehension for all values of a
			b = [difflib.SequenceMatcher(None, ask, x).ratio() for x in a]
			return pd.Series(a + b)
		
		df1 = df['pokemon'].apply(Spelling)

		#Changing column names
		a = len(df1.columns) // 2
		df1.columns = ['pokemon'] + \
        	    	  ['Spell_Score']

		#Deleting undesired columns and merging all together
		columns_to_delete = ['pokemon']
		originaldf.drop(columns_to_delete, inplace=True, axis=1)
		originaldf.drop_duplicates(inplace=True)
		df2 = originaldf.join(df1)
		
		columns_to_delete = ['Spell_Score', 'id']
		df2.drop(columns_to_delete, inplace=True, axis=1)
		df2.drop_duplicates(inplace=True)

		#Converting Pandas DataFrame to GeoPandas

		gdf = gpd.GeoDataFrame(
			df2, geometry=gpd.points_from_xy(df2.longitude, df.latitude)
		)

		columns_to_delete = ['latitude', 'longitude']
		gdf.drop(columns_to_delete, inplace=True, axis=1)
		gdf.drop_duplicates(inplace=True)

		#Creating geojson from GeoPandas DataFrame

		gdf.to_file("../data_wrangling/points.geojson", driver='GeoJSON')

finally:
	connection.close()
