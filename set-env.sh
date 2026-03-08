#!/bin/bash

# Load environment variables from .env file
# Equivalent to set-env.cmd for Bash/Linux environments

while IFS='=' read -r line; do
  # Skip comments and blank lines
  if [[ $line =~ ^\s*# ]] || [[ -z $line ]]; then
    continue
  fi

  # Remove 'export ' prefix if present
  line=$(echo "$line" | sed 's/^\s*export\s*//')

  # Parse key and value
  if [[ $line =~ ^\s*([^=]+?)\s*=\s*(.*)$ ]]; then
    key="${BASH_REMATCH[1]}"
    value="${BASH_REMATCH[2]}"

    # Strip surrounding double quotes
    if [[ $value =~ ^\"(.*)\"$ ]]; then
      value="${BASH_REMATCH[1]}"
    # Strip surrounding single quotes
    elif [[ $value =~ ^\'(.*)\'$ ]]; then
      value="${BASH_REMATCH[1]}"
    fi

    # Export the variable
    export "$key=$value"
  fi
done < .env