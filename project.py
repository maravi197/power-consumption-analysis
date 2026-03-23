import re
from datetime import datetime
import matplotlib.pyplot as plt

input_file = 'household_power_consumption.txt'
power_spike_threshold = 5.0
peak_hour_starts = 17

valid = []
problem_lines = []

print(f"Starting analysis of '{input_file}'...")

try:
    with open(input_file, 'r') as f:
        header = f.readline()
        temp = 1

        for line in f:
            temp += 1
            try:
                values = line.strip().split(';')
                date_str = values[0]
                time_str = values[1]
                power = float(values[2])
                dt_obj = datetime.strptime(f"{date_str} {time_str}", '%d/%m/%Y %H:%M:%S')
                sub_1 = float(values[6])
                sub_2 = float(values[7])
                sub_3 = float(values[8])
                hour = dt_obj.hour
                weekday = dt_obj.weekday()


                valid.append({
                    'datetime': dt_obj,
                    'date': date_str,
                    'time': time_str,
                    'hour': hour,
                    'power': power,
                    'weekday': weekday,
                    'sub1' : sub_1,
                    'sub2' : sub_2,
                    'sub3' : sub_3,
                })
            except (ValueError, IndexError, TypeError) as e:
                problem_lines.append({
                    'line_number': temp,
                    'content': line.strip(),
                    'error': str(e)
                })

except FileNotFoundError:
    print(f"ERROR: Could not find file '{input_file}'")
    exit()

print(f"File processing complete. Found {len(valid)} valid readings and {len(problem_lines)} problem lines")

if problem_lines:
    print("\n--- Power Lines Skipped ---")
    print(f"Found total of {len(problem_lines)} in the datase")

if valid:
    print("\n--- Power Consumption Analysis ---")

    def analyze_overall_stats(readings):
        max_reading = max(readings, key=lambda r: r['power'])
        min_reading = min(readings, key=lambda r: r['power'])
        total_power = sum(r['power'] for r in readings)
        avg_power = total_power / len(readings)
        
        print("\n--- Overall Statistics ---")
        print(f" - Overall Average Power: {avg_power:.3f} kW")
        print(f" - Absolute Highest Peak: {max_reading['power']:.3f} kW (on {max_reading['date']} @ {max_reading['time']})")
        print(f" - Minimum Base Load:   {min_reading['power']:.3f} kW (on {min_reading['date']} @ {min_reading['time']})")
    
    def sub_metering_analysis(readings):
        total_power = sum(r['power'] for r in readings)
        total_power_in_wH = ((total_power)*(1000))/60
        total_sub_1 = int(sum(r['sub1'] for r in readings))
        total_sub_2 = int(sum(r['sub2'] for r in readings))
        total_sub_3 = int(sum(r['sub3'] for r in readings))
        others = int(total_power_in_wH - (total_sub_1+total_sub_2+total_sub_3))
        percentages = { 'Sub Metering 1' : total_sub_1, 'Sub Mertering 2' : total_sub_2, 'Sub Metering 3' : total_sub_3, 'Others' : others }
        return percentages

    def get_time_block(hour):
        if 0 <= hour <= 5: return 'Night'
        elif 6 <= hour <= 11: return 'Morning'
        elif 12 <= hour <= 16: return 'Afternoon'
        elif 17 <= hour <= 23: return 'Evening'
        return 'Unknown'

    def analyze_by_time_blocks(readings):
        blocks = {'Night': [], 'Morning': [], 'Afternoon': [], 'Evening': []}
        for r in readings:
            block_name = get_time_block(r['hour'])
            if block_name != 'Unknown':
                blocks[block_name].append(r['power'])
        
        print("\n--- Average Power by Time of Day ---")
        averages = {}
        for block_name, power_list in blocks.items():
            if power_list:
                avg_power = sum(power_list) / len(power_list)
                averages[block_name] = avg_power
                print(f" - {block_name} (avg): {avg_power:.3f} kW")
            else:
                averages[block_name] = 0
                print(f" - {block_name} (avg): No data")
        return averages

    def analyze_by_day_type(readings):
        weekday_readings = [r['power'] for r in readings if r['weekday'] <= 4]
        weekend_readings = [r['power'] for r in readings if r['weekday'] >= 5]
        
        print("\n--- Average Power by Day Type ---")
        averages = {}
        if weekday_readings:
            avg_weekday = sum(weekday_readings) / len(weekday_readings)
            averages['Weekday'] = avg_weekday
            print(f" - Weekday (Mon-Fri) Avg: {avg_weekday:.3f} kW")
        else:
            averages['Weekday'] = 0
            print(" - Weekday (Mon-Fri) Avg: No data")
            
        if weekend_readings:
            avg_weekend = sum(weekend_readings) / len(weekend_readings)
            averages['Weekend'] = avg_weekend
            print(f" - Weekend (Sat-Sun) Avg: {avg_weekend:.3f} kW")
        else:
            averages['Weekend'] = 0
            print(" - Weekend (Sat-Sun) Avg: No data")
        return averages

    def plot_power_over_time(readings, spike_threshold):
        print("\nPlotting Power Consumption vs. Time...")
        
        x_times = [r['datetime'] for r in readings]
        y_power = [r['power'] for r in readings]
        
        plt.figure(figsize=(15, 6))
        plt.plot(x_times, y_power, label='Power Usage (kW)', linewidth=1)
        
        plt.axhline(y=spike_threshold, color='r', linestyle='--', label=f'Spike Threshold ({spike_threshold} kW)')
        
        plt.xlabel('Date / Time')
        plt.ylabel('Power (kW)')
        plt.title('Power Consumption Over Time')
        plt.legend()
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)
        plt.gcf().autofmt_xdate()
        plt.show()

    def plot_time_block_averages(block_data):
        print("Plotting Average Power by Time Block...")
        
        labels = ['Night', 'Morning', 'Afternoon', 'Evening']
        values = [block_data.get(label, 0) for label in labels]
        
        plt.figure(figsize=(8, 5))
        plt.bar(labels, values, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
        
        plt.xlabel('Time of Day')
        plt.ylabel('Average Power (kW)')
        plt.title('Average Power by Time of Day')
        plt.show()

    def plot_day_type_averages(day_data):
        print("Plotting Weekday vs. Weekend Average Power...")
        
        labels = list(day_data.keys())
        values = list(day_data.values())
        
        plt.figure(figsize=(6, 5))
        plt.bar(labels, values, color=['gray', 'orange'])
        
        plt.ylabel('Average Power (kW)')
        plt.title('Weekday vs. Weekend Average Power')
        plt.show()
    
    def plot_sub_meterings(readings):
        print("Plotting Pie chart of Sub Meterings...")
        colors = ['skyblue', 'lightcoral', 'gold', 'lightgreen']
        plt.pie(readings.values(),labels=readings.keys(),colors=colors,autopct='%1.1f%%')
        plt.title("Percentage Breakdown of Total Energy Consumed")
        plt.show()

    analyze_overall_stats(valid)
    time_block_avg_data = analyze_by_time_blocks(valid)
    day_type_avg_data = analyze_by_day_type(valid)

    print("\n--- Spike Analysis ---")
    spikes = list(filter(lambda r: r['power'] >= power_spike_threshold, valid))
    print(f"Found {len(spikes)} power spike(s) (>= {power_spike_threshold} kW):")

    print("\n--- Peak Hour Analysis ---")
    peak_hour_readings = list(filter(lambda r: r['hour'] >= peak_hour_starts, valid))
    if peak_hour_readings:
        total_power = sum(r['power'] for r in peak_hour_readings)
        avg_power = total_power / len(peak_hour_readings)
        print(f"Analysis for 'Peak Hours' (on or after {peak_hour_starts}:00)")
        print(f" - Average power during peak hours: {avg_power:.3f} kW")
    else:
        print(f"No valid reading found during peak hours (after {peak_hour_starts}:00).")
    
    sub_percentages = sub_metering_analysis(valid)
    print("\n--- Sub Metering Analysis ---")
    print("Percentage breakdown of total energy consumed:")
    total=sum(r for k,r in sub_percentages.items())
    for category,x in sub_percentages.items():
        percent=(x/total)*100
        print(f"  -{category + ':':} {percent:.2f}%")

    print("\n--- Visualizations ---")  
    plot_power_over_time(valid, power_spike_threshold)
    plot_time_block_averages(time_block_avg_data)
    plot_day_type_averages(day_type_avg_data)
    plot_sub_meterings(sub_percentages)
    

else:
    print("\nNo valid data found to analyze.")

print("\n--- Analysis complete. ---")