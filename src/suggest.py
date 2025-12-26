import plotly.graph_objects as go



def get_suggestions(prediction, probability, input_data):
    """Generate suggestions based on prediction and input data"""
    suggestions = []
    
    if prediction == 0:  # Will NOT complete
        suggestions.append({
            'title': '🚨 HIGH RISK - Booking Likely to be Abandoned',
            'priority': 'CRITICAL',
            'class': 'high-risk'
        })
        suggestions.append({
            'title': '📞 Immediate Follow-up Required',
            'description': 'Contact customer within 2 hours to address concerns and provide assistance',
            'class': 'high-risk'
        })
        suggestions.append({
            'title': '🎁 Apply Incentive Offer',
            'description': 'Offer 10-15% discount or complimentary service upgrade to encourage completion',
            'class': 'high-risk'
        })
    else:  # Will complete
        if probability < 0.7:  # Low confidence
            suggestions.append({
                'title': '⚠️ MEDIUM RISK - Monitor Closely',
                'priority': 'MODERATE',
                'class': 'medium-risk'
            })
            suggestions.append({
                'title': '📧 Send Confirmation Reminder',
                'description': 'Send an email within 24 hours with booking benefits and support contact',
                'class': 'medium-risk'
            })
        else:
            suggestions.append({
                'title': '✅ LOW RISK - Standard Monitoring',
                'priority': 'LOW',
                'class': 'low-risk'
            })
            suggestions.append({
                'title': '📬 Standard Follow-up',
                'description': 'Send automated confirmation email and proceed with normal workflow',
                'class': 'low-risk'
            })
    
    # Specific suggestions based on input
    if input_data['purchase_lead'] < 7:
        suggestions.append({
            'title': '📅 Last-Minute Booking',
            'description': 'Expedite support response. Ensure 24/7 helpline availability. Highlight flexible cancellation.',
            'class': 'high-risk' if prediction == 0 else 'medium-risk'
        })
    
    if input_data['total_extras'] == 0:
        suggestions.append({
            'title': '💰 Price-Sensitive Customer',
            'description': 'Emphasize value for money. Offer bundle deals (e.g., baggage + meals at 20% off).',
            'class': 'medium-risk'
        })
    
    if input_data['num_passengers'] >= 3:
        suggestions.append({
            'title': '👨‍👩‍👧‍👦 Group Booking',
            'description': 'Verify group discount is applied. Assign dedicated agent. Simplify group check-in process.',
            'class': 'medium-risk'
        })
    
    if input_data['flight_duration'] > 6:
        suggestions.append({
            'title': '✈️ Long-Haul Flight',
            'description': 'Highlight premium amenities, entertainment options, and comfort features.',
            'class': 'low-risk'
        })
    
    if input_data['sales_channel'] == 'Mobile':
        suggestions.append({
            'title': '📱 Mobile Booking',
            'description': 'Ensure mobile-optimized checkout. Send push notifications. Enable quick payment options.',
            'class': 'medium-risk' if prediction == 0 else 'low-risk'
        })
    
    if input_data['length_of_stay'] > 14:
        suggestions.append({
            'title': '🏨 Extended Stay',
            'description': 'Recommend hotel packages, car rental deals, or travel insurance for long trips.',
            'class': 'low-risk'
        })
    
    if input_data['inconvenient_flight_time']:
        suggestions.append({
            'title': '🌙 Inconvenient Flight Time',
            'description': 'Offer lounge access or airport hotel options. Explain convenience of early/late flights.',
            'class': 'medium-risk'
        })
    
    return suggestions

def create_prediction_visual(prediction, probability):
    """Create a visual representation of the prediction"""
    
    if prediction == 1:
        color = '#10b981'
        result_text = "WILL COMPLETE"
        icon = "✅"
        confidence = "High Confidence" if probability > 0.7 else "Moderate Confidence"
    else:
        color = '#ef4444'
        result_text = "WILL NOT COMPLETE"
        icon = "❌"
        confidence = "High Confidence" if probability < 0.3 else "Moderate Confidence"
    
    fig = go.Figure()
    
    fig.add_trace(go.Indicator(
        mode = "gauge+number",
        value = probability * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"<b>{result_text}</b><br><span style='font-size:16px'>{confidence}</span>", 
                 'font': {'size': 24}},
        number = {'suffix': "% Confidence", 'font': {'size': 40}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 2},
            'bar': {'color': color, 'thickness': 0.8},
            'bgcolor': "white",
            'borderwidth': 3,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': '#fee2e2'},
                {'range': [50, 100], 'color': '#d1fae5'}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 6},
                'thickness': 0.9,
                'value': 50
            }
        }
    ))
    
    fig.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=80, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "#1e293b", 'family': "Arial"}
    )
    
    return fig
