#!/bin/bash

echo "##########################################"
echo "# UBUNTU LIVE SERVER POST-INSTALL SCRIPT #"
echo "##########################################"

echo "Mise à jour de l'APT"
apt-get update
#apt-get upgrade

echo "Installation des paquets de base"
sudo apt-get install --yes git git-extras build-essential python3-pip htop glances

clear

#Installation de mysql-server
echo "Installation de MySql-server.."
sudo apt install mysql-server


echo "Installation de MySql-server-secure.."
sudo mysql_secure_installation

echo "Réglage de la date et l'heure"
timedatectl set-timezone Europe/Paris

#Commande permettant de désactiver l'authentification par mdp
while true; do
    read -p "Voulez vous désactiver l'authentification par mot de passe ?" yn
    case $yn in
        [Yn]* ) cd /etc/ssh
        sed -i -e 's/#PasswordAuthentication yes/PasswordAuthentication no/g' sshd_config; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done



# echo "Allowing ssh key connexion only..."
# cd /etc/ssh

# #faire attention generation de cle avant de lancer le script!!
# sed -i -e 's/#PasswordAuthentication yes/PasswordAuthentication no/g' sshd_config

echo "Server has been configured successfully!"

