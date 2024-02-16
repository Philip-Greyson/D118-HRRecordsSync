"""Script to send data to HR Records from PowerSchool.

https://github.com/Philip-Greyson/D118-HRRecordsSync

See the following for PS table information:
https://ps.powerschool-docs.com/pssis-data-dictionary/latest/teachers-ver7-8-0
https://ps.powerschool-docs.com/pssis-data-dictionary/latest/userscorefields-ver7-7-1
"""


# importing module
import os  # needed for environement variable reading
from datetime import *

import oracledb  # needed for connection to PowerSchool server (ordcle database)
import pysftp  # needed for sftp file upload

# set up database connection info
DB_UN = os.environ.get('POWERSCHOOL_READ_USER')  # username for read-only database user
DB_PW = os.environ.get('POWERSCHOOL_DB_PASSWORD')  # the password for the database account
DB_CS = os.environ.get('POWERSCHOOL_PROD_DB')  # the IP address, port, and database name to connect to

#set up sftp login info, stored as environment variables on system
SFTP_UN = os.environ.get('HRRECORDS_SFTP_USERNAME')
SFTP_PW = os.environ.get('HRRECORDS_SFTP_PASSWORD')
SFTP_HOST = os.environ.get('HRRECORDS_SFTP_ADDRESS')
CNOPTS = pysftp.CnOpts(knownhosts='known_hosts')  # connection options to use the known_hosts file for key validation

SFTP_OUTPUT_DIRECTORY = '/syncNine/Inbound'

print(f"Username: {DB_UN} | Password: {DB_PW} | Server: {DB_CS}")  # debug so we can see where oracle is trying to connect to/with
print(f"SFTP Username: {SFTP_UN} | SFTP Password: {SFTP_PW} | SFTP Server: {SFTP_HOST}")  # debug so we can see where pysftp is trying to connect to/with
badnames = ['use', 'training1','trianing2','trianing3','trianing4','planning','admin','nurse','user', 'use ', 'test', 'testtt']


if __name__ == '__main__':  # main file execution
    with open('HRRecords_log.txt', 'w') as log:
        startTime = datetime.now()
        startTime = startTime.strftime('%H:%M:%S')
        print(f'INFO: Execution started at {startTime}')
        print(f'INFO: Execution started at {startTime}', file=log)
        with open('StaffData.txt', 'w') as StaffDataOutput:
            with open('Job Types.txt', 'w') as JobTypesOutput:
                # print out header rows into files, column names with tab delimiters
                print('Global Identifier\tEmployee ID\tFirst Name\tLast Name\tWork Email\tBuilding ID\tHome Phone\tBirth Date\tGender\tUsername\tPersonal Email\tMiddle Name\tStreet Address\tCity\tState\tZip\tStatus\tDeactivated\tDCID', file=StaffDataOutput)
                print('Employee ID\tJob Type\tBuilding ID\tFirst Name\tLast Name', file=JobTypesOutput)
                try:
                    with oracledb.connect(user=DB_UN, password=DB_PW, dsn=DB_CS) as con:  # create the connecton to the database
                        with con.cursor() as cur:  # start an entry cursor
                            print("Connection established - version: " + con.version)
                            print("Connection established - version: " + con.version, file=log)
                            # do the main SQL query for all staff members
                            cur.execute('SELECT teachers.email_addr, teachers.teachernumber, teachers.first_name, teachers.last_name, teachers.staffstatus, teachers.homeschoolid, teachers.schoolid, teachers.home_phone, userscorefields.dob, userscorefields.gender, teachers.email_addr, u_humanresources.personal_email, teachers.middle_name, teachers.street, teachers.city, teachers.state, teachers.zip, teachers.status, teachers.users_dcid\
                                        FROM teachers LEFT JOIN UsersCoreFields ON Teachers.USERS_DCID = UsersCoreFields.UsersDCID LEFT JOIN u_humanresources ON teachers.users_dcid = u_humanresources.usersdcid\
                                        WHERE teachers.email_addr IS NOT NULL ORDER BY teachers.users_dcid')
                            staffMembers = cur.fetchall()  # fetchall() is used to fetch all records from result set
                            for staff in staffMembers:
                                try:
                                    if staff[5] == staff[6]:  # check the homeschoolid against school id, only print if they match so we dont get duplicates with teachers in multiple buildings
                                        if not staff[2].lower() in badnames and not staff[3].lower() in badnames:  # check first and last name against array of bad names, only print if both come back not in it
                                            email = str(staff[0])
                                            teacherNum = staff[1]
                                            firstName = str(staff[2])
                                            lastName = str(staff[3])
                                            staffType = staff[4]
                                            if staffType == 1:  # if their staffstatus is 1 they are a teacher
                                                staffType = 'Teacher'
                                            elif staffType == 3:  # if their staffstatus is 3 they are a lunch staff/playground supervisor
                                                staffType = 'Lunch Staff'
                                            elif staffType == 4:  # if staffstatus is 4 they are a sub
                                                staffType = 'Substitute'
                                            else:  # otherwise just consider them staff
                                                staffType = 'Staff'
                                            schoolID = str(staff[5])
                                            homePhone = str(staff[7]) if staff[7] else ''  # take the result if there is one, otherwise just use a empty string so output does not break
                                            birthday = str(staff[8]) if staff[8] else ''
                                            gender = str(staff[9]) if staff[9] else ''
                                            personalEmail = str(staff[11]) if staff[11] else ''
                                            middleName = str(staff[12]) if staff[12] else ''
                                            address = str(staff[13]) if staff[13] else ''
                                            city = str(staff[14]) if staff[14] else ''
                                            state = str(staff[15]) if staff[15] else ''
                                            zipcode = str(staff[16]) if staff[16] else ''
                                            staffStatus = str(staff[17]) if staff[17] else ''
                                            # If staffstatus is 1 they are active so the "deactivated" field is set to false, otherwise set to true
                                            deactivated = 'False' if staffStatus == '1' else 'True'
                                            teacherDCID = str(staff[18])

                                            # Print out all the fields to the staff data file, tab delimited
                                            print(f'{email}\t{teacherNum}\t{firstName}\t{lastName}\t{email}\t{schoolID}\t{homePhone}\t{birthday}\t{gender}\t{email}\t{personalEmail}\t{middleName}\t{address}\t{city}\t{state}\t{zipcode}\t{staffStatus}\t{deactivated}\t{teacherDCID}', file=StaffDataOutput)
                                            # Then print out the fields for the job types file, tabe delimited again
                                            print(f'{teacherNum}\t{staffType}\t{schoolID}\t{firstName}\t{lastName}', file=JobTypesOutput)
                                        else:
                                            print(f'WARN: Found bad name {staff[2]} {staff[3]}, skipping')
                                            print(f'WARN: Found bad name {staff[2]} {staff[3]}, skipping', file=log)

                                except Exception as er:
                                    print(f'ERROR while processing {staff[0]}: {er}')
                                    print(f'ERROR while processing {staff[0]}: {er}', file=log)

                except Exception as er:
                    print(f'ERROR while connecting to PS Database or running initial query: {er}')
                    print(f'ERROR while connecting to PS Database or running initial query: {er}', file=log)

        with pysftp.Connection(SFTP_HOST, username=SFTP_UN, password=SFTP_PW, cnopts=CNOPTS) as sftp:
            print(f'INFO: SFTP connection to HR Records at {SFTP_HOST} successfully established')
            print(f'INFO: SFTP connection to HR Records at {SFTP_HOST} successfully established', file=log)
            # print(sftp.pwd)  # debug, show what folder we connected to
            # print(sftp.listdir())  # debug, show what other files/folders are in the current directory
            sftp.chdir(SFTP_OUTPUT_DIRECTORY)  # change to the extensionfields folder
            # print(sftp.pwd)  # debug, make sure out changedir worked
            # print(sftp.listdir())
            sftp.put('StaffData.txt')  # upload the file onto the sftp server
            print("INFO: Staff Data file placed on remote server")
            print("INFO: Staff Data file placed on remote server", file=log)
            sftp.put('Job Types.txt')  # upload the file onto the sftp server
            print("INFO: Job Types file placed on remote server")
            print("INFO: Job Types file placed on remote server", file=log)

        endTime = datetime.now()
        endTime = endTime.strftime('%H:%M:%S')
        print(f'INFO: Execution ended at {endTime}')
        print(f'INFO: Execution ended at {endTime}', file=log)
