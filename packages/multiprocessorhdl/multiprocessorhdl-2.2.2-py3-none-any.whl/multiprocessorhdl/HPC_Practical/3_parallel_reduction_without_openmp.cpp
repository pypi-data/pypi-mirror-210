#include <iostream>
#include <vector>
#include <climits>
#include <random>
#include <thread>

using namespace std;

struct ReductionData {
    int min_value;
    int max_value;
    int sum;

    ReductionData() : min_value(INT_MAX), max_value(INT_MIN), sum(0) {}
};

void reduce(const vector<int>& arr, int start, int end, ReductionData& data) {
    for (int i = start; i < end; i++) {
        if (arr[i] < data.min_value) {
            data.min_value = arr[i];
        }
        if (arr[i] > data.max_value) {
            data.max_value = arr[i];
        }
        data.sum += arr[i];
    }
}

void parallelReduction(const vector<int>& arr, ReductionData& data, int num_threads) {
    int chunk_size = arr.size() / num_threads;
    vector<thread> threads;

    for (int i = 0; i < num_threads; i++) {
        int start = i * chunk_size;
        int end = (i == num_threads - 1) ? arr.size() : (i + 1) * chunk_size;
        threads.emplace_back(reduce, std::ref(arr), start, end, std::ref(data));
    }

    for (auto& thread : threads) {
        thread.join();
    }
}

int main() {
    const int size = 100;
    const int num_threads = 4;

    vector<int> vec(size);
    random_device rd;
    mt19937 gen(rd());
    uniform_int_distribution<int> dis(1, 1000);
    cout << "Size of Vector: " << vec.size() << endl;

    cout << "Vector values: ";
    for (int i = 0; i < size; ++i) {
        vec[i] = dis(gen);
        cout << vec[i] << " ";
    }
    cout << endl;

    ReductionData data;
    double start_time = clock();
    parallelReduction(vec, data, num_threads);
    double end_time = clock();

    cout << "Minimum value: " << data.min_value << endl;
    cout << "Maximum value: " << data.max_value << endl;
    cout << "Sum: " << data.sum << endl;
    cout << "Average: " << static_cast<double>(data.sum) / size << endl;
    cout << "Runtime: " << (end_time - start_time) / CLOCKS_PER_SEC << " seconds" << endl;

    return 0;
}
