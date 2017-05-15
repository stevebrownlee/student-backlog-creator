
### GitHub Issues Import ###

This Python script allows you to import issues and pull requests from one repository to another; works even for private repositories, and if the two repositories are not related to each other in any way.

#### Usage ####

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

