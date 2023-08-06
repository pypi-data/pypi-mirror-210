Idem_vmware_alb
===============

vmware_alb Cloud Provider for Idem

DEVELOPMENT
===========

Clone the `idem_vmware_alb` repository and install with pip.

.. code:: bash

    git clone git@gitlab.com:my-user/idem_vmware_alb.git
    pip install -e idem_vmware_alb

ACCT
====

After installation vmware_alb Idem Provider execution and state modules will be accessible to the pop `hub`.
In order to use them we need to set up our credentials.

Create a new file called `credentials.yaml` and populate it with profiles.
The `default` profile will be used automatically by `idem` unless you specify one with `--acct-profile=profile_name` on the cli.

`acct backends <https://gitlab.com/saltstack/pop/acct-backends>`_ provide alternate methods for storing profiles.

The vmware_alb provider uses the vmware_alb acct plugin for authentication.
A profile needs to specify the authentication parameters for vmware_alb.

credentials.yaml

..  code:: sls

    vmware_alb:
      default:
        username: my_user
        password: my_good_password
        endpoint_url: https://console.vmware_alb.com/api

Now encrypt the credentials file and add the encryption key and encrypted file path to the ENVIRONMENT.

The `acct` command should be available as it is a requisite of `idem` and `idem_vmware_alb`.
Encrypt the the credential file.

.. code:: bash

    acct encrypt credentials.yaml

output::

    -A9ZkiCSOjWYG_lbGmmkVh4jKLFDyOFH4e4S1HNtNwI=

Add these to your environment:

.. code:: bash

    export ACCT_KEY="-A9ZkiCSOjWYG_lbGmmkVh4jKLFDyOFH4e4S1HNtNwI="
    export ACCT_FILE=$PWD/credentials.yaml.fernet


USAGE
=====
A profile can be specified for use with a specific state.
If no profile is specified, the profile called "default", if one exists, will be used:

.. code:: sls

    ensure_user_exists:
      vmware_alb.user.present:
        - acct_profile: my-staging-env
        - name: a_user_name
        - kwarg1: val1

It can also be specified from the command line when executing states.

.. code:: bash

    idem state --acct-profile my-staging-env my_state.sls

It can also be specified from the command line when calling an exec module directly.

.. code:: bash

    idem exec --acct-profile my-staging-env vmware_alb.user.list
