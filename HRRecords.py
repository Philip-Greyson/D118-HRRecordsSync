# importing module
import oracledb
import sys
import datetime
import os
from datetime import *

un = 'PSNavigator' #PSNavigator is read only, PS is read/write
pw = os.environ.get('POWERSCHOOL_DB_PASSWORD') #the password for the database account
cs = os.environ.get('POWERSCHOOL_PROD_DB') #the IP address, port, and database name to connect to

print("Username: " + str(un) + " |Password: " + str(pw) + " |Server: " + str(cs)) #debug so we can see where oracle is trying to connect to/with
badnames = ['USE', 'Training1','Trianing2','Trianing3','Trianing4','Planning','Admin','NURSE','USER', 'USE ', 'TEST', 'TESTTT']


with oracledb.connect(user=un, password=pw, dsn=cs) as con: # create the connecton to the database
    with con.cursor() as cur:  # start an entry cursor
        with open('StaffData.txt', 'w') as StaffDataOutput:
            with open('Job Types.txt', 'w') as JobTypesOutput:
                print("Connection established: " + con.version)
                try:
                    cur.execute('SELECT teachers.email_addr, teachers.teachernumber, teachers.first_name, teachers.last_name, teachers.staffstatus, teachers.homeschoolid, teachers.schoolid, teachers.home_phone, userscorefields.dob, userscorefields.gender, teachers.email_addr, U_DEF_EXT_SCHOOLSTAFF.HR_PERSONAL_EMAIL, teachers.middle_name, teachers.street, teachers.city, teachers.state, teachers.zip, teachers.status, teachers.users_dcid FROM teachers LEFT JOIN UsersCoreFields ON Teachers.USERS_DCID = UsersCoreFields.UsersDCID LEFT JOIN U_DEF_EXT_SCHOOLSTAFF On Teachers.dcid = U_DEF_EXT_SCHOOLSTAFF.SCHOOLSTAFFDCID WHERE teachers.email_addr IS NOT NULL ORDER BY teachers.users_dcid')
                    rows = cur.fetchall()  # fetchall() is used to fetch all records from result set

                    # print out header row into files
                    print('Global Identifier\tEmployee ID\tFirst Name\tLast Name\tWork Email\tBuilding ID\tHome Phone\tBirth Date\tGender\tUsername\tPersonal Email\tMiddle Name\tStreet Address\tCity\tState\tZip\tStatus\tDeactivated\tDCID\t', file=StaffDataOutput)
                    print('Employee ID\tJob Type\tBuilding ID\tFirst Name\tLast Name', file=JobTypesOutput)
                    for count, entrytuple in enumerate(rows):
                        try:
                            sys.stdout.write('\rProccessing staff entry %i' % count) # sort of fancy text to display progress of how many students are being processed without making newlines
                            sys.stdout.flush()
                            # print(entrytuple) # debug
                            entry = list(entrytuple) # convert tuples to an actual list so we can edit it
                            if entry[5] == entry[6]: #check the homeschoolid against school id, only print if they match so we dont get duplicates with teachers in multiple buildings
                                if not entry[2] in badnames and not entry[3] in badnames: #check first and last name against array of bad names, only print if both come back not in it
                                    email = str(entry[0])
                                    teacherNum = int(entry[1])
                                    firstName = str(entry[2])
                                    lastName = str(entry[3])
                                    staffType = entry[4]
                                    if staffType == 1: # if their staffstatus is 1 they are a teacher
                                        staffType = 'Teacher'
                                    elif staffType == 3: # if staffstatus is 3 they are a sub
                                        staffType = 'Substitute'
                                    else: # otherwise just consider them staff
                                        staffType = 'Staff'
                                    schoolID = str(entry[5])
                                    homePhone = str(entry[7])
                                    birthday = str(entry[8])
                                    gender = str(entry[9])
                                    personalEmail = str(entry[11])
                                    middleName = str(entry[12])
                                    address = str(entry[13])
                                    city = str(entry[14])
                                    state = str(entry[15])
                                    zipcode = str(entry[16])
                                    staffStatus = str(entry[17])
                                    # If staffstatus is 1 they are active so the "deactivated" field is set to false, otherwise set to true
                                    deactivated = 'False' if staffStatus == '1' else 'True'
                                    teacherDCID = str(entry[18])
                                    
                                    # Print out all the fields to the staff data file
                                    print(email + '\t' + str(teacherNum) + '\t' + firstName + '\t' + lastName + '\t' + email + '\t' + schoolID + '\t' + homePhone + '\t' + birthday + '\t' + gender + '\t' + email + '\t' + personalEmail + '\t' + middleName + '\t' + address + '\t' + city + '\t' + state + '\t' + zipcode + '\t' + staffStatus + '\t' + deactivated + '\t' + teacherDCID, file=StaffDataOutput)
                                    # Then print out the fields for the job types file
                                    print(str(teacherNum) + '\t' + staffType + '\t' + schoolID + '\t' + firstName + '\t' + lastName, file=JobTypesOutput)

                        except Exception as er:
                            print('Error on ' + entrytuple[0] + ': ' + str(er))
                        
                except Exception as er:
                    print('Error:'+str(er))


