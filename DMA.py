import time
import numpy as np
from pynq import Overlay
from pynq import allocate

# Handle the preprocessing and passing of data into the FPGA
def main():

   # Load the test for evaluation
   print('Loading data')
   t_acc_x, t_acc_y, t_acc_z, t_gyr_x, t_gyr_y, t_gyr_z, extracted_test_data, y_test = load_test_data()
   timer = 0
   
   result = []

   # Program the FPGA with the bitstream and initialize communication with the DMA
   ol = Overlay('pynq/overlays/AI/design_1_wrapper.bit')
   dma = ol.axi_dma_0

   # Process the data in 1 array to pass to DMA
   for j in range(2947):

      print(j)

      t_acc_x_new = []
      for i in t_acc_x[j]:
         t_acc_x_new.append(i[0])
      t_acc_x2 = []
      for i in t_acc_x_new:
         t_acc_x2.append(int(i * 100000000))

      t_acc_y_new = []
      for i in t_acc_y[j]:
         t_acc_y_new.append(i[0])
      t_acc_y2 = []
      for i in t_acc_y_new:
         t_acc_y2.append(int(i * 100000000))

      t_acc_z_new = []
      for i in t_acc_z[j]:
         t_acc_z_new.append(i[0])
      t_acc_z2 = []
      for i in t_acc_z_new:
         t_acc_z2.append(int(i * 100000000))

      t_gyr_x_new = []
      for i in t_gyr_x[j]:
         t_gyr_x_new.append(i[0])
      t_gyr_x2 = []
      for i in t_gyr_x_new:
         t_gyr_x2.append(int(i * 100000000))

      t_gyr_y_new = []
      for i in t_gyr_y[j]:
         t_gyr_y_new.append(i[0])
      t_gyr_y2 = []
      for i in t_gyr_y_new:
         t_gyr_y2.append(int(i * 100000000))

      t_gyr_z_new = []
      for i in t_gyr_z[j]:
         t_gyr_z_new.append(i[0])
      t_gyr_z2 = []
      for i in t_gyr_z_new:
         t_gyr_z2.append(int(i * 100000000))
         
      extracted_test_data_new = []
      for i in extracted_test_data[j]:
         extracted_test_data_new.append(i)
      extracted_test_data2 = []
      for i in extracted_test_data_new:
         extracted_test_data2.append(int(i * 100000000))

      final = []
      for i in t_acc_x2:
         final.append(i)
      for i in t_acc_y2:
         final.append(i)
      for i in t_acc_z2:
         final.append(i)
      for i in t_gyr_x2:
         final.append(i)
      for i in t_gyr_y2:
         final.append(i)
      for i in t_gyr_z2:
         final.append(i)
      for i in extracted_test_data2:
         final.append(i)

      input_buffer = allocate(shape=(792,), dtype=np.intc)
      output_buffer = allocate(shape=(1,), dtype=np.intc)
      
      for i in range(792):
         input_buffer[i] = final[i]
      
      start = time.perf_counter()

      # Pass the data to DMA to be processed by FPGA
      dma.sendchannel.transfer(input_buffer)
      dma.recvchannel.transfer(output_buffer)
      dma.sendchannel.wait()
      dma.recvchannel.wait()

      result.append(output_buffer[0])

      end = time.perf_counter()
      timer += end - start

   # Evaluate the accuracy of the model
   counter = 0
   matrix = [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]

   for i in range(2947):
      matrix[result[i]-1][y_test[i]-1] += 1
      if result[i] == y_test[i]:
         counter += 1
   
   print("Accuracy: ", end="")
   print(counter / 2947 * 100)

   print("* 0 1 2 3 4")
   for i in range(5):
      print(i, end=" ")
      for j in range(5):
         print(matrix[i][j], end=" ")
      print()

   print("Time Taken: ", end="")
   print(timer)


# Function loads the sensor data for testing.
def load_test_data():

   body_acc_x = []
   body_acc_y = []
   body_acc_z = []
   body_gyr_x = []
   body_gyr_y = []
   body_gyr_z = []

   with open("body_acc_x_test.txt", 'r') as f:
      for row in f:
         body_acc_x.append(row.replace("  ", " ").strip().split(" "))

   with open("body_acc_y_test.txt", 'r') as f:
      for row in f:
         body_acc_y.append(row.replace("  ", " ").strip().split(" "))

   with open("body_acc_z_test.txt", 'r') as f:
      for row in f:
         body_acc_z.append(row.replace("  ", " ").strip().split(" "))

   with open("body_gyro_x_test.txt", 'r') as f:
      for row in f:
         body_gyr_x.append(row.replace("  ", " ").strip().split(" "))

   with open("body_gyro_y_test.txt", 'r') as f:
      for row in f:
         body_gyr_y.append(row.replace("  ", " ").strip().split(" "))

   with open("body_gyro_z_test.txt", 'r') as f:
      for row in f:
         body_gyr_z.append(row.replace("  ", " ").strip().split(" "))

   label = []

   with open("y_test.txt") as f:
         
      for row in f:
         number = int(row.strip())

         if number == 6:
            label.append(5)
         else:
            label.append(number)

   extracted_data = extract_data(np.array(body_acc_x).astype(np.float32), np.array(body_acc_y).astype(np.float32), np.array(body_acc_z).astype(np.float32), np.array(body_gyr_x).astype(np.float32), np.array(body_gyr_y).astype(np.float32), np.array(body_gyr_z).astype(np.float32))
   body_acc_x = np.transpose([body_acc_x],(1,2,0)).astype(np.float32)
   body_acc_y = np.transpose([body_acc_y],(1,2,0)).astype(np.float32)
   body_acc_z = np.transpose([body_acc_z],(1,2,0)).astype(np.float32)
   body_gyr_x = np.transpose([body_gyr_x],(1,2,0)).astype(np.float32)
   body_gyr_y = np.transpose([body_gyr_y],(1,2,0)).astype(np.float32)
   body_gyr_z = np.transpose([body_gyr_z],(1,2,0)).astype(np.float32)
    
   return body_acc_x, body_acc_y, body_acc_z, body_gyr_x, body_gyr_y, body_gyr_z, extracted_data, np.array(label).astype(np.uint32)

# Extract the feture of the data set to sent to DMA
def extract_data(body_acc_x, body_acc_y, body_acc_z, body_gyr_x, body_gyr_y, body_gyr_z):

   acc_x_mean = np.mean(body_acc_x, axis=1).reshape(-1,1)
   acc_y_mean = np.mean(body_acc_y, axis=1).reshape(-1,1)
   acc_z_mean = np.mean(body_acc_z, axis=1).reshape(-1,1)
   gyr_x_mean = np.mean(body_gyr_x, axis=1).reshape(-1,1)
   gyr_y_mean = np.mean(body_gyr_y, axis=1).reshape(-1,1)
   gyr_z_mean = np.mean(body_gyr_z, axis=1).reshape(-1,1)
   sd_acc_x = np.std(body_acc_x, axis=1).reshape(-1,1)
   sd_acc_y = np.std(body_acc_y, axis=1).reshape(-1,1)
   sd_acc_z = np.std(body_acc_z, axis=1).reshape(-1,1)
   sd_gyr_x = np.std(body_gyr_x, axis=1).reshape(-1,1)
   sd_gyr_y = np.std(body_gyr_y, axis=1).reshape(-1,1)
   sd_gyr_z = np.std(body_gyr_z, axis=1).reshape(-1,1)

   max_acc_x = np.amax(body_acc_x, axis=1).reshape(-1,1)
   max_acc_y = np.amax(body_acc_y, axis=1).reshape(-1,1)
   max_acc_z = np.amax(body_acc_z, axis=1).reshape(-1,1)
   max_gyr_x = np.amax(body_gyr_x, axis=1).reshape(-1,1)
   max_gyr_y = np.amax(body_gyr_y, axis=1).reshape(-1,1)
   max_gyr_z = np.amax(body_gyr_z, axis=1).reshape(-1,1)

   min_acc_x = np.amin(body_acc_x, axis=1).reshape(-1,1)
   min_acc_y = np.amin(body_acc_y, axis=1).reshape(-1,1)
   min_acc_z = np.amin(body_acc_z, axis=1).reshape(-1,1)
   min_gyr_x = np.amin(body_gyr_x, axis=1).reshape(-1,1)
   min_gyr_y = np.amin(body_gyr_y, axis=1).reshape(-1,1)
   min_gyr_z = np.amin(body_gyr_z, axis=1).reshape(-1,1)

   return np.concatenate((acc_x_mean, acc_y_mean, acc_z_mean, gyr_x_mean, gyr_y_mean, gyr_z_mean, sd_acc_x, sd_acc_y, sd_acc_z, sd_gyr_x, sd_gyr_y, sd_gyr_z, max_acc_x, max_acc_y, max_acc_z, max_gyr_x, max_gyr_y, max_gyr_z, min_acc_x, min_acc_y, min_acc_z, min_gyr_x, min_gyr_y, min_gyr_z), axis=1)

if __name__ == "__main__":
    main()