Peux-tu écrire un script python qui extrait des données d'un enregistrement de log, et regroupe les données selon les règles suivantes :  
\- les données sont toutes sous le format suivant : \[\<interface id\>\] \<time\_stamp\> \<type de donnée\> \<valeur\>  
\- l' \<interface id\> vau soit IFACE1, soit IFACE2  
\- \<type de donnée\> \= soit une commande MIDI (PC, CC, Note On, Note Off, Start, Stop, Continue, Clock), soit la chaine "CQ18T Chunk"

Pour les données de commande MIDI standard :   
\- PC \<PC number\>,   
\- CC \<CC number\> \<value\>,   
\- Note On \<Note name\> \<velocity\>,   
\- Note Off \<Note name\> \<velocity\>.   
Les commandes Start, Stop, Continue, Clock n'ont pas d'argument.

Pour les commandes "CQ18T Chunk", chaque enregistrement est un morceau de la donnée complète.   
\- Chaque enregistrement fait 3 octets (par exemple B0 62 40).   
\- Les octets sont représentés en hexadécimal, sans le préfixe 0x.   
\- La donnée complète en constituée de 3 ou 4 enregistrements (lignes), selon le sous-type de commande.   
\- Une commande complète commence toujours par les octets 0xB0 0x63.   
\- Elle est constituée de 3 enregistrements (9 octets) si le 8ème octet vaut 0x60 ou 0x61.   
\- Elle est constitué de 4 enregistrements (12 octets) dans les autres cas. 

Dans toutes les commandes CQ18T Chunk,   
\- L'octet 3 représente le poids fort du canal,   
\- L'octet 6 représente le poids faible du canal. 

Dans les commandes CQ18T Chunk à 9 octets, le 9eme octet représente la valeur. 

Dans les commandes CQ18T Chunk à 12 octets, l'octet 9 représente le poids fort de la valeur, et l'octet 12 représente le poids faible de la valeur.

Une commande CQ18T Chunk est de type "MUTE" si le canal, une fois assemblés le poids fort et le poids faible, a une valeur comprise entre 0x0000 et 0x0403. Le dictionnaire suivant donne le nom du canal en fonction du numéro de canal:

CQ\_MUTE\_CHANNELS\_MAP \= {  
    \# 16 Canaux Mono (IN1-IN16)   
    'IN1':    0x0000, 'IN2':     0x0001, 'IN3':     0x0002, 'IN4':     0x0003,   
    'IN5':    0x0004, 'IN6':     0x0005, 'IN7':     0x0006, 'IN8':     0x0007,   
    'IN9':    0x0008, 'IN10':    0x0009, 'IN11':    0x000A, 'IN12':    0x000B,   
    'IN13':   0x000C, 'IN14':    0x000D, 'IN15':    0x000E, 'IN16':    0x000F,

    \# Entrées Stéréo Dédiées et Retours Numériques  
    'ST1':    0x0018,     \# ST17/18  
    'ST2':    0x001A,  
    'USB':    0x001C,     \# USB   
    'BT':     0x001E,     \# Bluetooth  
      
    \# Sorties Bus FX  
    'FX1':    0x0051, 'FX2':     0x0052, 'FX3':     0x0053, 'FX4':     0x0054,   
      
    \# Sorties Bus mix  
    'MAIN':   0x0044,  
    'OUT1':   0x0045, 'OUT2':    0x0046, 'OUT3':    0x0047, 'OUT4':    0x0048, 'OUT5':    0x0049, 'OUT6':    0x004A,   
      
    \# MIX GROUPS  
    'MGRP1':  0x0400, 'MGRP2':   0x0401, 'MGRP3':   0x0402, 'MGRP4':   0x0403,   
      
    \# DCA  
    'DCA1':   0x0200, 'DCA2':    0x0201, 'DCA3':    0x0202, 'DCA4':    0x0203  
}

Une commande CQ18T Chunk est de type "Fader to main" si le canal, une fois assemblés le poids fort et le poids faible, a une valeur comprise entre 0x4000 et 0x403F. Le dictionnaire suivant donne le nom du canal en fonction du numéro de canal:

CQ\_FADER\_TO\_MAIN\_MAP \= {  
    \# 16 Canaux Mono (IN1-IN16)   
    'IN1':    0x4000, 'IN2':     0x4001, 'IN3':     0x4002, 'IN4':     0x4003,   
    'IN5':    0x4004, 'IN6':     0x4005, 'IN7':     0x4006, 'IN8':     0x4007,   
    'IN9':    0x4008, 'IN10':    0x4009, 'IN11':    0x400A, 'IN12':    0x400B,   
    'IN13':   0x400C, 'IN14':    0x400D, 'IN15':    0x400E, 'IN16':    0x400F,

    \# Entrées Stéréo Linkées (Le contrôle se fait via l'index du premier canal)  
    'ST1/2':  0x4000, 'ST3/4':   0x4002, 'ST5/6':   0x4004, 'ST7/8':   0x4006,   
    'ST9/10': 0x4008, 'ST11/12': 0x400A, 'ST13/14': 0x400C, 'ST15/16': 0x400E,

    \# Entrées Stéréo Dédiées et Retours Numériques  
    'ST1':    0x4018,     \# ST17/18  
    'ST2':    0x401A,  
    'USB':    0x401C,     \# USB   
    'BT':     0x401E,     \# Bluetooth  
      
    \# Sorties Bus FX  
    'FX1':    0x403C, 'FX2':     0x403D, 'FX3':     0x403E, 'FX4':     0x403F     
}

Une commande CQ18T Chunk est de type "Fader to aux" si le canal, une fois assemblés le poids fort et le poids faible, a une valeur comprise entre 0x4044 et 0x463D. Le dictionnaire suivant donne le nom du canal en fonction du numéro de canal:

CQ\_FADER\_TO\_OUT\_MAP \= {  
    \# 16 Canaux Mono (IN1-IN16)   
    'IN1':    0x4044, 'IN2':     0x4050, 'IN3':     0x405C, 'IN4':     0x4068,   
    'IN5':    0x4074, 'IN6':     0x4100, 'IN7':     0x410C, 'IN8':     0x4118,   
    'IN9':    0x4124, 'IN10':    0x4130, 'IN11':    0x413C, 'IN12':    0x4148,   
    'IN13':   0x4154, 'IN14':    0x4160, 'IN15':    0x416C, 'IN16':    0x4178,

    \# Entrées Stéréo Dédiées et Retours Numériques  
    'ST1':    0x4264,     \# ST17/18  
    'ST2':    0x427C,  
    'USB':    0x4314,     \# USB   
    'BT':     0x432C,     \# Bluetooth  
      
    \# Sorties Bus FX  
    'FX1':    0x4614, 'FX2':     0x4620, 'FX3':     0x462C, 'FX4':     0x4638   
}

Le "AUX" peut valoir entre 1 et 6, et peut être déduit du numéro de canal. Par exemple, le canal 0x4044 est le fader IN1 vers la sortie AUX1, le canal 0x4045 est le fader IN1 vers la sortie AUX2, le canal 0x4049 est le fader IN1 vers la sortie AUX6. Le canal 0x413F est le fader IN11 vers la sortie AUX4.

Une commande CQ18T Chunk est de type "Fader to Fx" si la valeur est comprise entre 0x4C14 et 0x4E13.Le dictionnaire suivant donne le nom du canal en fonction du numéro de canal:

CQ\_FADER\_TO\_FX\_MAP \= {  
    \# 16 Canaux Mono (IN1-IN16)   
    'IN1':    0x4C14, 'IN2':     0x4C18, 'IN3':     0x4C1C, 'IN4':     0x4C20,   
    'IN5':    0x4C24, 'IN6':     0x4C28, 'IN7':     0x4C2C, 'IN8':     0x4C30,   
    'IN9':    0x4C34, 'IN10':    0x4C38, 'IN11':    0x4C3C, 'IN12':    0x4C40,   
    'IN13':   0x4C44, 'IN14':    0x4C48, 'IN15':    0x4C4C, 'IN16':    0x4C50,

    \# Entrées Stéréo Dédiées et Retours Numériques  
    'ST1':    0x4C74,     \# ST17/18  
    'ST2':    0x4C7C,  
    'USB':    0x4D04,     \# USB   
    'BT':     0x4D0C,     \# Bluetooth  
      
    \# Sorties Bus FX  
    'FX1':    0x4E04, 'FX2':     0x4E08, 'FX3':     0x4E0C, 'FX4':     0x4E10     
}

Le "FX" peut valoir entre 1 et 4, et peut être déduit du numéro de canal. Par exemple, le canal 0x4C14 est le fader IN1 vers la sortie FX1, le canal 0x4C17 est le fader IN1 vers la sortie FX4, le canal 0x4C4A est le fader IN14 vers la sortie FX3.

Une commande CQ18T Chunk est de type "Bus Fader" si la valeur est comprise entre 0x4F00 et 0x4F23.Le dictionnaire suivant donne le nom du canal en fonction du numéro de canal:

CQ\_BUS\_FADER\_MAP \= {  
    'MAIN':   0x4F00,  
    'OUT1':   0x4F01, 'OUT2':   0x4F02, 'OUT3':   0x4F03, 'OUT4':   0x4F04, 'OUT5':   0x4F05, 'OUT6':   0x4F06,   
    'FX1':    0x4F0D, 'FX2':    0x4F0E, 'FX3':    0x4F0F, 'FX4':    0x4F10,   
    'DCA1':   0x4F20, 'DCA2':   0x4F21, 'DCA3':   0x4F22, 'DCA4':   0x4F23   
}

Une commande CQ18T Chunk est de type "Pan to Main" si la valeur est comprise entre 0x5000 et 0x503F.Le dictionnaire suivant donne le nom du canal en fonction du numéro de canal:

CQ\_PAN\_TO\_MAIN\_MAP \= {  
    \# 16 Canaux Mono (IN1-IN16)   
    'IN1':    0x5000, 'IN2':     0x5001, 'IN3':     0x5002, 'IN4':     0x5003,   
    'IN5':    0x5004, 'IN6':     0x5005, 'IN7':     0x5006, 'IN8':     0x5007,   
    'IN9':    0x5008, 'IN10':    0x5009, 'IN11':    0x500A, 'IN12':    0x500B,   
    'IN13':   0x500C, 'IN14':    0x500D, 'IN15':    0x500E, 'IN16':    0x500F,

    \# Entrées Stéréo Linkées (Le contrôle se fait via l'index du premier canal)  
    'ST1/2':  0x5000, 'ST3/4':   0x5002, 'ST5/6':   0x5004, 'ST7/8':   0x5006,   
    'ST9/10': 0x5008, 'ST11/12': 0x500A, 'ST13/14': 0x500C, 'ST15/16': 0x500E,

    \# Entrées Stéréo Dédiées et Retours Numériques  
    'ST1':    0x5018,     \# ST17/18  
    'ST2':    0x501A,  
    'USB':    0x501C,     \# USB   
    'BT':     0x501E,     \# Bluetooth  
      
    \# Sorties Bus FX  
    'FX1':    0x503C, 'FX2':     0x503D, 'FX3':     0x503E, 'FX4':     0x503F     
}

Une commande CQ18T Chunk est de type "Pan to Aux" si la valeur est comprise entre 0x5044 et 0x563C.Le dictionnaire suivant donne le nom du canal en fonction du numéro de canal:

CQ\_PAN\_TO\_OUT\_MAP \= {  
    \# 16 Canaux Mono (IN1-IN16)   
    'IN1':    0x5044, 'IN2':     0x5050, 'IN3':     0x505C, 'IN4':     0x5068,   
    'IN5':    0x5074, 'IN6':     0x5100, 'IN7':     0x510C, 'IN8':     0x5118,   
    'IN9':    0x5124, 'IN10':    0x5130, 'IN11':    0x513C, 'IN12':    0x5148,   
    'IN13':   0x5154, 'IN14':    0x5160, 'IN15':    0x516C, 'IN16':    0x5178,

    \# Entrées Stéréo Dédiées et Retours Numériques  
    'ST1':    0x5264,     \# ST17/18  
    'ST2':    0x527C,  
    'USB':    0x5314,     \# USB   
    'BT':     0x532C,     \# Bluetooth  
      
    \# Sorties Bus FX  
    'FX1':    0x5614, 'FX2':     0x5620, 'FX3':     0x562C, 'FX4':     0x5638     
}

Le "AUX" peut valoir entre 1 et 6, et peut être déduit du numéro de canal. Par exemple, le canal 0x5044 est le pan IN1 vers la sortie AUX1, le canal 0x5046 est le pan IN1 vers la sortie AUX3, le canal 0x5048 est le fader IN1 vers la sortie AUX5. Le canal 0x416E est le fader IN15 vers la sortie AUX3.

Dans les commandes CQ18T Chunk, la valeur associée aux commandes "Fader to main", "Fader to Aux" , "Fader to Fx" et "Bus Fader" est codée selon la table d'interpolation suivante, dans laquelle la première valeur représente un gain en décibels, et la seconde valeur représente la valeur en hexadécimal à décoder :

TABLE\_VCVF\_FADER\_VAL14 \= \[  
    \[-89, 0x0140\], \[-85, 0x0200\], \[-80, 0x0240\], \[-75, 0x0300\], \[-70, 0x0400\], \[-65, 0x0500\], \[-60, 0x0600\], \[-55, 0x0700\],  
    \[-50, 0x0800\], \[-45, 0x0C00\], \[-40, 0x0F40\], \[-38, 0x1240\], \[-36, 0x1540\], \[-35, 0x1700\], \[-34, 0x1900\], \[-33, 0x1A00\],  
    \[-32, 0x1C00\], \[-31, 0x1D40\], \[-30, 0x1F00\], \[-29, 0x2040\], \[-28, 0x2200\], \[-27, 0x2340\], \[-26, 0x2500\], \[-25, 0x2640\],  
    \[-24, 0x2840\], \[-23, 0x2A00\], \[-22, 0x2B40\], \[-21, 0x2D00\], \[-20, 0x2E40\], \[-19, 0x3000\], \[-18, 0x3140\], \[-17, 0x3300\],  
    \[-16, 0x3440\], \[-15, 0x3600\], \[-14, 0x3800\], \[-13, 0x3940\], \[-12, 0x3B00\], \[-11, 0x3C40\], \[-10, 0x3E00\], \[-9,  0x4140\],  
    \[-8,  0x4440\], \[-7,  0x4800\], \[-6,  0x4B00\], \[-5,  0x4E40\], \[-4,  0x5240\], \[-3,  0x5640\], \[-2,  0x5A00\], \[-1,  0x5E00\],  
    \[0,   0x6200\], \[1,   0x6540\], \[2,   0x6900\], \[3,   0x6C40\], \[4,   0x7000\], \[5,   0x7340\], \[6,   0x7540\], \[7,   0x7800\],  
    \[8,   0x7A40\], \[9,   0x7D00\], \[10,  0x7F40\]  
\]

Dans les commandes CQ18T Chunk, la valeur associée aux commandes "Pan to main", et "Pan  to Aux" est codée selon la table d'interpolation suivante, dans laquelle la première valeur représente un pourcentage, et la seconde valeur représente la valeur en hexadécimal à décoder. Si le pourcentage est négatif, la sortie du script doit donner "left " suivi de la valeur absolue du pourcentage. Si le pourcentage est positif, la sortie du script doit donner "right " suivi de la valeur absolue du pourcentage. Si le pourcentage est égal à 0, la sortie du script doit donner "center". :

TABLE\_VCVF\_PAN\_VAL14 \= \[  
    \[-100, 0x0000\], \[-90, 0x0633\], \[-80, 0x0C66\], \[-70, 0x1319\], \[-60, 0x194C\], \[-50, 0x1F7F\], \[-40, 0x2632\], \[-30, 0x2C65\],  
    \[-20,  0x3318\], \[-15, 0x3632\], \[-10, 0x394B\], \[-5,  0x3C65\], \[0,   0x4000\], \[5,   0x4318\], \[10,  0x4632\], \[15,  0x494B\],  
    \[20,   0x4C65\], \[30,  0x5318\], \[40, 0x594B\],  \[50,  0x5F7F\], \[60,  0x6632\], \[60,  0x6632\], \[70,  0x6C65\], \[80,  0x7318\],  
    \[90,   0x764B\], \[100, 0x7F7F\]  
\]

Le script a pour arguments de ligne de commande :  
\- \--in: le nom du fichier à analyser. Par défaut, on utilise l'entrée standard stdin  
\- \--out: le nom du fichier de sortie. Par défaut, on utilise la sortie standard stdout  
\- \--ignore: argument chaîne contenant une ou plusieurs interfaces à filter (IFACE1 ou IFACE2)  
\- \--start: timestamp de début d'analyse. Par défaut, l'analyse commence au premier enregistrement  
\- \--stop: timestamp de fin d'analyse. Par défaut, l'analyse commence au dernier enregistrement  
\- \--filter: le script recopie en sortie, sans analyse, tous les enregistrements relatifs à l'interface spécifiée (IFACE1 ou IFACE2), et ignore les enregistrements de l'autre interface. Les arguments start et stop sont pris en compte dans le mode filtrage.

peux-tu modifier le script pour le timestamp corresponde au format de datetime python. VOiic un exemple de fichier d'enregistrement 

\[IFACE 2\] 2025-10-18 12:53:03.208213 CQ18T Chunk B0 63 4F  
\[IFACE 2\] 2025-10-18 12:53:03.212980 CQ18T Chunk B0 62 00  
\[IFACE 2\] 2025-10-18 12:53:03.217904 CQ18T Chunk B0 06 3A  
\[IFACE 2\] 2025-10-18 12:53:03.223020 CQ18T Chunk B0 26 40  
\[IFACE 2\] 2025-10-18 12:53:03.567383 CQ18T Chunk B0 63 4F  
\[IFACE 2\] 2025-10-18 12:53:03.570768 CQ18T Chunk B0 62 00  
\[IFACE 2\] 2025-10-18 12:53:03.575601 CQ18T Chunk B0 06 39  
\[IFACE 2\] 2025-10-18 12:53:03.580591 CQ18T Chunk B0 26 00  
\[IFACE 1\] 2025-10-18 12:53:21.800930 CC 0 \<0\>  
\[IFACE 1\] 2025-10-18 12:53:21.809998 CC 32 \<0\>  
\[IFACE 1\] 2025-10-18 12:53:21.815440 PC \<11\>  
\[IFACE 1\] 2025-10-18 12:53:21.820365 Note On C0 \<127\>  
\[IFACE 1\] 2025-10-18 12:53:21.825182 PC \<94\>  
\[IFACE 1\] 2025-10-18 12:53:21.830033 Note On D5 \<127\>

Peux-tu modifier le script pour ajouter une fonction permettant de faciliter l'analyse. 

Dans un fichier, je vais définir des timetags, au même format que les timestamp de l'enregistrement.

Entre 2 timetags, il faudra extraire uniquement la dernière valeur de chaque commande CQ18T Chunk. 

Par exemple, avec les timetags suivants,   
timetag1, 2025-10-18 16:31:00.0  
timetag2, 2025-10-18 16:41:00.0  
timetag3, 2025-10-18 16:51:00.0  
le script ne devrait conserver que les 2 résultats   
\[IFACE 2\] 2025-10-18 16:31:22.897065 CQ18T: Fader to Main IN12 \= 0.1 dB (interpolé) (0x400B, Valeur: 0x6240)  
\[IFACE 2\] 2025-10-18 16:41:23.654150 CQ18T: Fader to Main IN12 \= \-5.7 dB (interpolé) (0x400B, Valeur: 0x4C00)

