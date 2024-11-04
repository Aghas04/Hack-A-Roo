# Open the file in read mode and read the lines into a list
with open('Banking-Data.csv', 'r') as file:
    lines = file.readlines()

# List of categories
categories = [
    ['Shopping'], ['None'], ['Entertainment'], ['Travel'], 
    ['ATM'], ['Medical'], ['Rent'], ['Salary'], ['Interest'], ['Restaurant']
]

# Loop through each line and place the whole line of data into the corresponding category
for line in lines:
    # Split the line by commas
    data = line.strip().split(',')

    # Check if there are enough elements in the split data and get the category at index 3
    if len(data) > 3:
        category = data[3].strip()  # Assuming the category is at index 3

        # Find the matching category list and append the whole data list
        for cat_list in categories:
            if category == cat_list[0]:
                cat_list.append(data)  # Append the whole data list
                break

# Print the  categories
for cat_list in categories:
    print(f"Category: {cat_list[0]}")
    for entry in cat_list[1:]:
        print(entry)
    print()