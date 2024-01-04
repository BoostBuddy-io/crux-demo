import os
import requests
import argparse
import matplotlib.pyplot as plt
from dotenv import load_dotenv

load_dotenv()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Audit URL with CrUX dataset.'
    )

    parser.add_argument(
        '-u',
        '--url',
        required=True,
        type=str,
        help='Provide URL to audit'
    )

    args = parser.parse_args()

    headers = {
        'Accept': 'application.json',
        'Content-Type': 'application.json'
    }

    devices = [
        'PHONE',
        'DESKTOP'
    ]

    for d in devices:        

        json = {
            'formFactor': d,
            'origin': args.url,
            'metrics': [
                'largest_contentful_paint',
                'first_input_delay',
                'cumulative_layout_shift',
                'first_contentful_paint',
                'interaction_to_next_paint',
                'experimental_time_to_first_byte'
            ]
        }

        url = f"https://chromeuxreport.googleapis.com/v1/records:queryRecord?key={os.getenv('CRUX_KEY')}"
        response = requests.post(url, headers=headers, json=json).json()
        
        fig, axs = plt.subplots(1, 6, figsize=[15, 5], sharey=True, tight_layout=True)
        n_bins = 3
        
        count = 0
        for metric in response['record']['metrics']:
            data = response['record']['metrics'][metric]

            densities = []
            time_thresholds = []
            for h in data['histogram']:

                if 'end' in h:
                    interval = f"{h['start']} - {h['end']} ms"
                else:
                    interval = f"> {h['start']} ms"

                time_thresholds.append(interval)
                densities.append(round(h['density'] * 100, 2))
            
            axs[count].bar(range(len(densities)), densities, color=['green', 'orange', 'red'])
            axs[count].set_xticks(range(len(densities)))
            axs[count].set_xticklabels(time_thresholds, rotation=30)
            axs[count].set_title(metric)
            count += 1
        
        fig.suptitle(d)
        plt.show()
