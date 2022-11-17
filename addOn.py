

def Read_data():
	"""
	Reading the details of the tasks to be scheduled from the user as
	Number of tasks n:
	Period of task P:
	Worst case excecution time WCET:
	"""

	global n
	global hp
	global tasks
	global dList

	dList = {}

	n = int(input("\n \t\tEnter number of Tasks:"))
	# Storing data in a dictionary
	for  i in range(n):
		dList["TASK_%d"%i] = {"start":[],"finish":[]}

	dList["TASK_IDLE"] = {"start":[],"finish":[]}

	for i in range(n):
		tasks[i] = {}
		print("\n\n\n Enter Period of task T",i,":")
		p = input()
		tasks[i]["Period"] = int(p)
		print("Enter the WCET of task C",i,":")
		w = input()
		tasks[i]["WCET"] = int(w)
		print("Enter 0 for non-secure, 1 for secure task S",i,":")
		s = input()
		tasks[i]["Secure"] = int(s)
		print("Enter 1 if its the observer task, else 0 Observer",i,":")
		o = input()
		tasks[i]["Observer"] = int(o)

	# Writing the dictionary into a JSON file
	with open('tasks.json','w') as outfile:
		json.dump(tasks,outfile,indent = 4)


def filter_out(start_array,finish_array,release_time):
	"""A filtering function created to create the required data struture from the simulation results"""
	new_start = []
	new_finish = []
	beg_time = min(start_array)
	diff = int(hp/release_time)
	# Calculation of finish time and start time from simulation results
	if(release_time>1):
		new_start.append(beg_time)
		prev = beg_time
		for i in range(int(release_time-1)):
			beg_time = beg_time + diff
			new_start.append(beg_time)
			print("prev:%d\r\n "%prev)
			count = start_array.index(prev)
			print("count:%d\r\n "%count)
			for i in range(start_array.index(prev),start_array.index(beg_time)-1):
				count+=1
			new_finish.append(finish_array[count])
			prev = beg_time
		new_finish.append(max(finish_array))

	else:
		end_time = max(finish_array)
		new_start.append(beg_time)
		new_finish.append(int(end_time))
	return new_start,new_finish


def showMetrics():
	"""
	Displays the resultant metrics after scheduling such as
	average response time, the average waiting time and the
	time of first deadline miss
	"""
	N = []
	startTime = []
	releaseTime = []
	finishTime = []
	avg_respTime = []
	avg_waitTime = []
	n = len(tasks)
	# Calculation of number of releases and release time
	# for i in tasks.keys():
	#	if (tasks[i]["Observer"]==1):
	#		print("Execution intervals of the observer task: \r\n",ExecIntervals)
	#		break

	for i in tasks.keys():
		release = int(hp) / int(tasks[i]["Period"])
		N.append(release)
		temp = []
		for j in range(int(N[i])):
			temp.append(j * int(tasks[i]["Period"]))
		# temp.append(hp)
		releaseTime.append(temp)

	# Calculation of start time of each task
	for j, i in enumerate(tasks.keys()):
		start_array, end_array = filter_out(dList["TASK_%d" % i]["start"], dList["TASK_%d" % i]["finish"], N[j])
		startTime.append(start_array)
		finishTime.append(end_array)

	# Calculation of average waiting time and average response time of tasks
	for i in tasks.keys():
		avg_waitTime.append(st.mean([a_i - b_i for a_i, b_i in zip(startTime[i], releaseTime[i])]))
		avg_respTime.append(st.mean([a_i - b_i for a_i, b_i in zip(finishTime[i], releaseTime[i])]))

	# Printing the resultant metrics
	for i in tasks.keys():
		metrics[i]["Releases"] = N[i]
		metrics[i]["Period"] = tasks[i]["Period"]
		metrics[i]["WCET"] = tasks[i]["WCET"]
		metrics[i]["AvgRespTime"] = avg_respTime[i]
		metrics[i]["AvgWaitTime"] = avg_waitTime[i]

		print("\n Number of releases of task %d =" % i, int(N[i]))
		print("\n Release time of task%d = " % i, releaseTime[i])
		print("\n start time of task %d = " % i, startTime[i])
		print("\n finish time of task %d = " % i, finishTime[i])
		print("\n Average Response time of task %d = " % i, avg_respTime[i])
		print("\n Average Waiting time of task %d = " % i, avg_waitTime[i])
		print("\n")

	# Storing results into a JSON file
	with open('Metrics.json', 'w') as f:
		json.dump(metrics, f, indent=4)
	print("\n\n\t\tScheduling of %d tasks completed succesfully...." % n)

