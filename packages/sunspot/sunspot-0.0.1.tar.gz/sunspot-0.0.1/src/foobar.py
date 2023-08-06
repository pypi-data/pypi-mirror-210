import concurrent.futures

# [rest of code]

def thread_function( n ):
    print( n )

if __name__ == "__main__":

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(thread_function, range(3))
