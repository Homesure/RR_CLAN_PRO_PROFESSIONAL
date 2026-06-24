from app import create_app, db
from app.models import Service

app = create_app()

services = [
    # CARE CLAN - SPECIAL OFFERS
    ("CARE CLAN", "Special Offers", "1 BHK Deep Cleaning + Free Veg Meal", 1999, "4-5 Hours", "Cleaning", "Complete 1 BHK deep cleaning with complimentary vegetarian meal.", "cleaning.jpg"),
    ("CARE CLAN", "Special Offers", "2 BHK Deep Cleaning + Free Veg Meal", 2999, "5-6 Hours", "Cleaning", "Complete 2 BHK deep cleaning with complimentary vegetarian meal.", "cleaning.jpg"),
    ("CARE CLAN", "Special Offers", "3 BHK Deep Cleaning + Free Veg Meal", 3999, "6-8 Hours", "Cleaning", "Complete 3 BHK deep cleaning with complimentary vegetarian meal.", "cleaning.jpg"),

    # CARE CLAN - CLEANING
    ("CARE CLAN", "House Cleaning", "Basic House Cleaning (1 BHK)", 2550, "3-4 Hours", "Cleaning", "Complete basic cleaning for 1 BHK home.", "cleaning.jpg"),
    ("CARE CLAN", "House Cleaning", "Basic House Cleaning (2 BHK)", 3550, "4-5 Hours", "Cleaning", "Complete basic cleaning for 2 BHK home.", "cleaning.jpg"),
    ("CARE CLAN", "House Cleaning", "Basic House Cleaning (3 BHK)", 4550, "5-6 Hours", "Cleaning", "Complete basic cleaning for 3 BHK home.", "cleaning.jpg"),
    ("CARE CLAN", "Deep Cleaning", "Deep Cleaning (1 BHK)", 4050, "4-5 Hours", "Cleaning", "Deep cleaning for 1 BHK home.", "cleaning.jpg"),
    ("CARE CLAN", "Deep Cleaning", "Deep Cleaning (2 BHK)", 5550, "5-6 Hours", "Cleaning", "Deep cleaning for 2 BHK home.", "cleaning.jpg"),
    ("CARE CLAN", "Deep Cleaning", "Deep Cleaning (3 BHK)", 7050, "6-8 Hours", "Cleaning", "Deep cleaning for 3 BHK home.", "cleaning.jpg"),
    ("CARE CLAN", "Special Cleaning", "Sofa Cleaning (5 Seater)", 750, "60-90 Minutes", "Cleaning", "Professional sofa cleaning.", "cleaning.jpg"),
    ("CARE CLAN", "Special Cleaning", "Mattress Cleaning", 550, "45-60 Minutes", "Cleaning", "Mattress dust and stain cleaning.", "cleaning.jpg"),
    ("CARE CLAN", "Special Cleaning", "Carpet Cleaning", 650, "60 Minutes", "Cleaning", "Carpet shampoo cleaning.", "cleaning.jpg"),
    ("CARE CLAN", "Special Cleaning", "Bathroom Cleaning", 550, "60 Minutes", "Cleaning", "Bathroom deep cleaning.", "cleaning.jpg"),
    ("CARE CLAN", "Special Cleaning", "Kitchen Deep Cleaning", 1550, "2-3 Hours", "Cleaning", "Kitchen oil, grease and deep cleaning.", "cleaning.jpg"),
    ("CARE CLAN", "Water Tank Cleaning", "Water Tank Cleaning (1000L)", 1050, "90 Minutes", "Cleaning", "Water tank cleaning up to 1000L.", "cleaning.jpg"),

    # CARE CLAN - CAR WASH
    ("CARE CLAN", "Car Wash", "Basic Car Wash", 400, "45 Minutes", "Car Wash", "Exterior basic car wash.", "carwash.jpg"),
    ("CARE CLAN", "Car Wash", "Foam Wash", 550, "60 Minutes", "Car Wash", "Premium foam wash.", "carwash.jpg"),
    ("CARE CLAN", "Car Wash", "Interior Cleaning", 850, "90 Minutes", "Car Wash", "Interior vacuum and cleaning.", "carwash.jpg"),
    ("CARE CLAN", "Car Wash", "Interior + Exterior Detailing", 2550, "3-4 Hours", "Car Wash", "Complete car detailing.", "carwash.jpg"),
    ("CARE CLAN", "Car Wash", "Ceramic Coating", 15050, "1 Day", "Car Wash", "Premium ceramic coating.", "carwash.jpg"),
    ("CARE CLAN", "Car Wash", "Bike Wash", 250, "30 Minutes", "Car Wash", "Bike wash service.", "carwash.jpg"),

    # TECH CLAN - AC
    ("TECH CLAN", "AC Service", "AC Service (Split)", 550, "45 Minutes", "AC Service", "Split AC servicing.", "ac.jpg"),
    ("TECH CLAN", "AC Service", "AC Service (Window)", 650, "45 Minutes", "AC Service", "Window AC servicing.", "ac.jpg"),
    ("TECH CLAN", "AC Service", "AC Gas Refilling", 2550, "90 Minutes", "AC Service", "AC gas refill service.", "ac.jpg"),
    ("TECH CLAN", "AC Service", "AC Installation", 1550, "2 Hours", "AC Service", "AC installation service.", "ac.jpg"),
    ("TECH CLAN", "AC Service", "AC Uninstallation", 850, "60 Minutes", "AC Service", "AC uninstallation service.", "ac.jpg"),
    ("TECH CLAN", "AC Service", "AC Repair Visit", 350, "Inspection Visit", "AC Service", "AC repair inspection visit.", "ac.jpg"),

    # TECH CLAN - PLUMBING
    ("TECH CLAN", "Plumbing", "Tap Repair", 300, "30-45 Minutes", "Plumbing", "Tap repair service.", "plumbing.jpg"),
    ("TECH CLAN", "Plumbing", "Basin Installation", 550, "60 Minutes", "Plumbing", "Wash basin installation.", "plumbing.jpg"),
    ("TECH CLAN", "Plumbing", "Toilet Repair", 550, "60 Minutes", "Plumbing", "Toilet repair service.", "plumbing.jpg"),
    ("TECH CLAN", "Plumbing", "Pipe Leakage Repair", 450, "60 Minutes", "Plumbing", "Pipe leakage repair.", "plumbing.jpg"),
    ("TECH CLAN", "Plumbing", "Drain Unclogging", 650, "60-90 Minutes", "Plumbing", "Drain blockage cleaning.", "plumbing.jpg"),
    ("TECH CLAN", "Plumbing", "Water Pump Repair", 850, "90 Minutes", "Plumbing", "Water pump repair.", "plumbing.jpg"),

    # TECH CLAN - GEYSER
    ("TECH CLAN", "Geyser", "Geyser Installation", 750, "60 Minutes", "Geyser", "Geyser installation.", "electrical.jpg"),
    ("TECH CLAN", "Geyser", "Geyser Repair", 550, "60 Minutes", "Geyser", "Geyser repair visit.", "electrical.jpg"),

    # TECH CLAN - ELECTRICAL
    ("TECH CLAN", "Electrical", "Switch Replacement", 250, "30 Minutes", "Electrical", "Switch replacement.", "electrical.jpg"),
    ("TECH CLAN", "Electrical", "Socket Installation", 300, "30-45 Minutes", "Electrical", "Socket installation.", "electrical.jpg"),
    ("TECH CLAN", "Electrical", "Fan Installation", 450, "60 Minutes", "Electrical", "Fan installation.", "electrical.jpg"),
    ("TECH CLAN", "Electrical", "Ceiling Fan Repair", 400, "45 Minutes", "Electrical", "Ceiling fan repair.", "electrical.jpg"),
    ("TECH CLAN", "Electrical", "Light Installation", 300, "30-45 Minutes", "Electrical", "Light installation.", "electrical.jpg"),
    ("TECH CLAN", "Electrical", "MCB Replacement", 450, "45 Minutes", "Electrical", "MCB replacement.", "electrical.jpg"),
    ("TECH CLAN", "Electrical", "Wiring Repair", 550, "60 Minutes", "Electrical", "Wiring repair.", "electrical.jpg"),
    ("TECH CLAN", "Electrical", "Inverter Installation", 1050, "90 Minutes", "Electrical", "Inverter installation.", "electrical.jpg"),

    # TECH CLAN - CCTV
    ("TECH CLAN", "CCTV", "CCTV Installation (per camera)", 550, "Per Camera", "CCTV", "CCTV camera installation.", "electrical.jpg"),
    ("TECH CLAN", "CCTV", "CCTV Service Visit", 450, "Inspection Visit", "CCTV", "CCTV repair/service visit.", "electrical.jpg"),

    # TECH CLAN - CARPENTRY
    ("TECH CLAN", "Carpentry", "Door Repair", 550, "60 Minutes", "Carpentry", "Door repair service.", "plumbing.jpg"),
    ("TECH CLAN", "Carpentry", "Lock Installation", 450, "45 Minutes", "Carpentry", "Lock installation.", "plumbing.jpg"),
    ("TECH CLAN", "Carpentry", "Curtain Rod Installation", 350, "45 Minutes", "Carpentry", "Curtain rod installation.", "plumbing.jpg"),
    ("TECH CLAN", "Carpentry", "Furniture Assembly", 550, "60-90 Minutes", "Carpentry", "Furniture assembly.", "plumbing.jpg"),
    ("TECH CLAN", "Carpentry", "Carpentry Visit Charge", 350, "Inspection Visit", "Carpentry", "Carpentry inspection visit.", "plumbing.jpg"),

    # FORCE CLAN
    ("FORCE CLAN", "Pest Control", "Cockroach Treatment (1 BHK)", 1050, "60 Minutes", "Pest Control", "Cockroach pest control for 1 BHK.", "pest.jpg"),
    ("FORCE CLAN", "Pest Control", "Cockroach Treatment (2 BHK)", 1550, "90 Minutes", "Pest Control", "Cockroach pest control for 2 BHK.", "pest.jpg"),
    ("FORCE CLAN", "Pest Control", "Termite Treatment (per sq ft)", 6, "Per Sq Ft", "Pest Control", "Termite treatment per sq ft.", "pest.jpg"),
    ("FORCE CLAN", "Pest Control", "Bed Bug Treatment", 2550, "2-3 Hours", "Pest Control", "Bed bug treatment.", "pest.jpg"),
    ("FORCE CLAN", "Pest Control", "Rodent Control", 1250, "60-90 Minutes", "Pest Control", "Rodent control.", "pest.jpg"),
    ("FORCE CLAN", "Pest Control", "Mosquito Control", 1550, "60-90 Minutes", "Pest Control", "Mosquito control.", "pest.jpg"),

    ("FORCE CLAN", "Painting & Waterproofing", "Interior Painting (per sq ft)", 19, "Per Sq Ft", "Painting", "Interior painting per sq ft.", "garden.jpg"),
    ("FORCE CLAN", "Painting & Waterproofing", "Exterior Painting (per sq ft)", 26, "Per Sq Ft", "Painting", "Exterior painting per sq ft.", "garden.jpg"),
    ("FORCE CLAN", "Painting & Waterproofing", "Waterproofing (per sq ft)", 36, "Per Sq Ft", "Waterproofing", "Waterproofing per sq ft.", "garden.jpg"),

    ("FORCE CLAN", "Garden Maintenance", "Lawn Mowing", 1050, "60-90 Minutes", "Gardening", "Lawn mowing service.", "garden.jpg"),
    ("FORCE CLAN", "Garden Maintenance", "Garden Maintenance Visit", 1550, "2-3 Hours", "Gardening", "Garden maintenance visit.", "garden.jpg"),
]

with app.app_context():
    for item in services:
        clan, category, name, price, duration, skill, description, image = item

        existing = Service.query.filter_by(name=name).first()

        if not existing:
            service = Service(
                clan=clan,
                category=category,
                name=name,
                price=price,
                duration=duration,
                skill_required=skill,
                description=description,
                image=image
            )
            db.session.add(service)
        else:
            existing.clan = clan
            existing.category = category
            existing.price = price
            existing.duration = duration
            existing.skill_required = skill
            existing.description = description
            existing.image = image

    db.session.commit()
    print("All RR CLAN PRO services and special offers added successfully.")