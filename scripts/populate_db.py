import requests, os

URL = "http://localhost:7777/michelangelo"

def rel_path(path):
    this_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(this_dir, path)

def check_status_code(status_code):
    if not (status_code >= 200 and status_code < 300):
        raise Exception(f"Error: Server responded with code {status_code}")


def post_picture(path):
    pic = open(rel_path(path),"rb")
    files = {"picture": pic}
    endpoint = "/pictures"
    r = requests.post(URL + endpoint, files=files)
    check_status_code(r.status_code)
    json = r.json()
    return json["picName"], json["md5"]

# picName":null,"md5":null,"prodName":"33","prodPrice":"hello","prodInStock":"5"}'
def post_product(
        prod_name: str,
        prod_price: float,
        prod_instock: int,
        pic_path: str = "",
        prod_descr: str = ""):

    pic_name, pic_md5 = None, None
    if pic_path:
        pic_name, pic_md5 = post_picture(pic_path)

    data = {
        "picName": pic_name,
        "md5": pic_md5,
        "prodName": prod_name,
        "prodPrice": prod_price,
        "prodInStock": prod_instock,
        "prodDescr": prod_descr
    }
    endpoint= "/products"
    r = requests.post(URL + endpoint, json=data)
    check_status_code(r.status_code)
    json = r.json()
    return json["picId"], json["prodId"]


products = [
    (
        "Bandana",
        1.99,
        60,
        "img/bandana.jpg",
        "A nice bandana for tying your hair and enjoying the summer breeze"
    ),
    (
        "Boots",
        48.98,
        12,
        "img/boots.png",
        "With these boots, not only will your feet be well protect, but you will also look awesome!"
    ),
    (
        "Emperor clothes",
        999.95,
        1,
        "img/emperor-clothes.jpg",
        "You wanna look like a 19th century emperor? We've got you covered!"
    ),
    (
        "Feathered hat",
        29.80,
        10,
        "img/feathered-hat.jpg",
        "With this amazing hat, you will be the star of the party! Made with the softest plumes of rare tropical birds — ha! not really, it is all vegan!"
    ),
    (
        "French revolutionary suit",
        59.40,
        5,
        "img/french-revolutionary-suit.jpg",
        "In 1789, the French showed the world that there was no more space for tyranny and autocracy. Now you too can be a libertarian!"
    ),
    (
        "Golden crown",
        1998.01,
        19,
        "img/golden-crown.jpg",
        "Terrific! You will shine. Long live the king!"
    ),
    (
        "Mask",
        14.99,
        1000,
        "img/mask.jpg",
        "Where are you going on this Halloween? Where are you going on next Carnival? For all festive occasions, this mask will not let you down."
    ),
    (
        "Monocle",
        34.98,
        1,
        "img/monocle.jpg",
        "For the weak of vision. As they say, in the land of the bild, the one-eyed is king."
    ),
    (
        "Pantaloons",
        17.05,
        0,
        "img/pantaloons.jpg",
        "With these pantaloons, you will move with great freedom and comfort."
    ),
    (
        "Pirate hat",
        7.99,
        53,
        "img/pirate-hat.jpg",
        "Do what you want 'cos a pirate is free, you are a pirate."
    ),
    (
        "Scarf",
        7.05,
        5,
        "img/scarf.jpg",
        "In any occasion, this scarf will warm you and make you the most handsome guy or gal in the party."
    ),
    (
        "Top hat",
        47.57,
        9,
        "img/top-hat.jpg",
        "A must for every gentleman"
    ),
    (
        "Victorian gothic dress",
        148.99,
        20,
        "img/victorian-gothic-dress.jpg",
        "Enjoy the steampunk vibes"
    )
]

def add_products():
    count = 0
    while True:
        for product in products:
            post_product(*product)
            print(".", end="", flush=True)
            count += 1
            if count == 60:
                return


def main():
    print("Populating database... please be patient")
    add_products()
    special_product = (
        "Web developer",
        148.99,
        20,
        "img/victorian-gothic-dress.jpg",
        "Congratulations, you Special limited edition. Converts caffeine into code. "
    )
    post_product(*special_product)
    print()

main()