import pandas as pd
import random

df = pd.read_csv('data/data.csv')

no_of_experiments = 500
max_random_counties = 20
min_population_factor = 0.95
max_population_factor = 1.05



last_good_df = df.copy()


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
			
			

original_populations, all_dems, all_reps, results = getPopulations(df)
last_good_eg = getEfficiencyGap(original_populations, all_dems, all_reps, results)

print "Original efficiency gap: ", last_good_eg
print "-----------------"
min_population = min_population_factor * min(original_populations)
max_population = max_population_factor * max(original_populations)



	
for i in range(no_of_experiments):
	no_of_randomized_counties = random.randint(0, max_random_counties)
	current_trial_df = last_good_df.copy()
	random_rows = current_trial_df.sample(n = no_of_randomized_counties)

	#The following starts after each omega test.
	counties_done = []
	for index, row in random_rows.iterrows():
		current_county_id = row['county_id']
		current_district = row['district']
		if current_county_id not in counties_done:
			counties_done.append(current_county_id)
			for neighbor in row['neighbors'].split(","):
				
				if neighbor != "" and (int(neighbor) not in counties_done):
					county_row = current_trial_df[current_trial_df.county_id == int(neighbor)]
					
					if(current_district != county_row['district'].item()):
						current_trial_df = current_trial_df.set_value(county_row.index, 'district', current_district)
						counties_done.append(int(neighbor))
						break
		else:
			#We'll skip this iteration if the counties has already been manipulated
			continue

	populations, all_dems, all_reps, results = getPopulations(current_trial_df)
	this_min = min(populations)
	this_max = max(populations)
	if ((this_min >= min_population) and (max(populations) <= max_population)):
		current_eg = getEfficiencyGap(populations, all_dems, all_reps, results)
		print "Current Efficiency Gap: ", current_eg
		if current_eg < last_good_eg:
			last_good_df = current_trial_df.copy()
			last_good_eg = current_eg
			print "--------"
			print "New best Efficiency Gap: ", current_eg
			print no_of_randomized_counties, " counties randomized."
	else:
		print "------------"
		print "Populations inconsistent - Skipping configuration."
		# print "Min Populations", this_min, "Min allowed: ", min_population
		# print "Max Populations", this_max, "Max allowed: ", max_population
print "Best Efficiency Gap attained: ", last_good_eg
last_good_df.to_csv('data/new_eg_'+str(last_good_eg)+'.csv', index = False)	
	#update the last_good_df if consistent and gap decrease