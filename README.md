## VOS-Server

This is the server side implementation of VOS. The server supports `Python` and uses `Flask` as backend framework.   
Find the allied client side [code here](https://github.com/AKS1996/VOS-Client.git). In short ```Desktop=Process``` and ```Server=OS```.  

## Demo1: Scheduling
We'll try to simulate various scheduling algorithms over cloud.
For simplicity, we assume the execution time is specified for each process. If many instances of the client side script are running, the server needs an algorithm to cater all of them.

## Demo2: Synchronization
For the prime testing problem, the list of data set assigned to each client is a shared resource.
