# This file must be run as a module
# e.g., from /michelangelo directory, run "python3.8 -m scripts.populate_db"

import time, os
import tests.api_test as api_test

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

special_product = (
    "Web developer",
    1995.20,
    1,
    "img/webdev.jpeg",
    "Congratulations, you found the surprise offer! Special limited edition. Converts caffeine into code. (Price must be negotiated, terms and conditions apply)"
)

def add_products(base_dir = "", throttle = False):
    count = 0
    while True:
        for product in products:
            if count > len(products) and throttle:
                # You might want to throttle a little bit just to avoid race
                # conditions that wouldn't be realistic in a real case scenario
                time.sleep(0.1)

            api_test.post_product(*product, base_dir = base_dir)
            print(".", end="", flush=True)
            count += 1
            if count == 16:
                return

def main():
    if not api_test.is_server_connected():
        raise Exception("Cannot populated database! Server is not connected!")

    this_dir = os.path.dirname(__file__)
    print("Populating database... please be patient")
    add_products(base_dir = this_dir)
    time.sleep(1)
    api_test.post_product(*special_product, base_dir = this_dir)
    print("\ndone")

if __name__ == "__main__":
    main()