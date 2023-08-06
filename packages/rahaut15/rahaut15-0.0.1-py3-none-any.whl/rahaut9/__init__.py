from collections import Counter
  
def count_in_list(l, word):
  c = Counter(l)
  return c[word]

def h1():
  s="#include<bits/stdc++.h>\n\
#include<omp.h>\n\
using namespace std;\n\
void serial_dfs(int src, int v, vector<vector<int>> adj, vector<bool> &visited, vector<int> &dfs)\n\
{\n\
	stack<int> s;\n\
	s.push(src);\n\
	while(!s.empty())\n\
	{\n\
		int node = s.top();\n\
		s.pop();\n\
		if(!visited[node])\n\
		{\n\
			visited[node] = true;\n\
			dfs.push_back(node);\n\
			for(int i=0; i<v; i++){\n\
				if(adj[node][i] && !visited[i])\n\
				{\n\
					s.push(i);\n\
				}\n\
			}\n\
		}\n\
	}\n\
}\n\
void parallel_dfs(int src, int v, vector<vector<int>> adj, vector<bool> &visited, vector<int> &dfs)\n\
{\n\
	stack<int> s;\n\
	s.push(src);\n\
    	#pragma omp parallel\n\
    	{\n\
        	while(!s.empty()) \n\
        	{\n\
			int node = s.top();\n\
                	s.pop();\n\
                	if (!visited[node]) \n\
                	{\n\
                  		#pragma omp critical\n\
                    		{\n\
                        		visited[node] = true;\n\
                       			dfs.push_back(node); \n\
                    		}	\n\
                  		for(int i=0; i<v; i++)\n\
                    		{\n\
                    			if(adj[node][i] && !visited[i])\n\
                    				s.push(i);\n\
                    		}\n\
                    	}\n\
            	}\n\
        }\n\
}\n\
void serial_bfs(int src, int v, vector<vector<int>> adj, vector<bool> &visited, vector<int> &bfs)\n\
{\n\
	queue<int> q;\n\
	q.push(src);\n\
	while(!q.empty())\n\
	{\n\
		int node = q.front();\n\
		q.pop();\n\
		if(!visited[node])\n\
		{\n\
			visited[node] = true;\n\
			bfs.push_back(node);\n\
			for(int i=0; i<v; i++){\n\
				if(adj[node][i] && !visited[i])\n\
				{\n\
					q.push(i);\n\
				}\n\
			}\n\
		}\n\
	}\n\
}\n\
void parallel_bfs(int src, int v, vector<vector<int>> adj, vector<bool> &visited, vector<int> &bfs)\n\
{\n\
	queue<int> q;\n\
	q.push(src);\n\
    	#pragma omp parallel\n\
    	{\n\
        	while(!q.empty()) \n\
        	{\n\
			int node = q.front();\n\
                	q.pop();\n\
                	if (!visited[node]) \n\
                	{\n\
                  		#pragma omp critical\n\
                    		{\n\
                        		visited[node] = true;\n\
                       			bfs.push_back(node); \n\
                    		}\n\
                  		for(int i=0; i<v; i++)\n\
                    		{\n\
                    			if(adj[node][i] && !visited[i])\n\
                    				q.push(i);\n\
                    		}\n\
                    	}\n\
            	}\n\
        }\n\
}\n\
int main()\n\
{\n\
	int v;\n\
	cout<<\n\"\n\n Enter the number of vertices : \n\";\n\
	cin>>v;\n\
	vector<vector<int>> adj(v, vector<int>(v, 0));\n\
	//randomly initializing adjacency matrix\n\
	for(int i=0; i<v; i++){\n\
		for(int j=0; j<v; j++)\n\
			if(i!=j)\n\
				adj[i][j] = rand()%2;\n\
	}\n\
	for(int i=0; i<v; i++)\n\
	{\n\
		cout<<endl;\n\
		for(int j=0; j<v; j++)\n\
			cout<<adj[i][j]<<\n\" \n\";\n\
	}\n\
	cout<<\n\"\n\n Enter the source vertex : \n\";\n\
	int src; cin>>src;\n\
	double start, end;\n\
	vector<int> bfs1, bfs2, dfs1, dfs2;\n\
	vector<bool> vis1(v, false), vis2(v, false), vis3(v, false), vis4(v, false);\n\
	cout<<\n\"\n\n**************** SERIAL BFS *****************\n\n\n\";\n\
	start = omp_get_wtime();\n\
	serial_bfs(src, v, adj, vis1, bfs1);\n\
	end = omp_get_wtime();\n\
	for(int i=0; i<bfs1.size(); i++)\n\
		cout<<bfs1[i]<<\n\" \n\";\n\
	cout<<\n\"\n\n Time taken = \n\"<<end-start<<\n\" seconds.\n\n\n\";\n\
	cout<<\n\"\n\n**************** PARALLEL BFS *****************\n\n\n\";\n\
	start = omp_get_wtime();\n\
	parallel_bfs(src, v, adj, vis2, bfs2);\n\
	end = omp_get_wtime();\n\
	for(int i=0; i<bfs2.size(); i++)\n\
		cout<<bfs2[i]<<\n\" \n\";\n\
	cout<<\n\"\n\n Time taken = \n\"<<end-start<<\n\" seconds.\n\n\n\";\n\
	cout<<\n\"\n\n**************** SERIAL DFS *****************\n\n\n\";\n\
	start = omp_get_wtime();\n\
	serial_dfs(src, v, adj, vis3, dfs1);\n\
	end = omp_get_wtime();\n\
	for(int i=0; i<dfs1.size(); i++)\n\
		cout<<dfs1[i]<<\n\" \n\";\n\
	cout<<\n\"\n\n Time taken = \n\"<<end-start<<\n\" seconds.\n\n\n\";\n\
	cout<<\n\"\n\n**************** PARALLEL DFS *****************\n\n\n\";\n\
	start = omp_get_wtime();\n\
	parallel_dfs(src, v, adj, vis4, dfs2);\n\
	end = omp_get_wtime();\n\
	for(int i=0; i<dfs2.size(); i++)\n\
		cout<<dfs2[i]<<\n\" \n\";\n\
	cout<<\n\"\n\n Time taken = \n\"<<end-start<<\n\" seconds.\n\n\n\";\n\
	return 0;\n\
		\n\
		\n\
		\n\
		\n\
		\n\
		\n\
		\n\
		\n\
    	\n\
		\n\
		\n\
		\n\
		\n\
		\n\
		\n\
		\n\
  }"
  print(s)
h1()
def h2():
  s="#include<bits/stdc++.h>\n\
#include<omp.h>\n\
using namespace std;\n\
void serial_bubble_sort(vector<int> &arr, int n)\n\
{\n\
	int i, j;\n\
    	for (i = 0; i < n - 1; i++) {\n\
        	for (j = 0; j < n - i - 1; j++) {\n\
            		if (arr[j] > arr[j + 1]) \n\
                		swap(arr[j], arr[j + 1]);\n\
       		}\n\
    	}\n\
}\n\
void parallel_bubble_sort(vector<int> &arr, int n)\n\
{\n\
	int phase, i;\n\
    	for (phase = 0; phase < n; phase++) {\n\
        	if (phase % 2 == 0) {  \n\
            		#pragma omp parallel for private(i)\n\
            		for (i = 2; i < n; i += 2) {\n\
                		if (arr[i - 1] > arr[i]) \n\
		            		swap(arr[i-1], arr[i]);\n\
                	}\n\
            	}\n\
        	else {  \n\
            		#pragma omp parallel for private(i)\n\
            		for (i = 1; i < n; i += 2) {\n\
                		if (arr[i - 1] > arr[i]) \n\
		            		swap(arr[i-1], arr[i]);\n\
                	}\n\
            	}\n\
        }\n\
}\n\
void merge(vector<int> &arr, int l, int m, int r) \n\
{\n\
	int n1 = m - l + 1;\n\
	int n2 = r - m;\n\
	int L[n1], R[n2];\n\
	int i, j, k;\n\
	for (i = 0; i < n1; i++)\n\
		L[i] = arr[l + i];\n\
	for (j = 0; j < n2; j++)\n\
		R[j] = arr[m + 1 + j];\n\
	i = 0;\n\
	j = 0;\n\
	k = l;\n\
	while (i < n1 && j < n2) {\n\
		if (L[i] <= R[j]) {\n\
	    		arr[k] = L[i];\n\
	    		i++;\n\
		}\n\
		else {\n\
	    		arr[k] = R[j];\n\
	    		j++;\n\
		}\n\
		k++;\n\
	}\n\
	while (i < n1) {\n\
		arr[k] = L[i];\n\
		i++;\n\
		k++;\n\
	}\n\
	while (j < n2) {\n\
		arr[k] = R[j];\n\
		j++;\n\
		k++;\n\
	}\n\
}\n\
void serial_merge_sort(vector<int> &arr, int l, int r)\n\
{\n\
	if (l < r) \n\
	{\n\
        	int m = l + (r - l) / 2;\n\
		serial_merge_sort(arr, l, m);\n\
		serial_merge_sort(arr, m + 1, r);\n\
        	merge(arr, l, m, r);\n\
    	}\n\
}\n\
void parallel_merge_sort(vector<int> &arr, int l, int r)\n\
{\n\
	if (l < r) \n\
	{\n\
        	int m = l + (r - l) / 2;\n\
        	#pragma omp parallel sections\n\
        	{\n\
            		#pragma omp section\n\
            		{\n\
                		parallel_merge_sort(arr, l, m);\n\
            		}\n\
            		#pragma omp section\n\
            		{\n\
                		parallel_merge_sort(arr, m + 1, r);\n\
            		}\n\
        	}\n\
        	merge(arr, l, m, r);\n\
    	}\n\
}\n\
int main()\n\
{\n\
	int n; \n\
	cout<<\n\"\n\n Enter the size of the array : \n\";\n\
	cin>>n;\n\
	vector<int> arr, arr1, arr2, arr3, arr4;\n\
	for(int i=0; i<n; i++)\n\
		arr.push_back(rand()%500);\n\
	cout<<endl;\n\
	double start, end;\n\
	cout<<\n\"\n\n**************** SERIAL BUBBLE SORT *****************\n\n\n\";\n\
	arr1 = arr;\n\
	start = omp_get_wtime();\n\
	serial_bubble_sort(arr1, n);\n\
	end = omp_get_wtime();\n\
	cout<<\n\"\n\n Time taken = \n\"<<end-start<<\n\" seconds.\n\n\n\";\n\
	cout<<\n\"\n\n**************** PARALLEL BUBBLE SORT *****************\n\n\n\";\n\
	arr2 = arr;\n\
	start = omp_get_wtime();\n\
	parallel_bubble_sort(arr2, n);\n\
	end = omp_get_wtime();\n\
	cout<<\n\"\n\n Time taken = \n\"<<end-start<<\n\" seconds.\n\n\n\";\n\
	cout<<\n\"\n\n**************** SERIAL MERGE SORT *****************\n\n\n\";\n\
	arr3 = arr;\n\
	start = omp_get_wtime();\n\
	serial_merge_sort(arr3, 0, n);\n\
	end = omp_get_wtime();\n\
	cout<<\n\"\n\n Time taken = \n\"<<end-start<<\n\" seconds.\n\n\n\";\n\
	cout<<\n\"\n\n**************** PARALLEL MERGE SORT *****************\n\n\n\";\n\
	arr4 = arr;\n\
	start = omp_get_wtime();\n\
	parallel_merge_sort(arr4, 0, n);\n\
	end = omp_get_wtime();\n\
	cout<<\n\"\n\n Time taken = \n\"<<end-start<<\n\" seconds.\n\n\n\";\n\
	return 0;\n\
		\n\
		\n\
		\n\
		\n\
		\n\
		\n\
		\n\
		\n\
    	\n\
		\n\
		\n\
		\n\
		\n\
		\n\
		\n\
		\n\
}"
  print(s)
h2()
def h3():
  s="#include <bits/stdc++.h>\n\
#include <omp.h>\n\
using namespace std;\n\
int arr[]={2 ,1 ,5 ,7 ,6 ,3};\n\
int n=6;\n\
void max_reduction(){\n\
	int maximum=arr[0];\n\
	#pragma omp parallel for reduction(max:maximum)\n\
	for(int i=0;i<n;i++){\n\
		if(arr[i]>maximum){\n\
			maximum=arr[i];		\n\
		}	\n\
	}\n\
	cout<<\n\"maximum element is: \n\"<<maximum<<endl;\n\
}\n\
void min_reduction(){\n\
	int minimum=arr[0];\n\
	#pragma omp parallel for reduction(min:minimum)\n\
	for(int i=0;i<n;i++){\n\
		if(arr[i]<minimum){\n\
			minimum=arr[i];		\n\
		}	\n\
	}\n\
	cout<<\n\"minimum element is: \n\"<<minimum<<endl;\n\
}\n\
void sum_reduction(){\n\
	int total=0;\n\
	#pragma omp parallel for reduction(+:total)\n\
	for(int i=0;i<n;i++){\n\
		total=total+arr[i]\n\
	}\n\
	cout<<\n\"sum of element is: \n\"<<total<<endl;\n\
}\n\
void avg_reduction(){\n\
	int total=0;\n\
	#pragma omp parallel for reduction(+:total)\n\
	for(int i=0;i<n;i++){\n\
		total=total+arr[i]\n\
	}\n\
	cout<<\n\"avg of element is: \n\"<<(total/(double)n)<<endl;\n\
}\n\
int main(){\n\
	min_reduction();\n\
	max_reduction();\n\
	sum_reduction();\n\
	avg_reduction();\n\
	return 0;\n\
		\n\
		\n\
		\n\
		\n\
		\n\
		\n\
		\n\
		\n\
    	\n\
		\n\
		\n\
		\n\
		\n\
		\n\
		\n\
		\n\
}"
  print(s)
h3()
def h4a():
  s="#include <iostream>\n\
#include <cstdlib>\n\
#include <cstdio>\n\
#include <ctime>\n\
#define TILE_WIDTH 32\n\
__global__ void matrixMult(int *a, int *b, int *c, int n)\n\
{\n\
    int row = blockIdx.y * blockDim.y + threadIdx.y;\n\
    int col = blockIdx.x * blockDim.x + threadIdx.x;\n\
    if (row < n && col < n) {\n\
        int sum = 0;\n\
        for (int i = 0; i < n; ++i) {\n\
            sum += a[row * n + i] * b[i * n + col];\n\
        }\n\
        c[row * n + col] = sum;\n\
    }\n\
}\n\
int main()\n\
{\n\
    int n;\n\
    n=4;\n\
    // allocate memory for matrices on host\n\
    int *a = new int[n * n];\n\
    int *b = new int[n * n];\n\
    int *c = new int[n * n];\n\
    // initialize matrices with random values\n\
    std::srand(std::time(0));\n\
    for (int i = 0; i < n * n; ++i) {\n\
        a[i] = std::rand() % 10;\n\
        b[i] = std::rand() % 10;\n\
    }\n\
    // allocate memory for matrices on device\n\
    int *dev_a, *dev_b, *dev_c;\n\
    cudaMalloc(&dev_a, n * n * sizeof(int));\n\
    cudaMalloc(&dev_b, n * n * sizeof(int));\n\
    cudaMalloc(&dev_c, n * n * sizeof(int));\n\
    // copy matrices from host to device\n\
    cudaMemcpy(dev_a, a, n * n * sizeof(int), cudaMemcpyHostToDevice);\n\
    cudaMemcpy(dev_b, b, n * n * sizeof(int), cudaMemcpyHostToDevice);\n\
    // launch kernel\n\
    dim3 dimGrid((n - 1) / TILE_WIDTH + 1, (n - 1) / TILE_WIDTH + 1, 1);\n\
    dim3 dimBlock(TILE_WIDTH, TILE_WIDTH, 1);\n\
    matrixMult<<<dimGrid, dimBlock>>>(dev_a, dev_b, dev_c, n);\n\
    // copy result matrix from device to host\n\
    cudaMemcpy(c, dev_c, n * n * sizeof(int), cudaMemcpyDeviceToHost);\n\
    // print result matrix\n\
 std::cout << \n\"Result matrix:\n\n\n\";\n\
    for (int i = 0; i < n; ++i) {\n\
        for (int j = 0; j < n; ++j) {\n\
            std::cout << a[i * n + j] << \n\" \n\";\n\
        }\n\
        std::cout << \n\"\n\n\n\";\n\
    }\n\
 std::cout << \n\"Result matrix:\n\n\n\";\n\
    for (int i = 0; i < n; ++i) {\n\
        for (int j = 0; j < n; ++j) {\n\
            std::cout << b[i * n + j] << \n\" \n\";\n\
        }\n\
        std::cout << \n\"\n\n\n\";\n\
    }\n\
    std::cout << \n\"Result matrix:\n\n\n\";\n\
    for (int i = 0; i < n; ++i) {\n\
        for (int j = 0; j < n; ++j) {\n\
            std::cout << c[i * n + j] << \n\" \n\";\n\
        }\n\
        std::cout << \n\"\n\n\n\";\n\
    }\n\
    // free memory on device\n\
    cudaFree(dev_a);\n\
    cudaFree(dev_b);\n\
    cudaFree(dev_c);\n\
    // free memory on host\n\
    delete[] a;\n\
    delete[] b;\n\
    delete[] c;\n\
    return 0;\n\
		\n\
		\n\
		\n\
		\n\
		\n\
		\n\
		\n\
		\n\
    	\n\
		\n\
		\n\
		\n\
		\n\
		\n\
		\n\
		\n\
}\n\
"
  print(s)
h4a()
def h4b():
  s="#include <iostream>\n\
#include <vector>\n\
#include <cstdlib>\n\
#include <ctime>\n\
using namespace std;\n\
__global__ void vector_add(int *a, int *b, int *c, int n) {\n\
    int i = threadIdx.x + blockIdx.x * blockDim.x;\n\
    if (i < n) {\n\
        c[i] = a[i] + b[i];\n\
    }\n\
}\n\
int main() {\n\
    const int n = 100;  // Length of vectors\n\
    std::vector<int> a(n), b(n), c(n);\n\
    // Initialize vectors with random values\n\
    std::srand(std::time(nullptr));\n\
    for (int i = 0; i < n; ++i) {\n\
        a[i] = std::rand() % 100;\n\
        b[i] = std::rand() % 100;\n\
    }\n\
    // Allocate memory on device\n\
    int *d_a, *d_b, *d_c;\n\
    cudaMalloc(&d_a, n * sizeof(int));\n\
    cudaMalloc(&d_b, n * sizeof(int));\n\
    cudaMalloc(&d_c, n * sizeof(int));\n\
    // Copy input data from host to device\n\
    cudaMemcpy(d_a, a.data(), n * sizeof(int), cudaMemcpyHostToDevice);\n\
    cudaMemcpy(d_b, b.data(), n * sizeof(int), cudaMemcpyHostToDevice);\n\
    // Launch kernel\n\
    const int block_size = 256;\n\
    const int num_blocks = (n + block_size - 1) / block_size;\n\
    vector_add<<<num_blocks, block_size>>>(d_a, d_b, d_c, n);\n\
    // Copy output data from device to host\n\
    cudaMemcpy(c.data(), d_c, n * sizeof(int), cudaMemcpyDeviceToHost);\n\
    // Free memory on device\n\
    cudaFree(d_a);\n\
    cudaFree(d_b);\n\
    cudaFree(d_c);\n\
    // Print results\n\
    std::cout << \n\"Vector a: \n\";\n\
    for (int i = 0; i < n; ++i) {\n\
        std::cout << a[i] << \n\" \n\";\n\
    }\n\
    std::cout << std::endl;\n\
    std::cout << \n\"Vector b: \n\";\n\
    for (int i = 0; i < n; ++i) {\n\
        std::cout << b[i] << \n\" \n\";\n\
    }\n\
    std::cout << std::endl;\n\
    std::cout << \n\"Vector c: \n\";\n\
    for (int i = 0; i < n; ++i) {\n\
        std::cout << c[i] << \n\" \n\";\n\
    }\n\
    std::cout << std::endl;\n\
    return 0;\n\
    \n\
		\n\
		\n\
		\n\
		\n\
		\n\
		\n\
		\n\
    	\n\
		\n\
		\n\
		\n\
		\n\
		\n\
		\n\
		\n\
}\n\
"
  print(s)
h4b()
def h5():
  s="!pip install numpy\n\
!pip install seaborn\n\
import numpy as np\n\
import matplotlib.pyplot as plt\n\
import tensorflow as tf\n\
from tensorflow import keras\n\
from sklearn.metrics import confusion_matrix\n\
import seaborn as sns\n\
(x_train, y_train), (x_test, y_test) = keras.datasets.fashion_mnist.load_data()\n\
x_train = x_train / 255.0\n\
x_test = x_test / 255.0\n\
x_train = x_train.reshape(-1, 28, 28, 1)\n\
x_test = x_test.reshape(-1, 28, 28, 1)\n\
class_names = [\n\'T_shirt/top\n\', \n\'Trouser\n\', \n\'Pullover\n\', \n\'Dress\n\', \n\'Coat\n\', \n\
               \n\'Sandal\n\', \n\'Shirt\n\', \n\'Sneaker\n\', \n\'Bag\n\', \n\'Ankle boot\n\']\n\
plt.figure(figsize=(12, 8))\n\
plt.subplot(2, 2, 1)\n\
classes, counts = np.unique(y_train, return_counts=True)\n\
plt.barh(class_names, counts)\n\
plt.title(\n\'Class distribution in training set\n\')\n\
plt.subplot(2, 2, 2)\n\
classes, counts = np.unique(y_test, return_counts=True)\n\
plt.barh(class_names, counts)\n\
plt.title(\n\'Class distribution in testing set\n\')\n\
plt.figure(figsize=(10, 10))\n\
for i in range(25):\n\
    plt.subplot(5, 5, i + 1)\n\
    plt.xticks([])\n\
    plt.yticks([])\n\
    plt.grid(False)\n\
    plt.imshow(x_train[i].reshape((28,28)), cmap=plt.cm.binary)\n\
    label_index = int(y_train[i])\n\
    plt.title(class_names[label_index])\n\
plt.show()\n\
plt.tight_layout()\n\
model = keras.Sequential([\n\
    keras.layers.Conv2D(32, (3,3), padding=\n\'same\n\', activation=\n\'relu\n\', input_shape=(28,28,1)),\n\
    keras.layers.MaxPooling2D((2,2)),\n\
    keras.layers.Conv2D(64, (3,3), padding=\n\'same\n\', activation=\n\'relu\n\'),\n\
    keras.layers.MaxPooling2D((2,2)),\n\
    keras.layers.Flatten(),\n\
    keras.layers.Dense(128, activation=\n\'relu\n\'),\n\
    keras.layers.Dense(10, activation=\n\'softmax\n\')\n\
])\n\
model.compile(optimizer=\n\'adam\n\',\n\
              loss=\n\'sparse_categorical_crossentropy\n\',\n\
              metrics=[\n\'accuracy\n\'])\n\
history=model.fit(x_train, y_train, epochs=10, validation_data=(x_test, y_test))\n\
test_loss, test_acc = model.evaluate(x_test, y_test)\n\
print(\n\'Test accuracy:\n\', test_acc)\n\
plt.figure(figsize=(12, 8))\n\
plt.subplot(2, 2, 1)\n\
plt.plot(history.history[\n\'loss\n\'], label=\n\'Loss\n\')\n\
plt.plot(history.history[\n\'val_loss\n\'], label=\n\'val_Loss\n\')\n\
plt.legend()\n\
plt.title(\n\'Loss evolution\n\')\n\
plt.subplot(2, 2, 2)\n\
plt.plot(history.history[\n\'accuracy\n\'], label=\n\'accuracy\n\')\n\
plt.plot(history.history[\n\'val_accuracy\n\'], label=\n\'val_accuracy\n\')\n\
plt.legend()\n\
plt.title(\n\'Accuracy evolution\n\')\n\
predicted_classes = model.predict(x_test)\n\
predicted_classes = np.argmax(predicted_classes, axis=1)\n\
test_img = x_test[0]\n\
prediction = model.predict(x_test)\n\
prediction[0]\n\
np.argmax(prediction[0])\n\
L = 5\n\
W = 5\n\
fig, axes = plt.subplots(L, W, figsize = (12,12))\n\
axes = axes.ravel()\n\
for i in np.arange(0, L * W):  \n\
    axes[i].imshow(x_test[i].reshape(28,28))\n\
    axes[i].set_title(f\n\"Prediction Class = {(predicted_classes[i]):0.1f}\n\n True Class = {y_test[i]:0.1f}\n\")\n\
    axes[i].axis(\n\'off\n\')\n\
plt.subplots_adjust(wspace=0.5)\n\
cm = confusion_matrix(y_test, predicted_classes)\n\
plt.figure(figsize = (14,10))\n\
sns.heatmap(cm, annot=True)\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
    	\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
"
  print(s)

h5()
def h6():
  s="import numpy as np\n\
from keras import models, layers, optimizers\n\
from keras.preprocessing.text import Tokenizer\n\
# from keras.preprocessing.sequence import pad_sequences\n\
from tensorflow.keras.utils import pad_sequences, to_categorical\n\
import pandas as pd\n\
from sklearn import preprocessing\n\
# Load the data\n\
df=pd.read_csv(\n\"IMDB_Dataset.csv\n\")\n\
train_df = df.sample(frac=0.8, random_state=25)\n\
test_df = df.drop(train_df.index)\n\
print(train_df)\n\
print(test_df)\n\
model = models.Sequential()\n\
model.add(layers.Embedding(10000, 64, input_length=max_length))\n\
model.add(layers.Flatten())\n\
model.add(layers.Dropout(0.2)),\n\
model.add(layers.Dense(32, activation=\n\'relu\n\'))\n\
model.add(layers.Dropout(0.5))\n\
model.add(layers.Dense(1, activation=\n\'sigmoid\n\'))\n\
model.compile(optimizer=\n\'adam\n\',  loss=\n\'binary_crossentropy\n\', metrics=[\n\'accuracy\n\'])\n\
history = model.fit(train_data, train_labels, epochs=5, batch_size=32, validation_split=0.2)\n\
test_labels= label_encoder.fit_transform(test_df[\n\'sentiment\n\'])\n\
print(test_labels[2])\n\
#test_labels = to_categorical(test_df[\n\'sentiment\n\'])\n\
test_loss, test_acc = model.evaluate(test_data, test_labels)\n\
print(\n\'Test accuracy:\n\', test_acc)\n\
import matplotlib.pyplot as plt\n\
plt.plot(history.history[\n\'loss\n\'], label=\n\'Training Loss\n\')\n\
plt.plot(history.history[\n\'val_loss\n\'], label=\n\'Validation Loss\n\')\n\
plt.xlabel(\n\'Epoch\n\')\n\
plt.ylabel(\n\'Loss\n\')\n\
plt.legend()\n\
plt.show()\n\
plt.plot(history.history[\n\'accuracy\n\'], label=\n\'Training Accuracy\n\')\n\
plt.plot(history.history[\n\'val_accuracy\n\'], label=\n\'Validation Accuracy\n\')\n\
plt.xlabel(\n\'Epoch\n\')\n\
plt.ylabel(\n\'Accuracy\n\')\n\
plt.legend()\n\
plt.show()\n\
predictions = model.predict(test_data)\n\
text = tokenizer.sequences_to_texts(test_data)\n\
pred = np.zeros(len(predictions))\n\
for i, score in enumerate(predictions):\n\
    pred[i] = np.round(score)\n\
predicted_sentiments = [\n\'positive\n\' if label == 1 else \n\'negative\n\' for label in pred]  \n\
print(f\n\"Review text: {text[5]}\n\n\n\")\n\
print(f\n\"Review : {predicted_sentiments[5]}\n\")\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
    	\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
"
  print(s)

h6()
def h7():
  s="import tensorflow as tf\n\
import numpy as np\n\
import pandas as pd\n\
from sklearn import preprocessing\n\
from sklearn.model_selection import train_test_split\n\
from sklearn.metrics import mean_squared_error\n\
df = pd.read_csv(\n\'HousingData.csv\n\')\n\
df.head(10)\n\
df.isnull().sum()\n\
df.isnull().sum()\n\
from sklearn.model_selection import train_test_split\n\
X = df.loc[:, df.columns != \n\'MEDV\n\']\n\
y = df.loc[:, df.columns == \n\'MEDV\n\']\n\
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=123)\n\
from keras.models import Sequential\n\
from keras.layers import Dense\n\
model = Sequential()\n\
model.add(Dense(128, input_shape=(13, ), activation=\n\'relu\n\', name=\n\'dense_1\n\'))\n\
model.add(Dense(64, activation=\n\'relu\n\', name=\n\'dense_2\n\'))\n\
model.add(Dense(1, activation=\n\'linear\n\', name=\n\'dense_output\n\'))\n\
model.compile(optimizer=\n\'adam\n\', loss=\n\'mse\n\', metrics=[\n\'mae\n\'])\n\
model.summary()\n\
history = model.fit(X_train, y_train, epochs=100, validation_split=0.05, verbose = 1)\n\
y_pred = model.predict(X_test)\n\
mse = mean_squared_error(y_test, y_pred)**(0.5)\n\
mse\n\
new_input = np.array([[0.006,18.0,2.3,0.0,0.53,6.5,65.2,4.0,1.0,296.0,15.0,396.9,4.98]])\n\
predictions = model.predict(new_input)\n\
print(\n\"Predicted house price:\n\", predictions[0][0])\n\
  		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
    	\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
  "
  print(s)

h7()
def h8():
    s="!pip install keras\n\
!pip install tensorflow\n\
import numpy as np \n\
import pandas as pd \n\
import matplotlib.pyplot as plt\n\
from sklearn.preprocessing import MinMaxScaler\n\
from keras.models import Sequential\n\
from keras.layers import Dense\n\
from keras.layers import LSTM\n\
from keras.layers import Dropout\n\
dataset_train = pd.read_csv(\n\"trainset.csv\n\")\n\
dataset_train.head(10)\n\
trainset = dataset_train.iloc[:,1:2].values\n\
trainset\n\
sc = MinMaxScaler(feature_range = (0,1))\n\
training_scaled = sc.fit_transform(trainset)\n\
training_scaled\n\
x_train = []\n\
y_train = []\n\
for i in range(60,1259):\n\
    x_train.append(training_scaled[i-60:i, 0])\n\
    y_train.append(training_scaled[i,0])\n\
    x_train = np.array(x_train)\n\
y_train=np.array(y_train)\n\
x_train.shape\n\
x_train = np.reshape(x_train, (x_train.shape[0],x_train.shape[1],1))\n\
model = Sequential()\n\
model.add(LSTM(units = 50,return_sequences = True,input_shape = (x_train.shape[1],1)))\n\
model.add(Dropout(0.2))\n\
model.add(LSTM(units = 50,return_sequences = True))\n\
model.add(Dropout(0.2))\n\
model.add(LSTM(units = 50,return_sequences = True))\n\
model.add(Dropout(0.2))\n\
model.add(LSTM(units = 50))\n\
model.add(Dropout(0.2))\n\
model.add(Dense(units = 1))\n\
model.compile(optimizer = \n\'adam\n\',loss = \n\'mean_squared_error\n\')\n\
model.fit(x_train,y_train,epochs = 30, batch_size = 32)\n\
dataset_test =pd.read_csv(\n\"testset.csv\n\")\n\
real_stock_price = dataset_test.iloc[:,1:2].values\n\
dataset_total = pd.concat((dataset_train[\n\'Open\n\'],dataset_test[\n\'Open\n\']),axis = 0)\n\
dataset_total\n\
inputs = dataset_total[len(dataset_total) - len(dataset_test)-60:].values\n\
inputs\n\
inputs = inputs.reshape(-1,1)\n\
inputs\n\
inputs = sc.transform(inputs)\n\
inputs.shape\n\
x_test = []\n\
for i in range(60,185):\n\
    x_test.append(inputs[i-60:i,0])\n\
x_test = np.array(x_test)\n\
x_test.shape\n\
x_test = np.reshape(x_test, (x_test.shape[0],x_test.shape[1],1))\n\
x_test.shape\n\
predicted_price = model.predict(x_test)\n\
predicted_price = sc.inverse_transform(predicted_price)\n\
predicted_price\n\
plt.plot(real_stock_price,color = \n\'red\n\', label = \n\'Real Price\n\')\n\
plt.plot(predicted_price, color = \n\'blue\n\', label = \n\'Predicted Price\n\')\n\
plt.title(\n\'Google Stock Price Prediction\n\')\n\
plt.xlabel(\n\'Time\n\')\n\
plt.ylabel(\n\'Google Stock Price\n\')\n\
plt.legend()\n\
plt.show()\n\
  		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
    	\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
		\n\n\n\
    "
    print(s)
    
h8()
def h9():
  s="import pandas as pd\n\
import matplotlib.pyplot as plt\n\
import numpy as np\n\
from sklearn import model_selection\n\
from sklearn.preprocessing import StandardScaler,LabelEncoder, OneHotEncoder\n\
from sklearn.neural_network import MLPClassifier\n\
from sklearn.model_selection import train_test_split\n\
from sklearn.metrics import classification_report\n\
from sklearn.metrics import confusion_matrix\n\
from sklearn.metrics import accuracy_score\n\
from tensorflow.keras.models import Sequential\n\
from tensorflow.keras.layers import Dense, Dropout\n\
# from sklearn import preprocessing\n\
# from yellowbrick.classifier import ConfusionMatrix\n\
df = pd.read_csv(\n\"letter-recognition.data\n\", sep = \n\",\n\", header=None)\n\
df.head(10)\n\
names = [\n\'letter_Class\n\',\n\
         \n\'x-box\n\',\n\
         \n\'y-box\n\',\n\
         \n\'width\n\',\n\
         \n\'high\n\',\n\
         \n\'onpix\n\',\n\
         \n\'x-bar\n\',\n\
         \n\'y-bar\n\',\n\
         \n\'x2bar\n\',\n\
         \n\'y2bar\n\',\n\
         \n\'xybar\n\',\n\
         \n\'x2ybr\n\',\n\
         \n\'xy2br\n\',\n\
         \n\'x-ege\n\',\n\
         \n\'xegvy\n\',\n\
         \n\'y-ege\n\',\n\
         \n\'yegvx\n\']\n\
df.columns = names\n\
df.head(10)\n\
# X = df.iloc[:, 1 : 17]\n\
# Y = df.select_dtypes(include = [object])\n\
X = df.iloc[:, 1:].values\n\
y = df.iloc[:, 0].values\n\
label_encoder = LabelEncoder()\n\
y = label_encoder.fit_transform(y)\n\
y\n\
onehot_encoder = OneHotEncoder(categories=\n\'auto\n\')\n\
y = onehot_encoder.fit_transform(y.reshape(-1, 1)).toarray()\n\
y\n\
scaler = StandardScaler()\n\
X = scaler.fit_transform(X)\n\
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\n\
model = Sequential()\n\
model.add(Dense(64, input_shape=(16,), activation=\n\'relu\n\'))\n\
model.add(Dropout(0.2))\n\
model.add(Dense(32, activation=\n\'relu\n\'))\n\
model.add(Dropout(0.2))\n\
model.add(Dense(26, activation=\n\'softmax\n\'))\n\
model.compile(loss=\n\'categorical_crossentropy\n\', optimizer=\n\'adam\n\', metrics=[\n\'accuracy\n\'])\n\
model.fit(X_train, y_train, epochs=200, batch_size=32, validation_data=(X_test, y_test))\n\
score = model.evaluate(X_test, y_test)\n\
print(f\n\'Test loss: {score[0]}\n\')\n\
print(f\n\'Test accuracy: {score[1]}\n\')\n\
# print(confusion_matrix(Y_test, predictions))\n\
y_pred = model.predict(X_test)\n\
y_pred = np.argmax(y_pred, axis=1)\n\
y_true = np.argmax(y_test, axis=1)\n\
cm = confusion_matrix(y_true, y_pred)\n\
print(cm)\n\
target_names = label_encoder.inverse_transform(np.arange(26))\n\
print(classification_report(y_true, y_pred, target_names=target_names))\n\
# create a new input with 16 feature values\n\
new_input = [[4,2,5,4,4,8,7,6,6,7,6,6,2,8,7,10]]\n\
# standardize the input using the scaler object\n\
new_input = scaler.transform(new_input)\n\
# make a prediction\n\
prediction = model.predict(new_input)\n\
# print the predicted letter\n\
val=np.argmax(prediction)\n\
print(chr(ord(\n\'A\n\')+val))\n\
# create a new input with 16 feature values\n\
new_input = [[5,12,3,7,2,10,5,5,4,13,3,9,2,8,4,10]]\n\
# standardize the input using the scaler object\n\
new_input = scaler.transform(new_input)\n\
# make a prediction\n\
prediction = model.predict(new_input)\n\
# print the predicted letter\n\
val=np.argmax(prediction)\n\
print(chr(ord(\n\'A\n\')+val))\n\
  "
  print(s)
h9()