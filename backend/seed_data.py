"""Seed script to populate the database from invitation.txt."""

from db import SessionLocal, engine, Base
from models import Family, Guest

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Clear existing data
db.query(Guest).delete()
db.query(Family).delete()
db.commit()


def parse_invitations(filepath: str) -> tuple[list[dict], list[str]]:
    """Parse invitation.txt into families and individual guests.

    Args:
        filepath: Path to the invitation.txt file

    Returns:
        Tuple of (families list, individuals list)
        Each family is a dict with 'name' and 'members' keys
    """
    families = []
    individuals = []
    current_family = None
    skip_section = False

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                # Empty line - if we have a current family with members, save it
                if current_family and current_family['members']:
                    families.append(current_family)
                    current_family = None
                skip_section = False
                continue

            # Main section header
            if line.startswith('# '):
                section_name = line[2:].strip()
                # Skip "Sposi" section (bride & groom)
                if section_name == 'Sposi':
                    skip_section = True
                    current_family = None
                    continue
                skip_section = False

                # Check if it's a family or individual marker
                if 'famiglia' in section_name or 'Genitori' or "Virginia & Alfredo" in section_name:
                    if current_family and current_family['members']:
                        families.append(current_family)
                    current_family = {'name': section_name, 'members': []}
                else:
                    # Testimoni, Nonna, etc - treat following names as individuals
                    if current_family and current_family['members']:
                        families.append(current_family)
                    current_family = None
                continue

            # Sub-section header (##)
            if line.startswith('## '):
                continue

            # Skip if in skipped section
            if skip_section:
                continue

            # It's a name
            if current_family is not None:
                current_family['members'].append(line)
            else:
                individuals.append(line)

    # Don't forget last family if file doesn't end with blank line
    if current_family and current_family['members']:
        families.append(current_family)

    return families, individuals


# Parse the invitation file
families_data, individuals_data = parse_invitations('../data/invitation.txt')

# Create families and their guests
for fam_data in families_data:
    family = Family(family_name=fam_data['name'])
    db.add(family)
    db.commit()
    db.refresh(family)

    for member_name in fam_data['members']:
        db.add(Guest(name=member_name, family_id=family.id))

# Create individual guests
for name in individuals_data:
    db.add(Guest(name=name, family_id=None))

db.commit()
db.close()

print("Database seeded successfully!")
print(f"Created {len(families_data)} families:")
for fam in families_data:
    print(f"  - {fam['name']}: {len(fam['members'])} members")
print(f"Created {len(individuals_data)} individual guests:")
for name in individuals_data:
    print(f"  - {name}")
