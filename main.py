from graphic import Graphic

def main():

    file_path = './asset/input/level1.txt' 
    wumpus_world = Graphic(file_path)
    wumpus_world.run_game()

if __name__ == "__main__":
    main()