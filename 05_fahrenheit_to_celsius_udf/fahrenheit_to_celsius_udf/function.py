import sys 

def fahrenheit_to_celsius(temp_f:float) -> float:
    """
    Convert temperature from Fahrenheit to Celsius.
    
    Args:
        temp_f (float): Temperature in Fahrenheit.
        
    Returns:
        float: Temperature in Celsius.
    """
    return (temp_f - 32) * 5.0/9.0


# Local debugging: allows you to run the script directly with a command line argument for testing
# Exécute le code suivant seulement si ce fichier est lancé directement.
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python function.py <temperature_in_fahrenheit>")
        sys.exit(1) # sert à arrêter immédiatement le programme Python.

    try:
        temp_f = float(sys.argv[1])
        temp_c = fahrenheit_to_celsius(temp_f)
        print(f"{temp_f}°F is equal to {temp_c:.2f}°C")
        #print("{}°F is equal to {:.2f}°C".format(temp_f, temp_c))

    except ValueError:
        print("Please provide a valid number for temperature in Fahrenheit.")
        sys.exit(1)
