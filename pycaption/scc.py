#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import math
import string
import textwrap

from .base import (
    BaseReader, BaseWriter, Caption, CaptionSet, CaptionNode,
) 
from .exceptions import CaptionReadNoCaptions


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
PAC_HIGH_BYTE_BY_ROW = [u'xx',u'91',u'91',u'92',u'92',u'15',u'15',u'16',u'16',u'97',u'97',u'10',u'13',u'13',u'94',u'94']
PAC_LOW_BYTE_BY_ROW = [u'xx',u'd0',u'70',u'd0',u'70',u'd0',u'70',u'd0',u'70',u'd0',u'70',u'd0',u'd0',u'70',u'd0',u'70']


# Inverted character lookup
CHARACTER_TO_CODE = {character: code for code, character in CHARACTERS.iteritems()}
SPECIAL_OR_EXTENDED_CHAR_TO_CODE = {character: code for code, character in EXTENDED_CHARS.iteritems()}
SPECIAL_OR_EXTENDED_CHAR_TO_CODE.update({character: code for code, character in SPECIAL_CHARS.iteritems()})


# Time to transmit a single codeword = 1 second / 29.97
MICROSECONDS_PER_CODEWORD = 1000.0 * 1000.0 / (30.0 * 1000.0 / 1001.0)


HEADER = u'Scenarist_SCC V1.0'


class SCCReader(BaseReader):
    def __init__(self, *args, **kw):
        self.scc = []
        self.time = u''
        self.pop_buffer = u''
        self.paint_buffer = u''
        self.last_command = u''
        self.roll_rows = []
        self.roll_rows_expected = 0
        self.pop_on = False
        self.paint_on = False
        self.frame_count = 0
        self.simulate_roll_up = False
        self.offset = 0

    def detect(self, content):
        lines = content.splitlines()
        if lines[0] == HEADER:
            return True
        else:
            return False

    def read(self, content, lang=u'en-US', simulate_roll_up=False, offset=0):
        if type(content) != unicode:
            raise RuntimeError('The content is not a unicode string.')

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

        if captions.is_empty():
            raise CaptionReadNoCaptions(u"empty caption file")

        return captions

    def _translate_line(self, line):
        # ignore blank lines
        if line.strip() == u'':
            return

        # split line in timestamp and words
        r = re.compile(u"([0-9:;]*)([\s\t]*)((.)*)")
        parts = r.findall(line.lower())

        self.time = parts[0][0]
        self.frame_count = 0

        # loop through each word
        for word in parts[0][2].split(u' '):
            # ignore empty results
            if word.strip() != u'':
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
            self.last_command = u''
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
        if word == u'9420':
            self.pop_on = True
            self.paint_on = False

        # if command is paint_on / _roll_up
        elif word in [u'9429', u'9425', u'9426', u'94a7']:
            self.paint_on = True
            self.pop_on = False

            # count how many lines are expected
            if word == u'9429':
                self.roll_rows_expected = 1
            elif word == u'9425':
                self.roll_rows_expected = 2
            elif word == u'9426':
                self.roll_rows_expected = 3
            elif word == u'94a7':
                self.roll_rows_expected = 4

            # if content is in the queue, turn it into a caption
            if self.paint_buffer:
                # convert and empty buffer
                self._convert_to_caption(self.paint_buffer, self.paint_time)
                self.paint_buffer = u''

            # set rows to empty, configure start time for caption
            self.roll_rows = []
            self.paint_time = self._translate_time(self.time[:-2] +
                                                   unicode(int(self.time[-2:]) +
                                                   self.frame_count))

        # clear pop_on buffer
        elif word == u'94ae':
            self.pop_buffer = u''

        # display pop_on buffer
        elif word == u'942f' and self.pop_buffer:
            # configure timestamp, convert and empty buffer
            self.pop_time = self._translate_time(self.time[:-2] +
                                                 unicode(int(self.time[-2:]) +
                                                 self.frame_count))
            self._convert_to_caption(self.pop_buffer, self.pop_time)
            self.pop_buffer = u''

        # roll up captions
        elif word == u'94ad':
            # display paint_on buffer
            if self.paint_buffer:
                self._roll_up()

        # clear screen
        elif word == u'942c':
            self.roll_rows = []

            if self.paint_buffer:
                self._roll_up()

            # attempt to add proper end time to last caption
            if self.scc and self.scc[-1].end == 0:
                last_time = self._translate_time(self.time[:-2] +
                                                 unicode(int(self.time[-2:]) +
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
        if u';' in stamp:
            # Drop-frame timebase runs at the same rate as wall clock
            seconds_per_timestamp_second = 1.0
        else:
            # Non-drop-frame timebase runs "slow"
            # 1 second of timecode is longer than an actual second (1.001s)
            seconds_per_timestamp_second = 1001.0 / 1000.0

        timesplit = stamp.replace(u';', u':').split(u':')

        timestamp_seconds = (int(timesplit[0]) * 3600 +
                             int(timesplit[1]) * 60 +
                             int(timesplit[2]) +
                             int(timesplit[3]) / 30.0)

        seconds = timestamp_seconds * seconds_per_timestamp_second
        microseconds = seconds * 1000 * 1000 - self.offset

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
        for element in buffer.split(u'<$>'):
            # skip empty elements
            if element.strip() == u'':
                continue

            # handle line breaks
            elif element == u'{break}':
                self._translate_break(caption)

            # handle open italics
            elif element == u'{italic}':
                # add italics
                caption.nodes.append(CaptionNode.create_style(True, {u'italics': True}))
                # open italics, no longer first element
                self.open_italic = True
                self.first_element = False

            # handle clone italics
            elif element == u'{end-italic}' and self.open_italic:
                caption.nodes.append(CaptionNode.create_style(False, {u'italics': True}))
                self.open_italic = False

            # handle text
            else:
                # add text
                caption.nodes.append(CaptionNode.create_text(u' '.join(element.split())))
                # no longer first element
                self.first_element = False

        # close any open italics left over
        if self.open_italic == True:
            caption.nodes.append(CaptionNode.create_style(False, {u'italics': True}))

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
            caption.nodes.append(CaptionNode.create_style(False, {u'italics': True}))
            self.open_italic = False

        # add line break
        caption.nodes.append(CaptionNode.create_break())

    def _remove_italics(self, caption):
        i = 0
        length = max(0, len(caption.nodes) - 2)
        while i < length:
            if (caption.nodes[i].type == CaptionNode.STYLE and caption.nodes[i].content[u'italics'] and
                        caption.nodes[i + 1].type == CaptionNode.BREAK and
                        caption.nodes[i + 2].type == CaptionNode.STYLE and caption.nodes[i + 2].content[u'italics']):
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
        self.paint_buffer = u' '.join(self.roll_rows)

        # convert buffer and empty
        self._convert_to_caption(self.paint_buffer, self.paint_time)
        self.paint_buffer = u''

        # configure time
        self.paint_time = self._translate_time(
            self.time[:-2] +
            unicode(int(self.time[-2:]) +
            self.frame_count))

        # try to insert the proper ending time for the previous caption
        try:
            self.scc[-1].end = self.paint_time
        except IndexError:
            pass


class SCCWriter(BaseWriter):

    def write(self, caption_set):
        output = HEADER + u'\n\n'

        if caption_set.is_empty():
            return output

        # Only support one language.
        lang = caption_set.get_languages()[0]
        captions = caption_set.get_captions(lang)

        # PASS 1: compute codes for each caption
        codes = [(self._text_to_code(caption), caption.start, caption.end)
                 for caption in captions]

        # PASS 2:
        # Advance start times so as to have time to write to the pop-on
        # buffer; possibly remove the previous clear-screen command
        for index, (code, start, end) in enumerate(codes):
            code_words = len(code) / 5 + 8
            code_time_microseconds = code_words * MICROSECONDS_PER_CODEWORD
            code_start = start - code_time_microseconds
            if index == 0:
                continue
            previous_code, previous_start, previous_end = codes[index-1]
            if previous_end + 3 * MICROSECONDS_PER_CODEWORD >= code_start:
                codes[index-1] = (previous_code, previous_start, None)
            codes[index] = (code, code_start, end)

        # PASS 3:
        # Write captions.
        for (code, start, end) in codes:
            output += (u'%s\t' % self._format_timestamp(start))
            output += u'94ae 94ae 9420 9420 '
            output += code
            output += u'942c 942c 942f 942f\n\n'
            if end != None:
                output += u'%s\t942c 942c\n\n' % self._format_timestamp(end)

        return output

    # Wrap lines at 32 chars
    def _layout_line(self, caption):
        def caption_node_to_text(caption_node):
            if caption_node.type == CaptionNode.TEXT:
                return unicode(caption_node.content)
            elif caption_node.type == CaptionNode.BREAK:
                return u'\n'
        caption_text = u''.join([caption_node_to_text(node)
                                for node in caption.nodes])
        inner_lines = string.split(caption_text, u'\n')
        inner_lines_laid_out = [textwrap.fill(x, 32) for x in inner_lines]
        return u'\n'.join(inner_lines_laid_out)

    def _maybe_align(self, code):
        # Finish a half-word with a no-op so we can move to a full word
        if len(code) % 5 == 2:
            code += u'80 '
        return code

    def _maybe_space(self, code):
        if len(code) % 5 == 4:
            code += u' '
        return code

    def _print_character(self, code, char):
        try:
            char_code = CHARACTER_TO_CODE[char]
        except KeyError:
            try:
                char_code = SPECIAL_OR_EXTENDED_CHAR_TO_CODE[char]
            except KeyError:
                char_code = u'91b6' # Use £ as "unknown character" symbol

        if len(char_code) == 2:
            return code + char_code
        elif len(char_code) == 4:
            return self._maybe_align(code) + char_code
        else:
            # This should not happen!
            return code

    def _text_to_code(self, s):
        code = u''
        lines = string.split(self._layout_line(s), u'\n')
        for row, line in enumerate(lines):
            row = 16 - len(lines) + row
            # Move cursor to column 0 of the destination row
            for _ in range(2):
                code += (u'%s%s ' % (PAC_HIGH_BYTE_BY_ROW[row],
                                    PAC_LOW_BYTE_BY_ROW[row]))
            # Print the line using the SCC encoding
            for index, char in enumerate(line):
                code = self._print_character(code, char)
                code = self._maybe_space(code)
            code = self._maybe_align(code)
        return code

    def _format_timestamp(self, microseconds):
        seconds_float = microseconds / 1000.0 / 1000.0
        # Convert to non-drop-frame timecode
        seconds_float *= 1000.0 / 1001.0
        hours = math.floor(seconds_float / 3600)
        seconds_float -= hours * 3600
        minutes = math.floor(seconds_float / 60)
        seconds_float -= minutes * 60
        seconds = math.floor(seconds_float)
        seconds_float -= seconds
        frames = math.floor(seconds_float * 30)
        return u'%02d:%02d:%02d:%02d' % (hours, minutes, seconds, frames)




