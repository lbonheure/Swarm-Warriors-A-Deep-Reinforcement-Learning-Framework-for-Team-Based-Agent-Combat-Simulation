
def creata_map0():
    bases = [(0,0), (19,0), (7,0), (12,0),
             (0,19), (19,19), (7,19), (12,19)]
    
    walls = []
    for i in range(10):
        walls.append((3, i+5))
        walls.append((16, i+5))
    
    for j in range(3):
        walls.append((j+5, 10))
        walls.append((j+11, 10))
        
    file = "map0.csv"
    f = open(file, "w", encoding="UTF-8")
    for y in range(20):
        for x in range(20):
            if (x, y) in bases:
                f.write("B, ")
            elif (x, y) in walls:
                f.write("W, ")
            else:
                f.write("_, ")
        f.write("\n")
    f.close()
    
    
creata_map0()