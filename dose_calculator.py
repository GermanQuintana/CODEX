import json
import os

# --- Helper Functions ---
def get_positive_float_input(prompt_message):
    """
    Prompts the user for a positive float input until a valid value is entered.

    Args:
        prompt_message (str): The message to display to the user.

    Returns:
        float: The positive float value entered by the user.
    """
    while True:
        try:
            value = float(input(prompt_message))
            if value > 0:
                return value
            else:
                print("Value must be positive. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

# --- Calculation Helper Functions (Pure Logic) ---
def perform_dose_per_weight_calculation(weight_kg, dose_mg_per_kg, concentration_value, concentration_unit_str):
    """
    Performs the core dose-per-weight calculation.
    Returns: (total_mg_needed, quantity_to_administer, admin_unit_str)
    Raises: ValueError if concentration_value is zero.
    """
    if concentration_value == 0:
        raise ValueError("Concentration value cannot be zero.")
    
    total_mg_needed = weight_kg * dose_mg_per_kg
    admin_unit_str = "unrecognized_unit"
    quantity_to_administer = None

    unit_lower = concentration_unit_str.lower()
    if "/ml" in unit_lower: # Liquid
        quantity_to_administer = total_mg_needed / concentration_value
        admin_unit_str = "mL"
    elif "/tablet" in unit_lower or "mg/tab" in unit_lower: # Solid
        quantity_to_administer = total_mg_needed / concentration_value
        admin_unit_str = "tablets"
    
    return total_mg_needed, quantity_to_administer, admin_unit_str

def perform_infusion_preparation_calculation(total_dose_mg, drug_concentration_value_mg_ml, total_final_infusion_volume_ml):
    """
    Performs the core infusion preparation calculation.
    Returns: (drug_volume_ml, diluent_volume_ml, final_concentration_mg_ml)
    Raises: ValueError for zero drug_concentration or final_volume, or if drug_volume exceeds final_volume.
    """
    if drug_concentration_value_mg_ml == 0:
        raise ValueError("Drug concentration cannot be zero.")
    if total_final_infusion_volume_ml == 0:
        raise ValueError("Total final infusion volume cannot be zero.")

    volume_of_drug_to_draw_mL = total_dose_mg / drug_concentration_value_mg_ml

    if volume_of_drug_to_draw_mL > total_final_infusion_volume_ml:
        raise ValueError("Volume of drug to draw exceeds the total final infusion volume.")
    
    if volume_of_drug_to_draw_mL < 0: # Should not happen if inputs are positive, but defensive
        raise ValueError("Calculated volume of drug to draw is negative.")

    volume_of_diluent_mL = total_final_infusion_volume_ml - volume_of_drug_to_draw_mL
    
    # volume_of_diluent_mL < 0 check is implicitly covered by volume_of_drug_to_draw_mL > total_final_infusion_volume_ml

    final_infusion_concentration_mg_per_mL = total_dose_mg / total_final_infusion_volume_ml
    
    return volume_of_drug_to_draw_mL, volume_of_diluent_mL, final_infusion_concentration_mg_per_mL

def perform_rate_duration_calculation(total_volume_ml, total_drug_mg_in_infusion, value, mode):
    """
    Performs the core infusion rate/duration calculation.
    Returns: (calculated_rate_ml_hr, calculated_duration_hr, drug_delivery_rate_mg_hr)
    Raises: ValueError if rate, duration, or total_volume_ml (for concentration calc) is zero.
    """
    if mode == 'rate_from_duration':
        duration_hours = value
        if duration_hours == 0:
            raise ValueError("Duration cannot be zero.")
        infusion_rate_mL_per_hour = total_volume_ml / duration_hours
        drug_delivery_rate_mg_per_hour = total_drug_mg_in_infusion / duration_hours
        return infusion_rate_mL_per_hour, duration_hours, drug_delivery_rate_mg_per_hour
    elif mode == 'duration_from_rate':
        infusion_rate_mL_per_hour = value
        if infusion_rate_mL_per_hour == 0:
            raise ValueError("Infusion rate cannot be zero.")
        if total_volume_ml == 0: # Needed for drug_concentration calculation
             raise ValueError("Total volume cannot be zero for drug concentration calculation in this mode.")
        duration_hours = total_volume_ml / infusion_rate_mL_per_hour
        drug_concentration_mg_per_mL = total_drug_mg_in_infusion / total_volume_ml
        drug_delivery_rate_mg_per_hour = infusion_rate_mL_per_hour * drug_concentration_mg_per_mL
        return infusion_rate_mL_per_hour, duration_hours, drug_delivery_rate_mg_per_hour
    else:
        raise ValueError(f"Invalid mode: {mode}")

# --- UI and File I/O Functions ---
def load_medications(filepath="medications.json"):
    """
    Loads medication data from a JSON file.

    Args:
        filepath (str, optional): The path to the JSON file.
            Defaults to "medications.json".

    Returns:
        list: A list of medication objects (dictionaries), or an empty list
              if the file doesn't exist or an error occurs.
    """
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r') as f:
            medications = json.load(f)
        return medications
    except (IOError, json.JSONDecodeError):
        return []

def save_medications(medications, filepath="medications.json"):
    """
    Saves a list of medication objects to a JSON file.

    Args:
        medications (list): A list of medication objects (dictionaries).
        filepath (str, optional): The path to the JSON file.
            Defaults to "medications.json".

    Returns:
        bool: True if saving was successful, False otherwise.
    """
    try:
        with open(filepath, 'w') as f:
            json.dump(medications, f, indent=4)
        return True
    except IOError:
        return False

def add_medication():
    """
    Prompts the user for medication details, adds it to the list,
    and saves it.
    """
    medications = load_medications()
    print("\nAdding a new medication:")
    commercial_name = input("Enter Commercial Name: ").strip()
    presentation = input("Enter Presentation (e.g., '100 mg / 5 mL vial', '50 mg tablet'): ").strip()
    concentration_value = get_positive_float_input("Enter Concentration Value (e.g., 20.0, 50.0): ")
    concentration_unit = input("Enter Concentration Unit (e.g., 'mg/mL', 'mg/tablet'): ").strip()

    # Basic validation for key fields
    if not commercial_name:
        print("Error: Commercial Name cannot be empty.")
        input("\nPress Enter to return to the main menu...")
        return
    if not concentration_unit:
        print("Error: Concentration Unit cannot be empty.")
        input("\nPress Enter to return to the main menu...")
        return

    new_medication = {
        "commercial_name": commercial_name,
        "presentation": presentation,
        "concentration_value": concentration_value,
        "concentration_unit": concentration_unit,
    }
    medications.append(new_medication)
    if save_medications(medications):
        print(f"Medication '{commercial_name}' added successfully.")
    else:
        print(f"Error: Could not save medication '{commercial_name}'.")
    input("\nPress Enter to return to the main menu...")

def view_medications():
    """
    Loads and displays all medications.
    """
    medications = load_medications()
    if not medications:
        print("\nNo medications found in the system.")
        return

    print("\n--- List of Medications ---")
    for idx, med in enumerate(medications):
        print(f"{idx + 1}. Name: {med.get('commercial_name', 'N/A')}")
        print(f"   Presentation: {med.get('presentation', 'N/A')}")
        print(f"   Concentration: {med.get('concentration_value', 'N/A')} {med.get('concentration_unit', '')}")
        print("-------------------------")
    input("\nPress Enter to return to the main menu...")
    return medications # Return the list for selection purposes

def calculate_dose_per_weight():
    """
    Calculates the dose of a medication based on animal weight and desired dosage.
    """
    # view_medications() now includes "Press Enter..." so it's called for display,
    # then we load medications again silently for processing.
    view_medications() 
    medications_list = load_medications() # Load silently for processing

    if not medications_list:
        # view_medications would have already printed "No medications found..."
        # and handled the "Press Enter..."
        return

    while True:
        try:
            selection_str = input(f"Select a medication by number (1-{len(medications_list)}): ")
            if not selection_str.strip(): # Handle empty input
                print("Selection cannot be empty. Please enter a number.")
                continue
            selection = int(selection_str)
            if 1 <= selection <= len(medications_list):
                selected_med = medications_list[selection - 1]
                break
            else:
                print(f"Invalid selection. Please enter a number between 1 and {len(medications_list)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    print(f"\nCalculating dose for: {selected_med.get('commercial_name')}")
    concentration_value = selected_med.get('concentration_value')
    # The concentration_value from JSON should already be a number if saved correctly by add_medication.
    # The check for positivity is crucial before division.
    concentration_unit = selected_med.get('concentration_unit', '').lower()

    if not isinstance(concentration_value, (int, float)) or concentration_value <= 0:
        print(f"Error: Invalid or non-positive concentration value ({concentration_value}) for selected medication '{selected_med.get('commercial_name')}'. Cannot calculate dose.")
        input("\nPress Enter to return to the main menu...")
        return

    weight_kg = get_positive_float_input("Enter animal's weight in kg: ")
    dose_mg_per_kg = get_positive_float_input("Enter desired dose in mg/kg: ")

    try:
        total_mg_needed, quantity_to_administer, admin_unit_str = \
            perform_dose_per_weight_calculation(weight_kg, dose_mg_per_kg, concentration_value, concentration_unit)
        
        print(f"\nTotal medication needed: {total_mg_needed:.2f} mg")

        if admin_unit_str == "mL":
            print(f"Administer: {quantity_to_administer:.2f} mL")
        elif admin_unit_str == "tablets":
            print(f"Administer: {quantity_to_administer:.2f} tablets")
            if quantity_to_administer > 0: # Practical advice for tablets
                if quantity_to_administer < 0.25:
                    print("Consider if this dose is too small to accurately administer with available tablet sizes.")
                elif quantity_to_administer % 0.25 != 0 :
                    print("You may need to round to the nearest practical fraction (e.g., 1/4, 1/2, 3/4 tablet).")
        else: # unrecognized_unit
            print(f"Error: Concentration unit '{selected_med.get('concentration_unit')}' is not recognized for automatic dose calculation (e.g., '/mL' or '/tablet').")
            print("Please calculate manually based on the concentration.")
            
    except ValueError as e:
        print(f"Error during calculation: {e}")
        # This error (e.g. conc_value = 0) is already caught by the check before calling this UI function,
        # but good to have for robustness if perform_ was called directly with bad data from elsewhere.
    input("\nPress Enter to return to the main menu...")

def calculate_infusion_preparation():
    """
    Calculates the volumes needed to prepare an infusion.
    """
    # Similar to calculate_dose_per_weight, view first, then load silently.
    view_medications()
    medications_list = load_medications()

    if not medications_list:
        return

    while True:
        try:
            selection_str = input(f"Select a medication for infusion by number (1-{len(medications_list)}): ")
            if not selection_str.strip():
                print("Selection cannot be empty. Please enter a number.")
                continue
            selection = int(selection_str)
            if 1 <= selection <= len(medications_list):
                selected_med = medications_list[selection - 1]
                break
            else:
                print(f"Invalid selection. Please enter a number between 1 and {len(medications_list)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    med_name = selected_med.get('commercial_name', 'N/A')
    concentration_value = selected_med.get('concentration_value')
    # The concentration_value from JSON should already be a number.
    # Check for positivity before division.
    concentration_unit = selected_med.get('concentration_unit', '').lower()

    print(f"\nPreparing infusion with: {med_name} ({concentration_value} {selected_med.get('concentration_unit')})")

    if not ("/ml" in concentration_unit or "/ ml" in concentration_unit):
        print(f"Error: Selected medication '{med_name}' is not a liquid formulation suitable for infusion (e.g., does not have 'mg/mL' or similar units).")
        return

    if not isinstance(concentration_value, (int, float)) or concentration_value <= 0:
        print(f"Error: Invalid or non-positive concentration value ({concentration_value}) for selected medication '{med_name}'. Cannot calculate infusion.")
        input("\nPress Enter to return to the main menu...")
        return

    total_dose_mg = get_positive_float_input("Enter total dose of the drug to be added to infusion (mg): ")
    total_final_volume_mL = get_positive_float_input("Enter total final volume of the infusion (e.g., saline bag/syringe) in mL: ")

    try:
        volume_of_drug_to_draw_mL, volume_of_diluent_mL, final_infusion_concentration_mg_per_mL = \
            perform_infusion_preparation_calculation(total_dose_mg, concentration_value, total_final_volume_mL)

        print("\n--- Infusion Preparation Instructions ---")
        print(f"To prepare the infusion for {med_name}:")
        print(f"1. Draw {volume_of_drug_to_draw_mL:.2f} mL of {med_name} ({concentration_value} {selected_med.get('concentration_unit')}).")
        print(f"2. Add this to {volume_of_diluent_mL:.2f} mL of your chosen diluent (e.g., Saline).")
        print(f"This will result in a total volume of {total_final_volume_mL:.2f} mL.")
        print(f"The final concentration of the infusion will be {final_infusion_concentration_mg_per_mL:.2f} mg/mL.")
    except ValueError as e:
        print(f"Error during calculation: {e}")
        # This also handles cases like drug_volume > total_volume from the pure function
    input("\nPress Enter to return to the main menu...")

def calculate_infusion_rate_duration():
    """
    Calculates infusion rate given duration, or duration given rate,
    for a pre-made infusion.
    """
    print("\n--- Infusion Rate/Duration Calculator ---")
    print("This calculation is for a pre-made infusion (e.g., a bag with a known total volume and total drug amount).")

    total_volume_mL = get_positive_float_input("Enter the TOTAL volume of the infusion (mL): ")
    total_drug_mg_in_infusion = get_positive_float_input(f"Enter the TOTAL amount of active drug in the {total_volume_mL:.2f} mL infusion (mg): ")

    print("\nWhat do you want to calculate?")
    print("1. Infusion Rate (mL/hour) - given desired duration")
    print("2. Infusion Duration (hours) - given desired rate")

    while True:
        choice = input("Enter your choice (1 or 2): ")
        if choice in ['1', '2']:
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")

    try:
        if choice == '1': # Calculate Rate given Duration
            duration_input = get_positive_float_input("Enter desired duration of infusion (hours): ")
            calculated_rate, actual_duration, drug_delivery_rate = \
                perform_rate_duration_calculation(total_volume_mL, total_drug_mg_in_infusion, duration_input, 'rate_from_duration')
            
            print("\n--- Calculation Results ---")
            print(f"To infuse {total_volume_mL:.2f} mL containing {total_drug_mg_in_infusion:.2f} mg of drug over {actual_duration:.2f} hours:")
            print(f"Set infusion pump to: {calculated_rate:.2f} mL/hour.")
            print(f"This will deliver: {drug_delivery_rate:.2f} mg of drug per hour.")
            print(f"The infusion will complete in {actual_duration:.2f} hours.")

        elif choice == '2': # Calculate Duration given Rate
            rate_input = get_positive_float_input("Enter desired infusion rate (mL/hour): ")
            actual_rate, calculated_duration, drug_delivery_rate = \
                perform_rate_duration_calculation(total_volume_mL, total_drug_mg_in_infusion, rate_input, 'duration_from_rate')

            print("\n--- Calculation Results ---")
            print(f"To infuse {total_volume_mL:.2f} mL containing {total_drug_mg_in_infusion:.2f} mg of drug at a rate of {actual_rate:.2f} mL/hour:")
            print(f"The infusion will take {calculated_duration:.2f} hours to complete.")
            print(f"This will deliver: {drug_delivery_rate:.2f} mg of drug per hour.")
    except ValueError as e:
        print(f"Error during calculation: {e}")
    input("\nPress Enter to return to the main menu...")

def main_menu():
    """
    Displays the main menu and handles user interaction.
    """
    while True:
        print("\nVeterinary Dose Calculator")
        print("---------------------------")
        print("1. Add New Medication")
        print("2. View All Medications")
        print("3. Calculate Dose (Per Weight)")
        print("4. Calculate Infusion Preparation")
        print("5. Calculate Infusion Rate/Duration")
        print("0. Exit")
        print("---------------------------")

        choice = input("Enter your choice: ")

        if choice == '1':
            add_medication()
        elif choice == '2':
            view_medications()
        elif choice == '3':
            calculate_dose_per_weight()
        elif choice == '4':
            calculate_infusion_preparation()
        elif choice == '5':
            calculate_infusion_rate_duration()
        elif choice == '0':
            print("\nExiting Dose Calculator. Goodbye!")
            break
        else:
            print("\nInvalid choice. Please try again.")
            input("Press Enter to continue...") # Keep this for invalid menu choices

if __name__ == "__main__":
    # os.remove("medications.json") # Optional: uncomment to clear data on each run for testing
    # print("Previous medications.json removed for a clean test run.") # Optional
    main_menu()
