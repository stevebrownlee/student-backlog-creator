#!/bin/bash

# Function to read user input using gum
read_input() {
    gum input --placeholder "$1" | tr -d '\n'
}

# Function to display issue titles using gum
display_issues() {
    gum clear
    echo "Source Repository Issues:"
    for ((i=0; i<${#issues[@]}; i++)); do
        gum draw text "${issues[$i]}" --x 1 --y $((i+2))
    done
}

# Function to move issue titles up or down
move_issue() {
    local direction=$1
    local index=$2

    if [ "$direction" == "up" ]; then
        if [ $index -gt 0 ]; then
            tmp=${issues[$index]}
            issues[$index]=${issues[$((index-1))]}
            issues[$((index-1))]=$tmp
        fi
    elif [ "$direction" == "down" ]; then
        if [ $index -lt $(( ${#issues[@]} - 1 )) ]; then
            tmp=${issues[$index]}
            issues[$index]=${issues[$((index+1))]}
            issues[$((index+1))]=$tmp
        fi
    fi
}

# Function to display spinner while processing
display_spinner() {
    gum spin --spinner dot --title "$1" -- "$2"
}

# Function to confirm user choice using gum
confirm_choice() {
    gum confirm --message "$1"
}

# Function to transfer issues
transfer_issues() {
    for ((i=0; i<${#issues[@]}; i++)); do
        display_spinner "Transferring issue: ${issues[$i]}" "curl -X POST -H 'Authorization: $authorization' -H 'Accept: application/vnd.github.inertia-preview+json' -d '{\"issues\": [\"${issues[$i]}\"]}' '$target_url/issues'"
        sleep 10
    done
}

# Main script

# Read source and target repository URLs
source_url=$(read_input "Source Repository URL")
target_url=$(read_input "Target Repository URL")

# Read GitHub username and PAT from .env file
source .env
token="$GITHUB_USERNAME:$GITHUB_PAT"

# Construct token in the correct format
authorization="Basic $(echo -n "$token" | base64)"

# Fetch issues from source repository
display_spinner "Fetching issues..." "curl -s -H 'Authorization: $authorization' -H 'Accept: application/vnd.github.inertia-preview+json' '$source_url/issues'"
issues=($(curl -s -H "Authorization: $authorization" -H "Accept: application/vnd.github.inertia-preview+json" "$source_url/issues" | jq -r '.[].title'))

# Display fetched issues
display_issues

# Allow user to reorder issues
while true; do
    gum draw text "Use arrow keys to move issues up/down. Press Enter when done." --x 1 --y $(( ${#issues[@]} + 2 ))
    read -rsn1 input
    case $input in
        $'\x1b[A') # Up arrow key
            move_issue "up" $((gum y))
            display_issues
            ;;
        $'\x1b[B') # Down arrow key
            move_issue "down" $((gum y))
            display_issues
            ;;
        $'\x0a') # Enter key
            break
            ;;
    esac
done

# Confirm user choice
confirm_choice "Do you want to transfer these issues to the target repository? (Yes/No)"
if [ $? -eq 0 ]; then
    # Transfer issues to target repository
    transfer_issues
    echo "Issues transferred successfully!"
else
    echo "Operation aborted."
fi
