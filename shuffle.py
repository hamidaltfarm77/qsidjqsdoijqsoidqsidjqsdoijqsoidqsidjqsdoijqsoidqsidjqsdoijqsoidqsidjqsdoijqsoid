import random

def shuffle_file(input_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()
        random.shuffle(lines)
    
    with open(input_file, 'w') as f:
        f.writelines(lines)

if __name__ == "__main__":
    input_file = "accounts.txt"
    shuffle_file(input_file)
    print("Shuffled bud!")
