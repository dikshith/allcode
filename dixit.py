
def one_line():
    output = []
    with open("toChris.txt", "r") as f:
        line = f.readline()
        counter = 0
        temp = []
        while line:
            if "{" in line:
                counter += 1
            elif "}" in line:
                counter -= 1

            temp.append(line)
            if counter == 0:
                output.append(temp)
                temp = []
            line = f.readline()
    result = []
    for o in output:
        txt = "".join(o).replace("\n", "").replace(" ", "").replace(":", ": ")
        result.append(txt)

    return "\n".join(result)



if __name__ == "__main__":
    print(one_line())
