if __name__ == "__main__":
    with open("test.txt","r") as f:
        for line in f:
            line = line.strip()
            print line
