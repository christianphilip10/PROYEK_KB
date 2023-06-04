import random
from operator import attrgetter

def blend_colors(color1, color2, ratio=0.5):
    blended_color = (
        int(color1[0] * ratio + color2[0] * (1 - ratio)),
        int(color1[1] * ratio + color2[1] * (1 - ratio)),
        int(color1[2] * ratio + color2[2] * (1 - ratio))
    )
    return blended_color

def bound_value(v, min_v, max_v):
    return min(max(min_v, v), max_v)

# Fungsi yang menghasilkan keturunan yang baru
def recombinate(pairs, gene_props, mutation_probability=0.1, effect=0.5):
    offspring = []
    for p1, p2 in pairs:
        children_genes = {}
        for gen in p1.genes.keys():
            values = [p1.genes[gen], p2.genes[gen]]
            if gen == "colors":
                children_genes[gen] = blend_colors(min(values), max(values))
            else:
                children_genes[gen] = random.uniform(min(values), max(values))
                if random.random() < mutation_probability:
                    min_v = gene_props[gen]['min']
                    max_v = gene_props[gen]['max']
                    v = children_genes[gen]
                    rv = random.choice([-1, 1]) * random.uniform(0, effect * (max_v - min_v))
                    # new_v_gauss = bound_value(random.gauss(v, (max_v - min_v) * effect), min_v, max_v)
                    new_v = bound_value(v + rv, min_v, max_v)
                    # print '----- Mutating ' + gen + ' - RV: ' + str(rv) + ' - V: ' + str(v) + ' - New: ' + str(new_v) + ' - Gaussian: ' + str(new_v_gauss)
                    # rv = random.uniform(children_genes[gen], (max_v - min_v)*0.1)
                    children_genes[gen] = new_v
        offspring.append(children_genes)
    return offspring

# Fungsi untuk memilih pasangan individu yang akan melakukan perkawinan (mating)
# Pemilihan pasangan individu menggunakan roulette_wheele
def mating_pool(population, num_of_pairs=10, evaluator=attrgetter('fitness')):
    evaluated_population = evaluate(population, evaluator)
    return zip(roulette_wheel(evaluated_population, k=num_of_pairs),
               roulette_wheel(evaluated_population, k=num_of_pairs))

# Fungsi ini juga digunakan untuk memilih pasangan individu untuk perkawinan, namun menggunakan metode turnamen.
# Individu dipilih secara acak dan dibandingkan berdasarkan fitness mereka.
def mating_pool_tournament(population, num_of_pairs=10, evaluator=attrgetter('fitness')):
    pool = []
    while len(pool) < num_of_pairs:
        # Generate a pair for mating
        p1 = tournament(population, evaluator)
        p2 = tournament(population - {p1}, evaluator)
        pool.append((p1, p2))
    return pool

# Fungsi ini digunakan untuk mengevaluasi populasi dengan menggunakan fungsi evaluator yang diberikan.
# Fungsi evaluator digunakan untuk menghitung nilai fitness individu.
# Hasil evaluasi populasi berupa pasangan (individu, fitness).
def evaluate(population, evaluator=attrgetter('fitness')):
    return map(lambda x: (x, evaluator(x)), population)

# Fungsi ini mengimplementasikan metode roda roulette untuk memilih individu dari populasi yang telah dievaluasi.
# Individu dipilih dengan mempertimbangkan fitness mereka.
# Semakin tinggi fitness = semakin besar kemungkinan individu terpilih.
def roulette_wheel(evaluated_population, k=10):
    sum_fitness = sum([v[1] for v in evaluated_population])
    selected = []
    while len(selected) < k:
        r = random.uniform(0, sum_fitness)
        for i in evaluated_population:
            r -= i[1]
            if r < 0:
                selected.append(i[0])
                break
    return selected

# Fungsi ini mengimplementasikan metode turnamen untuk memilih individu dari populasi.
# Beberapa individu dipilih secara acak dari populasi dan dibandingkan berdasarkan fitness mereka.
# Individu dengan fitness tertinggi dipilih sebagai hasil turnamen.
def tournament(population, evaluator, k=2):
    sample = population if len(population) < k else random.sample(population, k)
    return max(sample, key=evaluator)


if __name__ == '__main__':
    pop = {15, 18, 30, 100, 120, 60, 35, 40, 42}
    print (mating_pool(pop, evaluator=lambda x: x))
    print (mating_pool_tournament(pop, evaluator=lambda x: x))
