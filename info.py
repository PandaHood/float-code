import datetime
import time


def main():
    team_number = input("Team Number: ")
    profile_num = input("Profile Number (1 or 2): ")
    # check what else we need to print out
    print(f"Team_number: {team_number}, Team_name: NUWave, Time: {datetime.datetime.now()}")
    time.sleep(5)
    

if __name__ == "__main__":
    main()