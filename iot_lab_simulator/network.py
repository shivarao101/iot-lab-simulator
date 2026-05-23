"""Network simulation modules (MQTT, ThingSpeak, etc.)"""

import json
from datetime import datetime

class SimulatedMQTTBroker:
    """Simulated MQTT broker for testing"""
    
    def __init__(self):
        self.topics = {}
        self.clients = []
        
    def publish(self, topic, message):
        """Publish a message to a topic"""
        if topic not in self.topics:
            self.topics[topic] = []
        self.topics[topic].append({
            'message': message,
            'timestamp': datetime.now()
        })
        # Notify subscribers
        for client in self.clients:
            if hasattr(client, 'subscriptions') and topic in client.subscriptions:
                client.on_message(topic, message)
                
    def subscribe(self, client, topic):
        """Subscribe a client to a topic"""
        if not hasattr(client, 'subscriptions'):
            client.subscriptions = []
        client.subscriptions.append(topic)
        if client not in self.clients:
            self.clients.append(client)
        
    def get_messages(self, topic, limit=10):
        """Get recent messages from a topic"""
        if topic in self.topics:
            return self.topics[topic][-limit:]
        return []

class SimulatedThingSpeak:
    """Simulated ThingSpeak cloud service"""
    
    def __init__(self):
        self.channels = {}
        
    def update_channel(self, channel_id, data):
        """Update a channel with new data"""
        if channel_id not in self.channels:
            self.channels[channel_id] = []
        self.channels[channel_id].append({
            'data': data,
            'timestamp': datetime.now()
        })
        return True
        
    def get_data(self, channel_id, limit=10):
        """Get recent data from a channel"""
        if channel_id in self.channels:
            return self.channels[channel_id][-limit:]
        return []