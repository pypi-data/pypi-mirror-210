import csv
import random
from pathlib import Path
import argparse


STORED_NOUNS_FILE = "nounseed/storednouns.csv"
CSV_FILE = "nounseed/nounlist.csv"


class NounSeeder:
    def __init__(self, nouns):
        self.nouns = nouns

    @classmethod
    def load_nouns(cls, filename):
        csv_file = Path(filename)
        with csv_file.open('r') as csvfile:
            reader = csv.reader(csvfile)
            nouns = [row[0] for row in reader]
        return cls(nouns)

    def generate_project_ideas(self, num_ideas):
        if len(self.nouns) < 2:
            raise ValueError("There are not enough nouns to generate project ideas.")

        original_list = []
        project_ideas = []
        for _ in range(num_ideas):
            noun1, noun2 = random.sample(self.nouns, 2)
            original_list.extend([noun1, noun2])
            project_ideas.append(f"{noun1}{noun2}")

        return project_ideas, original_list


class ProjectIdeasManager:
    def __init__(self, ideas, original_list):
        self.original_ideas = ideas
        self.ideas = ideas
        self.original_list = original_list

    def select_ideas(self, user_input=input):
        while True:
            choices = user_input(
                "OPTIONS\n"
                "Enter the numbers of the project ideas you want to store:\n"
                "'v' to view stored ideas,\n"
                "'r' to remix the chosen nouns,\n"
                "'g' to generate new nouns, or\n"
                "'q' to quit: "
            )

            choices_lower = choices.lower()
            if choices_lower == 'v' or choices_lower == 'r' or choices_lower == 'g' or choices_lower == 'q':
                return choices_lower

            choices = [int(choice.strip()) for choice in choices.split(',') if choice.strip().isdigit()]

            if not choices:
                print("No choices provided. Exiting the program.")
                raise SystemExit

            if any(choice not in range(1, len(self.ideas) + 1) for choice in choices):
                print("Invalid choices. Please enter valid numbers.")
                raise SystemExit

            return choices

    def remix_ideas(self, original_list):
        new_ideas = []
        for _ in range(len(original_list) // 2):
            noun1, noun2 = random.sample(original_list, 2)
            new_ideas.append(f"{noun1}{noun2}")
        return new_ideas

    def store_ideas(self, choices, writer=print):
        if choices == 'v':
            self.view_stored_ideas(writer)
            return
        elif choices == 'r':
            self.ideas.extend(self.remix_ideas(self.original_list))
            writer("Remixed Project Ideas:")
            for i, idea in enumerate(self.ideas, start=1):
                writer(f"{i}. {idea}")
            return
        elif choices == 'g':
            return 'g'

        stored_nouns_file = Path(STORED_NOUNS_FILE)
        with stored_nouns_file.open('a', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            for choice in choices:
                selected_idea = self.ideas[choice - 1]
                csv_writer.writerow([selected_idea])
                writer(f"Idea '{selected_idea}' has been stored in '{STORED_NOUNS_FILE}'.")

    @staticmethod
    def view_stored_ideas(writer=print):
        stored_nouns_file = Path(STORED_NOUNS_FILE)
        if stored_nouns_file.exists():
            with stored_nouns_file.open('r') as csvfile:
                reader = csv.reader(csvfile)
                stored_ideas = list(reader)
                writer("Stored Project Ideas:")
                for i, idea in enumerate(stored_ideas, start=1):
                    writer(f"{i}. {idea[0]}")
        else:
            writer("No stored project ideas found.")


def main():
    parser = argparse.ArgumentParser(description="Generate and store project ideas.")
    parser.add_argument("-n", "--num-ideas", type=int, default=10, help="number of project ideas to generate")
    args = parser.parse_args()

    seed = NounSeeder.load_nouns(CSV_FILE)
    original_ideas, original_list = seed.generate_project_ideas(args.num_ideas)
    ideas_manager = ProjectIdeasManager(original_ideas, original_list)

    while True:
        print("Generated Project Ideas:")
        for i, idea in enumerate(ideas_manager.ideas, start=1):
            print(f"{i}. {idea}")

        choices = ideas_manager.select_ideas()
        if choices == 'g':
            seed = NounSeeder.load_nouns(CSV_FILE)
            ideas_manager.original_ideas, ideas_manager.original_list = seed.generate_project_ideas(args.num_ideas)
            ideas_manager.ideas = ideas_manager.original_ideas
            continue
        elif choices == 'q':
            break

        ideas_manager.store_ideas(choices)

        if choices != 'r':
            break

        ideas_manager.ideas = ideas_manager.original_ideas

    print("Exiting the program.")


if __name__ == '__main__':
    main()
