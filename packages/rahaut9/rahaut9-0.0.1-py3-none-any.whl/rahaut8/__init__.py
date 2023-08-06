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
}\n\
"
  print(s)
h4b()