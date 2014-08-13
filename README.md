Ansible Playbooks for Galaxy deployment at Princeton
====================================================

`galaxy_deploy.yaml`
--------------------

Stops the galaxy server if it's running, clones the specified revision, applies custom patches, installs legacy tools and dependencies (not binaries) and restarts the server.

**Required parameters:**

* `-i`: inventory host file
* `--ask-sudo-pass`: password to be used to sudo to galaxy user
* `--ask-vault-pass`: password used to decrypt the passwords file (used for production only)

*Examples:*

* `ansible-playbook -i development/inventory --ask-sudo-pass galaxy_deploy.yaml`
* `ansible-playbook -i producion/inventory --ask-sudo-pass --ask-vault-pass galaxy_deploy.yaml`


`galaxy_stop.yaml`
-------------------

Stops the galaxy server and reports web applications if they are running.  Changes the 503 error message, which Apache will now serve up, to "scheduled outage".

**Required parameters:**

* `-i`: inventory host file
* `--ask-sudo-pass`: password to be used to sudo to galaxy user

*Examples:*

* `ansible-playbook -i development/inventory --ask-sudo-pass galaxy_stop.yaml`


`galaxy_start.yaml`
-------------------

Starts the galaxy server and reports web applications.  Changes the 503 error message, which should no longer show up, to "unscheduled outage".

**Required parameters:**

* `-i`: inventory host file
* `--ask-sudo-pass`: password to be used to sudo to galaxy user

*Examples:*

* `ansible-playbook -i development/inventory --ask-sudo-pass galaxy_start.yaml`


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

