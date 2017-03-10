import pandas as pd
import random

input_file = 'data/input.csv'

df = pd.read_csv(input_file)
district_index = dict(zip(df.county_id, df.district))
neighbor_index = dict(zip(df.county_id, df.neighbors))

no_of_experiments = 100
max_random_counties = 20 #Should be less than the number of counties.
min_population_factor = 0.95
max_population_factor = 1.05



last_good_df = df.copy()

def getPopulations(current_trial_df, ifPrint = False):
	populations = []
	all_dems = []
	all_reps = []
	results = []
	sum = 0
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
			
		district_population = total_reps + total_dems
		sum += district_population
		populations.append(district_population)
		if ifPrint:
			print "District ",district,": Democrates - ",total_dems,". Republicans - ",total_reps, ". Total: ", district_population
	if ifPrint:		
		print "Total population: ", sum 

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
			
			

original_populations, all_dems, all_reps, results = getPopulations(df, ifPrint = True)
last_good_eg = getEfficiencyGap(original_populations, all_dems, all_reps, results)

print "Original efficiency gap: ", last_good_eg
print "-----------------"
min_population = min_population_factor * min(original_populations)
max_population = max_population_factor * max(original_populations)



	
for i in range(no_of_experiments):
	no_of_randomized_counties = random.randint(0, max_random_counties)
	current_trial_df = last_good_df.copy()
	
	#We'll randomly select a random number of counties.
	random_rows = current_trial_df.sample(n = no_of_randomized_counties)

	counties_done = []
	for index, row in random_rows.iterrows():
		current_county_id = row['county_id']
		current_district = row['district']
		if current_county_id not in counties_done:
			#If we've not already manipulated this particular county, we'll iterate through its neighbors and will check their district allegience.
			for neighbor_county_id in row['neighbors'].split(","):
				if neighbor_county_id != "" and (int(neighbor_county_id) not in counties_done):
					#If the neighbor has not already been encountered, we'll fetch its row, so that we can check its destrict allegience
					county_row = current_trial_df[current_trial_df.county_id == int(neighbor_county_id)]

					if(current_district != county_row['district'].item()):
						
						#If this neighbor's allegience is not the same as current_county_id's, we'll change its allegience to that of current_county_id.
						county_row_neighbors = county_row['neighbors'].item()

						same_district_neighbors = []
						for county_row_neighbor in county_row_neighbors.split(","):
							if county_row_neighbor != "":
								county_row_neighbor = int(county_row_neighbor)
								if district_index[county_row_neighbor] == county_row['district'].item():
									same_district_neighbors.append(county_row_neighbor)
						
						risky_pairs = []
						for n in same_district_neighbors:
							for m in same_district_neighbors:
								if n != m and ([n, m] not in risky_pairs) and ([m, n] not in risky_pairs):
									if str(n) not in neighbor_index[m].split(","):
										risky_pairs.append([n, m])
										
						if len(risky_pairs) > 0:
							continue
						else:

							current_trial_df = current_trial_df.set_value(county_row.index, 'district', current_district)
							district_index[int(neighbor_county_id)] = current_district
							counties_done.append(int(neighbor_county_id))
							break
		else:
			#We'll skip this iteration if the county has already been manipulated
			continue

	populations, all_dems, all_reps, results = getPopulations(current_trial_df)
	if ((min(populations) >= min_population) and (max(populations) <= max_population)):
		current_eg = getEfficiencyGap(populations, all_dems, all_reps, results)
		print "This configuration's Efficiency Gap: ", current_eg
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
print "---------------------------------------------------------------------"
print "Best Efficiency Gap attained: ", last_good_eg
getPopulations(last_good_df, ifPrint = True)


#last_good_df.to_csv(input_file, index = False)	
last_good_df.to_csv('data/new_eg_'+str(last_good_eg)+'.csv', index = False)	
	#update the last_good_df if consistent and gap decrease