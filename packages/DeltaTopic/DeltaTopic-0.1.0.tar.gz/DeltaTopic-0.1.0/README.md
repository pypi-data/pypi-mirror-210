[![PyPi][badge-pypi]][link-pypi]
[![Docs][badge-docs]][link-docs]

[badge-pypi]: https://badge.fury.io/py/DeltaTopic.svg
[link-pypi]: https://pypi.org/project/DeltaTopic/
[badge-docs]: https://readthedocs.org/projects/deltatopic/badge/?version=latest
[link-docs]: https://deltatopic.readthedocs.io

## DeltaTopic: Dynamically-Encoded Latent Transcriptomic pattern Analysis by Topic modeling

This is a project repository for our paper

- Y Zhang, M Khalilitousi, YP Park, [Unraveling dynamically-encoded latent transcriptomic patterns in pancreatic cancer cells by topic modelling](https://www.biorxiv.org/content/10.1101/2023.03.11.532182v1.abstract).

### Summary

Building a comprehensive topic model has become an important research tool in single-cell genomics. With a topic model, we can decompose and ascertain distinctive cell topics shared across multiple cells, and the gene programs implicated by each topic can later serve as a predictive model in translational studies. Here, we present a Bayesian topic model that can uncover short-term RNA velocity patterns from a plethora of spliced and unspliced single-cell RNA-seq counts. We showed that modelling both types of RNA counts can improve robustness in statistical estimation and reveal new aspects of dynamic changes that can be missed in static analysis. We showcase that our modelling framework can be used to identify statistically-significant dynamic gene programs in pancreatic cancer data. Our results discovered that seven dynamic gene programs (topics) are highly correlated with cancer prognosis and generally enrich immune cell types and pathways.

### Installation

DeltaTopic requires Python 3.8 or later. We recommend to use [Miniconda](http://conda.pydata.org/miniconda.html).


Install DeltaTopic from [PyPI](https://pypi.org/project/DeltaTopic) using:

```bash
pip install DeltaTopic
```

  
To work with the latest development version, install from [GitHub](https://github.com/causalpathlab/deltaTopic) using:

```bash
python3 -m pip install git+https://github.com/causalpathlab/DeltaTopic
```

### Data

We obtained the original FASTQ files for pancreatic ductal adenocarcinoma (PDAC) from the [public repository](https://ngdc.cncb.ac.cn/gsa/browse/CRA001160) provided by two PDAC studies. The spliced and unspliced count matrices were quantified by [kb-python](https://www.kallistobus.tools/).

```bash
kb count -i index.idx -g t2g.txt -x 10xv2 -o ${output} \
-c1 spliced_t2c.txt -c2 unspliced_t2c.txt \
--workflow lamanno --filter bustools \
${fastq1} ${fastq2}
```

### Run

```bash
# train BALASM model on the spliced count data
BALSAM --nLV 32 --EPOCHS 100 
```

```bash
# train deltaTopic model
DeltaTopic --nLV 32 --EPOCHS 100 
```

#### For full documentaions, please refer to [DeltaTopic Documentation](https://deltatopic.readthedocs.io/en/latest/)
