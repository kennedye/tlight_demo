# Raspberry Pi traffic light Kubernetes demo

This is a (very) simple sample project to demonstrate running a Python script that accesses a Raspberry Pi's GPIO pins within a Kubernetes (k3s in this case) cluster running on Raspberry Pis. 

## The basics

I happened to have a collection of three Raspberry Pi 3Bs lying around (I know, I should have sold them right?) without a project to use on them. I also happened to have two of [these](https://lowvoltagelabs.com/products/pi-traffic/) mini-traffic light boards from Low Voltage Labs without a project for them as well. Since I'm in the middle of studying for the CKA exam, inspiration struck: how about combining all three?

## The plan

Step one is to set up a Kubernetes cluster using the three Pis; there's plenty of documentation on doing so online, I chose to set up a [k3s](https://k3s.io) cluster using the 64-bit version of [Rasperry Pi OS Lite](https://www.raspberrypi.com/software/operating-systems/) so that I can easily build `aarch64` images from my M1 Mac. (One thing that's not mentioned in the guides I found: don't rely on DNS resolution via `avahi-daemon` as apparently it's not supported by Go's internal libraries, and therefore Kubernetes's. Use IP addresses or host entries instead.)

Step two is the Python script located elsewhere in the repo. It is a very simple script that just loops through all three lights, illuminating each one for a second. It runs until interrupted by a Control-C or `SIGINT` signal. Because the traffic light board can be connected in two different places on a standard 40-pin Pi board, and to demonstrate environment variable use, the script reads the pin values from the Kubernetes pod deployment YAML.

Step three is to push the script into a CRI-compatible container image, in this case by just building it using the supplied Dockerfile and uploading to Docker Hub. For simplicity's sake I used a pretty fat base image, there's a lot of optimization that could be done here to produce a smaller container.

Step four is the PodSpec YAML file, which in this case just launches a single Pod onto a node. As noted [here](https://ikarus.sg/kubernetes-with-k3s/) k3s does not automatically prevent workloads from launching on the control-plane node, and since only two of the three Pis have the traffic light module on them, I used the `kubectl taint` command suggested on that page to make sure the pod only runs on the two worker nodes. The PodSpec is fairly basic, just downloading the container image from Docker Hub and giving it the environment variables representing which GPIO pins to use. A couple of notes about the spec:
- the pod is marked as running in `privileged` context, which unfortunately is necessary to allow access to the GPIO header from within the container. There are reportedly [ways around this](https://stackoverflow.com/questions/30059784/docker-access-to-raspberry-pi-gpio-pins) for plain Docker but I haven't been able to get them to work within k3s yet. **Don't run containers in privileged mode in production** if you can help it.
- there's a `preStop` hook that gives the script a chance to turn off the GPIO pins before the pod halts, otherwise one of the lights could remain on even after termination.

## The future

So it all works remarkably well, even over the Pi's built-in wifi, but it's not exactly practical to just cycle through three lights over and over. Ideally the lights would be hooked up to some sort of [Flask app](https://flask.palletsprojects.com) that would let me set the lights programmatically, although in response to what I couldn't exactly say yet. That's tomorrow's problem anyway. (It also involves learning Flask, which doesn't look easy.) Also, the PodSpec probably ought to be worked up into either a full-on deployment or a DaemonSet similar to [this really cool project](https://github.com/apprenda/blinkt-k8s-controller) to show how many pods are running on a given Pi. Plus, you know, more Pis to make a bigger/better/more redundant cluster, but given how hard it is to find Pi 4s these days that's definitely not happening for a while. Besides, I also have a Pi 2 with a [Unicorn HAT HD](https://www.adafruit.com/product/3580) on it that I need to figure out how to use. Making a cluster of those is left as an exercise for the reader.
