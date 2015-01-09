Ansible Playbooks for Galaxy deployment at Princeton
====================================================

`galaxy_deploy.yaml`
--------------------

Stops the galaxy server if it's running, clones the specified revision, applies custom patches, installs legacy tools and dependencies (not binaries) and restarts the server.

**Required parameters:**

* `-i`: inventory host file
* `--ask-sudo-pass`: password to be used to sudo to galaxy user
* `--ask-vault-pass`: password used to decrypt the passwords file (used for production only)

**Optional parameters:**

* `--tags`: only run plays and tasks tagged with these values (start, stop, restart)
* `--skip-tags`: only run plays and tasks whose tags do not match these values (start, stop, restart)


*Examples:*

* Deploy galaxy to development, restarting galaxy

    `ansible-playbook -i development/inventory --ask-sudo-pass galaxy_deploy.yaml`

* Deploy galaxy to production (including restart)

    `ansible-playbook -i producion/inventory --ask-sudo-pass --ask-vault-pass galaxy_deploy.yaml`

* Deploy galaxy, but do NOT restart

    `ansible-playbook -i development/inventory --ask-sudo-pass --skip-tags restart galaxy_deploy.yaml`

* Restart galaxy, but do not update any files (no deployment related tasks)

    `ansible-playbook -i development/inventory --ask-sudo-pass --tags restart galaxy_deploy.yaml`



`galaxy_test.yaml`
------------------

**BETA**

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

