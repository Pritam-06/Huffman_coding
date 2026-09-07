import socket
import json
import struct
import math
import heapq
from collections import Counter

# =====================================================================
# 1. HUFFMAN SOURCE CODING MODULE
# =====================================================================

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def build_huffman_tree(text):
    if not text:
        return None, {}
    freq_map = dict(Counter(text))
    heap = [HuffmanNode(char, freq) for char, freq in freq_map.items()]
    heapq.heapify(heap)

    if len(heap) == 1:
        root = HuffmanNode(None, heap[0].freq)
        root.left = heap[0]
        return root, freq_map

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        parent = HuffmanNode(None, left.freq + right.freq)
        parent.left = left
        parent.right = right
        heapq.heappush(heap, parent)

    return heap[0], freq_map

def generate_codes(root, current_code="", codes=None):
    if codes is None:
        codes = {}
    if root is None:
        return codes
    if root.char is not None:
        codes[root.char] = current_code if current_code else "0"
        return codes
    generate_codes(root.left, current_code + "0", codes)
    generate_codes(root.right, current_code + "1", codes)
    return codes

def rebuild_tree_from_freq(freq_map):
    heap = [HuffmanNode(char, freq) for char, freq in freq_map.items()]
    heapq.heapify(heap)
    if len(heap) == 1:
        root = HuffmanNode(None, heap[0].freq)
        root.left = heap[0]
        return root
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        parent = HuffmanNode(None, left.freq + right.freq)
        parent.left = left
        parent.right = right
        heapq.heappush(heap, parent)
    return heap[0]

def compress(text, codes):
    return "".join(codes[char] for char in text)

def decompress(encoded_text, freq_map):
    if not encoded_text or not freq_map:
        return ""
    root = rebuild_tree_from_freq(freq_map)
    decoded = []
    curr = root
    if root.char is not None:
        return root.char * len(encoded_text)
    for bit in encoded_text:
        curr = curr.left if bit == '0' else curr.right
        if curr.char is not None:
            decoded.append(curr.char)
            curr = root
    return "".join(decoded)

# =====================================================================
# 2. STEP-BY-STEP DISPLAY & METRICS REPORT (USED ON BOTH DEVICES)
# =====================================================================

def display_conversion_report(node_title, text, encoded_bitstream, freq_map):
    total_chars = len(text)
    root = rebuild_tree_from_freq(freq_map)
    codes = generate_codes(root)

    print("\n" + "=" * 70)
    print(f" {node_title.upper()} - STEP-BY-STEP HUFFMAN CONVERSION REPORT")
    print("=" * 70)

    # STEP 1: Probability & Code Allocation Table
    print("\n--- STEP 1: CHARACTER PROBABILITY & CODE ALLOCATION ---")
    print(f"{'Symbol':<10}{'Count':<8}{'Probability (p_i)':<20}{'Huffman Code':<16}{'Length (l_i)':<12}")
    print("-" * 70)

    entropy = 0.0
    avg_length = 0.0

    # Sort characters by frequency (descending)
    for char, freq in sorted(freq_map.items(), key=lambda x: x[1], reverse=True):
        p_i = freq / total_chars
        code = codes[char]
        l_i = len(code)

        entropy -= p_i * math.log2(p_i)
        avg_length += p_i * l_i
        
        char_display = repr(char)  # Shows ' ' for space cleanly
        print(f"{char_display:<10}{freq:<8}{p_i:<20.4f}{code:<16}{l_i:<12}")

    # STEP 2: Character-by-Character Conversion Trace
    print("\n--- STEP 2: CHARACTER-BY-CHARACTER ENCODING TRACE ---")
    char_trace = " ".join([f"{repr(c)}->{codes[c]}" for c in text[:15]])
    if len(text) > 15:
        char_trace += " ..."
    print(f"Substitutions (First 15 chars): {char_trace}")

    # STEP 3: Final Transmitted Bitstream
    print("\n--- STEP 3: FINAL TRANSMITTED BINARY CODE ---")
    print(f"Encoded Bitstream : {encoded_bitstream}")
    print(f"Total Bits Count  : {len(encoded_bitstream)} bits")

    # STEP 4: Performance & Text Compression Parameters
    uncompressed_bits = total_chars * 8
    compressed_bits = len(encoded_bitstream)
    efficiency = (entropy / avg_length) * 100 if avg_length > 0 else 0
    compression_ratio = uncompressed_bits / compressed_bits if compressed_bits > 0 else 0
    bandwidth_savings = ((uncompressed_bits - compressed_bits) / uncompressed_bits) * 100 if uncompressed_bits > 0 else 0

    print("\n--- STEP 4: TEXT COMPRESSION PARAMETERS ---")
    print(f"Original Input Text               : \"{text}\"")
    print(f"Original Size (8-bit ASCII)       : {uncompressed_bits} bits ({total_chars} bytes)")
    print(f"Compressed Size (Huffman Code)    : {compressed_bits} bits")
    print(f"Source Entropy H(X)               : {entropy:.4f} bits/symbol")
    print(f"Average Code Length (L)           : {avg_length:.4f} bits/symbol")
    print(f"Source Coding Efficiency (η)      : {efficiency:.2f}%")
    print(f"Compression Ratio (CR)            : {compression_ratio:.2f}:1")
    print(f"Bandwidth Savings                 : {bandwidth_savings:.2f}%")
    print("=" * 70 + "\n")

# =====================================================================
# 3. SOCKET NETWORKING UTILITIES
# =====================================================================

def send_packet(sock, data_dict):
    json_bytes = json.dumps(data_dict).encode('utf-8')
    header = struct.pack('>I', len(json_bytes))
    sock.sendall(header + json_bytes)

def receive_packet(sock):
    raw_header = recv_all(sock, 4)
    if not raw_header:
        return None
    length = struct.unpack('>I', raw_header)[0]
    raw_data = recv_all(sock, length)
    if not raw_data:
        return None
    return json.loads(raw_data.decode('utf-8'))

def recv_all(sock, n):
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return bytes(data)

# =====================================================================
# 4. TRANSMITTER & RECEIVER MODES
# =====================================================================

def run_receiver(port=5000):
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(('0.0.0.0', port))
    server_sock.listen(1)
    print(f"\n[RECEIVER NODE] Listening for incoming packet on port {port}...")

    conn, addr = server_sock.accept()
    print(f"[RECEIVER NODE] Connection established with Transmitter at {addr[0]}:{addr[1]}")

    packet = receive_packet(conn)
    conn.close()
    server_sock.close()

    if not packet:
        print("[RECEIVER NODE] Error: Failed to receive packet.")
        return

    freq_map = packet['freq_map']
    encoded_bitstream = packet['encoded_bitstream']

    # Source Decoding
    decoded_text = decompress(encoded_bitstream, freq_map)

    # Display full report on Receiver Node
    display_conversion_report("Receiver Device (Node B)", decoded_text, encoded_bitstream, freq_map)

def run_transmitter(receiver_ip, port=5000):
    text = input("\nEnter text to compress & transmit: ").strip()
    if not text:
        print("Error: Text cannot be empty.")
        return

    # Source Encoding
    root, freq_map = build_huffman_tree(text)
    codes = generate_codes(root)
    encoded_bitstream = compress(text, codes)

    # Display full report on Transmitter Node
    display_conversion_report("Transmitter Device (Node A)", text, encoded_bitstream, freq_map)

    # Prepare packet
    packet = {
        "freq_map": freq_map,
        "encoded_bitstream": encoded_bitstream
    }

    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"[TRANSMITTER NODE] Transmitting packet to {receiver_ip}:{port}...")
    try:
        client_sock.connect((receiver_ip, port))
        send_packet(client_sock, packet)
        print("[TRANSMITTER NODE] Transmission Successful!")
    except Exception as e:
        print(f"[TRANSMITTER NODE] Transmission Failed: {e}")
    finally:
        client_sock.close()

def run_loopback():
    text = input("\nEnter text for loopback test: ").strip()
    if not text:
        return
    root, freq_map = build_huffman_tree(text)
    codes = generate_codes(root)
    encoded_bitstream = compress(text, codes)
    
    display_conversion_report("Local Loopback Demonstration", text, encoded_bitstream, freq_map)

# =====================================================================
# MAIN ENTRY POINT
# =====================================================================

if __name__ == "__main__":
    print("=====================================================")
    print("  HUFFMAN SOURCE CODING DIGITAL COMMUNICATOR         ")
    print("=====================================================")
    print("1. Run as RECEIVER (Device B)")
    print("2. Run as TRANSMITTER (Device A)")
    print("3. Run LOCAL LOOPBACK TEST (Single Device Demo)")
    
    choice = input("\nSelect Mode (1/2/3): ").strip()

    if choice == '1':
        run_receiver()
    elif choice == '2':
        ip = input("Enter Receiver IP Address (e.g., 192.168.1.50 or 127.0.0.1): ").strip()
        run_transmitter(ip)
    elif choice == '3':
        run_loopback()
    else:
        print("Invalid selection.")