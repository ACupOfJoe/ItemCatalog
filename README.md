# Introduction
This project creates a database of stocks sorted by industries, updated with the latest close price, and allows the database to be read and edited through a server using python and html. It includes JSON API endpoints and third party authentication. 

# Requirements: 
1. Vagrant 
	* https://www.vagrantup.com/downloads.html
2. VirtualBox 
	* https://www.virtualbox.org/

If not relying on vagrant, set up environment with: 
1. Python 2.7 
2. sqlite3
3. flask
4. sqlalchemy

## Additional Packages 
Using an installer such as "pip" use the commands "sudo pip install <package>" to install the following package. 
1. pandas

# How to create the stockbyindustrieswithuser database: 
## Setting up the virtual environment: 
1. Set up the vagrant virtual environment
2. Move the Vagrantfile into the vagrant folder 
4. Open a terminal ("Git Bash" for Windows or Terminal for Linux/Mac) (after installing Vagrant and VirtualBox)
5. Cd (Change Directory) into fullstack-nanodegree-vm/vagrant
6. Type "vagrant up" 
7. Wait for initialization the virtual machine. 
8. Type "vagrant ssh" to log into the virtual machine 
9. Type "python lotsofstocks.py" to run the database setup file. This may take a 30 seconds to a minute to load since it grabs stock price data from online. 

#Running the Server
1. With Git Bash open and having ran both vagrant up and vagrant ssh type, "python finalProject.py" to run the server.
2. Open a web browser with the address "http://localhost:5000" to access the server.
3. The server is now running. 






