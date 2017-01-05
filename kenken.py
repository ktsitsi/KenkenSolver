from csp import *
import ast
import sys
import time
#from collections import defaultdict


class KenKen(CSP):

	def __init__(self,inpfile):
		self.magnitude = 0
		self.vars = []
		self.clique = defaultdict(list)	#key: vars, value: (clique_id, numerical_expr)
		self.clique_neighbours = defaultdict(list) #key:vars , value = [cli_neighb1,cli_neighb2,...]
		self.domain = defaultdict(list)
		self.neighbours = defaultdict(list)
		self.parse_input(inpfile)

		#print("Vars:",self.vars)
		#print("Domains:",self.domain.items(),"\n")
		#print("Neighbours:",self.neighbours.items(),"\n")
		#print("Clique:",self.clique.items(),"\n")
		#print("Clique_Neighbours:",self.clique_neighbours.items(),"\n")

		CSP.__init__(self,self.vars,self.domain,self.neighbours,self.kenken_constraints)

	
	def parse_input(self,inpfile):
		with open(inpfile) as inputf:
			content = inputf.readlines()

		#magnitude of the given matrix of puzzle
		self.magnitude = int(content[0])

		constr_list = []
		parse_constr_list = content[1:]
		for i in parse_constr_list:
				i = i.strip('\n')
				i = i.split(" ")	#Now j will be a list with
				i[0] = ast.literal_eval(i[0])
				for j in i[0]:
					self.vars.append(j)
				i[2] = int(i[2])
				constr_list.append(i)

		#print(constr_list)
		for cid,const in enumerate(constr_list):
			for i in const[0]:
				self.clique[i].append((cid,const[1],const[2]))
		
		for i in self.vars:
			self.domain[i] = list(range(self.magnitude+1)[1::])

		#update the clique_neighbours dict
		for i in constr_list:
			for j in i[0]:
				for k in i[0]:
					if j != k:
						self.clique_neighbours[j].append(k)
		
		#add neighbours of same line and column
		for i in self.vars:
			for k in list(range(self.magnitude)):
				for j in list(range(self.magnitude)):
					if k == i[0] and j != i[1]:
						self.neighbours[i].append((k,j))
					elif k != i[0] and j == i[1]:
						self.neighbours[i].append((k,j))

	def same_clique(self,A,a,B,b):
		target = a
		ass = self.infer_assignment()
		assigned_clique = 0
		if self.clique[A][0][1] == 'add':
			for i in self.clique_neighbours[A]:
				if i in ass and i != B:
					assigned_clique += 1
					target += ass[i]
			target += b
			if assigned_clique == len(self.clique_neighbours[A])-1:
				return target == self.clique[A][0][2]
			elif assigned_clique < len(self.clique_neighbours[A])-1:
				return target < self.clique[A][0][2]
			else:
				return False
		elif self.clique[A][0][1] == 'mult':
			for i in self.clique_neighbours[A]:
				if i in ass and i != B:
					assigned_clique += 1
					target *= ass[i]
			target *= b
			if assigned_clique == len(self.clique_neighbours[A])-1:
				return target == self.clique[A][0][2]
			elif assigned_clique < len(self.clique_neighbours[A])-1:
				return target <= self.clique[A][0][2]
		elif self.clique[A][0][1] == 'sub':
			return abs(a-b) == self.clique[A][0][2]
		elif self.clique[A][0][1] == 'div':
			if max(a,b) == a:
				return a/b == self.clique[A][0][2]
			else:
				return b/a == self.clique[A][0][2]
		elif self.clique[A][0][1] == "''":
			return a == self.clique[A][0][2]

	def kenken_constraints(self,A,a,B,b):
		if A[0] == B[0] or A[1] == B[1]:
			#For same rows or same lines impose constraint of alldiff
			alldiff = (a != b)
			if alldiff == False:
				#print("VA:",A,"=",a,"|VB:",B,"=",b,"|ALL:",alldiff,"|CC: None","|Overall: False\n")
				return False
		if self.clique[A][0] == self.clique[B][0]:
			#if belong to same clique
			clique_constr = self.same_clique(A,a,B,b)
		else:
			#check only the constraint for the clique of A
			clique_constr = True
		#print("VA:",A,"=",a,"|VB:",B,"=",b,"|ALL:",alldiff,"|CC:",clique_constr,"|Overall:",clique_constr,"\n")
		return clique_constr
	def kenken_display(self,assignment):
		for i in list(range(self.magnitude)):
			for j in sorted(assignment.items()):
				if j[0][0] == i:
					print(j[1], end=" ")
			print('\n',end="")

inputfile = sys.argv[1]
algorithm = sys.argv[2]
if algorithm == 'bt':
	k = KenKen(inputfile)
	start_time = time.clock()
	result = backtracking_search(k)
	elapsed_time = time.clock() - start_time
	print("BT Duration: --- %s seconds ---"% elapsed_time)
	print("BT Assignments: --- %s assignments ---"% k.nassigns)
	k.kenken_display(result)
elif algorithm == 'btmrv':
	k = KenKen(inputfile)
	start_time = time.clock()
	result = backtracking_search(k, select_unassigned_variable=mrv)
	elapsed_time = time.clock() - start_time
	print("BT+MRV Duration: --- %s seconds ---"% elapsed_time)
	print("BT+MRV Assignments: --- %s assignments ---"% k.nassigns)
	k.kenken_display(result)
elif algorithm == 'btfc':
	k = KenKen(inputfile)
	start_time = time.clock()
	result = backtracking_search(k, inference=forward_checking)
	elapsed_time = time.clock() - start_time
	print("FC Duration: --- %s seconds ---"% elapsed_time)
	print("FC Assignments: --- %s assignments---"% k.nassigns)
	k.kenken_display(result)
elif algorithm == 'fcmrv':
	k = KenKen(inputfile)
	start_time = time.clock()
	result = backtracking_search(k, select_unassigned_variable=mrv,inference=forward_checking)
	elapsed_time = time.clock() - start_time
	print("FC+MRV Duration: --- %s seconds ---"% elapsed_time)
	print("FC+MRV Assignments: --- %s assignments ---"% k.nassigns)
	k.kenken_display(result)
elif algorithm == 'mac':
	k = KenKen(inputfile)
	start_time = time.clock()
	result = backtracking_search(k, inference=mac)
	elapsed_time = time.clock() - start_time
	print("MAC Duration: --- %s seconds ---"% elapsed_time)
	print("MAC Assignments: --- %s assignments ---"% k.nassigns )
	k.kenken_display(result)
elif algorithm == 'min':
	k = KenKen(inputfile)
	start_time = time.clock()
	result = min_conflicts(k)
	elapsed_time = time.clock() - start_time
	print("Min Duration: --- %s seconds ---"% elapsed_time)
	print("Min Assignments: --- %s assignments ---"% k.nassigns)
	k.kenken_display(result)
else:
	print("Wrong inline argument")