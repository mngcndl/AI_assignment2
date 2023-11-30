import copy
import random
import math


# 0 - horizontal
# 1 - vertical
class Word:
    def __init__(self, word, x_coord=0, y_coord=0, orientation=0):
        self.word = word
        self.x = x_coord
        self.y = y_coord
        self.orientation = orientation

    def __str__(self):
        return f"{self.word}, x: {self.x}, y: {self.y}, {'horizontal' if self.orientation == 0 else 'vertical'}"


class Crossword:
    def __init__(self, list_of_words):
        self.words = list_of_words
        self.fitness = self.new_fitness_counter()

    def __str__(self):
        to_print = ''
        for word in self.words:
            to_print += str(word) + "\n"
        return to_print

    # def count_fitness(self) -> float:
    #     corner_problems = 0
    #     border_problems = 0
    #     intersection_problems = 0
    #     intersection_successes = 0
    #     filled_cells_list = set()
    #     num_of_intersections = 0
    #
    #     # Intersection problems check
    #     for word in self.words:
    #         has_intersections = False
    #         for i in range(len(word.word)):
    #             if word.orientation == 0:
    #                 if (word.x, word.y + i) not in filled_cells_list:
    #                     filled_cells_list.add((word.x, word.y + i))
    #                 else:
    #                     has_intersections = True
    #                     for vertical_word in self.words:
    #                         if vertical_word.orientation == 1:
    #                             if (word.y + i == vertical_word.y and vertical_word.x < word.x < vertical_word.x +
    #                                     len(vertical_word.word)):
    #                                 if word.word[i] != vertical_word.word[abs(vertical_word.x - word.x)]:
    #                                     intersection_problems += 1
    #                                 else:
    #                                     intersection_successes += 1
    #                                 break
    #             else:
    #                 if (word.x + i, word.y) not in filled_cells_list:
    #                     filled_cells_list.add((word.x + i, word.y))
    #         if has_intersections: num_of_intersections += 1
    #
    #     for word in self.words:
    #         if word.orientation == 1:
    #             # Corner problems check
    #             if (word.x - 1, word.y) in filled_cells_list:
    #                 corner_problems += 1
    #             if (word.x - 1, word.y - 1) in filled_cells_list:
    #                 corner_problems += 1
    #             if (word.x - 1, word.y + 1) in filled_cells_list:
    #                 corner_problems += 1
    #             if (word.x + len(word.word), word.y) in filled_cells_list:
    #                 corner_problems += 1
    #             if (word.x + len(word.word), word.y - 1) in filled_cells_list:
    #                 corner_problems += 1
    #             if (word.x + len(word.word), word.y + 1) in filled_cells_list:
    #                 corner_problems += 1
    #
    #             # Border problems check
    #             border_problems_left = False
    #             border_problems_right = False
    #             for i in range(1, len(word.word)):
    #                 if (word.x + i, word.y - 1) in filled_cells_list and (word.x + i - 1, word.y - 1) in filled_cells_list:
    #                     border_problems_left = True
    #                 if (word.x + i, word.y + 1) in filled_cells_list and (word.x + i - 1, word.y + 1) in filled_cells_list:
    #                     border_problems_right = True
    #             border_problems += 1 if border_problems_left else 0
    #             border_problems += 1 if border_problems_right else 0
    #
    #     fitness_function_score = (- 2000 * corner_problems - 100 * border_problems - 0.5 * intersection_problems + 10000 * intersection_successes + num_of_intersections * 5)
    #     return fitness_function_score

    def parallel_neighbours_counter(self) -> int:
        parallel_neighbours = 0
        for i in range(len(self.words)):
            for j in range(i + 1, len(self.words)):
                if self.words[i].orientation == self.words[j].orientation:
                    if self.words[i].orientation == 0 and abs(self.words[i].x - self.words[j].x) == 1 :
                        filled_cells = set()
                        for letter_index in range(len(self.words[j].word)):
                            filled_cells.add(self.words[j].y + letter_index)
                        for letter_index in range(len(self.words[i].word)):
                            if self.words[i].y + letter_index in filled_cells:
                                parallel_neighbours += 1
                                break
                    if self.words[i].orientation == 1 and abs(self.words[i].y - self.words[j].y) == 1:
                        filled_cells = set()
                        for letter_index in range(len(self.words[j].word)):
                            filled_cells.add(self.words[j].x + letter_index)
                        for letter_index in range(len(self.words[i].word)):
                            if self.words[i].x + letter_index in filled_cells:
                                parallel_neighbours += 1
                                break
        return parallel_neighbours // 2

    def words_connection_counter(self) -> int:
        def dfs(x, y):
            if x < 0 or x >= 20 or y < 0 or y >= 20 or (x, y) in visited:
                return
            visited.add((x, y))
            for i in range(len(self.words)):
                w = self.words[i]
                for j in range(len(w.word)):
                    if w.orientation == 0 and (x, y) == (w.x + j, w.y):
                        for k in range(len(w.word)):
                            dfs(w.x + k, w.y)
                    elif w.orientation == 1 and (x, y) == (w.x, w.y + j):
                        for k in range(len(w.word)):
                            dfs(w.x, w.y + k)
        visited = set()
        for word in self.words:
            dfs(word.x, word.y)
        return len(visited)

    def overlaps_counter(self) -> int:
        overlaps = 0
        filled_cells = set()
        overlapped_cells = set()

        for word in self.words:
            for i in range(len(word.word)):
                cell = (word.x + i, word.y) if word.orientation == 0 else (word.x, word.y + i)
                if cell in filled_cells:
                    overlapped_cells.add(cell)
                filled_cells.add(cell)
        return overlaps

    def intersection_counter(self) -> [int, int]:
        incorrect_intersections = 0
        correct_intersections = 0
        filled_cells = set()
        for word in self.words:
            for i in range(len(word.word)):
                cell = (word.x + i, word.y) if word.orientation == 0 else (word.x, word.y + i)
                if cell in filled_cells:
                    for intersected_word in self.words:
                        if (
                            intersected_word.orientation == 1
                            and cell[0] == intersected_word.x
                            and intersected_word.y < cell[1] < intersected_word.y + len(intersected_word.word)
                        ):
                            if word.word[i] != intersected_word.word[abs(intersected_word.y - cell[1])]:
                                incorrect_intersections += 1
                            else:
                                correct_intersections += 1
                            break
                filled_cells.add(cell)
        return [incorrect_intersections, correct_intersections]

    def corner_counter(self) -> [int, int]: # incorrect, correct
        corner_problems = 0
        corners = 0
        filled_cells = set()
        for word in self.words:
            if word.orientation == 0:
                for i in range(len(word.word)):
                    filled_cells.add((word.x, word.y+i))
                    if 0 <= word.x <= 19 and 0 <= word.y+i <= 19:
                        corners += 1
            else:
                for i in range(len(word.word)):
                    filled_cells.add((word.x+i, word.y))
                    if 0 <= word.x+i <= 19 and 0 <= word.y <= 19:
                        corners += 1

        for word in self.words:
            if word.orientation == 1:
                if (word.x - 1, word.y) in filled_cells:
                    corner_problems += 1
                if (word.x - 1, word.y - 1) in filled_cells:
                    corner_problems += 1
                if (word.x - 1, word.y + 1) in filled_cells:
                    corner_problems += 1
                if (word.x + len(word.word), word.y) in filled_cells:
                    corner_problems += 1
                if (word.x + len(word.word), word.y - 1) in filled_cells:
                    corner_problems += 1
                if (word.x + len(word.word), word.y + 1) in filled_cells:
                    corner_problems += 1
            else:
                if (word.x, word.y - 1) in filled_cells:
                    corner_problems +=1
                if (word.x - 1, word.y - 1) in filled_cells:
                    corner_problems += 1
                if (word.x + 1, word.y - 1) in filled_cells:
                    corner_problems += 1
                if (word.x, word.y + len(word.word)) in filled_cells:
                    corner_problems += 1
                if (word.x - 1, word.y+len(word.word)) in filled_cells:
                    corner_problems += 1
                if (word.x + 1, word.y + len(word.word)) in filled_cells:
                    corner_problems += 1
        return [corner_problems, corners - corner_problems]

    def new_fitness_counter(self) -> float:
        overlaps = self.overlaps_counter()
        correct_intersections = self.intersection_counter()[1]
        fitness = (- self.parallel_neighbours_counter()
                   + 10 * self.words_connection_counter() / len(self.words)
                   - (overlaps - correct_intersections)
                   - self.intersection_counter()[0] + 5 * correct_intersections
                   - self.corner_counter()[0] + 5 * self.corner_counter()[1])
        if self.overlaps_counter() == self.intersection_counter()[1]:
            fitness += 5
        return fitness


    def print_crossword(self):
        crossword = [['.' for _ in range(20)] for _ in range(20)]
        for word in self.words:
            if word.orientation == 0:
                for i in range(len(word.word)):
                    if word.x <= 19 and word.y + i <= 19:
                        crossword[word.x][word.y + i] = word.word[i]
            else:
                for i in range(len(word.word)):
                    if word.x + i <= 19 and word.y <= 19:
                        crossword[word.x + i][word.y] = word.word[i]
        for i in range(20):
            cur_line = ""
            for j in range(20):
                cur_line += crossword[i][j] + ' '
            print(cur_line)
        return


def generate_crossword(words) -> Crossword:
    words_copy = copy.deepcopy(words)
    for word in words_copy:
        word.orientation = random.randint(0, 1)
        if word.orientation == 0:  # Horizontal
            word.x, word.y = random.randint(0, 19), random.randint(0, 20 - len(word.word))
        else:  # Vertical
            word.x, word.y = random.randint(0, 20 - len(word.word)), random.randint(0, 19)
    cw = Crossword(words_copy)
    return cw


def select_individuals(population, number_of_individuals):
    population.sort(key=lambda crossword: crossword.fitness, reverse=True)
    return population[:number_of_individuals]


def crossover_population(population, number_of_individuals):
    new_population = []
    population_size = len(population)

    while len(new_population) < number_of_individuals:
        parent1 = population[random.randint(0, population_size - 1)]
        parent2 = population[random.randint(0, population_size - 1)]
        while parent2 == parent1:
            parent2 = population[random.randint(0, population_size - 1)]

        crossover_point = random.randint(0, min(len(parent1.words), len(parent2.words)) - 1)
        child_words = parent1.words[:crossover_point] + parent2.words[crossover_point:]
        child = Crossword(child_words)
        new_population.append(child)
    return new_population


def mutate(population, number_of_individuals):
    new_population = []
    for i in range(number_of_individuals):
        random.seed(i)
        number_of_changes = random.randint(0, len(population[i].words))
        orientation_change = math.ceil(number_of_changes/random.randint(2,4))
        crossword = population[i]
        new_crossword = copy.deepcopy(crossword)

        for j in range(number_of_changes - orientation_change):
            random.seed(j)
            candidate1 = new_crossword.words[random.randint(0, math.ceil(len(new_crossword.words) / 2))]
            candidate2 = new_crossword.words[random.randint(math.ceil(len(new_crossword.words) / 2), len(new_crossword.words) - 1)]

            temp_x, temp_y = candidate1.x, candidate1.y
            candidate1.x, candidate1.y = candidate2.x, candidate2.y
            candidate2.x, candidate2.y = temp_x, temp_y

        for j in range(orientation_change):
            random.seed(j)
            candidate = new_crossword.words[random.randint(0, len(new_crossword.words) - 1)]
            if candidate.orientation == 0:
                candidate.orientation = 1
            else:
                candidate.orientation = 0

        new_population.append(new_crossword)
    return new_population



def main():
    words = []
    with open("input.txt", "r") as file:
        for line in file:
            word = Word(line.strip())
            words.append(word)

    # Generating the population
    population = []
    for _ in range(100):
        crossword = generate_crossword(words)
        population.append(crossword)
    # for cw in population:

    initial_babe = select_individuals(population,1)[0]
    initial_babe.print_crossword()
    print(initial_babe.fitness)
    print()

    generation_counter = 0
    max_generations = 200
    while generation_counter < max_generations:
        selected_individuals = select_individuals(population, 10)
        crossovered_individuals = crossover_population(population, 60)
        mutated_individuals = mutate(population, 30)
        population = selected_individuals + crossovered_individuals + mutated_individuals
        generation_counter += 1

    best_solution = select_individuals(population, 1)[0]
    best_solution.print_crossword()
    print(best_solution.fitness)


if __name__ == '__main__':
    main()
