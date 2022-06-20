from datetime import datetime
import pandas as pd
import datetime
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

# User Story 17 : CP
# No marriages to children
def us17():
    df_copy = df_fam.copy()
    error = []
    for k in range(0, df_copy.shape[0]):
        for i, j in df_copy.iterrows():
            if df_copy['Husband ID'][i] in df_copy['Children'][k]:
                if df_copy['Wife ID'][i] == df_copy['Wife ID'][k]:
                    error.append("ERROR: " + "FAMILY: " + "US17: " + str(i) + ": " + " " +
                                 df_copy['ID'][i] + ": " + "Parent " + df_copy['Husband ID'][i] + " is married to their child : " + df_copy['Wife ID'][i])
                else:
                    continue
            elif df_copy['Wife ID'][i] in df_copy['Children'][k]:
                if df_copy['Husband ID'][i] == df_copy['Husband ID'][k]:
                    error.append("ERROR: " + "FAMILY: " + "US17: " + str(i) + ": " + " " +
                                 df_copy['ID'][i] + ": " + "Parent " + df_copy['Husband ID'][i] + " is married to their child : " + df_copy['Wife ID'][i])
                else:
                    continue
            else:
                continue
    return error


us17Error = us17()
print(*us17Error, sep="\n")


# User Story 18 : CP
# Siblings should not marry
def us18():
    df_copy = df_fam.copy()
    error = []
    for i, j in df_copy.iterrows():
        for item in df_copy['Children']:
            if df_copy['Husband ID'][i] in item:
                if df_copy['Wife ID'][i] in item:
                    error.append("ERROR: " + "FAMILY: " + "US18: " + str(i) + ": " + " " +
                                 df_copy['ID'][i] + ": " + "Siblings " + df_copy['Husband ID'][i] + " and " + df_copy['Wife ID'][i] + " are married")
                else:
                    continue
            else:
                continue
    return error


us18Error = us18()
print(*us18Error, sep="\n")

######################### End of Chaitanya Pawar's Code #########################

######################### Jonathan Kim's Code #########################

def US23():

    error = []
    for i in range(len(df_indi)):
        name = df_indi['Name'][i]
        birthday = df_indi['Birthday'][i]
        for j in range(len(df_indi)):
            if j == i:
                continue
            name_search = df_indi['Name'][j]
            birthday_search = df_indi['Birthday'][j]
            if name_search == name and birthday_search == birthday:
                error.append("ERROR: " + "INDIVIDUAL: " + "US23: " + str(i) + ": " + " individual "+ df_indi['ID'][i] + " and individual "+ df_indi['ID'][j] + " have the same name and birthday.")


    return error

US23Error = US23()
print(*US23Error, sep="\n")

def US24():

    error = []
    for i in range(len(df_fam)):
        husband = df_fam['Husband Name'][i]
        wife = df_fam['Wife Name'][i]
        marriage_date = df_fam['Married'][i]
        for j in range(len(df_fam)):
            if j == i:
                continue
            husband_search = df_fam['Husband Name'][j]
            wife_search = df_fam['Wife Name'][j]
            marriage_date_search = df_fam['Married'][j]
            if husband_search == husband and wife_search == wife and marriage_date_search == marriage_date:
                error.append("ERROR: " + "FAMILY: " + "US24: " + str(i) + ": " + " Fndividual "+ df_fam['ID'][i] + " and family "+ df_fam['ID'][j] + " have the same husband and wife name and marriage date.")

    return error
US24Error = US24()
print(*US24Error, sep="\n")

######################### End of Jonathan Kim's Code #########################
