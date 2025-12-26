import streamlit as st
import pandas as pd
import numpy as np
import pickle
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px


from src.feature_eng import get_feature_columns,engineer_features
from src.suggest import get_suggestions


# Page configuration
st.set_page_config(
    page_title="BA Booking Prediction",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

#Load CSS
def load_css(path):
    with open(path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
load_css("assets/style.css")

# Load models and preprocessors
@st.cache_resource
def load_model_and_scaler():
    try:
        with open('model/best_model.pkl', 'rb') as f:
            model = pickle.load(f)
        with open('model/scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        return model, scaler
    except FileNotFoundError:
        st.error("⚠️ Model files not found! Please ensure 'best_model.pkl' and 'scaler.pkl' are in the same directory.")
        return None, None

model, scaler = load_model_and_scaler()

# Main App
def main():
    # Header
    st.markdown(
        """
        <div style="width:100%; display:flex; justify-content:center;">
            <div class="header">✈️ British Airways Booking Prediction System</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style="width:100%; display:flex; justify-content:center;">
            <div class="sub-header">Predict booking completion probability with AI-powered insights</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if model is None or scaler is None:
        st.error("Cannot proceed without model files. Please check the error message above.")
        return
    
    # Sidebar info
    st.sidebar.title("ℹ️ System Information")
    st.sidebar.info("""
    **Prediction Model**
    - Type: Classification
    - Output: Will Complete / Will Not Complete
    - Confidence Score: Model certainty
    
    **How to Use:**
    1. Enter booking details
    2. Click "Predict Booking Status"
    3. Review classification result
    4. Follow actionable suggestions
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.success("✅ Model: Loaded & Ready")
    st.sidebar.metric("Model Type", "Binary Classifier")
    
    # Main input section
    st.markdown("## 📝 Enter Booking Details")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 👥 Travel Information")
        num_passengers = st.number_input("Number of Passengers", min_value=1, max_value=10, value=1)
        trip_type = st.selectbox("Trip Type", ["RoundTrip", "OneWay", "CircleTrip"])
        length_of_stay = st.number_input("Length of Stay (days)", min_value=1, max_value=365, value=7)
    
    with col2:
        st.markdown("### 🕒 Flight Details")
        purchase_lead = st.number_input("Booking in Advance (days)", min_value=0, max_value=365, value=30,
                                       help="How many days before the flight is the booking made?")
        flight_hour = st.slider("Flight Departure Hour (24h)", 0, 23, 12)
        flight_day = st.selectbox("Flight Day", 
                                 ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        flight_day_num = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].index(flight_day) + 1
        flight_duration = st.number_input("Flight Duration (hours)", min_value=0.5, max_value=20.0, value=5.0, step=0.5)
    
    with col3:
        st.markdown("### ✨ Add-on Services")
        sales_channel = st.selectbox("Booking Channel", ["Internet", "Mobile"])
        wants_extra_baggage = st.checkbox("Extra Baggage")
        wants_preferred_seat = st.checkbox("Preferred Seat")
        wants_in_flight_meals = st.checkbox("In-flight Meals")
        
        st.markdown("### 🌍 Route Information")
        route = st.text_input("Route (e.g., LHR-JFK)", value="LHR-JFK")
        booking_origin = st.text_input("Booking Origin Country", value="UK")
    
    # Predict button
    st.markdown("---")
    if st.button("🔮 Predict Booking Status", use_container_width=True, type="primary"):
        # Prepare input data
        input_data = {
            'num_passengers': num_passengers,
            'sales_channel': sales_channel,
            'trip_type': trip_type,
            'purchase_lead': purchase_lead,
            'length_of_stay': length_of_stay,
            'flight_hour': flight_hour,
            'flight_day': flight_day_num,
            'route': route,
            'booking_origin': booking_origin,
            'wants_extra_baggage': int(wants_extra_baggage),
            'wants_preferred_seat': int(wants_preferred_seat),
            'wants_in_flight_meals': int(wants_in_flight_meals),
            'flight_duration': flight_duration,
            'total_extras': int(wants_extra_baggage) + int(wants_preferred_seat) + int(wants_in_flight_meals),
            'inconvenient_flight_time': int(flight_hour < 6 or flight_hour >= 22)
        }
        
        # Create DataFrame
        input_df = pd.DataFrame([input_data])
        
        # Engineer features
        featured_df = engineer_features(input_df)
        
        # Get prediction features in correct order
        feature_cols = get_feature_columns()
        X_pred = featured_df[feature_cols]
        
        # Scale features if using Logistic Regression
        try:
            X_pred_scaled = scaler.transform(X_pred)
            X_final = X_pred_scaled
        except:
            X_final = X_pred
        
        # Make prediction
        prediction = model.predict(X_final)[0]
        probability = model.predict_proba(X_final)[0][1]  # Probability of class 1 (completion)
        
        # Adjust probability based on prediction
        if prediction == 0:
            confidence_score = 1 - probability  # Confidence in "will not complete"
        else:
            confidence_score = probability  # Confidence in "will complete"
        
        # Display results
        st.markdown("---")
        st.markdown("## 🎯 Prediction Results")
        
        # Top section with prediction and key metrics
        result_col1, result_col2 = st.columns([2, 1])
        
        with result_col1:
           
            st.markdown("### 💡 Actionable Suggestions")
            
            # Get suggestions
            suggestions = get_suggestions(prediction, confidence_score, input_data)
            
            # Display suggestions
            for suggestion in suggestions:
                risk_class = suggestion.get('class', 'low-risk')
                title = suggestion.get('title', '')
                description = suggestion.get('description', '')
                priority = suggestion.get('priority', '')
                
                if priority:
                    st.markdown(f"""
                        <div class="suggestion-box {risk_class}">
                            <h4 style="margin: 0 0 0.5rem 0;">{title}</h4>
                            <p style="margin: 0; font-weight: bold;">Priority: {priority}</p>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div class="suggestion-box {risk_class}">
                            <h4 style="margin: 0 0 0.5rem 0;">{title}</h4>
                            <p style="margin: 0; font-size: 0.9rem;">{description}</p>
                        </div>
                    """, unsafe_allow_html=True)
        
        with result_col2:
            st.markdown("### 📊 Classification Result")
            
            # Main prediction box
            if prediction == 1:
                box_class = "will-complete"
                emoji = "✅"
                result = "WILL COMPLETE"
                message = "Customer likely to complete booking"
            else:
                box_class = "will-not-complete"
                emoji = "❌"
                result = "WILL NOT COMPLETE"
                message = "Customer likely to abandon booking"
            
            st.markdown(f"""
                <div class="prediction-box {box_class}">
                    <h1 style="font-size: 3rem; margin: 0;">{emoji}</h1>
                    <h2 style="margin: 0.5rem 0;">{result}</h2>
                    <p style="margin: 0; font-size: 1.1rem;">{message}</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 📈 Key Metrics")
            st.metric("Model Confidence", f"{confidence_score*100:.1f}%")
            st.metric("Risk Level", 
                     "🔴 HIGH" if prediction == 0 else "🟡 MEDIUM" if confidence_score < 0.7 else "🟢 LOW")
            st.metric("Follow-up Priority", 
                     "URGENT" if prediction == 0 else "STANDARD")
        
        # Detailed analysis section
        st.markdown("---")
        st.markdown("## 📊 Detailed Analysis")
        
        analysis_col1, analysis_col2 = st.columns([2, 1])
        
        with analysis_col1:
            st.markdown("### 🔍 Booking Profile Analysis")
            
            # Create analysis dataframe
            profile_data = {
                'Category': ['Customer Type', 'Booking Behavior', 'Service Preference', 'Trip Type'],
                'Classification': [
                    '👤 Solo' if num_passengers == 1 else '👥 Couple' if num_passengers == 2 else '👨‍👩‍👧‍👦 Group',
                    '🏃 Last Minute' if purchase_lead < 7 else '📅 Short Term' if purchase_lead < 30 else '📆 Well Planned',
                    '💎 Premium' if input_data['total_extras'] == 3 else '⭐ Standard' if input_data['total_extras'] > 0 else '💰 Budget',
                    '🔄 Round Trip' if trip_type == 'RoundTrip' else '➡️ One Way' if trip_type == 'OneWay' else '🔁 Circle Trip'
                ],
                'Risk Factor': [
                    'Low' if num_passengers <= 2 else 'Medium',
                    'High' if purchase_lead < 7 else 'Medium' if purchase_lead < 30 else 'Low',
                    'Low' if input_data['total_extras'] >= 2 else 'High',
                    'Low' if trip_type == 'RoundTrip' else 'Medium'
                ]
            }
            
            profile_df = pd.DataFrame(profile_data)
            st.dataframe(profile_df, use_container_width=True, hide_index=True)
            
            
        with analysis_col2:
            # Additional factors
            st.markdown("### 📌 Key Factors Identified")
            factor_cols = st.columns(3)
            
            with factor_cols[0]:
                if purchase_lead < 7:
                    st.error("⚠️ Last-minute booking")
                if input_data['total_extras'] == 0:
                    st.warning("💰 No add-ons selected")
            
            with factor_cols[1]:
                if num_passengers >= 3:
                    st.info("👨‍👩‍👧‍👦 Group travel")
                if flight_duration > 6:
                    st.info("✈️ Long-haul flight")
            
            with factor_cols[2]:
                if sales_channel == 'Mobile':
                    st.info("📱 Mobile booking")
                if length_of_stay > 14:
                    st.info("🏨 Extended stay")
        
        # Action buttons section
        st.markdown("---")
        st.markdown("## 🎯 Recommended Actions")
        
        action_col1, action_col2, action_col3 = st.columns(3)
        
        with action_col1:
            if st.button("📧 Send Follow-up Email", use_container_width=True):
                st.success("✅ Follow-up email queued for delivery")
        
        with action_col2:
            if st.button("📞 Schedule Support Call", use_container_width=True):
                st.success("✅ Support call scheduled with next available agent")
        
        with action_col3:
            if prediction == 0:
                if st.button("🎁 Generate Incentive Code", use_container_width=True):
                    st.success("✅ 10% discount code: BA2024SAVE10")
            else:
                if st.button("📋 Add to Follow-up List", use_container_width=True):
                    st.success("✅ Added to standard follow-up queue")

if __name__ == "__main__":
    main()