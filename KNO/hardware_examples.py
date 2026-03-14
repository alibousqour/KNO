# =========================================================================
# Hardware Abstraction Layer - Usage Examples
# =========================================================================
"""
Comprehensive examples for using the KNO Hardware Abstraction Layer (HAL)

This file demonstrates:
1. Basic initialization and resource queries
2. CPU management and monitoring
3. Memory management
4. Storage and disk monitoring
5. Network interface management
6. Audio device management
7. Power and battery management
8. Temperature monitoring
9. System health checks
10. Continuous monitoring
"""

from hardware import HardwareManager
import json


def example_1_basic_initialization():
    """Example 1: Basic initialization and system info"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Initialization")
    print("="*70)
    
    # Initialize HardwareManager
    hw = HardwareManager()
    
    print(f"Hardware Manager: {hw}")
    print(f"Platform: {hw.platform_name}")
    print(f"Version: {hw.VERSION}")
    
    # Get system information
    sys_info = hw.get_system_info()
    print(f"\nSystem Information:")
    print(json.dumps({k: str(v) for k, v in sys_info.items()}, indent=2))


def example_2_cpu_management():
    """Example 2: CPU management and monitoring"""
    print("\n" + "="*70)
    print("EXAMPLE 2: CPU Management")
    print("="*70)
    
    hw = HardwareManager()
    
    # Get CPU information
    print(f"CPU Cores: {hw.cpu.get_count()}")
    print(f"CPU Usage: {hw.cpu.get_usage():.1f}%")
    
    # Per-core usage
    per_core = hw.cpu.get_usage(per_core=True)
    print(f"Per-core usage: {[f'{u:.1f}%' for u in per_core]}")
    
    # CPU frequency
    freq = hw.cpu.get_frequency()
    print(f"CPU Frequency: {freq['current']:.0f} MHz (min: {freq['min']:.0f}, max: {freq['max']:.0f})")
    
    # CPU temperature
    temp = hw.cpu.get_temperature()
    if temp:
        print(f"CPU Temperature: {temp:.1f}°C")
    
    # Top processes
    print("\nTop CPU-consuming processes:")
    for proc in hw.cpu.get_top_processes(limit=5):
        print(f"  {proc['name']:20s} PID: {proc['pid']:6d} CPU: {proc['cpu_percent']:5.1f}%")


def example_3_memory_management():
    """Example 3: Memory management"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Memory Management")
    print("="*70)
    
    hw = HardwareManager()
    
    # Memory information
    mem_info = hw.memory.get_info()
    print(f"Total Memory: {mem_info['total'] / (1024**3):.2f} GB")
    print(f"Available: {mem_info['available'] / (1024**3):.2f} GB")
    print(f"Used: {mem_info['used'] / (1024**3):.2f} GB")
    print(f"Memory Usage: {mem_info['percent']:.1f}%")
    
    # Swap information
    swap_info = hw.memory.get_swap_info()
    print(f"\nSwap Total: {swap_info['total'] / (1024**3):.2f} GB")
    print(f"Swap Used: {swap_info['used'] / (1024**3):.2f} GB")
    print(f"Swap Usage: {swap_info['percent']:.1f}%")


def example_4_storage_management():
    """Example 4: Storage and disk management"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Storage Management")
    print("="*70)
    
    hw = HardwareManager()
    
    # List all disks
    print("Mounted filesystems:")
    disks = hw.storage.get_disk_info()
    for disk in disks:
        usage = hw.storage.get_disk_usage(disk['mountpoint'])
        total_gb = usage['total'] / (1024**3)
        used_gb = usage['used'] / (1024**3)
        percent = usage['percent']
        print(f"  {disk['device']:15s} → {disk['mountpoint']:20s} {percent:5.1f}% ({used_gb:.1f}/{total_gb:.1f}GB)")
    
    # Root filesystem
    print("\nRoot filesystem usage:")
    root_usage = hw.storage.get_root_usage()
    print(f"  Total: {root_usage['total'] / (1024**3):.2f} GB")
    print(f"  Used: {root_usage['used'] / (1024**3):.2f} GB")
    print(f"  Free: {root_usage['free'] / (1024**3):.2f} GB")
    print(f"  Usage: {root_usage['percent']:.1f}%")


def example_5_network_management():
    """Example 5: Network interface management"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Network Management")
    print("="*70)
    
    hw = HardwareManager()
    
    # Get network interfaces
    interfaces = hw.network.get_interfaces()
    print(f"Total interfaces: {len(interfaces)}\n")
    
    for iface_name, iface_info in interfaces.items():
        print(f"Interface: {iface_name}")
        print(f"  IP Address: {iface_info.get('ip', 'N/A')}")
        print(f"  MAC Address: {iface_info.get('mac', 'N/A')}")
        
        # Get interface stats
        stats = hw.network.get_interface_stats(iface_name)
        if stats:
            print(f"  Status: {'UP' if stats.get('is_up') else 'DOWN'}")
            print(f"  MTU: {stats.get('mtu', 'N/A')}")
        print()


def example_6_audio_management():
    """Example 6: Audio device management"""
    print("\n" + "="*70)
    print("EXAMPLE 6: Audio Device Management")
    print("="*70)
    
    hw = HardwareManager()
    
    # List input devices
    print("Audio Input Devices (Microphones):")
    input_devices = hw.audio.list_input_devices()
    for dev in input_devices:
        print(f"  [{dev['id']}] {dev['name']}")
        print(f"      Channels: {dev['channels']}, Sample Rate: {dev['sample_rate']} Hz")
    
    # List output devices
    print("\nAudio Output Devices (Speakers):")
    output_devices = hw.audio.list_output_devices()
    for dev in output_devices:
        print(f"  [{dev['id']}] {dev['name']}")
        print(f"      Channels: {dev['channels']}, Sample Rate: {dev['sample_rate']} Hz")
    
    # Volume
    volume = hw.audio.get_volume()
    print(f"\nCurrent Volume: {volume*100:.0f}%")


def example_7_power_management():
    """Example 7: Power and battery management"""
    print("\n" + "="*70)
    print("EXAMPLE 7: Power & Battery Management")
    print("="*70)
    
    hw = HardwareManager()
    
    # Battery information
    battery = hw.power.get_battery_info()
    if battery:
        print(f"Battery Percentage: {battery['percent']:.1f}%")
        print(f"Power Plugged In: {battery['power_plugged']}")
        if battery['secsleft'] > 0:
            hours = battery['secsleft'] // 3600
            minutes = (battery['secsleft'] % 3600) // 60
            print(f"Time Left: {hours}h {minutes}m")
    else:
        print("No battery information available (desktop system?)")


def example_8_temperature_monitoring():
    """Example 8: Temperature monitoring"""
    print("\n" + "="*70)
    print("EXAMPLE 8: Temperature Monitoring")
    print("="*70)
    
    hw = HardwareManager()
    
    # Get all temperatures
    temps = hw.temperature.get_all_temperatures()
    print("System Temperatures:")
    for sensor_name, temp_c in temps.items():
        print(f"  {sensor_name:15s} {temp_c:6.1f}°C")
    
    # Thermal health
    thermal_health = hw.temperature.check_thermal_health()
    print(f"\nThermal Health: {thermal_health.upper()}")
    
    max_temp = hw.temperature.get_max_temperature()
    print(f"Maximum Temperature: {max_temp:.1f}°C")


def example_9_system_health_check():
    """Example 9: Comprehensive system health check"""
    print("\n" + "="*70)
    print("EXAMPLE 9: System Health Check")
    print("="*70)
    
    hw = HardwareManager()
    
    # Run health check
    health = hw.run_health_check()
    
    print(f"\nOverall Health: {health['overall'].upper()}\n")
    print(f"CPU Health: {health['cpu']['status'].upper()}")
    print(f"  Usage: {health['cpu']['usage_percent']:.1f}%")
    print(f"  Temperature: {health['cpu']['temperature_c']:.1f}°C")
    
    print(f"\nMemory Health: {health['memory']['status'].upper()}")
    print(f"  Usage: {health['memory']['usage_percent']:.1f}%")
    
    print(f"\nStorage Health: {health['storage']['status'].upper()}")
    print(f"  Root Usage: {health['storage']['root_usage_percent']:.1f}%")
    
    print(f"\nNetwork Health: {health['network']['status'].upper()}")
    print(f"  Active Interfaces: {health['network']['active_interfaces']}")
    
    print(f"\nThermal Health: {health['thermal']['status'].upper()}")
    print(f"  Max Temperature: {health['thermal']['max_temp_c']:.1f}°C")


def example_10_continuous_monitoring():
    """Example 10: Continuous system monitoring"""
    print("\n" + "="*70)
    print("EXAMPLE 10: Continuous Monitoring")
    print("="*70)
    
    import time
    
    hw = HardwareManager()
    
    # Start monitoring
    print("Starting system monitoring (10 seconds)...")
    hw.start_monitoring(interval_seconds=2)
    
    # Monitor for 10 seconds
    for i in range(5):
        time.sleep(2)
        resource_usage = hw.get_resource_usage()
        
        print(f"\n[{i+1}] CPU: {resource_usage['cpu']['usage']:.1f}%, "
              f"Memory: {resource_usage['memory']:.1f}%, "
              f"Disk: {resource_usage['disk']['percent']:.1f}%")
    
    # Stop monitoring
    hw.stop_monitoring()
    
    # Get health history
    history = hw.get_health_history()
    print(f"\nCollected {len(history)} health snapshots")


def example_11_export_to_json():
    """Example 11: Export hardware information to JSON"""
    print("\n" + "="*70)
    print("EXAMPLE 11: Export to JSON")
    print("="*70)
    
    hw = HardwareManager()
    
    # Export to JSON
    json_str = hw.export_to_json(include_history=False)
    
    print("Export sample (first 500 chars):")
    print(json_str[:500] + "\n...")


# =========================================================================
# MAIN ENTRY POINT
# =========================================================================

if __name__ == "__main__":
    """Run all examples"""
    
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "KNO v6.0 Hardware Abstraction Layer (HAL)" + " "*12 + "║")
    print("║" + " "*20 + "Comprehensive Usage Examples" + " "*22 + "║")
    print("╚" + "="*68 + "╝")
    
    try:
        example_1_basic_initialization()
        example_2_cpu_management()
        example_3_memory_management()
        example_4_storage_management()
        example_5_network_management()
        example_6_audio_management()
        example_7_power_management()
        example_8_temperature_monitoring()
        example_9_system_health_check()
        # example_10_continuous_monitoring()  # Uncomment to test monitoring
        example_11_export_to_json()
        
        print("\n" + "="*70)
        print("✓ All examples completed successfully!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()
