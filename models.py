# models.py
from sqlalchemy import Column, Integer, String, Date, Boolean, Float
from database import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    
    # 1. Core Patient Information (PII like address, email, phone removed)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    country = Column(String, nullable=True)
    emergency_contact_name = Column(String, nullable=True)
    emergency_contact_relationship = Column(String, nullable=True)

    # 2. Dietary & Nutrition Preferences
    favorite_foods = Column(String, nullable=True)
    least_preferred_foods = Column(String, nullable=True)
    dietary_restrictions = Column(String, nullable=True)
    meal_schedule = Column(String, nullable=True)
    preferred_drinks = Column(String, nullable=True)
    hydration_tracking = Column(String, nullable=True)
    feeding_assistance_required = Column(Boolean, default=False)

    # 3. Sensory Preferences
    preferred_music_genre = Column(String, nullable=True)
    favorite_color = Column(String, nullable=True)
    least_preferred_color = Column(String, nullable=True)
    preferred_smells = Column(String, nullable=True)
    sensitivity_to_noise = Column(Boolean, default=False)
    sensitivity_to_light = Column(Boolean, default=False)

    # 4. Cognitive & Recreational Interests
    favorite_activities = Column(String, nullable=True)
    hobbies = Column(String, nullable=True)
    former_profession = Column(String, nullable=True)
    languages_spoken = Column(String, nullable=True)
    religion_or_spiritual_beliefs = Column(String, nullable=True)
    cultural_background = Column(String, nullable=True)
    education_level = Column(String, nullable=True)

    # 5. Daily Routine / Behavior Monitoring
    usual_sleep_time = Column(String, nullable=True)
    wake_up_time = Column(String, nullable=True)
    daily_routine_description = Column(String, nullable=True)
    preferred_clothing_type = Column(String, nullable=True)
    preferred_social_activity = Column(String, nullable=True)
    wandering_tendency = Column(Boolean, default=False)
    incontinence_status = Column(Boolean, default=False)
    mobility_status = Column(String, nullable=True)
    communication_method = Column(String, nullable=True)
    agitation_triggers = Column(String, nullable=True)
    calming_strategies = Column(String, nullable=True)

    # 6. Caregiver Info (PII removed)
    primary_caregiver_name = Column(String, nullable=True)
    caregiver_relationship_to_patient = Column(String, nullable=True)
    living_arrangement = Column(String, nullable=True)
    social_support_services = Column(String, nullable=True)
    
    # 7. Clinical Data & Monitoring
    blood_pressure = Column(String, nullable=True)
    heart_rate = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    bmi = Column(Float, nullable=True)
    blood_sugar_level = Column(String, nullable=True)
    cholesterol_level = Column(String, nullable=True)

    # 8. Images (storing file paths)
    partner_image_path = Column(String, nullable=True)
    children_image_path = Column(String, nullable=True)
    pet_image_path = Column(String, nullable=True)
    car_image_path = Column(String, nullable=True)
    house_image_path = Column(String, nullable=True)