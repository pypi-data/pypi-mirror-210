[![Python application](https://github.com/jermwatt/quick_batch/actions/workflows/python-app.yml/badge.svg)](https://github.com/jermwatt/quick_batch/actions/workflows/python-app.yml)

# quick_batch

quick_batch is an ultra-simple command-line tool for large batch processing and transformation. It allows you to scale any `processor` function that needs to be run over a large set of input data, enabling batch/parallel processing of the input with minimal setup and teardown.

- [quick\_batch](#quick_batch)
  - [Why use quick\_batch](#why-use-quick_batch)
  - [Installation](#installation)
  - [Usage](#usage)
    - [`processor.py`](#processorpy)
    - [`config.yaml`](#configyaml)
    - [Running quick\_batch](#running-quick_batch)


## Why use quick_batch

quick_batch aims to be

- **dead simple to use:** versus standard cloud service batch transformation services that require significant configuration / service understanding

- **ultra fast setup:** versus setup of heavier orchestration tools like `airflow` or `mlflow`, which may be a hinderance due to time / familiarity / organisational constraints

- **100% portable:** - use quick_batch on any machine, anywhere

- **processor-invariant:** quick_batch works with arbitrary processes, not just machine learning or deep learning tasks.

- **transparent and open source:** quick_batch uses Docker under the hood and only abstracts away the not-so-fun stuff - including instantiation, scaling, and teardown.  you can still monitor your processing using familiar Docker command-line arguments (like `docker service ls`, `docker service logs`, etc.).


## Installation

To install quick_batch, simply use `pip`:

```bash
pip install quick-batch
```

## Usage

To use quick_batch, you need to define a `processor.py` file and a `config.yaml` file containing the necessary paths and parameters.

### `processor.py`

Create a `processor.py` file with the following pattern:

```python
import ...

def processor(todos):
    # Processor code
```

quick_batch will essentially point your `processor.py` at the `input_path` defined in your `config.yaml` and process this input in parallel at a scale given by your choice of `num_processors`.  Output will be written to the `output_path` specified in the configuration file.

### `config.yaml`

Create a `config.yaml` file with the following structure:

```yaml
data:
  input_path: /path/to/your/input/data
  output_path: /path/to/your/output/data
  log_path: /path/to/your/log/file

queue:
  feed_rate: <int - number of examples processed per processor instance>
  order_files: <boolean - whether or not to order input files by size>

processor:
  processor_path: /path/to/your/processor/processor.py
  num_processors: <int - instances of processor to run in parallel>
```

### Running quick_batch

To run quick_batch, execute the following command in your terminal:

```bash
quick_batch /path/to/your/config.yaml
```
