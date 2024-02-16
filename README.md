# D118-HRRecordsSync

Script to synchronize the HR Records program with staff data from PowerSchool

## Overview

The script is pretty simple, it first makes the output files and prints the header row with column labels to them. Then a large SQL query is performed to return all the staff members in PowerSchool who have an email (not "fake" accounts). These staff members are iterated over and any entries that are not the homeschool entry are skipped. The demographic info is taken, a staff type string is assigned based on the staff status number, and then the data is output to the StaffData.txt and Job Types.txt files. These files are then uploaded via SFTP to the HR Records server for processing.
Right now this script references the teachers reporting view, though it would probably be better to query the users and schoolstaff tables individually, and I might do a refactor that eventually.

## Requirements

The following Environment Variables must be set on the machine running the script:

- POWERSCHOOL_READ_USER
- POWERSCHOOL_DB_PASSWORD
- POWERSCHOOL_PROD_DB
- HRRECORDS_SFTP_USERNAME
- HRRECORDS_SFTP_PASSWORD
- HRRECORDS_SFTP_ADDRESS

These are fairly self explanatory, and just relate to the usernames, passwords, and host IP/URLs for PowerSchool and the HR Records SFTP server (provided by them). If you wish to directly edit the script and include these credentials, you can.

You will need to provide the staff member's personal email into a custom field in PowerSchool so that it can be retrieved and output to HR Records. We use a custom table and field named `u_humanresouces.personal_email`, so that is what the script is configured to use by default. See customization below for more information.

Additionally, the following Python libraries must be installed on the host machine (links to the installation guide):

- [Python-oracledb](https://python-oracledb.readthedocs.io/en/latest/user_guide/installation.html)
- [pysftp](https://pypi.org/project/pysftp/)

**As part of the pysftp connection to the output SFTP server, you must include the server host key in a file** with no extension named "known_hosts" in the same directory as the Python script. You can see [here](https://pysftp.readthedocs.io/en/release_0.2.9/cookbook.html#pysftp-cnopts) for details on how it is used, but the easiest way to include this I have found is to create an SSH connection from a linux machine using the login info and then find the key (the newest entry should be on the bottom) in ~/.ssh/known_hosts and copy and paste that into a new file named "known_hosts" in the script directory.

## Customization

This is a pretty basic script, and just gets the fields in the format that HR Records wants. That being said, here are a few things you could change:

- We have the personal email coming from a custom table and field in PowerSchool named `u_humanresources.personal_email`, if you have the personal email somewhere else edit the main SQL query and change that part of the SELECT to match your custom table/field name. If you don't have the personal emails in a field, you will need to edit the SQL query to remove that, but also the storing of the output in the section below so that the indexes match up to the new output with one less field.
- If you want to change the "Staff Type" for the job types file to have different titles, you will need to edit the multiple `if staffType == x` statements with your desired title.
- If you need different names for the output files or a different directory to upload to, edit the `STAFF_DATA_FILENAME`, `JOB_TYPES_FILENAME` and `SFTP_OUTPUT_DIRECTORY` constants near the top of the file.
