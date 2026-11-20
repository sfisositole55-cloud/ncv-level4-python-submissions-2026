
marks = []

text = input("Enter a mark (0-100) or x to finish: ")

while text != "x":
    if text.isdigit() and int(text) <= 100:
        marks.append(int(text))
    else:
        print("Invalid mark ignored.")

    text = input("Enter a mark (0-100) or x to finish: ")

if len(marks) == 0:
    print("No marks captured.")
else:
    total = 0

    for m in marks:
        total = total + m

    average = total / len(marks)

    print("Total:", total)
    print("Average:", average)


    
   
        


                   







