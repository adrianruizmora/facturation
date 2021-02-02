::La commande echo off désactive l'affichage pour le script entier.
@ECHO OFF
:: chcp 65001 nous permet de prendre en compte les caractères utf-8
chcp 65001

echo                                     ################################
ECHO ------------------------------------### Lancement du script Bat..###-----------------------------------
echo                                     ################################

Echo Salut %USERNAME% !
ECHO Génération de la clé publique :

:: Commande permettant de demander à l'utilisateur si il veut continuer

:choice
set /P c=Etes vous sûr de vouloir générer la clé [Y/N]?
if /I "%c%" EQU "Y" goto :somewhere
if /I "%c%" EQU "N" goto :somewhere_else
goto :choice

:: Début des actions si Yes
:somewhere

set /p login=Veuillez entrer votre LOGIN:
:blank
if "%LOGIN%" == "" (
    echo Entrez quelque chose !
    set /p login=Veuillez entrer votre LOGIN:
    goto :blank
)

set /p ip=Veuillez entrer votre IP:
:blank2
if "%ip%" == "" (
    echo Entrez quelque chose !
    set /p ip=Veuillez entrer votre IP:
    goto :blank2
)

ECHO Génération de la clé pour l'adresse %LOGIN%@%ip%
PAUSE

::Commande nous permettant de générer les clés

ssh-keygen

ECHO Connexion au serveur ssh ...
PAUSE

::ssh %LOGIN%@%ip% test -f filename

ssh %LOGIN%@%ip% "mkdir .ssh && cd .ssh && touch authorized_keys"
type C:\Users\%USERNAME%\.ssh\id_rsa.pub | ssh %LOGIN%@%ip% "cat >> .ssh/authorized_keys"
::ssh selem@%ip% cat C:\Users\Sêlêm\.ssh\id_rsa.pub >> ~/.ssh/authorized_keys

ECHO La clé a été généré et copié vers l'adresse !
echo %ip%>C:\Users\%USERNAME%\Desktop\iptest.txt
PAUSE

:choicefile
set /P c=Souhaitez vous envoyer un fichier vers l'adresse [Y/N]?
if /I "%c%" EQU "Y" goto :somewhere1
if /I "%c%" EQU "N" goto :somewhere_else1
goto :choicefile

:somewhere1

echo Envoie du fichier fichier vers l'adresse ...

set /p cheminfichier=Veuillez entrer le chemin exact vers le fichier:

:blank3
if "%cheminfichier%" == "" (
    echo Entrez quelque chose !
    set /p cheminfichier=Veuillez entrer le chemin exact vers le fichier:
    goto :blank3
)


set /p destinationfichier=Veuillez entrer la destination du fichier: 
:blank4
if "%destinationfichier%" == "" (
    echo Entrez quelque chose !
    set /p destinationfichier=Veuillez entrer la destination du fichier:
    goto :blank4
)

:: ligne permettant d'envoyer un fichier !
scp %cheminfichier% %LOGIN%@%ip%:%destinationfichier%

echo Le fichier à bien été envoyé !
pause

Echo Lancement du script sur la vm :
::ssh %LOGIN%@%ip% "sudo -A"
ssh %LOGIN%@%ip% "chmod 777 ./post-install-server.sh"
ssh -T %LOGIN%@%ip% "sudo -S ./post-install-server.sh"
::ssh %LOGIN%@%ip% "sh ./post-install-server.sh"
pause

exit

:somewhere_else1
echo Vous avez choisis de ne pas envoyer de fichier .
Echo Lancement du script sur la vm :
::ssh %LOGIN%@%ip% "sudo -A"
ssh %LOGIN%@%ip% "chmod 777 ./post-install-server.sh"
ssh -T %LOGIN%@%ip% "sudo -S ./post-install-server.sh"
::ssh %LOGIN%@%ip% "sh ./post-install-server.sh"
pause
echo Fin du script.
pause
exit

::scp C:\Users\Sêlêm\Desktop\InstallKey.Bat %LOGIN%@%ip%:/home


:somewhere_else

ECHO La clé n'a pas été généré...
echo Fin du script

PAUSE
exit

