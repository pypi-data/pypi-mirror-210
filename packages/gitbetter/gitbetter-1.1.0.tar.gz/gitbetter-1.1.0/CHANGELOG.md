# Changelog

## v1.0.0 (2023-05-21)

#### New Features

* all git functions can return stdout as a string
#### Fixes

* fix issue where git.add() would remove path separators
#### Refactorings

* git bindings are now contained in the `Git` class
* do_commit() doesn't assume arg string is a message
* make capture_stdout a class property
* update shell to use Git class
* move git functions into a class so dev can specify whether to capture stdout or not
#### Docs

* update readme


## v0.5.2 (2023-05-15)

#### Fixes

* fix create_remote_from_cwd function to properly add remote and push


## v0.5.1 (2023-05-13)

#### Fixes

* fix  create_remote_from_cwd() not setting remote to upstream


## v0.5.0 (2023-05-11)

#### New Features

* add create_remote_from_cwd()
#### Refactorings

* rename do_list_branches() to do_branches()
* do_new_gh_remote invokes create_remote_from_cwd so url no longer needs to be added manually after creating remote
#### Docs

* update readme
* update doc string


## v0.4.0 (2023-05-04)

#### New Features

* add status command


## v0.3.0 (2023-05-02)

#### Refactorings

* remove do_cmd as it's now covered by parent class's do_sys


## v0.2.0 (2023-05-02)

#### New Features

* override do_help to display unrecognized_command_behavior_status after standard help message
* add functionality to toggle unrecognized command behavior
* add default override to execute line as system command when unrecognized
* display current working directory in prompt
#### Fixes

* set requires-python to >=3.10
#### Refactorings

* remove cwd command
#### Docs

* update readme


## v0.1.1 (2023-04-30)

#### Fixes

* cast Pathier objects to strings in recurse_files()


## v0.1.0 (2023-04-30)

#### New Features

* add do_cmd() to excute shell commands without quitting gitbetter
* enclose 'message' in quotes if you forget them
#### Refactorings

* rename some functions
#### Docs

* update readme
* add future feature to list in readme


## v0.0.0 (2023-04-29)
