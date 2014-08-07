Ansible Playbooks for Galaxy deployment at Princeton
====================================================

`deploy_galaxy.yaml`
--------------------

Stops the galaxy server if it's running, clones the specified revision, applies custom patches, installs legacy tools and dependencies (not binaries) and restarts the server.

**Required parameters:**

* `-i`: inventory host file
* `--ask-sudo-pass`: password to be used to sudo to galaxy user
* `--ask-vault-pass`: password used to decrypt the inventory file (contains passwords)

*Example:*

`ansible-playbook -i development/inventory --ask-sudo-pass --ask-vault-pass deploy_galaxy.yaml`


`galaxy_test.yaml`
------------------

Runs functional tests on specified galaxy hosts and downloads the results.

**Required parameters:**

* `-i`: inventory host file
* `--ask-sudo-pass`: password to be used to sudo to galaxy user
* `--ask-vault-pass`: password used to decrypt the inventory file (contains passwords)

**Optional parameters:**

* `-e "test_params=PARAMS"`: extra parameters to be passed to the functional test script

*Examples:*

`ansible-playbook -i development/inventory --ask-sudo-pass --ask-vault-pass galaxy_test.yaml`

`ansible-playbook -i development/inventory --ask-sudo-pass --ask-vault-pass -e "test_params=-migrated" galaxy_test.yaml`

