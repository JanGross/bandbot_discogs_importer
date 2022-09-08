import discogs_client, json, re, urllib.request, os

client = discogs_client.Client('ExampleApplication/0.1', user_token="QwqnxQajRTDmDtmFgDBJCJjbAcyLFzYwPUbuLHrd")

discogs_id = int(input("Enter Discogs ID: "))
band = client.artist(discogs_id)

band_json = {}
band_json['name'] = band.name
band_json['id'] = discogs_id
band_json['description'] = band.profile
band_json['image'] = band.images[0]['uri']
band_json['enabled'] = 0

members_json = []

def resolve_ref(match):
    print(f"Resolving {match.group()} => ", end="")
    ref = client.artist(int(match.group()[2:-1]))
    print(f"{ref.name}")
    return ref.name

def sanitize_path(path):
    return path.replace(" ", "_")

def image_closest_to_aspect(images):
    aspect = 0.6
    closest = None
    for image in images:
        if image['width'] / image['height'] > aspect and image['width'] < image['height']:
            if closest is None or image['width'] < closest['width']:
                closest = image
    return closest if closest is not None else images[0]

band_folder = sanitize_path(band.name)
if not os.path.exists(f"assets/cards/{band_folder}"):
    os.makedirs(f"assets/cards/{band_folder}")


for member in band.members:
    print(member.name)
    profile = str(member.profile)
    profile = re.sub(r'\[a[0-9|a-zA-Z]*\]', resolve_ref, profile)
    profile = re.sub(r'\[a=[0-9|a-zA-Z ]*\]', lambda match: match.group()[3:-1], profile)

    print("Downloading image...")
    image_path = f"{band_folder}/{member.id}_{sanitize_path(member.name)}.jpeg"
    if not member.images:
        print("No image found.")
        image_path = "assets/cards/no_image.png"
    else:
        urllib.request.urlretrieve(image_closest_to_aspect(member.images)['uri'], f"assets/cards/{image_path}")

    member = {
        'id': member.id,
        'bandId': discogs_id,
        'name': member.name,
        'description': profile,
        'imageIdentifier': image_path,
        'enabled': 0
    }
    members_json.append(member)

with open(f"assets/import/characters/{band_folder}_characters.json", "w") as characters_file:
    json.dump(members_json, characters_file, indent=4, sort_keys=False)

with open(f"assets/import/bands/{band_folder}.json", "w") as band_file:
    json.dump(band_json, band_file, indent=4, sort_keys=False)