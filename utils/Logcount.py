import logging
import os


def log_run(log_path='log/', code_name='test'):
    # Configure the logger
    log_path = log_path + code_name
    log_name = code_name + '.log'
    os.makedirs(log_path, exist_ok=True)
    logging.basicConfig(
        filename=os.path.join(log_path, log_name),
        level=logging.INFO,
        format="Run Count: %(message)s - %(asctime)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    """Logs the total number of code executions, timestamp, and returns the total run count."""
    # Check if a file to keep track of the run count exists
    count_file = os.path.join(log_path, "run_count.txt")

    # Initialize run count
    if os.path.exists(count_file):
        with open(count_file, "r") as file:
            run_count = int(file.read().strip()) + 1
    else:
        run_count = 1

    # Update the run count in the file
    with open(count_file, "w") as file:
        file.write(str(run_count))

    # Log the run count
    logging.info(run_count)
    print(run_count)
    # Return the run count
    return run_count

# # Example function call
# total_runs = log_run()
# print(total_runs)
