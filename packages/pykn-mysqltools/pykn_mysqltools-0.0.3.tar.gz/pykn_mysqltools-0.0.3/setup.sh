#!/bin/bash
# Creates a virtual environment venv if it doesn't exist, and installs requirements from requirements.txt.
# If requirements.txt doesn't exist, this script does nothing.

#set -o errexit # Fail fast on errors

required_packages=("python3")
exit_code=0

# Check if this script is in the project directory
if [[ ! $PWD == *"/pykn-mysql-tools" ]]; then
    echo "This script should be run in the root directory of the project."
    echo "Current directory: ${PWD}"
    exit 1
fi

# Check if required system packages are installed
missing_packages=0
for package in ${required_packages[@]}; do
    echo "Checking for ${package}..."
    package_ok=$(dpkg-query -W --showformat='${Status}\n' $package|grep "install ok installed") 
    if [[ "" = "$package_ok" ]]; then
        echo "${package} not installed. Run 'sudo apt update', and then 'sudo apt install ${package}'."
        missing_packages=$((missing_packages+1))
        exit_code=1
    else
        echo "${package} is installed."
    fi
done
echo "Total missing packages: ${missing_packages}"

# Check for requirements.txt, virtual environment
if [[ -e ./requirements.txt ]]; then
    if [[ ! -e ./venv/ ]]; then
        echo "Creating virtual environment..."
        python3 -m venv ./venv
    fi
    echo "Activating virtual environment..."
    source ./venv/bin/activate
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
    echo "Deactivating virtual environment..."
    deactivate
else
    echo "requirements.txt not found, did you move it?"
    exit_code=1
fi

# Check Python version >= 3.10. Needed for switch statements.
echo "Checking for Python 3.10+..."
echo "Activating virtual environment..."
source ./venv/bin/activate
if ! python -c 'import sys; assert sys.version_info >= (3,10)' > /dev/null; then
    echo "Python version not >= 3.10. 3.10 is required. Update Python to at least 3.10 and re-run. Exiting..."
    exit_code=1
    exit $exit_code
fi
echo "Deactivating virtual environment..."
deactivate

# Check for .env
if [[ ! -e ./.env ]]; then
    echo ".env not found, did you move it?"
    exit_code=1
fi

exit $exit_code
