from br_helper.br_helper import BrowserHelper
from string import ascii_letters
import time

br = BrowserHelper(
                    browser="firefox", driver_path="/home/tornike/bin/geckodriver",
                    options={'hide_images': True},
                    )

# navigate
br.get('https://www.keybr.com/')

# close tutorial popup
br.css1('.Tour-close').click()

# activate typing mode
br.find('Click to activate...').click()


def get_key_to_press(current_val):
    current_val = current_val.strip()

    helper = dict(zip(ascii_letters, ascii_letters))

    specials = {
        '␣': 'space',  # key to use in br.press method
    }

    helper.update(specials)

    # key to press  & if it needs special handling
    return (
            helper[current_val],
            current_val in specials
        )


document_body = br.css1('body')

counter = 0
main_start_time = time.time()

while True:
    print(time.time())
    active_char = br.css1('div.TextInput-fragment span.TextInput-item--cursor').text
    print(time.time())
    translated_char, special_case = get_key_to_press(active_char)
    print(time.time())

    if not special_case:
        document_body.send_keys(translated_char)
    else:
        br.press(translated_char, elem=document_body)
    print(time.time())

    print(f"Clicked on {active_char} ({translated_char})")
    # time.sleep(0.001)

    print("-" * 100)

    counter += 1
    if counter == 100:
        print(f"Done In {time.time() - main_start_time}")
        break
