#!/bin/bash

WORKSPACE_DIR=$(pwd)

# Detect if we're in a Docker container, or not
[[ $(grep -Ec "/docker" < /proc/1/cgroup) -gt 0 ]]
IN_DOCKER=$?

# Update APT packages list if in Docker
if [[ $IN_DOCKER = 0 ]]; then
	echo "Docker container detected."
	apt-get update -y
	apt-get upgrade -y
	apt-get install -y git
	apt-get install -y vim

	cp default-gitconfig.ini ~/.gitconfig
	touch ~/.bashrc

	# Install python packages
	pip install --no-cache-dir -r requirements.txt

	cd /
fi

mkdir git-test-repo
cd git-test-repo
if [[ $IN_DOCKER = 0 ]]; then
	TEST_REPO=$(pwd)
	DEBUG="True"
	echo -e "TEST_REPO=$TEST_REPO\nDEBUG=$DEBUG" >> /etc/environment
	echo -e "export TEST_REPO=$TEST_REPO\nexport DEBUG=$DEBUG" >> /.bashrc
	source /.bashrc
fi

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
#                       |     * commit 11 (change-first-lorem-paragraph)
#                       |     |     📝 Update first paragraph of lorem text
#                       |     |
#                       |  *  | commit 10 (lorem)
#                       |  |  |     ✨ Add lorem again
#                       |  |  |         * Fixed #5
#                       |  | /
#                       |  |/
#                       |  * commit 9 (lorem)
#                       |  |     ✨ Add more lorem!
#                       |  |         * Fixed #4 and #2.
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
#   * Fixed #2.      |  |
#                     \ |
#                      \|
#                       * commit 5 (HEAD -> master) (no fast-forward)
#                       |\    🔀 Merge branch 'getting-started' onto master
#                       | \
#                       |  |
#                       |  * commit 4 (getting-started)
#                       |  |     📝 Add more content in Getting Started
#                       |  |         * Improved #1.
#                       |  |
#                       |  * commit 3 (getting-started)
#                       |  |     📝 Add Getting Started section
#                       | /
#                       |/
#                       |
#                       * commit 2 (master) (tag: v1.0)
#                       |     📝 Add description
#                       |         * Started #1.
#                       |
#                       * commit 1 (master)
#                             🎉 First commit

# Add README in repo
echo "# git-test-repo" > README.md
git init
# Commit
git add .
git commit -m ":tada: First commit" # commit 1 (master)

# Add description
echo -e "\nThis is a description" >> README.md
# Commit and tag
git add .
git commit -m "$(echo -e ':pencil: Add description\n\n* Started #1.')" # commit 2 (master) (tag: v1.0)
git tag -a v1.0 -m "My version where my README has a description"

# Create new branch "getting-started" and write a getting started section in RADME
git checkout -b getting-started
echo -e "\n## Getting Started\n\nThis project is empty." >> README.md
# Commit
git add .
git commit -m ":pencil: Add Getting Started section" # commit 3 (getting-started)
# Add new content
echo -e "Feel free to add new content!" >> README.md
# Commit
git add .
git commit -m "$(echo -e ':pencil: Add more content in Getting Started\n\n* Improved #1.')" # commit 4 (getting-started)
# Merge (conserve branch)
git checkout master
git merge getting-started --no-ff -m ":twisted_rightwards_arrows: Merge branch 'getting-started' onto master" # commit 5 (HEAD -> master) (no fast-forward)

# Create new branch
git checkout -b license
echo "LICENSE" > LICENSE.txt
# Commit
git add .
git commit -m "$(echo -e ':page_facing_up: Add LICENSE\n\n* Fixed #2.')" # commit 6 (license)
# Go back to master and commit
git checkout master
echo "Be nice to the community!" >> README.md
# Commit
git add .
git commit -m ":pencil: Update README" # commit 7 (master)
# Create another new branch
git checkout -b lorem
echo "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua." > lorem.txt
# Commit
git add .
git commit -m ":sparkles: Add lorem" # commit 8 (lorem)
# Add more lorem
echo "Pretium lectus quam id leo in vitae turpis massa." >> lorem.txt
# Commit
git add .
git commit -m "$(echo -e ':sparkles: Add more lorem!\n\n* Fixed #4 and #2.')" # commit 9 (lorem)

# Create new branch on lorem
git checkout -b change-first-lorem-paragraph

# Come back to lorem and commit new lorem
git checkout lorem
echo "Ac tincidunt vitae semper quis lectus nulla at." >> lorem.txt
# Commit
git add .
git commit -m "$(echo -e ':sparkles: Add lorem again!\n\n* Fixed #5')" # commit 10 (lorem)

# Go to branch created before and commit
git checkout change-first-lorem-paragraph
new_content="Lorem ipsum dolor sit amet."
sed -i "1s/.*/$new_content/" lorem.txt
# Commit
git add .
git commit -m ":pencil: Update first paragraph of lorem text" # commit 11 (change-first-lorem-paragraph)

# Checkout on master
git checkout master

# Create new banch "acknowledgements"
git checkout -b acknowledgements
# Add Acknowledgements.txt
echo -e "Acknowledgements\n" > Acknowledgements.txt
# Commit
git add .
git commit -m ":sparkles: Add Acknowledgements.txt" # commit 12 (acknowledgements)

# Checkout on master
git checkout master
# Create .gitignore
echo "*~" > .gitignore
# Commit
git add .
git commit -m ":see_no_evil: Add .gitignore" # commit 13 (master)

# Merge "acknowledgements" (conserve branch)
git merge acknowledgements --no-ff -m ":twisted_rightwards_arrows: Merge branch 'acknowledgements' onto master" # commit 14 (HEAD -> master)

# Go back to workspace
cd $WORKSPACE_DIR

# Copy bashrc to current user (root)
if [[ $IN_DOCKER = 0 ]]; then
	cp -f /.bashrc ~/.bashrc
fi
