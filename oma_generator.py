#!/usr/bin/env python3
"""
OMa File Generator for Huvitz Excelon Frame Scan Data
Generates OMa files from captured frame scan data
"""

import struct
import json
import numpy as np
from datetime import datetime
import os

class OMAGenerator:
    def __init__(self):
        self.oma_header = {
            'version': '1.0',
            'device': 'Huvitz Excelon',
            'format': 'OMA'
        }
    
    def create_oma_file(self, scan_data, filename):
        """Create an OMa file from scan data"""
        try:
            # Create the OMa file structure
            oma_content = self._build_oma_content(scan_data)
            
            # Write to file
            with open(filename, 'wb') as f:
                f.write(oma_content)
            
            print(f"OMa file created successfully: {filename}")
            return filename
            
        except Exception as e:
            print(f"Error creating OMa file: {e}")
            return None
    
    def _build_oma_content(self, scan_data):
        """Build the binary content for the OMa file"""
        # Header information
        header = self._create_header(scan_data)
        
        # Frame data
        frame_data = self._create_frame_data(scan_data)
        
        # Radius data
        radius_data = self._create_radius_data(scan_data)
        
        # Combine all data
        content = header + frame_data + radius_data
        
        return content
    
    def _create_header(self, scan_data):
        """Create the OMa file header"""
        # OMa file header structure
        header = struct.pack('<4s', b'OMAF')  # Magic number
        header += struct.pack('<I', 1)  # Version
        header += struct.pack('<I', len(scan_data.get('radii', [])))  # Number of radius points
        
        # Timestamp
        timestamp = scan_data.get('timestamp', datetime.now().isoformat())
        timestamp_bytes = timestamp.encode('utf-8')
        header += struct.pack('<I', len(timestamp_bytes))
        header += timestamp_bytes
        
        # Device information
        device_info = "Huvitz Excelon Frame Scanner"
        device_bytes = device_info.encode('utf-8')
        header += struct.pack('<I', len(device_bytes))
        header += device_bytes
        
        return header
    
    def _create_frame_data(self, scan_data):
        """Create frame measurement data"""
        measurements = scan_data.get('measurements', {})
        
        # Frame measurements
        width = measurements.get('width', 0)
        height = measurements.get('height', 0)
        area = measurements.get('area', 0)
        perimeter = measurements.get('perimeter', 0)
        
        center = measurements.get('center', (0, 0))
        center_x, center_y = center
        
        # Pack frame data
        frame_data = struct.pack('<4I', width, height, center_x, center_y)
        frame_data += struct.pack('<2d', area, perimeter)
        
        return frame_data
    
    def _create_radius_data(self, scan_data):
        """Create radius data section"""
        radii = scan_data.get('radii', [])
        
        if not radii:
            return b''
        
        # Pack radius data as 16-bit integers
        radius_data = struct.pack(f'<{len(radii)}H', *radii)
        
        return radius_data
    
    def read_oma_file(self, filename):
        """Read and parse an OMa file"""
        try:
            with open(filename, 'rb') as f:
                content = f.read()
            
            return self._parse_oma_content(content)
            
        except Exception as e:
            print(f"Error reading OMa file: {e}")
            return None
    
    def _parse_oma_content(self, content):
        """Parse the binary OMa file content"""
        offset = 0
        
        # Read header
        magic = struct.unpack('<4s', content[offset:offset+4])[0]
        offset += 4
        
        if magic != b'OMAF':
            raise ValueError("Invalid OMa file format")
        
        version = struct.unpack('<I', content[offset:offset+4])[0]
        offset += 4
        
        num_radii = struct.unpack('<I', content[offset:offset+4])[0]
        offset += 4
        
        # Read timestamp
        timestamp_len = struct.unpack('<I', content[offset:offset+4])[0]
        offset += 4
        timestamp = content[offset:offset+timestamp_len].decode('utf-8')
        offset += timestamp_len
        
        # Read device info
        device_len = struct.unpack('<I', content[offset:offset+4])[0]
        offset += 4
        device_info = content[offset:offset+device_len].decode('utf-8')
        offset += device_len
        
        # Read frame data
        width, height, center_x, center_y = struct.unpack('<4I', content[offset:offset+16])
        offset += 16
        area, perimeter = struct.unpack('<2d', content[offset:offset+16])
        offset += 16
        
        # Read radius data
        radii = list(struct.unpack(f'<{num_radii}H', content[offset:offset+num_radii*2]))
        
        return {
            'version': version,
            'timestamp': timestamp,
            'device_info': device_info,
            'measurements': {
                'width': width,
                'height': height,
                'center': (center_x, center_y),
                'area': area,
                'perimeter': perimeter
            },
            'radii': radii
        }
    
    def export_to_json(self, scan_data, filename):
        """Export scan data to JSON format for debugging"""
        try:
            # Convert numpy arrays to lists for JSON serialization
            json_data = {
                'timestamp': scan_data.get('timestamp'),
                'measurements': scan_data.get('measurements', {}),
                'radii': scan_data.get('radii', []),
                'frame_shape': scan_data.get('frame_shape')
            }
            
            with open(filename, 'w') as f:
                json.dump(json_data, f, indent=2)
            
            print(f"JSON export created: {filename}")
            return filename
            
        except Exception as e:
            print(f"Error creating JSON export: {e}")
            return None
    
    def create_sample_oma(self, filename="sample_1552_51_13.oma"):
        """Create a sample OMa file based on the provided data"""
        # Sample radius data from your example
        sample_radii = [
            2354,2359,2365,2370,2376,2381,2387,2393,2398,2404,2410,2416,2423,2429,2435,2442,2448,2455,2461,2468,
            2475,2482,2489,2496,2503,2510,2518,2525,2532,2540,2547,2555,2563,2570,2578,2586,2594,2602,2609,2617,
            2625,2633,2640,2645,2651,2655,2659,2662,2664,2666,2667,2668,2667,2666,2665,2663,2660,2656,2652,2647,
            2641,2635,2628,2620,2611,2601,2592,2582,2572,2561,2550,2540,2529,2518,2507,2496,2484,2473,2462,2450,
            2439,2427,2415,2403,2392,2380,2368,2356,2344,2332,2320,2308,2297,2285,2274,2263,2252,2241,2230,2219,
            2208,2198,2187,2177,2166,2156,2146,2136,2126,2116,2107,2097,2088,2078,2069,2060,2051,2042,2033,2025,
            2016,2008,1999,1991,1983,1975,1967,1959,1951,1943,1936,1928,1921,1914,1906,1899,1892,1885,1878,1872,
            1865,1858,1852,1845,1839,1833,1826,1820,1814,1808,1802,1797,1791,1785,1780,1774,1769,1763,1758,1753,
            1748,1742,1737,1732,1728,1723,1718,1713,1709,1704,1700,1695,1691,1687,1682,1678,1674,1670,1666,1662,
            1659,1655,1651,1648,1644,1641,1637,1634,1631,1628,1624,1621,1618,1615,1612,1610,1607,1604,1601,1599,
            1596,1594,1591,1589,1587,1585,1582,1580,1578,1576,1574,1572,1570,1569,1567,1565,1563,1562,1560,1559,
            1557,1556,1555,1553,1552,1551,1550,1549,1548,1547,1546,1545,1544,1544,1543,1542,1542,1541,1541,1540,
            1540,1539,1539,1539,1539,1538,1538,1538,1538,1538,1538,1539,1539,1539,1539,1540,1540,1541,1541,1542,
            1542,1543,1544,1544,1545,1546,1547,1548,1549,1550,1551,1552,1553,1555,1556,1557,1559,1560,1562,1563,
            1565,1567,1568,1570,1572,1574,1576,1578,1580,1582,1584,1586,1589,1591,1594,1596,1599,1601,1604,1606,
            1609,1612,1615,1618,1621,1624,1627,1630,1634,1637,1640,1644,1647,1651,1654,1658,1662,1666,1670,1674,
            1678,1682,1686,1690,1695,1699,1704,1708,1713,1718,1722,1727,1732,1737,1742,1748,1753,1758,1764,1769,
            1775,1780,1786,1792,1798,1804,1810,1816,1822,1829,1835,1842,1848,1855,1862,1868,1875,1882,1889,1896,
            1904,1911,1919,1926,1934,1941,1949,1957,1965,1973,1981,1990,1998,2007,2015,2024,2033,2042,2051,2060,
            2069,2078,2088,2097,2107,2116,2126,2136,2146,2156,2166,2176,2187,2197,2207,2218,2229,2239,2250,2261,
            2271,2282,2292,2303,2313,2324,2334,2345,2355,2365,2376,2386,2396,2406,2416,2426,2436,2445,2454,2462,
            2471,2479,2487,2494,2502,2509,2515,2522,2528,2534,2540,2545,2550,2554,2559,2563,2567,2570,2573,2576,
            2579,2581,2583,2585,2587,2589,2590,2592,2593,2594,2595,2596,2597,2598,2598,2598,2599,2599,2599,2599,
            2598,2598,2597,2597,2596,2595,2594,2593,2591,2590,2589,2587,2586,2584,2582,2580,2579,2577,2574,2572,
            2570,2568,2565,2563,2560,2558,2555,2552,2549,2546,2543,2540,2537,2534,2531,2527,2524,2521,2517,2514,
            2511,2508,2504,2501,2498,2495,2492,2489,2486,2483,2480,2477,2474,2472,2469,2466,2464,2461,2459,2457,
            2454,2452,2450,2448,2445,2443,2441,2439,2437,2436,2434,2432,2430,2429,2427,2426,2424,2423,2422,2420,
            2419,2418,2417,2416,2415,2414,2413,2412,2411,2410,2410,2409,2408,2408,2407,2407,2407,2406,2406,2406,
            2406,2406,2406,2406,2406,2406,2406,2406,2406,2406,2405,2405,2404,2404,2403,2402,2401,2401,2400,2398,
            2396,2394,2391,2388,2384,2380,2375,2370,2364,2358,2352,2345,2337,2329,2320,2311,2301,2291,2281,2271,
            2261,2251,2241,2231,2221,2211,2201,2191,2180,2170,2160,2149,2139,2129,2119,2109,2100,2090,2081,2071,
            2062,2053,2044,2035,2026,2018,2009,2001,1992,1984,1976,1968,1960,1952,1945,1937,1929,1922,1915,1907,
            1900,1893,1886,1879,1872,1866,1859,1852,1846,1840,1833,1827,1821,1815,1809,1803,1797,1792,1786,1780,
            1775,1770,1764,1759,1754,1749,1744,1739,1734,1729,1724,1719,1715,1710,1706,1701,1697,1693,1688,1684,
            1680,1676,1672,1668,1664,1661,1657,1653,1650,1646,1643,1639,1636,1633,1629,1626,1623,1620,1617,1614,
            1611,1609,1606,1603,1601,1598,1595,1593,1591,1588,1586,1584,1582,1579,1577,1575,1573,1571,1570,1568,
            1566,1564,1563,1561,1560,1558,1557,1555,1554,1553,1551,1550,1549,1548,1547,1546,1545,1544,1543,1542,
            1542,1541,1540,1540,1539,1539,1538,1538,1537,1537,1537,1537,1537,1536,1536,1536,1536,1536,1537,1537,
            1537,1537,1538,1538,1538,1539,1539,1540,1541,1541,1542,1543,1544,1545,1545,1546,1547,1549,1550,1551,
            1552,1553,1555,1556,1558,1559,1561,1562,1564,1566,1568,1569,1571,1573,1575,1577,1579,1582,1584,1586,
            1588,1591,1593,1596,1598,1601,1604,1606,1609,1612,1615,1618,1621,1624,1627,1631,1634,1637,1641,1644,
            1648,1652,1655,1659,1663,1667,1671,1675,1679,1683,1687,1691,1695,1700,1704,1709,1713,1718,1723,1727,
            1732,1737,1742,1747,1752,1758,1763,1768,1774,1779,1785,1790,1796,1802,1808,1814,1820,1826,1832,1838,
            1845,1851,1858,1864,1871,1878,1885,1892,1899,1906,1913,1920,1927,1935,1942,1949,1957,1964,1972,1979,
            1987,1995,2002,2010,2017,2024,2031,2038,2045,2052,2059,2065,2071,2078,2083,2089,2094,2099,2104,2108,
            2112,2116,2119,2122,2125,2127,2129,2131,2133,2134,2136,2137,2138,2139,2141,2142,2143,2144,2145,2146,
            2147,2148,2148,2149,2150,2151,2152,2153,2154,2155,2156,2157,2158,2159,2160,2161,2162,2164,2165,2166,
            2168,2169,2170,2172,2173,2175,2176,2178,2180,2181,2183,2185,2187,2189,2191,2193,2195,2197,2199,2201,
            2204,2206,2209,2211,2214,2217,2219,2222,2225,2228,2231,2234,2237,2241,2244,2247,2251,2254,2258,2261,
            2265,2269,2273,2276,2280,2284,2289,2293,2297,2301,2306,2310,2315,2320,2324,2329,2334,2339,2344,2349
        ]
        
        # Create sample scan data
        sample_data = {
            'timestamp': datetime.now().isoformat(),
            'measurements': {
                'width': 1552,
                'height': 51,
                'center': (776, 25),
                'area': 79152,
                'perimeter': 3206
            },
            'radii': sample_radii,
            'frame_shape': (1080, 1920, 3)
        }
        
        return self.create_oma_file(sample_data, filename) 