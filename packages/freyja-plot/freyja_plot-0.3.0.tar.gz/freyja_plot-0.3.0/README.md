# freyja-plot
Plotting lineage abundance for individual samples from aggregated freyja demix results

![Example Lineage Abundance Plot](example/example_images/batch_comparison_selection_example.png "These samples had some issues on plate1 or else the 'plate1' and 'plate2' versions of each sample would look more similar.")

## Installation:
```console
pip install freyja-plot
```

## Inputs:
`freyja-plot` enables the production of plots from aggregated freyja data. This can be acquired after two Freyja steps. See the [Freyja docs](https://github.com/andersen-lab/Freyja) for more details.
1. `freyja demix [variants-file] [depth-file] --output [output-file]`
2. `freyja aggregate [directory-of-output-files] --output [aggregated-filename.tsv]`

`freyja-plot` just needs the output file from `freyja aggregate`: [aggregated-filename.tsv].

## Usage:
### Create a freyja plotter with one or more files
```python
from freyja_plot import FreyjaPlotter

# single batch plotter from one file
plotter = FreyjaPlotter("examples/wastewater-freyja-aggregated.tsv")

# single batch plotter with multiple input files
# note: default behavior assumes multiple files should be compared, so set compare=False to avoid this
multi_file_plotter = FreyjaPlotter(
    ["examples/wastewater-freyja-aggregated.tsv","examples/wastewater-freyja-compare1.tsv"],
    compare=False
)
```

### Create a freyja plotter for comparing samples across batches
Note: this requires a different file for each batch.
```python
from freyja_plot import FreyjaPlotter

# comparison plotter, derived names
comp_plotter_derived_names = FreyjaPlotter([
    "example/wastewater-freyja-compare1.tsv",
    "example/wastewater-freyja-compare2.tsv",
])

# comparison plotter, customized batch names (this uses a dict as input)
# note: the value associated with each filename key will be appended to each sample name when plotted
comp_plotter_explicit_names = FreyjaPlotter({
    "example/wastewater-freyja-compare1.tsv":"plate1",
    "example/wastewater-freyja-compare2.tsv":"plate2",
})
```

### Plotting
Plotting works the same whether comparing multiple batches or viewing a single set of samples, so we'll simplify our several plotter examples from above into one `plotter`. The method `FreyjaPlotter.plotLineages()` returns a plotly figure that can be used for further analysis. If a filename is given, the fig will be saved there. `freyja-plot` currently supports html and png files. Writing .png files may not work... see [this link](https://github.com/plotly/Kaleido/issues/134) for more details.
```python
# simple plot of lineage abundances for all samples in file
plotter.plotLineages(fn="lineage_abundance_example.html")
```

With more samples or more varied samples, the above non-summarized plot may take a while to produce. Sometimes, it may be more useful to get a summarized view of the lineages and their abundance in each sample.
```python
plotter.plotLineages(summarized=True,fn="summarized_lineage_abundance_example.html")
```

To view higher level lineage assignments with the non-summarized freyja output, the `superlineage` flag can be used. The base `superlineage` is demarked level 0. Each next sublineage (to the next ".") can be attained by adding 1 for each sublineage desired. 'BA.5.1' with a requested sublineage of 0 would return 'BA.*', as would a sample with the lineage 'BA'. For less specific lineages, if the `superlineage` level gets to high, the most specific lineage possible will be returned. 'BA.5.1' with a requested sublineage of 5 would still only return 'BA.5.1'.
```python
# plotting superlineage, level 0: e.g. BA.* ()
fig1 = plotter.plotLineages(superlineage=0,fn="superlineage_abundance_example.html")
# plotting superlineage, level 2: e.g. BA.5.1.* ()
fig2 = plotter.plotLineages(superlineage=2,fn="superlineage_abundance_example.html")
```

To stack multiple lineage plots
```python
plotter.plotLineages([fig1,fig2],["Fig 1 Title","Fig 2 Title"],fn="combined_plots_example.html")
```

#### Example plots
Here's an example plot from a single batch.

![superlineage_example.png](example/example_images/superlineage_example.png?raw=true "Lineage abundance plot with superlineage=2 - png")

Here's an example plot from a batch comparison with summarized=True.

![batch_comparison_example.png](example/example_images/batch_comparison_example.png?raw=true "Batch comparison of samples using summarized lineage abundances - png")

Did you notice how some samples are missing labels in the example plots when presented as .png files? If you zoom in or expand the html version of the plot enough (or you have fewer samples per plot), missing names should appear.

## Testing
If you run the script [create_test_plots.py](example\create_test_plots.py), some test png/html files will be produced in a new directory `./example/test_images`. They should look like the images above in this tutorial.

## Additional functionality
To see what else you can do, use python's `help()` function. Here's a useful excerpt from the portion that's most useful.
```python
>>> import freyja_plot
>>> help(freyja_plot.FreyjaPlotter)
...
plotLineages(self, 
    summarized=False, superlineage=None, minimum=0.05, 
    fn=None, title='Freyja lineage prevalence', samples='all', 
    include_pattern=None, exclude_pattern=None)
Returns plot of stacked bars showing lineage abundances for each sample

Args:
    `summarized` (bool): whether to use summarized lineages or all, defaults to False
    `superlineage` (int|None): number of superlineages to consider, ignored if not provided, 0 is the base lineage, defaults to None
    `minimum` (float): minimum abundance value to include in plot - anything less is categorized in "Other", defualts to 0.05
    `fn` (str|Path): where to write fig, if provided, defaults to None
    `title` (str): plot title, defualts to "Freyja lineage prevalence"
    `samples` (list|"all"): only the listed samples will be plotted
    `include_pattern` (str): samples to include like "sample1|sample2"
    `exclude_pattern` (str): samples to exclude like "sample1|sample2"
...
```