
# Fdetect

This program will detect changes in a directory and email them to the specified email.

The following diagram shows the basic paths of the script as an activity model.

## Features

This project contains the following features:

* Detect directory changes;
* Email the directory changes.

## Installation

Start by installing project dependencies:

```bash
$ pip3 install -r requirements.txt
```

Edit the `databaseinit.py` script and change the database path to the desired one. Run the `databaseinit.py` script to create the initial database:

```bash
$ python3 databaseinit.py
```

Open a python interpreter and setup a keyring password:

```bash
$ python3
>>> import keyring
>>> keyring.set_password("system","EMAIL_TO_SEND","PASSWORD_FROM_YOUR_EMAIL_HERE")
```
Leave the first two parameters of `keyring.set_password` as they are; change only the `PASSWORD_FROM_YOUR_EMAIL_HERE` to the password from the email that you want to send the message from.

Edit the `detectFile.py` script and change the database path to the desired one, the `IN_FOLDER` to the folder that you want to check for files, the `FROM_EMAIL` to the email corresponding to the previous set password and the `TO_EMAIL` to the email where you want to receive your message
    
## Run

To run the script, type:

```bash
$ python3 detectFile.py
```