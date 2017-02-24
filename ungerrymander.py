import pandas as pd
import random

df = pd.read_csv('data.csv')

no_of_experiments = 1
no_of_randomized_counties = 5
min_population_factor = 0.9
max_population_factor = 1.1

random_rows = df.sample(n = no_of_randomized_counties)

last_df = df


def getPopulations(current_trial_df):
	populations = []
	for district in current_trial_df['district'].unique():
		district_rows = df[df.district == district]
		population = (district_rows['rep'] + district_rows['dem']).sum()
		populations.append(population)
	print populations
	return populations
		
def checkConsistency(current_trial_df, min_population, max_population):
	populations = getPopulations(current_trial_df)
	if ((min(populations) >= min_population) and (max(populations) <= max_population)):
		get
	else:
		print "Populations not consistent"
		return False

original_populations = getPopulations(df)
min_population = min_population_factor * min(original_populations)
max_population = max_population_factor * max(original_populations)
print min_population
print max_population

	
for i in range(no_of_experiments):
	current_trial_df = last_df
	#The following starts after each omega test.
	counties_done = []
	for index, row in random_rows.iterrows():
		county_id = row['county_id']
		current_district = row['district']
		if county_id not in counties_done:
			counties_done.append(county_id)
			shuffled_neighbors = row['neighbors'].split(",")
			for neighbor in shuffled_neighbors:
				if neighbor != "":
					county_row = df[df.county_id == int(neighbor)]
					if(current_district != county_row['district'].item()):
						current_trial_df.set_value(county_row.index, 'district', county_row['district'])
						counties_done.append(int(neighbor))
		else:
			#We'll skip this iteration if the counties has already been manipulated
			continue
	
	checkConsistency(current_trial_df, min_population, max_population)
	# ifOmegaIncrease = 