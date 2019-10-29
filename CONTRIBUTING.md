# Contributing

### Branches ###
* _master_: The `master` branch is exclusively for code that has already been released on Pypi. Pull requests are required to merge changes into this branch.
* _uat_: Code that is in 'in-package' testing. This means that the latest TestPypi release should remain synced with this branch. Pull requests are not required to merge changes into this branch.

### General contribution pipeline ###
This is a suggestion, not regulation. You may control your source code however you wish, however please keep `uat` mostly bug-free. All changes to master must go through a pull request.
1. Create a record of what you are contributing in the 'Contribution' project. If the change is responding to a recorded issue, this should already be listed.
2. Using `uat`, create a new branch for your contribution. This should have a clear name that reflects what the change is.
3. Masterfully program your contribution (and test, if you feel so inclined).
4. Merge your branch into `uat`.
5. Release `uat` onto TestPypi
6. Test
7. If testing fails, revert `uat` and return to 3
8. If testing succeeds, create a pull request for `uat`->`master`
