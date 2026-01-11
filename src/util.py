def output_txt(time, depth, pressure):
    with open(f"profile.txt", "a") as file:
        file.write(f"{time}, {depth}, {pressure}\n")

#brainstorm more util functions?