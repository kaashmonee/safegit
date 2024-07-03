# safegit

## Installation
```
git clone git@github.com:kaashmonee/safegit.git


```

Add the following function to your `~/.bashrc` or `~/.zshrc`.
```
function gcap() {
    /Users/<myusername>/<installationdir>/safegit/safegit.py "$1"
    if [ $? -eq 0 ]; then
            git push
    fi
}
```

## Usage:

Clone, make executable, and move to whichever location
```
git add .
gcap "my commit message"
```

If CODEOWNERS exists and all the staged files match the pattern in the CODEOWNERS file:
```
[main fdf6a1f] test commit
 2 files changed, 7 insertions(+), 5 deletions(-)
```

If a CODEOWNERS file doesn't exist or you try to stage and commit a file that doesn't exist
in the CODEOWNERS listing:
```
The following staged files are not in CODEOWNERS:
randomfile.txt
```


