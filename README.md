
# Corgi-OS 1.0 🐕🐶
# Corgi-OS is still in development expect issues.
> If there are any issues please submit them to our [issues page](https://github.com/ILikeLinux123/Corgi-OS/issues)

## About:

Corgi-OS is a makeshift Linux distro (please do not attempt to install on a computer)
I am really hoping i can make it so it is bootable on an actual computer
This is a project i have been working on for months and over 3000 lines of code,
all of this has been writen in python including all commands

# Installation:
## Corgi-OS comes with an installer script but for that you need the python requests module and tkinter python library
> Read below too see how to install them

To install Corgi-OS you need at least Python 3.10 (latest version recommended)

## Windows

```
py -m pip install psutil requests pyreadline3
```

### Debian/Ubuntu (or anything that uses apt)

```
sudo apt update && sudo apt install -y python3-tk && python3 -m pip install psutil requests
```

### Arch

```
sudo pacman -Syu --needed tk python-pip && python -m pip install psutil requests
```

### After that run the [installer.py script](https://github.com/ILikeLinux123/Corgi-OS/blob/main/installer.py)

### Or if you dont want to use the installer just simply run the main.py in the same directory as every other file

## Features

-  Custom Corgi Shell
-  Virtual filesystem
-  Multiple user accounts
-  Login system
-  Kernel system
-  Custom commands
-  Filesystem refresh system
-  Built-in installer
-  Corgi kernel panic messages

# Future Update plans

- Make it more in depth and customizable
- Get paw app manager working
- Fix bugs (obviously)
- More Programing Languages supported
- And more!

# Showcase
> Showcase of the neofetch from Corgi-OS on my system which is a Windows computer

<img width="1280" height="720" alt="2026-07-23 22-35-33" src="https://github.com/user-attachments/assets/210726fe-b0e4-47ce-8962-18ac75179b89" />
