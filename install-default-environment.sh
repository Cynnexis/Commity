#!/bin/bash

# Update APT packages list
apt-get update -qq
apt-get upgrade -qq
apt-get install -qy git
apt-get install -qy vim

cp default-gitconfig.ini ~/.gitconfig
touch ~/.bashrc

# Install python packages
pip install --no-cache-dir -r requirements.txt

# Add default git repo for testing
#                       |  * commit 9 (lorem)
#                       |  |     ✨ Add more lorem!
#                       |  |
#                       |  * commit 8 (lorem)
#                       |  |     ✨ Add lorem
#                       | /
#                       |/
#                       |
#                       * commit 7 (master)
#                       |     📝 Update README
# commit 6 (license) *  |
#   Add LICENSE      |  |
#                     \ |
#                      \|
#                       * commit 5 (HEAD -> master)
#                       |\    Merge getting-started -> master
#                       | \
#                       |  |
#                       |  * commit 4 (getting-started)
#                       |  |     📝 Add more content in Getting Started
#                       |  |
#                       |  * commit 3 (getting-started)
#                       |  |     📝 Add Getting Started section
#                       | /
#                       |/
#                       |
#                       * commit 2 (master) (tag: v1.0)
#                       |     📝 Add description
#                       |
#                       * commit 1 (master)
#                             🎉 First commit

cd ~
mkdir git-test-repo
cd git-test-repo
TEST_REPO=$(pwd)
DEBUG="True"
echo -e "TEST_REPO=$TEST_REPO\nDEBUG=$DEBUG" >> /etc/environment
echo -e "export TEST_REPO=$TEST_REPO\nexport DEBUG=$DEBUG" >> ~/.bashrc
source ~/.bashrc

# Add README in repo
echo "# git-test-repo" > README.md
git init
# Commit
git add .
git commit -m ":tada: First commit"

# Add description
echo -e "\nThis is a description" >> README.md
# Commit and tag
git add .
git commit -m ":pencil: Add description"
git tag -a v1.0 -m "My version where my README has a description"

# Create new branch "getting-started" and write a getting started section in RADME
git checkout -b getting-started
echo -e "\n## Getting Started\n\nThis project is empty." >> README.md
# Commit
git add .
git commit -m ":pencil: Add Getting Started section"
# Add new content
echo -e "Feel free to add new content!" >> README.md
# Commit
git add .
git commit -m ":pencil: Add more content in Getting Started"
# Merge (conserve branch)
git checkout master
git merge getting-started

# Create new branch
git checkout -b license
echo "LICENSE" > LICENSE.txt
# Commit
git add .
git commit -m ":page_facing_up: Add LICENSE"
# Go back to master and commit
git checkout master
echo "Be nice to the community!" >> README.md
# Commit
git add .
git commit -m ":pencil: Update README"
# Create another new branch
git checkout -b lorem
echo "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua." > lorem.txt
# Commit
git add .
git commit -m ":sparkles: Add lorem"
# Add more lipsum
echo "Pretium lectus quam id leo in vitae turpis massa." >> lorem.txt
# Commit
git add .
git commit -m ":sparkles: Add more lorem!"
# Go back to master
git checkout master
