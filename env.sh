####################### SSH KEY FOR GIT ###################################
eval `ssh-agent -s` && ssh-add -k
####################### To be added to git account settings ################


###################### GIT PARAMETERS #####################################
export GIT_PARENT_DIR=~
export GIT_REPO_NAME=BTech-Project
export GIT_BRANCH_NAME=master
export GIT_USER=Sana-Shikalgar
export GIT_EMAIL=sanasshikalgar@gmail.com
export GITHUB_ACCESS_TOKEN=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
export GIT_USER_UPSTREAM=Sana


############################################################################
#### DO NOT EDIT BELOW THIS LINE: derived variables
############################################################################

export GIT_REMOTE_URL=git@github.com:$GIT_USER/$GIT_REPO_NAME.git
export GIT_REMOTE_URL_HTTPS=https://github.com/$GIT_USER/$GIT_REPO_NAME.git
export GIT_REMOTE_UPSTREAM=$GIT_USER_UPSTREAM/$GIT_REPO_NAME


####################### Git Repo where notebooks will be pushed ############
cd $GIT_PARENT_DIR && git clone $GIT_REMOTE_URL_HTTPS



####################### Change in jupyter config ###########################
if [ ! -f ~/.jupyter/jupyter_notebook_config.py ]; then
   jupyter notebook --generate-config
fi

echo 'c.NotebookApp.disable_check_xsrf = True' >> ~/.jupyter/jupyter_notebook_config.py

cp $GIT_PARENT_DIR/githubcommit/config ~/.ssh/config
