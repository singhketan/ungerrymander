import pandas as pd
import random

df = pd.read_csv('data.csv')

no_of_experiments = 20
no_of_randomized_counties = 20
min_population_factor = 0.9
max_population_factor = 1.1



last_df = df.copy()


def getPopulations(current_trial_df):
	populations = []
	all_dems = []
	all_reps = []
	results = []
	for district in current_trial_df['district'].unique():
		district_rows = current_trial_df[current_trial_df.district == district]
		total_reps = (district_rows['rep']).sum()
		total_dems = (district_rows['dem']).sum()
		all_dems.append(total_dems)
		all_reps.append(total_reps)
		if total_dems > total_reps:
			results.append('dems')
		else:
			results.append('reps')
		populations.append(total_reps + total_dems)

	return populations, all_dems, all_reps, results
	
def getEfficiencyGap(populations, all_dems, all_reps, results):
	dems_total_wasted = 0
	reps_total_wasted = 0
	total_votes = 0
	for i, result in enumerate(results):
		for_win = round(populations[i]/2) + 1
		if result == "dems":
			dems_total_wasted +=  all_dems[i] - for_win
			reps_total_wasted += all_reps[i]
		else:
			reps_total_wasted +=  all_reps[i] - for_win
			dems_total_wasted += all_dems[i]
			
		total_votes += populations[i]
		
	return 100 * (abs(dems_total_wasted - reps_total_wasted)/total_votes)
			
			
def checkConsistency(current_trial_df, min_population, max_population):
	populations, all_dems, all_reps, results = getPopulations(current_trial_df)
	if ((min(populations) >= min_population) and (max(populations) <= max_population)):
		print getEfficiencyGap(populations, all_dems, all_reps, results)
	else:
		print "Populations not consistent"
		return False

original_populations, all_dems, all_reps, results = getPopulations(df)
efficiencyGap = getEfficiencyGap(original_populations, all_dems, all_reps, results)

print "Original efficiency gap:"
print efficiencyGap
min_population = min_population_factor * min(original_populations)
max_population = max_population_factor * max(original_populations)



	
for i in range(no_of_experiments):
	current_trial_df = last_df.copy()
	random_rows = current_trial_df.sample(n = no_of_randomized_counties)

	#The following starts after each omega test.
	counties_done = []
	for index, row in random_rows.iterrows():
		current_county_id = row['county_id']
		current_district = row['district']
		if current_county_id not in counties_done:
			counties_done.append(current_county_id)
			shuffled_neighbors = row['neighbors'].split(",")
			for neighbor in shuffled_neighbors:
				
				if neighbor != "":
					county_row = current_trial_df[current_trial_df.county_id == int(neighbor)]
					
					if(current_district != county_row['district'].item()):
						current_trial_df = current_trial_df.set_value(county_row.index, 'district', current_district)
						counties_done.append(int(neighbor))
						break
		else:
			#We'll skip this iteration if the counties has already been manipulated
			continue

	checkConsistency(current_trial_df, min_population, max_population)
	#update the last_df if consistent and gap decrease