
marks = {"bongane": 65,"Lerato": 82,"Sipho": 48,"teka": 90,"amos": 73,
}


records = []
for name in marks:
    records.append((marks[name], name))



def bubble_sort_desc(items):
    n = len(items)
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            if items[j][0] < items[j + 1][0]:      
                items[j], items[j + 1] = items[j + 1], items[j]
                swapped = True
        if not swapped:                            
            break
    return items


bubble_sort_desc(records)


print("Ranking (highest to lowest)")
print("---------------------------")
rank = 1
for mark, name in records:
    print(f"{rank}. {name:<8} {mark}")
    rank += 1


