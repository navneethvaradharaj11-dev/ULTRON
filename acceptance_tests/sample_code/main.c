#include <stdio.h>

void print_greeting(const char* name) {
    printf("ULTRON Operating System Engine: Hello %s!\n", name);
}

int calculate_burst_time(int task_count) {
    return task_count * 5;
}

int main() {
    print_greeting("ULTRON User");
    int total_time = calculate_burst_time(4);
    printf("Total Execution Time: %d ms\n", total_time);
    return 0;
}
