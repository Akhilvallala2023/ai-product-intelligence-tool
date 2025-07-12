import json
from typing import List, Dict, Any

# Static product database with 20 sample products (lights and fans)
SAMPLE_PRODUCTS = [
    # String Lights (10 products)
    {
        "id": 1,
        "name": "Brightown 50ft LED String Lights",
        "price": 29.99,
        "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400",
        "category": "lighting",
        "product_type": "string lights",
        "brand": "Brightown",
        "color": "warm white",
        "size": "50 ft",
        "material": "plastic",
        "style": "outdoor",
        "key_features": ["waterproof", "dimmable", "connectable", "25 bulbs", "2 spare bulbs"],
        "specifications": {
            "length": "50 ft",
            "bulb_count": 25,
            "light_color": "warm white",
            "waterproof_rating": "IP65",
            "power_source": "AC"
        },
        "description": "Premium outdoor string lights perfect for patios, gardens, and parties"
    },
    {
        "id": 2,
        "name": "Solar Powered Garden String Lights",
        "price": 19.99,
        "image_url": "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=400",
        "category": "lighting",
        "product_type": "string lights",
        "brand": "SolarGlow",
        "color": "multicolor",
        "size": "33 ft",
        "material": "copper wire",
        "style": "decorative",
        "key_features": ["solar powered", "8 lighting modes", "waterproof", "auto on/off"],
        "specifications": {
            "length": "33 ft",
            "bulb_count": 100,
            "light_color": "multicolor",
            "waterproof_rating": "IP44",
            "power_source": "solar"
        },
        "description": "Eco-friendly solar string lights with vibrant colors and multiple lighting modes"
    },
    {
        "id": 3,
        "name": "Vintage Edison Bulb String Lights",
        "price": 39.99,
        "image_url": "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=400",
        "category": "lighting",
        "product_type": "string lights",
        "brand": "RetroLite",
        "color": "amber",
        "size": "25 ft",
        "material": "glass",
        "style": "vintage",
        "key_features": ["edison bulbs", "dimmable", "warm glow", "commercial grade"],
        "specifications": {
            "length": "25 ft",
            "bulb_count": 12,
            "light_color": "amber",
            "waterproof_rating": "IP65",
            "power_source": "AC"
        },
        "description": "Classic vintage string lights with authentic Edison bulbs for elegant ambiance"
    },
    {
        "id": 4,
        "name": "USB Powered Fairy Lights",
        "price": 12.99,
        "image_url": "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=400",
        "category": "lighting",
        "product_type": "string lights",
        "brand": "FairyGlow",
        "color": "cool white",
        "size": "20 ft",
        "material": "copper wire",
        "style": "fairy",
        "key_features": ["USB powered", "flexible wire", "timer function", "remote control"],
        "specifications": {
            "length": "20 ft",
            "bulb_count": 200,
            "light_color": "cool white",
            "waterproof_rating": "IP20",
            "power_source": "USB"
        },
        "description": "Delicate fairy lights perfect for indoor decoration and crafts"
    },
    {
        "id": 5,
        "name": "Outdoor Bistro String Lights",
        "price": 45.99,
        "image_url": "https://images.unsplash.com/photo-1513475382585-d06e58bcb0e0?w=400",
        "category": "lighting",
        "product_type": "string lights",
        "brand": "BistroLux",
        "color": "warm white",
        "size": "48 ft",
        "material": "plastic",
        "style": "bistro",
        "key_features": ["shatterproof", "heavy duty", "linkable", "commercial grade"],
        "specifications": {
            "length": "48 ft",
            "bulb_count": 24,
            "light_color": "warm white",
            "waterproof_rating": "IP65",
            "power_source": "AC"
        },
        "description": "Commercial-grade bistro lights perfect for restaurants and outdoor events"
    },
    # Ceiling Fans (10 products)
    {
        "id": 6,
        "name": "Hunter Original 52-inch Ceiling Fan",
        "price": 149.99,
        "image_url": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400",
        "category": "fans",
        "product_type": "ceiling fan",
        "brand": "Hunter",
        "color": "white",
        "size": "52 inch",
        "material": "metal",
        "style": "traditional",
        "key_features": ["reversible motor", "5 blades", "pull chain", "lifetime warranty"],
        "specifications": {
            "diameter": "52 inch",
            "blade_count": 5,
            "motor_type": "reversible",
            "airflow": "4968 CFM",
            "power_consumption": "75W"
        },
        "description": "Classic ceiling fan with powerful motor and traditional design"
    },
    {
        "id": 7,
        "name": "Modern LED Ceiling Fan with Remote",
        "price": 199.99,
        "image_url": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400",
        "category": "fans",
        "product_type": "ceiling fan",
        "brand": "ModernAir",
        "color": "black",
        "size": "44 inch",
        "material": "aluminum",
        "style": "modern",
        "key_features": ["LED lighting", "remote control", "reversible", "quiet operation"],
        "specifications": {
            "diameter": "44 inch",
            "blade_count": 3,
            "motor_type": "DC motor",
            "airflow": "3200 CFM",
            "power_consumption": "32W"
        },
        "description": "Sleek modern ceiling fan with integrated LED lighting and remote control"
    },
    {
        "id": 8,
        "name": "Vintage Industrial Ceiling Fan",
        "price": 289.99,
        "image_url": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400",
        "category": "fans",
        "product_type": "ceiling fan",
        "brand": "Industrial",
        "color": "bronze",
        "size": "60 inch",
        "material": "iron",
        "style": "industrial",
        "key_features": ["cage design", "vintage bulbs", "heavy duty", "adjustable speeds"],
        "specifications": {
            "diameter": "60 inch",
            "blade_count": 4,
            "motor_type": "AC motor",
            "airflow": "6800 CFM",
            "power_consumption": "188W"
        },
        "description": "Industrial-style ceiling fan with vintage cage design and Edison bulbs"
    },
    {
        "id": 9,
        "name": "Smart WiFi Ceiling Fan",
        "price": 329.99,
        "image_url": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400",
        "category": "fans",
        "product_type": "ceiling fan",
        "brand": "SmartHome",
        "color": "white",
        "size": "52 inch",
        "material": "composite",
        "style": "smart",
        "key_features": ["WiFi enabled", "app control", "voice control", "scheduling"],
        "specifications": {
            "diameter": "52 inch",
            "blade_count": 5,
            "motor_type": "DC motor",
            "airflow": "4200 CFM",
            "power_consumption": "45W"
        },
        "description": "Smart ceiling fan with WiFi connectivity and app control"
    },
    {
        "id": 10,
        "name": "Outdoor Patio Ceiling Fan",
        "price": 249.99,
        "image_url": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400",
        "category": "fans",
        "product_type": "ceiling fan",
        "brand": "OutdoorPro",
        "color": "bronze",
        "size": "54 inch",
        "material": "stainless steel",
        "style": "outdoor",
        "key_features": ["weather resistant", "damp rated", "powerful motor", "rust proof"],
        "specifications": {
            "diameter": "54 inch",
            "blade_count": 5,
            "motor_type": "AC motor",
            "airflow": "5200 CFM",
            "power_consumption": "89W"
        },
        "description": "Weather-resistant ceiling fan designed for outdoor patios and covered areas"
    },
    # Table Fans (5 products)
    {
        "id": 11,
        "name": "Honeywell Turbo Desktop Fan",
        "price": 39.99,
        "image_url": "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=400",
        "category": "fans",
        "product_type": "table fan",
        "brand": "Honeywell",
        "color": "black",
        "size": "8 inch",
        "material": "plastic",
        "style": "desktop",
        "key_features": ["compact design", "quiet operation", "adjustable tilt", "3 speeds"],
        "specifications": {
            "diameter": "8 inch",
            "blade_count": 3,
            "motor_type": "AC motor",
            "airflow": "145 CFM",
            "power_consumption": "25W"
        },
        "description": "Compact desktop fan perfect for personal cooling in offices and bedrooms"
    },
    {
        "id": 12,
        "name": "Retro Metal Oscillating Fan",
        "price": 79.99,
        "image_url": "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=400",
        "category": "fans",
        "product_type": "table fan",
        "brand": "RetroWind",
        "color": "copper",
        "size": "12 inch",
        "material": "metal",
        "style": "retro",
        "key_features": ["oscillating", "metal construction", "vintage design", "powerful motor"],
        "specifications": {
            "diameter": "12 inch",
            "blade_count": 4,
            "motor_type": "AC motor",
            "airflow": "450 CFM",
            "power_consumption": "45W"
        },
        "description": "Classic retro-style metal fan with oscillating function and vintage appeal"
    },
    {
        "id": 13,
        "name": "USB Rechargeable Desk Fan",
        "price": 24.99,
        "image_url": "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=400",
        "category": "fans",
        "product_type": "table fan",
        "brand": "PortablePro",
        "color": "white",
        "size": "6 inch",
        "material": "plastic",
        "style": "portable",
        "key_features": ["rechargeable battery", "USB charging", "clip-on design", "quiet"],
        "specifications": {
            "diameter": "6 inch",
            "blade_count": 3,
            "motor_type": "DC motor",
            "airflow": "95 CFM",
            "power_consumption": "5W"
        },
        "description": "Portable rechargeable fan with clip-on design for versatile placement"
    },
    {
        "id": 14,
        "name": "Tower Fan with Remote Control",
        "price": 89.99,
        "image_url": "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=400",
        "category": "fans",
        "product_type": "tower fan",
        "brand": "TowerCool",
        "color": "silver",
        "size": "42 inch",
        "material": "plastic",
        "style": "tower",
        "key_features": ["oscillating", "timer function", "remote control", "LED display"],
        "specifications": {
            "height": "42 inch",
            "blade_count": 0,
            "motor_type": "AC motor",
            "airflow": "280 CFM",
            "power_consumption": "65W"
        },
        "description": "Sleek tower fan with remote control and multiple speed settings"
    },
    {
        "id": 15,
        "name": "Pedestal Fan with Height Adjustment",
        "price": 69.99,
        "image_url": "https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=400",
        "category": "fans",
        "product_type": "pedestal fan",
        "brand": "FloorStand",
        "color": "white",
        "size": "16 inch",
        "material": "plastic",
        "style": "pedestal",
        "key_features": ["height adjustable", "oscillating", "tilt adjustment", "stable base"],
        "specifications": {
            "diameter": "16 inch",
            "blade_count": 5,
            "motor_type": "AC motor",
            "airflow": "520 CFM",
            "power_consumption": "55W"
        },
        "description": "Adjustable pedestal fan with oscillating function and stable base"
    },
    # Additional Lighting (5 products)
    {
        "id": 16,
        "name": "LED Strip Lights RGB",
        "price": 34.99,
        "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400",
        "category": "lighting",
        "product_type": "LED strips",
        "brand": "ColorLED",
        "color": "RGB",
        "size": "32 ft",
        "material": "silicone",
        "style": "accent",
        "key_features": ["color changing", "app control", "music sync", "cuttable"],
        "specifications": {
            "length": "32 ft",
            "led_count": 300,
            "light_color": "RGB",
            "waterproof_rating": "IP65",
            "power_source": "AC adapter"
        },
        "description": "Flexible RGB LED strip lights with app control and music synchronization"
    },
    {
        "id": 17,
        "name": "Solar Pathway Lights Set",
        "price": 49.99,
        "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400",
        "category": "lighting",
        "product_type": "pathway lights",
        "brand": "SolarPath",
        "color": "warm white",
        "size": "pack of 8",
        "material": "stainless steel",
        "style": "landscape",
        "key_features": ["solar powered", "auto on/off", "weather resistant", "easy install"],
        "specifications": {
            "quantity": 8,
            "light_color": "warm white",
            "waterproof_rating": "IP65",
            "power_source": "solar",
            "runtime": "8 hours"
        },
        "description": "Set of 8 solar pathway lights for garden and landscape illumination"
    },
    {
        "id": 18,
        "name": "Smart Motion Sensor Light",
        "price": 29.99,
        "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400",
        "category": "lighting",
        "product_type": "motion sensor light",
        "brand": "SmartSense",
        "color": "white",
        "size": "6 inch",
        "material": "aluminum",
        "style": "security",
        "key_features": ["motion detection", "adjustable sensitivity", "battery powered", "wireless"],
        "specifications": {
            "detection_range": "20 ft",
            "light_color": "cool white",
            "waterproof_rating": "IP54",
            "power_source": "battery",
            "battery_life": "6 months"
        },
        "description": "Wireless motion sensor light with adjustable sensitivity and long battery life"
    },
    {
        "id": 19,
        "name": "Vintage Pendant Light",
        "price": 79.99,
        "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400",
        "category": "lighting",
        "product_type": "pendant light",
        "brand": "VintageHome",
        "color": "bronze",
        "size": "12 inch",
        "material": "metal",
        "style": "vintage",
        "key_features": ["adjustable cord", "Edison bulb", "industrial design", "dimmable"],
        "specifications": {
            "diameter": "12 inch",
            "cord_length": "6 ft",
            "light_color": "warm white",
            "bulb_type": "Edison",
            "power_source": "AC"
        },
        "description": "Industrial vintage pendant light with Edison bulb and adjustable cord"
    },
    {
        "id": 20,
        "name": "Rechargeable Work Light",
        "price": 44.99,
        "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400",
        "category": "lighting",
        "product_type": "work light",
        "brand": "WorkPro",
        "color": "yellow",
        "size": "10 inch",
        "material": "plastic",
        "style": "portable",
        "key_features": ["rechargeable", "magnetic base", "adjustable brightness", "rugged"],
        "specifications": {
            "brightness": "2000 lumens",
            "light_color": "cool white",
            "waterproof_rating": "IP65",
            "power_source": "rechargeable battery",
            "runtime": "4 hours"
        },
        "description": "Heavy-duty rechargeable work light with magnetic base and high brightness"
    }
]


class ProductDatabase:
    def __init__(self):
        self.products = SAMPLE_PRODUCTS
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        """Get all products from the database"""
        return self.products
    
    def get_product_by_id(self, product_id: int) -> Dict[str, Any]:
        """Get a specific product by ID"""
        for product in self.products:
            if product["id"] == product_id:
                return product
        return None
    
    def get_products_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get products by category"""
        return [product for product in self.products if product["category"].lower() == category.lower()]
    
    def get_products_by_type(self, product_type: str) -> List[Dict[str, Any]]:
        """Get products by product type"""
        return [product for product in self.products if product_type.lower() in product["product_type"].lower()]
    
    def search_products(self, query: str) -> List[Dict[str, Any]]:
        """Basic text search across product fields"""
        query = query.lower()
        results = []
        
        for product in self.products:
            # Search in various fields
            searchable_text = " ".join([
                product["name"].lower(),
                product["category"].lower(),
                product["product_type"].lower(),
                product["brand"].lower() if product["brand"] else "",
                product["color"].lower(),
                product["style"].lower(),
                product["description"].lower(),
                " ".join(product["key_features"]),
            ])
            
            if query in searchable_text:
                results.append(product)
        
        return results


# Global instance
product_db = ProductDatabase() 