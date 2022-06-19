from datetime import datetime
from datetime import date, timedelta
import pandas as pd
from collections import Counter
import datetime
import dateutil.relativedelta
from tabulate import tabulate
from pandas._libs.tslibs.offsets import relativedelta
import logging

justLines = []
dictIndi = {}
dictFam = {}
with open('Family.ged') as f:
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
        alive = True

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
# User Story 25 : CP
# Unique first names in families
def US25():

    df_copy_indi = df_indi.copy()
    df_copy_fam = df_fam.copy()
    row = df_copy_indi.iloc[1:7]
    df_copy = df_copy_indi.append(row, ignore_index=True)
    name_birth_list = []
    error = []

    for index, col in df_copy_fam.iterrows():
        child = col['Children']
        if child != None:
            for index, col in df_copy.iterrows():
                if col['ID'] in child:
                    name = col['Name']
                    birth = str(col['Birthday'])
                    temp = (name, birth)
                    name_birth_list.append(temp)

    count = dict(Counter(name_birth_list))

    for key, value in count.items():
        if value > 1:
            error.append(
                "ERROR: INDIVIDUAL: US25: No unique first name in family for name: " + str(key[0]))

    return error


us25Error = US25()
print(*us25Error, sep="\n")

# User Story 26 : CP
# Corresponding entries
def US26():

    df_copy_indi = df_indi.copy()
    df_copy_fam = df_fam.copy()

    date_value = datetime.datetime.strptime('1960-04-14', '%Y-%m-%d').date()
    entries_fam_roles = []
    entries_indi_roles = []
    error_indi = []
    error_fam = []
    error = []

    fam_id_list = ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10"]
    indi_id_list = ["I1", "I2", "I3", "I4", "I5", "I6", "I7", "I8", "I9",
                    "I10", "I11", "I12", "I13", "I14", "I15", "I16", "I17", "I18"]

    df_copy_indi = df_copy_indi.append({'ID': 'I2', 'Name': 'Robb /Stark/', 'Gender': 'M',
                                        'Birthday': date_value, 'Age': 22, 'Child': 'F11', 'Spouce': 'F12'}, ignore_index=True)

    df_copy_fam = df_copy_fam.append({'ID': 'F2', 'Husband ID': 'I19', 'Husband Name': 'Ned Stark',
                                      'Wife ID': 'I0', 'Wife Name': 'Cate Laniaster', 'Children': ['I20']}, ignore_index=True)

    # FAM ROLES
    for index, col in df_copy_indi.iterrows():
        child = col["Child"]
        spouse = col["Spouce"]
        if (child != 'NA' or spouse != 'NA'):
            if (child in fam_id_list or spouse in fam_id_list):
                entries_fam_roles.append(child)
                entries_fam_roles.append(spouse)
            else:
                error_indi.append("ERROR: INDIVIDUAL: US26: No corresponding entries for " +
                                  col["Name"] + " in the corresponding family records")

    # INDI ROLES
    for index, col in df_copy_fam.iterrows():
        children = col["Children"]
        husb_id = col["Husband ID"]
        wife_id = col["Wife ID"]
        if (children != 'NA' or husb_id != 'NA' or wife_id != 'NA'):
            if (children in indi_id_list or husb_id in indi_id_list or wife_id in indi_id_list):
                entries_indi_roles.append(children)
                entries_indi_roles.append(husb_id)
                entries_indi_roles.append(wife_id)

            else:
                error_fam.append("ERROR: FAMILY: US26: No corresponding entries for Husband Name: " +
                                 col["Husband Name"] + " and Wife Name: " + col["Wife Name"] + " in the corresponding individual records")

    error = error_indi + error_fam

    return error


us26Error = US26()
print(*us26Error, sep="\n")

######################### End of Chaitanya Pawar's Code #########################