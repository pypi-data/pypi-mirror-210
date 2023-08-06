# defense

The goal of this project is to visualize military spending of countries.

Using a SIPRI dataset, milspend can visualize military spending of up to four countries.

The SIPRI dataset is downloadable from:

https://sipri.org/sites/default/files/SIPRI-Milex-data-1949-2020_0.xlsx

The number of the vertical axis indicates the US dollars in millions.

<img src='https://github.com/ytakefuji/defense/raw/main/result.png' width=640 height=480>

# How to install milspend
You may need matplotlib library.

$ pip install matplotlib

$ pip install milspend

# How to run milspend
Milspend program allows user to specify up to four countries to plot military spending of the specified countries.
For example, the following command can display military spending of the US, China, Russia and Japan in the graph.

$ milspend USA China Russia Japan

<img src='https://github.com/ytakefuji/defense/raw/main/uscnrujp.png' height=480 width=640>
The following command can display military spending of Japan and South Korea.

$ milspend Japan 'Korea, South'

<img src='https://github.com/ytakefuji/defense/raw/main/koreajapan.png' height=480 width=640>

