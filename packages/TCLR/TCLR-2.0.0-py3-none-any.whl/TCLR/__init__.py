import datetime
now = datetime.datetime.now()
formatted_date_time = now.strftime('%Y-%m-%d %H:%M:%S')


print('Tree classifier for linear regression (TCLR)')
print('Author : Bin CAO (binjacobcao@gmail.com) ')
print('DOI : 10.20517/jmi.2022.04')
print('URL : https://github.com/Bin-Cao/TCLRmodel')
print('Executed on :',formatted_date_time)


"""
The entire feature space is divided into disjointed unit intervals by hyperplanes parallel to the coordinate axes.
In each partition, TCLR models target y as the function of a feature
TCLR choses the features and split-point to attain the best fit and recursive binary partitions the space,
until some stopping rules are applied.

Algorithm Patent No. : 2021SR1951267, China
Reference : Domain knowledge guided interpretive machine learning ——  Formula discovery for the oxidation behavior of Ferritic-Martensitic steels in supercritical water. Bin Cao et al., 2022, JMI, journal paper.
DOI : 10.20517/jmi.2022.04
"""