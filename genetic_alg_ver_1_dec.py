import copy
import math
import random
import time


# 0 - horizontal
# 1 - vertical
class Word:
    def __init__(self, word, x_coord=0, y_coord=0, orientation=0):
        self.word = word
        self.x = x_coord
        self.y = y_coord
        self.orientation = orientation
        self.occupied_cells = get_filled_cells(self)

    def __str__(self):
        # return f"{self.word}, x: {self.x}, y: {self.y}, {'horizontal' if self.orientation == 0 else 'vertical'}"
        return f"{self.word}"

    def __len__(self):
        length = 0
        while length < len(self.word):
            length += 1
        return length

    def __getitem__(self, index):
        return str(self.word)[index]

class Crossword:
    def __init__(self, list_of_words):
        self.words = list_of_words
        self.fitness = self.new_fitness_counter()

    def __str__(self):
        to_print = ''
        for word in self.words:
            to_print += str(word) + "\n"
        return to_print

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

    def parallel_neighbours_counter(self) -> int:
        parallel_neighbours = 0
        visited_pairs = set()
        counted_words = set()

        for i in range(len(self.words)):
            for j in range(i + 1, len(self.words)):
                if self.words[i].orientation == self.words[j].orientation:
                    pair = (min(i, j), max(i, j))
                    if pair not in visited_pairs:
                        visited_pairs.add(pair)
                        if self.words[i].orientation == 0:
                            if abs(self.words[i].x - self.words[j].x) == 1:
                                cells_of_first_word = set()
                                for k in range(len(self.words[i].word)):
                                    cells_of_first_word.add(self.words[i].y + k)

                                for k in range(len(self.words[j].word)):
                                    if (self.words[j].y + k) in cells_of_first_word:
                                        parallel_neighbours += 1
                                        if self.words[j] not in counted_words and self.words[i] not in counted_words:
                                            parallel_neighbours += 1
                                            counted_words.add(self.words[j])
                                            counted_words.add(self.words[i])
                                        break
                        else:
                            if abs(self.words[i].y - self.words[j].y) == 1:
                                cells_of_first_word = set()
                                for k in range(len(self.words[i].word)):
                                    cells_of_first_word.add(self.words[i].x + k)

                                for k in range(len(self.words[j].word)):
                                    if (self.words[j].x + k) in cells_of_first_word:
                                        parallel_neighbours += 1
                                        if self.words[j] not in counted_words and self.words[i] not in counted_words:
                                            parallel_neighbours += 1
                                            counted_words.add(self.words[j])
                                            counted_words.add(self.words[i])
                                        break
        return parallel_neighbours

    def not_connected_words_counter(self) -> int:
        filled_cells = set()
        for word in self.words:
            filled_cells.union(word.occupied_cells)

        # connected_words = set()
        has_intersections_with_other_words = [0 for _ in range(len(self.words))]
        index = 0
        for word in self.words:
            word.occupied_cells = get_filled_cells(word)

        for word in self.words:
            for other_word in self.words:
                if other_word.orientation == 1 - word.orientation:
                    if word.occupied_cells.intersection(other_word.occupied_cells):
                        has_intersections_with_other_words[index] = 1
                        break
            index += 1
        return len(self.words) - sum(has_intersections_with_other_words)

    def overlaps_counter(self) -> int:
        overlapped_words = set()
        for word in self.words:
            for other_word in self.words:
                if word != other_word and word.orientation == other_word.orientation and word.occupied_cells.intersection(
                        other_word.occupied_cells):
                    overlapped_words.add(word)
                    overlapped_words.add(word)
        return len(overlapped_words)

    def new_intersection_counter(self) -> [int, int]:
        incorrect_intersections = 0
        correct_intersections = 0

        for word in self.words:
            word.occupied_cells = get_filled_cells(word)

        for word in self.words:
            for other_word in self.words:
                if word.orientation != other_word.orientation:
                    location = word.occupied_cells.intersection(other_word.occupied_cells)
                    if location and set(word.word).intersection(set(other_word.word)):
                        word_letter, other_word_letter = '[', ']'
                        if word.orientation == 0:
                            for i in range(len(word)):
                                if {(word.x, word.y + i)} == location:
                                    word_letter = word.word[i]
                                    # print("word.word = ", word.word)
                                    # word_letter = [char for char in word.word][i]
                                    break
                            for i in range(len(other_word)):
                                if {(other_word.x + i, other_word.y)} == location:
                                    other_word_letter = other_word.word[i]
                                    # print("other_word.word = ", other_word.word)
                                    # other_word_letter = [char for char in other_word.word][i]
                                    break
                            if word_letter != other_word_letter:
                                incorrect_intersections += 1
                            else:
                                correct_intersections += 1
        return [incorrect_intersections, correct_intersections]

    def corner_counter(self) -> [int, int]:  # incorrect, correct
        def within_bounds(x, y):
            return 0 <= x <= 19 and 0 <= y <= 19

        def get_horizontal_corners(word):
            x_s, y_s = word.x, word.y
            x_e, y_e = x_s + len(word.word) - 1, y_s

            corners = [
                (x_s - 1, y_s),
                (x_s - 1, y_s - 1),
                (x_s - 1, y_s + 1),
                (x_e + 1, y_e),
                (x_e + 1, y_e - 1),
                (x_e + 1, y_e + 1)
            ]
            return [corner for corner in corners if within_bounds(*corner)]

        def get_vertical_corners(word):
            x_s, y_s = word.x, word.y
            x_e, y_e = x_s, y_s + len(word.word) - 1

            corners = [
                (x_s, y_s - 1),
                (x_s - 1, y_s - 1),
                (x_s + 1, y_s - 1),
                (x_e, y_e + 1),
                (x_e - 1, y_e + 1),
                (x_e + 1, y_e + 1)
            ]
            return [corner for corner in corners if within_bounds(*corner)]

        corner_problems = 0
        available_corners = 0
        filled_cells = set()
        for word in self.words:
            if word.orientation == 0:
                available_corners += len(get_horizontal_corners(word))
                for i in range(len(word.word)):
                    filled_cells.add((word.x, word.y + i))
            else:
                available_corners += len(get_vertical_corners(word))
                for i in range(len(word.word)):
                    filled_cells.add((word.x + i, word.y))

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
                    corner_problems += 1
                if (word.x - 1, word.y - 1) in filled_cells:
                    corner_problems += 1
                if (word.x + 1, word.y - 1) in filled_cells:
                    corner_problems += 1
                if (word.x, word.y + len(word.word)) in filled_cells:
                    corner_problems += 1
                if (word.x - 1, word.y + len(word.word)) in filled_cells:
                    corner_problems += 1
                if (word.x + 1, word.y + len(word.word)) in filled_cells:
                    corner_problems += 1
        if available_corners == 0:
            available_corners = 1
        return [corner_problems / available_corners, (available_corners - corner_problems) / available_corners]

    def words_fit_grid(self) -> int:
        words_fit_counter = len(self.words)
        for word in self.words:
            if word.orientation == 0:
                if word.y + len(word.word) > 20:
                    words_fit_counter -= 1
            else:
                if word.x + len(word.word) > 20:
                    words_fit_counter -= 1
        return words_fit_counter

    def new_fitness_counter(self) -> float:
        unique_words = set()
        for word in self.words:
            word.occupied_cells = get_filled_cells(word)
            if word.word in unique_words:
                print("GOT REPEATED: ", word)
            else:
                unique_words.add(word.word)

        overlapped_words_number = self.overlaps_counter()  # up to 10
        not_overlapped_words_number = len(self.words) - overlapped_words_number
        parallel_neighbours_number = self.parallel_neighbours_counter()  # up to 10
        not_connected_words_number = self.not_connected_words_counter()  # up to 10
        incorrect_intersections_number, correct_intersections_number = self.new_intersection_counter()  # incorrect intersection - up to 5, correct intersection - up to 5
        wrong_corners, correct_corners = self.corner_counter()  # up to 60
        words_fitting_grid_number = self.words_fit_grid()  # up to 10

        c1 = -4.0  # Coefficient for overlapped words
        c2 = 1.0  # Coefficient for not overlapped words
        c3 = -2.0  # Coefficient for parallel neighbors
        c4 = -2.5  # Coefficient for not connected words
        c5 = 5.0  # Coefficient for correct intersections
        c6 = -3.0  # Coefficient for incorrect intersections
        c7 = 7  # Coefficient for correct corners
        c8 = -25.0  # Coefficient for incorrect corners
        c9 = 0.5  # Coefficient for words fitting the grid

        fitness = (
                c1 * overlapped_words_number +
                c2 * not_overlapped_words_number +
                c3 * parallel_neighbours_number +
                c4 * not_connected_words_number +
                c5 * correct_intersections_number +
                c6 * incorrect_intersections_number +
                c7 * correct_corners +
                c8 * wrong_corners +
                c9 * words_fitting_grid_number
        )

        # self.print_crossword()
        # print(fitness)
        # print()
        return fitness


def get_filled_cells(word: Word):
    filled = set()
    if word.orientation == 0:
        for i in range(len(word.word)):
            filled.add((word.x, word.y + i))
    else:
        for i in range(len(word.word)):
            filled.add((word.x + i, word.y))
    return filled


def if_two_words_parallel(word1: Word, word2: Word):
    if word1.orientation == 0:
        if abs(word1.x - word2.x) == 1:
            cells_of_first_word = set()
            for k in range(len(word1.word)):
                cells_of_first_word.add(word1.y + k)

            for k in range(len(word2.word)):
                if (word2.y + k) in cells_of_first_word:
                    return True
    else:
        if abs(word1.y - word2.y) == 1:
            cells_of_first_word = set()
            for k in range(len(word1.word)):
                cells_of_first_word.add(word1.x + k)

            for k in range(len(word2.word)):
                if (word2.x + k) in cells_of_first_word:
                    return True
    return False


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

        # print("1: ", [str(word.word) for word in parent1.words])
        # print("1: ", [isinstance(word, Word) for word in parent1.words])
        # print("2: ", [str(word.word) for word in parent2.words])
        # print("2: ", [isinstance(word, Word) for word in parent2.words])
        # crossover_point = random.randint(0, min(len(parent1.words), len(parent2.words)) - 1)
        # child_words = parent1.words[:crossover_point] + parent2.words[crossover_point:]
        # child = Crossword(child_words)
        # new_population.append(child)

        # Sort the words based on their order in the original parents
        # print("CROSSOVER")
        parent2_words_sorted = []
        for word1 in parent1.words:
            for word2 in parent2.words:
                if str(word1.word) == str(word2.word):
                    parent2_words_sorted.append(word2)
        parent2_crossword = Crossword(parent2_words_sorted)

        # print("1: ", [str(word.word) for word in parent1.words])
        # print("2: ", [str(word.word) for word in parent2_crossword.words])
        # print()

        max_crossover_point = min(len(parent1.words), len(parent2_words_sorted))
        if max_crossover_point <= 2:
            crossover_point = 1
        else:
            crossover_point = random.randint(0, max_crossover_point - 1)
        # print("par1: ", len(parent1))
        # print("par2: ", len(parent2_words_sorted))
        child_words = parent1.words[:crossover_point] + parent2_crossword.words[crossover_point:]
        child = Crossword(child_words)
        # print("after crossover: ", len(child.words))
        # print(child.words)
        # print()
        new_population.append(child)

    return new_population


def mutate1(population, number_of_individuals):
    new_population = []
    for i in range(number_of_individuals):
        random.seed(i)
        crossword = population[i]
        if len(population[i].words) < 6:
            max_amount_coord_changes = 1
            coordinate_changes = max_amount_coord_changes
        else:
            max_amount_coord_changes = max(2, math.ceil(len(population[i].words) / 4))
            coordinate_changes = random.randint(1, max_amount_coord_changes)
        coordinate_changes_applied = 0
        orientation_changes = random.randint(1, max(len(crossword.words) - 2 * coordinate_changes, 2))
        orientation_changes_applied = 0

        old_words = copy.deepcopy(crossword.words)
        # print("MUTATION")
        # print(crossword.words)
        # print(old_words)
        random.shuffle(old_words)

        new_list_of_words = []
        # print("before mutation: ", len(old_words))
        while coordinate_changes_applied < coordinate_changes:
            draft_word1 = old_words.pop(0)
            draft_word2 = old_words.pop(0)
            new_word1 = Word(draft_word1, draft_word2.x, draft_word2.y, draft_word1.orientation)
            new_word2 = Word(draft_word2, draft_word1.x, draft_word1.y, draft_word2.orientation)
            # print(new_word1)
            # print(new_word2)
            new_list_of_words.append(new_word1)
            new_list_of_words.append(new_word2)
            coordinate_changes_applied += 1
        #     print("after popping: ", old_words)
        #     print("changes applied: ", coordinate_changes_applied)
        #     print("changes needed: ", coordinate_changes - coordinate_changes_applied)
        #
        # print("after coord changes: ", new_list_of_words)
        # print()
        # print()
        # for word in old_words:
        #     for new_word in new_list_of_words:
        #         if new_word.word == word.word:
        #             old_words.remove(word)


        # print("after popping: ", len(new_list_of_words))
        # print("leftover words number: ", len(old_words))

        # print("expected orientation changes: ", orientation_changes)
        i = len(old_words)
        while i > 0:
        # for word in old_words:
            word = old_words[0]
            # print("orientation changes applied: ", orientation_changes_applied)
            if orientation_changes_applied < orientation_changes:
                orientation = 1 - word.orientation
                new_word = Word(word.word, word.x, word.y, orientation)
                old_words.remove(word)
                i -= 1
                orientation_changes_applied += 1
                # print("1 word added, left ", len(old_words))
                # print(new_word)

            else:
                new_word = Word(word.word, word.x, word.y, word.orientation)
                # print(new_word)
                old_words.remove(word)
                i -= 1
                # print("1 word added, left ", len(old_words))
            # if not isinstance(new_word, Word):
                # print("PROBLEM WORD: ", new_word)
            new_list_of_words.append(new_word)

        new_crossword = Crossword(new_list_of_words)

        # print("after orientation changes: ", new_list_of_words)
        # print()
        new_population.append(new_crossword)
        # print("after all: ", len(new_crossword.words))
        # print(new_crossword.words)
        # print()

    return new_population


def main():
    words = []
    with open("input.txt", "r") as file:
        for line in file:
            word = Word(line.strip())
            words.append(word)

    population = []
    for _ in range(100):
        crossword = generate_crossword(words)
        population.append(crossword)

    initial_babe = population[random.randint(0, len(population) - 1)]
    initial_babe.print_crossword()
    print(initial_babe.fitness)
    print()

    generation_counter = 0
    max_generations = 100
    start_time = time.time()
    while generation_counter < max_generations:
        print("GEN ", generation_counter)
        selected_individuals = select_individuals(population, 10)
        # print("Crossover")
        crossovered_individuals = crossover_population(population, 70)
        # print()
        # print("MutatO")
        mutated_individuals = mutate1(population, 20)
        # print()
        population = selected_individuals + mutated_individuals + crossovered_individuals
        # population = selected_individuals + crossovered_individuals
        generation_counter += 1

    best_solution = select_individuals(population, 1)[0]
    best_solution.print_crossword()
    print(best_solution.fitness)
    print(time.time() - start_time)


if __name__ == '__main__':
    main()
