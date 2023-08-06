def assignment1():
    print("""
        #include <iostream>
        #include <vector>
        #include <queue>
        #include <stack>
        #include <cstdlib>
        #include <ctime>
        #include <omp.h>
        #include <chrono>

        using namespace std;
        using namespace std::chrono;

        // Function to perform Breadth-First Search (BFS)
        void BFS(const vector<vector<int>>& graph, int startVertex) {
            vector<bool> visited(graph.size(), false);
            queue<int> q;

            visited[startVertex] = true;
            q.push(startVertex);

            cout << "BFS traversal: ";

            while (!q.empty()) {
                int currentVertex = q.front();
                q.pop();

                cout << currentVertex << " ";

                for (int i = 0; i < graph[currentVertex].size(); ++i) {
                    int adjacentVertex = graph[currentVertex][i];
                    if (!visited[adjacentVertex]) {
                        visited[adjacentVertex] = true;
                        q.push(adjacentVertex);
                    }
                }
            }

            cout << endl;
        }

        // Function to perform Depth-First Search (DFS)
        void DFS(const vector<vector<int>>& graph, int startVertex) {
            vector<bool> visited(graph.size(), false);
            stack<int> s;

            s.push(startVertex);

            cout << "DFS traversal: ";

            while (!s.empty()) {
                int currentVertex = s.top();
                s.pop();

                if (!visited[currentVertex]) {
                    cout << currentVertex << " ";
                    visited[currentVertex] = true;

                    for (int i = 0; i < graph[currentVertex].size(); ++i) {
                        int adjacentVertex = graph[currentVertex][i];
                        if (!visited[adjacentVertex]) {
                            s.push(adjacentVertex);
                        }
                    }
                }
            }

            cout << endl;
        }

        // Function to perform Breadth-First Search (BFS) using OMP
        void BFS_PARALLEL(const vector<vector<int>>& graph, int startVertex) {
            vector<bool> visited(graph.size(), false);
            queue<int> q;

            visited[startVertex] = true;
            q.push(startVertex);

            cout << "BFS traversal: ";

            while (!q.empty()) {
                int currentVertex;
                #pragma omp critical
                {
                    currentVertex = q.front();
                    q.pop();
                }

                cout << currentVertex << " ";

                #pragma omp parallel for shared(visited, q)
                for (int i = 0; i < graph[currentVertex].size(); ++i) {
                    int adjacentVertex = graph[currentVertex][i];
                    if (!visited[adjacentVertex]) {
                        #pragma omp critical
                        {
                            visited[adjacentVertex] = true;
                            q.push(adjacentVertex);
                        }
                    }
                }
            }

            cout << endl;
        }

        // Function to perform Depth-First Search (DFS) using OMP
        void DFS_PARALLEL(const vector<vector<int>>& graph, int startVertex) {
            vector<bool> visited(graph.size(), false);
            stack<int> s;

            s.push(startVertex);

            cout << "DFS traversal: ";

            while (!s.empty()) {
                int currentVertex;
                #pragma omp critical
                {
                    currentVertex = s.top();
                    s.pop();
                }

                if (!visited[currentVertex]) {
                    cout << currentVertex << " ";
                    visited[currentVertex] = true;

                    #pragma omp parallel for shared(visited, s)
                    for (int i = 0; i < graph[currentVertex].size(); ++i) {
                        int adjacentVertex = graph[currentVertex][i];
                        if (!visited[adjacentVertex]) {
                            #pragma omp critical
                            {
                                s.push(adjacentVertex);
                            }
                        }
                    }
                }
            }

            cout << endl;
        }

        // Function to generate a random graph
        vector<vector<int>> generateRandomGraph(int numVertices, int numEdges) {
            vector<vector<int>> graph(numVertices);

            srand(time(nullptr));

            for (int i = 0; i < numEdges; ++i) {
                int u = rand() % numVertices;
                int v = rand() % numVertices;

                graph[u].push_back(v);
                graph[v].push_back(u);
            }

            return graph;
        }

        int main() {
            int numVertices, numEdges;
            cout << "Enter the number of vertices in the graph: ";
            cin >> numVertices;
            cout << "Enter the number of edges in the graph: ";
            cin >> numEdges;

            vector<vector<int>> graph = generateRandomGraph(numVertices, numEdges);

            int startVertex;
            cout << "Enter the starting vertex for traversal: ";
            cin >> startVertex;

            // auto start = high_resolution_clock::now();
            BFS(graph, startVertex);
            // auto end = high_resolution_clock::now();

            // auto dur = duration_cast<microseconds>(end - start);
            // cout << dur.count() << "ms" << endl;

            // start = high_resolution_clock::now();
            DFS(graph, startVertex);
            // end = high_resolution_clock::now();

            // dur = duration_cast<microseconds>(end - start);
            // cout << dur.count() << "ms" << endl;

            // start = high_resolution_clock::now();
            BFS_PARALLEL(graph, startVertex);
            // end = high_resolution_clock::now();

            // dur = duration_cast<microseconds>(end - start);
            // cout << dur.count() << "ms" << endl;

            // start = high_resolution_clock::now();
            DFS_PARALLEL(graph, startVertex);
            // end = high_resolution_clock::now();

            // dur = duration_cast<microseconds>(end - start);
            // cout << dur.count() << "ms" << endl;

            return 0;
        }
    """ 
    )

def assignment2():
    print(
        """
        #include <iostream>
        #include <vector>
        #include <cstdlib>
        #include <ctime>
        #include <omp.h>

        using namespace std;

        // Function to generate random input array
        vector<int> generateRandomArray(int size) {
            vector<int> arr(size);

            srand(time(nullptr));

            for (int i = 0; i < size; ++i) {
                arr[i] = rand() % 100;  // Generate random numbers between 0 and 99
            }

            return arr;
        }

        // Function to print the elements of an array
        void printArray(const vector<int>& arr) {
            for (int i = 0; i < arr.size(); ++i) {
                cout << arr[i] << " ";
            }
            cout << endl;
        }

        // Bubble Sort
        void bubbleSort(vector<int>& arr) {
            int n = arr.size();
            bool swapped;

            for (int i = 0; i < n - 1; ++i) {
                swapped = false;

                for (int j = 0; j < n - i - 1; ++j) {
                    if (arr[j] > arr[j + 1]) {
                        swap(arr[j], arr[j + 1]);
                        swapped = true;
                    }
                }

                // If no two elements were swapped in the inner loop, the array is already sorted
                if (!swapped) {
                    break;
                }
            }
        }

        // Merge two sorted subarrays into a single sorted array
        void merge(vector<int>& arr, int left, int mid, int right) {
            int n1 = mid - left + 1;
            int n2 = right - mid;

            vector<int> L(n1), R(n2);

            for (int i = 0; i < n1; ++i) {
                L[i] = arr[left + i];
            }
            for (int j = 0; j < n2; ++j) {
                R[j] = arr[mid + 1 + j];
            }

            int i = 0, j = 0, k = left;

            while (i < n1 && j < n2) {
                if (L[i] <= R[j]) {
                    arr[k] = L[i];
                    ++i;
                } else {
                    arr[k] = R[j];
                    ++j;
                }
                ++k;
            }

            while (i < n1) {
                arr[k] = L[i];
                ++i;
                ++k;
            }

            while (j < n2) {
                arr[k] = R[j];
                ++j;
                ++k;
            }
        }

        // Merge Sort
        void mergeSort(vector<int>& arr, int left, int right) {
            if (left < right) {
                int mid = left + (right - left) / 2;

                mergeSort(arr, left, mid);
                mergeSort(arr, mid + 1, right);

                merge(arr, left, mid, right);
            }
        }

        // Bubble Sort
        void bubbleSort_parallel(vector<int>& arr) {
            int n = arr.size();
            bool swapped;

            #pragma omp parallel shared(arr, n, swapped)
            {
                #pragma omp for
                for (int i = 0; i < n - 1; ++i) {
                    swapped = false;

                    for (int j = 0; j < n - i - 1; ++j) {
                        if (arr[j] > arr[j + 1]) {
                            swap(arr[j], arr[j + 1]);
                            swapped = true;
                        }
                    }

                    // If no two elements were swapped in the inner loop, the array is already sorted
                    if (!swapped) {
                        break;
                    }
                }
            }
        }

        // Merge Sort
        void mergeSort_parallel(vector<int>& arr, int left, int right) {
            if (left < right) {
                int mid = left + (right - left) / 2;

                #pragma omp parallel sections
                {
                    #pragma omp section
                    {
                        mergeSort(arr, left, mid);
                    }

                    #pragma omp section
                    {
                        mergeSort(arr, mid + 1, right);
                    }
                }

                merge(arr, left, mid, right);
            }
        }

        int main() {
            int size;
            cout << "Enter the size of the array: ";
            cin >> size;

            vector<int> arr = generateRandomArray(size);

            cout << "Original array: ";
            printArray(arr);

            vector<int> bubbleSortedArr = arr;
            bubbleSort(bubbleSortedArr);
            cout << "Bubble Sort result: ";
            printArray(bubbleSortedArr);

            vector<int> mergeSortedArr = arr;
            mergeSort(mergeSortedArr, 0, mergeSortedArr.size() - 1);
            cout << "Merge Sort result: ";
            printArray(mergeSortedArr);

            cout << "Bubble Sort result: ";
            bubbleSortedArr = arr;
            bubbleSort_parallel(bubbleSortedArr);
            printArray(bubbleSortedArr);

            cout << "Merge Sort result: ";
            mergeSortedArr = arr;
            mergeSort_parallel(mergeSortedArr, 0, mergeSortedArr.size() - 1);
            printArray(mergeSortedArr);

            return 0;
        }
        """
    )

def assignment3():
    print(
        """
        #include <iostream>
        #include <vector>
        #include <cstdlib>
        #include <ctime>
        #include <algorithm>
        #include <omp.h>

        using namespace std;

        // Function to generate random input array
        vector<int> generateRandomArray(int size) {
            vector<int> arr(size);

            srand(time(nullptr));

            for (int i = 0; i < size; ++i) {
                arr[i] = rand() % 100;  // Generate random numbers between 0 and 99
            }

            return arr;
        }

        // Function to calculate the minimum value in the array
        int findMin(const vector<int>& arr) {
            int minVal = arr[0];

            for (int i = 1; i < arr.size(); ++i) {
                if (arr[i] < minVal) {
                    minVal = arr[i];
                }
            }

            return minVal;
        }

        // Function to calculate the maximum value in the array
        int findMax(const vector<int>& arr) {
            int maxVal = arr[0];

            for (int i = 1; i < arr.size(); ++i) {
                if (arr[i] > maxVal) {
                    maxVal = arr[i];
                }
            }

            return maxVal;
        }

        // Function to calculate the sum of the elements in the array
        int calculateSum(const vector<int>& arr) {
            int sum = 0;

            for (int i = 0; i < arr.size(); ++i) {
                sum += arr[i];
            }

            return sum;
        }

        // Function to calculate the average of the elements in the array
        double calculateAverage(const vector<int>& arr) {
            int sum = calculateSum(arr);
            int n = arr.size();

            return static_cast<double>(sum) / n;
        }

        // Function to calculate the minimum value in the array
        int findMin_parallel(const vector<int>& arr) {
            int minVal = arr[0];

            #pragma omp parallel for reduction(min : minVal)
            for (int i = 1; i < arr.size(); ++i) {
                if (arr[i] < minVal) {
                    minVal = arr[i];
                }
            }

            return minVal;
        }

        // Function to calculate the maximum value in the array
        int findMax_parallel(const vector<int>& arr) {
            int maxVal = arr[0];

            #pragma omp parallel for reduction(max : maxVal)
            for (int i = 1; i < arr.size(); ++i) {
                if (arr[i] > maxVal) {
                    maxVal = arr[i];
                }
            }

            return maxVal;
        }

        // Function to calculate the sum of the elements in the array
        int calculateSum_parallel(const vector<int>& arr) {
            int sum = 0;

            #pragma omp parallel for reduction(+: sum)
            for (int i = 0; i < arr.size(); ++i) {
                sum += arr[i];
            }

            return sum;
        }

        // Function to calculate the average of the elements in the array
        double calculateAverage_parallel(const vector<int>& arr) {
            int sum = calculateSum(arr);
            int n = arr.size();

            return static_cast<double>(sum) / n;
        }

        int main() {
            int size;
            cout << "Enter the size of the array: ";
            cin >> size;

            vector<int> arr = generateRandomArray(size);

            cout << "Generated array: ";
            for (int i = 0; i < arr.size(); ++i) {
                cout << arr[i] << " ";
            }
            cout << endl;

            int minValue = findMin(arr);
            int maxValue = findMax(arr);
            int sum = calculateSum(arr);
            double average = calculateAverage(arr);

            cout << "Minimum value: " << minValue << endl;
            cout << "Maximum value: " << maxValue << endl;
            cout << "Sum of the elements: " << sum << endl;
            cout << "Average of the elements: " << average << endl;

            minValue = findMin_parallel(arr);
            maxValue = findMax_parallel(arr);
            sum = calculateSum_parallel(arr);
            average = calculateAverage_parallel(arr);

            cout << "Minimum value: " << minValue << endl;
            cout << "Maximum value: " << maxValue << endl;
            cout << "Sum of the elements: " << sum << endl;
            cout << "Average of the elements: " << average << endl;

            return 0;
        }
        """
    )

def assignment4():
    print("""
        #include <iostream>
        #include <vector>
        #include <cstdlib>
        #include <ctime>
        #include <cmath>
        #include <omp.h>

        using namespace std;

        // Function to generate random input data
        vector<pair<double, double>> generateRandomData(int size) {
            vector<pair<double, double>> data(size);

            srand(time(nullptr));

            for (int i = 0; i < size; ++i) {
                double x = rand() % 100;  // Generate random x values between 0 and 99
                double y = 2 * x + (rand() % 10 - 5);  // Generate y values with some noise
                data[i] = make_pair(x, y);
            }

            return data;
        }

        // Function to calculate the mean of a vector of values
        double calculateMean(const vector<double>& values) {
            double sum = 0.0;

            for (double value : values) {
                sum += value;
            }

            return sum / values.size();
        }

        // Function to calculate the slope (m) of the linear regression line
        double calculateSlope(const vector<pair<double, double>>& data) {
            vector<double> xValues, yValues;

            for (const auto& point : data) {
                xValues.push_back(point.first);
                yValues.push_back(point.second);
            }

            double xMean = calculateMean(xValues);
            double yMean = calculateMean(yValues);

            double numerator = 0.0, denominator = 0.0;

            for (int i = 0; i < data.size(); ++i) {
                numerator += (xValues[i] - xMean) * (yValues[i] - yMean);
                denominator += pow(xValues[i] - xMean, 2);
            }

            return numerator / denominator;
        }

        // Function to calculate the slope (m) of the linear regression line
        double calculateSlope_parallel(const vector<pair<double, double>>& data) {
            vector<double> xValues, yValues;

            for (const auto& point : data) {
                xValues.push_back(point.first);
                yValues.push_back(point.second);
            }

            double xMean = calculateMean(xValues);
            double yMean = calculateMean(yValues);

            double numerator = 0.0, denominator = 0.0;

            #pragma omp parallel for reduction(+: numerator, denominator)
            for (int i = 0; i < data.size(); ++i) {
                numerator += (xValues[i] - xMean) * (yValues[i] - yMean);
                denominator += pow(xValues[i] - xMean, 2);
            }

            return numerator / denominator;
        }

        // Function to calculate the y-intercept (c) of the linear regression line
        double calculateIntercept(double slope, double xMean, double yMean) {
            return yMean - slope * xMean;
        }

        // Function to perform linear regression and return the slope and intercept
        pair<double, double> performLinearRegression(const vector<pair<double, double>>& data) {
            vector<double> xValues, yValues;

            for (const auto& point : data) {
                xValues.push_back(point.first);
                yValues.push_back(point.second);
            }

            double xMean = calculateMean(xValues);
            double yMean = calculateMean(yValues);
            double slope = calculateSlope(data);

            double intercept = calculateIntercept(slope, xMean, yMean);

            return make_pair(slope, intercept);
        }

        // Function to perform linear regression and return the slope and intercept
        pair<double, double> performLinearRegression_parallel(const vector<pair<double, double>>& data) {
            vector<double> xValues, yValues;

            for (const auto& point : data) {
                xValues.push_back(point.first);
                yValues.push_back(point.second);
            }

            double xMean = calculateMean(xValues);
            double yMean = calculateMean(yValues);
            double slope = calculateSlope_parallel(data);
            
            double intercept = calculateIntercept(slope, xMean, yMean);

            return make_pair(slope, intercept);
        }

        int main() {
            int size;
            cout << "Enter the number of data points: ";
            cin >> size;

            vector<pair<double, double>> data = generateRandomData(size);

            cout << "Generated data points: " << endl;
            for (const auto& point : data) {
                cout << "(" << point.first << ", " << point.second << ") , ";
            }

            cout << endl;

            pair<double, double> regression = performLinearRegression(data);
            double slope = regression.first;
            double intercept = regression.second;

            cout << "Linear regression line equation: y = " << slope << "x + " << intercept << endl;

            regression = performLinearRegression_parallel(data);
            slope = regression.first;
            intercept = regression.second;

            cout << "Linear regression line equation: y = " << slope << "x + " << intercept << endl;

            return 0;
        }
    """)

def assignment5():
    print("""
        #include <iostream>
        #include <vector>
        #include <cstdlib>
        #include <ctime>
        #include <cmath>
        #include <algorithm>
        #include <omp.h>

        using namespace std;

        // Data point structure
        struct DataPoint {
            double x;
            double y;
            int label;
        };

        // Function to generate random input data
        vector<DataPoint> generateRandomData(int size, int numClasses) {
            vector<DataPoint> data(size);

            srand(time(nullptr));

            for (int i = 0; i < size; ++i) {
                double x = rand() % 100;  // Generate random x values between 0 and 99
                double y = rand() % 100;  // Generate random y values between 0 and 99
                int label = rand() % numClasses;  // Assign a random label
                data[i] = {x, y, label};
            }

            return data;
        }

        // Function to calculate the Euclidean distance between two data points
        double calculateDistance(const DataPoint& p1, const DataPoint& p2) {
            double dx = p2.x - p1.x;
            double dy = p2.y - p1.y;
            return sqrt(dx * dx + dy * dy);
        }

        // Function to perform K-Nearest Neighbors classification
        int classifyKNN(const vector<DataPoint>& data, const DataPoint& point, int k) {
            // Calculate distances between the point and all data points
            vector<pair<double, int>> distances;
            for (const auto& dataPoint : data) {
                double distance = calculateDistance(point, dataPoint);
                distances.push_back({distance, dataPoint.label});
            }

            // Sort distances in ascending order
            sort(distances.begin(), distances.end());

            // Count the occurrences of each label in the k nearest neighbors
            vector<int> labelCount(k, 0);
            for (int i = 0; i < k; ++i) {
                int label = distances[i].second;
                labelCount[label]++;
            }

            // Find the label with the maximum count
            int maxCount = 0;
            int maxLabel = -1;
            for (int i = 0; i < k; ++i) {
                if (labelCount[i] > maxCount) {
                    maxCount = labelCount[i];
                    maxLabel = i;
                }
            }

            return maxLabel;
        }

        // Function to perform K-Nearest Neighbors classification
        int classifyKNN_parallel(const vector<DataPoint>& data, const DataPoint& point, int k) {
            // Calculate distances between the point and all data points
            int dataSize = data.size();
            vector<pair<double, int>> distances(dataSize);

            #pragma omp parallel for
            for (int i = 0; i < dataSize; ++i) {
                double distance = calculateDistance(point, data[i]);
                distances[i] = make_pair(distance, data[i].label);
            }

            // Sort distances in ascending order
            sort(distances.begin(), distances.end());

            // Count the occurrences of each label in the k nearest neighbors
            vector<int> labelCount(k, 0);

            #pragma omp parallel for
            for (int i = 0; i < k; ++i) {
                int label = distances[i].second;
                #pragma omp atomic
                labelCount[label]++;
            }

            // Find the label with the maximum count
            int maxCount = 0;
            int maxLabel = -1;

            #pragma omp parallel for
            for (int i = 0; i < k; ++i) {
                #pragma omp critical
                {
                    if (labelCount[i] > maxCount) {
                        maxCount = labelCount[i];
                        maxLabel = i;
                    }
                }
            }

            return maxLabel;
        }

        int main() {
            int size;
            int numClasses;
            int k;

            cout << "Enter the number of data points: ";
            cin >> size;

            cout << "Enter the number of classes: ";
            cin >> numClasses;

            cout << "Enter the value of k: ";
            cin >> k;

            vector<DataPoint> data = generateRandomData(size, numClasses);

            cout << "Generated data points: " << endl;
            for (const auto& point : data) {
                cout << "(" << point.x << ", " << point.y << ") Label: " << point.label << endl;
            }

            // Generate a random point for classification
            DataPoint testPoint;
            testPoint.x = rand() % 100;
            testPoint.y = rand() % 100;

            int predictedLabel = classifyKNN(data, testPoint, k);

            cout << "Test point: (" << testPoint.x << ", " << testPoint.y << ")" << endl;
            cout << "Predicted label: " << predictedLabel << endl;

            predictedLabel = classifyKNN_parallel(data, testPoint, k);

            cout << "Test point: (" << testPoint.x << ", " << testPoint.y << ")" << endl;
            cout << "Predicted label: " << predictedLabel << endl;

            return 0;
        }
    """)

def assignmentcuda1():
    print("""
        #include <iostream>
        #include <vector>
        #include <cuda_runtime.h>

        void vectorAdditionCPU(const std::vector<float>& a, const std::vector<float>& b, std::vector<float>& result) {
            int size = a.size();
            for (int i = 0; i < size; ++i) {
                result[i] = a[i] + b[i];
            }
        }

        int main() {
            int size = 1000000; // Size of the vectors
            int numBytes = size * sizeof(float);

            // Allocate memory on the CPU
            std::vector<float> h_a(size);
            std::vector<float> h_b(size);
            std::vector<float> h_result(size);
            std::vector<float> h_resultCPU(size);

            // Initialize input vectors with random values
            for (int i = 0; i < size; ++i) {
                h_a[i] = static_cast<float>(rand()) / RAND_MAX;
                h_b[i] = static_cast<float>(rand()) / RAND_MAX;
            }

            // Allocate memory on the GPU
            float* d_a;
            float* d_b;
            float* d_result;
            cudaMalloc((void**)&d_a, numBytes);
            cudaMalloc((void**)&d_b, numBytes);
            cudaMalloc((void**)&d_result, numBytes);

            // Copy input vectors from host to device
            cudaMemcpy(d_a, h_a.data(), numBytes, cudaMemcpyHostToDevice);
            cudaMemcpy(d_b, h_b.data(), numBytes, cudaMemcpyHostToDevice);

            // Set up the execution configuration
            int blockSize = 256;
            int gridSize = (size + blockSize - 1) / blockSize;

            // Launch the CUDA kernel
            vectorAddition<<<gridSize, blockSize>>>(d_a, d_b, d_result, size);

            // Copy the result vector from device to host
            cudaMemcpy(h_result.data(), d_result, numBytes, cudaMemcpyDeviceToHost);

            // Perform vector addition on the CPU for verification
            vectorAdditionCPU(h_a, h_b, h_resultCPU);

            // Compare the results
            bool success = true;
            for (int i = 0; i < size; ++i) {
                if (std::abs(h_result[i] - h_resultCPU[i]) > 1e-5) {
                    success = false;
                    break;
                }
            }

            if (success) {
                std::cout << "Vector addition successful!" << std::endl;
            } else {
                std::cout << "Vector addition failed!" << std::endl;
            }

            // Free device memory
            cudaFree(d_a);
            cudaFree(d_b);
            cudaFree(d_result);

            return 0;
        }
    """)

def assignmentcuda2():
    print("""
        #include <iostream>
        #include <cuda_runtime.h>

        // CUDA kernel for matrix multiplication
        __global__ void matrixMultiplication(const float* A, const float* B, float* C, int N) {
            int row = blockIdx.y * blockDim.y + threadIdx.y;
            int col = blockIdx.x * blockDim.x + threadIdx.x;

            if (row < N && col < N) {
                float sum = 0.0f;
                for (int i = 0; i < N; ++i) {
                    sum += A[row * N + i] * B[i * N + col];
                }
                C[row * N + col] = sum;
            }
        }

        int main() {
            int N = 1024;  // Size of the square matrices
            int numElements = N * N;
            int numBytes = numElements * sizeof(float);

            // Allocate memory on the host (CPU)
            float* h_A = new float[numElements];
            float* h_B = new float[numElements];
            float* h_C = new float[numElements];
            float* h_result = new float[numElements];

            // Initialize input matrices with random values
            for (int i = 0; i < numElements; ++i) {
                h_A[i] = static_cast<float>(rand()) / RAND_MAX;
                h_B[i] = static_cast<float>(rand()) / RAND_MAX;
            }

            // Allocate memory on the device (GPU)
            float* d_A;
            float* d_B;
            float* d_C;
            cudaMalloc((void**)&d_A, numBytes);
            cudaMalloc((void**)&d_B, numBytes);
            cudaMalloc((void**)&d_C, numBytes);

            // Copy input matrices from host to device
            cudaMemcpy(d_A, h_A, numBytes, cudaMemcpyHostToDevice);
            cudaMemcpy(d_B, h_B, numBytes, cudaMemcpyHostToDevice);

            // Set up the execution configuration
            dim3 blockSize(16, 16);
            dim3 gridSize((N + blockSize.x - 1) / blockSize.x, (N + blockSize.y - 1) / blockSize.y);

            // Launch the CUDA kernel
            matrixMultiplication<<<gridSize, blockSize>>>(d_A, d_B, d_C, N);

            // Copy the result matrix from device to host
            cudaMemcpy(h_C, d_C, numBytes, cudaMemcpyDeviceToHost);

            // Perform matrix multiplication on the CPU for verification
            for (int i = 0; i < N; ++i) {
                for (int j = 0; j < N; ++j) {
                    float sum = 0.0f;
                    for (int k = 0; k < N; ++k) {
                        sum += h_A[i * N + k] * h_B[k * N + j];
                    }
                    h_result[i * N + j] = sum;
                }
            }

            // Compare the results
            bool success = true;
            for (int i = 0; i < numElements; ++i) {
                if (std::abs(h_C[i] - h_result[i]) > 1e-5) {
                    success = false;
                    break;
                }
            }

            if (success) {
                std::cout << "Matrix multiplication successful!" << std::endl;
            } else {
                std::cout << "Matrix multiplication failed!" << std::endl;
            }

            // Free device and host memory
            cudaFree(d_A);
            cudaFree(d_B);
            cudaFree(d_C);
            delete[] h_A;
            delete[] h_B;
            delete[] h_C;
            delete[] h_result;

            return 0;
        }

    """)