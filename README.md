# GitHub Issues Import

This Python script allows you to import issues and pull requests from one repository to another; works even for private repositories, and if the two repositories are not related to each other in any way.

## Usage

### Importing Open Issues to Student Repo

Whether you are importing all open issues into a individual student repository, or to a team's organization repo, use the following command. This is most useful

```sh
python gh-issues-import.py --source nashville-software-school/repo --target student-account/repo --open
```

### Importing Blocks of Issues

I created a bash script to help with the automation of importing blocks of tickets to student personal websites. Since we aren't going to give them all of the tickets at once, but rather in blocks when we cover a specific technology, it would require too man copy pastas.

1. Have students send you their Github handles.
1. Copy them all into a file (e.g. `cohort22`) and delimit them with semi-colons. [Example](./cohort22)
1. Run the `backlog.sh` script and the filename holding the handles as the single argument.
    ```sh
    ./backlog cohort22
    ```
1. It will prompt you for the block of tickets you want to import. Enter them in delimited by a space (e.g. `14 15 16 17`)
1. The importing process will start.

```sh
╭─ ~/dev/github/stevebrownlee/github-backlog-creator  ‹master*› 
╰─$ ./backlog.sh cohort22
Issues > 12 13 14

python gh-issues-import.py --source stevebrownlee/personal-site --target tgbowman/tgbowman.github.io --issues 12 13 14
Loaded options from default config file in '/Users/stevebrownlee/dev/github/stevebrownlee/github-backlog-creator/config.ini'

You are about to add to 'tgbowman/tgbowman.github.io':
 * 3 new issues
Successfully created issue 'Populate your resume page with data in the database'
Successfully created issue 'Populate your projects page from data in the database'
Successfully created issue 'Populate your contact page from data in the database'
python gh-issues-import.py --source stevebrownlee/personal-site --target rmbw74/rmbw74.github.io --issues 12 13 14
Loaded options from default config file in '/Users/stevebrownlee/dev/github/stevebrownlee/github-backlog-creator/config.ini'

You are about to add to 'rmbw74/rmbw74.github.io':
 * 3 new issues
Successfully created issue 'Populate your resume page with data in the database'
Successfully created issue 'Populate your projects page from data in the database'
Successfully created issue 'Populate your contact page from data in the database'
python gh-issues-import.py --source stevebrownlee/personal-site --target kghaggerty/kghaggerty.github.io --issues 12 13 14
Loaded options from default config file in '/Users/stevebrownlee/dev/github/stevebrownlee/github-backlog-creator/config.ini'

etc...
```

### More Details

The script will by default look for a file named `config.ini` located in the same folder as the Python script. For a list of all possible configuration options, see [_Configuration_](http://www.iqandreas.com/github-issues-import/configuration/).

To quickly get started, rename `config.ini.sample` to `config.ini`, and edit the fields to match your login info and repository info. If you have 2FA enabled on your Github account, you will need to create a personal access token and put that in place of your account password.

Run the script with the following command to import all open issues into the repository defined in the config:

```
 $ python3 gh-issues-import.py --open
```

If you want to import all issues (including the closed ones), use `--all` instead of `--open`. Closed issues will still be open in the target repository, but titles will begin with `[CLOSED]`.

Or to only import specific issues, run the script and include the issue numbers of all issues you wish to import (can be done for one or several issues, and will even include closed issues):

```
 $ python3 gh-issues-import.py --issues 25 26 29
```

Some config options can be passed as arguments. For a full list, see [the the _Arguments_ page](http://www.iqandreas.com/github-issues-import/arguments/), or run the script using the `--help` flag.

