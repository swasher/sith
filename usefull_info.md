[CPU socket](https://en.wikipedia.org/wiki/CPU_socket)

==================================================

ark dependencies
Installing collected packages: arksearch, click, beautifulsoup4, requests, terminaltables

AMD Info:

http://www.cpu-world.com/CPUs/Bulldozer/AMD-A8-Series%20A8-7650K.html

http://products.amd.com/en-us/search?k=DesktopProcessors#k=a8-7650K
--->
http://products.amd.com/en-us/search/APU/AMD-A-Series-Processors/AMD-A8-Series-APU-for-Desktops/A8-7650K-with-Radeon%E2%84%A2-R7-Graphics-and-Near-Silent-Thermal-Solution/176

По Intel Ark
============================

- Recommended Customer Price (RPC) - это примерная цена, указанная для 1000 юнитов. Если две цены, это OEM/BOX
- Отсутствует инфа Microarchitecture (Codename) - Haswell, Skylake, etc
- На вкладке Ordering можно найти Spec code (SR14E) и Ordering code (BX80646I54570), которые точно определяют процессор.

Linux hardware info
============================

lscpu
------------------------------
Usage: lscpu

Info about cpu. Useful info:
    Model name:            Intel(R) Core(TM) i7-4770 CPU @ 3.40GHz

That's all.


*** lshw
------------------------------
Usage: sudo lshw -json > report.json

Info about varios components. Useful info:


lspci, lsscsi, lsusb, lsblk
-----------------------------------
Отчет про устройства на шине PCI, SCSI, USB и block devices. Мало полезно для моих целей.
С usb можно попробовать вытянуть мышь и клаву


*** hwinfo
-------------------------------
Very detailed info. Article about usage: http://www.binarytides.com/linux-hwinfo-command/

Может быть имеет смысл не парсить весь вывод, а отдельные команды типа `hwinfo --short --cpu`



*** dmidecode
-----------------------------------
Very detailed info:
- Memory manufacturer

*** hdparm
-----------------------------------
sudo hdparm -I /dev/sda
sudo hdparm -i /dev/sda


LINKS
=====================================

Пример стайлинга бутстрап табов
http://jsfiddle.net/KyleMit/2VmmW/
