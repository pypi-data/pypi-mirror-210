# nounseed

![logo](/nounseed_logo.png)

# NounSeed

NounSeed is a Python package that generates and stores project ideas based on a list of nouns. It uses random combinations of nouns to create unique project ideas. The generated ideas can be stored for future reference or remixed to generate new ideas.

## Installation

To install NounSeed, you can use `pip`:

```bash
pip install nounseed
```

## Usage

After installing NounSeed, you can run it from the command line by typing `nounseed`. By default, it will generate 10 project ideas. You can specify the number of ideas to generate using the `-n` or `--num-ideas` option:

```bash
nounseed -n 20
```

## Options

When running NounSeed, you have the following options:

- Enter the numbers of the project ideas you want to store.
- 'v' to view stored ideas.
- 'r' to remix the chosen nouns.
- 'g' to generate new nouns.
- 'q' to quit the program.

## Configuration

NounSeed requires two input files:

- `nounlist.csv`: This file should contain a list of nouns, each on a separate line.
- `storednouns.csv`: This file is used to store the project ideas you choose to save.

Make sure these files are present in the same directory as the NounSeed script.

## Examples

Here are some examples of using NounSeed:

```bash
# Generate 10 project ideas
nounseed

# Generate 20 project ideas
nounseed -n 20
```

## About

NounSeed is developed by [psibir](https://github.com/psibir) and is released under the MIT license. You can find the source code and contribute to the project on [GitHub](https://github.com/psibir/NounSeed).

For any issues or questions, please open an issue on the GitHub repository.

Enjoy generating unique project ideas with NounSeed!