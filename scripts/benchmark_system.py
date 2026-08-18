import sys
from test_full_system import run_tests

if __name__ == "__main__":
    print("Benchmarking BATMAN System...")
    # For now, benchmark just runs the full system test and records time.
    import time
    start = time.time()
    run_tests()
    print(f"System benchmark completed in {time.time() - start:.2f} seconds.")
