import os
import subprocess

def analyze_code(directory):
    # List Python files in the directory
    python_files = [file for file in os.listdir(directory) if file.endswith('.py')]
    if not python_files:
        print("No Python files found in the specified directory.")
        return
    report_dir = os.path.join(directory, "reports")
    os.makedirs(report_dir, exist_ok=True)

    for file in python_files:
        print(f"Analyzing file: {file}")
        file_path = os.path.join(directory, file)
        
        # Run Black (code formatter)
        print("\nRunning Black...")
        black_command = f"black {file_path} --check"
        subprocess.run(black_command, shell=True)
        
        # Run Flake8 (linter)
        print("\nRunning Flake8...")
        flake8_output_file = os.path.join(report_dir, f"{file}_flake8_report.txt")
        with open(flake8_output_file, "w") as flake8_output:
            flake8_command = f"flake8 {file_path}"
            subprocess.run(flake8_command, shell=True, stdout=flake8_output, stderr=subprocess.STDOUT)
        print(f"Flake8 report saved to {flake8_output_file}")

        # Run Bandit (security analysis)
        print("\nRunning Bandit...")
        bandit_output_file = os.path.join(report_dir, f"{file}_bandit_report.txt")
        with open(bandit_output_file, "w") as bandit_output:
            bandit_command = f"bandit -r {file_path}"
            subprocess.run(bandit_command, shell=True, stdout=bandit_output, stderr=subprocess.STDOUT)
        print(f"Bandit report saved to {bandit_output_file}")
        print(f"Analyzing file: {file} Completed!!!!")
        print('================'*5)
        print('================'*5
if __name__ == "__main__":
    directory = r"C:\Users\abhay\OneDrive\Desktop\auto\Part7"
    analyze_code(directory)