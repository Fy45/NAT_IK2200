Welcome to the IK2200_NAT wiki!

<!-- GFM-TOC -->
* [Introduction](#Introduction)
* [1. Profiling of NAT performance](#1-Profiling-NAT-performance)
<!-- GFM-TOC -->
# Introduction
This wiki contains the brief explanation of our single core NAT system performance test and possible implementation of multi-core NAT system.
# 1. Profiling of NAT performance
## 1.1 Linux Perf tool
During the profiling stage of our project, we choose the [Perf tool](https://perf.wiki.kernel.org/index.php/Tutorial#Introduction) as our powerful performance counter, the perf tool contains multiple different functions, we apply specifically 3 different functions in our test:

``` perf record -ag -e cycles -o data/name_of_flow.data  -- sleep 100``` 

This command with several parameters has the job to analyze the whole system CPUs performance for 100 seconds, taking CPU cycles event as metrics and keep the extra calling relationship between different stacks/functions. This will reveal the performance bottleneck on certain functions easily.

``` perf report -i data/name_of_flow.data -n --stdio --no-children -s pid ```

After we kept the record as name_of_flow.data we can analyze the CPU utilization status we collect sorted by the process without the child function. For readability, the command counts the percentage of each call stack and then ranks from high to low. 

``` perf top -p pid -e event_name ```
Finally, we could view the real-time performance for the specific event of the certain process.

## 1.2 FlameGraphs
*****Only using the Perf tool won't show our result vividly based on our own test cases*****

As we want to compare the performance of our middle system with and without NAT running in the KVM, so there will be a change trend of our profiling result. In that case, we found a plotting tool named [FlameGraphs](http://www.brendangregg.com/flamegraphs.html), with the help of ```perf script``` to generate the graphs for the system changes as we desired. The whole figure looks like a beating flame, which is the origin of its name. Burning at the tip of the flame is the operation that the CPU is performing, but it should be noted that the color is random and has no special meaning. The vertical indicates the depth of the call stack, and the horizontal indicates the time consumed. Because the call stack is sorted alphabetically in the horizontal direction, and the same call stack will be merged, the larger the width of a grid, the more likely it is to be a bottleneck.

All the plots are stored in ```IK2200_NAT/Profiling Plot/ ```, we carried out 2 separated transport protocols with a different number of flows per set and generated its flamegraphs as the tool provided us.

The command line we use is:

```perf script -i data/name_of_flow.data | FlameGraph/stackcollapse-perf.pl | FlameGraph/flamegraph.pl > graphs/name_of_flow.svg ```

Conveniently, it's a combined line, * for the first part of this command we use ```perf script``` to analyze the perf data and create the collapsed call stack file.* Then use ```stackcollapse-perf.pl``` in FlameGraphs to collapse the symbols the former file, from folded file to unfolded one.*  Finally, we generate the flame graph in _.svg_ format.

**SVG** (Scalable Vector Graphics) format of figures is designed as an interactive figure, it has lots of useful functions. For example, it can zoom in/out the whole graph; and with mouse click/fly on a certain box, it will show the function and its percentage of CPU utilization. Here we show the Plot of 50 TCP streams transmitting without/with NAT as an example, you can browse others in our repository:


<p align="center">__50 streams of TCP flow without NAT__</p>

![50 streams of TCP flow](https://rawgit.com/Fy45/NAT_IK2200/master/plot/Profiling%20Plot/tcp/tcp_50.svg)

<p align="center">__50 streams of TCP flow with NAT__</p>

![NAT](https://rawgit.com/Fy45/NAT_IK2200/master/plot/Profiling%20Plot/tcp/nat_tcp_50.svg)

It's obviously to obtain from the graphs that the transmitting process using NAT is taking more of CPU performance than without NAT in the middle.

## 1.3 Differential Plot

As I claimed in the previous section, we want to see the tendency of CPU utilization on different functions for comprehensive analysis. So we introduce the [Differential Flame Graphs](http://www.brendangregg.com/blog/2014-11-09/differential-flame-graphs.html) into our graph analysis.

In the ordinary FlameGraphs, it only indicates the function of the top layer which occupies the largest width. As long as there is a "plateaus", it means that the function may have performance problems.

However, in order to deal with the performance regression problem, it is necessary to continuously switch the contrast between the flamegraph before and after the modification or in different periods and scenes to find out the problem. The red/blue differential flame graphs use two colors to indicate the state, the red indicates the growth, blue indicates attenuation. The principle of coloring is that if the stack frame appears more frequently in ```name_of_flow2. data```, it is marked in red, otherwise, it is marked in blue. The color is filled according to the difference before and after the modification.

In this part, we use the command lines shown below:

```perf script -i data/name_of_flow.data | FlameGraph/stackcollapse-perf.pl > name_of_flow.folded ```

and

```FlameGraph/difffolded.pl -n name_of_flow2.folded name_of_flow1.folded | FlameGraph/flamegraph.pl --negate > graphs/diff.svg ```

The first line has the same effect as we produce the flamegraph, and the latter one has the meaning of when using the differential flamegraph function for generation, ``` --negate``` is to reverse the color scheme, and transpose of the two .fold files is to based on the pre-modification profile file, and the color of the graph indicates what will happen.

So in this following graph, the width of the figure is as same as the flamegraph when the 50 flows of TCP transmission without NAT. The red boxes are the functions that will increase the usage of CPU while blue boxes functions will decreasing when we have NAT running.

<p align="center">__50 streams of TCP flow Differential FlameGraph__</p>

![Differential plot of TCP](https://rawgit.com/Fy45/NAT_IK2200/master/plot/Profiling%20Plot/tcp/diff-50_tcp.svg)


***
To be continued...