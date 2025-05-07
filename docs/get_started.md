# Get started

Initialize an `AstroPilot` instance and describe the data and tools to be employed.

```python
from astropilot import AstroPilot, Journal

astro_pilot = AstroPilot(project_dir="project_dir")

prompt = "Analyze the experimental data stored in /path/to/data.csv using sklearn and pandas. This data includes time-series measurements from a particle detector."

astro_pilot.set_data_description(prompt)
```

Generate a research idea from that data specification.

```python
astro_pilot.get_idea()
```

Generate the methodology required for working on that idea.

```python
astro_pilot.get_method()
```

With the methodology setup, perform the required computations and get the plots and results.

```python
astro_pilot.get_results()
```

Finally, generate a latex article with the results. You can specify the journal style, in this example we choose the [APS (Physical Review Journals)](https://journals.aps.org/) style.

```python
from astropilot import Journal

astro_pilot.get_paper(journal=Journal.APS)
```

You can also manually provide any info as a string or markdown file in an intermediate step, using the `set_idea`, `set_method` or `set_results` methods. For instance, for providing a file with the methodology developed by the user:

```python
astro_pilot.set_method(path_to_the_method_file.md)
```