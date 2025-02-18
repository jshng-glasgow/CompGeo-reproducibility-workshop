import subprocess
import sys

def is_git_clean():
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
    hash_cmd = ('git', 'rev-parse', 'HEAD')
    revision = subprocess.check_output(hash_cmd)
    return revision