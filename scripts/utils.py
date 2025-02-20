import subprocess
import sys
import datetime

def is_git_clean():
    """Checks to see if the current branch has bene committed. If not, the 
    code will exit without running.
    """
    # Check for uncommitted changes (staged & unstaged)
    dirty = subprocess.call(['git', 'diff', '--quiet'])  # Returns 1 if dirty

    # Check for untracked files
    untracked = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard']).strip()

    # Check if we're on a valid branch
    branch_status = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip().decode()

    if dirty != 0 or untracked or branch_status == "HEAD":
        print('Repository dirty or on a detached HEAD state. Please commit and/or track your changes first.')
        sys.exit(1)

def retrieve_git_hash():
    """Gets the current git-hash value"""
    hash_cmd = ('git', 'rev-parse', 'HEAD')
    revision = subprocess.check_output(hash_cmd)
    return revision

def save_metadata(seed, git_hash, save_path):
    """Saves the relevant metadata associated with a results.
    
    args:
        seed (int) : the random seed used during the run.
        git_hash (str) : the git hash of the current commit.
        save_path (str) : the location in which to save the metadata.
    """
    # add metadata for results
    results_metadata = {"seed":seed,
                        "timestamp":str(datetime.datetime.now()),
                        "git_hash":git_hash,
                        "system":sys.version}
    
    with open(save_path, 'w') as f:
        f.write(str(results_metadata))