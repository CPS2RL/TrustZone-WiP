#!/usr/bin/env python3
# ------------------------------------------
# RM_scheduling.py: RM
# Author: Aguida Mohamed Anis
# ------------------------------------------
import json
import copy
from sys import *
from math import gcd
from collections import OrderedDict
import matplotlib.pyplot as plt
import numpy as np
import statistics as st
from collections import defaultdict

tasks = dict()
RealTime_task = dict()
metrics = defaultdict(dict)
d = dict()
dList = {}
T = []
C = []
U = []
# For gantt chart
y_axis  = []
from_x = []
to_x = []

ExecIntervals = []
ExecStart = []
ExecFinish = []
ExecTemp= []


def createIDLE():
	global dList
	dList["TASK_IDLE"] = {"start": [], "finish": []}


def createTask(taskID,period,WCET,secure,observer):
	global hp
	global tasks
	global dList

	dList["TASK_%d"%taskID] = {"start":[],"finish":[]}
	tasks[taskID] = {}
	tasks[taskID]["Period"] = period
	tasks[taskID]["WCET"] = WCET
	tasks[taskID]["Secure"] = secure
	tasks[taskID]["Observer"] = observer

def jsonTask(tasks):
	with open('tasks.json','w') as outfile:
		json.dump(tasks,outfile,indent = 4)

def Hyperperiod():
	"""
	Calculates the hyper period of the tasks to be scheduled
	"""
	temp = []
	n = len(tasks)
	for i in range(n):
		temp.append(tasks[i]["Period"])
	HP = temp[0]
	for i in temp[1:]:
		HP = HP*i//gcd(HP, i)
	print ("\n Hyperperiod:",HP)
	return HP

def Schedulablity():
	"""
	Calculates the utilization factor of the tasks to be scheduled
	and then checks for the schedulablity and then returns true is
	schedulable else false.
	"""
	for i in range(len(tasks)):
		T.append(int(tasks[i]["Period"]))
		C.append(int(tasks[i]["WCET"]))
		u = int(C[i])/int(T[i])
		U.append(u)

	U_factor = sum(U)
	if U_factor<=1:
		print("\nUtilization factor: ",U_factor, "underloaded tasks")
		n=len(tasks)
		sched_util = n*(2**(1/n)-1)
		print("Checking condition: ",sched_util)

		count = 0
		T.sort()
		for i in range(len(T)):
			if T[i]%T[0] == 0:
				count = count + 1

		# Checking the schedulablity condition
		if U_factor <= sched_util or count == len(T):
			print("\n\tTasks are schedulable by Rate Monotonic Scheduling!")
			return True
		else:
			print("\n\tTasks are not schedulable by Rate Monotonic Scheduling!")
			return False
	print("\n\tOverloaded tasks!")
	print("\n\tUtilization factor > 1")
	return False

def estimatePriority(RealTime_task):
	"""
	Estimates the priority of tasks at each real time period during scheduling
	"""
	tempPeriod = hp
	P = -1    #Returns -1 for idle tasks
	for i in RealTime_task.keys():
		if (RealTime_task[i]["WCET"] != 0):
			if (tempPeriod > RealTime_task[i]["Period"] or tempPeriod > tasks[i]["Period"]):
				tempPeriod = tasks[i]["Period"] #Checks the priority of each task based on period
				P = i
	return P


def observer_func(t,counter):
	ExecStart.append(t)
	ExecFinish.append(t+1)


def Simulation(hp):
	"""
	The real time schedulng based on Rate Monotonic scheduling is simulated here.
	"""

	# Real time scheduling are carried out in RealTime_task
	global RealTime_task
	RealTime_task = copy.deepcopy(tasks)
	# validation of schedulablity neessary condition
	for i in RealTime_task.keys():
		RealTime_task[i]["DCT"] = RealTime_task[i]["WCET"]
		if (RealTime_task[i]["WCET"] > RealTime_task[i]["Period"]):
			print(" \n\t The task can not be completed in the specified time ! ", i )

	# main loop for simulator
	counter = 0
	for t in range(hp):

		# Determine the priority of the given tasks
		priority = estimatePriority(RealTime_task)

		if (priority != -1):    #processor is not idle
			if (RealTime_task[priority]["Observer"]==1):
				observer_func(t,counter)
				counter = counter + 1
			print("\nt{}-->t{} :TASK{}".format(t,t+1,priority))
			# Update WCET after each clock cycle
			RealTime_task[priority]["WCET"] -= 1
			# For the calculation of the metrics
			dList["TASK_%d"%priority]["start"].append(t)
			dList["TASK_%d"%priority]["finish"].append(t+1)
			# For plotting the results
			y_axis.append("TASK%d"%priority)
			from_x.append(t)
			to_x.append(t+1)

		else:    #processor is idle
			print("\nt{}-->t{} :IDLE".format(t,t+1))
			# For the calculation of the metrics
			dList["TASK_IDLE"]["start"].append(t)
			dList["TASK_IDLE"]["finish"].append(t+1)
			# For plotting the results
			y_axis.append("IDLE")
			from_x.append(t)
			to_x.append(t+1)

		# Update Period after each clock cycle
		for i in RealTime_task.keys():
			RealTime_task[i]["Period"] -= 1
			if (RealTime_task[i]["Period"] == 0):
				RealTime_task[i] = copy.deepcopy(tasks[i])

		with open('RM_sched.json','w') as outfile2:
			json.dump(dList,outfile2,indent = 4)


def drawGantt():
	"""
	The scheduled results are displayed in the form of a
	gantt chart for the user to get better understanding
	"""

	i=0
	j=0
	print(len(ExecStart) - 2)
	while (j <= len(ExecFinish)-1):
		while (j < len(ExecFinish)-1) and (ExecFinish[j]==ExecStart[j+1]):
			j= j+1
			print(j)
		ExecTemp.append({"start":ExecStart[i],"finish":ExecFinish[j]})
		j=j+1
		i=j
	for i in tasks.keys():
		if (tasks[i]["Observer"]==1):
			print("Execution intervals of the observer task: \r\n",ExecTemp)
			break

	n= len(tasks)
	colors = ['red','green','blue','orange','yellow']
	fig = plt.figure()
	ax = fig.add_subplot(111)
	# the data is plotted from_x to to_x along y_axis
	ax = plt.hlines(y_axis, from_x, to_x, linewidth=20, color = colors[n-1])
	plt.title('Rate Monotonic scheduling')
	plt.grid(True)
	plt.xlabel("Real-Time clock")
	plt.ylabel("HIGH------------------Priority--------------------->LOW")
	plt.xticks(np.arange(min(from_x), max(to_x)+1, 1.0))
	plt.show()





def timewindow(victimperiod,hyperperiod,observerExec):
	ladder =[0] * hyperperiod
	for i in range(len(observerExec)):
		for j in range(observerExec[i]["start"],observerExec[i]["finish"]):
			ladder[j]=1
	result = [0] * victimperiod
	for i in range(len(ladder)):
		result[i % victimperiod] += ladder[i]

	print(ladder)
	print(result)




if __name__ == '__main__':

	print("\n\n\t\t_RATE MONOTONIC SCHEDULER_\n")

	#Read_data()
	#IDLE task

	# from paper
	#createTask(0, 10, 3, 1, 0)
	#createTask(1,100,15,1,0)
	#createTask(2, 200, 15, 1, 0)
	#createTask(3,400,40,1,0)
	#createTask(4, 1000, 30, 0, 1)
	#createTask(5, 1000, 200, 1, 0)

	createTask(0, 5, 2, 1, 0)
	createTask(1,8,1,1,0)
	createTask(2, 10, 2, 0, 1)
	createIDLE()
	#print(tasks)
	jsonTask(tasks)

	sched_res = Schedulablity()
	if sched_res == True:

		hp = Hyperperiod()
		Simulation(hp)
		drawGantt()
		timewindow(5,hp,ExecTemp)

	else:
		#Read_data()
		sched_res = Schedulablity()
