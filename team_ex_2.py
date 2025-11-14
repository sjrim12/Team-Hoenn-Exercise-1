import time
import os
import wikipedia
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from pathlib import Path

# Configuration
DEFAULT_SEARCH_TERM = "generative artificial intelligence"
MIN_SEARCH_LENGTH = 4
OUTPUT_DIR = "wiki_dl"


def convert_to_str(obj):

    if isinstance(obj, list):
        return '\n'.join(str(item) for item in obj)
    elif isinstance(obj, (str, int, float)):
        return str(obj)
    else:
        return str(obj)


def setup_output_directory():

    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(exist_ok=True)
    print(f"Output directory: {output_path.absolute()}")
    return output_path


def get_search_term():

    user_input = input("Enter a Wikipedia search term (or press Enter for default): ").strip()
    
    if len(user_input) < MIN_SEARCH_LENGTH:
        print(f"Search term too short. Using default: '{DEFAULT_SEARCH_TERM}'")
        return DEFAULT_SEARCH_TERM
    
    return user_input


def dl_and_save(item, output_dir):

    try:
        page = wikipedia.page(item, auto_suggest=False)
        title = page.title
        references = convert_to_str(page.references)
        
        # Sanitize filename to remove invalid characters
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        out_filename = os.path.join(output_dir, f"{safe_title}.txt")
        
        with open(out_filename, 'w', encoding='utf-8') as fileobj:
            fileobj.write(references)
        
        print(f"✓ Saved: {safe_title}.txt")
        return (True, title, None)
    
    except wikipedia.exceptions.DisambiguationError as e:
        error_msg = f"Disambiguation error for '{item}': {e.options[:3]}"
        print(f"✗ {error_msg}")
        return (False, item, error_msg)
    
    except wikipedia.exceptions.PageError:
        error_msg = f"Page not found: '{item}'"
        print(f"✗ {error_msg}")
        return (False, item, error_msg)
    
    except Exception as e:
        error_msg = f"Error processing '{item}': {str(e)}"
        print(f"✗ {error_msg}")
        return (False, item, error_msg)


def wiki_sequentially(search_term, output_dir):

    t_start = time.perf_counter()
    
    try:
        results = wikipedia.search(search_term)
        print(f"Found {len(results)} results for '{search_term}'")
        
        successful = 0
        failed = 0
        
        for item in results:
            success, _, _ = dl_and_save(item, output_dir)
            if success:
                successful += 1
            else:
                failed += 1
        
        t_end = time.perf_counter()
        t_lapse = t_end - t_start
        
        stats = {
            'method': 'Sequential',
            'time': t_lapse,
            'successful': successful,
            'failed': failed,
            'total': len(results)
        }
        
        print(f"\nCompleted in {t_lapse:.2f} seconds")
        print(f"Success: {successful}/{len(results)}, Failed: {failed}")
        
        return stats
    
    except Exception as e:
        print(f"Error in sequential execution: {str(e)}")
        return {'method': 'Sequential', 'error': str(e)}


def concurrent_threads(search_term, output_dir, max_workers=None):

    t_start = time.perf_counter()
    
    try:
        results = wikipedia.search(search_term)
        print(f"Found {len(results)} results for '{search_term}'")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(dl_and_save, item, output_dir) for item in results]
            outcomes = [future.result() for future in futures]
        
        successful = sum(1 for success, _, _ in outcomes if success)
        failed = len(outcomes) - successful
        
        t_end = time.perf_counter()
        t_lapse = t_end - t_start
        
        stats = {
            'method': 'Thread Pool',
            'time': t_lapse,
            'successful': successful,
            'failed': failed,
            'total': len(results)
        }
        
        print(f"\nCompleted in {t_lapse:.2f} seconds")
        print(f"Success: {successful}/{len(results)}, Failed: {failed}")
        
        return stats
    
    except Exception as e:
        print(f"Error in thread pool execution: {str(e)}")
        return {'method': 'Thread Pool', 'error': str(e)}


# Helper function for process pool (must be at module level for pickling)
def dl_and_save_process(args):

    item, output_dir = args
    return dl_and_save(item, output_dir)


def concurrent_process(search_term, output_dir, max_workers=None):

    t_start = time.perf_counter()
    
    try:
        results = wikipedia.search(search_term)
        print(f"Found {len(results)} results for '{search_term}'")
        
        # Prepare arguments for process pool
        args_list = [(item, output_dir) for item in results]
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            outcomes = list(executor.map(dl_and_save_process, args_list))
        
        successful = sum(1 for success, _, _ in outcomes if success)
        failed = len(outcomes) - successful
        
        t_end = time.perf_counter()
        t_lapse = t_end - t_start
        
        stats = {
            'method': 'Process Pool',
            'time': t_lapse,
            'successful': successful,
            'failed': failed,
            'total': len(results)
        }
        
        print(f"\nCompleted in {t_lapse:.2f} seconds")
        print(f"Success: {successful}/{len(results)}, Failed: {failed}")
        
        return stats
    
    except Exception as e:
        print(f"Error in process pool execution: {str(e)}")
        return {'method': 'Process Pool', 'error': str(e)}


def print_performance_summary(stats_list):

    print("\n" + "="*60)
    print("PERFORMANCE SUMMARY")
    print("="*60)
    
    for stats in stats_list:
        if 'error' not in stats:
            print(f"\n{stats['method']}:")
            print(f"  Time: {stats['time']:.2f} seconds")
            print(f"  Success Rate: {stats['successful']}/{stats['total']} "
                  f"({stats['successful']/stats['total']*100:.1f}%)")


def main():

    # Setup
    output_dir = setup_output_directory()
    search_term = get_search_term()
    
    print(f"\nSearching for: '{search_term}'")
    print(f"Output directory: {output_dir}")
    
    # Run all three implementations
    all_stats = []
    
    stats_seq = wiki_sequentially(search_term, str(output_dir))
    all_stats.append(stats_seq)
    
    stats_thread = concurrent_threads(search_term, str(output_dir))
    all_stats.append(stats_thread)
    
    stats_process = concurrent_process(search_term, str(output_dir))
    all_stats.append(stats_process)
    
    # Print summary
    print_performance_summary(all_stats)
    
    print("\n" + "="*60)
    print("All downloads complete!")
    print("="*60)


if __name__ == "__main__":
    main()
