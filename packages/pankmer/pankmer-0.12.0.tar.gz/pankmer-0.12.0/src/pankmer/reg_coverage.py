#===============================================================================
# reg_coverage.py
#===============================================================================

"""High-level functions for k-mer coverage analysis"""



# Imports ======================================================================

import gzip
import matplotlib.pyplot as plt
import os.path
import pandas as pd
import seaborn as sns
import gff2bed
from Bio.bgzf import BgzfReader, BgzfWriter
from io import IOBase
from itertools import accumulate, chain, groupby, islice, cycle
from math import floor, log10
from operator import itemgetter
from pankmer.env import GENES_PATH, COORD_REGEX
from pyfaidx import Fasta
from statistics import mean




# Constants ====================================================================

COLOR_PALETTE = sns.color_palette().as_hex()




# Functions ====================================================================

def parse_coords(coords: str):
    """Parse the coordinate string into its components
    
    Parameters
    ----------
    coords : str
        String of form chr:start-end giving genomic coordinates
    """

    chrom, start, end = coords.replace('-', ':').split(':')
    return chrom, int(start), int(end)


def parse_gene(gene: str, genes_path=GENES_PATH): # Not used yet, but will be useful later
    with gzip.open(genes_path, 'rt') as f:
        for line in f:
            parsed_line = line.split()
            if parsed_line[3] == gene:
                chrom, start, end = parsed_line[:3]
                break
        else:
            raise RuntimeError('gene not found')
    return chrom, int(start), int(end)


def gff_to_dict(gff, type='gene', n_features=None):
    """Parse a GFF file into a dictionary of feature coordinates

    Parameters
    ----------
    gff: str
       path to GFF file
    type
        string indicating feature type to include, or None to include all
        features
    n_features
        int indicating number of features to include, or None to include all
        features

    Returns
    -------
    dict
        coordinates of features in the GFF
    """

    sorted_features = sorted(gff2bed.parse(gff, type=type, parse_attr=False),
                             key=itemgetter(1))
    if n_features:
        return {chrom: [[start, end] for _, start, end, *_ in coords][:n_features]
            for chrom, coords in groupby(sorted_features, key=itemgetter(0))}
    else:
        return {chrom: [[start, end] for _, start, end, *_ in coords]
            for chrom, coords in groupby(sorted_features, key=itemgetter(0))}


def attr_to_coords(gff, type='gene', attr="Name"):
    """Parse a GFF file into a dictionary of feature coordinates with an attr
       (e.g. "Name") as keys

    Parameters
    ----------
    gff: str
       path to GFF file
    type
        string indicating feature type to include, or None to include all
        features
    n_features
        int indicating number of features to include, or None to include all
        features

    Returns
    -------
    dict
        coordinates of features in the GFF keyed by attr 
    """

    parsed_features = gff2bed.parse(gff, type=type)
    return {attr_vals[attr]: (seqid, start, end)
        for seqid, start, end, _, attr_vals in parsed_features}


def generate_coverage_values(chrom, start, end, *regcov_dicts, summary_func=mean):
    for position, *values in zip(range(start, end + 1),
        *(next(iter(regcov_dict[chrom].values())) for regcov_dict in regcov_dicts)):
        yield chrom, position-1, position, *(summary_func(v) for v in values)


def reg_coverage(*pk_results, ref, coords, summary_func=mean, output_file=None,
                 bgzip: bool = False, genes=None, flank: int = 0,
                 processes: int = 1):
    """Generate k-mer coverage levels across the input region

    Parameters
    ----------
    pk_results
        a PKResults object
    ref: str
        path to a reference genome in BGZIP compressed FASTA format
    coords: str
        genomic coordinates formatted as ctg:start-end
    summary_func
        function for summarizing the coverage value of a kmer across genomes
        in the index. The default is statistics.mean
    output_file
        filename or file object to write to
    bgzip: bool
        if True, output_file will be block compressed
    genes: str
        path to gff3 file containing gnes
    flank: int
        size of flanking region
    processes: int
        number of processes to use

    Yields
    ------
    contig, start, end, *values
        row of bedGraph data
    """
    
    if genes and not (COORD_REGEX.match(coords)):
        contig, start, end = attr_to_coords(genes)[coords]
    else:
        contig, start, end = parse_coords(coords)
    start -= flank
    end += flank
    for result in pk_results:
        result.threads = processes
    regcov_dicts = (result.get_collapsed_regional_scores(ref, {contig: [[start, end]]})
                    for result in  pk_results)
    if output_file:
        with (output_file if isinstance(output_file, (BgzfWriter, IOBase))
              else (BgzfWriter if bgzip else open)(output_file, 'wb')) as f:
            for cg, st, ed, *vs in generate_coverage_values(
                contig, start, end, *regcov_dicts, summary_func=summary_func
            ):
                f.write(('\t'.join(str(x) for x in (cg, st, ed, *vs))+'\n').encode())
    return generate_coverage_values(contig, start, end, *regcov_dicts,
                                        summary_func=summary_func)


def check_for_bgzip(reference: str):
    try:
        BgzfReader(reference)
    except ValueError:
        raise RuntimeError('Input FASTA must be BGZIP compressed')        


def get_chromosome_sizes_from_ref(reference: str):
    """Extract chromosome sizes from reference FASTA

    Parameters
    ----------
    reference : str
        path to reference FASTA file

    Returns
    -------
    DataFrame
        name and size of each chromosome
    """
    return pd.DataFrame(((k, len(v)) for k, v in Fasta(reference).items()),
                        columns=('name', 'size'))



def generate_plotting_data(coverage_values, groups, size, scale: float = 1,
                           shift: float = 0, bin_size: int = 0,
                           single_chrom: bool = False):
    """Construct rows of preprocessed data for the plotting data frame. Data
    are binned by rounding to the nearest bin coordinate, while bin coordinates
    are determined by the bin size parameter.

    Parameters
    ----------
    coverage values
        iterable of iterables listing coverage values
    groups
        iterable of group names
    size
        chromosome size in bp
    scale
        ratio of chromosome size to mean chromosome size
    shift
        x-axis shift of this chromosome, for plots showing multiple chromosomes
        consecutively
    bin_size
        set bin size. The input <int> is converted to the bin size by the
        formula: 10^(<int>+6) bp. The default value is 0, i.e. 1-megabase bins.

    Yields
    ------
    tuple
        bin coordinate, value, and group ID of a coverage data point
    """

    yield from ((chrom, min(round(int(pos), -6-bin_size), size)/size*scale + shift,
                float(cov), group, f'{group}' if single_chrom else f'{group}_{chrom}')
        for chrom, _, pos, cov, group
        in (list(vals)+[g] for cv, g in zip(coverage_values, groups) for vals in cv))


def collapse_plotting_data(rows):
    yield from ((c, x, mean(r[2] for r in rws), g, n)
                for (c, x, g, n), rws in groupby(rows, key=itemgetter(0,1,3,4)))


def regcov_dicts_tuple(*pk_results, ref, chromosomes):
    return tuple(result.get_collapsed_regional_scores(ref, {c: [] for c in chromosomes})
                    for result in  pk_results)


def genome_coverage_df(*regcov_dicts, sizes, chromosomes: list,
                       summary_func=mean, groups=None,
                       legend_title: str = 'Group', bin_size: int = 0,
                       x_label: str = 'Chromosome'):
    sizes.index = sizes.name
    sizes = sizes.loc[chromosomes, 'size']
    scales = sizes / sizes.mean()
    shifts = pd.Series(accumulate(chain((0,),scales[:-1])), index=scales.index)
    return pd.DataFrame(
        chain.from_iterable((collapse_plotting_data(generate_plotting_data(
                (generate_coverage_values(chrom, 0,
                    sizes[chrom], rd, summary_func=summary_func)
                    for rd in regcov_dicts),
                groups, size, scale=scale, shift=shift, bin_size=bin_size,
                single_chrom=(len(chromosomes)==1)))
            for chrom, size, scale, shift
            in zip(chromosomes, sizes, scales, shifts))),
        columns=('SeqID', x_label, 'K-mer coverage (%)', legend_title,
                 f'{legend_title}_chrom'))


def genome_coverage_plot(plotting_data, output: str,
                         groups=None, loci=None, sizes=None,
                         title: str = 'Coverage', x_label: str = 'Chromosome',
                         legend: bool = False,
                         legend_title: str = 'Group', legend_loc: str = 'best',
                         width: float = 7.0, height: float = 3.0,
                         color_palette=COLOR_PALETTE, alpha: float = 0.5,
                         linewidth: int = 3, xtlabel_rotation: int = 0,
                         xtlabel_ha: str = 'center'):
    """Generate a plot of average k-mer coverage values in bins, from a DF
    generated by genome_coverage_df

    Parameters
    ----------
    plotting_data
        pandas DataFrame as generated by genome_coverage_df
    output : str
        path to destination file for the plot
    groups
        iterable of group names
    loci
        list of strings indicating loci in form "contig:pos:name"
    sizes
        pandas DataFrame containing chrom.sizes table
    title : str
        title of the plot
    x_label : str
        x-axis label
    legend : bool
        if true, draw a legend for the plot
    legend_title : str
        title for the plot legend
    legend_loc : str
        location of legend. must be one of "best", "upper left", "upper right",
        "lower left", "lower right", "outside"
    width : float
        width of the plot in inches
    height : float
        height of the plot in inches
    color_palette
        color palette for plot lines
    alpha : float
        alpha value for plot lines
    linewidth : float
        width value for plot lines
    xtlabel_rotation : int
        rotation for x-axis tick labels
    xtlabel_ha : str
        horizontal alignment for x-axis tick labels (left, center, right)
    """

    chromosomes = plotting_data.loc[:,'SeqID'].unique()
    if legend:
        data_groups = plotting_data.loc[:,legend_title].unique()
        if groups is None:
            groups = data_groups
        else:
            groups_dict = dict(zip(data_groups, groups))
            plotting_data[legend_title] = tuple(groups_dict[x] for x in plotting_data[legend_title])
            plotting_data[f'{legend_title}_chrom'] = tuple(groups_dict[x] for x in plotting_data[f'{legend_title}_chrom'])
    palette = tuple(islice(cycle(color_palette[:len(groups)]),
                                 len(chromosomes) * len(groups)))
    shifts = plotting_data.loc[:,['SeqID', x_label]].groupby('SeqID').min()
    if sizes is not None:
        sizes.index = sizes.name
        sizes = sizes.loc[chromosomes, 'size']
    if loci is not None:
        if sizes is None:
            raise RuntimeError('loci argument requires sizes argument')
        scales = sizes / sizes.mean()
        loci_parsed = tuple(
            (int(p)/sizes[c] * scales[c] + shifts.loc[c, x_label], n)
            for c, p, n in (l.split(':') for l in loci))
        loci_x = tuple(l[0] for l in loci_parsed)
        ticks_labels = sorted(loci_parsed + tuple(zip(shifts[x_label],
                                                      chromosomes)))
        xticks = tuple(tl[0] for tl in ticks_labels)
        xlabels = tuple(tl[1] for tl in ticks_labels)
    else:
        xticks = shifts[x_label]
        xlabels = chromosomes
    ax = sns.lineplot(x=x_label, y='K-mer coverage (%)',
                      hue=f'{legend_title}_chrom', data=plotting_data, errorbar=None,
                      linewidth=linewidth,
                      palette=palette,
                      alpha=alpha,
                      legend='auto' if legend else False)
    ax.set_title(title)
    if (loci is not None) and (sizes is not None):
        ax.vlines(x=loci_x, ymin=min(plotting_data['K-mer coverage (%)']),
                  ymax=max(plotting_data['K-mer coverage (%)']),
                  colors='gray',
                  linestyles='dashed')
    if (len(chromosomes) == 1) and (sizes is not None):
        xticks = ax.get_xticks()[1:-1]
        xlabels=tuple(f"{x*sizes.loc[chromosomes[0]]/1e6:.1f}" for x in xticks)
    ax.set_xticks(xticks)
    ax.set_xticklabels(xlabels, rotation=xtlabel_rotation, ha=xtlabel_ha)
    if legend:
        if legend_loc == 'outside':
            leg = ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left',
                            borderaxespad=0, title=legend_title)
        else:
            leg = ax.legend(loc=legend_loc, title=legend_title)
        for line in leg.get_lines():
            line.set_linewidth(linewidth)
            line.set_alpha(alpha)
    fig = ax.get_figure()
    fig.set_figwidth(width)
    fig.set_figheight(height)
    fig.tight_layout()
    fig.savefig(output)
    fig.clf()


def genome_coverage(*pk_results, output: str, ref: str, chromosomes: list,
                    output_table=None, summary_func=mean, groups=None, loci=None,
                    title: str = 'Coverage', x_label: str = 'Chromosome',
                    legend: bool = False, legend_title='Group', legend_loc='best',
                    bin_size: int = 0, width: float = 7.0, height: float = 3.0,
                    color_palette=COLOR_PALETTE, alpha: float = 0.5,
                    linewidth: int = 3, processes: int = 1,
                    xtlabel_rotation: int = 0, xtlabel_ha: str = 'center'):

    """Generate a plot of average k-mer coverage values in bins across the
    input genome

    Parameters
    ----------
    pk_results
        a PKResults object
    output : str
        path to destination file for the plot
    ref : str
        path to the input reference genome in BGZIP compressed FASTA format
    chromosomes : list
        list of chromosomes to include in the plot
    output_table
        path to write TSV table containing underlying plotting data
    summary_func
        function for summarizing the coverage value of a kmer across genomes
        in the index. The default is statistics.mean
    groups
        iterable of group names
    title : str
        title of the plot
    x_label : str
        x-axis label
    legend : bool
        if true, draw a legend for the plot
    legend_title : str
        title for the plot legend
    legend_loc : str
        location of legend. must be one of "best", "upper left", "upper right",
        "lower left", "lower right", "outside"
    bin_size
        set bin size. The input <int> is converted to the bin size by the
        formula: 10^(<int>+6) bp. The default value is 0, i.e. 1-megabase bins.
    width : float
        width of the plot in inches
    height : float
        height of the plot in inches
    color_palette
        color palette for plot lines
    alpha : float
        alpha value for plot lines
    linewidth : float
        width value for plot lines
    processes: int
        number of processes to use
    xtlabel_rotation : int
        rotation for x-axis tick labels
    xtlabel_ha : str
        horizontal alignment for x-axis tick labels (left, center, right)
    """

    check_for_bgzip(ref)
    if not groups:
        groups = list(range(len(pk_results)))
    for result in pk_results:
        result.threads = processes
    regcov_dicts = regcov_dicts_tuple(*pk_results, ref=ref,
        chromosomes=chromosomes)
    sizes = get_chromosome_sizes_from_ref(ref)
    plotting_data = genome_coverage_df(*regcov_dicts, sizes=sizes,
        chromosomes=chromosomes, summary_func=summary_func, groups=groups,
        legend_title=legend_title, bin_size=bin_size, x_label=x_label)
    if output_table:
        plotting_data.to_csv(output_table, sep='\t', index=False)
    genome_coverage_plot(plotting_data, output=output,
        groups=groups, loci=loci, sizes=sizes, title=title, x_label=x_label,
        legend=legend, legend_title=legend_title, legend_loc=legend_loc,
        width=width, height=height, color_palette=color_palette, alpha=alpha,
        linewidth=linewidth, xtlabel_rotation=xtlabel_rotation,
        xtlabel_ha=xtlabel_ha)


def coverage_heatmap(pk_results, refs, features, output, n_features=None, width=7, height=7):
    if not output.endswith('.png'):
        raise RuntimeError('output file path must end with .png')
    results = tuple(pk_results.get_collapsed_regional_scores(ref, gff_to_dict(gff, n_features=n_features))
        for ref, gff in zip(refs, features))
    dfs = tuple(pd.DataFrame({os.path.basename(ref.replace('.fasta', '').replace('.gz', '')):
            tuple(sum(v) for values in regcov_dict.values() for v in values)}).transpose()
        for ref, regcov_dict in zip(refs, results))
    vmin = min(df.values.min() for df in dfs)
    vmax = max(df.values.max() for df in dfs)
    sns.set_context('paper')
    fig, axs = plt.subplots(nrows=len(dfs))
    fig.set_figwidth(width)
    fig.set_figheight(height)
    def round(n, k):
        return n - n % k
    for df, ax in zip(dfs, axs):
        dft = df.transpose()
        tick_step = int(10**(floor(log10(dft.index.max() - dft.index.min()))))
        tick_min = int(round(dft.index.min(), (-1 * tick_step)))
        tick_max = int(round(dft.index.max(), (1 * tick_step))) + tick_step
        xticklabels = range(tick_min, tick_max, tick_step)
        xticks = [dft.index.get_loc(label) for label in xticklabels]
        xticklabels_pretty = tuple(
            (f'{int(x)}BP' if x<1e3
             else f'{int(x/1e3)}KB' if x<1e6
             else f'{int(x/1e6)}MB')
            for x in xticklabels)
        sns.heatmap(df, ax=ax, vmin=vmin, vmax=vmax,
            xticklabels=xticklabels_pretty)
        ax.tick_params(labelrotation=0)
        ax.set_xticks(xticks, rotation=0, labels=xticklabels_pretty)
    fig.tight_layout()
    fig.savefig(output)
