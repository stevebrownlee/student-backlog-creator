# GitHub Issues Import

This Python script allows you to import issues and pull requests from one repository to another; works even for private repositories, and if the two repositories are not related to each other in any way.

## Setup

### 2FA Setup

> Note: You should have 2FA on your account

If you have 2FA enabled on your Github account, you will need to create a personal access token and put that in place of your account password.

1. Copy `config.ini.sample` to `config.ini`.
1. Open the new file
1. Go to your Github account
1. Open settings
1. Click on Developer Settings
1. Click on Personal Access Tokens
1. Click on Generate New Token
1. Call the new token _Backlog generator_
1. Scroll down and click the Generate Token button
1. Copy the token that gets created
1. Paste it into the `password` key in the `config.ini` file.

```html
[login]
username = you
password = xxxxxxxxxxx your token here xxxxxxxxx
```

### Non 2FA Accounts

Just type in your account password in the `ini` file.

## Usage

### Importing Open Issues to Student Repo

Whether you are importing all open issues into a individual student repository, or to a team's organization repo, use the following command.

```html
python gh-issues-import.py \
    --source nashville-software-school/repo \
    --target target-organization/repo \
    --open
```

### More Details

For a list of all possible configuration options in `config.ini`, see [_Configuration_](http://www.iqandreas.com/github-issues-import/configuration/).

To quickly get started, rename `config.ini.sample` to `config.ini`, and edit the fields to match your login info and repository info. If you have 2FA enabled on your Github account, you will need to create a personal access token and put that in place of your account password.

Some config options can be passed as arguments. For a full list, see [the the _Arguments_ page](http://www.iqandreas.com/github-issues-import/arguments/), or run the script using the `--help` flag.

