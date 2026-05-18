import os, traceback , boto3

from models.user import User
from models.role import Role
from models.monster_type import MonsterType
from models.taste_preference import TastePreference
from models.is_sugar_free_enum import IsSugarFreeEnum
from models.taste_profile_enum import TasteProfileEnum

from configuration.database import DATABASE_URL
from configuration.s3_config import S3_CONFIG, BUCKET_NAME, S3_PUBLIC_ENDPOINT

from configuration.security import get_password_hash

from sqlmodel import (
    Session,
    create_engine,
    SQLModel,
    select
)

engine = create_engine(DATABASE_URL, echo=True)

PUBLIC_MONSTER_FOLDER = "public/monsters"
CURRENT_FILE_PATH = os.path.abspath(__file__)
SEED_DIR = os.path.dirname(CURRENT_FILE_PATH)
APP_DIR = os.path.dirname(SEED_DIR)
LOCAL_SEED_DIR = os.path.join(APP_DIR, "dataset", "seed")

class SeedData:
    def __init__(self):
        self.session = Session(engine)
            
    def seed_data(self):
        SQLModel.metadata.create_all(engine)
        if not self.session.exec(select(Role)).first():
            self.seed_roles()
        
        if not self.session.exec(select(User)).first():
            self.seed_users() 
        
        self.seed_monsters()
        
    def seed_roles(self):
        roles = [
            Role(name="Admin"),
            Role(name="User")
        ]
        self.session.add_all(roles)
        self.session.commit()
    
    def seed_users(self):
        admin_role = self.session.exec(select(Role).where(Role.name == "Admin")).first()
        user_role = self.session.exec(select(Role).where(Role.name == "User")).first()

        admin = User(
            username="admin",
            normalized_username="ADMIN",
            email="admin@example.com",
            normalized_email="ADMIN@EXAMPLE.COM",
            password=get_password_hash("Admin123!"),
            is_active=True,
            roles=[admin_role]
        )
        
        admin_taste = TastePreference(
            user_id=admin.id,
            is_sweet=True,
            is_sour=False,
            is_moderate=False,
            is_sugar_free=IsSugarFreeEnum.no_preference
        )
        
        user = User(
            username="user",
            normalized_username="USER",
            email="user@example.com",
            normalized_email="USER@EXAMPLE.COM",
            password=get_password_hash("User123!"),
            is_active=True,
            roles=[user_role]
        )
        
        user_taste = TastePreference(
            user_id=user.id,
            is_sweet=False,
            is_sour=True,
            is_moderate=False,
            is_sugar_free=IsSugarFreeEnum.yes
        )
        
        self.session.add_all([admin, user, admin_taste, user_taste])
        self.session.commit()
        
    def seed_monsters(self):
        monsters_data = [
            {
                "name": "Juiced Aussie Lemonade",
                "description": "Klasyczna australijska lemoniada, kwaśno-słodka z sokiem.",
                "caffeine_mg": 160,
                "taste_profile": TasteProfileEnum.sour
            },
            {
                "name": "Bad Apple",
                "description": "Intensywny i lekko wytrawny smak jabłka, nie za słodki.",
                "caffeine_mg": 160,
                "taste_profile": TasteProfileEnum.moderate
            },
            {
                "name": "Full Throttle",
                "description": "Oryginalny energetyk cytrusowy, intensywny w smaku.",
                "caffeine_mg": 160,
                "taste_profile": TasteProfileEnum.sweet
            },
            {
                "name": "Juiced Mango Loco",
                "description": "Egzotyczna mieszanka soków z dominującym smakiem mango.",
                "caffeine_mg": 160,
                "taste_profile": TasteProfileEnum.sweet
            },
            {
                "name": "Juiced Monarch",
                "description": "Połączenie soków brzoskwini i nektarynki, bardzo słodki.",
                "caffeine_mg": 160,
                "taste_profile": TasteProfileEnum.sweet
            },
            {
                "name": "Juiced Viking Berry",
                "description": "Nordyckie dzikie jagody połączone z energią Monstera.",
                "caffeine_mg": 160,
                "taste_profile": TasteProfileEnum.sweet
            },
            {
                "name": "Lando Norris Zero Sugar",
                "description": "Zero cukru. Lekki, orzeźwiający smak melona z cytrusową nutą yuzu.",
                "caffeine_mg": 160,
                "taste_profile": TasteProfileEnum.moderate
            },
            {
                "name": "Monster Energy",
                "description": "Klasyczny, oryginalny, słodki i mocny smak Monster Energy.",
                "caffeine_mg": 160,
                "taste_profile": TasteProfileEnum.sweet
            },
            {
                "name": "Monster Energy Zero Sugar",
                "description": "Klasyczny, oryginalny, słodki i mocny smak Monster Energy w wersji bez cukru.",
                "caffeine_mg": 160,
                "taste_profile": TasteProfileEnum.sweet
            },
            {
                "name": "Monster Nitro Super Dry",
                "description": "Technologia infuzji azotem, kremowa tekstura z cytrusowym smakiem Super Dry.",
                "caffeine_mg": 160,
                "taste_profile": TasteProfileEnum.moderate
            },
            {
                "name": "Reserve Peaches N' Cream",
                "description": "Gładkie i kremowe połączenie smaku słodkiej brzoskwini z delikatną śmietanką.",
                "caffeine_mg": 160,
                "taste_profile": TasteProfileEnum.sweet
            },
            {
                "name": "Rio Punch",
                "description": "Tropikalny punch z nutą papai, wanilii i czarnej porzeczki. Słodki, owocowy i lekko przyprawowy.",
                "caffeine_mg": 160,
                "taste_profile": TasteProfileEnum.sweet
            },
            {
                "name": "The Doctor",
                "description": "Dedykowany Valentino Rossi, orzeźwiający smak cytrusów (cytryna-pomarańcza).",
                "caffeine_mg": 160,
                "taste_profile": TasteProfileEnum.sour
            },
            {
                "name": "Ultra Black",
                "description": "Mocny smak ciemnej czereśni, zero cukru.",
                "caffeine_mg": 150,
                "taste_profile": TasteProfileEnum.moderate
            },
            {
                "name": "Ultra Blue",
                "description": "Lekko kwaskowaty smak niebieskiej maliny, lżejszy profil bez cukru.",
                "caffeine_mg": 150,
                "taste_profile": TasteProfileEnum.sour
            },
            {
                "name": "Ultra Fantasy Ruby Red",
                "description": "Zero cukru. Orzeźwiający smak różowego grejpfruta z mocną cytrusową nutą.",
                "caffeine_mg": 160,
                "taste_profile": TasteProfileEnum.moderate
            },
            {
                "name": "Ultra Fiesta Mango",
                "description": "Kombinacja mango bez cukru, która smakuje jak prawdziwa fiesta.",
                "caffeine_mg": 150,
                "taste_profile": TasteProfileEnum.sweet
            },
            {
                "name": "Ultra Gold",
                "description": "Smak świeżego ananasa ukryty w puszce bez cukru.",
                "caffeine_mg": 150,
                "taste_profile": TasteProfileEnum.sweet
            },
            {
                "name": "Ultra Peachy Keen",
                "description": "Zero cukru, orzeźwiający smak letniej brzoskwini.",
                "caffeine_mg": 150,
                "taste_profile": TasteProfileEnum.sweet
            },
            {
                "name": "Ultra Red",
                "description": "Smak czerwonych jagód i żurawiny, bez cukru.",
                "caffeine_mg": 150,
                "taste_profile": TasteProfileEnum.moderate
            },
            {
                "name": "Ultra Rosa",
                "description": "Lekki i rześki smak z kwiatowymi nutami, bez cukru.",
                "caffeine_mg": 150,
                "taste_profile": TasteProfileEnum.moderate
            },
            {
                "name": "Ultra Vice Guava",
                "description": "Tropikalna gujawa z charakterystycznym orzeźwieniem Ultra.",
                "caffeine_mg": 150,
                "taste_profile": TasteProfileEnum.sweet
            },
            {
                "name": "Ultra Violet",
                "description": "Fioletowy klasyk bez cukru o smaku winogronowo-cytrusowym.",
                "caffeine_mg": 150,
                "taste_profile": TasteProfileEnum.sour
            },
            {
                "name": "Ultra Watermelon",
                "description": "Orzeźwiający i lekki smak soczystego arbuza w wersji bez dodatku cukru.",
                "caffeine_mg": 160,
                "taste_profile": TasteProfileEnum.sweet
            },
            {
                "name": "Ultra White",
                "description": "Biały klasyk Monster Ultra. Zero cukru, smak cytrusowy (grejpfrut/cytryna).",
                "caffeine_mg": 150,
                "taste_profile": TasteProfileEnum.moderate
            },
            {
                "name": "VR46",
                "description": "Wersja The Doctor sygnowana numerem 46, mocno cytrusowa.",
                "caffeine_mg": 160,
                "taste_profile": TasteProfileEnum.sour
            },
            {
                "name": "Juiced Khaotic",
                "description": "Powrót do klasycznego Khaosa - mieszanka soków owocowych o smaku pomarańczowym.",
                "caffeine_mg": 160,
                "taste_profile": TasteProfileEnum.sweet
            },
            {
                "name": "Pacific Punch",
                "description": "Klasyczny poncz owocowy inspirowany żeglarskimi klimatami.",
                "caffeine_mg": 160,
                "taste_profile": TasteProfileEnum.sweet
            },
            {
                "name": "Pipeline Punch",
                "description": "Mieszanka marakui, pomarańczy i gujawy. Hawajski klasyk.",
                "caffeine_mg": 160,
                "taste_profile": TasteProfileEnum.sweet
            },
            {
                "name": "Ultra Paradise",
                "description": "Kiwi, limonka i odrobina ogórka. Tropiki bez cukru.",
                "caffeine_mg": 150,
                "taste_profile": TasteProfileEnum.sour
            },
            {
                "name": "Rehab Wild Berry Tea",
                "description": "Czarna herbata połączona z sokiem z owoców leśnych. Nie gazowana.",
                "caffeine_mg": 160,
                "taste_profile": TasteProfileEnum.moderate
            },
            {
                "name": "Killer Brew Loca Moca",
                "description": "Monster Java. Kremowa kawa z czekoladową mokką.",
                "caffeine_mg": 188,
                "taste_profile": TasteProfileEnum.sweet
            },
            {
                "name": "Peach Dragon Ice Tea",
                "description": "Mrożona herbata brzoskwiniowa Rehab Dragon, nie gazowana.",
                "caffeine_mg": 160,
                "taste_profile": TasteProfileEnum.moderate
            },
            {
                "name": "Absolutely Zero",
                "description": "Smak bardzo zbliżony do oryginalnego, ale całkowicie bez kalorii i cukru.",
                "caffeine_mg": 160,
                "taste_profile": TasteProfileEnum.sweet            
            },
            {
                "name": "Java Cafe Latte",
                "description": "Łagodna kawa z dużą ilością mleka i energii Monster.",
                "caffeine_mg": 188,
                "taste_profile": TasteProfileEnum.moderate            
            },
            {
                "name": "Java Irish Cream",
                "description": "Kawa o smaku irlandzkiego kremu, bez alkoholu.",
                "caffeine_mg": 188,
                "taste_profile": TasteProfileEnum.sweet            
            },
            {
                "name": "Java Salted Caramel",
                "description": "Połączenie słonego karmelu i klasycznej kawy energetycznej.",
                "caffeine_mg": 188,
                "taste_profile": TasteProfileEnum.sweet
            }
        ]
        
        added_count = 0
        updated_count = 0
        
        for monster_data in monsters_data:
            existing_monster = self.session.exec(
                select(MonsterType).where(MonsterType.name == monster_data["name"])
            ).first()

            if not existing_monster or not existing_monster.image_url:
                print(f"Przetwarzam zdjęcia dla: {monster_data['name']}...")
                local_img_path = self.find_local_image(monster_data["name"])
                
                if local_img_path:
                    s3_url = self.upload_photo_sync(monster_data["name"], local_img_path)
                    
                    if s3_url:
                        monster_data["image_url"] = s3_url
                        print(f"Success: Photo uploaded: {s3_url}")
                    else:
                        print(f"Error uploading photo for {monster_data['name']}")
                else:
                    print(f"Warning: File not found for '{monster_data['name']}'")

                if not existing_monster:
                    monster = MonsterType(**monster_data)
                    self.session.add(monster)
                    added_count += 1
                elif "image_url" in monster_data:
                    existing_monster.image_url = monster_data["image_url"]
                    self.session.add(existing_monster)
                    updated_count += 1
        
        if added_count > 0 or updated_count > 0:
            self.session.commit()
            print(f"Successfully seeded {added_count} new Monsters")
            print(f"Successfully updated images for {updated_count} existing Monsters.")
        else:
            print("All Monsters already have images. No changes made.")

    def find_local_image(self, monster_name: str) -> str | None:
        name_lower = monster_name.lower()
        variants = [name_lower.replace(" ", "_"), name_lower]
        extensions = ['.jpg', '.png', '.jpeg']
        
        for variant in variants:
            for extension in extensions:
                file_path = os.path.join(LOCAL_SEED_DIR, variant + extension)
                if os.path.exists(file_path):
                    return file_path
        return None
    
    def upload_photo_sync(self, monster_name: str, local_path: str) -> str | None:
        ext = ".png" if local_path.endswith(".png") else ".jpg"
        s3_key = f"{PUBLIC_MONSTER_FOLDER}/{monster_name.replace(' ', '_')}{ext}"
        content_type = "image/png" if ext == ".png" else "image/jpeg"

        s3_client = boto3.client(
            "s3",
            endpoint_url=S3_CONFIG["endpoint_url"],
            aws_access_key_id=S3_CONFIG["aws_access_key_id"],
            aws_secret_access_key=S3_CONFIG["aws_secret_access_key"],
            region_name=S3_CONFIG["region_name"]
        )

        try:
            with open(local_path, "rb") as f:
                s3_client.upload_fileobj(
                    f, 
                    BUCKET_NAME, 
                    s3_key, 
                    ExtraArgs={"ContentType": content_type}
                )
            
            return f"{S3_PUBLIC_ENDPOINT}/{BUCKET_NAME}/{s3_key}"
            
        except Exception as e:
            print(f"Error occurred while uploading photo for {monster_name}: {e}")
            traceback.print_exc()
            return None