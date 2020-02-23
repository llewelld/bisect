#include <iostream>
#include <random>
#include <sstream>
#include <vector>
#include <chrono>

// returns lowest line above a particular commit
unsigned int line_above_commit(int commit, std::vector<unsigned int> lines_per_commit) {
    unsigned int accumulator = 0;
    for (unsigned int j = 0; j <= commit && j < lines_per_commit.size(); j++) {
        accumulator += lines_per_commit[j];
    }
    return accumulator;
}

// returns highest line below a particular commit 
unsigned int line_below_commit(int commit, std::vector<unsigned int> lines_per_commit) {
    return line_above_commit(commit, lines_per_commit) - lines_per_commit[commit];
}

// returns commit containing a given line
unsigned int commit_from_line(unsigned int line, std::vector<unsigned int> lines_per_commit) {
    unsigned int commit = 0;
    long accumulator = 0;
    for (int j = 0; j < lines_per_commit.size(); j++) {
        accumulator += lines_per_commit[j];

        if (accumulator >= line) {
            commit = j;
            break;
        }
    }
    return commit;		
}

int
main(
    int argc,
    char *argv[])
{
    if (argc != 4) {
        std::cerr << "please specify 3 arguments (max number of commits (>= 3) & max number of lines per commit (>= 1) & number of runs per number of commits >= 1)" << std::endl;
        return -1;
    }

    std::random_device r;
    //std::default_random_engine generator{};
    std::default_random_engine generator{r()};

    std::stringstream max_number_of_commits_s(argv[1]);
    unsigned int max_number_of_commits;
    max_number_of_commits_s >> max_number_of_commits;

    std::stringstream max_number_of_lines_per_commit_s(argv[2]);
    unsigned int max_number_of_lines_per_commit;
    max_number_of_lines_per_commit_s >> max_number_of_lines_per_commit;

    std::stringstream number_of_runs_s(argv[3]);
    unsigned int number_of_runs;
    number_of_runs_s >> number_of_runs;

    long int amount_of_times_regular_was_better = 0, amount_of_times_modified_was_better = 0;
    for (int c = 3; c < max_number_of_commits; c++) {
        //std::cout << "MNOC: " << c << std::endl;

        std::uniform_int_distribution<unsigned int> distribution_commits(3, c /* current max number of commits */);

        for (int run = 0; run < number_of_runs; run++) {
            //std::cout << "RUN: " << run << std::endl;

            int current_amount_of_commits = distribution_commits(generator);

            std::uniform_int_distribution<unsigned int> distribution_lines_per_commit(1, max_number_of_lines_per_commit);
 
            std::vector<unsigned int> lines_per_commit;
 
            for (unsigned int i = 0; i < current_amount_of_commits; i++) {
                lines_per_commit.push_back(distribution_lines_per_commit(generator));
            }
 
            long long int number_of_lines = 0;
            for (auto &n : lines_per_commit) {
                number_of_lines += n;
            }

#if 0
            std::uniform_int_distribution<unsigned int> distribution_bad_commit(0, current_amount_of_commits - 1);
            unsigned int bad_commit = distribution_bad_commit(generator);
#else
            std::uniform_int_distribution<unsigned int> distribution_bad_line(0, number_of_lines - 1);
            unsigned int bad_line = distribution_bad_line(generator);
            unsigned int bad_commit = commit_from_line(bad_line, lines_per_commit);
#endif

            // regular bisect:
            int current_commit = current_amount_of_commits / 2;
            int steps_regular = 0;
            unsigned int min_commit_checked = 0;
            unsigned int max_commit_checked = current_amount_of_commits;
            while (current_commit != bad_commit) {
                if (current_commit < bad_commit) {
                    min_commit_checked = current_commit;
	                  current_commit = min_commit_checked + (max_commit_checked - min_commit_checked + 1) / 2;
                } else {
                    max_commit_checked = current_commit;
	                  current_commit = max_commit_checked - (max_commit_checked - min_commit_checked + 1) / 2;
                }
                steps_regular++;
            }
            int current_line = number_of_lines / 2;

            // find commit for line
            current_commit = commit_from_line(current_line, lines_per_commit);
            int steps_modified = 0;
            unsigned int min_line_checked = 0;
            unsigned int max_line_checked = number_of_lines;
            while (current_commit != bad_commit) {
                if (current_commit < bad_commit) {
                    min_line_checked = line_above_commit(current_commit, lines_per_commit) + 1;
	                  current_line = min_line_checked + (max_line_checked - min_line_checked) / 2;
                } else {
                    max_line_checked = line_below_commit(current_commit, lines_per_commit);
	                  current_line = max_line_checked - (max_line_checked - min_line_checked) / 2;
                }
                steps_modified++;

                // find commit for line
                current_commit = commit_from_line(current_line, lines_per_commit);
            }

            std::cout << "MNOC: " << max_number_of_commits << " SR: " << steps_regular << " SM: " << steps_modified << std::endl;
            if (steps_regular > steps_modified) {
                amount_of_times_modified_was_better++;
            } else if (steps_regular < steps_modified) {
                amount_of_times_regular_was_better++;
            }
        }
    }

    std::cout << "RUNS: " << (max_number_of_commits - 2) * number_of_runs << " REGULAR SCORE: " << amount_of_times_regular_was_better << " MODIFIED SCORE: " << amount_of_times_modified_was_better << std::endl;

    return 0;
}


