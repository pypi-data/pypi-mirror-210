import numpy as np
import random
import matplotlib.pyplot as plt
import numpy.random as npr

#Code author: Sriram Ranganathan, Meng. ECE, University of Waterloo
class candidate:
  def __init__(self, bitstream,  fitness = 0.00):
    self.fitness = fitness
    self.bitstream = bitstream
  def __eq__(self, x):
    if self.bitstream == x.bitstream:
      return True
    return False


class top_solution:
  def __init__(self, new,  iter = 0):
    self.iter = iter
    self.new = new


#Code author: Sriram Ranganathan, Meng. ECE, University of Waterloo
class Genetic_algorithm:

  def __init__(self, input_data_x, input_data_y, max_population, crossover_prob, mutation_r, stop_by_f, stop_fitness, fitness_func):
    self.input_data_x = input_data_x
    self.input_data_y = input_data_y.to_numpy()
    self.max_population = max_population
    self.columns = self.input_data_x.columns
    self.fitness_func = fitness_func
    self.populate()
    self.calculate_fitness()
    self.mating_pool_size = max_population//5
    self.crossover_prob = crossover_prob
    self.mutation_r = mutation_r
    self.Best_solutions = []
    self.Best_solutions_bit = []
    self.Best_iteration = 0 
    self.stop_fitness = stop_fitness
    self.stop_by_f = stop_by_f
    self.fitness_dispersion = []
    self.len_bitstream_dispersion = []

  def train_test_split(self, train_x, train_y, test_size):
    data = list(zip(train_x, train_y))  # Combine train_x and train_y
    random.shuffle(data)  # Shuffle the data randomly
    test_size = int(len(train_x)*test_size)
    split_index = len(data) - test_size
    train_data = data[:split_index]
    test_data = data[split_index:]
    train_x, train_y = zip(*train_data)  # Unzip the train_data
    test_x, test_y = zip(*test_data)  # Unzip the test_data
    return train_x, train_y, test_x, test_y

  def evolve(self, no_iters):
    print("Genetic Algorithm Evolving")
    i = 0
    self.average = []
    self.Top_sols = []
    self.worst_sols = []
    self.tot_crossov = []
    self.tot_mut = []
    l = range(0,no_iters)
    self.crossover = 0
    self.mutation = 0
    for i in l:
      top_sol = self.current_population[0]
      self.Best_solutions.append(top_sol.fitness)
      self.Best_solutions_bit.append(top_sol.bitstream)
      print("Top solution fitness "+ str(top_sol.fitness))
      print("Iteration_No: ", i)
      
      fitness = [m.fitness for m in self.current_population]
      self.average.append(sum(fitness)/len(fitness))
      self.Top_sols.append(max(fitness))
      self.worst_sols.append(min(fitness))
      if ((top_sol.fitness > self.stop_fitness) & (self.stop_by_f)):
        return top_sol
      self.current_population = self.cross_over_mutate(self.current_population)
      self.calculate_fitness()
      i+=1
      self.current_population.sort(key=lambda x: x.fitness, reverse=True)
      self.tot_crossov.append(self.crossover)
      self.tot_mut.append(self.mutation)
    best_ind = np.argmax(self.Best_solutions)
    best_bit_stream = np.array(self.Best_solutions_bit[best_ind])
    columns_to_keep = np.where(best_bit_stream == 1)[0].tolist()
    return max(self.Best_solutions), columns_to_keep


  def populate(self, initial = False):
    print("Creating Initial population")
    self.current_population = []
    for i in range(0,self.max_population):
      bitstream = []
      for i in self.input_data_x.columns:
        if random.randrange(10)<=5:
          bitstream.append(1)
        else:
          bitstream.append(0)
      
      new_cand = candidate(bitstream)
      rep = False
      for i in self.current_population:
        if bitstream == i.bitstream:
          rep = True
          break
      if rep == True:
        continue
      self.current_population.append(new_cand)
    return

  def calculate_fitness(self):
    print("Calculating fitness")
    
    for i in self.current_population:
      new_data_frame = self.input_data_x
      bitstream = i.bitstream
      drop_columns = []
      for k in range(0,len(bitstream)):
        if bitstream[k] == 1:
          continue
        if bitstream[k] == 0:
          drop_columns.append(self.columns[k])
        
      new_data_frame = self.input_data_x.drop(drop_columns, axis = 1)
      Train_x = new_data_frame.to_numpy()
      X_train, y_train ,X_test, y_test = self.train_test_split(Train_x, self.input_data_y, 0.2)
      i.fitness = self.fitness_func(X_train, y_train, X_test, y_test, )
    return
  
  def roulette_select_one(self, c_population):
    max = sum([f.fitness for f in c_population])
    probs = [f.fitness/max for f in c_population]
    return c_population[npr.choice(len(c_population), p=probs)]
  

  def cross_over_mutate(self, current_population):
    self.fitness_dispersion.append([f.fitness for f in self.current_population])
    y = [np.array(f.bitstream) for f in self.current_population]
    y = [np.sum(l) for l in y]
    self.len_bitstream_dispersion.append(y)
    current_population.sort(key=lambda x: x.fitness, reverse=True)
    new_population = current_population[0:2]
    print("Top 2 Fitness of new population", new_population[0].fitness, new_population[1].fitness)
    mating_pool = current_population[:self.mating_pool_size].copy()
    m = 0
    while(len(new_population)<len(current_population)):
      n = m
      if m>=len(mating_pool):
        n = m%len(mating_pool)
      p1 = self.roulette_select_one(mating_pool)
      new_mating_pool = mating_pool.copy()
      new_mating_pool.pop(n)
      new_cand = candidate([], 0)
      if random.uniform(0, 1)<=self.crossover_prob:
        self.crossover+=1
        p2 = self.roulette_select_one(mating_pool)
        trait_split = random.randrange(self.input_data_x.shape[1])
        L = [k for k in range(trait_split,self.input_data_x.shape[1])]
        trait_split1 = random.choice(L)
        new_bitstream = self.mutate(p1.bitstream[0:trait_split] + p1.bitstream[trait_split:trait_split1]+p2.bitstream[trait_split1:])
        new_cand.bitstream = new_bitstream
        bs = [str(k) for k in new_cand.bitstream]
        rep = False
        new_population.append(new_cand)
      m+=1
    current_population = new_population.copy()
    
    current_population.sort(key=lambda x: x.fitness, reverse=True)
    return current_population
  

  def mutate(self, bitstream):
    for i in range(0,len(bitstream)):
      if random.uniform(0, 1)<=self.mutation_r:
        self.mutation
        if bitstream[i]==0:
          bitstream[i] = 1
        else:
          bitstream[i] = 0
    return bitstream

  def plot(self, path):
    try:
      plt.plot(range(0,len(self.Top_sols)),self.average, label = "Avg Fitness")
      plt.plot(range(0,len(self.Top_sols)),self.Top_sols, label = "Max Fitness")
      plt.plot(range(0,len(self.Top_sols)),self.worst_sols, label = "Min Fitness")

      plt.xlabel('Generations') 
      plt.ylabel('Validation Accuracy from solutions(fitness)') 
      plt.legend(loc="lower right")

      # displaying the title
      plt.title("White wine")
      plt.savefig(path)
    except:
      print("Please evolve first")
    return