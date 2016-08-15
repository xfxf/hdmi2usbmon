hdmi2usbmon api
===============

Introduction
------------

*The API described in this document is currently a moving target.*

This document is intended to document the formal api of the hdmi2usbmon api.
The method by which the api is delivered will vary depending upon the medium employed,
but the fundamental api should be roughly equivalent.

**hdmi2usbd** is a daemon written in C that attaches to the device and provides the
ability to reliably multiplex communications with the device with one or more clients
that connect via the network.

hdmi2usbmon is a python module that uses the hdmi2usbd daemon to monitor and
control a HDMI2USB device, such as the Numato Opsis. It provides a interface
layer that supports the following functionality:

* start the **hdmi2usbd** daemon if required
* connect to **hdmi2usbd** and determine initial device status
* adjust device settings as required for monitoring purposes
* provide an event framework with callbacks based on event type to service:
  - synchronous requests for status (request)
  - asynchronous updates on status changes (callbacks)

hdmi2usbmon provides only the api endpoint and not the view.
Delivery of the api is currenly provided as a logging example only.

Python API
----------
The fundamental level of the monitor API design deals with python objects.

The API is split into two major categories:

* The **Request API** deals in specific request or query based API, where the
  client obtains a synchronous response after sending a request
* The **Callback API** deals in calling user code when specific (or all) events occur.

A web implementation of this API will use json formatted responses to effectively
serialise those python objects.
The Request API returns json responses to web requests.
The Callback API emits callback events over web sockets.


Request API
-----------

This section describes the query API; that is, those parts of the API which are
in a standard query/response format used for device discovery.
All of the request API is implemented in a single class, each request having a
corresponding method in the hdmi2usbmon.Hdmi2UsbDe
