# nounseed

![logo](/nounseed_logo.png)

Nounseed is a Python script that generates project ideas by combining two randomly selected nouns. It allows you to store and manage project ideas for future reference.

## Requirements

- Python 3.x

## Installation

1a. Run:

```Python
pip install nounseed
```
or

1b. Clone the repository:
   ```shell
   git clone https://github.com/psibir/nounseed.git
   ```
2. Navigate to the project directory:
   ```shell
   cd nounseed
   ```

## Usage

1. Make sure you have a CSV file containing a list of nouns. The CSV file should have one noun per line.

2. Execute the script by running the following command:
   ```shell
   python nounseed.py [-n NUM_IDEAS]
   ```

   Optional argument:
   - `-n NUM_IDEAS, --num-ideas NUM_IDEAS`: Number of project ideas to generate (default is 10).

3. The script will generate project ideas by randomly combining two nouns from the provided CSV file. The generated project ideas will be displayed.

4. You can choose to store project ideas, view stored project ideas, remix the chosen nouns, generate new nouns, or quit the program by entering the corresponding options:
   - Enter the numbers of the project ideas you want to store.
   - 'v' to view stored ideas.
   - 'r' to remix the chosen nouns and generate new project ideas.
   - 'g' to generate new nouns and project ideas.
   - 'q' to quit the program.

5. If you choose to store project ideas, they will be stored in a CSV file named `storednouns.csv` located in the `nounseed` directory.

## Examples

1. Generate 5 project ideas:
   ```shell
   python nounseed.py -n 5
   ```

2. Generate project ideas and store some of them:
   ```shell
   python nounseed.py
   ```

   ```
   Generated Project Ideas:
   1. Idea 1
   2. Idea 2
   3. Idea 3
   4. Idea 4
   5. Idea 5
   6. Idea 6
   7. Idea 7
   8. Idea 8
   9. Idea 9
   10. Idea 10

   OPTIONS
   Enter the numbers of the project ideas you want to store:
   'v' to view stored ideas,
   'r' to remix the chosen nouns,
   'g' to generate new nouns, or
   'q' to quit: 1, 4, 6
   Idea 'Idea 1' has been stored in 'storednouns.csv'.
   Idea 'Idea 4' has been stored in 'storednouns.csv'.
   Idea 'Idea 6' has been stored in 'storednouns.csv'.
   ```

## Contributing

Contributions to NounSeed are welcome! If you encounter any issues or have suggestions for improvements, please create a new issue on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

The NounSeed script was developed by [psibir](https://github.com/psibir).

That's it! You can use this README as a starting point and modify it according to your needs.
