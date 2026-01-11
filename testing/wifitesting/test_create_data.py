for i in range(1000):
  file = open("test_data.txt", "w")
  file.write(i) 
  file.write("\n") 
  file.close() 

print("Data is written into the file.")