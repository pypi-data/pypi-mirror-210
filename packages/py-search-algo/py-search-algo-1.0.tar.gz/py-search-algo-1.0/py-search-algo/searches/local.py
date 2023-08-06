import random 
import math
import numpy as np
from sympy import symbols, Eq, solve,parse_expr
import copy
import numbers
import math
import random
import heapq
from queue import PriorityQueue
import sys
sys.path.append("G:\\ai_project")
sys.path.append("G:\\ai_project\\src")
sys.path.append("G:\\ai_project\\src\\searches")
sys.path.append("G:\\ai_project\\src\\games")
sys.path.append("G:\\ai_project\\src\\utile")
from src.utile.util import *
from src.utile.problem import *


class local:
    def  __init__(self):
        pass

    @staticmethod
    def local_beam(problem, heuristic, k):
        path = []
        # Initialize k random states
        current_states = [problem.random_state() for _ in range(k)]
        while True:
            # Generate all the successors of the current k states
            successors = []
            for state in current_states:
                successors.extend(problem.generate_successors(state))
            if len(successors) == 0:
                break
            # Select k best states from successors
            next_states = sorted(successors, key=lambda successor: heuristic(successor, problem.goal), reverse=True)[:k]
            # If one of the next states is the goal, return it
            for next_state in next_states:
                if problem.test_goal(next_state):
                    return next_state
            # If none of the next states is better than current states, break
            if all(heuristic(next_state, problem.goal) <= heuristic(current_state, problem.goal) for next_state, current_state in zip(next_states, current_states)):
                break
            # Select the k best states from the next states
            current_states = sorted(next_states, key=lambda state: heuristic(state, problem.goal), reverse=True)[:k]
        # Return the best state from current k states
        return path,max(current_states, key=lambda state: heuristic(state, problem.goal))


    @staticmethod
    def simulated_annealing(problem,initial_temp,final_temp,max_iter,heuristic):
        current_state = problem.random_state()
        current_state_h = heuristic(current_state,problem.goal)
        current_temp = initial_temp
        path = [current_state]
        iter = 1
        while current_temp > final_temp and iter < max_iter :
            next_states = problem.generate_successors(current_state)
            for next_state in next_states :
                next_state_h = heuristic(next_state,problem.goal)
                Delta = next_state_h - current_state_h
                #if the new solution is better, accept it
                if Delta > 0 :
                    current_state = next_state
                    current_state_h = next_state_h
                #if it is not, accept it with some probability less than 1
                else :
                    if math.exp(-Delta / current_temp) > random.uniform(0, 1) :
                        current_state = next_state
                        current_state_h = next_state_h
                        
                #calculate temperature using logarithmic cooling schedule
                
                current_temp = initial_temp / math.log(iter + 1)
            iter += 1
            path.append(current_state)
        return path,current_state




    #steepest ascent hill climbing algorithm
    @staticmethod
    def steepest_ascent_hc(problem,heuristic):
        current_state = problem.root
        path = [current_state]
        while not problem.test_goal(current_state): #loop until the current state is the goal state of the problem
                successors = problem.generate_successors(current_state)
                best_state = None
                for successor in successors:
                    if not best_state: # i changed this hb
                        best_state = successor  # i changed this hb
                    if problem.test_goal(successor) :
                        path = path + [successor]
                        return path,successor
                    elif heuristic(successor,problem.goal) < heuristic(best_state,problem.goal):
                        best_state = successor
                if  heuristic(best_state,problem.goal) <  heuristic(current_state,problem.goal):
                    current_state = best_state
                
                path = path + [best_state]
                
        return path,current_state
                
    #first choice hill climbing algorithm
    @staticmethod
    def first_choice_hc(problem,heuristic):
        current_state = problem.root
        path = [current_state]
        while not problem.test_goal(current_state):
            successors = problem.generate_successors(current_state)
            temp = current_state
            for successor in successors:
                if problem.test_goal(successor):
                        path = [successor]
                        return path,successor
                elif heuristic(successor,problem.goal) < heuristic(current_state,problem.goal):
                    current_state = successor 
                    break
            if current_state == temp :
                #going down? must return failure i guess
                    return path,None
            path = path+[current_state]
        return path,current_state

    @staticmethod
    #stochastic hill climbing algorithm
    def stochastic_hc(problem,heuristic):
        current_state = problem.root  # Initialize current solution
        path = [current_state]
        while not problem.test_goal(current_state):
            successors = problem.generate_successors(current_state) # Generate neighboring solutions
            #random.shuffle(successors)  # Shuffle the neighbors randomly to introduce stochasticity
            
            if isinstance(successors,dict):
                l = list(successors.items())
                random.shuffle(l)
                successors = dict(l)
            else:
                random.shuffle(successors)
            
            # Select the first improving neighbor, if any
            temp = current_state
            for successor in successors:
                if problem.test_goal(successor):
                        path = path + [successor]
                        return path,successor
                if   heuristic(successor,problem.goal) < heuristic(current_state,problem.goal):
                    current_state = successor
                    break
            if current_state == temp :
                #going down? must return failure i guess
                    return path,None
            path = path + [current_state]
        return path,current_state

    #random restart hill climbing algorithm
    @staticmethod
    def random_restart_hc(problem,h,max_restarts=100):
        count=0
        current_state = problem.root
        path = []
        while (not current_state or (not problem.test_goal(current_state) )) and count < max_restarts:
            path,current_state = steepest_ascent_hc(problem,h)
            count +=1
        return path,current_state



    #selection methods 
    @staticmethod
    def roulette_wheel_selection(population,k,fitness):
        f_score = []
        final=[]
        result = []
        f_score = [fitness(i) for i in population]
        total_proba=sum(f_score)
        f_score = [i/total_proba for i in f_score]
        result,f_score = mergeSort(population,f_score,"dsc")
        cumulative_probs = [0]*len(f_score)
        cumulative_probs = np.cumsum(f_score)
        final_indices = np.searchsorted(cumulative_probs, np.random.rand(len(result)))
        final_indices = final_indices.astype(int)
        f_score = [f_score[i] for i in final_indices]
        final =  [result[i] for i in final_indices]
        final,_ = mergeSort(final,f_score,"asc")
        return final
    @staticmethod
    def stochastic_universal_sampling(pupulation,k,fitness):
        result = []
        f_score2 = []
        f_score = [fitness(i) for i in pupulation]
        total_proba=sum(f_score)
        distance = int(total_proba/k) if not int(total_proba/k) == 0 else 1
        start = random.randint(0,distance)
        pupulation,f_score= mergeSort(pupulation,f_score,"dsc")
        pointers = [start+i*distance for i in range(0,k)]
        cumultative = 0 
        for p in pointers:
            i = 0 
            try:
                while sum([f_score[k] for k in range(0,i+1)]) < p:
                    i += 1
            except:
                nothing = 0 #do nothing out of range cant put the if statement there or else its gonna be an infinite loop
            if(i>=len(pupulation)):
                i = i%len(pupulation)
            result = result +[pupulation[i]]
            f_score2 = f_score2 + [f_score[i]]
        result,_= mergeSort(result,f_score2,"asc")
        return result
        
    @staticmethod
    def tournament_selection(population,k,fitness):
        final = []   
        f_scores = []
        for _ in range(k):
            temp = []
            f_score = 0
            best = 0
            for i in range(len(population)):
                temp = temp + [random.choice(population)]
                if f_score < fitness(temp[-1]):
                    f_score = fitness(temp[-1])
                    best = i    
            final = final + [temp[best]]
            f_scores = f_scores + [f_score]
        final,_= mergeSort(final,f_scores,"asc") 
        return final

    #ranked 
    @staticmethod
    def tournament_selection(population,k,fitness):
        final = []   
        f_scores = []
        for _ in range(k):
            temp = None
            f_score = 0
            best = 0
            for i in range(len(population)):
                temp =  random.choice(population)
                if temp is None or f_score < fitness(temp):
                    f_score = fitness(temp)
                    best = str(temp) 
            final = final + [best]
            f_scores = f_scores + [f_score]
        final,f_scores= mergeSort(final,f_scores,"asc") 
        return final

    @staticmethod
    def linear_ranked_selection(population,k,fitness,sp=1.5):
        #sp which can take values between 1.0 (no selection pressure) and 2.0 (high selection pressure)
        if sp > 2 or sp < 1 :
            sp = 1.5
        f_score = [fitness(i) for i in population]
        result,f_score= mergeSort(population,f_score,"dsc")
        #calculating the probabilities 
        #f_score = [(sp-((2*sp-2)*((i-1)/(len(result)-1))))/len(result) for i in range(1,len(result)+1)] uses desc order
        f_score = [(2-sp+2*(sp-1)*((i-1)/(len(result)-1)))/len(result) for i in range(1,len(result)+1)] 
        chosen_indices = np.random.choice(np.arange(len(result)), size=k, p=f_score, replace=False)
        f_score = [f_score[i] for i in chosen_indices]
        result = [result[i] for i in chosen_indices]
        result,_ = mergeSort(result,f_score,"asc")
        
        return result
    @staticmethod
    def non_linear_ranked_selection(population,k,fitness,sp=1.5):
        #doesnt work if the root in non real
        #permits higher selective pressures than the linear ranking method
        if sp > 2 or sp < 1 :
            sp = 1.5
        f_score = [fitness(i) for i in population]
        result,f_score= mergeSort(population,f_score,"dsc")
        #0=(SP-1) X^(Nind-1)+SP X^(Nind-2)+...+SP X+SP.
        equation = ""
        for i in range(1,len(result)+1):
            equation+= f"+{sp}*(x**({str(len(result)-i)}))"
        equation = f"{sp-1}*"+equation[1:]+"+"+str(sp)
        equation = parse_expr(equation)
        sol = solve(Eq(equation,0))[0]  
        if isinstance(sol, complex):
            return None
        #Fitness(Pos)=Nind X^(Pos-1)/sum(X^(i-1)); i=1...Nind. x is the sol variable
        f_score = [float(((sol**(i-1))*len(result))/((1 - sol**(len(result)-1)) / (1 - sol))) for i in range(1,len(result)+1)] 
        #if not sum(f_score) == 1:
        for i in range(len(result)+1) : 
            if f_score[i]>=0  :
                f_score[i] = f_score[i]/sum(f_score) 
            else : 
                f_score.remove(f_score[i])
            
        if(len(f_score) == 0):
            return None
        chosen_indices = np.random.choice(np.arange(len(f_score)), size=k, p=f_score, replace=False)
        f_score = [f_score[i] for i in chosen_indices] 
        result = [result[i] for i in chosen_indices]
        result,_ = mergeSort(result,f_score,"asc")
        return result 
        
        
    #random usualy avoided 
    @staticmethod
    def random_selection(population,k):
        return np.random.choice(result, size=k)


    # crossover methods
    @staticmethod
    def one_point_crossover(parents,crossover_probability=.8):
        children = []
        for i in range(0,len(parents),2):
            if math.floor(random.random())  <= crossover_probability: 
                random_point = random.randint(0,len(parents[0])-1)
                children = children + [parents[i][:random_point]+parents[i+1][random_point:]]
                children = children + [parents[i][random_point:]+parents[i+1][:random_point]]
            else:
                children = children + [parents[i],parents[i+1]]

        return children

    #Uniform Crossover
    '''In this type of crossover, 
    each gene for an offspring is selected with 0.5 probability from Parent-1 and 0.5 probability from Parent-2.
    If a gene from parent – 1 is selected, the same indexed gene from parent – 2 is chosen for the other offspring. 
    It is demonstrated in the following diagram.
    '''
    @staticmethod
    def uniform_crossover(parents,crossover_probability=.8):
        children = []
        for i in range(0,len(parents),2):
            if math.floor(random.random())  <= crossover_probability: 
                mask = [random.randint(0,1) for i in range(len(parents[0]))]
                child = ""
                child2 = ""
                for i in range(len(parents[0])):
                    child = child + parents[i+mask[i]][i]
                    child2 = child2 + parents[i+1-mask[i]][i]
                children = children + [child,child2]
            else:
                children = children + [parents[i],parents[i+1]]
        return children



    #multipoint crossover
    @staticmethod
    def multipoint_crossover(parents,crossover_probability=.8,points=2):
        children = []
        if points > len(parents[0]):
            points = len(parents[0])-1
        for i in range(0,len(parents),2):
            if math.floor(random.random())  <= crossover_probability: 
                child = ""
                child2 = ""
                a = random.sample(range(1, len(parents[0])), points)
                random_points,_ = mergeSort(a,a ,"dsc" )
                parent_is = 0 
                current = 0
                for k,point in enumerate(random_points):
                    if k == len(random_points)-1:
                        point = len(parents[0])
                    child +=   parents[i+parent_is][current:point]
                    child2 +=   parents[i+1-parent_is][current:point]
                    parent_is = 1 - parent_is #permutate parents 
                    current = point
                children = children + [child,child2]
            else:
                children = children + [parents[i],parents[i+1]]
        return children




    #mutation methods 
    @staticmethod
    #Swap mutation: This method involves swapping the values of two genes within an individual's chromosome.
    def swap_mutation(generation,mutation_rate=0.01):
        for i in range(0,len(generation)-1) :
            if math.floor(random.random()) <= mutation_rate:
                random_f_point = random.randint(0,len(generation[0])-1)
                random_s_point = random.randint(0,len(generation[0])-1)
                temp = generation[i][random_f_point]
                generation[i] = generation[i][:random_f_point]+generation[i+1][random_s_point]+generation[i][random_f_point+1:]
                generation[i+1] = generation[i+1][:random_s_point]+temp+generation[i+1][random_s_point+1:]            
        return generation
    @staticmethod
    #Random mutation: This method involves randomly changing one or more genes in an individual's chromosome to a new value.
    def random_initialization(generation,genes,mutation_rate=0.01):
        for i in range(0,len(generation)) :
            if math.floor(random.random()) <= mutation_rate:
                random_point = random.randint(0,len(generation[0])-1)
                random_gene = genes[random.randint(0,len(genes)-1)]
                generation[i] = generation[i][:random_point]+random_gene+generation[i][random_point+1:]
        return generation

    @staticmethod
    def random_mutation(generation,genes,mutation_rate=0.01,genes_number=1):
        if genes_number > len(generation[0]) : 
            genes_number = len(generation[0])
        for i in range(0,len(generation)) :
            if math.floor(random.random()) <= mutation_rate:
                random_gene = copy.deepcopy(generation[i])
                for k in range(0,genes_number):
                    random_point = random.randint(0,len(generation[0])-1)
                    random_gene = genes[random.randint(0,len(genes)-1)]
                    generation[i] = generation[i][:random_point]+random_gene+generation[i][random_point+1:]
                generation[i] = generation[i][:random_point]+random_gene+generation[i][random_point+1:]
        return generation
        
        
    #Inversion mutation: This method involves reversing the order of a sequence of genes within an individual's chromosome.

    @staticmethod
    def inversion_mutation(generation,genes,mutation_rate=0.01,genes_number=1):
        if genes_number > len(generation[0]) : 
            genes_number = len(generation[0])
        for i in range(0,len(generation)) :
            if math.floor(random.random()) <= mutation_rate:
                if not genes_number :
                    genes_number = 0
                while genes_number == 0 :
                    random_point = random.randint(0,len(generation[0])-1)
                    genes_number = random.randint(0,len(generation[0])-random_point)
                    generation[i] = generation[i][:random_point]+generation[i][random_point:random_point+genes_number][::-1]+generation[i][random_point+genes_number:]
        return generation


    #Scramble mutation: This method involves reversing the order of a sequence of genes within an individual's chromosome.

    @staticmethod
    def scramble_mutation(generation,genes,mutation_rate=0.01,genes_number=1):
        if genes_number > len(generation[0]) : 
            genes_number = len(generation[0])
        for i in range(0,len(generation)) :
            if math.floor(random.random()) <= mutation_rate:
                if not genes_number :
                    genes_number = 0
                while genes_number == 0 :
                    random_point = random.randint(0,len(generation[0])-1)
                    genes_number = random.randint(0,len(generation[0])-random_point)
                    scrumbled = ''.join(random.sample(generation[i][random_point:random_point+genes_number], genes_number))
                    generation[i] = generation[i][:random_point]+scrumbled+generation[i][random_point+genes_number:]
        return generation
    
    @staticmethod
    #Boundary mutation: This method involves changing the value of a gene in an individual's chromosome to the nearest boundary value if it exceeds the allowed range.
    def boundary_mutation(generation,genes,bondary_a,bondary_b,mutation_rate=0.1,genes_number=1):
        if genes_number > len(generation[0]) : 
            genes_number = len(generation[0])
        for i in range(0,len(generation)) :
            if math.floor(random.random()) <= mutation_rate:
                for k in range(0,genes_number):
                    random_point = random.randint(0,len(generation[0])-1)
                    random_gene = genes[random.randint(0,len(genes)-1)]
                    random_gene = max(bondary_a,random_gene) #to stay in boundary 
                    random_gene = min(random_gene,bondary_b) #to stay in boundary 
                    generation[i] = generation[i][:random_point]+random_gene+generation[i][random_point+1:]
                generation[i] = generation[i][:random_point]+random_gene+generation[i][random_point+1:]
        return generation



    '''
    Gaussian mutation: This method involves adding a small random value to each gene in an individual's chromosome, with the random values drawn from a Gaussian distribution.
    '''
  
    @staticmethod
    def GA(population, fitness,genes, k=30, mutation_rate=0.01, crossover_probability=0.8, fit_limit=1, time_limit=float("inf"),selection_function="roulette_wheel",crossover_function="one_point",mutation_function="random",sp=1.5,crossover_points_number=2,mutation_genes_number=1,boundary_a=None,boundary_b=None):
            solution = None
            initial_population = []
            time = 0

            initial_population = population
            generation = 0
            path = []
            mutate,crossover,select = None,None,None
            
            if selection_function == "SUS":
                select = local.stochastic_universal_sampling
            elif selection_function == "tournament":
                select = local.tournament_selection
            elif selection_function == "l_ranked":
                select = local.linear_ranked_selection
            elif selection_function == "NL_ranked":
                select = local.non_linear_ranked_selection
            elif random  == "SUS":
                select = local.random_selection
            else :
                select = local.roulette_wheel_selection



            if crossover_function == "uniform" :
                crossover = local.uniform_crossover
            elif crossover_function == "multi_point":
                crossover = local.multipoint_crossover
            else:
                crossover = local.one_point_crossover

            if mutation_function == "swap" :
                mutate = local.swap_mutation
            elif mutation_function == "inverse":
                mutate = local.inversion_mutation
            elif mutation_function == "scramble":
                mutate = local.scramble_mutation
            elif mutation_function == "boundary":
                mutate = local.boundary_mutation
                if not boudary_a:
                    boundary_a = min(genes)
                if not boudary_b:
                    boudary_b = max(genes)
            else:
                mutate = local.random_mutation

            next_generation_parents,next_generation_children,next_generation_embryos=[],[],[]

            while not solution:
                
                generation +=1
                if selection_function == "random":
                    next_generation_parents = select(initial_population,k)
                elif selection_function == "NL_ranked" or selection_function == "l_ranked":
                    next_generation_parents = select(initial_population,k, fitness,sp)
                else : 
                    next_generation_parents = select(initial_population,k, fitness)


                if fitness(next_generation_parents[0])>=fit_limit:
                    return next_generation_parents[0],path

                if time_limit != float("inf") and time > time_limit:
                    return next_generation_parents[0],path

                if crossover_function=="multi_point":
                    next_generation_embryos = crossover(next_generation_parents, crossover_probability,crossover_points_number)
                
                else :
                    next_generation_embryos = crossover(next_generation_parents, crossover_probability)            

                if mutation_function == "swap":
                    next_generation_children = mutate(next_generation_embryos, mutation_rate)
                elif mutation_function == "boundary":
                    next_generation_children = mutate(next_generation_embryos,genes,boundary_a,boundary_b, mutation_rate,mutation_genes_number)
                elif mutation_function == "inverse":
                    next_generation_children = mutate(next_generation_embryos,genes,mutation_rate,mutation_genes_number)
                else :
                    next_generation_children = mutate(next_generation_embryos,genes, mutation_rate)

                initial_population = next_generation_children
                path.append(next_generation_parents[0])   
                # Check time limit
                if time_limit != float("inf"):
                    time += 1
            
            return solution,path
        
        