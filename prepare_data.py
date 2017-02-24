import pandas as pd

df = pd.read_excel('raw.xlsx')

all_new_neighbors = []
for index, row in df.iterrows():
	raw_neighbors = row['neighbor']
	neighbors = raw_neighbors.split(",")
	new_neighbors = []
	print index
	print "-----"
	for neighbor in neighbors:
		print neighbor
		county_id = (neighbor.split("-"))[-1]
		new_neighbors.append(county_id)
		
	all_new_neighbors.append(",".join(str(x) for x in new_neighbors))

df['neighbors'] = all_new_neighbors
df.drop(['neighbor'], axis = 1, inplace = True, errors = 'ignore')
df.drop(['C_Number'], axis = 1, inplace = True, errors = 'ignore')

df.to_csv('test_data.csv', index = False)