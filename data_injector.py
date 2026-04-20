import redis
import json
import time
import random

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

zones = ['North Gate', 'South Gate', 'East Stand', 'West Stand', 'Food Court']
stalls = ['food_A', 'food_B', 'food_C', 'merch_stand', 'wc_north', 'wc_south']

print("Data injector started - Dashboard will show LIVE data now!")

while True:
    try:
        # Generate random crowd data
        densities = {}
        for zone in zones:
            count = random.randint(50, 450)
            capacity = 500
            densities[zone] = round(count / capacity, 2)
        
        hotspot = max(densities, key=densities.get)
        
        crowd_data = {
            'zone_densities': densities,
            'hotspot': hotspot,
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S')
        }
        r.setex('crowd_state', 30, json.dumps(crowd_data))
        
        # Generate random queue data
        queue_data = {}
        for stall in stalls:
            wait = random.randint(1, 15)
            queue_data[stall] = wait
        r.setex('queue_state', 30, json.dumps(queue_data))
        
        # Generate recommendations
        busy_zone = hotspot
        less_busy = min(densities, key=densities.get)
        
        recs = {
            'action': f'Go to {less_busy} - Less crowded!',
            'reason': f'{busy_zone} is at {int(densities[busy_zone]*100)}% capacity',
            'confidence': round(random.uniform(0.7, 0.95), 2),
            'staff_alert': 'Long queues at Food Court!' if densities['Food Court'] > 0.8 else None
        }
        r.setex('recommendations', 30, json.dumps(recs))
        
        # Set match phase
        phases = ['PRE', 'LIVE', 'HALFTIME', 'POST']
        current_phase = random.choice(phases)
        r.setex('match_phase', 30, current_phase)
        
        # Set plan
        plan = {
            'current_phase': current_phase,
            'plan_sequence': [
                {'action': f'Enter via {less_busy}', 'confidence': 0.85},
                {'action': 'Grab food early', 'confidence': 0.75}
            ]
        }
        r.setex('plan', 30, json.dumps(plan))
        
        print(f"Updated: {current_phase} | Hotspot: {hotspot} | Queues: {len(queue_data)} stalls")
        time.sleep(2)
        
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)
