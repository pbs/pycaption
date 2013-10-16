#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from pycaption import BaseReader, Caption, CaptionSet, CaptionNode

COMMANDS = {
    '9420': u'',
    '9429': u'',
    '9425': u'',
    '9426': u'',
    '94a7': u'',
    '942a': u'',
    '94ab': u'',
    '942c': u'',
    '94ae': u'',
    '942f': u'',
    '9779': u'<$>{break}<$>',
    '9775': u'<$>{break}<$>',
    '9776': u'<$>{break}<$>',
    '9770': u'<$>{break}<$>',
    '9773': u'<$>{break}<$>',
    '10c8': u'<$>{break}<$>',
    '10c2': u'<$>{break}<$>',
    '166e': u'<$>{break}<$>{italic}<$>',
    '166d': u'<$>{break}<$>',
    '166b': u'<$>{break}<$>',
    '10c4': u'<$>{break}<$>',
    '9473': u'<$>{break}<$>',
    '977f': u'<$>{break}<$>',
    '977a': u'<$>{break}<$>',
    '1668': u'<$>{break}<$>',
    '1667': u'<$>{break}<$>',
    '1664': u'<$>{break}<$>',
    '1661': u'<$>{break}<$>',
    '10ce': u'<$>{break}<$>{italic}<$>',
    '94c8': u'<$>{break}<$>',
    '94c7': u'<$>{break}<$>',
    '94c4': u'<$>{break}<$>',
    '94c2': u'<$>{break}<$>',
    '94c1': u'<$>{break}<$>',
    '915e': u'<$>{break}<$>',
    '915d': u'<$>{break}<$>',
    '915b': u'<$>{break}<$>',
    '925d': u'<$>{break}<$>',
    '925e': u'<$>{break}<$>',
    '925b': u'<$>{break}<$>',
    '97e6': u'<$>{break}<$>',
    '97e5': u'<$>{break}<$>',
    '97e3': u'<$>{break}<$>',
    '97e0': u'<$>{break}<$>',
    '97e9': u'<$>{break}<$>',
    '9154': u'<$>{break}<$>',
    '9157': u'<$>{break}<$>',
    '9151': u'<$>{break}<$>',
    '9258': u'<$>{break}<$>',
    '9152': u'<$>{break}<$>',
    '9257': u'<$>{break}<$>',
    '9254': u'<$>{break}<$>',
    '9252': u'<$>{break}<$>',
    '9158': u'<$>{break}<$>',
    '9251': u'<$>{break}<$>',
    '94cd': u'<$>{break}<$>',
    '94ce': u'<$>{break}<$>{italic}<$>',
    '94cb': u'<$>{break}<$>',
    '97ef': u'<$>{break}<$>{italic}<$>',
    '1373': u'<$>{break}<$>',
    '97ec': u'<$>{break}<$>',
    '97ea': u'<$>{break}<$>',
    '15c7': u'<$>{break}<$>',
    '974f': u'<$>{break}<$>{italic}<$>',
    '10c1': u'<$>{break}<$>',
    '974a': u'<$>{break}<$>',
    '974c': u'<$>{break}<$>',
    '10c7': u'<$>{break}<$>',
    '976d': u'<$>{break}<$>',
    '15d6': u'<$>{break}<$>',
    '15d5': u'<$>{break}<$>',
    '15d3': u'<$>{break}<$>',
    '15d0': u'<$>{break}<$>',
    '15d9': u'<$>{break}<$>',
    '9745': u'<$>{break}<$>',
    '9746': u'<$>{break}<$>',
    '9740': u'<$>{break}<$>',
    '9743': u'<$>{break}<$>',
    '9749': u'<$>{break}<$>',
    '15df': u'<$>{break}<$>',
    '15dc': u'<$>{break}<$>',
    '15da': u'<$>{break}<$>',
    '15f8': u'<$>{break}<$>',
    '94fe': u'<$>{break}<$>',
    '94fd': u'<$>{break}<$>',
    '94fc': u'<$>{break}<$>',
    '94fb': u'<$>{break}<$>',
    '944f': u'<$>{break}<$>{italic}<$>',
    '944c': u'<$>{break}<$>',
    '944a': u'<$>{break}<$>',
    '92fc': u'<$>{break}<$>',
    '1051': u'<$>{break}<$>',
    '1052': u'<$>{break}<$>',
    '1054': u'<$>{break}<$>',
    '92fe': u'<$>{break}<$>',
    '92fd': u'<$>{break}<$>',
    '1058': u'<$>{break}<$>',
    '157a': u'<$>{break}<$>',
    '157f': u'<$>{break}<$>',
    '9279': u'<$>{break}<$>',
    '94f4': u'<$>{break}<$>',
    '94f7': u'<$>{break}<$>',
    '94f1': u'<$>{break}<$>',
    '9449': u'<$>{break}<$>',
    '92fb': u'<$>{break}<$>',
    '9446': u'<$>{break}<$>',
    '9445': u'<$>{break}<$>',
    '9443': u'<$>{break}<$>',
    '94f8': u'<$>{break}<$>',
    '9440': u'<$>{break}<$>',
    '1057': u'<$>{break}<$>',
    '9245': u'<$>{break}<$>',
    '92f2': u'<$>{break}<$>',
    '1579': u'<$>{break}<$>',
    '92f7': u'<$>{break}<$>',
    '105e': u'<$>{break}<$>',
    '92f4': u'<$>{break}<$>',
    '1573': u'<$>{break}<$>',
    '1570': u'<$>{break}<$>',
    '1576': u'<$>{break}<$>',
    '1575': u'<$>{break}<$>',
    '16c1': u'<$>{break}<$>',
    '16c2': u'<$>{break}<$>',
    '9168': u'<$>{break}<$>',
    '16c7': u'<$>{break}<$>',
    '9164': u'<$>{break}<$>',
    '9167': u'<$>{break}<$>',
    '9161': u'<$>{break}<$>',
    '9162': u'<$>{break}<$>',
    '947f': u'<$>{break}<$>',
    '91c2': u'<$>{break}<$>',
    '91c1': u'<$>{break}<$>',
    '91c7': u'<$>{break}<$>',
    '91c4': u'<$>{break}<$>',
    '13e3': u'<$>{break}<$>',
    '91c8': u'<$>{break}<$>',
    '91d0': u'<$>{break}<$>',
    '13e5': u'<$>{break}<$>',
    '13c8': u'<$>{break}<$>',
    '16cb': u'<$>{break}<$>',
    '16cd': u'<$>{break}<$>',
    '16ce': u'<$>{break}<$>{italic}<$>',
    '916d': u'<$>{break}<$>',
    '916e': u'<$>{break}<$>{italic}<$>',
    '916b': u'<$>{break}<$>',
    '91d5': u'<$>{break}<$>',
    '137a': u'<$>{break}<$>',
    '91cb': u'<$>{break}<$>',
    '91ce': u'<$>{break}<$>{italic}<$>',
    '91cd': u'<$>{break}<$>',
    '13ec': u'<$>{break}<$>',
    '13c1': u'<$>{break}<$>',
    '13ea': u'<$>{break}<$>',
    '13ef': u'<$>{break}<$>{italic}<$>',
    '94f2': u'<$>{break}<$>',
    '97fb': u'<$>{break}<$>',
    '97fc': u'<$>{break}<$>',
    '1658': u'<$>{break}<$>',
    '97fd': u'<$>{break}<$>',
    '97fe': u'<$>{break}<$>',
    '1652': u'<$>{break}<$>',
    '1651': u'<$>{break}<$>',
    '1657': u'<$>{break}<$>',
    '1654': u'<$>{break}<$>',
    '10cb': u'<$>{break}<$>',
    '97f2': u'<$>{break}<$>',
    '97f1': u'<$>{break}<$>',
    '97f7': u'<$>{break}<$>',
    '97f4': u'<$>{break}<$>',
    '165b': u'<$>{break}<$>',
    '97f8': u'<$>{break}<$>',
    '165d': u'<$>{break}<$>',
    '165e': u'<$>{break}<$>',
    '15cd': u'<$>{break}<$>',
    '10cd': u'<$>{break}<$>',
    '9767': u'<$>{break}<$>',
    '9249': u'<$>{break}<$>',
    '1349': u'<$>{break}<$>',
    '91d9': u'<$>{break}<$>',
    '1340': u'<$>{break}<$>',
    '91d3': u'<$>{break}<$>',
    '9243': u'<$>{break}<$>',
    '1343': u'<$>{break}<$>',
    '91d6': u'<$>{break}<$>',
    '1345': u'<$>{break}<$>',
    '1346': u'<$>{break}<$>',
    '9246': u'<$>{break}<$>',
    '94e9': u'<$>{break}<$>',
    '94e5': u'<$>{break}<$>',
    '94e6': u'<$>{break}<$>',
    '94e0': u'<$>{break}<$>',
    '94e3': u'<$>{break}<$>',
    '15ea': u'<$>{break}<$>',
    '15ec': u'<$>{break}<$>',
    '15ef': u'<$>{break}<$>{italic}<$>',
    '16fe': u'<$>{break}<$>',
    '16fd': u'<$>{break}<$>',
    '16fc': u'<$>{break}<$>',
    '16fb': u'<$>{break}<$>',
    '1367': u'<$>{break}<$>',
    '94ef': u'<$>{break}<$>{italic}<$>',
    '94ea': u'<$>{break}<$>',
    '94ec': u'<$>{break}<$>',
    '924a': u'<$>{break}<$>',
    '91dc': u'<$>{break}<$>',
    '924c': u'<$>{break}<$>',
    '91da': u'<$>{break}<$>',
    '91df': u'<$>{break}<$>',
    '134f': u'<$>{break}<$>{italic}<$>',
    '924f': u'<$>{break}<$>{italic}<$>',
    '16f8': u'<$>{break}<$>',
    '16f7': u'<$>{break}<$>',
    '16f4': u'<$>{break}<$>',
    '16f2': u'<$>{break}<$>',
    '16f1': u'<$>{break}<$>',
    '15e0': u'<$>{break}<$>',
    '15e3': u'<$>{break}<$>',
    '15e5': u'<$>{break}<$>',
    '15e6': u'<$>{break}<$>',
    '15e9': u'<$>{break}<$>',
    '9757': u'<$>{break}<$>',
    '9754': u'<$>{break}<$>',
    '9752': u'<$>{break}<$>',
    '9751': u'<$>{break}<$>',
    '9758': u'<$>{break}<$>',
    '92f1': u'<$>{break}<$>',
    '104c': u'<$>{break}<$>',
    '104a': u'<$>{break}<$>',
    '104f': u'<$>{break}<$>{italic}<$>',
    '105d': u'<$>{break}<$>',
    '92f8': u'<$>{break}<$>',
    '975e': u'<$>{break}<$>',
    '975d': u'<$>{break}<$>',
    '975b': u'<$>{break}<$>',
    '1043': u'<$>{break}<$>',
    '1040': u'<$>{break}<$>',
    '1046': u'<$>{break}<$>',
    '1045': u'<$>{break}<$>',
    '1049': u'<$>{break}<$>',
    '9479': u'<$>{break}<$>',
    '917f': u'<$>{break}<$>',
    '9470': u'<$>{break}<$>',
    '9476': u'<$>{break}<$>',
    '917a': u'<$>{break}<$>',
    '9475': u'<$>{break}<$>',
    '927a': u'<$>{break}<$>',
    '927f': u'<$>{break}<$>',
    '134a': u'<$>{break}<$>',
    '15fb': u'<$>{break}<$>',
    '15fc': u'<$>{break}<$>',
    '15fd': u'<$>{break}<$>',
    '15fe': u'<$>{break}<$>',
    '1546': u'<$>{break}<$>',
    '1545': u'<$>{break}<$>',
    '1543': u'<$>{break}<$>',
    '1540': u'<$>{break}<$>',
    '1549': u'<$>{break}<$>',
    '13fd': u'<$>{break}<$>',
    '13fe': u'<$>{break}<$>',
    '13fb': u'<$>{break}<$>',
    '13fc': u'<$>{break}<$>',
    '92e9': u'<$>{break}<$>',
    '92e6': u'<$>{break}<$>',
    '9458': u'<$>{break}<$>',
    '92e5': u'<$>{break}<$>',
    '92e3': u'<$>{break}<$>',
    '92e0': u'<$>{break}<$>',
    '9270': u'<$>{break}<$>',
    '9273': u'<$>{break}<$>',
    '9275': u'<$>{break}<$>',
    '9276': u'<$>{break}<$>',
    '15f1': u'<$>{break}<$>',
    '15f2': u'<$>{break}<$>',
    '15f4': u'<$>{break}<$>',
    '15f7': u'<$>{break}<$>',
    '9179': u'<$>{break}<$>',
    '9176': u'<$>{break}<$>',
    '9175': u'<$>{break}<$>',
    '947a': u'<$>{break}<$>',
    '9173': u'<$>{break}<$>',
    '9170': u'<$>{break}<$>',
    '13f7': u'<$>{break}<$>',
    '13f4': u'<$>{break}<$>',
    '13f2': u'<$>{break}<$>',
    '13f1': u'<$>{break}<$>',
    '92ef': u'<$>{break}<$>{italic}<$>',
    '92ec': u'<$>{break}<$>',
    '13f8': u'<$>{break}<$>',
    '92ea': u'<$>{break}<$>',
    '154f': u'<$>{break}<$>{italic}<$>',
    '154c': u'<$>{break}<$>',
    '154a': u'<$>{break}<$>',
    '16c4': u'<$>{break}<$>',
    '16c8': u'<$>{break}<$>',
    '97c8': u'<$>{break}<$>',
    '164f': u'<$>{break}<$>{italic}<$>',
    '164a': u'<$>{break}<$>',
    '164c': u'<$>{break}<$>',
    '1645': u'<$>{break}<$>',
    '1646': u'<$>{break}<$>',
    '1640': u'<$>{break}<$>',
    '1643': u'<$>{break}<$>',
    '1649': u'<$>{break}<$>',
    '94df': u'<$>{break}<$>',
    '94dc': u'<$>{break}<$>',
    '94da': u'<$>{break}<$>',
    '135b': u'<$>{break}<$>',
    '135e': u'<$>{break}<$>',
    '135d': u'<$>{break}<$>',
    '1370': u'<$>{break}<$>',
    '9240': u'<$>{break}<$>',
    '13e9': u'<$>{break}<$>',
    '1375': u'<$>{break}<$>',
    '1679': u'<$>{break}<$>',
    '1358': u'<$>{break}<$>',
    '1352': u'<$>{break}<$>',
    '1351': u'<$>{break}<$>',
    '1376': u'<$>{break}<$>',
    '1357': u'<$>{break}<$>',
    '1354': u'<$>{break}<$>',
    '1379': u'<$>{break}<$>',
    '94d9': u'<$>{break}<$>',
    '94d6': u'<$>{break}<$>',
    '94d5': u'<$>{break}<$>',
    '15462': u'<$>{break}<$>',
    '94d3': u'<$>{break}<$>',
    '94d0': u'<$>{break}<$>',
    '13e0': u'<$>{break}<$>',
    '13e6': u'<$>{break}<$>',
    '976b': u'<$>{break}<$>',
    '15c4': u'<$>{break}<$>',
    '15c2': u'<$>{break}<$>',
    '15c1': u'<$>{break}<$>',
    '976e': u'<$>{break}<$>{italic}<$>',
    '134c': u'<$>{break}<$>',
    '15c8': u'<$>{break}<$>',
    '92c8': u'<$>{break}<$>',
    '16e9': u'<$>{break}<$>',
    '16e3': u'<$>{break}<$>',
    '16e0': u'<$>{break}<$>',
    '16e6': u'<$>{break}<$>',
    '16e5': u'<$>{break}<$>',
    '91e5': u'<$>{break}<$>',
    '91e6': u'<$>{break}<$>',
    '91e0': u'<$>{break}<$>',
    '91e3': u'<$>{break}<$>',
    '13c4': u'<$>{break}<$>',
    '13c7': u'<$>{break}<$>',
    '91e9': u'<$>{break}<$>',
    '13c2': u'<$>{break}<$>',
    '9762': u'<$>{break}<$>',
    '15ce': u'<$>{break}<$>{italic}<$>',
    '9761': u'<$>{break}<$>',
    '15cb': u'<$>{break}<$>',
    '9764': u'<$>{break}<$>',
    '9768': u'<$>{break}<$>',
    '91ef': u'<$>{break}<$>{italic}<$>',
    '91ea': u'<$>{break}<$>',
    '91ec': u'<$>{break}<$>',
    '13ce': u'<$>{break}<$>{italic}<$>',
    '13cd': u'<$>{break}<$>',
    '97da': u'<$>{break}<$>',
    '13cb': u'<$>{break}<$>',
    '13462': u'<$>{break}<$>',
    '16ec': u'<$>{break}<$>',
    '16ea': u'<$>{break}<$>',
    '16ef': u'<$>{break}<$>{italic}<$>',
    '97c1': u'<$>{break}<$>',
    '97c2': u'<$>{break}<$>',
    '97c4': u'<$>{break}<$>',
    '97c7': u'<$>{break}<$>',
    '92cd': u'<$>{break}<$>',
    '92ce': u'<$>{break}<$>{italic}<$>',
    '92cb': u'<$>{break}<$>',
    '92da': u'<$>{break}<$>',
    '92dc': u'<$>{break}<$>',
    '92df': u'<$>{break}<$>',
    '97df': u'<$>{break}<$>',
    '155b': u'<$>{break}<$>',
    '155e': u'<$>{break}<$>',
    '155d': u'<$>{break}<$>',
    '97dc': u'<$>{break}<$>',
    '1675': u'<$>{break}<$>',
    '1676': u'<$>{break}<$>',
    '1670': u'<$>{break}<$>',
    '1673': u'<$>{break}<$>',
    '16462': u'<$>{break}<$>',
    '97cb': u'<$>{break}<$>',
    '97ce': u'<$>{break}<$>{italic}<$>',
    '97cd': u'<$>{break}<$>',
    '92c4': u'<$>{break}<$>',
    '92c7': u'<$>{break}<$>',
    '92c1': u'<$>{break}<$>',
    '92c2': u'<$>{break}<$>',
    '1551': u'<$>{break}<$>',
    '97d5': u'<$>{break}<$>',
    '97d6': u'<$>{break}<$>',
    '1552': u'<$>{break}<$>',
    '97d0': u'<$>{break}<$>',
    '1554': u'<$>{break}<$>',
    '1557': u'<$>{break}<$>',
    '97d3': u'<$>{break}<$>',
    '1558': u'<$>{break}<$>',
    '167f': u'<$>{break}<$>',
    '137f': u'<$>{break}<$>',
    '167a': u'<$>{break}<$>',
    '92d9': u'<$>{break}<$>',
    '92d0': u'<$>{break}<$>',
    '92d3': u'<$>{break}<$>',
    '92d5': u'<$>{break}<$>',
    '92d6': u'<$>{break}<$>',
    '10dc': u'<$>{break}<$>',
    '9262': u'<$>{break}<$>',
    '9261': u'<$>{break}<$>',
    '91f8': u'<$>{break}<$>',
    '10df': u'<$>{break}<$>',
    '9264': u'<$>{break}<$>',
    '91f4': u'<$>{break}<$>',
    '91f7': u'<$>{break}<$>',
    '91f1': u'<$>{break}<$>',
    '91f2': u'<$>{break}<$>',
    '97d9': u'<$>{break}<$>',
    '9149': u'<$>{break}<$>',
    '9143': u'<$>{break}<$>',
    '9140': u'<$>{break}<$>',
    '9146': u'<$>{break}<$>',
    '9145': u'<$>{break}<$>',
    '9464': u'<$>{break}<$>',
    '9467': u'<$>{break}<$>',
    '9461': u'<$>{break}<$>',
    '9462': u'<$>{break}<$>',
    '9468': u'<$>{break}<$>',
    '914c': u'<$>{break}<$>',
    '914a': u'<$>{break}<$>',
    '914f': u'<$>{break}<$>{italic}<$>',
    '10d3': u'<$>{break}<$>',
    '926b': u'<$>{break}<$>',
    '10d0': u'<$>{break}<$>',
    '10d6': u'<$>{break}<$>',
    '926e': u'<$>{break}<$>{italic}<$>',
    '926d': u'<$>{break}<$>',
    '91fd': u'<$>{break}<$>',
    '91fe': u'<$>{break}<$>',
    '10d9': u'<$>{break}<$>',
    '91fb': u'<$>{break}<$>',
    '91fc': u'<$>{break}<$>',
    '946e': u'<$>{break}<$>{italic}<$>',
    '946d': u'<$>{break}<$>',
    '946b': u'<$>{break}<$>',
    '10da': u'<$>{break}<$>',
    '10d5': u'<$>{break}<$>',
    '9267': u'<$>{break}<$>',
    '9268': u'<$>{break}<$>',
    '16df': u'<$>{break}<$>',
    '16da': u'<$>{break}<$>',
    '16dc': u'<$>{break}<$>',
    '9454': u'<$>{break}<$>',
    '9457': u'<$>{break}<$>',
    '9451': u'<$>{break}<$>',
    '9452': u'<$>{break}<$>',
    '136d': u'<$>{break}<$>',
    '136e': u'<$>{break}<$>{italic}<$>',
    '136b': u'<$>{break}<$>',
    '13d9': u'<$>{break}<$>',
    '13da': u'<$>{break}<$>',
    '13dc': u'<$>{break}<$>',
    '13df': u'<$>{break}<$>',
    '1568': u'<$>{break}<$>',
    '1561': u'<$>{break}<$>',
    '1564': u'<$>{break}<$>',
    '1567': u'<$>{break}<$>',
    '16d5': u'<$>{break}<$>',
    '16d6': u'<$>{break}<$>',
    '16d0': u'<$>{break}<$>',
    '16d3': u'<$>{break}<$>',
    '945d': u'<$>{break}<$>',
    '945e': u'<$>{break}<$>',
    '16d9': u'<$>{break}<$>',
    '945b': u'<$>{break}<$>',
    '156b': u'<$>{break}<$>',
    '156d': u'<$>{break}<$>',
    '156e': u'<$>{break}<$>{italic}<$>',
    '105b': u'<$>{break}<$>',
    '1364': u'<$>{break}<$>',
    '1368': u'<$>{break}<$>',
    '1361': u'<$>{break}<$>',
    '13d0': u'<$>{break}<$>',
    '13d3': u'<$>{break}<$>',
    '13d5': u'<$>{break}<$>',
    '13d6': u'<$>{break}<$>',
    '97a1': u'',
    '97a2': u'',
    '9723': u'',
    '94a1': u'',
    '94a4': u'',
    '94ad': u'',
    '1020': u'',
    '10a1': u'',
    '10a2': u'',
    '1023': u'',
    '10a4': u'',
    '1025': u'',
    '1026': u'',
    '10a7': u'',
    '10a8': u'',
    '1029': u'',
    '102a': u'',
    '10ab': u'',
    '102c': u'',
    '10ad': u'',
    '10ae': u'',
    '102f': u'',
    '97ad': u'',
    '97a4': u'',
    '9725': u'',
    '9726': u'',
    '97a7': u'',
    '97a8': u'',
    '9729': u'',
    '972a': u'',
    '9120': u'<$>{end-italic}<$>',
    '91a1': u'',
    '91a2': u'',
    '9123': u'',
    '91a4': u'',
    '9125': u'',
    '9126': u'',
    '91a7': u'',
    '91a8': u'',
    '9129': u'',
    '912a': u'',
    '91ab': u'',
    '912c': u'',
    '91ad': u'',
    '97ae': u'',
    '972f': u'',
    '91ae': u'<$>{italic}<$>',
    '912f': u'<$>{italic}<$>',
    '94a8': u'',
    '9423': u'',
    '94a2': u'',
}

CHARACTERS = {
    '20': u' ',
    'a1': u'!',
    'a2': u'"',
    '23': u'#',
    'a4': u'$',
    '25': u'%',
    '26': u'&',
    'a7': u'\'',
    'a8': u'(',
    '29': u')',
    '2a': u'á',
    'ab': u'+',
    '2c': u',',
    'ad': u'-',
    'ae': u'.',
    '2f': u'/',
    'b0': u'0',
    '31': u'1',
    '32': u'2',
    'b3': u'3',
    '34': u'4',
    'b5': u'5',
    'b6': u'6',
    '37': u'7',
    '38': u'8',
    'b9': u'9',
    'ba': u':',
    '3b': u';',
    'bc': u'<',
    '3d': u'=',
    '3e': u'>',
    'bf': u'?',
    '40': u'@',
    'c1': u'A',
    'c2': u'B',
    '43': u'C',
    'c4': u'D',
    '45': u'E',
    '46': u'F',
    'c7': u'G',
    'c8': u'H',
    '49': u'I',
    '4a': u'J',
    'cb': u'K',
    '4c': u'L',
    'cd': u'M',
    'ce': u'N',
    '4f': u'O',
    'd0': u'P',
    '51': u'Q',
    '52': u'R',
    'd3': u'S',
    '54': u'T',
    'd5': u'U',
    'd6': u'V',
    '57': u'W',
    '58': u'X',
    'd9': u'Y',
    'da': u'Z',
    '5b': u'[',
    'dc': u'é',
    '5d': u']',
    '5e': u'í',
    'df': u'ó',
    'e0': u'ú',
    '61': u'a',
    '62': u'b',
    'e3': u'c',
    '64': u'd',
    'e5': u'e',
    'e6': u'f',
    '67': u'g',
    '68': u'h',
    'e9': u'i',
    'ea': u'j',
    '6b': u'k',
    'ec': u'l',
    '6d': u'm',
    '6e': u'n',
    'ef': u'o',
    '70': u'p',
    'f1': u'q',
    'f2': u'r',
    '73': u's',
    'f4': u't',
    '75': u'u',
    '76': u'v',
    'f7': u'w',
    'f8': u'x',
    '79': u'y',
    '7a': u'z',
    'fb': u'ç',
    '7c': u'÷',
    'fd': u'Ñ',
    'fe': u'ñ',
    '7f': u'',
    '80': u''
}

SPECIAL_CHARS = {
    '91b0': u'®',
    '9131': u'°',
    '9132': u'½',
    '91b3': u'¿',
    '91b4': u'™',
    '91b5': u'¢',
    '91b6': u'£',
    '9137': u'♪',
    '9138': u'à',
    '91b9': u' ',
    '91ba': u'è',
    '913b': u'â',
    '91bc': u'ê',
    '913d': u'î',
    '913e': u'ô',
    '91bf': u'û'
}

EXTENDED_CHARS = {
    '9220': u'Á',
    '92a1': u'É',
    '92a2': u'Ó',
    '9223': u'Ú',
    '92a4': u'Ü',
    '9225': u'ü',
    '9226': u'‘',
    '92a7': u'¡',
    '92a8': u'*',
    '9229': u'’',
    '922a': u'—',
    '92ab': u'©',
    '922c': u'℠',
    '92ad': u'•',
    '92ae': u'“',
    '922f': u'”',
    '92b0': u'À',
    '9231': u'Â',
    '9232': u'Ç',
    '92b3': u'È',
    '9234': u'Ê',
    '92b5': u'Ë',
    '92b6': u'ë',
    '9237': u'Î',
    '9238': u'Ï',
    '92b9': u'ï',
    '92ba': u'Ô',
    '923b': u'Ù',
    '92bc': u'ù',
    '923d': u'Û',
    '923e': u'«',
    '92bf': u'»',
    '1320': u'Ã',
    '13a1': u'ã',
    '13a2': u'Í',
    '1323': u'Ì',
    '13a4': u'ì',
    '1325': u'Ò',
    '1326': u'ò',
    '13a7': u'Õ',
    '13a8': u'õ',
    '1329': u'{',
    '132a': u'}',
    '13ab': u'\\',
    '132c': u'^',
    '13ad': u'_',
    '13ae': u'¦',
    '132f': u'~',
    '13b0': u'Ä',
    '1331': u'ä',
    '1332': u'Ö',
    '13b3': u'ö',
    '1334': u'ß',
    '13b5': u'¥',
    '13b6': u'¤',
    '1337': u'|',
    '1338': u'Å',
    '13b9': u'å',
    '13ba': u'Ø',
    '133b': u'ø',
    '13bc': u'┌',
    '133d': u'┐',
    '133e': u'└',
    '13bf': u'┘',
}


class SCCReader(BaseReader):
    def __init__(self, *args, **kw):
        self.scc = []
        self.time = ''
        self.pop_buffer = ''
        self.paint_buffer = ''
        self.last_command = ''
        self.roll_rows = []
        self.roll_rows_expected = 0
        self.pop_on = False
        self.paint_on = False
        self.frame_count = 0
        self.simulate_roll_up = False
        self.offset = 0

    def detect(self, content):
        lines = content.splitlines()
        if lines[0] == 'Scenarist_SCC V1.0':
            return True
        else:
            return False

    def read(self, content, lang='en', simulate_roll_up=False, offset=0):
        self.simulate_roll_up = simulate_roll_up
        self.offset = offset * 1000000
        # split lines
        lines = content.splitlines()

        # loop through each line except the first
        for line in lines[1:]:
            self._translate_line(line)

        # after converting lines, see if anything is left in paint_buffer
        if self.paint_buffer:
            self._roll_up()

        captions = CaptionSet()
        captions.set_captions(lang, self.scc)
        return captions

    def _translate_line(self, line):
        # ignore blank lines
        if line.strip() == '':
            return

        # split line in timestamp and words
        r = re.compile("([0-9:;]*)([\s\t]*)((.)*)")
        parts = r.findall(line.lower())

        self.time = parts[0][0]
        self.frame_count = 0

        # loop through each word
        for word in parts[0][2].split(' '):
            # ignore empty results
            if word.strip() != '':
                self._translate_word(word)

    def _translate_word(self, word):
        # count frames for timing
        self.frame_count += 1

        # first check if word is a command
        if word in COMMANDS:
            self._translate_command(word)

        # second, check if word is a special character
        elif word in SPECIAL_CHARS:
            self._translate_special_char(word)

        elif word in EXTENDED_CHARS:
            self._translate_extended_char(word)

        # third, try to convert word into 2 characters
        else:
            self._translate_characters(word)

    def _handle_double_command(self, word):
        # ensure we don't accidentally use the same command twice
        if word == self.last_command:
            self.last_command = ''
            return True
        else:
            self.last_command = word
            return False

    def _translate_special_char(self, word):
        if self._handle_double_command(word):
            return

        # add to buffer
        if self.paint_on:
            self.paint_buffer += SPECIAL_CHARS[word]
        else:
            self.pop_buffer += SPECIAL_CHARS[word]

    def _translate_extended_char(self, word):
        if self._handle_double_command(word):
            return

        # add to buffer
        if self.paint_on:
            if self.paint_buffer:
                self.paint_buffer = self.paint_buffer[:-1]
            self.paint_buffer += EXTENDED_CHARS[word]
        else:
            if self.pop_buffer:
                self.pop_buffer = self.pop_buffer[:-1]
            self.pop_buffer += EXTENDED_CHARS[word]

    def _translate_command(self, word):
        if self._handle_double_command(word):
            return

        # if command is pop_up
        if word == '9420':
            self.pop_on = True
            self.paint_on = False

        # if command is paint_on / _roll_up
        elif word in ['9429', '9425', '9426', '94a7']:
            self.paint_on = True
            self.pop_on = False

            # count how many lines are expected
            if word == '9429':
                self.roll_rows_expected = 1
            elif word == '9425':
                self.roll_rows_expected = 2
            elif word == '9426':
                self.roll_rows_expected = 3
            elif word == '94a7':
                self.roll_rows_expected = 4

            # if content is in the queue, turn it into a caption
            if self.paint_buffer:
                # convert and empty buffer
                self._convert_to_caption(self.paint_buffer, self.paint_time)
                self.paint_buffer = ''

            # set rows to empty, configure start time for caption
            self.roll_rows = []
            self.paint_time = self._translate_time(self.time[:-2] +
                                                   str(int(self.time[-2:]) +
                                                   self.frame_count))

        # clear pop_on buffer
        elif word == '94ae':
            self.pop_buffer = ''

        # display pop_on buffer
        elif word == '942f' and self.pop_buffer:
            # configure timestamp, convert and empty buffer
            self.pop_time = self._translate_time(self.time[:-2] +
                                                 str(int(self.time[-2:]) +
                                                 self.frame_count))
            self._convert_to_caption(self.pop_buffer, self.pop_time)
            self.pop_buffer = ''

        # roll up captions
        elif word == '94ad':
            # display paint_on buffer
            if self.paint_buffer:
                self._roll_up()

        # clear screen
        elif word == '942c':
            self.roll_rows = []

            if self.paint_buffer:
                self._roll_up()

            # attempt to add proper end time to last caption
            if self.scc and self.scc[-1].end == 0:
                last_time = self._translate_time(self.time[:-2] +
                                                 str(int(self.time[-2:]) +
                                                 self.frame_count))
                self.scc[-1].end = last_time

        # if command not one of the aforementioned, add to buffer
        else:
            if self.paint_on:
                self.paint_buffer += COMMANDS[word]
            else:
                self.pop_buffer += COMMANDS[word]

    def _translate_characters(self, word):
        # split word into the 2 bytes
        byte1 = word[:2]
        byte2 = word[2:]

        # check to see if the the bytes are recognized characters
        if byte1 not in CHARACTERS or byte2 not in CHARACTERS:
            return

        # if so, add to buffer
        if self.paint_on:
            self.paint_buffer += CHARACTERS[byte1] + CHARACTERS[byte2]
        else:
            self.pop_buffer += CHARACTERS[byte1] + CHARACTERS[byte2]

    # convert SCC timestamp into total microseconds
    def _translate_time(self, stamp):
        if ';' in stamp:
            frames_per_second = 30.00
        else:
            frames_per_second = 29.97

        timesplit = stamp.replace(';', ':').split(':')

        microseconds = (int(timesplit[0]) * 3600000000 +
                        int(timesplit[1]) * 60000000 +
                        int(timesplit[2]) * 1000000 +
                        (int(timesplit[3]) / frames_per_second * 1000000) -
                        self.offset)

        if microseconds < 0:
            microseconds = 0

        return microseconds

    # convert buffer into Caption object
    def _convert_to_caption(self, buffer, start):
        # check to see if previous caption needs an end-time
        if self.scc and self.scc[-1].end == 0:
            self.scc[-1].end = start

        # initial variables
        caption = Caption()
        caption.start = start
        caption.end = 0 # Not yet known; filled in later
        self.open_italic = False
        self.first_element = True

        # split into elements (e.g. break, italics, text)
        for element in buffer.split('<$>'):
            # skip empty elements
            if element.strip() == '':
                continue

            # handle line breaks
            elif element == '{break}':
                self._translate_break(caption)

            # handle open italics
            elif element == '{italic}':
                # add italics
                caption.nodes.append(CaptionNode.create_style(True, {'italics': True}))
                # open italics, no longer first element
                self.open_italic = True
                self.first_element = False

            # handle clone italics
            elif element == '{end-italic}' and self.open_italic:
                caption.nodes.append(CaptionNode.create_style(False, {'italics': True}))
                self.open_italic = False

            # handle text
            else:
                # add text
                caption.nodes.append(CaptionNode.create_text(' '.join(element.split())))
                # no longer first element
                self.first_element = False

        # close any open italics left over
        if self.open_italic == True:
            caption.nodes.append(CaptionNode.create_style(False, {'italics': True}))

        # remove extraneous italics tags in the same caption
        self._remove_italics(caption)

        # only add captions to list if content inside exists
        if caption.nodes:
            self.scc.append(caption)

    def _translate_break(self, caption):
        # if break appears at start of caption, skip break
        if self.first_element == True:
            return
        # if the last caption was a break, skip this break
        elif caption.nodes[-1].type == CaptionNode.BREAK:
            return
        # close any open italics
        elif self.open_italic == True:
            caption.nodes.append(CaptionNode.create_style(False, {'italics': True}))
            self.open_italic = False

        # add line break
        caption.nodes.append(CaptionNode.create_break())

    def _remove_italics(self, caption):
        i = 0
        length = max(0, len(caption.nodes) - 2)
        while i < length:
            if (caption.nodes[i].type == CaptionNode.STYLE and caption.nodes[i].content['italics'] and
                        caption.nodes[i + 1].type == CaptionNode.BREAK and
                        caption.nodes[i + 2].type == CaptionNode.STYLE and caption.nodes[i + 2].content['italics']):
                # Remove the two italics style nodes
                caption.nodes.pop(i)
                caption.nodes.pop(i + 1)
                length -= 2
            i += 1

    def _roll_up(self):
        if self.simulate_roll_up == False:
            self.roll_rows = []

        # if rows already filled, drop the top one
        if len(self.roll_rows) >= self.roll_rows_expected:
            self.roll_rows.pop(0)

        # add buffer as row to bottom
        self.roll_rows.append(self.paint_buffer)
        self.paint_buffer = ' '.join(self.roll_rows)

        # convert buffer and empty
        self._convert_to_caption(self.paint_buffer, self.paint_time)
        self.paint_buffer = ''

        # configure time
        self.paint_time = self._translate_time(
            self.time[:-2] +
            str(int(self.time[-2:]) +
            self.frame_count))

        # try to insert the proper ending time for the previous caption
        try:
            self.scc[-1].end = self.paint_time
        except IndexError:
            pass
