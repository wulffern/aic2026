footer: Carsten Wulff 2025
slidenumbers:true
autoscale:true
theme: Plain Jane, 1
text:  Helvetica
header:  Helvetica
date: 2025-01-01

<!--pan_title: Sky130nm tutorial -->

**Status:** 1.0

<!--pan_doc: <iframe width="560" height="315" src="https://www.youtube.com/embed/YoJCkAmBo44?si=3xzkkX-U4_HSl49A" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe> -->

# Tools

I would strongly recommend that you install all tools locally on your system. 

<iframe width="400" height="315" src="https://www.youtube.com/embed/DRppsdjo2Rc" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

For the analog toolchain we need some tools, and a process design kit (PDK).

- [Skywater 130nm PDK](https://github.com/google/skywater-pdk). I use [open_pdks](https://github.com/RTimothyEdwards/open_pdks) to install the PDK
- [Magic VLSI](https://github.com/RTimothyEdwards/magic) for layout
- [ngspice](https://git.code.sf.net/p/ngspice/ngspice) for simulation 
- [netgen](https://github.com/RTimothyEdwards/netgen.git) for LVS
- [xschem](https://github.com/StefanSchippers/xschem)
- python > 3.10

The tools are not that big, but the PDK is huge, so you need to have about 50 GB
disk space available. 

## Setup WSL (Applicable for Windows users)

Install a Linux distribution such as Ubuntu 24.04 LTS by running the following command in PowerShell on Windows and follow the instructions.
```bash
wsl --install -d Ubuntu-24.04
```

When you have installed the Linux distribution and  signed into it, install make

```bash
sudo apt install make
```


## Setup public key towards github

Do 

```bash
ssh-keygen -t rsa
```

And press "enter" on most things, or if you're paranoid, add a passphrase

Then 
```bash 
cat ~/.ssh/id_rsa.pub 
```

And add the public key to your github account. Settings - SSH and GPG keys 

## Provide git with author identity

There are interactions with git that require an author identity. You are supposed to use one of these interactions a lot during the project, namely, ```git commit```. What you need to provide is an email address and a name. If you would like to keep your real email address private/secret, read what it says on GitHub at your user settings page under [emails](https://github.com/settings/emails). Use the below commands to provide the author identity information to git.

```bash
git config --global user.email "you@example.com"
git config --global user.name "Your Name"
```

## Get AICEX and setup your shell 

You don't have to put aicex in `$HOME/pro`, but if you don't know where to put
it, chose that directory.

```bash
cd 
mkdir pro 
cd pro
git clone --recursive https://github.com/wulffern/aicex.git
```

You need to add the following to your `~/.bashrc` (note that `~` refers to your
home directory `$HOME/.bashrc` also works, or `$HOME/.bash_profile` on some
newer macs) 

```bash
export PDK_ROOT=/opt/pdk/share/pdk
export LD_LIBRARY_PATH=/opt/eda/lib
export PATH=/opt/eda/bin:$HOME/.local/bin:$PATH
```

## On systems with python3 > 3.12

On newer systems it's not trivial to install python packages because python is
externally managed. As such, we need to install a python environment.

```bash 
#- Find a package similar to name below
sudo apt-get update
sudo apt install python3.12-venv
sudo mkdir /opt
sudo mkdir /opt/eda
sudo mkdir /opt/eda/python3
sudo chown -R $USER:$USER /opt/eda/python3/
python3 -m venv /opt/eda/python3
```

Modify the `~/.bashrc` to include the python environment

```bash
export PATH=/opt/eda/bin:/opt/eda/python3/bin:$HOME/.local/bin:$PATH
```



## Install Tools

Make sure you load the settings before you proceed

```bash
source ~/.bashrc
```
Hopefully the commands below work, if not, then try again, or try to understand
what fails. There is no point in continuing if one command fails. 


```bash
cd aicex/tests/
make requirements
make tt
```

On a mac, you probably need to add bison to the path

```bash
export PATH="/opt/homebrew/opt/bison/bin:$PATH"
```

I've split the install of each of the tools. It's possible to run the commented
out lines instead, but they often fail

```bash
#make eda_compile
#sudo make eda_install
make magic_compile  magic_install
make netgen_compile netgen_install
make xschem_compile xschem_install
make iverilog_compile iverilog_install
make ngspice_compile # Sometimes fails
make ngspice_compile ngspice_install
```

On Mac, do 

```bash 
brew install yosys verilator
```

On Linux, do 

``` bash 
make yosys_compile yosys_install
``` 

On all, do

```bash 
python3 -m ensurepip --default-pip

python3 -m pip install matplotlib numpy click svgwrite \
    pyyaml pandas tabulate wheel setuptools tikzplotlib
source install_open_pdk.sh
```

## Install cicconf 

cIcConf is used for configuration. How the IPs are connected, and what version
of IPs to get. 

``` bash
cd
cd pro/aicex/ip/cicconf
git checkout main 
git pull
python3 -m pip install -e .
cd ../
```

Update IPs

```sh
cicconf clone --https 
cd ../..
```

## Install cicsim

cIcSim is used for simulation orchestration. 

``` bash
cd aicex/ip/cicsim
python3 -m pip install -e .
cd ../..
```

---


## Setup your ngspice settings

Edit `~/.spiceinit` and add

```bash
set ngbehavior=hsa     ; set compatibility for PDK libs
set ng_nomodcheck      ; don't check the model parameters
set num_threads=8      ; CPU hardware threads available
set skywaterpdk
option noinit          ; don't print operating point data
option klu
optran 0 0 0 100p 2n 0 ; don't use dc operating point,
option opts
```

---

# Check that magic and xschem works

To check that magic and xschem works

``` sh
cd ~/pro/aicex/ip/sun_sar9b_sky130nm/work 
magic ../design/SUN_SAR9B_SKY130NM/SUNSAR_SAR9B_CV.mag &
xschem -b ../design/SUN_SAR9B_SKY130NM/SUNSAR_SAR9B_CV.sch &
```

---

# Design tutorial

<iframe width="560" height="315" src="https://www.youtube.com/embed/YoJCkAmBo44?si=PA9Td0lBYERgkOrS" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

## Create the IP 

I've made some scripts to automatically generate the IP. 

To see what files are generated, see `tech_sky130A/cicconf/ip_template.yaml`

```bash
cd aicex/ip
cicconf newip ex
```

## The file structure 
    
It matters how you name files, and store files. I would be surprised if you 
had a good method already, as such, I won't allow you to make your own folder
structure and names for things. I also control the filenames and folder
structure because there are many scripts to make your life easier (yes, really)
that rely on an exact structure. Don't mess with it. 

### Github workflows

On github it's possible use something called workflows to run things every time
you push a new version. It's really nice, since it can then check that
your design is valid. 

The grading of the milestones is determined by passing github workflows. 

We will
also check that you have not cheated, and modified the workflows just to get
them passing. 

The workflows are defined below. 

```bash
.github
   workflows  
   docs.yaml # Generate a github page 
   drc.yaml  # Run Design Rule Checks 
   gds.yaml  # Generate a GDS file from layout 
   lvs.yaml  # Run Layout Versus Schematic 
             # and Layout Parasitic Extraction
   sim.yaml  # Run a simulation 
```

### Configuration files 

Each IP has a few files that define the setup, you'll need to modify at least
the `README.md` and the `info.yaml`.

```bash
 .gitignore  # files that are ignored by git
 README.md   # Frontpage documentation 
 config.yaml # What libraries are used. Used by  cicconf
 info.yaml   # Setup names, authors etc 
 media       # Where you should store images for documentation
 tech -> ../tech_sky130A  # The technology library
``` 

### Design files 

A "cell" in the open source EDA world should consists of the following files

- Schematic (.sch)
- Layout (.mag)
- Documenation (.md)

The files must have the same name, and must be stored in `design/<LIB>/` as
shown below. 

Note there are also two symbolic links to other libraries. These two libraries
contain standard cells and standard analog transistors (ATR) that you should be using.

```bash
design
  JNW_EX_SKY130A
  JNW_EX.sch
  JNW_ATR_SKY130A -> ../../jnw_atr_sky130a/design/JNW_ATR_SKY130A
  JNW_TR_SKY130A -> ../../jnw_tr_sky130a/design/JNW_TR_SKY130A
```

For example, if the cell name was `JNW_EX`, then you would have 

- `design/JNW_EX_SKY130A/JNW_EX.sch`: Schematic (xschem)
- `design/JNW_EX_SKY130A/JNW_EX.sym`: Schematic (xschem)
- `design/JNW_EX_SKY130A/JNW_EX.mag`: Layout (Magic)
- `design/JNW_EX_SKY130A/JNW_EX.md` : Markdown documentation (any text editor)

All these files are text files, so you can edit them in a text editor, but
mostly you shouldn't (except for the Markdown)


### Simulations 

All simulations shall be stored in `sim`. Once you have a Schematic ready for
simulation, then 

```bash 
cd sim 
make cell CELL=JNW_EX
```
This will make a simulation folder for you. Repeat for all your cells. 

```bash
sim
  Makefile
  cicsim.yaml -> ../tech/cicsim/cicsim.yaml
```


### The work 

All commands (except for simulation), shall be run in the `work` folder. 

In the `work/` folder there are startup files for Xschem (xschemrc) and Magic (.magicrc).
They tell the tools where to find the process design kit, symbols, etc. At some point you probably
need to learn those also, but I'd wait until you feel a bit more comfortable.


```bash 
work
 .magicrc
 Makefile
 mos.24bit.dstyle -> ../tech/magic/mos.24bit.dstyle
 mos.24bit.std.cmap -> ../tech/magic/mos.24bit.std.cmap
 xschemrc
```

## Github setup

Create a repository on [github](https://github.com).
The name of the repository that you make on GitHub has to be the same as what is written after ```<your username>``` in the last command below. In this example, that is ```jnw_ex_sky130a```.


``` bash
cd jnw_ex_sky130a
git remote add origin \
 git@github.com:<your username>/jnw_ex_sky130a.git
```

## Start working 

### Edit README.md

Open README.md in your favorite text editor and make necessary changes.

### Familiarize yourself with the Makefile and make

I write all commands I do into a Makefile. There is nothing special with a Makefile, it's just what I choose
to use 20 years ago. I'm not sure I'd choose something different now.

``` bash
cd work
make
```

Take a look inside the file called Makefile.

## Draw Schematic <a name="sch"></a>

The block we'll make is a current mirror with a 1 to 4 scaling. 

A schematic is how we describe the connectivity, and the types of devices in an
analog circuit. The open source schematic editor we will use is XSchem.

Open the schematic:

```bash
xschem -b ../design/JNW_EX_SKY130A/JNW_EX.sch &
```

### Add Ports

Add IBPS\_5U and IBNS\_20U ports, the P and N in the name signifies what
transistor the current comes from. So IBPS must go into a diode connected NMOS,
and N will be our output, and go into a diode connected PMOS somewhere else.

### Add transistors

Use 'I' or 'Shift+i' (note the letter case) to open the library manager. Click the `jnw_ex_sky130A/design`
path, then `JNW_ATR_SKY130A` and select `JNWATR_NCH_4C5F0.sym`

The naming convention for these transistors is `<number of contacts on
drain/source>C<times minimum gate length>F`, so the number before the C is the width,
and the number before/after the F is the length. The absolute size does not matter for now.
Just think "4C5F0 is a 4 contact wide long transistor", while a "4C1F2 is a 4
contact wide, short transistor".

Select the transistor and press 'c' to copy it, while dragging, press 'shift-f'
to flip the transistor so our current mirror looks nice. 'shift-r' rotates the
transistor, but we don't want that now.

Press ESC to deselect everything

Select the input transistor, and change the name to 'xi'

Select the output transistor, and change the name to 'xo[3:0]'. Using bus
notation on the name will create 4 transistors

Select ports, and use 'm' to move the ports close to the transistors.

Press 'w' to route wires.

Use 'shift-z' and z, to zoom in and out

Use 'f' to zoom full screen

Remember to save the schematic

![](../media/JNW_EX0.svg)

### Netlist schematic

Check that the netlist looks OK

In work/
``` bash
make xsch CELL=JNW_EX
cat xsch/JNW_EX.spice
```

---

## Typical corner SPICE simulation <a name="simschtyp"></a>

I've made [cicsim](https://github.com/wulffern/cicsim) that I use to run simulations (ngspice) and extract
results

### Setup simulation environment
Navigate to the `jnw_ex_sky130a/sim/` directory.

Make a new simulation folder

``` bash
cicsim simcell  JNW_EX_SKY130A JNW_EX \
    ../tech/cicsim/cell_spice/template.yaml
```

I would recommend you have a look at simcell_template.yaml file to understand what happens.

### Familiarize yourself with the simulation folder

I've added quite a few options to cicsim, and it might be confusing. For
reference, these are what the files are used for

| File         | Description                                       |
|--------------|---------------------------------------------------|
| Makefile     | Simulation commands                               |
| cicsim.yaml  | Setup for cicsim                                  |
| summary.yaml | Generate a README with simulation results         |
| tran.meas    | Measurement to be done after simulation           |
| tran.py      | Optional python script to run for each simulation |
| tran.spi     | Transient testbench                               |
| tran.yaml    | What measurements to summarize                                                   |


The default setup should run, so

``` bash
cd JNW_EX
make typical
```

### Modify default testbench (tran.spi)

Delete the VDD source

Add a current source of 5uA, and a voltage source of 1V to IBNS_20U

``` spice
IBP 0 IBPS_5U dc 5u
V0  IBNS_20U 0 dc 1
```

Save the current in V0 by adding i(V0) to the save statement in the testbench

Save the voltage by adding v(IBPS_5U) to the save statement

```spice 
.save i(V0) v(IBPS_5U)
```

### Modify measurements (tran.meas)

Add measurement of the current and VGS. It must be added between the
"MEAS_START" and "MEAS_END" lines.

``` spice
let ibn = -i(v0)
meas tran ibns_20u find ibn at=5n
meas tran vgs_m1 find v(ibps_5u) at=5n
```

Run simulation

``` bash
make typical
```
and check that the output looks okish. 

Try to run the simulation again 

``` bash
make typical
```

If everything works, then the simulation now should **not** be run. Every time
cicsim runs (provided the `sha: True` option is set in `cicsim.yaml`) cicsim will 
compute a SHA hash of all files (stored in output_tran/*.sha*) that is
referenced in the `tran.spi`. Next time cicsim is run, it checks the hash's and
does not re-run if there is no need (no files changed). 

Sometimes you want to force running, and you can do that by 

```bash 
make typical OPT="--no-sha"
```
 
Often, it's the measurement that I get wrong, so instead of rerunning simulation every time
I've added a "--no-run" option to cicsim. For example

``` bash
make typical OPT="--no-run"
```

will skip the
simulation, and rerun only the measurement. This is why you should split the testbench and the
measurement. Simulations can run for days, but measurement takes seconds.

### Modify result specification (tran.yaml)

Add the result specifications, for example

``` yaml
ibn:
  src:
    - ibns_20u
  name: Output current
  min: -20%
  typ: 20
  max: 20%
  scale: 1e6
  digits: 3
  unit: uA

vgs:
  src:
    - vgs_m1
  name: Gate-Source voltage
  typ: 0.6
  min: 0.3
  max: 0.7
  scale: 1
  digits: 3
  unit: V
```

Re-run the measurement and result generation

``` bash
make typical OPT="--no-run"
```

Open `result/tran_Sch_typical.html`


### Check waveforms

You can either use ngspice, or you can use cicsim, or you can use something I
don't know about 

Open the raw file with 

``` bash
cicsim wave output_tran/tran_SchGtKttTtVt.raw 
```

Load the results, and try to look at the plots. There might not be that much
interesting happening 

---

## All corners SPICE simulations <a name="simschcorner"></a>

Analog circuits must be simulated for all physical conditions, we call them corners.
We must check high and low temperature, high and low voltage, all process corners, and device-to-device mismatch.

For the current mirror we don't need to vary voltage, since we don't have a VDD.

### Remove Vh and Vl corners (Makefile)
Open Makefile in your favorite text editor.

Change all instances of "Vt,Vl,Vh" and "Vl,Vh" to Vt


### Run all corners
To simulate all corners do

``` bash
make typical etc mc
```

where etc is extreme test condition and mc is monte-carlo.

Wait for simulations to complete.


### Get creative with python

Open `tran.py` in your favorite editor, try to read and understand it.

The `name` parameter is the corner currently running, for example `tran_SchGtAmcttTtVt`.

The measured outputs from ngspice will be added to `tran_SchGtAmcttTtVt.yaml`

Delete the "return" line.

Add the following lines (they automatically plot the current and gate voltage)

```python
import cicsim as cs
fname = name +".png"
print(f"Saving {fname}")
cs.rawplot(name + ".raw","time","v(ibps_5u),i(v0)" \
  ,ptype="",fname=fname)
```

Re-run measurements to check the python code

```bash
make typical etc mc OPT="--no-run"
```

You'll see that cicsim writes all the png's. Check with `ls -l output_tran/*.png`.

You'll also notice it will slow down the simulation, so maybe remove the lines
from `tran.py` again ;-) 

### Generate simulation summary

Run

``` bash
make summary
```

Install [pandoc](https://pandoc.org) if you don't have it

Run

``` bash
pandoc -s  -t slidy README.md -o README.html
```

to generate a HTML slideshow that you can open in browser. Open the HTML file.

### Viewing results without GUI browser 

If your on a system without a browser, or indeed a GUI, then it's possible to
view the results in the terminal.

Check if `lynx` is installed, if it's not installed, then 

On linux
```bash
sudo apt-get install lynx
```

On Mac
```bash
brew install lynx
```

Then 

```bash
lynx README.html
```

### Think about the results

From the corner and mismatch simulation, we can observe a few things.

- The typical value is not 20 uA. This is likely because we have a M2 VDS of 1 V, which is not the same
  as the VDS of M1. As such, the current will not be the same.
- The statistics from 30 corners show that when we add or subtract 3 standard deviation from the mean,
  the resulting current is outside our specification of +- 20 %. I'll leave it up to you to fix it.

---

## Draw Layout <a name="layout"></a>


A foundry (the factory that makes integrated circuits) needs to know how we want
  them to create our circuit. So we need to provide them with a "layout", the
  recipe, or instruction, for how to make the circuit. Although the layout
  contains the same components as the schematic, the layout contains the
  physical locations, and how to actually instruct the foundry on how to make
  the transistors we want.


Open Magic VLSI

``` bash
cd work
magic ../design/JNW_EX_SKY130A/JNW_EX.mag
```

Now brace yourself, Magic VLSI was created in the 1980's. For it's time it was extremely modern,
however, today it seems dated. However, it is free, so we use it.

### Magic VLSI

Try google for most questions, and there are youtube videos that give an intro.

- [Magic Tutorial 1](https://www.youtube.com/watch?v=ORw5OaY33A4&t=9s)
- [Magic Tutorial 2](https://www.youtube.com/watch?v=NUahmUtY814)
- [Magic Tutorial 3](https://www.youtube.com/watch?v=OKWM1D0_fPI)
- [Magic command
  reference](http://opencircuitdesign.com/magic/commandref/commands.html)
- [Magic Documentation](https://analogicus.com/magic/)

Default magic start with the BOX tool. Mouse left-click to select bottom corner,
left-click to select top corner.

Press "space" to select another tool (WIRING, NETLIST, PICK).

Type "macro help" in the command window to see all shortcuts

| Hotkey      | Function                          |
|-------------|-----------------------------------|
| v           | View all                          |
| shift-z     | zoom out                          |
| z           | zoom in                           |
| x           | look inside box (expand)          |
| shift-x     | don't look inside box  (unexpand) |
| u           | undo                              |
| d           | delete                            |
| s           | select                            |
| Shift-Up    | Move cell up                      |
| Shift-Down  | Move cell down                    |
| Shift-Left  | Move cell left                    |
| Shift-Right | Move cell right                   |


### Add transistors

Open Cell -> Place Instance. Navigate to the right transistor.

Place it. Hover over the transistor and select it with 's'. Now comes a bit of
tedious thing. Select again, and copy. It's possible to align the transistors
on-top of eachother, but it's a bit finicky.

Place all transistors on top of each other.

![](../media/placement.png)

### Add Ground

In the command window, type

```tcl
see no *
see viali
see locali
see m1
see via1
see m2
```

Change to the 'wire tool' with spacebar. Press the top transistor 'S' and draw
all the way down to connect all of the transistors' source terminals. 

Change grid to 0.5 um.

Select a 0.5 um box below the transistors and paint the rectangle with locali (middle click on locali)

Connect guard rings to ground. Use the 'wire tool'

Connect the sources to ground. Use the 'wire tool'. Use 'shift-right click' to
change layer down 

![](../media/ground.png)

### Route Gates

Press "space" to enter wire mode. Left click to start a wire, and right click to end the wire.

The drain of M1 transistor needs a connection from gate to drain. We do that
for the middle transistor.

Start the route, press 'shift-left click' to go up one layer, route over to
drain, and 'shift-right click' to go down.

![](../media/gates.png)

### Drain of M2

Use the wire tool to draw connections for the drains.

To add vias you can do "shift-left click" to move up a metal, and "shift-right click" to go down.

![](../media/drains.png)

### Add labels

Select a box on a metal, and use "Edit->Text" to add labels for the ports.
Select the port button.

---

## Layout verification <a name="ver"></a>

The DRC can be seen directly in Magic VLSI as you draw.

To check layout versus schematic navigate to work/ and do

``` tcl
make cdl lvs
```

If you've routed correctly, then the LVS should be correct. 

![](../media/layout.png)


---

## Extract layout parasitics <a name="lpe"></a>

With the layout complete, we can extract parasitic capacitance.

``` bash
make lpe
```

Check the generated netlist

``` bash
cat lpe/JNW_EX_lpe.spi
```

---

## Simulate with layout parasitics <a name="simlpe"></a>

Navigate to sim/JNW_EX. We now want to simulate the layout.

The default `tran.spi` should already have support for that.

Open the Makefile, and change

```bash
VIEW=Sch
```

to

```bash
VIEW=Lay
```

### Typical simuation

Run

```bash
make typical
```

### Corners
Navigate to sim/JNW_EX. Run all corners again

``` bash
make all
```

### Simulation summary

Open `summary.yaml` and add the layout files.

``` yaml
      - name: Lay_typ
        src: results/tran_Lay_typical
        method: typical
      - name: Lay_etc
        src: results/tran_Lay_etc
        method: minmax
      - name: Lay_3std
        src: results/tran_Lay_mc
        method: 3std
```

Run summary again

```bash
make summary
pandoc -s  -t slidy README.md -o README.html
```

Open the README.html and have a look a the results. The layout should be close
to the schematic simulation. 

## Make documentation 

Make a file (or it may exists) `design/JNW_EX_SKY130A/JNW_EX.md` and add some
docs. 

## Edit info.yaml 

Finally, let's setup the `info.yaml` so that all the github workflows run
correctly. 

Mine will look like this. 

You need to setup the url (probably something like `<your username>.github.io`)
to what is correct for you.

I've added the doc section such that the workflows will generate the docs. 

The sim is to run a typical simulation. 

```yaml
library: JNW_EX_SKY130A
cell: JNW_EX
author: Carsten Wulff
github: wulffern
tagline: The answer is 42
email: carsten@wulff.no
url: analogicus.github.io
doc:
  libraries:
    JNW_EX_SKY130A:
      - JNW_EX
sim:
  JNW_EX: make typical
```

## Setup github pages 

Go to your GitHub repository (repo). Press Settings. Press Pages. Choose source under Build and Deployment  ->
GitHub Actions

Wait for the workflows to build. And check your github pages. 
Mine is [https://analogicus.github.io/jnw_ex0_sky130a/](https://analogicus.github.io/jnw_ex0_sky130a/).


## Frequency asked questions

*Q:*  My GDS/LVS/DRC action fails, even though it works locally. 

Sometimes the reference to the transistors in the magic file might be wrong.
Open the .mag file in a text editor and check. The correct way is 

```sh
use JNWATR_NCH_4C5F0  JNWATR_NCH_4C5F0_0 ../JNW_ATR_SKY130A
```

It's the last `../JNW_ATR_SKY130A` that sometimes is missing.




