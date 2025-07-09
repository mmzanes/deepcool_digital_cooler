#!/usr/bin/env python3
"""
DeepCool Digital Cooler Controller - Universal Windows/Linux Support
Automatically detects and controls DeepCool digital display coolers
Supports: AG400, AG620, and other compatible models

Based on: https://github.com/Algorithm0/deepcool-digital-info
"""


from deepcool_util import DeepCoolController

def main():
    """Main function with interactive menu"""
    print("DeepCool Digital Cooler Controller")
    print("==================================")
    print("Universal Windows/Linux Support")
    print()

    controller = DeepCoolController()

    try:
        # Auto-detect and connect to device
        if not controller.find_and_connect_device():
            print("No compatible devices found. Exiting.")
            return

        # Initialize display
        if not controller.initialize_display():
            print("Failed to initialize display. Exiting.")
            return

        # Interactive menu
        while True:
            print("\nOptions:")
            print("1. Start temperature monitoring")
            print("2. Start CPU usage monitoring")
            print("3. Start both (alternating)")
            print("4. Test display")
            print("5. Quit")

            try:
                choice = input("Select option (1-5): ").strip()

                if choice == '1':
                    controller.run_monitoring_loop(show_temp=True, show_usage=False)
                elif choice == '2':
                    controller.run_monitoring_loop(show_temp=False, show_usage=True)
                elif choice == '3':
                    controller.run_monitoring_loop(show_temp=True, show_usage=True, alternating=True)
                elif choice == '4':
                    controller.test_display()
                elif choice == '5':
                    break
                else:
                    print("Invalid choice. Please select 1-5.")

            except (KeyboardInterrupt, EOFError):
                break

    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        controller.close()
        print("Goodbye!")

if __name__ == "__main__":
    main()
