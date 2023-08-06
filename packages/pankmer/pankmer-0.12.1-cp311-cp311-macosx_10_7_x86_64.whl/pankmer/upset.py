import pandas as pd
import upsetplot
import gzip
from collections import Counter
from itertools import compress
from matplotlib import pyplot

def generate_relevant_scores(pk_results, genomes):
    genome_set = set(genomes)
    genomes_reversed = tuple(pk_results.genomes)[::-1]
    for _, _, score in pk_results:
        memberships = set(compress(genomes_reversed, (x==1 for x in score)))
        inter = memberships.intersection(genome_set)
        if inter:
            yield tuple(sorted(inter))


def generate_relevant_scores_exclusive(pk_results, genomes):
    genome_set = set(genomes)
    genomes_reversed = tuple(pk_results.genomes)[::-1]
    for _, _, score in pk_results:
        memberships = set(compress(genomes_reversed, (x==1 for x in score)))
        inter = memberships.intersection(genome_set)
        diff = memberships - genome_set
        if inter and not diff:
            yield tuple(sorted(inter))


def count_scores(pk_results, genomes, exclusive=False):
    counts = Counter(generate_relevant_scores_exclusive(pk_results, genomes)
        if exclusive else generate_relevant_scores(pk_results, genomes))
    return pd.Series(counts.values(), index=pd.MultiIndex.from_tuples(
        (tuple(g in k for g in genomes) for k in counts.keys()),
        names=genomes))


def upset(pk_results, output, genomes, vertical=False, show_counts=False,
          min_subset_size=None, max_subset_size=None, exclusive=False,
          table=None):
    score_counts = count_scores(pk_results, genomes, exclusive=exclusive)
    if table:
        with (gzip.open if table.endswith('.gz') else open)(table, 'wb') as f:
            score_counts.to_csv(f, sep='\t', header=['k-mers'])
    upsetplot.plot(score_counts,
        orientation='vertical' if vertical else 'horizontal',
        show_counts=show_counts,
        min_subset_size=min_subset_size,
        max_subset_size=max_subset_size)
    pyplot.savefig(output)
