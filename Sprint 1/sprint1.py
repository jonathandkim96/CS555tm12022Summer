from datetime import datetime
import pandas as pd
import datetime
from tabulate import tabulate
from pandas._libs.tslibs.offsets import relativedelta

justLines = []
dictIndi = {}
dictFam = {}
with open('./Sprint 1/Family.ged') as f:
    lines = f.read().splitlines()
    justLines.append(lines)
lines = [[el] for el in lines]
for i in range(len(lines)):
    if((len(lines[i][0].strip().split())) < 2):
        lines[i] = "Incomplete GEDCOM on Line "+str(i)
    else:
        lines[i] = lines[i][0].strip().split(" ", 2)
        if(len(lines[i]) > 2 and lines[i][1] in ['INDI', 'FAM']):
            lines[i] = "Invalid GEDCOM on Line "+str(i)
        elif(len(lines[i]) > 2 and lines[i][2] in ['INDI', 'FAM']):
            lines[i][1], lines[i][2] = lines[i][2], lines[i][1]

valid_tags = {'INDI': '0', 'NAME': '1', 'SEX': '1', 'BIRT': '1', 'DEAT': '1', 'FAMC': '1', 'FAMS': '1', 'FAM': '0',
              'MARR': '1', 'HUSB': '1', 'WIFE': '1', 'CHIL': '1', 'DIV': '1', 'DATE': '2', 'HEAD': '0',
              'TRLR': '0', 'NOTE': '0'}

gedcom_out = []
for i in range(len(lines)):

    # print("-->"+justLines[0][i])
    if(len(lines[i]) > 2):
        if(lines[i][1] in valid_tags.keys() and valid_tags[lines[i][1]] == (lines[i][0])):
            # print("<--"+lines[i][0]+"|"+lines[i][1]+"|Y|"+lines[i][2])
            gedcom_out.append((lines[i][0], lines[i][1], lines[i][2]))
        elif(lines[i][0:2] == "In"):
            # print("<--"+lines[i])
            gedcom_out.append(lines[i])
        else:
            continue
            # print("<--"+lines[i][0]+"|"+lines[i][1]+"|N|"+lines[i][2])
    elif(len(lines[i]) == 2):
        if(lines[i][1] in valid_tags.keys() and valid_tags[lines[i][1]] == (lines[i][0])):
            # print("<--"+lines[i][0]+"|"+lines[i][1]+"|Y|")
            gedcom_out.append((lines[i][0], lines[i][1]))
        else:
            # print("<--"+lines[i][0]+"|"+lines[i][1]+"|N|")
            continue
gedcom_out.pop(0)
gedcom_out.pop(-1)
gedcom_out = list(filter((('1', 'BIRT')).__ne__, gedcom_out))

flag = 0
for i in range(len(gedcom_out)):
    if(i > 500):
        break
    lst_vals = []
    j = i+1
    if(gedcom_out[i][1] == 'INDI' and gedcom_out[i][0] == '0'):
        while(gedcom_out[j][1] != 'INDI'):
            key = gedcom_out[i][2][1:-1]
            if(gedcom_out[j][1] == 'FAM' and gedcom_out[j][0] == '0'):
                flag = 1
                break
            elif(gedcom_out[j][1] == 'DEAT' and gedcom_out[j][2] == 'Y'):
                lst_vals.append(('DEAT', gedcom_out[j+1][2]))
                j += 1
            elif(gedcom_out[j][1] == 'FAMS' or gedcom_out[j][1] == 'FAMC'):
                lst_vals.append((gedcom_out[j][1], gedcom_out[j][2][1:-1]))
            else:
                lst_vals.append((gedcom_out[j][1], gedcom_out[j][2]))
            j += 1
        dictIndi.update({key: lst_vals})
        if(flag == 1):
            break

# individuals dataframe
df_indi = pd.DataFrame(columns=[
                       'ID', 'Name', 'Gender', 'Birthday', 'Age', 'Alive', 'Death', 'Child', 'Spouce'])
name, gender, birt, deat = "", "", "", ""
alive = False
for key, value in dictIndi.items():
    age = 0
    for i in range(len(value)):
        famc, fams = "", ""
        if(value[i][0] == 'NAME'):
            name = value[i][1]
        if(value[i][0] == 'SEX'):
            gender = value[i][1]
        if(value[i][0] == 'DATE'):
            birt = value[i][1]
            birt = datetime.datetime.strptime(birt, '%d %b %Y').date()
        if(value[i][0] == 'DEAT'):
            deat = value[i][1]
            deat = datetime.datetime.strptime(deat, '%d %b %Y').date()
        if(value[i][0] == 'FAMC'):
            famc = value[i][1]
        if(value[i][0] == 'FAMS'):
            fams = value[i][1]
    if (any('DEAT' in i for i in value)):
        alive = True
        age = relativedelta(deat, birt).years
    else:
        age = relativedelta(datetime.datetime.now(), birt).years

    df_indi = df_indi.append({'ID': key, 'Name': name, 'Gender': gender, 'Birthday': birt,
                              'Alive': alive, 'Death': deat, 'Child': famc, 'Spouce': fams, 'Age': age}, ignore_index=True)
    df_indi = (df_indi.replace(r'^\s*$', 'NA', regex=True))

flag = 0
for i in range(len(gedcom_out)):
    if(i > 1000):
        break
    lst_vals = []
    j = i+1
    if(gedcom_out[i][1] == 'FAM' and gedcom_out[i][0] == '0'):
        while(j < len(gedcom_out)):
            key = gedcom_out[i][2][1:-1]
            # husb wife child extract
            if(gedcom_out[j][1] != 'MARR' and gedcom_out[j][1] != 'DIV' and gedcom_out[j][1] != 'DATE' and gedcom_out[j][1] != 'FAM'):
                lst_vals.append((gedcom_out[j][1], gedcom_out[j][2][1:-1]))
            # married date extract
            elif(gedcom_out[j][1] == 'MARR' and len(gedcom_out[j+1]) > 2):
                lst_vals.append(('MARR', gedcom_out[j+1][2]))
            # divo date extract
            elif(gedcom_out[j][1] == 'DIV' and len(gedcom_out[j+1]) > 2):
                lst_vals.append(('DIV', gedcom_out[j+1][2]))
            # if next fam then break
            elif(gedcom_out[j][1] == 'FAM' and gedcom_out[j][0] == '0'):
                flag = 1
                break
            j += 1
        dictFam.update({key: lst_vals})

# Families dataframe
husb_id, wife_id = 0, 0
husb_name, wife_name = "", ""
child = []
df_fam = pd.DataFrame(columns=['ID', 'Married', 'Divorced',
                               'Husband ID', 'Husband Name', 'Wife ID', 'Wife Name', 'Children'])
for key, value in dictFam.items():
    child = []
    married, div = "", ""
    for i in range(len(value)):
        if(value[i][0] == 'HUSB'):
            husb_id = value[i][1]
            husb_name = dictIndi[husb_id][0][1]
        if(value[i][0] == 'WIFE'):
            wife_id = value[i][1]
            wife_name = dictIndi[wife_id][0][1]
        if(value[i][0] == 'CHIL'):
            child.append(value[i][1])
        if(value[i][0] == 'MARR'):
            married = value[i][1]
            married = datetime.datetime.strptime(married, '%d %b %Y').date()
        if(value[i][0] == 'DIV'):
            div = value[i][1]
            div = datetime.datetime.strptime(div, '%d %b %Y').date()

    df_fam = df_fam.append({'ID': key, 'Married': married, 'Divorced': div, 'Husband ID': husb_id,
                            'Husband Name': husb_name, 'Wife ID': wife_id, 'Wife Name': wife_name, 'Children': child, }, ignore_index=True)
    df_fam = (df_fam.replace(r'^\s*$', 'NA', regex=True))

print("Individuals")
print(tabulate(df_indi, headers='keys', tablefmt='psql'))
print("Families")
print(tabulate(df_fam, headers='keys', tablefmt='psql'))
print('\n\n')

######################### Chaitanya Pawar's Code #########################
# US01 : CP
# Dates before current date


def US01():
    error = []
    todayDate = datetime.datetime.strptime(
        datetime.datetime.today().strftime('%Y-%m-%d'), '%Y-%m-%d').date()
    for i in range(len(df_indi)):
        if(df_indi['Birthday'][i] != 'NA' and df_indi['Birthday'][i] > todayDate):
            birthday = 'ERROR: INDIVIDUAL: US01: ' + \
                str(i)+': '+df_indi.loc[i]['ID']+': ' + str(df_indi.loc[i]['Name']) + ' has a Birthday on ' + \
                str(df_indi.loc[i]['Birthday']) + ' which occurs in the future'
            error.append(birthday)
        elif(df_indi['Death'][i] != 'NA' and df_indi['Death'][i] > todayDate):
            deathdate = 'ERROR: INDIVIDUAL: US01: ' + \
                str(i)+': '+df_indi.loc[i]['ID']+': ' + str(df_indi.loc[i]['Name']) + ' has a Deathday on ' + \
                str(df_indi.loc[i]['Death']) + ' which occurs in the future'
            error.append(deathdate)
    for i in range(len(df_fam)):
        if(df_fam['Married'][i] != 'NA' and df_fam['Married'][i] > todayDate):
            married = 'ERROR: FAMILY: US01: '+str(i)+': '+df_fam.loc[i]['ID']+': '+'Marriage Day ' + str(
                df_fam.loc[i]['Married']) + ' between ' + df_fam.loc[i]['Husband Name']+' (ID: ' + df_fam.loc[i]['Husband ID']+')'+' and ' + df_fam.loc[i]['Wife Name'] + ' (ID: '+df_fam.loc[i]['Wife ID'] + ')' + ' occurs in the future'
            error.append(married)
        elif(df_fam['Divorced'][i] != 'NA' and df_fam['Divorced'][i] > todayDate):
            divorced = 'ERROR: FAMILY: US01: '+str(i)+': '+df_fam.loc[i]['ID']+': '+'Divorce Day ' + str(
                df_fam.loc[i]['Divorced']) + ' between ' + df_fam.loc[i]['Husband Name']+' (ID: ' + df_fam.loc[i]['Husband ID']+')'+' and ' + df_fam.loc[i]['Wife Name'] + ' (ID: '+df_fam.loc[i]['Wife ID'] + ')' + ' occurs in the future'
            error.append(divorced)
    if((len(error)) > 0):
        return (error)
    else:
        error.append('ERROR: US01: No records found')
        return(error)


errorUS01 = US01()
print(*errorUS01, sep="\n")

# US02 : CP
# Dates Birth before marriage


def US02():
    error = []
    for i in range(len(df_indi)):
        if(df_indi['Birthday'][i] != 'NA' and df_indi['Spouce'][i] != 'NA' and (df_fam[df_fam['ID'] == df_indi['Spouce'][i]]['Married'].values[0]) < (df_indi['Birthday'][i])):
            if(df_indi['Gender'][i] == 'M'):
                print_line = 'ERROR: INDIVIDUAL: US02: '+str(i)+': '+df_indi.loc[i]['ID']+': '+df_indi.loc[i]['Name'] + ' has a birthday on ' + str(
                    df_indi.loc[i]['Birthday']) + ' which is after his marriage date ' + str(df_fam[df_fam['ID'] == df_indi['Spouce'][i]]['Married'].values[0])
                error.append(print_line)
            elif(df_indi['Gender'][i] == 'F'):
                print_line = 'ERROR: INDIVIDUAL: US02: '+str(i)+': '+df_indi.loc[i]['ID']+': '+df_indi.loc[i]['Name'] + ' has a birthday on ' + str(
                    df_indi.loc[i]['Birthday']) + ' which is after her marriage date ' + str(df_fam[df_fam['ID'] == df_indi['Spouce'][i]]['Married'].values[0])
                error.append(print_line)
            else:
                print_line = 'ERROR: INDIVIDUAL: US02: '+str(i)+': '+df_indi.loc[i]['ID']+': '+df_indi.loc[i]['Name'] + ' has a birthday on ' + str(
                    df_indi.loc[i]['Birthday']) + ' which is after their marriage date ' + str(df_fam[df_fam['ID'] == df_indi['Spouce'][i]]['Married'].values[0]) + '\n'
                error.append(print_line)
    if((len(error)) > 0):
        return (error)
    else:
        error.append('ERROR: US01: No records found')
        return(error)


errorUS02 = US02()
print(*errorUS02, sep="\n")

######################### End of Chaitanya Pawar's Code #########################

######################### Jonathan Kim's Code #########################
def US05():
    error = []
    for i in range(len(df_indi)):

        if(df_indi['Death'][i] != 'NA' and df_indi['Spouce'][i] != 'NA' and (df_fam[df_fam['ID'] == df_indi['Spouce'][i]]['Married'].values[0]) > (df_indi['Death'][i])):

            if(df_indi['Gender'][i] == 'M'):
                print_line = 'ERROR: INDIVIDUAL: US05: '+str(i)+': '+df_indi.loc[i]['ID']+': '+df_indi.loc[i]['Name'] + ' has a marriage on ' + str(
                    df_fam[df_fam['ID'] == df_indi['Spouce'][i]]['Married'].values[0]) + ' which is after his death date ' + str(df_indi['Death'][i])
                error.append(print_line)
            elif(df_indi['Gender'][i] == 'F'):
                print_line = 'ERROR: INDIVIDUAL: US05: '+str(i)+': '+df_indi.loc[i]['ID']+': '+df_indi.loc[i]['Name'] + ' has a marriage on ' + str(
                    df_fam[df_fam['ID'] == df_indi['Spouce'][i]]['Married'].values[0]) + ' which is after her death date ' + str(df_indi['Death'][i])
                error.append(print_line)
            else:
                print_line = 'ERROR: INDIVIDUAL: US05: '+str(i)+': '+df_indi.loc[i]['ID']+': '+df_indi.loc[i]['Name'] + ' has a marriage on ' + str(
                    df_indi.loc[i]['Death']) + ' which is after their death date ' + str(df_fam[df_fam['ID'] == df_indi['Spouce'][i]]['Death'].values[0]) + '\n'
                error.append(print_line)
    if((len(error)) > 0):
        return (error)
    else:
        error.append('ERROR: US05: No records found')
        return(error)


errorUS05 = US05()
print(*errorUS05, sep="\n")

def US06():
    error = []
    for i in range(len(df_indi)):

        if(df_indi['Death'][i] != 'NA' and df_indi['Spouce'][i] != 'NA' and (df_fam[df_fam['ID'] == df_indi['Spouce'][i]]['Divorced'].values[0]) > (df_indi['Death'][i])):

            if(df_indi['Gender'][i] == 'M'):
                print_line = 'ERROR: INDIVIDUAL: US06: '+str(i)+': '+df_indi.loc[i]['ID']+': '+df_indi.loc[i]['Name'] + ' has a divorce on ' + str(
                    df_fam[df_fam['ID'] == df_indi['Spouce'][i]]['Divorced'].values[0]) + ' which is after his death date ' + str(df_indi['Death'][i])
                error.append(print_line)
            elif(df_indi['Gender'][i] == 'F'):
                print_line = 'ERROR: INDIVIDUAL: US06: '+str(i)+': '+df_indi.loc[i]['ID']+': '+df_indi.loc[i]['Name'] + ' has a divorce on ' + str(
                    df_fam[df_fam['ID'] == df_indi['Spouce'][i]]['Divorced'].values[0]) + ' which is after her death date ' + str(df_indi['Death'][i])
                error.append(print_line)
            else:
                print_line = 'ERROR: INDIVIDUAL: US06: '+str(i)+': '+df_indi.loc[i]['ID']+': '+df_indi.loc[i]['Name'] + ' has a divorce on ' + str(
                    df_indi.loc[i]['Death']) + ' which is after their death date ' + str(df_fam[df_fam['ID'] == df_indi['Spouce'][i]]['Death'].values[0]) + '\n'
                error.append(print_line)
    if((len(error)) > 0):
        return (error)
    else:
        error.append('ERROR: US06: No records found')
        return(error)


errorUS06 = US06()
print(*errorUS06, sep="\n")

######################### End of Jonathan Kim's Code #########################
