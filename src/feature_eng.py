import pandas as pd
import numpy as np

# Feature engineering function
def engineer_features(df):
    """Apply the same feature engineering as in training"""
    
    # Temporal Features
    df['booking_urgency'] = pd.cut(df['purchase_lead'], 
                                    bins=[-1, 7, 30, 90, np.inf],
                                    labels=[0, 1, 2, 3])
    df['is_weekend_flight'] = df['flight_day'].isin([6, 7]).astype(int)
    
    def categorize_flight_time(hour):
        if 5 <= hour < 12:
            return 0  # morning
        elif 12 <= hour < 17:
            return 1  # afternoon
        elif 17 <= hour < 21:
            return 2  # evening
        else:
            return 3  # night
    
    df['flight_time_category'] = df['flight_hour'].apply(categorize_flight_time)
    df['inconvenient_flight_time'] = df['flight_hour'].isin(list(range(0, 6)) + list(range(22, 24))).astype(int)
    
    # Behavioral Features
    df['total_extras'] = (df['wants_extra_baggage'] + 
                          df['wants_preferred_seat'] + 
                          df['wants_in_flight_meals'])
    df['high_engagement'] = (df['total_extras'] >= 2).astype(int)
    df['is_premium_customer'] = (df['total_extras'] == 3).astype(int)
    df['no_extras'] = (df['total_extras'] == 0).astype(int)
    
    # Trip Complexity Features
    df['is_group_travel'] = (df['num_passengers'] >= 3).astype(int)
    df['is_solo_traveler'] = (df['num_passengers'] == 1).astype(int)
    df['is_long_haul'] = (df['flight_duration'] > 6).astype(int)
    df['is_short_trip'] = (df['length_of_stay'] <= 3).astype(int)
    df['is_extended_stay'] = (df['length_of_stay'] > 14).astype(int)
    
    df['trip_complexity'] = (
        df['is_group_travel'] * 1 +
        df['is_long_haul'] * 1 +
        df['is_extended_stay'] * 1 +
        (df['trip_type'] == 'CircleTrip').astype(int) * 2
    )
    
    # Route Features
    
    df['route_frequency'] = 100
    df['is_popular_route'] = 1
    
    # Interaction Features
    df['passengers_per_day'] = df['num_passengers'] / (df['length_of_stay'] + 1)
    df['planning_ratio'] = df['purchase_lead'] / (df['length_of_stay'] + 1)
    df['duration_per_passenger'] = df['flight_duration'] / df['num_passengers']
    df['last_minute_complex'] = ((df['purchase_lead'] < 7) & (df['trip_complexity'] >= 2)).astype(int)
    
    # Encode categorical variables
    sales_channel_map = {'Internet': 0, 'Mobile': 1}
    trip_type_map = {'RoundTrip': 0, 'OneWay': 1, 'CircleTrip': 2}
    
    df['sales_channel_encoded'] = df['sales_channel'].map(sales_channel_map).fillna(0)
    df['trip_type_encoded'] = df['trip_type'].map(trip_type_map).fillna(0)
    df['booking_urgency_encoded'] = df['booking_urgency'].astype(int)
    df['flight_time_category_encoded'] = df['flight_time_category'].astype(int)
    
    return df

def get_feature_columns():
    """Return the exact feature columns used in training"""
    return [
        'num_passengers', 'purchase_lead', 'length_of_stay', 
        'flight_hour', 'flight_day', 'flight_duration',
        'wants_extra_baggage', 'wants_preferred_seat', 'wants_in_flight_meals',
        'is_weekend_flight', 'inconvenient_flight_time',
        'total_extras', 'high_engagement', 'is_premium_customer', 'no_extras',
        'is_group_travel', 'is_solo_traveler', 'is_long_haul', 
        'is_short_trip', 'is_extended_stay', 'trip_complexity',
         'route_frequency', 'is_popular_route',
        'passengers_per_day', 'planning_ratio', 'duration_per_passenger', 
        'last_minute_complex',
        'sales_channel_encoded', 'trip_type_encoded', 
        'booking_urgency_encoded', 'flight_time_category_encoded'
    ]
