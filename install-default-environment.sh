#!/bin/bash

WORKSPACE_DIR=$(pwd)

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
#                       |
#                       * commit 14 (HEAD -> master)
#                       |\    🔀 Merge branch 'acknowledgements' onto master
#                       | \
#    commit 13 (master) *  |
#        Add .gitignore |  |
#                       |  |
#                       |  * commit 12 (acknowledgements)
#                       |  |     ✨ Add Acknowledgements.txt
#                       | /
#                       |/
#                       |    * commit 11 (change-first-lorem-paragraph)
#                       |    |     📝 Update first paragraph of lorem text
#                       |    |
#                       |  * | commit 10 (lorem)
#                       |  | |     ✨ Add lorem again
#                       |  | /
#                       |  |/
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
#                       |\    🔀 Merge branch 'getting-started' onto master
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

cd /
mkdir git-test-repo
cd git-test-repo
TEST_REPO=$(pwd)
DEBUG="True"
echo -e "TEST_REPO=$TEST_REPO\nDEBUG=$DEBUG" >> /etc/environment
echo -e "export TEST_REPO=$TEST_REPO\nexport DEBUG=$DEBUG" >> /.bashrc
source /.bashrc

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
git merge getting-started --no-ff -m ":twisted_rightwards_arrows: Merge branch 'getting-started' onto master"

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
# Add more lorem
echo "Pretium lectus quam id leo in vitae turpis massa." >> lorem.txt
# Commit
git add .
git commit -m ":sparkles: Add more lorem!"

# Create new branch on lorem
git checkout -b change-first-lorem-paragraph

# Come back to lorem and commit new lorem
git checkout lorem
echo "Ac tincidunt vitae semper quis lectus nulla at." >> lorem.txt
# Commit
git add .
git commit -m ":sparkles: Add lorem again!"

# Go to branch created before and commit
git checkout change-first-lorem-paragraph
new_content="Lorem ipsum dolor sit amet."
sed -i "1s/.*/$new_content/" lorem.txt
# Commit
git add .
git commit -m ":pencil: Update first paragraph of lorem text"

# Checkout on master
git checkout master

# Create new banch "acknowledgements"
git checkout -b acknowledgements
# Add Acknowledgements.txt
echo -e "Acknowledgements\n" > Acknowledgements.txt
# Commit
git add .
git commit -m ":sparkles: Add Acknowledgements.txt"

# Checkout on master
git checkout master
# Create .gitignore
echo "*~" > .gitignore
# Commit
git add .
git commit -m ":see_no_evil: Add .gitignore"

# Merge "acknowledgements" (conserve branch)
git merge acknowledgements --no-ff -m ":twisted_rightwards_arrows: Merge branch 'acknowledgements' onto master"

# Go back to workspace
cd $WORKSPACE_DIR

# Copy bashrc to current user (root)
cp -f /.bashrc ~/.bashrc
