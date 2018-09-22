#!/usr/bin/env python
from migrate.versioning.shell import main

if __name__ == '__main__':
    main(
        repository='billing_db_repo',
        url='postgresql://billingdb_user:billingdb_pwd@0.0.0.0:5432/billingdb',
        debug='False')
