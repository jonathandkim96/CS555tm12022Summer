from datetime import datetime
import pandas as pd
import datetime
from tabulate import tabulate
from pandas._libs.tslibs.offsets import relativedelta
import logging

justLines = []
dictIndi = {}
dictFam = {}
with open('./Sprint 2/Family.ged') as f:
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
alive = True
for key, value in dictIndi.items():
    age = 0
    deat_count = 0
    # print(value)
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
            deat_count = deat_count + 1
        if(value[i][0] == 'FAMC'):
            famc = value[i][1]
        if(value[i][0] == 'FAMS'):
            fams = value[i][1]
        if(deat_count < 1):
            deat = 'NA'
    if (any('DEAT' in i for i in value)):
        alive = False
        age = relativedelta(deat, birt).years
    else:
        age = relativedelta(datetime.datetime.now(), birt).years
        alive = 'NA'

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
print("\n")

######################### Chaitanya Pawar's Code #########################
# US09 : CP
# Child should be born before death of mother and before 9 months after death of father

def US09():
    count = 0
    error = []
    for i in range(len(df_fam)):
        if(len(df_fam['Children'][i]) > 0):
            if(len(df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values) > 0 and df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][8] != 'NA' and df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][6] != 'NA' and len(df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][8]) > 0 and df_indi['Alive'].loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0] == False):
                logging.debug('First IF is here')
                if(df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][2] == 'F' and df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][6] < df_indi.loc[df_indi['Child'] == df_fam['ID'][i]].values[0][3]):
                    print_line = 'ERROR: FAMILY: US09: '+str(i)+': '+df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][0]+': '+'Mother\'s death date ' + df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][6].strftime(
                        "%Y-%m-%d") + ' before birthdate of child ' + df_indi.loc[df_indi['Child'] == df_fam['ID'][i]].values[0][3].strftime("%Y-%m-%d")
                    count = count + 1
                    error.append(print_line)
                elif(df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][2] == 'M' and df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][6] < ((df_indi.loc[df_indi['Child'] == df_fam['ID'][i]].values[0][3]) - datetime.timedelta(9*365/12))):
                    print_line = 'ERROR: FAMILY: US09: '+str(i)+': '+df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][0]+': '+'Father\'s death date ' + df_indi.loc[df_indi['Spouce'] == df_fam['ID'][i]].values[0][6].strftime(
                        "%Y-%m-%d") + ' before birthdate of child ' + df_indi.loc[df_indi['Child'] == df_fam['ID'][i]].values[0][3].strftime("%Y-%m-%d")
                    count = count + 1
                    error.append(print_line)
    if(count > 0):
        return (error)
    else:
        error.append('ERROR: US09: No records found')
        return(error)


errorUS09 = US09()
print(*errorUS09, sep="\n")


# US10 : CP
# Marriage should be at least 14 years after birth of both spouses (parents must be at least 14 years old)
######################### End of Chaitanya Pawar's Code #########################

######################### Jonathan Kim's Code #########################

def US10():
    count = 0
    error = []
    no = []
    for i in range(len(df_fam)):
        if((df_fam['Married'][i]) != 'NA'):
            if((df_fam['Married'][i] - df_indi.loc[df_indi['ID'] == df_fam['Husband ID'][i]].values[0][3]) < datetime.timedelta(168*365/12)):
                print_line = 'ERROR: FAMILY: US10: '+str(i)+': '+df_indi.loc[df_indi['ID'] == df_fam['Husband ID'][i]].values[0][0]+': '+'Father\'s birth date ' + df_indi.loc[df_indi['ID']
                                                                                                                                                                               == df_fam['Husband ID'][i]].values[0][3].strftime("%Y-%m-%d") + ' less than 14 years of marriage date ' + df_fam['Married'][i].strftime("%Y-%m-%d")
                count += 1
                error.append(print_line)
            elif((df_fam['Married'][i] - df_indi.loc[df_indi['ID'] == df_fam['Wife ID'][i]].values[0][3]) < datetime.timedelta(168*365/12)):
                print_line = 'ERROR: FAMILY: US10: '+str(i)+': '+df_indi.loc[df_indi['ID'] == df_fam['Wife ID'][i]].values[0][0]+': '+'Mother\'s birth date ' + df_indi.loc[df_indi['ID']
                                                                                                                                                                            == df_fam['Wife ID'][i]].values[0][3].strftime("%Y-%m-%d") + ' less than 14 years of marriage date ' + df_fam['Married'][i].strftime("%Y-%m-%d")
                count += 1
                error.append(print_line)

    if(count > 0):
        return (error)
    else:
        no.append('ERROR: US10: No records found')
        return(no)


errorUS10 = US10()
print(*errorUS10, sep="\n")

def US15():
    error = []
    for i in range(len(df_fam)):
        if len(df_fam['Children'][i]) > 15:
            print_line = 'ERROR: FAMILY: US15: THERE SHOULD BE FEWER THAN 15 SIBLINGS IN A FAMILY'
            error.append(print_line)

    if((len(error)) > 0):
        return (error)
    else:
        error.append('ERROR: US15: No records found')
        return(error)

errorUS15 = US15()
print(*errorUS15, sep="\n")

def US16():
    error = []
    for i in range(len(df_fam)):

        last_name = df_fam['Husband Name'][0].split('/',1)[1]
        for j in range(len(df_fam['Children'][i])):
            if ((df_indi[df_indi['ID']==df_fam['Children'][i][j]]['Gender']) == 'F').values[0] == True:
                continue
            else:
                name_check = df_indi[df_indi['ID']==df_fam['Children'][i][j]]['Name'].values[0].split('/',1)[1]
                if name_check != last_name:

                    print_line = 'ERROR: FAMILY: US16: '+str(i)+': '+df_fam.loc[i]['ID']+ ': ALL MALE MEMBERS OF A FAMILY SHOULD HAVE THE SAME LAST NAME'
                    error.append(print_line)

    if((len(error)) > 0):
        return (error)
    else:
        error.append('ERROR: US16: No records found')
        return(error)

errorUS16 = US16()
print(*errorUS16, sep="\n")

######################### End of Jonathan Kim's Code #########################
