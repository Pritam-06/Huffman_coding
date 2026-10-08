Huffman Source Coding Digital Communicator

A simple Python project that demonstrates Huffman source coding along with TCP socket communication between a transmitter and receiver.

Features
Huffman encoding and decoding
Character frequency and probability calculation
Compression metrics and efficiency report
TCP-based data transmission
Transmitter and receiver modes
Local loopback demonstration
Requirements
Python 3.x
No external libraries required
How to Run
python filename.py


Choose one of the following modes:

Receiver – Waits for a Huffman-encoded message from another device.
Transmitter – Compresses entered text and sends it to the receiver.
Local Loopback – Demonstrates Huffman encoding on a single device.
Network Usage

First run the program on the receiver device and select Option 1.

Then run it on the transmitter device, select Option 2, and enter the receiver's IP address.

The default TCP port is 5000.

Example
Enter text to compress & transmit: HELLO WORLD


The program displays:

Character frequencies
Huffman codes
Encoding trace
Encoded bitstream
Compression ratio
Bandwidth savings
Source coding efficiency
Project Purpose

This project is intended as a simple demonstration of source coding, data compression, and digital communication using Python sockets.
