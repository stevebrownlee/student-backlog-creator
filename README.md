# NSS Project Backlog Creator

This tool will allow instructors to specify one of our source repositories that has issues tickets, and then import them into a student repository, create a project board, and add all of the tickets to the backlog swimlane.

![animation showing the creation of the project, columns, and tickets](./backlog-creator.gif)

## Prerequisites

Install pipenv with `brew install pipenv`

## Instructions

### Environment

1. Clone this repo
1. Run `pipenv install` to get dependencies
1. Run `pipenv shell` to activate virtual environment

### Configuration

1. Copy `config.ini.sample` to `config.ini` and open the new file.
1. In the login section, enter in your account name and password (no 2FA) or personal access token (needed if you have 2FA). See section below about how to generate a personal access token.
    ```ini
    [login]
    username = your_account
    password = password_or_PAT
    ```
1. Specify the account and repo from which you are importing issues.
    ```ini
    [source]
    repository = nashville-software-school/nutshell
    ```
1. Specify the account and repo to which the issues will be imported.
    ```ini
    [target]
    repository = nss-cohort-37/callous-capybaras-nutshell
    ```
1. Specify the name of the project board you want to create on the student repository. If you want different swimlanes for tickets, just change the items in the `columns` list.
    ```ini
    [project]
    name = Nutshell
    columns = ["Backlog", "In Progress", "Ready to Test", "Complete"]
    ```

That's all you will need to change each time you run this tool.

> **Note:** The Github API media type section _should_ not change very often, but if you cannot get this tool to work, check the docs and make sure the media type is still valid.
>
> ```ini
> [github]
> media_type = application/vnd.github.inertia-preview+json
> ```

### Migration

```html
python migrate.py --open
```

## Deactivating Virtual Environment

When you are done migrating issues to all of your students' repositories, first enter in the command `deactivate` in your terminal to stop the venv. If you later try to activate the venv again and you see the message:

```html
Shell for UNKNOWN_VIRTUAL_ENVIRONMENT already activated.
No action taken to avoid nested environments.
```

Then type in the command `exit` and it should force quit the environment.

## 2FA Setup

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

### More Details

For a list of all possible configuration options in `config.ini`, see [_Configuration_](http://www.iqandreas.com/github-issues-import/configuration/).

Some config options can be passed as arguments. For a full list, see [the the _Arguments_ page](http://www.iqandreas.com/github-issues-import/arguments/), or run the script using the `--help` flag.

