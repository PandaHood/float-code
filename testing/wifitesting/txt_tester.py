import time

time.sleep(45)

#Define the filename
filename = "sample.txt"

#Define the text content
text_content = "This is a simple text file created using Python."

#Open the file in write mode and write the text
with open(filename, "w") as file:
    file.write(text_content)

print(f"File '{filename}' has been created successfully.")
