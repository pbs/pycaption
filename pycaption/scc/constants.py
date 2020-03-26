# -*- coding: utf-8 -*-

from itertools import product

COMMANDS = {
    u'9420': u'',
    u'9429': u'',
    u'9425': u'',
    u'9426': u'',
    u'94a7': u'',
    u'942a': u'',
    u'94ab': u'',
    u'942c': u'',
    u'94ae': u'',
    u'942f': u'',
    u'9779': u'<$>{break}<$>',
    u'9775': u'<$>{break}<$>',
    u'9776': u'<$>{break}<$>',
    u'9770': u'<$>{break}<$>',
    u'9773': u'<$>{break}<$>',
    u'10c8': u'<$>{break}<$>',
    u'10c2': u'<$>{break}<$>',
    u'166e': u'<$>{break}<$>{italic}<$>',
    u'166d': u'<$>{break}<$>',
    u'166b': u'<$>{break}<$>',
    u'10c4': u'<$>{break}<$>',
    u'9473': u'<$>{break}<$>',
    u'977f': u'<$>{break}<$>',
    u'977a': u'<$>{break}<$>',
    u'1668': u'<$>{break}<$>',
    u'1667': u'<$>{break}<$>',
    u'1664': u'<$>{break}<$>',
    u'1661': u'<$>{break}<$>',
    u'10ce': u'<$>{break}<$>{italic}<$>',
    u'94c8': u'<$>{break}<$>',
    u'94c7': u'<$>{break}<$>',
    u'94c4': u'<$>{break}<$>',
    u'94c2': u'<$>{break}<$>',
    u'94c1': u'<$>{break}<$>',
    u'915e': u'<$>{break}<$>',
    u'915d': u'<$>{break}<$>',
    u'915b': u'<$>{break}<$>',
    u'925d': u'<$>{break}<$>',
    u'925e': u'<$>{break}<$>',
    u'925b': u'<$>{break}<$>',
    u'97e6': u'<$>{break}<$>',
    u'97e5': u'<$>{break}<$>',
    u'97e3': u'<$>{break}<$>',
    u'97e0': u'<$>{break}<$>',
    u'97e9': u'<$>{break}<$>',
    u'9154': u'<$>{break}<$>',
    u'9157': u'<$>{break}<$>',
    u'9151': u'<$>{break}<$>',
    u'9258': u'<$>{break}<$>',
    u'9152': u'<$>{break}<$>',
    u'9257': u'<$>{break}<$>',
    u'9254': u'<$>{break}<$>',
    u'9252': u'<$>{break}<$>',
    u'9158': u'<$>{break}<$>',
    u'9251': u'<$>{break}<$>',
    u'94cd': u'<$>{break}<$>',
    u'94ce': u'<$>{break}<$>{italic}<$>',
    u'94cb': u'<$>{break}<$>',
    u'97ef': u'<$>{break}<$>{italic}<$>',
    u'1373': u'<$>{break}<$>',
    u'97ec': u'<$>{break}<$>',
    u'97ea': u'<$>{break}<$>',
    u'15c7': u'<$>{break}<$>',
    u'974f': u'<$>{break}<$>{italic}<$>',
    u'10c1': u'<$>{break}<$>',
    u'974a': u'<$>{break}<$>',
    u'974c': u'<$>{break}<$>',
    u'10c7': u'<$>{break}<$>',
    u'976d': u'<$>{break}<$>',
    u'15d6': u'<$>{break}<$>',
    u'15d5': u'<$>{break}<$>',
    u'15d3': u'<$>{break}<$>',
    u'15d0': u'<$>{break}<$>',
    u'15d9': u'<$>{break}<$>',
    u'9745': u'<$>{break}<$>',
    u'9746': u'<$>{break}<$>',
    u'9740': u'<$>{break}<$>',
    u'9743': u'<$>{break}<$>',
    u'9749': u'<$>{break}<$>',
    u'15df': u'<$>{break}<$>',
    u'15dc': u'<$>{break}<$>',
    u'15da': u'<$>{break}<$>',
    u'15f8': u'<$>{break}<$>',
    u'94fe': u'<$>{break}<$>',
    u'94fd': u'<$>{break}<$>',
    u'94fc': u'<$>{break}<$>',
    u'94fb': u'<$>{break}<$>',
    u'944f': u'<$>{break}<$>{italic}<$>',
    u'944c': u'<$>{break}<$>',
    u'944a': u'<$>{break}<$>',
    u'92fc': u'<$>{break}<$>',
    u'1051': u'<$>{break}<$>',
    u'1052': u'<$>{break}<$>',
    u'1054': u'<$>{break}<$>',
    u'92fe': u'<$>{break}<$>',
    u'92fd': u'<$>{break}<$>',
    u'1058': u'<$>{break}<$>',
    u'157a': u'<$>{break}<$>',
    u'157f': u'<$>{break}<$>',
    u'9279': u'<$>{break}<$>',
    u'94f4': u'<$>{break}<$>',
    u'94f7': u'<$>{break}<$>',
    u'94f1': u'<$>{break}<$>',
    u'9449': u'<$>{break}<$>',
    u'92fb': u'<$>{break}<$>',
    u'9446': u'<$>{break}<$>',
    u'9445': u'<$>{break}<$>',
    u'9443': u'<$>{break}<$>',
    u'94f8': u'<$>{break}<$>',
    u'9440': u'<$>{break}<$>',
    u'1057': u'<$>{break}<$>',
    u'9245': u'<$>{break}<$>',
    u'92f2': u'<$>{break}<$>',
    u'1579': u'<$>{break}<$>',
    u'92f7': u'<$>{break}<$>',
    u'105e': u'<$>{break}<$>',
    u'92f4': u'<$>{break}<$>',
    u'1573': u'<$>{break}<$>',
    u'1570': u'<$>{break}<$>',
    u'1576': u'<$>{break}<$>',
    u'1575': u'<$>{break}<$>',
    u'16c1': u'<$>{break}<$>',
    u'16c2': u'<$>{break}<$>',
    u'9168': u'<$>{break}<$>',
    u'16c7': u'<$>{break}<$>',
    u'9164': u'<$>{break}<$>',
    u'9167': u'<$>{break}<$>',
    u'9161': u'<$>{break}<$>',
    u'9162': u'<$>{break}<$>',
    u'947f': u'<$>{break}<$>',
    u'91c2': u'<$>{break}<$>',
    u'91c1': u'<$>{break}<$>',
    u'91c7': u'<$>{break}<$>',
    u'91c4': u'<$>{break}<$>',
    u'13e3': u'<$>{break}<$>',
    u'91c8': u'<$>{break}<$>',
    u'91d0': u'<$>{break}<$>',
    u'13e5': u'<$>{break}<$>',
    u'13c8': u'<$>{break}<$>',
    u'16cb': u'<$>{break}<$>',
    u'16cd': u'<$>{break}<$>',
    u'16ce': u'<$>{break}<$>{italic}<$>',
    u'916d': u'<$>{break}<$>',
    u'916e': u'<$>{break}<$>{italic}<$>',
    u'916b': u'<$>{break}<$>',
    u'91d5': u'<$>{break}<$>',
    u'137a': u'<$>{break}<$>',
    u'91cb': u'<$>{break}<$>',
    u'91ce': u'<$>{break}<$>{italic}<$>',
    u'91cd': u'<$>{break}<$>',
    u'13ec': u'<$>{break}<$>',
    u'13c1': u'<$>{break}<$>',
    u'13ea': u'<$>{break}<$>',
    u'13ef': u'<$>{break}<$>{italic}<$>',
    u'94f2': u'<$>{break}<$>',
    u'97fb': u'<$>{break}<$>',
    u'97fc': u'<$>{break}<$>',
    u'1658': u'<$>{break}<$>',
    u'97fd': u'<$>{break}<$>',
    u'97fe': u'<$>{break}<$>',
    u'1652': u'<$>{break}<$>',
    u'1651': u'<$>{break}<$>',
    u'1657': u'<$>{break}<$>',
    u'1654': u'<$>{break}<$>',
    u'10cb': u'<$>{break}<$>',
    u'97f2': u'<$>{break}<$>',
    u'97f1': u'<$>{break}<$>',
    u'97f7': u'<$>{break}<$>',
    u'97f4': u'<$>{break}<$>',
    u'165b': u'<$>{break}<$>',
    u'97f8': u'<$>{break}<$>',
    u'165d': u'<$>{break}<$>',
    u'165e': u'<$>{break}<$>',
    u'15cd': u'<$>{break}<$>',
    u'10cd': u'<$>{break}<$>',
    u'9767': u'<$>{break}<$>',
    u'9249': u'<$>{break}<$>',
    u'1349': u'<$>{break}<$>',
    u'91d9': u'<$>{break}<$>',
    u'1340': u'<$>{break}<$>',
    u'91d3': u'<$>{break}<$>',
    u'9243': u'<$>{break}<$>',
    u'1343': u'<$>{break}<$>',
    u'91d6': u'<$>{break}<$>',
    u'1345': u'<$>{break}<$>',
    u'1346': u'<$>{break}<$>',
    u'9246': u'<$>{break}<$>',
    u'94e9': u'<$>{break}<$>',
    u'94e5': u'<$>{break}<$>',
    u'94e6': u'<$>{break}<$>',
    u'94e0': u'<$>{break}<$>',
    u'94e3': u'<$>{break}<$>',
    u'15ea': u'<$>{break}<$>',
    u'15ec': u'<$>{break}<$>',
    u'15ef': u'<$>{break}<$>{italic}<$>',
    u'16fe': u'<$>{break}<$>',
    u'16fd': u'<$>{break}<$>',
    u'16fc': u'<$>{break}<$>',
    u'16fb': u'<$>{break}<$>',
    u'1367': u'<$>{break}<$>',
    u'94ef': u'<$>{break}<$>{italic}<$>',
    u'94ea': u'<$>{break}<$>',
    u'94ec': u'<$>{break}<$>',
    u'924a': u'<$>{break}<$>',
    u'91dc': u'<$>{break}<$>',
    u'924c': u'<$>{break}<$>',
    u'91da': u'<$>{break}<$>',
    u'91df': u'<$>{break}<$>',
    u'134f': u'<$>{break}<$>{italic}<$>',
    u'924f': u'<$>{break}<$>{italic}<$>',
    u'16f8': u'<$>{break}<$>',
    u'16f7': u'<$>{break}<$>',
    u'16f4': u'<$>{break}<$>',
    u'16f2': u'<$>{break}<$>',
    u'16f1': u'<$>{break}<$>',
    u'15e0': u'<$>{break}<$>',
    u'15e3': u'<$>{break}<$>',
    u'15e5': u'<$>{break}<$>',
    u'15e6': u'<$>{break}<$>',
    u'15e9': u'<$>{break}<$>',
    u'9757': u'<$>{break}<$>',
    u'9754': u'<$>{break}<$>',
    u'9752': u'<$>{break}<$>',
    u'9751': u'<$>{break}<$>',
    u'9758': u'<$>{break}<$>',
    u'92f1': u'<$>{break}<$>',
    u'104c': u'<$>{break}<$>',
    u'104a': u'<$>{break}<$>',
    u'104f': u'<$>{break}<$>{italic}<$>',
    u'105d': u'<$>{break}<$>',
    u'92f8': u'<$>{break}<$>',
    u'975e': u'<$>{break}<$>',
    u'975d': u'<$>{break}<$>',
    u'975b': u'<$>{break}<$>',
    u'1043': u'<$>{break}<$>',
    u'1040': u'<$>{break}<$>',
    u'1046': u'<$>{break}<$>',
    u'1045': u'<$>{break}<$>',
    u'1049': u'<$>{break}<$>',
    u'9479': u'<$>{break}<$>',
    u'917f': u'<$>{break}<$>',
    u'9470': u'<$>{break}<$>',
    u'9476': u'<$>{break}<$>',
    u'917a': u'<$>{break}<$>',
    u'9475': u'<$>{break}<$>',
    u'927a': u'<$>{break}<$>',
    u'927f': u'<$>{break}<$>',
    u'134a': u'<$>{break}<$>',
    u'15fb': u'<$>{break}<$>',
    u'15fc': u'<$>{break}<$>',
    u'15fd': u'<$>{break}<$>',
    u'15fe': u'<$>{break}<$>',
    u'1546': u'<$>{break}<$>',
    u'1545': u'<$>{break}<$>',
    u'1543': u'<$>{break}<$>',
    u'1540': u'<$>{break}<$>',
    u'1549': u'<$>{break}<$>',
    u'13fd': u'<$>{break}<$>',
    u'13fe': u'<$>{break}<$>',
    u'13fb': u'<$>{break}<$>',
    u'13fc': u'<$>{break}<$>',
    u'92e9': u'<$>{break}<$>',
    u'92e6': u'<$>{break}<$>',
    u'9458': u'<$>{break}<$>',
    u'92e5': u'<$>{break}<$>',
    u'92e3': u'<$>{break}<$>',
    u'92e0': u'<$>{break}<$>',
    u'9270': u'<$>{break}<$>',
    u'9273': u'<$>{break}<$>',
    u'9275': u'<$>{break}<$>',
    u'9276': u'<$>{break}<$>',
    u'15f1': u'<$>{break}<$>',
    u'15f2': u'<$>{break}<$>',
    u'15f4': u'<$>{break}<$>',
    u'15f7': u'<$>{break}<$>',
    u'9179': u'<$>{break}<$>',
    u'9176': u'<$>{break}<$>',
    u'9175': u'<$>{break}<$>',
    u'947a': u'<$>{break}<$>',
    u'9173': u'<$>{break}<$>',
    u'9170': u'<$>{break}<$>',
    u'13f7': u'<$>{break}<$>',
    u'13f4': u'<$>{break}<$>',
    u'13f2': u'<$>{break}<$>',
    u'13f1': u'<$>{break}<$>',
    u'92ef': u'<$>{break}<$>{italic}<$>',
    u'92ec': u'<$>{break}<$>',
    u'13f8': u'<$>{break}<$>',
    u'92ea': u'<$>{break}<$>',
    u'154f': u'<$>{break}<$>{italic}<$>',
    u'154c': u'<$>{break}<$>',
    u'154a': u'<$>{break}<$>',
    u'16c4': u'<$>{break}<$>',
    u'16c8': u'<$>{break}<$>',
    u'97c8': u'<$>{break}<$>',
    u'164f': u'<$>{break}<$>{italic}<$>',
    u'164a': u'<$>{break}<$>',
    u'164c': u'<$>{break}<$>',
    u'1645': u'<$>{break}<$>',
    u'1646': u'<$>{break}<$>',
    u'1640': u'<$>{break}<$>',
    u'1643': u'<$>{break}<$>',
    u'1649': u'<$>{break}<$>',
    u'94df': u'<$>{break}<$>',
    u'94dc': u'<$>{break}<$>',
    u'94da': u'<$>{break}<$>',
    u'135b': u'<$>{break}<$>',
    u'135e': u'<$>{break}<$>',
    u'135d': u'<$>{break}<$>',
    u'1370': u'<$>{break}<$>',
    u'9240': u'<$>{break}<$>',
    u'13e9': u'<$>{break}<$>',
    u'1375': u'<$>{break}<$>',
    u'1679': u'<$>{break}<$>',
    u'1358': u'<$>{break}<$>',
    u'1352': u'<$>{break}<$>',
    u'1351': u'<$>{break}<$>',
    u'1376': u'<$>{break}<$>',
    u'1357': u'<$>{break}<$>',
    u'1354': u'<$>{break}<$>',
    u'1379': u'<$>{break}<$>',
    u'94d9': u'<$>{break}<$>',
    u'94d6': u'<$>{break}<$>',
    u'94d5': u'<$>{break}<$>',
    u'15462': u'<$>{break}<$>',
    u'94d3': u'<$>{break}<$>',
    u'94d0': u'<$>{break}<$>',
    u'13e0': u'<$>{break}<$>',
    u'13e6': u'<$>{break}<$>',
    u'976b': u'<$>{break}<$>',
    u'15c4': u'<$>{break}<$>',
    u'15c2': u'<$>{break}<$>',
    u'15c1': u'<$>{break}<$>',
    u'976e': u'<$>{break}<$>{italic}<$>',
    u'134c': u'<$>{break}<$>',
    u'15c8': u'<$>{break}<$>',
    u'92c8': u'<$>{break}<$>',
    u'16e9': u'<$>{break}<$>',
    u'16e3': u'<$>{break}<$>',
    u'16e0': u'<$>{break}<$>',
    u'16e6': u'<$>{break}<$>',
    u'16e5': u'<$>{break}<$>',
    u'91e5': u'<$>{break}<$>',
    u'91e6': u'<$>{break}<$>',
    u'91e0': u'<$>{break}<$>',
    u'91e3': u'<$>{break}<$>',
    u'13c4': u'<$>{break}<$>',
    u'13c7': u'<$>{break}<$>',
    u'91e9': u'<$>{break}<$>',
    u'13c2': u'<$>{break}<$>',
    u'9762': u'<$>{break}<$>',
    u'15ce': u'<$>{break}<$>{italic}<$>',
    u'9761': u'<$>{break}<$>',
    u'15cb': u'<$>{break}<$>',
    u'9764': u'<$>{break}<$>',
    u'9768': u'<$>{break}<$>',
    u'91ef': u'<$>{break}<$>{italic}<$>',
    u'91ea': u'<$>{break}<$>',
    u'91ec': u'<$>{break}<$>',
    u'13ce': u'<$>{break}<$>{italic}<$>',
    u'13cd': u'<$>{break}<$>',
    u'97da': u'<$>{break}<$>',
    u'13cb': u'<$>{break}<$>',
    u'13462': u'<$>{break}<$>',
    u'16ec': u'<$>{break}<$>',
    u'16ea': u'<$>{break}<$>',
    u'16ef': u'<$>{break}<$>{italic}<$>',
    u'97c1': u'<$>{break}<$>',
    u'97c2': u'<$>{break}<$>',
    u'97c4': u'<$>{break}<$>',
    u'97c7': u'<$>{break}<$>',
    u'92cd': u'<$>{break}<$>',
    u'92ce': u'<$>{break}<$>{italic}<$>',
    u'92cb': u'<$>{break}<$>',
    u'92da': u'<$>{break}<$>',
    u'92dc': u'<$>{break}<$>',
    u'92df': u'<$>{break}<$>',
    u'97df': u'<$>{break}<$>',
    u'155b': u'<$>{break}<$>',
    u'155e': u'<$>{break}<$>',
    u'155d': u'<$>{break}<$>',
    u'97dc': u'<$>{break}<$>',
    u'1675': u'<$>{break}<$>',
    u'1676': u'<$>{break}<$>',
    u'1670': u'<$>{break}<$>',
    u'1673': u'<$>{break}<$>',
    u'16462': u'<$>{break}<$>',
    u'97cb': u'<$>{break}<$>',
    u'97ce': u'<$>{break}<$>{italic}<$>',
    u'97cd': u'<$>{break}<$>',
    u'92c4': u'<$>{break}<$>',
    u'92c7': u'<$>{break}<$>',
    u'92c1': u'<$>{break}<$>',
    u'92c2': u'<$>{break}<$>',
    u'1551': u'<$>{break}<$>',
    u'97d5': u'<$>{break}<$>',
    u'97d6': u'<$>{break}<$>',
    u'1552': u'<$>{break}<$>',
    u'97d0': u'<$>{break}<$>',
    u'1554': u'<$>{break}<$>',
    u'1557': u'<$>{break}<$>',
    u'97d3': u'<$>{break}<$>',
    u'1558': u'<$>{break}<$>',
    u'167f': u'<$>{break}<$>',
    u'137f': u'<$>{break}<$>',
    u'167a': u'<$>{break}<$>',
    u'92d9': u'<$>{break}<$>',
    u'92d0': u'<$>{break}<$>',
    u'92d3': u'<$>{break}<$>',
    u'92d5': u'<$>{break}<$>',
    u'92d6': u'<$>{break}<$>',
    u'10dc': u'<$>{break}<$>',
    u'9262': u'<$>{break}<$>',
    u'9261': u'<$>{break}<$>',
    u'91f8': u'<$>{break}<$>',
    u'10df': u'<$>{break}<$>',
    u'9264': u'<$>{break}<$>',
    u'91f4': u'<$>{break}<$>',
    u'91f7': u'<$>{break}<$>',
    u'91f1': u'<$>{break}<$>',
    u'91f2': u'<$>{break}<$>',
    u'97d9': u'<$>{break}<$>',
    u'9149': u'<$>{break}<$>',
    u'9143': u'<$>{break}<$>',
    u'9140': u'<$>{break}<$>',
    u'9146': u'<$>{break}<$>',
    u'9145': u'<$>{break}<$>',
    u'9464': u'<$>{break}<$>',
    u'9467': u'<$>{break}<$>',
    u'9461': u'<$>{break}<$>',
    u'9462': u'<$>{break}<$>',
    u'9468': u'<$>{break}<$>',
    u'914c': u'<$>{break}<$>',
    u'914a': u'<$>{break}<$>',
    u'914f': u'<$>{break}<$>{italic}<$>',
    u'10d3': u'<$>{break}<$>',
    u'926b': u'<$>{break}<$>',
    u'10d0': u'<$>{break}<$>',
    u'10d6': u'<$>{break}<$>',
    u'926e': u'<$>{break}<$>{italic}<$>',
    u'926d': u'<$>{break}<$>',
    u'91fd': u'<$>{break}<$>',
    u'91fe': u'<$>{break}<$>',
    u'10d9': u'<$>{break}<$>',
    u'91fb': u'<$>{break}<$>',
    u'91fc': u'<$>{break}<$>',
    u'946e': u'<$>{break}<$>{italic}<$>',
    u'946d': u'<$>{break}<$>',
    u'946b': u'<$>{break}<$>',
    u'10da': u'<$>{break}<$>',
    u'10d5': u'<$>{break}<$>',
    u'9267': u'<$>{break}<$>',
    u'9268': u'<$>{break}<$>',
    u'16df': u'<$>{break}<$>',
    u'16da': u'<$>{break}<$>',
    u'16dc': u'<$>{break}<$>',
    u'9454': u'<$>{break}<$>',
    u'9457': u'<$>{break}<$>',
    u'9451': u'<$>{break}<$>',
    u'9452': u'<$>{break}<$>',
    u'136d': u'<$>{break}<$>',
    u'136e': u'<$>{break}<$>{italic}<$>',
    u'136b': u'<$>{break}<$>',
    u'13d9': u'<$>{break}<$>',
    u'13da': u'<$>{break}<$>',
    u'13dc': u'<$>{break}<$>',
    u'13df': u'<$>{break}<$>',
    u'1568': u'<$>{break}<$>',
    u'1561': u'<$>{break}<$>',
    u'1564': u'<$>{break}<$>',
    u'1567': u'<$>{break}<$>',
    u'16d5': u'<$>{break}<$>',
    u'16d6': u'<$>{break}<$>',
    u'16d0': u'<$>{break}<$>',
    u'16d3': u'<$>{break}<$>',
    u'945d': u'<$>{break}<$>',
    u'945e': u'<$>{break}<$>',
    u'16d9': u'<$>{break}<$>',
    u'945b': u'<$>{break}<$>',
    u'156b': u'<$>{break}<$>',
    u'156d': u'<$>{break}<$>',
    u'156e': u'<$>{break}<$>{italic}<$>',
    u'105b': u'<$>{break}<$>',
    u'1364': u'<$>{break}<$>',
    u'1368': u'<$>{break}<$>',
    u'1361': u'<$>{break}<$>',
    u'13d0': u'<$>{break}<$>',
    u'13d3': u'<$>{break}<$>',
    u'13d5': u'<$>{break}<$>',
    u'13d6': u'<$>{break}<$>',
    u'97a1': u'',
    u'97a2': u'',
    u'9723': u'',
    u'94a1': u'',
    u'94a4': u'',
    u'94ad': u'',
    u'1020': u'',
    u'10a1': u'',
    u'10a2': u'',
    u'1023': u'',
    u'10a4': u'',
    u'1025': u'',
    u'1026': u'',
    u'10a7': u'',
    u'10a8': u'',
    u'1029': u'',
    u'102a': u'',
    u'10ab': u'',
    u'102c': u'',
    u'10ad': u'',
    u'10ae': u'',
    u'102f': u'',
    u'97ad': u'',
    u'97a4': u'',
    u'9725': u'',
    u'9726': u'',
    u'97a7': u'',
    u'97a8': u'',
    u'9729': u'',
    u'972a': u'',
    u'9120': u'<$>{end-italic}<$>',
    u'91a1': u'',
    u'91a2': u'',
    u'9123': u'',
    u'91a4': u'',
    u'9125': u'',
    u'9126': u'',
    u'91a7': u'',
    u'91a8': u'',
    u'9129': u'',
    u'912a': u'',
    u'91ab': u'',
    u'912c': u'',
    u'91ad': u'',
    u'97ae': u'',
    u'972f': u'',
    u'91ae': u'<$>{italic}<$>',
    u'912f': u'<$>{italic}<$>',
    u'94a8': u'',
    u'9423': u'',
    u'94a2': u'',
}


CHARACTERS = {
    u'20': u' ',
    u'a1': u'!',
    u'a2': u'"',
    u'23': u'#',
    u'a4': u'$',
    u'25': u'%',
    u'26': u'&',
    u'a7': u'\'',
    u'a8': u'(',
    u'29': u')',
    u'2a': u'á',
    u'ab': u'+',
    u'2c': u',',
    u'ad': u'-',
    u'ae': u'.',
    u'2f': u'/',
    u'b0': u'0',
    u'31': u'1',
    u'32': u'2',
    u'b3': u'3',
    u'34': u'4',
    u'b5': u'5',
    u'b6': u'6',
    u'37': u'7',
    u'38': u'8',
    u'b9': u'9',
    u'ba': u':',
    u'3b': u';',
    u'bc': u'<',
    u'3d': u'=',
    u'3e': u'>',
    u'bf': u'?',
    u'40': u'@',
    u'c1': u'A',
    u'c2': u'B',
    u'43': u'C',
    u'c4': u'D',
    u'45': u'E',
    u'46': u'F',
    u'c7': u'G',
    u'c8': u'H',
    u'49': u'I',
    u'4a': u'J',
    u'cb': u'K',
    u'4c': u'L',
    u'cd': u'M',
    u'ce': u'N',
    u'4f': u'O',
    u'd0': u'P',
    u'51': u'Q',
    u'52': u'R',
    u'd3': u'S',
    u'54': u'T',
    u'd5': u'U',
    u'd6': u'V',
    u'57': u'W',
    u'58': u'X',
    u'd9': u'Y',
    u'da': u'Z',
    u'5b': u'[',
    u'dc': u'é',
    u'5d': u']',
    u'5e': u'í',
    u'df': u'ó',
    u'e0': u'ú',
    u'61': u'a',
    u'62': u'b',
    u'e3': u'c',
    u'64': u'd',
    u'e5': u'e',
    u'e6': u'f',
    u'67': u'g',
    u'68': u'h',
    u'e9': u'i',
    u'ea': u'j',
    u'6b': u'k',
    u'ec': u'l',
    u'6d': u'm',
    u'6e': u'n',
    u'ef': u'o',
    u'70': u'p',
    u'f1': u'q',
    u'f2': u'r',
    u'73': u's',
    u'f4': u't',
    u'75': u'u',
    u'76': u'v',
    u'f7': u'w',
    u'f8': u'x',
    u'79': u'y',
    u'7a': u'z',
    u'fb': u'ç',
    u'7c': u'÷',
    u'fd': u'Ñ',
    u'fe': u'ñ',
    u'7f': u'',
    u'80': u''
}


SPECIAL_CHARS = {
    u'91b0': u'®',
    u'9131': u'°',
    u'9132': u'½',
    u'91b3': u'¿',
    u'91b4': u'™',
    u'91b5': u'¢',
    u'91b6': u'£',
    u'9137': u'♪',
    u'9138': u'à',
    u'91b9': u' ',
    u'91ba': u'è',
    u'913b': u'â',
    u'91bc': u'ê',
    u'913d': u'î',
    u'913e': u'ô',
    u'91bf': u'û'
}


EXTENDED_CHARS = {
    u'9220': u'Á',
    u'92a1': u'É',
    u'92a2': u'Ó',
    u'9223': u'Ú',
    u'92a4': u'Ü',
    u'9225': u'ü',
    u'9226': u'‘',
    u'92a7': u'¡',
    u'92a8': u'*',
    u'9229': u'’',
    u'922a': u'—',
    u'92ab': u'©',
    u'922c': u'℠',
    u'92ad': u'•',
    u'92ae': u'“',
    u'922f': u'”',
    u'92b0': u'À',
    u'9231': u'Â',
    u'9232': u'Ç',
    u'92b3': u'È',
    u'9234': u'Ê',
    u'92b5': u'Ë',
    u'92b6': u'ë',
    u'9237': u'Î',
    u'9238': u'Ï',
    u'92b9': u'ï',
    u'92ba': u'Ô',
    u'923b': u'Ù',
    u'92bc': u'ù',
    u'923d': u'Û',
    u'923e': u'«',
    u'92bf': u'»',
    u'1320': u'Ã',
    u'13a1': u'ã',
    u'13a2': u'Í',
    u'1323': u'Ì',
    u'13a4': u'ì',
    u'1325': u'Ò',
    u'1326': u'ò',
    u'13a7': u'Õ',
    u'13a8': u'õ',
    u'1329': u'{',
    u'132a': u'}',
    u'13ab': u'\\',
    u'132c': u'^',
    u'13ad': u'_',
    u'13ae': u'¦',
    u'132f': u'~',
    u'13b0': u'Ä',
    u'1331': u'ä',
    u'1332': u'Ö',
    u'13b3': u'ö',
    u'1334': u'ß',
    u'13b5': u'¥',
    u'13b6': u'¤',
    u'1337': u'|',
    u'1338': u'Å',
    u'13b9': u'å',
    u'13ba': u'Ø',
    u'133b': u'ø',
    u'13bc': u'┌',
    u'133d': u'┐',
    u'133e': u'└',
    u'13bf': u'┘',
}


# Cursor positioning codes
PAC_HIGH_BYTE_BY_ROW = [
    u'xx',
    u'91',
    u'91',
    u'92',
    u'92',
    u'15',
    u'15',
    u'16',
    u'16',
    u'97',
    u'97',
    u'10',
    u'13',
    u'13',
    u'94',
    u'94'
]
PAC_LOW_BYTE_BY_ROW_RESTRICTED = [
    u'xx',
    u'd0',
    u'70',
    u'd0',
    u'70',
    u'd0',
    u'70',
    u'd0',
    u'70',
    u'd0',
    u'70',
    u'd0',
    u'd0',
    u'70',
    u'd0',
    u'70'
]

# High order bytes come first, then each key contains a list of low bytes.
# Any of the values in that list, coupled with the high order byte will
# map to the (row, column) tuple.
# This particular dictionary will get transformed to a more suitable form for
# usage like PAC_BYTES_TO_POSITIONING_MAP[u'91'][u'd6'] = (1, 12)
PAC_BYTES_TO_POSITIONING_MAP = {
    u'91': {
        (u'd0', u'51', u'c2', u'43', u'c4', u'45', u'46', u'c7', u'c8', u'49', u'4a', u'cb', u'4c', u'cd'): (1, 0),  # noqa
        (u'70', u'f1', u'62', u'e3', u'64', u'e5', u'e6', u'67', u'68', u'e9', u'ea', u'6b', u'ec', u'6d'): (2, 0),  # noqa
        (u'52', u'd3'): (1, 4),
        (u'54', u'd5'): (1, 8),
        (u'd6', u'57'): (1, 12),
        (u'58', u'd9'): (1, 16),
        (u'da', u'5b'): (1, 20),
        (u'dc', u'5d'): (1, 24),
        (u'5e', u'df'): (1, 28),

        (u'f2', u'73'): (2, 4),
        (u'f4', u'75'): (2, 8),
        (u'76', u'f7'): (2, 12),
        (u'f8', u'79'): (2, 16),
        (u'7a', u'fb'): (2, 20),
        (u'7c', u'fd'): (2, 24),
        (u'fe', u'7f'): (2, 28)
    },
    u'92': {
        (u'd0', u'51', u'c2', u'43', u'c4', u'45', u'46', u'c7', u'c8', u'49', u'4a', u'cb', u'4c', u'cd'): (3, 0),  # noqa
        (u'70', u'f1', u'62', u'e3', u'64', u'e5', u'e6', u'67', u'68', u'e9', u'ea', u'6b', u'ec', u'6d'): (4, 0),  # noqa
        (u'52', u'd3'): (3, 4),
        (u'54', u'd5'): (3, 8),
        (u'd6', u'57'): (3, 12),
        (u'58', u'd9'): (3, 16),
        (u'da', u'5b'): (3, 20),
        (u'dc', u'5d'): (3, 24),
        (u'5e', u'df'): (3, 28),

        (u'f2', u'73'): (4, 4),
        (u'f4', u'75'): (4, 8),
        (u'76', u'f7'): (4, 12),
        (u'f8', u'79'): (4, 16),
        (u'7a', u'fb'): (4, 20),
        (u'7c', u'fd'): (4, 24),
        (u'fe', u'7f'): (4, 28)
    },
    u'15': {
        (u'd0', u'51', u'c2', u'43', u'c4', u'45', u'46', u'c7', u'c8', u'49', u'4a', u'cb', u'4c', u'cd'): (5, 0),  # noqa
        (u'70', u'f1', u'62', u'e3', u'64', u'e5', u'e6', u'67', u'68', u'e9', u'ea', u'6b', u'ec', u'6d'): (6, 0),  # noqa
        (u'52', u'd3'): (5, 4),
        (u'54', u'd5'): (5, 8),
        (u'd6', u'57'): (5, 12),
        (u'58', u'd9'): (5, 16),
        (u'da', u'5b'): (5, 20),
        (u'dc', u'5d'): (5, 24),
        (u'5e', u'df'): (5, 28),

        (u'f2', u'73'): (6, 4),
        (u'f4', u'75'): (6, 8),
        (u'76', u'f7'): (6, 12),
        (u'f8', u'79'): (6, 16),
        (u'7a', u'fb'): (6, 20),
        (u'7c', u'fd'): (6, 24),
        (u'fe', u'7f'): (6, 28)
    },
    u'16': {
        (u'd0', u'51', u'c2', u'43', u'c4', u'45', u'46', u'c7', u'c8', u'49', u'4a', u'cb', u'4c', u'cd'): (7, 0),  # noqa
        (u'70', u'f1', u'62', u'e3', u'64', u'e5', u'e6', u'67', u'68', u'e9', u'ea', u'6b', u'ec', u'6d'): (8, 0),  # noqa
        (u'52', u'd3'): (7, 4),
        (u'54', u'd5'): (7, 8),
        (u'd6', u'57'): (7, 12),
        (u'58', u'd9'): (7, 16),
        (u'da', u'5b'): (7, 20),
        (u'dc', u'5d'): (7, 24),
        (u'5e', u'df'): (7, 28),

        (u'f2', u'73'): (8, 4),
        (u'f4', u'75'): (8, 8),
        (u'76', u'f7'): (8, 12),
        (u'f8', u'79'): (8, 16),
        (u'7a', u'fb'): (8, 20),
        (u'7c', u'fd'): (8, 24),
        (u'fe', u'7f'): (8, 28)
    },
    u'97': {
        (u'd0', u'51', u'c2', u'43', u'c4', u'45', u'46', u'c7', u'c8', u'49', u'4a', u'cb', u'4c', u'cd'): (9, 0),  # noqa
        (u'70', u'f1', u'62', u'e3', u'64', u'e5', u'e6', u'67', u'68', u'e9', u'ea', u'6b', u'ec', u'6d'): (10, 0),  # noqa
        (u'52', u'd3'): (9, 4),
        (u'54', u'd5'): (9, 8),
        (u'd6', u'57'): (9, 12),
        (u'58', u'd9'): (9, 16),
        (u'da', u'5b'): (9, 20),
        (u'dc', u'5d'): (9, 24),
        (u'5e', u'df'): (9, 28),

        (u'f2', u'73'): (10, 4),
        (u'f4', u'75'): (10, 8),
        (u'76', u'f7'): (10, 12),
        (u'f8', u'79'): (10, 16),
        (u'7a', u'fb'): (10, 20),
        (u'7c', u'fd'): (10, 24),
        (u'fe', u'7f'): (10, 28)
    },
    u'10': {
        (u'd0', u'51', u'c2', u'43', u'c4', u'45', u'46', u'c7', u'c8', u'49', u'4a', u'cb', u'4c', u'cd'): (11, 0),  # noqa
        (u'52', u'd3'): (11, 4),
        (u'54', u'd5'): (11, 8),
        (u'd6', u'57'): (11, 12),
        (u'58', u'd9'): (11, 16),
        (u'da', u'5b'): (11, 20),
        (u'dc', u'5d'): (11, 24),
        (u'5e', u'df'): (11, 28),
    },
    u'13': {
        (u'd0', u'51', u'c2', u'43', u'c4', u'45', u'46', u'c7', u'c8', u'49', u'4a', u'cb', u'4c', u'cd'): (12, 0),  # noqa
        (u'70', u'f1', u'62', u'e3', u'64', u'e5', u'e6', u'67', u'68', u'e9', u'ea', u'6b', u'ec', u'6d'): (13, 0),  # noqa
        (u'52', u'd3'): (12, 4),
        (u'54', u'd5'): (12, 8),
        (u'd6', u'57'): (12, 12),
        (u'58', u'd9'): (12, 16),
        (u'da', u'5b'): (12, 20),
        (u'dc', u'5d'): (12, 24),
        (u'5e', u'df'): (12, 28),

        (u'f2', u'73'): (13, 4),
        (u'f4', u'75'): (13, 8),
        (u'76', u'f7'): (13, 12),
        (u'f8', u'79'): (13, 16),
        (u'7a', u'fb'): (13, 20),
        (u'7c', u'fd'): (13, 24),
        (u'fe', u'7f'): (13, 28)
    },
    u'94': {
        (u'd0', u'51', u'c2', u'43', u'c4', u'45', u'46', u'c7', u'c8', u'49', u'4a', u'cb', u'4c', u'cd'): (14, 0),  # noqa
        (u'70', u'f1', u'62', u'e3', u'64', u'e5', u'e6', u'67', u'68', u'e9', u'ea', u'6b', u'ec', u'6d'): (15, 0),  # noqa
        (u'52', u'd3'): (14, 4),
        (u'54', u'd5'): (14, 8),
        (u'd6', u'57'): (14, 12),
        (u'58', u'd9'): (14, 16),
        (u'da', u'5b'): (14, 20),
        (u'dc', u'5d'): (14, 24),
        (u'5e', u'df'): (14, 28),

        (u'f2', u'73'): (15, 4),
        (u'f4', u'75'): (15, 8),
        (u'76', u'f7'): (15, 12),
        (u'f8', u'79'): (15, 16),
        (u'7a', u'fb'): (15, 20),
        (u'7c', u'fd'): (15, 24),
        (u'fe', u'7f'): (15, 28)
    }
}


def _create_position_to_bytes_map(bytes_to_pos):
    result = {}
    for high_byte, low_byte_dict in list(bytes_to_pos.items()):

        # must contain mappings to column, to the tuple of possible values
        for low_byte_list in list(low_byte_dict.keys()):
            column = bytes_to_pos[high_byte][low_byte_list][1]

            row = bytes_to_pos[high_byte][low_byte_list][0]
            if row not in result:
                result[row] = {}

            result[row][column] = (
                tuple(product([high_byte], low_byte_list)))
    return result

# (Almost) the reverse of PAC_BYTES_TO_POSITIONING_MAP. Call with arguments
# like for example [15][4] to get the tuple ((u'94', u'f2'), (u'94', u'73'))
POSITIONING_TO_PAC_MAP = _create_position_to_bytes_map(
    PAC_BYTES_TO_POSITIONING_MAP
)


def _restructure_bytes_to_position_map(byte_to_pos_map):
    return {
        k_: {
            low_byte: byte_to_pos_map[k_][low_byte_list]
            for low_byte_list in list(v_.keys()) for low_byte in low_byte_list
        }
        for k_, v_ in list(byte_to_pos_map.items())
    }

# Now use the dict with arguments like [u'91'][u'75'] directly.
PAC_BYTES_TO_POSITIONING_MAP = _restructure_bytes_to_position_map(
    PAC_BYTES_TO_POSITIONING_MAP)


# Inverted character lookup
CHARACTER_TO_CODE = {
    character: code
    for code, character in CHARACTERS.items()
}

SPECIAL_OR_EXTENDED_CHAR_TO_CODE = {
    character: code for code, character in EXTENDED_CHARS.items()
}
SPECIAL_OR_EXTENDED_CHAR_TO_CODE.update(
    {character: code for code, character in SPECIAL_CHARS.items()}
)

# Time to transmit a single codeword = 1 second / 29.97
MICROSECONDS_PER_CODEWORD = 1000.0 * 1000.0 / (30.0 * 1000.0 / 1001.0)


HEADER = u'Scenarist_SCC V1.0'
